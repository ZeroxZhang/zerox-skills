#!/usr/bin/env python3
"""Manage reproducible zerox-onepager project assets.

The CLI does not generate content. It persists the user-confirmed A/B/C/T/E/F
configuration, build artifacts, quality reports, and hashes.
"""

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Sequence

VALID_OPTIONS = {
    "A": {"A1", "A2", "A3", "A4"},
    "B": {f"B{index}" for index in range(1, 10)},
    "C": {"C1", "C2", "C3"},
    "T": {"T1", "T2", "T3", "T4"},
    "E": {"E1", "E2"},
}
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
VERSION_RE = re.compile(r"^v(\d{3})$")
TOOL_VERSION = "1.5.0"


class ProjectError(Exception):
    pass


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ProjectError(f"File not found: {path}") from error
    except json.JSONDecodeError as error:
        raise ProjectError(f"Invalid JSON in {path}: {error}") from error


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def relative_to_project(path: Path, project: Path) -> str:
    try:
        return str(path.resolve().relative_to(project.resolve()))
    except ValueError as error:
        raise ProjectError(f"Path must be inside the project directory: {path}") from error


def manifest_path(project: Path) -> Path:
    return project / "manifest.json"


def validate_configuration(configuration: dict) -> List[str]:
    errors = []
    for key, allowed in VALID_OPTIONS.items():
        if configuration.get(key) not in allowed:
            errors.append(f"configuration.{key} must be one of {sorted(allowed)}")
    signature = configuration.get("F")
    if not isinstance(signature, str) or not signature.strip():
        errors.append("configuration.F must be a non-empty string")
    return errors


def validate_blueprint(value: dict) -> List[str]:
    errors = []
    if value.get("schema_version") != 1:
        errors.append("blueprint.schema_version must be 1")
    for key in ("goal", "audience", "core_claim"):
        if not isinstance(value.get(key), str) or not value[key].strip():
            errors.append(f"blueprint.{key} must be a non-empty string")
    if value.get("logic") not in {"hierarchy", "process", "comparison", "matrix", "narrative"}:
        errors.append("blueprint.logic is invalid")
    modules = value.get("modules")
    if not isinstance(modules, list) or not modules:
        errors.append("blueprint.modules must be a non-empty array")
    else:
        ids = []
        for index, module in enumerate(modules):
            module_id = module.get("id") if isinstance(module, dict) else None
            if not isinstance(module_id, str) or not re.fullmatch(r"[a-z][a-z0-9_-]*", module_id):
                errors.append(f"blueprint.modules[{index}].id is invalid")
            else:
                ids.append(module_id)
            if not isinstance(module, dict) or not isinstance(module.get("source_refs"), list):
                errors.append(f"blueprint.modules[{index}].source_refs must be an array")
        if len(ids) != len(set(ids)):
            errors.append("blueprint module IDs must be unique")
    if not isinstance(value.get("missing"), list):
        errors.append("blueprint.missing must be an array")
    return errors


def validate_ir(value: dict) -> List[str]:
    errors = []
    if value.get("schema_version") != 1:
        errors.append("ir.schema_version must be 1")
    if not isinstance(value.get("blueprint"), dict):
        errors.append("ir.blueprint must be an object")
    else:
        errors.extend(validate_blueprint(value["blueprint"]))
    configuration = value.get("configuration")
    if not isinstance(configuration, dict):
        errors.append("ir.configuration must be an object")
    else:
        errors.extend(validate_configuration(configuration))
    modules = value.get("modules")
    if not isinstance(modules, list) or not modules:
        errors.append("ir.modules must be a non-empty array")
    else:
        ids = []
        for index, module in enumerate(modules):
            if not isinstance(module, dict):
                errors.append(f"ir.modules[{index}] must be an object")
                continue
            module_id = module.get("id")
            if not isinstance(module_id, str):
                errors.append(f"ir.modules[{index}].id is missing")
            else:
                ids.append(module_id)
            locked = module.get("locked")
            if not isinstance(locked, dict) or not all(
                isinstance(locked.get(key), bool) for key in ("content", "layout")
            ):
                errors.append(f"ir.modules[{index}].locked must contain boolean content/layout")
        if len(ids) != len(set(ids)):
            errors.append("IR module IDs must be unique")
    return errors


def validate_manifest(value: dict, project: Path, verify_hashes: bool = True) -> List[str]:
    errors = []
    if value.get("schema_version") != 1:
        errors.append("manifest.schema_version must be 1")
    project_info = value.get("project")
    if not isinstance(project_info, dict):
        errors.append("manifest.project must be an object")
    elif not SLUG_RE.fullmatch(str(project_info.get("slug", ""))):
        errors.append("manifest.project.slug is invalid")
    builds = value.get("builds")
    if not isinstance(builds, list):
        errors.append("manifest.builds must be an array")
        return errors

    versions = []
    for build_index, build in enumerate(builds):
        if not isinstance(build, dict):
            errors.append(f"manifest.builds[{build_index}] must be an object")
            continue
        version = build.get("version")
        if not isinstance(version, str) or not VERSION_RE.fullmatch(version):
            errors.append(f"manifest.builds[{build_index}].version is invalid")
        else:
            versions.append(version)
        tool = build.get("tool")
        if (
            not isinstance(tool, dict)
            or tool.get("name") not in {"onepager", "zerox-onepager"}
            or not re.fullmatch(r"\d+\.\d+\.\d+", str(tool.get("version", "")))
        ):
            errors.append(f"manifest.builds[{build_index}].tool is invalid")
        configuration = build.get("configuration")
        if not isinstance(configuration, dict):
            errors.append(f"manifest.builds[{build_index}].configuration must be an object")
        else:
            errors.extend(validate_configuration(configuration))
        for group in ("artifacts", "checks"):
            entries = build.get(group)
            if not isinstance(entries, list) or not entries:
                errors.append(f"manifest.builds[{build_index}].{group} must be non-empty")
                continue
            for entry_index, entry in enumerate(entries):
                if not isinstance(entry, dict):
                    errors.append(
                        f"manifest.builds[{build_index}].{group}[{entry_index}] must be an object"
                    )
                    continue
                entry_path = project / str(entry.get("path", ""))
                if not entry_path.is_file():
                    errors.append(f"Missing recorded file: {entry_path}")
                    continue
                if verify_hashes and entry.get("sha256") != sha256(entry_path):
                    errors.append(f"Hash mismatch: {entry_path}")
                if group == "checks":
                    if entry.get("verdict") != "PASS":
                        errors.append(f"Recorded check is not PASS: {entry_path}")
                    else:
                        report = read_json(entry_path)
                        if report.get("verdict") != "PASS":
                            errors.append(f"Check report content is not PASS: {entry_path}")
    if len(versions) != len(set(versions)):
        errors.append("Build versions must be unique")
    return errors


def next_version(manifest: dict) -> str:
    highest = 0
    for build in manifest.get("builds", []):
        match = VERSION_RE.fullmatch(str(build.get("version", "")))
        if match:
            highest = max(highest, int(match.group(1)))
    return f"v{highest + 1:03d}"


def command_init(args: argparse.Namespace) -> dict:
    project = args.project.resolve()
    if not SLUG_RE.fullmatch(args.slug):
        raise ProjectError("slug must match ^[a-z0-9][a-z0-9-]*$")
    if manifest_path(project).exists():
        raise ProjectError(f"Project already exists: {project}")
    for directory in ("source", "builds"):
        (project / directory).mkdir(parents=True, exist_ok=True)
    copied_sources = []
    for source in getattr(args, "source", None) or []:
        if not source.is_file():
            raise ProjectError(f"Source file not found: {source}")
        destination = project / "source" / source.name
        if destination.exists():
            raise ProjectError(f"Duplicate source filename: {source.name}")
        shutil.copy2(source, destination)
        copied_sources.append(str(destination))

    created_at = now_iso()
    manifest = {
        "schema_version": 1,
        "project": {
            "slug": args.slug,
            "title": args.title,
            "created_at": created_at,
            "updated_at": created_at,
        },
        "paths": {
            "source": "source",
            "blueprint": "blueprint.json",
            "ir": "onepager.ir.json",
            "builds": "builds",
        },
        "builds": [],
    }
    write_json(manifest_path(project), manifest)
    return {
        "status": "created",
        "project": str(project),
        "manifest": str(manifest_path(project)),
        "sources": copied_sources,
    }


def copy_artifact(source: Path, destination: Path) -> dict:
    if not source.is_file():
        raise ProjectError(f"Artifact not found: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return {
        "path": destination,
        "sha256": sha256(destination),
        "bytes": destination.stat().st_size,
    }


def command_record_build(args: argparse.Namespace) -> dict:
    project = args.project.resolve()
    manifest_file = manifest_path(project)
    manifest = read_json(manifest_file)
    version = args.version or next_version(manifest)
    if not VERSION_RE.fullmatch(version):
        raise ProjectError("version must use vNNN format")
    if any(build.get("version") == version for build in manifest.get("builds", [])):
        raise ProjectError(f"Build version already exists: {version}")

    configuration = {
        "A": args.A,
        "B": args.B,
        "C": args.C,
        "T": args.T,
        "E": args.E,
        "F": args.F,
    }
    configuration_errors = validate_configuration(configuration)
    if configuration_errors:
        raise ProjectError("; ".join(configuration_errors))

    static_report = read_json(args.static_check)
    render_report = read_json(args.render_check)
    for name, report in (("static", static_report), ("render", render_report)):
        if report.get("verdict") != "PASS":
            raise ProjectError(f"{name} check must be PASS before recording a build")

    build_dir = project / "builds" / version
    if build_dir.exists():
        raise ProjectError(f"Build directory already exists: {build_dir}")
    build_dir.mkdir(parents=True)

    artifact_inputs = []
    if args.html:
        artifact_inputs.append(("html", args.html, "output.html"))
    if args.png:
        artifact_inputs.append(("png", args.png, "output.png"))
    if args.svg:
        artifact_inputs.append(("svg", args.svg, "output.svg"))
    if not artifact_inputs:
        raise ProjectError("At least one artifact (--html, --png, or --svg) is required")

    try:
        artifacts = []
        for kind, source, filename in artifact_inputs:
            result = copy_artifact(source, build_dir / filename)
            artifacts.append(
                {
                    "kind": kind,
                    "path": relative_to_project(result["path"], project),
                    "sha256": result["sha256"],
                    "bytes": result["bytes"],
                }
            )

        checks = []
        for kind, source, filename in (
            ("static", args.static_check, "static-check.json"),
            ("render", args.render_check, "render-check.json"),
        ):
            result = copy_artifact(source, build_dir / filename)
            checks.append(
                {
                    "kind": kind,
                    "path": relative_to_project(result["path"], project),
                    "verdict": "PASS",
                    "sha256": result["sha256"],
                }
            )
    except Exception:
        shutil.rmtree(build_dir, ignore_errors=True)
        raise

    build = {
        "version": version,
        "created_at": now_iso(),
        "tool": {"name": "zerox-onepager", "version": TOOL_VERSION},
        "configuration": configuration,
        "artifacts": artifacts,
        "checks": checks,
    }
    manifest.setdefault("builds", []).append(build)
    manifest["project"]["updated_at"] = now_iso()
    write_json(manifest_file, manifest)
    return {"status": "recorded", "project": str(project), "version": version, "build": build}


def command_validate(args: argparse.Namespace) -> dict:
    project = args.project.resolve()
    manifest = read_json(manifest_path(project))
    errors = validate_manifest(manifest, project, verify_hashes=not args.skip_hashes)

    blueprint_path = project / manifest.get("paths", {}).get("blueprint", "blueprint.json")
    if blueprint_path.exists():
        errors.extend(validate_blueprint(read_json(blueprint_path)))
    elif args.require_sources:
        errors.append(f"Missing blueprint: {blueprint_path}")

    ir_path = project / manifest.get("paths", {}).get("ir", "onepager.ir.json")
    if ir_path.exists():
        errors.extend(validate_ir(read_json(ir_path)))
    elif args.require_sources:
        errors.append(f"Missing IR: {ir_path}")

    if errors:
        raise ProjectError("\n".join(f"- {error}" for error in errors))
    return {
        "status": "valid",
        "project": str(project),
        "builds": len(manifest.get("builds", [])),
        "hashes_checked": not args.skip_hashes,
    }


def command_next_version(args: argparse.Namespace) -> dict:
    manifest = read_json(manifest_path(args.project.resolve()))
    return {"version": next_version(manifest)}


def add_configuration_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--A", required=True, choices=sorted(VALID_OPTIONS["A"]))
    parser.add_argument("--B", required=True, choices=sorted(VALID_OPTIONS["B"]))
    parser.add_argument("--C", required=True, choices=sorted(VALID_OPTIONS["C"]))
    parser.add_argument("--T", required=True, choices=sorted(VALID_OPTIONS["T"]))
    parser.add_argument("--E", required=True, choices=sorted(VALID_OPTIONS["E"]))
    parser.add_argument("--F", required=True, help="Confirmed signature or '无'")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage reproducible zerox-onepager projects")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize a project directory")
    init_parser.add_argument("project", type=Path)
    init_parser.add_argument("--slug", required=True)
    init_parser.add_argument("--title", required=True)
    init_parser.add_argument(
        "--source",
        type=Path,
        action="append",
        help="Source file to copy into the project (repeatable)",
    )
    init_parser.set_defaults(handler=command_init)

    version_parser = subparsers.add_parser("next-version", help="Print the next build version")
    version_parser.add_argument("project", type=Path)
    version_parser.set_defaults(handler=command_next_version)

    record_parser = subparsers.add_parser("record-build", help="Record a verified build")
    record_parser.add_argument("project", type=Path)
    record_parser.add_argument("--version")
    add_configuration_arguments(record_parser)
    record_parser.add_argument("--html", type=Path)
    record_parser.add_argument("--png", type=Path)
    record_parser.add_argument("--svg", type=Path)
    record_parser.add_argument("--static-check", type=Path, required=True)
    record_parser.add_argument("--render-check", type=Path, required=True)
    record_parser.set_defaults(handler=command_record_build)

    validate_parser = subparsers.add_parser("validate", help="Validate project assets and hashes")
    validate_parser.add_argument("project", type=Path)
    validate_parser.add_argument("--skip-hashes", action="store_true")
    validate_parser.add_argument("--require-sources", action="store_true")
    validate_parser.set_defaults(handler=command_validate)
    return parser


def print_result(result: dict, output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for key, value in result.items():
            if isinstance(value, (dict, list)):
                print(f"{key}: {json.dumps(value, ensure_ascii=False)}")
            else:
                print(f"{key}: {value}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = args.handler(args)
    except ProjectError as error:
        if args.format == "json":
            print(json.dumps({"status": "error", "error": str(error)}, ensure_ascii=False))
        else:
            print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
    print_result(result, args.format)


if __name__ == "__main__":
    main()
