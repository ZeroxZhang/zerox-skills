import json
import shutil
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import project


class ProjectTests(unittest.TestCase):
    def test_validate_examples(self):
        blueprint = project.read_json(ROOT / "examples" / "blueprint.example.json")
        ir = project.read_json(ROOT / "examples" / "onepager.ir.example.json")
        self.assertEqual(project.validate_blueprint(blueprint), [])
        self.assertEqual(project.validate_ir(ir), [])

    def test_configuration_requires_all_interaction_dimensions(self):
        valid = {"A": "A4", "B": "B2", "C": "C2", "T": "T1", "E": "E2", "F": "无"}
        self.assertEqual(project.validate_configuration(valid), [])
        invalid = dict(valid)
        invalid.pop("B")
        self.assertTrue(any("configuration.B" in error for error in project.validate_configuration(invalid)))

    def test_print_mode_is_exclusive_to_optical_print(self):
        configuration = {"A": "A4", "B": "B2", "C": "C2", "T": "T4", "E": "E2", "F": "无"}
        self.assertEqual(project.validate_configuration({**configuration, "B_mode": "Poster"}), [])
        self.assertTrue(project.validate_configuration({**configuration, "B_mode": "Print"}))
        self.assertEqual(project.validate_configuration({**configuration, "B": "B12", "B_mode": "Print"}), [])

    def test_optional_scene_and_font_dimensions(self):
        base = {"A": "A4", "B": "B10", "C": "C2", "T": "T4", "E": "E2", "F": "无"}
        self.assertEqual(project.validate_configuration(base), [])
        self.assertEqual(
            project.validate_configuration({**base, "S": "S4", "G": "G4"}), []
        )
        self.assertTrue(
            any(
                "configuration.S" in error
                for error in project.validate_configuration({**base, "S": "S9"})
            )
        )
        self.assertTrue(
            any(
                "configuration.G" in error
                for error in project.validate_configuration({**base, "G": "G9"})
            )
        )

    def test_init_next_version_record_and_validate(self):
        with tempfile.TemporaryDirectory(prefix="onepager project ") as directory:
            root = Path(directory)
            project_dir = root / "项目 alpha"
            source = root / "原始资料.md"
            source.write_text("# 原始资料", encoding="utf-8")
            result = project.command_init(
                Namespace(
                    project=project_dir,
                    slug="project-alpha",
                    title="项目 Alpha",
                    force=False,
                    source=[source],
                )
            )
            self.assertEqual(result["status"], "created")
            self.assertTrue((project_dir / "source" / "原始资料.md").is_file())
            manifest = project.read_json(project_dir / "manifest.json")
            self.assertEqual(project.next_version(manifest), "v001")

            shutil.copy2(ROOT / "examples" / "blueprint.example.json", project_dir / "blueprint.json")
            shutil.copy2(ROOT / "examples" / "onepager.ir.example.json", project_dir / "onepager.ir.json")

            html = root / "input page.html"
            png = root / "input image.png"
            static_report = root / "static report.json"
            render_report = root / "render report.json"
            html.write_text("<html><body>fixture</body></html>", encoding="utf-8")
            png.write_bytes(b"fixture png")
            static_report.write_text(json.dumps({"verdict": "PASS"}), encoding="utf-8")
            render_report.write_text(json.dumps({"verdict": "PASS"}), encoding="utf-8")

            layout_report = root / "layout.json"
            layout_report.write_text(json.dumps({"verdict": "PASS"}), encoding="utf-8")
            record = project.command_record_build(
                Namespace(
                    project=project_dir,
                    version=None,
                    A="A4",
                    B="B12",
                    B_mode="Print",
                    C="C2",
                    T="T4",
                    layout_check=layout_report,
                    E="E2",
                    F="Zerox",
                    html=html,
                    png=png,
                    svg=None,
                    static_check=static_report,
                    render_check=render_report,
                )
            )
            self.assertEqual(record["version"], "v001")
            self.assertEqual(record["build"]["configuration"]["B_mode"], "Print")
            self.assertEqual({item["kind"] for item in record["build"]["checks"]}, {"static", "layout", "render"})
            self.assertEqual(record["build"]["tool"]["name"], "zerox-onepager")

            validation = project.command_validate(
                Namespace(
                    project=project_dir,
                    skip_hashes=False,
                    require_sources=True,
                )
            )
            self.assertEqual(validation["status"], "valid")
            self.assertEqual(validation["builds"], 1)
            self.assertEqual(project.next_version(project.read_json(project_dir / "manifest.json")), "v002")

            # 改名前保存的项目仍应可验证；无关工具不能冒充本技能。
            manifest = project.read_json(project_dir / "manifest.json")
            manifest["builds"][0]["tool"]["name"] = "onepager"
            self.assertEqual(project.validate_manifest(manifest, project_dir), [])
            schema = project.read_json(ROOT / "references" / "manifest-schema.json")
            accepted_names = schema["properties"]["builds"]["items"]["properties"]["tool"]["properties"]["name"]["enum"]
            self.assertEqual(set(accepted_names), {"onepager", "zerox-onepager"})
            manifest["builds"][0]["tool"]["name"] = "unrelated-tool"
            self.assertTrue(any(".tool is invalid" in error for error in project.validate_manifest(manifest, project_dir)))

    def test_record_rejects_non_pass_report(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project_dir = root / "project"
            project.command_init(
                Namespace(project=project_dir, slug="project", title="Project", force=False, source=[])
            )
            artifact = root / "output.html"
            static_report = root / "static.json"
            render_report = root / "render.json"
            artifact.write_text("<html></html>", encoding="utf-8")
            static_report.write_text(json.dumps({"verdict": "FAIL"}), encoding="utf-8")
            render_report.write_text(json.dumps({"verdict": "PASS"}), encoding="utf-8")

            with self.assertRaises(project.ProjectError):
                project.command_record_build(
                    Namespace(
                        project=project_dir,
                        version=None,
                        A="A4",
                        B="B2",
                        C="C2",
                        T="T1",
                        E="E2",
                        F="无",
                        html=artifact,
                        png=None,
                        svg=None,
                        static_check=static_report,
                        render_check=render_report,
                    )
                )

    def test_reviewed_layout_warning_round_trip(self):
        warning = {"verdict": "WARN", "warnings": ["vertical air estimate below target"], "errors": []}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            folder = root / "project"
            parser = project.build_parser()
            project.command_init(parser.parse_args(["init", str(folder), "--slug", "poster", "--title", "Poster"]))
            (root / "pass.json").write_text('{"verdict":"PASS"}', encoding="utf-8")
            (root / "layout.json").write_text(json.dumps(warning), encoding="utf-8")
            (root / "poster.html").write_text("<main></main>", encoding="utf-8")
            args = parser.parse_args([
                "record-build", str(folder), "--A", "A4", "--B", "B12", "--B-mode", "Print",
                "--C", "C2", "--T", "T4", "--E", "E2", "--F", "无", "--html", str(root / "poster.html"),
                "--static-check", str(root / "pass.json"), "--layout-check", str(root / "layout.json"),
                "--render-check", str(root / "pass.json")
            ])
            with self.assertRaisesRegex(project.ProjectError, "layout-review"):
                project.command_record_build(args)
            args.layout_review = "插图右侧留白容纳副标题，缩略图阅读顺序清楚。"
            recorded = project.command_record_build(args)
            note = next(check for check in recorded["build"]["checks"] if check["kind"] == "layout")
            self.assertEqual(note["verdict"], "WARN")
            self.assertEqual(note["review"], args.layout_review)
            self.assertEqual(project.validate_manifest(project.read_json(folder / "manifest.json"), folder), [])
            warning["errors"] = ["outside canvas"]
            (root / "layout.json").write_text(json.dumps(warning), encoding="utf-8")
            with self.assertRaisesRegex(project.ProjectError, "contains errors"):
                project.command_record_build(args)

    def test_validate_detects_hash_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project_dir = root / "project"
            project.command_init(
                Namespace(project=project_dir, slug="project", title="Project", force=False, source=[])
            )
            html = root / "output.html"
            static_report = root / "static.json"
            render_report = root / "render.json"
            html.write_text("first", encoding="utf-8")
            static_report.write_text(json.dumps({"verdict": "PASS"}), encoding="utf-8")
            render_report.write_text(json.dumps({"verdict": "PASS"}), encoding="utf-8")
            project.command_record_build(
                Namespace(
                    project=project_dir,
                    version=None,
                    A="A1",
                    B="B1",
                    C="C1",
                    T="T3",
                    E="E2",
                    F="无",
                    html=html,
                    png=None,
                    svg=None,
                    static_check=static_report,
                    render_check=render_report,
                )
            )
            recorded = project_dir / "builds" / "v001" / "output.html"
            recorded.write_text("changed", encoding="utf-8")
            manifest = project.read_json(project_dir / "manifest.json")
            errors = project.validate_manifest(manifest, project_dir)
            self.assertTrue(any("Hash mismatch" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
