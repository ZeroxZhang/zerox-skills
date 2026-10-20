"""生成阅读型 HTML 主报告和独立核验底稿；不自动生成事实、分析或研究完成声明。"""
import argparse
import tempfile
from pathlib import Path

from common import cli, dumps, fail, load_json, read_project, safe_write, structural_errors, semantic_errors
from build_audit_report import build as build_audit
from report_html import render
from report_media import load_media
from visual_review import review_visuals


def visual_audit(review):
    """把编辑线索留在底稿，不插入面向读者的正文。"""
    def cell(value):
        return str(value).replace("|", "／").replace("\n", " ")
    lines = ["", "## 逐章可视化编辑复核", "", review["meaning"], "",
             "| 章节 | 数据图 | 结构图 | 指标 | 图片 / 人物 | 编辑提示 |",
             "| --- | --- | --- | --- | --- | --- |"]
    for row in review["rows"]:
        c = row["counts"]
        structure = sum(c[k] for k in ("diagram_blocks", "process_blocks", "timeline_blocks", "matrix_blocks"))
        findings = "；".join(item["message"] for item in row["findings"]) or "未触发启发式提示，仍需人工复核。"
        lines.append(f'| {cell(row["title"])} | {c["quantitative_charts"]} | {structure} | {c["metric_items"]} | {c["images"]} / {c["people_profiles"]} | {cell(findings)} |')
    lines.extend(["", "请记录已转图或保留文字的具体理由；机器统计不代表事实与视觉验收通过。"])
    for finding in review["findings"]:
        lines.append(f'\n- {finding["message"]}')
    return "\n".join(lines) + "\n"


def build(project, output, sections=None, overwrite=False, content=None):
    output = Path(output)
    if output.suffix.lower() == ".md":
        if content is not None:
            fail("阅读稿 --content 应输出 .html；.md 只用于旧版核验底稿")
        result = build_audit(project, output, sections, overwrite)
        result["artifact_role"] = "audit_workpaper"
        return result
    if output.suffix.lower() != ".html":
        fail("主报告输出需为 .html；旧底稿输出可用 .md")
    if content is None:
        fail("HTML 主报告需要 --content 编辑后的阅读稿 JSON；不可直接拼接模块或台账")
    if not isinstance(content, dict) or content.get("version") != "1.2":
        fail("新 HTML 主报告需要 version=1.2：补齐公司、财务、营销与竞争主题及必要展示；旧 1.0/1.1 仅支持历史阅读检查")
    if sections is not None:
        fail("--sections 仅用于旧版 Markdown 底稿；HTML 请使用 --content")
    cfg, data = read_project(project)
    errors = structural_errors(data, cfg) + semantic_errors(cfg, data)
    if errors:
        fail("无法组装含结构错误的数据：" + "；".join(errors))
    audit = output.with_name(output.stem + "-audit.md")
    for path in (output, audit):
        if path.exists() and not overwrite:
            fail(f"输出已存在，需明确 --overwrite：{path}")
        if not path.parent.is_dir():
            fail(f"输出父目录不存在：{path.parent}")
    document, validation = render(content, cfg, data, audit.name, media=load_media(content, project))
    visual_review = review_visuals(content)
    # 先完整生成两个文件；检查失败不写入最终目录。
    with tempfile.TemporaryDirectory(prefix="zerox-report-") as tmp:
        tmp_audit = Path(tmp) / "audit.md"
        build_audit(project, tmp_audit, {
            "summary": content["summary"],
            "highlights": "阅读主报告见同目录 HTML。本文件保存完整研究过程与核验记录。",
            "judgment": content["scope_note"],
        })
        audit_text = tmp_audit.read_text(encoding="utf-8") + visual_audit(visual_review)
    safe_write(audit, audit_text, overwrite)
    safe_write(output, document, overwrite)
    return {"output": str(output), "audit": str(audit), "artifact_role": "reader_report",
            "chart_count": validation["chart_count"], "warnings": validation["warnings"] + visual_review["warnings"],
            "reader_coverage": validation["reader_coverage"],
            "visual_review": visual_review,
            "report_status": cfg["report_status"],
            "next": "运行 check_report.py，并复核图表事实、桌面/移动阅读与打印布局；结构通过不证明事实正确。"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--content", help="面向读者编写的报告 JSON")
    parser.add_argument("--sections", help="仅旧 Markdown 底稿使用的补充章节 JSON")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    print(dumps(build(args.project, args.output, load_json(args.sections) if args.sections else None,
                      args.overwrite, load_json(args.content) if args.content else None)), end="")


if __name__ == "__main__":
    raise SystemExit(cli(main))
