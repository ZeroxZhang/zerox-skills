#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""研究包完整性检查器。

① 正文引用号与参考列表一一对应（[3] / [3][5] / [3, p.12]）
② 参考条目的来源 ID 在 sources.md 中存在，对应存档文件存在
③ notes 里的逐字摘录能在对应快照中找到（归一化空白与全半角标点，忽略 Markdown 标记）
④ 元数据必填字段齐全，记录的哈希与文件一致
⑤ 列出孤立文件、未登记来源、被引用但完整度低于 partial 的来源
⑥ 输出 README 所需统计；--write-manifest 生成 manifest-sha256.txt

只用标准库。有错误退出码 1，仅警告退出码 0。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REQUIRED_META = [
    "id", "title", "url", "final_url", "author_org", "published", "accessed",
    "language", "source_type", "credibility", "conflict_of_interest",
    "capture_method", "completeness", "original_files", "sha256", "research_line",
    "supersedes", "archive_url", "access_note", "rights_note",
]
# 这些字段允许为 null（无原始文件 / 无取代 / 无存档），只要键在
NULLABLE_META = {"sha256", "supersedes", "archive_url"}
ID_RE = re.compile(r"^[A-Z]\d{3}$")
REF_TAIL_RE = re.compile(r"来源 ID\s*`([A-Z]\d{3})`\s*存档\s*\[([^\]]*)\]\(([^)]+)\)")
CITE_RE = re.compile(r"\[(\d+)(?:,\s*[^\]]*)?\]")
FULL2HALF = {
    "，": ",", "。": ".", "、": ",", "；": ";", "：": ":", "！": "!", "？": "?",
    "（": "(", "）": ")", "《": "<", "》": ">", "【": "[", "】": "]", "［": "[",
    "］": "]", "｛": "{", "｝": "}", "「": '"', "」": '"', "『": '"', "』": '"',
    "　": " ", "～": "~", "％": "%", "＃": "#", "＆": "&", "＊": "*", "＋": "+",
    "－": "-", "＝": "=", "＠": "@", "．": ".", "…": "...", "—": "-", "–": "-",
    "‘": "'", "’": "'", "“": '"', "”": '"',
}


# ---------------------------------------------------------------- 基础解析

def normalize(s: str) -> str:
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = re.sub(r"^\s{0,3}#{1,6}\s*", "", s, flags=re.M)
    s = re.sub(r"^\s{0,3}>\s?", "", s, flags=re.M)
    s = re.sub(r"`{1,3}([^`]*)`{1,3}", r"\1", s)
    s = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", s)
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    for mark in ("**", "__", "*", "~~"):
        s = s.replace(mark, "")
    s = s.replace("|", " ")
    for k, v in FULL2HALF.items():
        s = s.replace(k, v)
    s = s.casefold()
    return re.sub(r"\s+", " ", s).strip()


def strip_code_blocks(text: str) -> str:
    return re.sub(r"```.*?```", "", text, flags=re.S)


def parse_yaml_header(text: str):
    """解析快照的 YAML 头（本工具自产，只支持 key: value 与简单列表）。"""
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---", 3)
    if end < 0:
        return None, text
    header, body = text[3:end].strip("\n"), text[end + 4:]
    meta = {}
    for line in header.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, raw = line.partition(":")
        key, raw = key.strip(), raw.strip()
        if raw.startswith("[") and raw.endswith("]"):
            inner = raw[1:-1].strip()
            if not inner:
                meta[key] = []
            else:
                items = []
                for part in re.split(r",\s*", inner):
                    part = part.strip().strip('"').strip("'")
                    if part:
                        items.append(part)
                meta[key] = items
        else:
            if raw.lower() == "null":
                meta[key] = None
            else:
                meta[key] = raw.strip('"').strip("'")
    return meta, body


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------- 各检查项

def parse_report(report: Path):
    """返回 (引用号→出现位置, 参考条目列表, 错误列表)。"""
    text = read(report)
    m = re.search(r"^##\s*参考来源\s*$", text, flags=re.M)
    if not m:
        return {}, [], ["report.md 缺少「## 参考来源」小节"]
    body, ref_section = text[: m.start()], text[m.end():]

    refs = {}
    errors = []
    for i, line in enumerate(ref_section.splitlines(), 1):
        if not line.startswith("- ["):
            continue
        head = re.match(r"^- \[(\d+)\]", line)
        if not head:
            errors.append("参考条目格式无法解析（第 {} 行）: {}".format(i, line[:60]))
            continue
        num = int(head.group(1))
        tail = REF_TAIL_RE.search(line)
        refs[num] = {
            "line": line.strip(),
            "source_id": tail.group(1) if tail else None,
            "archive_path": tail.group(3) if tail else None,
        }
        if not tail:
            errors.append("[{}] 条目缺少「来源 ID `X` 存档 [路径](路径)」尾段".format(num))

    cites = defaultdict(list)
    for ln, line in enumerate(strip_code_blocks(body).splitlines(), 1):
        for m2 in CITE_RE.finditer(line):
            num = int(m2.group(1))
            if 1900 <= num <= 2100:  # 多半是年份，不当引用号
                continue
            cites[num].append(ln)
    return cites, refs, errors


def parse_sources_index(path: Path):
    """解析 sources.md 的表格，返回 {ID: 行信息}。"""
    out = {}
    if not path.exists():
        return out
    for line in read(path).splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells or cells[0] in ("ID", "---") or set(cells[0]) <= {"-", " "}:
            continue
        if not ID_RE.match(cells[0]):
            continue
        out[cells[0]] = {
            "title": cells[1] if len(cells) > 1 else "",
            "source_type": cells[5] if len(cells) > 5 else "",
            "credibility": cells[6] if len(cells) > 6 else "",
            "completeness": cells[7] if len(cells) > 7 else "",
            "files": cells[9] if len(cells) > 9 else "",
            "url": cells[10] if len(cells) > 10 else "",
            "cited": cells[11] if len(cells) > 11 else "",
        }
    return out


def parse_notes(pkg: Path, notes_dir: Path):
    """从 notes/*.md 抽出逐字摘录记录。"""
    records = []
    if not notes_dir.exists():
        return records
    for path in sorted(notes_dir.rglob("*.md")):
        try:
            shown = str(path.relative_to(pkg))
        except ValueError:
            shown = str(path)
        lines = read(path).splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]
            src = re.match(r"^\s*-\s*来源:\s*`([A-Z]\d{3})`", line)
            if not src:
                i += 1
                continue
            source_id = src.group(1)
            loc = ""
            lm = re.search(r"定位:\s*(.+?)\s*$", line)
            if lm:
                loc = lm.group(1)
            # 向下找「逐字摘录:」
            j, quote = i + 1, []
            while j < len(lines) and j < i + 12:
                if re.match(r"^\s*-\s*逐字摘录:\s*$", lines[j]):
                    j += 1
                    while j < len(lines) and (not lines[j].strip()
                                              or lines[j].lstrip().startswith(">")):
                        if lines[j].lstrip().startswith(">"):
                            quote.append(re.sub(r"^\s*>\s?", "", lines[j]))
                        j += 1
                    break
                if re.match(r"^\s*-\s*(论断|来源):", lines[j]):
                    break
                j += 1
            records.append({"file": shown, "source_id": source_id,
                            "loc": loc, "quote": "\n".join(quote).strip(), "line": i + 1})
            i += 1
    return records


def find_snapshots(pkg: Path):
    """返回 {ID: (路径, meta, body)}，以 raw/sources/ 下的快照为准。"""
    out = {}
    snap_dir = pkg / "raw" / "sources"
    if not snap_dir.exists():
        return out
    for path in sorted(snap_dir.glob("*.md")):
        meta, body = parse_yaml_header(read(path))
        if not meta:
            continue
        sid = meta.get("id") or path.stem.split("-")[0]
        out[sid] = (path, meta, body)
    return out


# ---------------------------------------------------------------- 主流程

def main(argv=None):
    ap = argparse.ArgumentParser(description="研究包完整性检查")
    ap.add_argument("package", help="研究包根目录")
    ap.add_argument("--write-manifest", action="store_true",
                    help="生成 manifest-sha256.txt（应在 README 写完后执行）")
    ap.add_argument("--json", action="store_true", help="以 JSON 输出结果")
    args = ap.parse_args(argv)

    pkg = Path(args.package).expanduser().resolve()
    if not pkg.is_dir():
        print("不是目录: {}".format(pkg), file=sys.stderr)
        return 1

    errors, warnings = [], []
    report = pkg / "report.md"
    sources_md = pkg / "sources.md"

    # ① 引用号 ↔ 参考列表
    cites, refs, ref_errors = parse_report(report) if report.exists() else ({}, {}, [])
    if not report.exists():
        errors.append("缺少 report.md")
    errors.extend(ref_errors)
    for num, lines in sorted(cites.items()):
        if num not in refs:
            errors.append("正文引用 [{}]（行 {}）在参考列表中无对应条目".format(num, ",".join(map(str, lines))))
    for num, entry in sorted(refs.items()):
        if num not in cites:
            warnings.append("[{}] 参考条目未被正文引用".format(num))

    # ② 参考条目 → sources.md → 存档文件
    index = parse_sources_index(sources_md)
    if not sources_md.exists():
        errors.append("缺少 sources.md")
    snapshots = find_snapshots(pkg)
    for num, entry in sorted(refs.items()):
        sid = entry["source_id"]
        if not sid:
            continue
        if sid not in index:
            errors.append("[{}] 来源 ID {} 不在 sources.md 中".format(num, sid))
        if sid not in snapshots:
            warnings.append("[{}] 来源 ID {} 没有快照文件".format(num, sid))
        apath = entry["archive_path"]
        if apath and not (pkg / apath).exists():
            errors.append("[{}] 存档路径不存在: {}".format(num, apath))

    # ③ 逐字摘录 → 快照原文
    for rec in parse_notes(pkg, pkg / "notes"):
        sid = rec["source_id"]
        if sid not in snapshots:
            errors.append("{}:{} 来源 {} 无快照可比对".format(rec["file"], rec["line"], sid))
            continue
        if not rec["quote"]:
            warnings.append("{}:{} 来源 {} 没有可检的逐字摘录".format(rec["file"], rec["line"], sid))
            continue
        snap_text = normalize(snapshots[sid][2])
        for block in re.split(r"\n{2,}", rec["quote"]):
            if not block.strip():
                continue
            if normalize(block) not in snap_text:
                errors.append("{}:{} 摘录在快照 {} 中找不到（定位: {}）".format(
                    rec["file"], rec["line"], sid, rec["loc"] or "—"))

    # ④ 元数据齐全 + 哈希一致
    for sid, (path, meta, body) in sorted(snapshots.items()):
        for field in REQUIRED_META:
            if field not in meta:
                errors.append("{} 缺少元数据字段 {}".format(path.name, field))
                continue
            if meta[field] in (None, ""):
                if field in NULLABLE_META and meta[field] is None:
                    continue  # 显式 null 是合法值（无原始文件 / 无取代 / 无存档）
                errors.append("{} 缺少元数据字段 {}".format(path.name, field))
        if meta.get("id") and meta["id"] != sid:
            errors.append("{} 元数据 id={} 与文件名前缀 {} 不一致".format(path.name, meta["id"], sid))
        digest = meta.get("sha256")
        originals = meta.get("original_files") or []
        if digest and digest not in ("null", "None") and originals:
            first = pkg / originals[0]
            if first.exists():
                actual = sha256_of(first)
                if actual != digest:
                    errors.append("{} 记录的哈希与 {} 不一致（记录 {}，实际 {}）".format(
                        path.name, originals[0], digest[:12], actual[:12]))
            else:
                errors.append("{} 元数据指向的原始文件不存在: {}".format(path.name, originals[0]))

    # ⑤ 孤立文件 / 未登记来源 / 低完整度引用
    for sid in sorted(index):
        if sid not in snapshots:
            warnings.append("sources.md 登记的 {} 没有对应快照".format(sid))
    for sid in sorted(snapshots):
        if sid not in index:
            warnings.append("快照 {} 未登记进 sources.md".format(sid))

    referenced_files = set()
    for sid, (path, meta, body) in snapshots.items():
        for rel in meta.get("original_files") or []:
            referenced_files.add(str(Path(rel)))
        referenced_files.add("raw/sources/" + path.name)

    skip_names = {"README.md", "report.md", "brief.md", "plan.md", "sources.md",
                  "manifest-sha256.txt"}
    # 检索日志与用户材料是过程记录，按包结构自登记，不算孤立文件
    self_registered = ("notes/", "analysis/", "tasks/", "raw/search-logs/", "raw/user-provided/")
    for path in sorted(pkg.rglob("*")):
        if not path.is_file():
            continue
        rel = str(path.relative_to(pkg))
        if path.name in skip_names or rel.startswith(self_registered):
            continue
        if rel not in referenced_files:
            warnings.append("孤立文件（无快照/元数据引用）: {}".format(rel))

    low_full = ("summary", "snippet-only", "metadata-only")
    for num, entry in sorted(refs.items()):
        sid = entry["source_id"]
        if not sid:
            continue
        comp = ""
        if sid in snapshots:
            comp = (snapshots[sid][1].get("completeness") or "").strip()
        elif sid in index:
            comp = (index[sid].get("completeness") or "").strip()
        if comp in low_full:
            warnings.append("[{}] 来源 {} 完整度为 {}，不得单独支撑关键结论".format(num, sid, comp))

    # ⑥ 统计
    comp_counter = Counter()
    type_counter = Counter()
    for sid, (path, meta, body) in snapshots.items():
        comp_counter[meta.get("completeness") or "?"] += 1
        type_counter[meta.get("source_type") or "?"] += 1
    search_blocks = 0
    search_queries = 0
    log_dir = pkg / "raw" / "search-logs"
    if log_dir.exists():
        for path in sorted(log_dir.rglob("*.md")):
            for line in read(path).splitlines():
                if line.startswith("## "):
                    search_blocks += 1
                if line.strip().startswith("- 查询原文:"):
                    search_queries += 1
    lines = sorted({sid[0] for sid in snapshots} | {
        p.stem.split("-")[0] for p in (pkg / "raw" / "search-logs").glob("*.md")
    }) if (pkg / "raw" / "search-logs").exists() else sorted({sid[0] for sid in snapshots})
    accessed = [meta.get("accessed") for _, meta, _ in snapshots.values() if meta.get("accessed")]
    cited_ids = {e["source_id"] for e in refs.values() if e["source_id"]}

    stats = {
        "sources_total": len(snapshots),
        "completeness": dict(comp_counter),
        "source_type": dict(type_counter),
        "search_blocks": search_blocks,
        "search_queries": search_queries,
        "research_lines": lines,
        "accessed_min": min(accessed) if accessed else None,
        "accessed_max": max(accessed) if accessed else None,
        "cited_sources": len(cited_ids),
        "uncited_sources": len(snapshots) - len(cited_ids),
        "reference_entries": len(refs),
    }

    manifest_note = None
    if args.write_manifest:
        manifest = pkg / "manifest-sha256.txt"
        rows = []
        for path in sorted(pkg.rglob("*")):
            if not path.is_file() or path.name == "manifest-sha256.txt":
                continue
            rel = path.relative_to(pkg)
            rows.append("{}  {}".format(sha256_of(path), rel))
        manifest.write_text("\n".join(rows) + "\n", encoding="utf-8")
        manifest_note = "已写入 manifest-sha256.txt（{} 个文件）".format(len(rows))

    if args.json:
        print(json.dumps({"package": str(pkg), "errors": errors, "warnings": warnings,
                          "stats": stats, "manifest": manifest_note},
                         ensure_ascii=False, indent=2))
    else:
        print("== 研究包检查: {} ==".format(pkg.name))
        if errors:
            print("\n-- 错误 ({}) --".format(len(errors)))
            for e in errors:
                print("  ✗ {}".format(e))
        else:
            print("\n-- 错误 (0) --  无")
        if warnings:
            print("\n-- 警告 ({}) --".format(len(warnings)))
            for w in warnings:
                print("  ! {}".format(w))
        else:
            print("\n-- 警告 (0) --  无")
        print("\n-- 统计 --")
        print("  来源总数: {}".format(stats["sources_total"]))
        print("  完整度: {}".format(stats["completeness"]))
        print("  层级: {}".format(stats["source_type"]))
        print("  检索次数: {} 段日志 / {} 条查询".format(stats["search_blocks"], stats["search_queries"]))
        print("  研究线: {}".format(",".join(stats["research_lines"]) or "—"))
        print("  起止: {} → {}".format(stats["accessed_min"] or "—", stats["accessed_max"] or "—"))
        print("  参考条目 {} 条，覆盖来源 {} 个，未被引用 {} 个".format(
            stats["reference_entries"], stats["cited_sources"], stats["uncited_sources"]))
        if manifest_note:
            print("\n  " + manifest_note)
        print("\n结果: {}".format("FAIL（{} 错误）".format(len(errors)) if errors else "PASS"))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
