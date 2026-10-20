"""生成可执行检索计划，不写入检索执行日志。"""
import argparse
from datetime import timedelta

from common import CONTRACT, cli, emit, iso_date, listed_entities, project_events, read_project, requirements


MODULE_TERMS = {
    "01": ("注册号 股权 实际控制人 历史名称", "公司注册处/交易所原件"),
    "02": ("董事 高管 任职 离任 利益冲突", "任职公告/监管记录"),
    "03": ("产品 定价 收入构成 客户 留存", "财报/合同/产品文档"),
    "04": ("市场规模 供需 产业链", "统计机构/行业原始研究"),
    "05": ("替代产品 市场份额 价格 竞争", "客户选择/竞品披露"),
    "06": ("复购 投诉 交付 单位经济", "客户记录/运营数据"),
    "07": ("增长 瓶颈 产能 融资 许可", "经营披露/供需证据"),
    "08": ("许可证 监管 政策 出口管制", "主管机关/现行规则"),
    "09": ("订单 合同 验收 回款 渠道", "双方合同/客户侧披露"),
    "10": ("产能 质量 延期 连续性 灾备", "生产记录/认证机构"),
    "11": ("专利 开源 数据权利 安全 模型成本", "权利原件/产品文档"),
    "12": ("财报 审计 现金流 应收 债务", "审计报表/附注"),
    "13": ("诉讼 执行 处罚 和解 担保", "法院/监管原始记录"),
    "14": ("排放 安全 劳工 事故 整改", "监管/第三方核验"),
    "15": ("违约 欠薪 风险 澄清 反证", "原始案件/公司回应"),
    "16": ("估值 并购 对价 交割 净债务", "交易公告/可比披露"),
    "17": ("付款 交付 账期 担保 资金归集", "合同/付款记录/担保原件"),
    "18": ("年报 中报 公司深度 业绩点评", "交易所/券商原始发布"),
}


def plan(cfg, data):
    as_of = iso_date(cfg["as_of_date"])
    tasks = []
    listed, _ = listed_entities(cfg, data)
    for entity in data["entity-map"]:
        aliases = [entity["legal_name"], *(entity["aliases"] or [])]
        if entity["security_code"]:
            aliases.append(entity["security_code"])
        for module, (terms, source) in MODULE_TERMS.items():
            if cfg["module_scope"][module]["status"] == "not_applicable":
                continue
            for name in dict.fromkeys(aliases):
                for language in cfg["languages"]:
                    english = " filings due diligence evidence risks counterevidence" if language == "en" else ""
                    tasks.append({"entity_id": entity["entity_id"], "module": module, "alias": name,
                                  "query": f'"{name}" {terms}{english}', "source": source,
                                  "geography": entity["geography"] or cfg["geography"], "language": language,
                                  "from": None, "to": cfg["as_of_date"], "status": "not_executed",
                                  "goal": "正面与反面证据并查；无结果时更换别名与来源"})
    required, _ = requirements(cfg, data)
    names = {r["entity_id"]: r["legal_name"] for r in data["entity-map"]}
    for target, parent, category in required:
        for days in (90, 180, 365, None):
            start = (as_of - timedelta(days=days)).isoformat() if days else None
            tasks.append({"entity_id": target, "research_entity_id": parent, "module": "18",
                          "category": category, "query": f'"{names[parent]}" "{names[target]}" '
                          f'{CONTRACT["research"]["category_names"][category]} equity research initiation earnings update sector report filetype:pdf',
                          "source": "原始发布机构→用户授权终端→合法公开平台", "language": "zh/en",
                          "from": start, "to": cfg["as_of_date"], "status": "not_executed",
                          "goal": "先近后远；取得最新相关全文并阅读；旧全文不得取代最新发现"})
    for word in cfg["industry_keywords"]:
        tasks.append({"module": "04", "query": f'{word} 行业深度 供需 价格 竞争 industry outlook',
                      "source": "统计机构/行业协会/券商研究", "to": cfg["as_of_date"], "status": "not_executed"})
    for event in project_events(cfg, data):
        tasks.append({"module": "18", "query": f'{names[event["entity_id"]]} {event["description"]} 事件点评',
                      "from": event["date"], "to": cfg["as_of_date"], "status": "not_executed",
                      "source": "官方公告/事件后券商研究", "goal": "未找到事件后报告则登记覆盖滞后"})
    return {"type": "plan_only", "target": cfg["target"], "as_of_date": cfg["as_of_date"],
            "listed_entities": listed, "network": cfg["constraints"]["network"], "tasks": tasks,
            "stop_rule": "关键问题覆盖、重大冲突处理及边际信息收益共同决定；资源耗尽仅能交付受限结果。",
            "warning": "此输出不是检索记录，未访问任何外部来源。"}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", required=True)
    p.add_argument("--output", help="可选 JSON 路径，默认标准输出，不覆盖")
    args = p.parse_args()
    emit(plan(*read_project(args.project)), args.output)


if __name__ == "__main__":
    raise SystemExit(cli(main))
