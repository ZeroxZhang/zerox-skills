"""检查结构和已声明状态，单独列出必须由分析者执行的语义复核。"""
import argparse
import re
from pathlib import Path

from common import (InputError, cli, emit, finite, indices, iso_time, load_json, read_project,
                    research_errors, research_gate, semantic_errors, structural_errors)
from scoring import project_score


MANUAL_REVIEW = [
    "逐句检查证据是否真正支持陈述，权威原件是否仅覆盖登记、自述或审计范围。",
    "复核实体、合并/单体/分部、币种、单位、期间与实际/预测；桥接说明是否合理。",
    "核对转载和共同原件是否已按同源组归并；独立观点不等于独立事实证据。",
    "核验检索渠道、最新发现、全文和已读状态，逐类复查交付前的新公告与事件。",
    "检查预测假设、估算区间、反证、利益冲突和重要遗漏；不能靠结构扫描确认。",
    "复核法律/名单命中身份、当前状态、限制范围以及建议与用户决策权限的关系。",
    "检查访谈、现场、函证、代码审查的执行证明，未实施工作只能列为计划。",
]


def check(project=None, report=None, mode="draft"):
    errors, warnings = [], []
    text = Path(report).read_text(encoding="utf-8") if report else ""
    if mode == "template":
        if not report:
            errors.append("模板模式必须指定 --report")
        return {"status": "template_checked" if not errors else "invalid", "errors": errors,
                "warnings": ["模板允许占位符；未验证任何真实研究结论。"], "manual_review": MANUAL_REVIEW}
    if not project:
        return {"status": "invalid", "errors": ["必须指定项目工作区"], "warnings": [], "manual_review": MANUAL_REVIEW}
    try:
        cfg, data = read_project(project)
    except (InputError, OSError, UnicodeError) as exc:
        return {"status": "invalid", "errors": [str(exc)], "warnings": [], "manual_review": MANUAL_REVIEW}
    errors.extend(structural_errors(data, cfg))
    if not errors:
        errors.extend(semantic_errors(cfg, data))
        errors.extend(research_errors(cfg, data))
    idx = indices(data)
    gate = research_gate(cfg, data)
    try:
        score = project_score(cfg, data)
        if cfg["published_score"] is not None:
            published = finite(cfg["published_score"], "已发布综合分")
            expected = score["overall_score"]
            if expected is None or abs(published - expected) > 1e-8:
                errors.append("综合评分与实际发布门槛/计算结果不一致")
    except InputError as exc:
        errors.append(f"评分：{exc}")
        score = {"status": "invalid"}
    if cfg["identity_status"] == "resolved" and idx["entity-map"].get(cfg["target_id"], {}).get("identity_status") != "resolved":
        errors.append("配置已锁定主体与台账身份状态不一致")
    complete = mode == "completed" or cfg["report_status"] == "complete" or cfg["declared_complete"]
    if complete:
        if not report:
            errors.append("完成态检查必须提供实际报告文件")
        if cfg["identity_status"] != "resolved":
            errors.append("主体未锁定不能宣称完成")
        if gate not in ("complete", "not_applicable"):
            errors.append("强制研报任务未完成，报告只能标为受限结果")
        if any(v["status"] == "pending" for v in cfg["module_scope"].values()):
            errors.append("完成报告仍有模块适用性待确认")
        if not cfg["last_refresh_at"]:
            errors.append("完成报告缺少最终最新性复查时间")
        if "{{" in text or "}}" in text:
            errors.append("正式完成报告残留模板占位符")
        if "尚未填写】" in text or "尚未录入经证据支持的综合摘要" in text:
            errors.append("正式完成报告残留未定制字段或缺少执行摘要")
        if "未提供模块分析" in text:
            errors.append("正式完成报告仍缺适用模块分析")
    for action in cfg["completed_actions"]:
        if not isinstance(action, dict) or not action.get("action") or action.get("status") not in ("completed", "planned"):
            errors.append("completed_actions 格式错误；需 action/status/evidence_ids/output_locator")
            continue
        if action["status"] == "completed":
            refs = action.get("evidence_ids", [])
            locator = action.get("output_locator")
            if not refs and not locator:
                errors.append(f"已完成动作缺少执行证据：{action['action']}")
            for eid in refs:
                if eid not in idx["evidence-ledger"]:
                    errors.append(f"已完成动作引用不存在：{eid}")
    if report:
        for eid in re.findall(r"\[(E-\d+)\]", text):
            if eid not in idx["evidence-ledger"]:
                errors.append(f"报告引用不存在：{eid}")
        for token in re.findall(r"\[(E-[^\]\s]+)\]", text):
            if not re.fullmatch(r"E-\d{4,}", token):
                errors.append(f"报告证据 ID 格式错误：{token}")
        for section in ("元信息", "执行摘要", "研究完成范围", "研报覆盖", "信息缺口", "下一步", "证据附录"):
            if not re.search(rf"^#{{1,6}}\s+.*{section}", text, re.MULTILINE):
                errors.append(f"报告缺少结构章节：{section}")
        if gate not in ("complete", "not_applicable") and re.search(r"(?m)^(?:研报(?:研究|门槛|任务)?|研究任务)[：: ]+(?:全部完成|已完成|完成)\s*$", text):
            errors.append("正文宣称研报或全部研究完成，但实际门槛未满足")
        if re.search(r"(?m)^综合评分[：: ]+\d", text) and score.get("overall_score") is None:
            errors.append("正文发布综合评分但证据门槛未满足")
        for n, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            if not stripped or stripped.startswith(("#", "|", "```", "-", ">")):
                continue
            if re.match(r"^(日期|基准日|版本|公式|方法|时区|期间|元信息|目的|深度|主体)", stripped):
                continue
            if re.search(r"\d", line) and not re.search(r"\[E-\d+\]", line) and not re.fullmatch(r"\d+[.、]\s*.*", stripped):
                warnings.append(f"第 {n} 行可能含未引用数字，需人工判断；不是硬错误")
    groups = {}
    for source in data["source-register"]:
        groups.setdefault(source["origin_group"], []).append(source["source_id"])
    for group, ids in groups.items():
        if len(ids) > 1:
            warnings.append(f"同源组 {group}：{ids}，不得计作多个独立事实来源")
    if gate in ("partial", "incomplete"):
        warnings.append("研报门槛未满足；允许交付清楚披露限制的阶段结果")
    # 如存在财务结果输入，验证证据 ID；空模板允许留在项目内。
    financial = Path(project) / "financial-input.json"
    if financial.exists():
        try:
            fin = load_json(financial)
            if fin.get("values"):
                from financial_ratios import calculate
                calculate(fin)
                for item in (fin, fin.get("prior")):
                    if item:
                        for sid in item["source_ids"]:
                            if sid not in idx["source-register"]:
                                errors.append(f"财务来源不存在：{sid}")
                        for refs in item["input_evidence"].values():
                            for eid in refs:
                                if eid not in idx["evidence-ledger"]:
                                    errors.append(f"财务输入证据不存在：{eid}")
        except (InputError, OSError) as exc:
            errors.append(f"财务输入：{exc}")
    return {"status": "invalid" if errors else "structure_passed", "errors": errors, "warnings": warnings,
            "research_gate": gate, "score": score, "manual_review": MANUAL_REVIEW,
            "meaning": "此结果仅为结构和显式状态校验；不证明财务真实、报告充分或决策正确。"}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project")
    p.add_argument("--report")
    p.add_argument("--mode", choices=["template", "draft", "completed"], default="draft")
    p.add_argument("--output")
    args = p.parse_args()
    result = check(args.project, args.report, args.mode)
    emit(result, args.output)
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(cli(main))
