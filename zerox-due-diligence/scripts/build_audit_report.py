"""组装独立 Markdown 核验底稿；包含过程记录，不作为默认阅读主报告。"""
import argparse
import re
from pathlib import Path

from common import CONTRACT, ROOT, cli, fail, load_json, read_project, research_gate, safe_write, structural_errors, semantic_errors
from scoring import project_score


DISPLAY = {
    "pending": "待确认", "applicable": "适用", "not_applicable": "不适用",
    "complete": "完成", "partial": "部分完成", "incomplete": "未完成",
    "draft": "草稿", "limited": "受限结果", "resolved": "已消歧/已解决",
    "ambiguous": "主体歧义", "listed": "已上市", "unlisted": "非上市", "unknown": "未知",
    "control": "控制", "joint_control": "共同控制", "minority": "参股",
    "actual": "实际", "forecast": "第三方预测", "estimate": "本项目估算",
    "consolidated": "合并", "standalone": "单体", "segment": "分部",
    "unread": "未读", "analyzed": "已读并分析", "full_text": "可读全文",
    "partial_text": "部分正文", "abstract_only": "仅摘要", "metadata_only": "仅元数据",
    "access_blocked": "访问受限", "unreadable": "不可读", "not_executed": "未执行",
    "found": "已发现", "not_found": "未找到", "failed": "失败",
    "open": "开放", "closed": "已关闭", "covered": "已覆盖", "lagging": "滞后",
    "high": "高", "medium": "中", "low": "低", "verified": "已核实",
    "insufficient_evidence": "证据不足，暂不提供综合评分", "purpose_pending": "目的待确认，暂不评分",
    "business": "业务适配", "growth": "增长", "governance": "治理", "financial": "财务",
    "compliance": "合规", "technology": "技术", "operations": "运营", "deal": "交易",
    "not_disclosed": "未披露", "access_restricted": "访问受限",
}
DISPLAY.update(CONTRACT["research"]["category_names"])


def cell(value):
    if value is None:
        return "未记录"
    if isinstance(value, list):
        value = "；".join(map(str, value))
    return DISPLAY.get(str(value), str(value)).replace("|", "\\|").replace("\n", "<br>")


def table(rows, columns):
    header = "| " + " | ".join(label for _, label in columns) + " |\n"
    header += "| " + " | ".join("---" for _ in columns) + " |\n"
    if not rows:
        return "未登记记录；不能据此推定没有风险或已完成研究。"
    return header + "\n".join("| " + " | ".join(cell(row.get(key)) for key, _ in columns) + " |" for row in rows)


def build(project, output, sections=None, overwrite=False):
    cfg, data = read_project(project)
    errors = structural_errors(data, cfg) + semantic_errors(cfg, data)
    if errors:
        fail("无法组装含结构错误的数据：" + "；".join(errors))
    sections = sections or {}
    allowed = {"summary", "highlights", "recommendation", "research_comparison", "data_bridge", "judgment", "next_steps"}
    if not isinstance(sections, dict) or set(sections) - allowed or any(not isinstance(v, str) for v in sections.values()):
        fail("sections 应为指定章节名到 Markdown 字符串的对象")
    gate = research_gate(cfg, data)
    gate_name = CONTRACT["research"]["status_names"][gate]
    score = project_score(cfg, data)
    limits = "离线材料分析；未执行在线补查。" if cfg["constraints"]["network"] == "offline" else "工具能力和访问范围以实际检索记录为准。"
    if gate in ("partial", "incomplete"):
        limits += " 强制研报任务尚未满足，结论仅限现有证据支持的局部问题。"
    legal_name = next(r["legal_name"] for r in data["entity-map"] if r["entity_id"] == cfg["target_id"])
    purpose = CONTRACT["scoring"]["purposes"][cfg["purpose"]]["label"] if cfg["purpose"] else "待确认，暂不评分"
    coverage_text = f"{score['coverage']:.1%}" if score.get("coverage") is not None else "不适用/目的待确认"
    partial_text = f"{score['partial_score']:.3f}" if score.get("partial_score") is not None else "证据不足，暂无分数"
    overall_text = f"{score['overall_score']:.3f}" if score.get("overall_score") is not None else "暂不提供"
    blocks = {
        "metadata": f"主体：{legal_name}（{cfg['target_id']}）；输入名称：{cfg['target']}\n\n"
                    f"目的：{purpose}；深度：{cfg['depth']}；地域：{cfg['geography'] or '待确认'}\n\n"
                    f"基准日：{cfg['as_of_date']}；时区：{cfg['timezone']}；版本：{cfg['version']}；保密范围：{cfg['confidentiality']}\n\n"
                    f"报告状态：{cell(cfg['report_status'])}；最终复查：{cfg['last_refresh_at'] or '未执行'}",
        "summary": sections.get("summary", "【缺口】尚未录入经证据支持的综合摘要。") + "\n\n" + sections.get("highlights", "亮点仅在有证据时填写，不强凑数量。"),
        "completion": f"研报门槛：{gate_name}\n\n{limits}\n\n" + table(
            [{"module": k, **v} for k, v in cfg["module_scope"].items()], [("module", "模块"), ("status", "适用性"), ("reason", "理由")]),
        "entities": table(data["entity-map"], [("entity_id", "主体 ID"), ("legal_name", "法定名"), ("registration_id", "注册号"), ("listing_status", "上市状态"), ("identity_status", "核验状态")])
                    + "\n\n" + table(data["entity-relations"], [("parent_id", "上层主体"), ("child_id", "下层主体"), ("relation_type", "关系"), ("control_basis", "控制依据"), ("effective_from", "生效"), ("effective_to", "失效"), ("evidence_ids", "证据")]),
        "coverage": table(data["research-coverage"], [("target_id", "目标"), ("research_entity_id", "研究主体"), ("category", "类别"),
                    ("latest_discovered_id", "最新发现"), ("latest_fulltext_id", "最新全文"), ("latest_read_id", "最新已读"),
                    ("event_coverage", "事件覆盖"), ("gate_status", "状态"), ("gap_id", "缺口")]),
        "score": (f"业务适配状态：{cell(score['status'])}；加权证据覆盖率：{coverage_text}\n\n"
                  f"已覆盖维度局部分数：{partial_text}；可发布综合分：{overall_text}\n\n"
                  "业务评价、风险矩阵和证据充分程度分别解释。")
                 + "\n\n" + table(data["scorecard"], [("dimension", "维度"), ("weight", "权重"), ("applicability", "适用性"), ("score", "评分"), ("anchor", "锚点"), ("reason", "缺失/不适用原因")]),
        "research_comparison": sections.get("research_comparison", "【缺口】尚未录入研报观点、预测口径、关键假设、分歧、反证及采信理由比较。"),
        "claims": table(data["claim-register"], [("claim_id", "声明"), ("statement", "陈述"), ("label", "标签"), ("entity_id", "主体"), ("verification", "核验"), ("confidence", "置信度"), ("unresolved", "未解决问题")])
                  + "\n\n" + table(data["claim-evidence"], [("claim_id", "声明"), ("evidence_id", "证据"), ("relation", "关系"), ("bridge", "口径桥接"), ("limitations", "限制")]),
        "data_bridge": sections.get("data_bridge", "未提供定量桥接或情景底稿；不能从集团总量推导子公司收入。"),
        "risks": table(data["risk-register"], [("risk_id", "风险"), ("description", "描述"), ("entity_id", "承担主体"), ("status", "性质"),
                   ("impact", "影响"), ("likelihood", "可能性"), ("time_horizon", "期间"), ("mitigation", "缓释"), ("residual_risk", "残余风险"), ("closure_condition", "关闭条件")])
                 + "\n\n" + table(data["conflict-register"], [("conflict_id", "冲突"), ("left_value_scope", "一方口径"), ("right_value_scope", "另一方口径"), ("status", "状态"), ("decision_impact", "决策影响")]),
        "judgment": sections.get("judgment", "暂不作超出现有证据的综合判断。") + "\n\n" + sections.get("recommendation", "行动建议须列依据、前置条件、责任角色、完成标准和残余风险。"),
        "gaps": table(data["gap-register"], [("gap_id", "缺口"), ("needed", "所需信息"), ("reason", "原因"), ("materiality", "重大性"), ("priority", "优先级"), ("acquisition_path", "获取路径"), ("owner_role", "责任角色"), ("status", "状态")]),
        "next_steps": sections.get("next_steps", "优先锁定主体、补齐 P0 缺口和必读研报；未经授权不对外联系、购买或自动建立监控。"),
        "requests": (Path(project) / "request-list.md").read_text(encoding="utf-8"),
        "interviews": (Path(project) / "interview-outline.md").read_text(encoding="utf-8"),
        "evidence": table([{**r, "reference": f"[{r['evidence_id']}]"} for r in data["evidence-ledger"]],
                          [("reference", "引用"), ("source_id", "来源"), ("entity_id", "主体"), ("scope", "范围"), ("attribute", "数据属性"), ("locator", "定位"), ("excerpt", "短摘录/释义"), ("limitations", "限制")])
                    + "\n\n" + table(data["source-register"], [("source_id", "来源"), ("title", "标题"), ("locator", "URL/本地文件"), ("published_date", "发布日期"), ("accessed_date", "访问日"), ("origin_group", "同源组"), ("access_status", "取得状态"), ("time_scope", "时点范围")]),
        "research_appendix": table(data["research-register"], [("research_id", "报告"), ("title", "标题"), ("publisher", "机构"), ("report_date", "发布日期"), ("categories", "类别"), ("access_status", "获取"), ("reading_status", "阅读"), ("relevant_sections", "目标章节"), ("interests", "利益披露"), ("key_views", "观点"), ("assumptions", "假设"), ("decision_impact", "对本项目影响"), ("limitations", "局限")]),
        "searches": table(data["search-log"], [("search_id", "检索"), ("searched_at", "时间"), ("channel", "渠道"), ("query", "查询"), ("status", "结果"), ("limitations", "覆盖限制")]),
        "limitations": limits + "\n\n结构检查不能证明事实真实。公开资料研究、待执行访谈与实际完成的专业核查分别记录。",
    }
    modules = []
    for number, scope in cfg["module_scope"].items():
        files = sorted((Path(project) / "modules").glob(f"{number}-*.md"))
        if len(files) > 1:
            fail(f"模块 {number} 存在多个候选版本，请明确保留本次版本")
        if scope["status"] == "not_applicable":
            body = f"不适用：{scope['reason']}"
        elif files:
            body = files[0].read_text(encoding="utf-8")
        else:
            body = "【缺口】未提供模块分析；该模块尚未执行或未交付。"
        modules.append(f"### 模块 {number}\n\n{body}")
    blocks["modules"] = "\n\n".join(modules)
    template = (ROOT / "templates" / ("report-quick.md" if cfg["depth"] == "Quick" else "report-full.md")).read_text(encoding="utf-8")
    rendered = re.sub(r"\{\{([a-z_]+)\}\}", lambda m: blocks.get(m[1], m[0]), template)
    if "{{" in rendered:
        # 已复制但未定制的资料清单/访谈占位符作为明确待办，不伪造执行内容。
        rendered = re.sub(r"\{\{([^}]+)\}\}", r"【缺口：\1 尚未填写】", rendered)
    safe_write(output, rendered, overwrite)
    return {"output": str(Path(output).resolve()), "research_gate": gate, "report_status": cfg["report_status"],
            "next": "运行 check_report.py，并逐项完成其人工复核清单。"}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--sections", help="可选 JSON：summary/highlights/recommendation/research_comparison/data_bridge/judgment/next_steps")
    p.add_argument("--overwrite", action="store_true", help="显式覆盖指定输出；默认拒绝已有文件")
    args = p.parse_args()
    from common import emit
    emit(build(args.project, args.output, load_json(args.sections) if args.sections else None, args.overwrite))


if __name__ == "__main__":
    raise SystemExit(cli(main))
