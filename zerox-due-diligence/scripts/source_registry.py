"""来源能力登记与选择。只读本地目录，不访问网络，不把计划写成已检索。"""
from __future__ import annotations

import argparse
import re

from common import ROOT, cli, fail, listed_entities, load_json


REGISTRY_PATH = ROOT / "references" / "sources" / "source-capabilities.json"
ID_RE = re.compile(r"^[a-z0-9]+(?:\.[a-z0-9_]+)+$")
MODULE_RE = re.compile(r"^(?:0[1-9]|1[0-8])$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CHECKED_RESULTS = ("entry_read", "access_blocked", "timeout", "empty_body")
UNCHECKED_RESULTS = ("not_executed", "not_connected")
FLAG_NAMES = (
    "listed", "brand", "consumer", "b2b_tech", "controversy", "cross_border",
    "sanctions_trigger", "legal_trigger", "procurement", "funding",
    "market_question", "employee", "digital_product",
)
SELECTION_KEYS = (
    "profile", "social", "budgets", "require_counterevidence_when_triggered",
    "include_capability_ids", "exclude_capability_ids",
)
BUDGET_KEYS = (
    "max_discover_tasks", "max_deepen_tasks", "max_social_tasks", "max_capability_tasks",
)
SOURCE_KEYS = (
    "capability_id", "name", "operator", "geography", "research_uses", "coverage",
    "ownership_form", "evidence_applicability", "applicability_note", "evidence_limits",
    "access_paths", "implementation", "verification", "fallback_capability_id",
    "selection", "lawful_access",
)
SELECTION_FIELDS = (
    "lane", "profiles", "geographies", "requires_any_signal", "priority", "social",
    "module", "entity_types",
)
BLOCKED_RESULTS = ("access_blocked", "timeout", "empty_body")
_REGISTRY = None


def default_selection():
    """与项目模板一致；缺字段的旧配置只在读取时补上，不回写。"""
    return {
        "profile": None,
        "social": "auto",
        "budgets": {
            "max_discover_tasks": 3,
            "max_deepen_tasks": 2,
            "max_social_tasks": 2,
            "max_capability_tasks": 8,
        },
        "require_counterevidence_when_triggered": True,
        "include_capability_ids": [],
        "exclude_capability_ids": [],
    }


def load_registry():
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = load_json(REGISTRY_PATH)
    return _REGISTRY


def _text(value, label):
    if not isinstance(value, str) or not value.strip():
        fail(f"{label} 必须为非空文字")
    return value.strip()


def _strings(value, label, allowed=None):
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
        fail(f"{label} 必须为非空字符串数组")
    if len(value) != len(set(value)):
        fail(f"{label} 含重复项")
    if allowed is not None and any(item not in allowed for item in value):
        fail(f"{label} 含未定义取值：{[item for item in value if item not in allowed]}")
    return value


def _optional_id_list(value, label):
    if not isinstance(value, list) or not all(isinstance(item, str) and ID_RE.fullmatch(item) for item in value):
        fail(f"{label} 必须为 capability_id 数组")
    if len(value) != len(set(value)):
        fail(f"{label} 含重复项")
    return value


def _count(value, label, upper=40):
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= upper:
        fail(f"{label} 必须为 0–{upper} 的整数")
    return value


def validate_selection_config(value, registry=None):
    """校验项目里的可选来源选择配置。不访问登记册以外的系统。"""
    if not isinstance(value, dict) or set(value) != set(SELECTION_KEYS):
        fail("source_selection 字段与模板不一致")
    registry = registry if registry is not None else load_registry()
    profiles = set(registry["vocabulary"]["profile"])
    profile = value["profile"]
    if profile is not None and profile not in profiles and profile != "auto":
        fail("source_selection.profile 无法识别")
    if value["social"] not in ("auto", "on", "off"):
        fail("source_selection.social 必须为 auto/on/off")
    budgets = value["budgets"]
    if not isinstance(budgets, dict) or set(budgets) != set(BUDGET_KEYS):
        fail("source_selection.budgets 字段与模板不一致")
    for key in BUDGET_KEYS:
        _count(budgets[key], key)
    if not isinstance(value["require_counterevidence_when_triggered"], bool):
        fail("require_counterevidence_when_triggered 必须为布尔值")
    _optional_id_list(value["include_capability_ids"], "include_capability_ids")
    _optional_id_list(value["exclude_capability_ids"], "exclude_capability_ids")
    return value


def validate_registry(registry=None):
    """校验能力登记自身。通过不表示任何来源当前可访问。"""
    registry = registry if registry is not None else load_registry()
    expected = {"registry_version", "catalog_note", "grade_rule", "distinct_from", "vocabulary", "sources"}
    if not isinstance(registry, dict) or set(registry) != expected:
        fail("来源能力登记顶层字段不正确")
    _text(registry["registry_version"], "registry_version")
    note = _text(registry["catalog_note"], "catalog_note")
    if "source-register" not in note or "未执行" not in note:
        fail("catalog_note 必须说明本登记不是 source-register，且未执行的核验不能当成已访问")
    grade_rule = _text(registry["grade_rule"], "grade_rule")
    if "S" not in grade_rule or "source-register" not in grade_rule:
        fail("grade_rule 必须说明能力登记不分配 S-D，等级只写在 source-register")
    if registry["distinct_from"] != "source-register":
        fail("能力登记必须与 source-register 区分")
    vocab = registry["vocabulary"]
    for key in ("ownership_form", "evidence_applicability", "access_kind", "access_available",
                "maturity", "verification_result", "verification_depth", "lane", "profile",
                "geography", "research_use"):
        _strings(vocab.get(key), f"vocabulary.{key}")
    if any(item in vocab["ownership_form"] or item in vocab["evidence_applicability"] for item in ("S", "A", "B", "C", "D")):
        fail("所有权形式和证据适用性不能用 S-D 等级表示")
    sources = registry["sources"]
    if not isinstance(sources, list) or not sources:
        fail("sources 不能为空")
    seen = set()
    for source in sources:
        if not isinstance(source, dict) or set(source) != set(SOURCE_KEYS):
            fail(f"来源字段不完整：{source.get('capability_id')!r}")
        sid = source["capability_id"]
        if not isinstance(sid, str) or not ID_RE.fullmatch(sid) or sid in seen:
            fail(f"capability_id 非法或重复：{sid!r}")
        seen.add(sid)
        _text(source["name"], f"{sid}.name")
        _text(source["operator"], f"{sid}.operator")
        _text(source["coverage"], f"{sid}.coverage")
        _text(source["applicability_note"], f"{sid}.applicability_note")
        _text(source["evidence_limits"], f"{sid}.evidence_limits")
        _text(source["lawful_access"], f"{sid}.lawful_access")
        if source["ownership_form"] not in vocab["ownership_form"]:
            fail(f"{sid}.ownership_form 未定义")
        _strings(source["geography"], f"{sid}.geography", vocab["geography"])
        _strings(source["research_uses"], f"{sid}.research_uses", vocab["research_use"])
        _strings(source["evidence_applicability"], f"{sid}.evidence_applicability", vocab["evidence_applicability"])
        if source["ownership_form"] in source["evidence_applicability"]:
            fail(f"{sid} 把所有权形式和证据适用性写成了同一标签")
        paths = source["access_paths"]
        if not isinstance(paths, list) or not paths:
            fail(f"{sid}.access_paths 不能为空")
        for path in paths:
            if not isinstance(path, dict) or set(path) != {"kind", "available", "url", "notes"}:
                fail(f"{sid} 访问路径字段不正确")
            if path["kind"] not in vocab["access_kind"] or path["available"] not in vocab["access_available"]:
                fail(f"{sid} 访问路径取值未定义")
            _text(path["notes"], f"{sid}.access_paths.notes")
            url = path["url"]
            if url is not None and (not isinstance(url, str) or not url.startswith("https://")):
                fail(f"{sid} 入口必须为空或 https URL")
            if path["available"] in ("reported_entry", "documented_untested") and not url:
                fail(f"{sid} 已声称的入口缺少 URL")
            if path["kind"] == "official_api" and path["available"] not in ("documented_untested", "not_available"):
                fail(f"{sid} 的官方接口只能标成未在本仓库测试，不能标成已接通")
        impl = source["implementation"]
        if not isinstance(impl, dict) or set(impl) != {"maturity", "connector", "automated_retrieval"}:
            fail(f"{sid}.implementation 字段不正确")
        if impl["maturity"] not in vocab["maturity"] or impl["connector"] is not False or impl["automated_retrieval"] is not False:
            fail(f"{sid} 不能声称已有连接器或自动抓取")
        ver = source["verification"]
        if not isinstance(ver, dict) or set(ver) != {"depth", "date", "result", "detail", "blockers"}:
            fail(f"{sid}.verification 字段不正确")
        if ver["depth"] not in vocab["verification_depth"] or ver["result"] not in vocab["verification_result"]:
            fail(f"{sid}.verification 取值未定义")
        _text(ver["detail"], f"{sid}.verification.detail")
        if not isinstance(ver["blockers"], list) or not all(isinstance(item, str) and item.strip() for item in ver["blockers"]):
            fail(f"{sid}.verification.blockers 必须为字符串数组")
        if ver["result"] in CHECKED_RESULTS:
            if not isinstance(ver["date"], str) or not DATE_RE.fullmatch(ver["date"]):
                fail(f"{sid} 已记录的入口核验必须有日期")
            if ver["depth"] == "none":
                fail(f"{sid} 已记录核验不能把深度标成 none")
            if ver["result"] != "entry_read" and not ver["blockers"]:
                fail(f"{sid} 受阻、超时或空正文必须写明 blocker")
            if impl["maturity"] != "entry_recorded":
                fail(f"{sid} 有入口核验记录时成熟度应为 entry_recorded")
        elif ver["result"] in UNCHECKED_RESULTS:
            if ver["date"] is not None or ver["depth"] != "none" or not ver["blockers"]:
                fail(f"{sid} 未执行或未接入的核验不能填写日期或假装已读入口")
            expected_maturity = "not_connected" if ver["result"] == "not_connected" else "catalog_only"
            if impl["maturity"] != expected_maturity:
                fail(f"{sid} 的成熟度与未核验状态不一致")
        else:
            fail(f"{sid}.verification.result 无法识别")
        fallback = source["fallback_capability_id"]
        if fallback is not None and (not isinstance(fallback, str) or not ID_RE.fullmatch(fallback) or fallback == sid):
            fail(f"{sid}.fallback_capability_id 非法")
        sel = source["selection"]
        if not isinstance(sel, dict) or set(sel) != set(SELECTION_FIELDS):
            fail(f"{sid}.selection 字段不正确")
        if sel["lane"] not in vocab["lane"] or sel["module"] is None or not MODULE_RE.fullmatch(str(sel["module"])):
            fail(f"{sid}.selection.lane/module 非法")
        _strings(sel["profiles"], f"{sid}.profiles", vocab["profile"])
        _strings(sel["geographies"], f"{sid}.geographies", vocab["geography"])
        if set(sel["geographies"]) != set(source["geography"]):
            fail(f"{sid} 的 geography 与 selection.geographies 不一致")
        if not isinstance(sel["requires_any_signal"], list) or any(item not in FLAG_NAMES for item in sel["requires_any_signal"]):
            fail(f"{sid}.requires_any_signal 含未知信号")
        _count(sel["priority"], f"{sid}.priority", 100)
        if not isinstance(sel["social"], bool):
            fail(f"{sid}.selection.social 必须为布尔值")
        if not isinstance(sel["entity_types"], list):
            fail(f"{sid}.entity_types 必须为数组")
        if sel["social"] and ("公开" not in source["lawful_access"] or "不得" not in source["lawful_access"]):
            fail(f"{sid} 的社交来源必须写明公开或授权边界")
        if any(token in source["lawful_access"] for token in ("绕过验证码即可", "购买匿名数据")):
            fail(f"{sid} 的访问说明不安全")
    known = {source["capability_id"] for source in sources}
    for source in sources:
        fallback = source["fallback_capability_id"]
        if fallback and fallback not in known:
            fail(f"{source['capability_id']} 的回退来源不存在：{fallback}")
    return registry


def _has(text, phrases, patterns=()):
    lowered = text.lower()
    if any(phrase.lower() in lowered for phrase in phrases):
        return True
    return any(re.search(pattern, lowered) for pattern in patterns)


def infer_context(cfg, data):
    """从配置、主体和问题读出选择信号。回答文本不参与，避免事后措辞反向扩大范围。"""
    geography = cfg.get("geography") or ""
    entity = next((row for row in data.get("entity-map", []) if row.get("entity_id") == cfg.get("target_id")), None)
    entity_type = entity.get("entity_type") if entity else ""
    question_text = " ".join(
        " ".join([item.get("question", ""), *item.get("sub_questions", [])])
        for item in cfg.get("key_questions") or [] if isinstance(item, dict))
    signal_text = " ".join([
        cfg.get("focus") or "", " ".join(cfg.get("industry_keywords") or []), question_text,
    ])
    home = []
    for code, phrases, patterns in (
        ("CN", ("中国大陆", "中国", "mainland china"), (r"\bcn\b",)),
        ("HK", ("香港", "hong kong"), (r"\bhk\b",)),
        ("MO", ("澳门", "macao", "macau"), ()),
        ("US", ("美国", "united states", "u.s."), (r"\busa\b", r"\bus\b")),
        ("GB", ("英国", "united kingdom", "britain"), (r"\buk\b", r"\bgb\b")),
        ("SG", ("新加坡", "singapore"), (r"\bsg\b",)),
        ("EU", ("欧盟", "欧洲", "european union"), (r"\beu\b",)),
    ):
        if _has(geography, phrases, patterns):
            home.append(code)
    consumer_words = _has(signal_text, (
        "消费者", "消费品", "零售", "门店", "电商", "c端", "2c", "consumer", "retail", "dtc", "餐饮", "口碑", "评价", "复购"))
    b2b = _has(signal_text, (
        "b2b", "企业服务", "saas", "软件", "专利", "开发者", "enterprise", "developer", "云计算", "半导体", "工业软件"))
    consumer = consumer_words or (entity_type == "brand" and not b2b)
    controversy = _has(signal_text, (
        "争议", "处罚", "诉讼", "造假", "丑闻", "欺诈", "lawsuit", "fraud", "召回", "监管措施", "制裁", "sanction"))
    sanction_words = _has(signal_text, ("制裁", "sanction", "sdn", "出口管制"))
    cross_border = _has(geography + " " + signal_text, ("出口", "跨境", "海外", "overseas", "export", "cross-border"))
    purpose = cfg.get("purpose")
    listed, _ = listed_entities(cfg, data) if data.get("entity-map") else ([], False)
    flags = {
        "listed": bool(listed),
        "brand": entity_type == "brand",
        "consumer": consumer,
        "b2b_tech": b2b,
        "controversy": controversy,
        "cross_border": cross_border,
        "sanction_words": sanction_words,
        "sanctions_trigger": sanction_words or cross_border or purpose in ("credit", "supplier", "investment", "acquisition"),
        "legal_trigger": controversy or purpose in ("credit", "supplier", "investment", "acquisition"),
        "procurement": _has(signal_text, ("采购", "招标", "投标", "政府采购", "procurement", "tender")),
        "funding": purpose in ("investment", "acquisition") or _has(signal_text, ("融资", "并购", "venture")),
        "market_question": _has(signal_text, ("市场", "行业", "规模", "market", "industry")),
        "employee": _has(signal_text, ("员工", "离职", "招聘", "雇主", "employer", "glassdoor", "脉脉", "workforce")),
        "digital_product": consumer or b2b or _has(signal_text, ("应用", "app", "软件", "网站", "saas", "小程序")),
        "explicit_social_words": _has(signal_text, (
            "小红书", "抖音", "微博", "微信公众号", "reddit", "linkedin", "领英", "知乎", "脉脉",
            "youtube", "官方账号", "社交媒体")),
    }
    return {"home": home, "entity_type": entity_type, "flags": flags, "listed_ids": list(listed)}


def infer_profiles(ctx):
    home = set(ctx["home"])
    flags = ctx["flags"]
    profiles = []
    if flags["consumer"] and home & {"CN", "HK", "MO"}:
        profiles.append("domestic_consumer")
    if flags["consumer"] and (home & {"US", "GB", "EU", "SG"} or flags["cross_border"]):
        profiles.append("overseas_product")
    if flags["b2b_tech"]:
        profiles.append("b2b_tech")
    if flags["listed"]:
        profiles.append("listed_company")
    if flags["controversy"]:
        profiles.append("controversy")
    if not profiles:
        profiles.append("general")
    return profiles


def social_enabled(mode, ctx):
    if mode == "off":
        return False
    if mode == "on":
        return True
    flags = ctx["flags"]
    return bool(flags["consumer"] or flags["b2b_tech"] or flags["employee"] or flags["explicit_social_words"])


def _scope_status(cfg, module):
    return ((cfg.get("module_scope") or {}).get(module) or {}).get("status")


def _match_source(source, ctx, exclude, cfg):
    sid = source["capability_id"]
    sel = source["selection"]
    if sid in exclude:
        return False
    if sel["lane"] == "reference_only":
        return False
    if ctx["entity_type"] == "person":
        return False
    if sel["entity_types"] and ctx["entity_type"] not in sel["entity_types"]:
        return False
    signals = sel["requires_any_signal"]
    if signals and not any(ctx["flags"].get(name) for name in signals):
        return False
    geos = set(sel["geographies"])
    home = set(ctx["home"])
    signal_hit = bool(signals) and any(ctx["flags"].get(name) for name in signals)
    geo_ok = bool(home) and (bool(home & geos) or ("global" in geos and signal_hit))
    if not geo_ok:
        return False
    if set(sel["profiles"]).isdisjoint(ctx["profiles"]):
        return False
    if sel["social"] and not ctx["social_on"]:
        return False
    status = _scope_status(cfg, sel["module"])
    if status in ("not_applicable", "deferred") and not signals:
        return False
    return True


def _prefer_path(paths):
    for kind in ("browser_public", "authorized_login", "user_material", "paid_terminal", "official_api"):
        for path in paths:
            if path["kind"] == kind and path["available"] != "not_available":
                return path
    return paths[0]


def _task(cfg, source, role, primary_id=None):
    sid = source["capability_id"]
    target_id = cfg["target_id"]
    verification = dict(source["verification"])
    verification["not_this_project"] = True
    social = bool(source["selection"]["social"]) or source["ownership_form"] in (
        "social_platform", "user_review", "employee_discussion")
    goal = (
        f"按预算核对「{source['name']}」能否覆盖当前问题。目录核验不是本次访问。"
        "真正读到的文件另登记 source-register，再按证据标准分开评级；来源类型本身不决定真伪。"
    )
    if role == "include":
        goal = "配置点名了此来源。" + goal
    if role == "fallback":
        goal = (
            f"能力登记把 {primary_id} 记为入口受阻、超时或空正文，因此把「{source['name']}」列为回退。"
            "登记日期不是本次项目的访问日。回退任务同样尚未执行。"
        )
    if social:
        goal += "社交和评价只作线索：区分原发与转载、账号身份和商业激励，保留时间、链接和上下文。负向样本占比不是不满率。"
    return {
        "task_id": f"source:{target_id}:{sid}",
        "task_type": "source_capability",
        "status": "not_executed",
        "role": role,
        "capability_id": sid,
        "entity_id": target_id,
        "module": source["selection"]["module"],
        "depends_on": [],
        "query": f'"{cfg.get("target") or target_id}" {source["name"]}',
        "source": source["name"],
        "goal": goal,
        "access_paths": source["access_paths"],
        "preferred_access_path": _prefer_path(source["access_paths"]),
        "implementation": dict(source["implementation"]),
        "catalog_verification": verification,
        "fallback_capability_id": source["fallback_capability_id"],
        "fallback_for": primary_id,
        "ownership_form": source["ownership_form"],
        "evidence_applicability": list(source["evidence_applicability"]),
        "applicability_note": source["applicability_note"],
        "lawful_access": source["lawful_access"],
        "social_guidance": "references/sources/social-evidence.md" if social else None,
        "to": cfg.get("as_of_date"),
        "network": (cfg.get("constraints") or {}).get("network", "unknown"),
    }


def _with_brand_dependency(task, cfg, source, entity_type):
    uses = set(source["research_uses"])
    if entity_type == "brand" and uses & {"registration", "identity", "control"} and "brand_trace" not in uses:
        task["depends_on"] = [f"brand:{cfg['target_id']}:resolution"]
        task["goal"] += " 品牌目标要先完成主体追溯；同名登记在经营主体明确前不能当作目标本身。"
    return task


def build_source_plan(cfg, data, registry=None):
    """生成能力任务和未选项说明。全部 status 保持 not_executed。"""
    registry = validate_registry(registry if registry is not None else load_registry())
    selection = cfg.get("source_selection") or default_selection()
    validate_selection_config(selection, registry)
    by_id = {source["capability_id"]: source for source in registry["sources"]}
    unknown = [sid for sid in [*selection["include_capability_ids"], *selection["exclude_capability_ids"]]
               if sid not in by_id]
    if unknown:
        fail("未知 capability_id：" + "、".join(unknown))
    ctx = infer_context(cfg, data)
    explicit = selection["profile"] not in (None, "auto")
    if explicit:
        profiles = [selection["profile"]]
        if ctx["flags"]["listed"] and "listed_company" not in profiles:
            profiles.append("listed_company")
        if ctx["flags"]["controversy"] and "controversy" not in profiles:
            profiles.append("controversy")
        mode = "explicit"
    else:
        profiles = infer_profiles(ctx)
        mode = "auto"
    ctx["profiles"] = profiles
    ctx["social_on"] = social_enabled(selection["social"], ctx)
    exclude = set(selection["exclude_capability_ids"])
    notes = []
    if ctx["entity_type"] == "person":
        notes.append({"code": "person_target_rejected", "detail": "自然人不作为本研究目标，不为其生成来源任务。"})
    if not ctx["home"]:
        notes.append({"code": "geography_unspecified", "detail": "未识别登记辖区，不猜测登记机关，也不把全球来源全部摊开。"})
    if not ctx["social_on"]:
        notes.append({"code": "social_not_triggered", "detail": "未触发消费者口碑、雇主讨论或显式社交问题；不逐个平台检查。"})
    if not ctx["flags"]["sanctions_trigger"]:
        notes.append({"code": "sanctions_not_triggered", "detail": "未触发跨境、制裁、授信、供应商准入或并购投资的名单筛查。"})

    eligible = [source for source in registry["sources"] if _match_source(source, ctx, exclude, cfg)]

    def ordered(social):
        rows = [source for source in eligible if bool(source["selection"]["social"]) is social
                and source["selection"]["lane"] in ("discover", "deepen")]
        return sorted(rows, key=lambda source: (source["selection"]["priority"], source["capability_id"]))

    discover = [source for source in ordered(False) if source["selection"]["lane"] == "discover"]
    deepen = [source for source in ordered(False) if source["selection"]["lane"] == "deepen"]
    social = ordered(True)
    budgets = selection["budgets"]
    max_cap = budgets["max_capability_tasks"]
    need_counter = bool(selection["require_counterevidence_when_triggered"] and (
        ctx["flags"]["controversy"] or ctx["flags"]["sanctions_trigger"] or (ctx["social_on"] and social)))
    reserved = 1 if need_counter and max_cap >= 1 else 0
    if need_counter and reserved == 0:
        notes.append({"code": "counterevidence_deferred", "detail": "反证任务因能力任务预算为 0 而未生成。这不是无风险，也不是已查找反证。"})
    selected = []
    selected_ids = set()
    deferred = []

    def room():
        return len(selected) < max(0, max_cap - reserved)

    def take(pool, limit, role):
        kept = 0
        for source in pool:
            sid = source["capability_id"]
            if sid in selected_ids:
                continue
            if kept >= limit or not room():
                deferred.append(_deferred(source, "budget", role))
            else:
                selected.append((source, role, None))
                selected_ids.add(sid)
                kept += 1

    take(discover, budgets["max_discover_tasks"], "discover")
    take(deepen, budgets["max_deepen_tasks"], "deepen")
    if ctx["social_on"]:
        take(social, budgets["max_social_tasks"], "social")

    for source, role, _primary in list(selected):
        fallback_id = source["fallback_capability_id"]
        if source["verification"]["result"] not in BLOCKED_RESULTS or not fallback_id:
            continue
        if fallback_id in exclude:
            notes.append({"code": "fallback_excluded", "detail": f"{source['capability_id']} 的回退 {fallback_id} 已在配置中排除。"})
            continue
        fallback = by_id[fallback_id]
        if fallback["selection"]["lane"] == "reference_only":
            notes.append({"code": "fallback_existing_task",
                          "detail": f"{source['capability_id']} 的回退 {fallback_id} 已有单独计划任务，不重复生成。"})
            continue
        if fallback_id in selected_ids:
            continue
        if not room():
            deferred.append(_deferred(fallback, "budget_fallback", "fallback", source["capability_id"]))
        else:
            selected.append((fallback, "fallback", source["capability_id"]))
            selected_ids.add(fallback_id)

    for sid in selection["include_capability_ids"]:
        if sid in exclude or sid in selected_ids:
            continue
        selected.append((by_id[sid], "include", None))
        selected_ids.add(sid)
    deferred = [item for item in deferred if item["capability_id"] not in selected_ids]
    if explicit and not any(role == "discover" for _source, role, _primary in selected):
        notes.append({"code": "profile_geography_mismatch",
                      "detail": "指定档案与已识别辖区没有匹配的发现来源；未改用其他辖区的登记机关充数。"})
    tasks = []
    for source, role, primary in selected:
        task = _with_brand_dependency(_task(cfg, source, role, primary), cfg, source, ctx["entity_type"])
        status = _scope_status(cfg, source["selection"]["module"])
        if status in ("not_applicable", "deferred") and source["selection"]["requires_any_signal"]:
            task["module_scope_override"] = status
            task["goal"] += f" 模块 {source['selection']['module']} 当前标记为 {status}，因问题信号仍列入计划；这不改写模块裁剪。"
        tasks.append(task)
    if reserved:
        tasks.append({
            "task_id": f"source:{cfg['target_id']}:counterevidence",
            "task_type": "source_counterevidence",
            "status": "not_executed",
            "role": "counterevidence",
            "capability_id": None,
            "entity_id": cfg["target_id"],
            "module": "15",
            "depends_on": [],
            "query": None,
            "source": "独立原件、当事人回应与已选来源的同源分组",
            "goal": ("为已触发的登记、名单、口碑或争议线索同时寻找支持证据和反证，优先核对独立形成的官方记录或当事人原文。"
                     "负向样本占比不是客户不满率；检索无结果不是无风险。来源类型、平台和目录记录都不能单独决定真伪。本任务尚未执行。"),
            "social_guidance": "references/sources/social-evidence.md" if ctx["social_on"] else None,
            "to": cfg.get("as_of_date"),
            "network": (cfg.get("constraints") or {}).get("network", "unknown"),
        })
    return {
        "tasks": tasks,
        "summary": {
            "profile_mode": mode,
            "profiles": profiles,
            "home_geographies": ctx["home"],
            "flags": ctx["flags"],
            "social_triggered": ctx["social_on"],
            "budgets": dict(budgets),
            "selected": [{"capability_id": source["capability_id"], "role": role, "priority": source["selection"]["priority"]}
                         for source, role, _primary in selected],
            "deferred": deferred,
            "excluded": sorted(exclude),
            "notes": notes,
            "catalog_verification_is_not_current_access": True,
            "execution": "not_executed",
            "stop_rule": "发现来源按辖区和问题从宽列入预算；加深和社交只在触发后、并在各自预算内选择。预算用尽记为 deferred，不写成已检索、无结果或无风险。触发口碑、名单或争议时保留反证任务。",
        },
    }


def _deferred(source, reason, role, primary_id=None):
    item = {
        "capability_id": source["capability_id"],
        "reason": reason,
        "role": role,
        "implementation_maturity": source["implementation"]["maturity"],
        "catalog_verification_result": source["verification"]["result"],
    }
    if primary_id:
        item["for"] = primary_id
    return item


def summarize_search_log(rows):
    """汇总已经写入 search-log 的状态。没有记录的计划任务不在这里出现。"""
    by_status = {}
    retrieved, inaccessible, not_found, not_executed = [], [], [], []
    for row in rows:
        status = row["status"]
        by_status[status] = by_status.get(status, 0) + 1
        if status == "found":
            retrieved.extend(row.get("source_ids") or [])
        elif status in ("access_blocked", "failed"):
            inaccessible.append(row["search_id"])
        elif status == "not_found":
            not_found.append(row["search_id"])
        elif status == "not_executed":
            not_executed.append(row["search_id"])
    return {
        "recorded_attempts": len(rows),
        "by_status": by_status,
        "retrieved_source_ids": sorted(set(retrieved)),
        "inaccessible_search_ids": inaccessible,
        "not_found_search_ids": not_found,
        "not_executed_search_ids": not_executed,
        "meaning": "只汇总已写入 search-log 的记录。未写入的计划不是已检索；无记录不是无风险。能力登记里的历史核验也不是本次访问。",
    }


def search_log_warnings(rows):
    warnings = []
    for row in rows:
        status = row["status"]
        limitation = (row.get("limitations") or "").strip()
        if status == "not_executed":
            warnings.append(f"{row['search_id']}：检索日志中的未执行记录不能当作已经搜索")
        elif status == "found" and not (row.get("source_ids") or []):
            warnings.append(f"{row['search_id']}：结果为 found 但未关联 source-register，不能当作已取得原件")
        elif status in ("access_blocked", "failed") and not limitation:
            warnings.append(f"{row['search_id']}：不可访问或失败时要写明限制，不能留空后视为已覆盖")
    return warnings


def search_log_preamble(rows):
    summary = summarize_search_log(rows)
    counts = "，".join(f"{key} {summary['by_status'][key]}" for key in sorted(summary["by_status"])) or "无"
    return (
        f"已记录检索 {summary['recorded_attempts']} 条（{counts}）。"
        f"已关联来源：{('、'.join(summary['retrieved_source_ids']) or '无')}。"
        f"不可访问或失败：{('、'.join(summary['inaccessible_search_ids']) or '无')}。"
        f"未找到：{('、'.join(summary['not_found_search_ids']) or '无')}。"
        f"日志中的未执行：{('、'.join(summary['not_executed_search_ids']) or '无')}。"
        "未出现在本表的计划任务都尚未执行。无记录不代表已经覆盖，也不代表没有风险。"
        "社交和评价门禁只在相应问题触发后适用，不要求每个平台都留下记录。\n\n"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate", action="store_true", help="只校验本地能力登记，不访问网络")
    args = parser.parse_args()
    if not args.validate:
        fail("请使用 --validate；选择来源请运行 search_plan.py")
    registry = validate_registry()
    from common import dumps
    print(dumps({
        "status": "registry_valid",
        "sources": len(registry["sources"]),
        "connectors": 0,
        "meaning": "登记结构有效。这不是连通性测试，也不表示所列来源当前可访问。",
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(cli(main))
