"""生成可执行检索计划，不写入检索执行日志。"""
import argparse
from datetime import timedelta

from common import CONTRACT, cli, emit, iso_date, listed_entities, project_events, read_project, requirements


MODULE_TERMS = {
    "01": ("公司介绍 发展历史 注册号 股权 实际控制人 历史名称", "目标官网对应页/公司注册处/交易所原件"),
    "02": ("创始人 创始合伙人 背景 职责 贡献 董事 任职 离任", "官网团队历史页/具名访谈/任职公告/监管记录"),
    "03": ("产品 定价 收入构成 客户 留存", "财报/合同/产品文档"),
    "04": ("市场规模 供需 产业链", "统计机构/行业原始研究"),
    "05": ("主要竞争对手 替代产品 价格 渠道 客户 市场份额", "客户选择/竞品官网对应页与原始披露"),
    "06": ("复购 投诉 交付 单位经济", "客户记录/运营数据"),
    "07": ("增长 瓶颈 产能 融资 许可", "经营披露/供需证据"),
    "08": ("许可证 监管 政策 出口管制", "主管机关/现行规则"),
    "09": ("营销 获客 内容 活动 渠道 转化 订单 合同 验收 回款", "官网活动及案例原页/双方合同/客户侧披露"),
    "10": ("产能 质量 延期 连续性 灾备", "生产记录/认证机构"),
    "11": ("专利 开源 数据权利 安全 模型成本", "权利原件/产品文档"),
    "12": ("营收规模 收入结构 毛利率 净利率 财报 审计 现金流 应收 债务", "官网投资者关系/监管申报/审计报表及附注"),
    "13": ("诉讼 执行 处罚 和解 担保", "法院/监管原始记录"),
    "14": ("排放 安全 劳工 事故 整改", "监管/第三方核验"),
    "15": ("违约 欠薪 风险 澄清 反证", "原始案件/公司回应"),
    "16": ("估值 并购 对价 交割 净债务", "交易公告/可比披露"),
    "17": ("付款 交付 账期 担保 资金归集", "合同/付款记录/担保原件"),
    "18": ("年报 中报 公司深度 业绩点评", "交易所/券商原始发布"),
}

OFFICIAL_PAGES = (
    ("about", "01", "公司介绍 关于我们 主营业务 about company",
     "读取公司/品牌范围、产品客户与经营地区；保留公司自述属性。"),
    ("products_pricing", "03", "产品 服务 价格 定价 product service pricing",
     "读取实际产品、购买方式与价格条件，记录国家、币种、版本、促销和采样日。"),
    ("founders_team", "02", "创始人 合伙人 团队 职责 founders leadership team",
     "逐人读取相关背景、加入和任职时间、职责与贡献；区分创始合伙人与商务伙伴，现任与前任。"),
    ("history_news", "01", "发展历程 公司新闻 产品发布 历史 history news milestones",
     "提取事件日期、宣布/计划/已发生属性及业务变化；日期未知就保留未知，不用发布日期代替。"),
    ("locations_channels", "09", "门店 经营地区 销售渠道 stores locations channels",
     "区分已经营和计划地点、服务可达范围与销售实绩；不凭照片推定完整店网。"),
    ("investor_relations", "12", "投资者关系 年报 财报 经营数据 investor relations financial results",
     "读取营收规模、结构、利润率与财报原件；无此栏目时记录路径限制，继续其他财务来源。"),
    ("terms_identity", "01", "使用条款 隐私 支付 发行方 terms privacy payment publisher",
     "读取公开披露的服务、收款、数据控制及合同责任主体，不把不同角色自动等同。"),
    ("visual_assets", "01", "品牌标识 媒体资料 产品图 门店图 logo media press kit",
     "寻找真实Logo、官网界面、产品和门店素材；记录来源页/原图、权利依据、日期、展示范围与署名。"),
)


def official_site_tasks(cfg, data):
    """为目标基础阅读安排依赖任务；不猜URL、不访问网络、不记录完成。"""
    target_id = cfg["target_id"]
    entity = next((row for row in data["entity-map"] if row["entity_id"] == target_id), None)
    aliases = list(dict.fromkeys([cfg["target"], *(
        [entity["legal_name"], *(entity["aliases"] or [])] if entity else []
    )]))
    identity_id = f"official:{target_id}:identity"
    common = {
        "entity_id": target_id, "scope": "target_basics", "url": None,
        "language": "/".join(cfg["languages"]), "geography": (
            entity["geography"] if entity and entity["geography"] else cfg["geography"]
        ), "from": None, "to": cfg["as_of_date"], "status": "not_executed",
    }
    tasks = [{
        **common, "task_id": identity_id, "task_type": "official_site_identity",
        "module": "01", "aliases": aliases, "depends_on": [],
        "query": f'"{cfg["target"]}" 官网 official website',
        "source": "用户提供的入口/监管登记链接/App发行方/可靠双向关联",
        "goal": "先确认目标官网归属，登记实际URL和真实性依据；不凭同名、搜索排名或自称确认，不猜域名。",
        "completion_criteria": [
            "登记官网归属依据及真实性状态；无法确认时保留未解决状态。",
            "记录实际访问和时间信息；计划或搜索摘要不得写成页面已读。",
        ],
    }]
    for page_type, module, terms, goal in OFFICIAL_PAGES:
        tasks.append({
            **common, "task_id": f"official:{target_id}:{page_type}",
            "task_type": "official_site_page", "page_type": page_type, "module": module,
            "depends_on": [identity_id], "query": f'"{cfg["target"]}" {terms}',
            "source": "已确认官网的实际导航/站内搜索/观察到的真实链接",
            "goal": goal,
            "record_fields": [
                "actual_page_url", "title", "authenticity", "authenticity_basis",
                "published_date", "information_period", "accessed_date",
                "access_status", "locator", "evidence_ids", "limitations",
            ],
            "recording": "这些是待采集信息标签；按现有来源/证据/缺口台账字段存储，不新增CSV列。",
            "completion_criteria": [
                "直接阅读对应页正文；不能用首页、搜索摘要或猜测路径充当完成。",
                "记录页面存在与可访问程度、各类日期和具体定位；缺失/受限进入日志与缺口。",
                "公司自述不等于独立认证；离线时仅分析已有授权存档，不声称重新访问。",
            ],
        })
    return tasks


def verification_tasks(cfg, data):
    """将已有关键问题与缺口排在泛化关键词前；缺失的验证设计不代填。"""
    names = {r["entity_id"]: r["legal_name"] for r in data["entity-map"]}
    selected = set((cfg.get("completion_review") or {}).get("key_claim_ids", []))
    claims = [r for r in data["claim-register"]
              if r["claim_id"] in selected or r["materiality"] in ("critical", "major")]
    claims.sort(key=lambda r: (r["claim_id"] not in selected,
                              r["materiality"] != "critical", r["claim_id"]))
    tasks, linked = [], set()
    for claim in claims:
        gaps = [g for g in data["gap-register"]
                if g["status"] == "open" and claim["claim_id"] in (g["affected_claims"] or [])]
        linked.update(g["gap_id"] for g in gaps)
        priority = min(["P0" if claim["materiality"] == "critical" else "P1",
                        *(g["priority"] for g in gaps)])
        tasks.append({
            "task_id": f'verify:{claim["claim_id"]}', "task_type": "claim_verification",
            "entity_id": claim["entity_id"], "module": claim["module"], "claim_id": claim["claim_id"],
            "priority": priority,
            "question": claim["statement"], "known_assumptions": claim["assumptions"],
            "known_counterevidence": claim["counterevidence"], "open_questions": claim["unresolved"],
            "gap_ids": [g["gap_id"] for g in gaps],
            "evidence_needed": [{"needed": g["needed"], "path": g["acquisition_path"]} for g in gaps],
            "query": f'"{names.get(claim["entity_id"], cfg["target"])}" {claim["statement"]}',
            "goal": "检索前写清当前解释、竞争性解释、区分证据与改判条件；用可得原件检验，不以正负关键词数量替代验证。",
            "recording": "设计与结果沿用声明的 assumptions/counterevidence/unresolved 和关联缺口；不新增台账，不把空设计视为已执行。",
            "to": cfg["as_of_date"], "status": "not_executed",
        })
    for gap in sorted(data["gap-register"], key=lambda g: (g["priority"], g["gap_id"])):
        if gap["status"] != "open" or gap["gap_id"] in linked:
            continue
        tasks.append({
            "task_id": f'gap:{gap["gap_id"]}', "task_type": "gap_resolution", "gap_id": gap["gap_id"],
            "entity_id": gap["entity_id"], "module": gap["module"], "priority": gap["priority"],
            "question": gap["needed"], "source": gap["acquisition_path"],
            "query": f'"{names.get(gap["entity_id"], cfg["target"])}" {gap["needed"]}',
            "goal": "核实此缺口影响哪些核心问题，按获取路径补证；无法取得则记录具体影响与可成立的判断范围。",
            "to": cfg["as_of_date"], "status": "not_executed",
        })
    return tasks


def plan(cfg, data):
    as_of = iso_date(cfg["as_of_date"])
    # 官网基础阅读独立于模块裁剪；栏目不存在不等于已完成其他页面的阅读。
    tasks = verification_tasks(cfg, data) + official_site_tasks(cfg, data)
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
                    tasks.append({"task_type": "keyword_candidate",
                                  "entity_id": entity["entity_id"], "module": module, "alias": name,
                                  "query": f'"{name}" {terms}{english}', "source": source,
                                  "geography": entity["geography"] or cfg["geography"], "language": language,
                                  "from": None, "to": cfg["as_of_date"], "status": "not_executed",
                                  "goal": "候选查询，按关键问题和主体/语言相关性裁剪，无需逐条执行；正反证并查，无结果时换别名与来源"})
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
        tasks.append({"task_type": "keyword_candidate", "module": "04",
                      "query": f'{word} 行业深度 供需 价格 竞争 industry outlook',
                      "source": "统计机构/行业协会/券商研究", "to": cfg["as_of_date"], "status": "not_executed",
                      "goal": "候选查询，按实际细分市场和关键问题选择，不要求逐词执行"})
    for event in project_events(cfg, data):
        tasks.append({"module": "18", "query": f'{names[event["entity_id"]]} {event["description"]} 事件点评',
                      "from": event["date"], "to": cfg["as_of_date"], "status": "not_executed",
                      "source": "官方公告/事件后券商研究", "goal": "未找到事件后报告则登记覆盖滞后"})
    return {"type": "plan_only", "target": cfg["target"], "as_of_date": cfg["as_of_date"],
            "listed_entities": listed, "network": cfg["constraints"]["network"], "tasks": tasks,
            "stop_rule": "按约定核心问题审核证据、重大冲突和剩余缺口；研报检索须真实执行，资料取得不足保持原状态。关键问题仍不可判则受限，不能靠缩小范围宣称完成。",
            "warning": "此输出不是检索记录，未访问任何外部来源。"}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", required=True)
    p.add_argument("--output", help="可选 JSON 路径，默认标准输出，不覆盖")
    args = p.parse_args()
    emit(plan(*read_project(args.project)), args.output)


if __name__ == "__main__":
    raise SystemExit(cli(main))
