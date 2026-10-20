"""阅读稿数据校验。只验证可机器判断的约束，事实支持关系仍须人工复核。"""
import re
from datetime import date
from urllib.parse import urlsplit

from common import fail, finite

KINDS = {"actual": "历史数据", "estimate": "估算", "forecast": "预测", "company_claim": "企业自述", "mixed": "含不同数据属性"}
PROCESS_TITLES = r"检索日志|模块适用|研究完成范围|评分覆盖|完整声明核验|访谈提纲|资料请求清单|research coverage|search log"
READER_TOPICS = {
    "identity": "公司是什么类型的业务，品牌与法律主体如何区分",
    "history_team": "何时创立、谁创办、处于什么发展阶段",
    "offering": "卖什么产品或服务，怎样定位与定价",
    "customers_markets": "谁使用、谁付款，面向哪些客户与市场",
    "transaction_flow": "一笔典型交易如何从需求走到交付和回款",
    "operating_model": "谁设计、生产、交付与服务，哪些自营、哪些依赖外部",
    "revenue_costs": "收入如何产生，主要成本与利润驱动是什么",
    "differentiation": "客户为什么选择它，差异化有哪些依据和边界",
}
EXTRA_TOPICS = {
    "financial_performance": "营收规模、营收构成、毛利率和净利率分别有什么依据、口径及缺口",
    "marketing": "通过什么渠道和营销方式获取客户，转化与复购效果如何",
    "competition": "主要竞争对手是谁，为什么可比，哪些维度相近或不同",
}
LEGACY_TOPICS = dict(READER_TOPICS)
READER_TOPICS.update(EXTRA_TOPICS)
BASIS = {"evidence": "资料支持", "company_claim": "公司口径", "inference": "分析示意", "unknown": "待核实"}


def validate_content(content, cfg, data):
    evidence = {r["evidence_id"]: r for r in data["evidence-ledger"]}
    entities = {r["entity_id"] for r in data["entity-map"]} | {"industry"}
    used = set()
    chart_count = 0
    warnings = []
    explanations = {}
    business_flows = 0
    history_sections = []
    people_sections = []
    images = 0
    matrices = 0

    def obj(value, required, optional, label):
        if not isinstance(value, dict):
            fail(f"{label} 必须为对象")
        missing, extra = set(required) - value.keys(), value.keys() - set(required) - set(optional)
        if missing or extra:
            fail(f"{label} 字段不符：缺少 {sorted(missing)}；未知 {sorted(extra)}")

    def text(value, label):
        if not isinstance(value, str) or not value.strip():
            fail(f"{label} 必须为非空文字")
        if "{{" in value or "}}" in value:
            fail(f"{label} 残留模板占位符")
        for token in re.findall(r"\[(E-[^\]\s]+)\]", value):
            refs([token], label)

    def array(value, label, minimum=1):
        if not isinstance(value, list) or len(value) < minimum:
            fail(f"{label} 必须为至少 {minimum} 项的数组")

    def refs(value, label):
        array(value, f"{label} 证据")
        for eid in value:
            if not isinstance(eid, str) or eid not in evidence:
                fail(f"{label} 引用不存在：{eid}")
            used.add(eid)

    def numeric(item, label, allow_null=False):
        if allow_null and item["value"] is None:
            return
        finite(item["value"], label)

    def scope(item, label):
        for field in ("unit", "period", "entity_id", "note"):
            text(item[field], f"{label}.{field}")
        if item["entity_id"] not in entities:
            fail(f"{label} 主体不存在：{item['entity_id']}")
        if not isinstance(item["kind"], str) or item["kind"] not in KINDS:
            fail(f"{label} 数据属性非法：{item['kind']}")
        refs(item["evidence_ids"], label)

    def attribute(kind, ids):
        if kind == "actual" and any(evidence[eid]["attribute"] in ("forecast", "estimate") for eid in ids):
            fail("预测或估算证据不得标为历史实际数据")

    obj(content, ["version", "title", "subtitle", "language", "summary", "scope_note", "sections"], [], "阅读稿")
    if content["version"] not in ("1.0", "1.1", "1.2") or content["language"] not in ("zh-CN", "en"):
        fail("阅读稿版本需为 1.2（历史稿兼容 1.0/1.1）；language 需为 zh-CN 或 en")
    current = content["version"] == "1.2"
    explained = content["version"] in ("1.1", "1.2")
    topics = READER_TOPICS if current else LEGACY_TOPICS
    for field in ("title", "subtitle", "summary", "scope_note"):
        text(content[field], field)
    array(content["sections"], "sections")
    ids = {"main", "overview", "sources", "evidence", "report-data", "toc-toggle"}
    for section in content["sections"]:
        obj(section, ["id", "title", "blocks"], ["summary"], "章节")
        sid = section["id"]
        if not isinstance(sid, str) or not re.fullmatch(r"[a-z][a-z0-9-]*", sid) or sid in ids or sid.startswith(("chart-", "ref-", "topic-")):
            fail(f"章节 ID 不合法或重复：{sid}")
        ids.add(sid)
        text(section["title"], "章节标题")
        if re.search(PROCESS_TITLES, section["title"], re.I):
            fail(f"过程章节应移到底稿：{section['title']}")
        if "summary" in section:
            text(section["summary"], "章节摘要")
        array(section["blocks"], "blocks")
        for block in section["blocks"]:
            if not isinstance(block, dict):
                fail("内容块必须为对象")
            kind = block.get("type")
            if kind in ("people", "image", "matrix") and not current:
                fail(f"{kind} 内容需要 version=1.2")
            if kind == "explanation":
                if not explained:
                    fail("explanation 内容需要 version=1.1 或 1.2")
                obj(block, ["type", "topic", "title", "text", "status", "evidence_ids", "limitations"], [], kind)
                topic = block["topic"]
                if not isinstance(topic, str) or topic not in topics:
                    fail(f"未知理解主题：{topic}")
                if topic in explanations:
                    fail(f"理解主题重复：{topic}；同一主题集中解释，其他章节可补充")
                if block["status"] not in ("supported", "partial", "unknown"):
                    fail(f"理解主题状态非法：{topic}")
                text(block["title"], f"{topic} 标题")
                text(block["text"], f"{topic} 正文")
                if not isinstance(block["limitations"], str):
                    fail(f"{topic} limitations 必须为文字")
                if block["status"] in ("partial", "unknown"):
                    text(block["limitations"], f"{topic} 未知范围与影响")
                elif block["limitations"]:
                    text(block["limitations"], f"{topic} 边界")
                array(block["evidence_ids"], f"{topic} 证据", 0 if block["status"] == "unknown" else 1)
                if block["evidence_ids"]:
                    refs(block["evidence_ids"], topic)
                explanations[topic] = {"status": block["status"], "section_id": sid,
                                       "evidence_ids": block["evidence_ids"], "limitations": block["limitations"]}
            elif kind == "people":
                obj(block, ["type", "title", "profiles"], [], kind)
                text(block["title"], "人物介绍标题")
                array(block["profiles"], "人物")
                people_sections.append(sid)
                for person in block["profiles"]:
                    obj(person, ["name", "role", "period", "background", "contribution", "limitations", "evidence_ids"], [], "人物")
                    for field in ("name", "role", "period", "background", "contribution"):
                        text(person[field], f"人物.{field}")
                    if not isinstance(person["limitations"], str):
                        fail("人物 limitations 必须为文字")
                    if person["limitations"]:
                        text(person["limitations"], "人物边界")
                    refs(person["evidence_ids"], "人物")
            elif kind == "image":
                obj(block, ["type", "role", "path", "title", "alt", "caption", "source_url", "captured_at", "usage_note", "evidence_ids"], [], kind)
                for field in ("path", "title", "alt", "caption", "captured_at", "usage_note"):
                    text(block[field], f"图片.{field}")
                if block["role"] not in ("logo", "website", "product", "store", "people", "other"):
                    fail("图片 role 非法")
                if not isinstance(block["source_url"], str):
                    fail("图片 source_url 必须为网址文字或空串；本地材料通过证据台账定位")
                try:
                    if block["source_url"]:
                        url = urlsplit(block["source_url"])
                        if url.scheme not in ("https", "http") or not url.netloc or url.username or url.password:
                            raise ValueError("不安全的 URL")
                    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", block["captured_at"]):
                        raise ValueError("日期格式")
                    date.fromisoformat(block["captured_at"])
                except ValueError:
                    fail("图片非空来源须为安全 HTTP(S) URL，取得日期须为 YYYY-MM-DD")
                refs(block["evidence_ids"], "图片")
                if block["captured_at"] > cfg["as_of_date"]:
                    warnings.append("图片取得时间晚于研究截止日，须确认历史状态可比性，不得把当前图片当历史实景。")
                images += 1
            elif kind == "matrix":
                obj(block, ["type", "title", "columns", "rows", "note"], ["purpose"], kind)
                text(block["title"], "矩阵标题")
                text(block["note"], "矩阵口径")
                if block.get("purpose", "other") not in ("competition", "marketing", "financial", "other"):
                    fail("矩阵 purpose 非法")
                array(block["columns"], "矩阵列", 2)
                for label in block["columns"]:
                    text(label, "矩阵列标题")
                array(block["rows"], "矩阵行")
                for row in block["rows"]:
                    obj(row, ["label", "cells"], [], "矩阵行")
                    text(row["label"], "矩阵行标题")
                    array(row["cells"], "矩阵单元格")
                    if len(row["cells"]) != len(block["columns"]):
                        fail("矩阵行列数量不符")
                    for cell in row["cells"]:
                        obj(cell, ["text", "basis", "evidence_ids"], [], "矩阵单元格")
                        text(cell["text"], "矩阵单元格")
                        if not isinstance(cell["basis"], str) or cell["basis"] not in BASIS:
                            fail("矩阵依据非法")
                        array(cell["evidence_ids"], "矩阵证据", 0 if cell["basis"] == "unknown" else 1)
                        if cell["evidence_ids"]:
                            refs(cell["evidence_ids"], "矩阵")
                matrices += 1
            elif kind == "text":
                obj(block, ["type", "text"], [], kind)
                text(block["text"], kind)
            elif kind == "bullets":
                obj(block, ["type", "items"], [], kind)
                array(block["items"], kind)
                for item in block["items"]:
                    text(item, kind)
            elif kind == "callout":
                obj(block, ["type", "title", "text"], [], kind)
                text(block["title"], kind)
                text(block["text"], kind)
            elif kind == "table":
                obj(block, ["type", "title", "columns", "rows", "note"], [], kind)
                text(block["title"], kind)
                text(block["note"], kind)
                array(block["columns"], kind)
                array(block["rows"], kind)
                for col in block["columns"]:
                    text(col, "列名")
                for row in block["rows"]:
                    array(row, "数据行")
                    if len(row) != len(block["columns"]):
                        fail("表格行列数量不符")
                    for cell in row:
                        text(cell, "单元格")
            elif kind == "metrics":
                obj(block, ["type", "items"], [], kind)
                array(block["items"], kind)
                for item in block["items"]:
                    obj(item, ["label", "value", "unit", "period", "entity_id", "kind", "evidence_ids", "note"], [], "指标")
                    text(item["label"], "指标名")
                    scope(item, "指标")
                    numeric(item, "指标")
                    attribute(item["kind"], item["evidence_ids"])
                    if item["kind"] == "mixed":
                        fail("单个指标不能为 mixed")
            elif kind == "chart":
                obj(block, ["type", "chart_type", "title", "unit", "period", "entity_id", "kind", "evidence_ids", "note", "points"], [], kind)
                text(block["title"], "图题")
                scope(block, "图表")
                if block["chart_type"] not in ("bar", "line", "donut"):
                    fail("chart_type 仅支持 bar / line / donut")
                array(block["points"], "数据点", 2)
                if len(block["points"]) > 24:
                    fail("单图最多 24 个数据点；应拆图以便阅读")
                labels = set()
                known = []
                for point in block["points"]:
                    obj(point, ["label", "value"], ["kind", "period", "evidence_ids"], "数据点")
                    text(point["label"], "数据点标签")
                    if point["label"] in labels:
                        fail("图表数据点标签重复")
                    labels.add(point["label"])
                    numeric(point, "图表数值", allow_null=True)
                    point_kind = point.get("kind", block["kind"])
                    if not isinstance(point_kind, str) or point_kind not in KINDS or point_kind == "mixed":
                        fail("mixed 图表的每个数据点必须给出独立 kind")
                    if "period" in point:
                        text(point["period"], "数据点期间")
                    point_refs = point.get("evidence_ids", block["evidence_ids"])
                    refs(point_refs, "数据点")
                    attribute(point_kind, point_refs)
                    if point["value"] is not None:
                        known.append(point["value"])
                    if block["chart_type"] == "donut" and (point["value"] is None or point["value"] < 0):
                        fail("构成图不允许缺失或负值")
                if len(known) < 2:
                    fail("可比较的已知数值不足两个，改用指标或文字说明")
                if block["chart_type"] == "donut" and (sum(known) <= 0 or len(known) > 6):
                    fail("构成图需要正总量且不超过六项")
                chart_count += 1
            elif kind in ("timeline", "process"):
                obj(block, ["type", "title", "items"], ["purpose", "ordering"] if kind == "process" else (["purpose"] if current else []), kind)
                text(block["title"], kind)
                array(block["items"], kind)
                if kind == "timeline" and "purpose" in block:
                    if block["purpose"] not in ("company_history", "other"):
                        fail("时间线 purpose 需为 company_history / other")
                    if block["purpose"] == "company_history":
                        array(block["items"], "公司发展时间线", 2)
                        history_sections.append(sid)
                business = kind == "process" and block.get("purpose") == "business_model"
                if kind == "process" and block.get("purpose", "other") not in ("business_model", "recommendation", "other"):
                    fail("流程 purpose 需为 business_model / recommendation / other")
                if kind == "process" and block.get("ordering", "sequence") not in ("sequence", "conceptual"):
                    fail("流程 ordering 需为 sequence / conceptual")
                if business:
                    array(block["items"], "业务过程图", 2)
                    business_flows += 1
                for item in block["items"]:
                    required = ["title", "text", "evidence_ids"]
                    if kind == "timeline":
                        required += ["date", "status"]
                    elif business:
                        required += ["basis"]
                    obj(item, required, ["basis"] if kind == "process" and not business else [], kind)
                    text(item["title"], kind)
                    text(item["text"], kind)
                    basis = item.get("basis", "evidence")
                    if not isinstance(basis, str) or basis not in BASIS:
                        fail("流程依据需为 evidence / company_claim / inference / unknown")
                    if basis == "unknown":
                        array(item["evidence_ids"], "未知环节证据", 0)
                        if item["evidence_ids"]:
                            refs(item["evidence_ids"], kind)
                    else:
                        refs(item["evidence_ids"], kind)
                    if kind == "timeline":
                        text(item["date"], "时间")
                        if item["status"] not in ("completed", "planned"):
                            fail("时间线状态需为 completed 或 planned")
                        if block.get("purpose") == "company_history" and item["status"] == "completed" and any(evidence[eid]["attribute"] == "forecast" for eid in item["evidence_ids"]):
                            fail("预测事件不得写成已完成的公司发展节点")
            else:
                fail(f"未知内容块：{kind}")
    if chart_count == 0:
        warnings.append("正文没有定量图表；人工核查是否确实无可比数据，不能用指标卡或定性图替代可用的数字分析。")
    if explained:
        missing = topics.keys() - explanations.keys()
        if missing:
            fail("正文遗漏理解主题：" + "；".join(f"{key}（{READER_TOPICS[key]}）" for key in topics if key in missing))
        if not business_flows and explanations["transaction_flow"]["status"] != "unknown":
            fail("缺少 purpose=business_model 的业务过程图；合作建议流程不能替代业务解释")
        if not business_flows:
            warnings.append("交易过程尚不清楚，已披露限制并免画业务图；不得据此宣称已理解或验证商业模式。")
        if all(item["status"] == "unknown" for item in explanations.values()):
            warnings.append("全部理解主题均未知；当前只能交付问题边界，不能形成公司的实质评价。")
    if current:
        identity_section = explanations["identity"]["section_id"]
        if history_sections and any(sid != identity_section for sid in history_sections):
            fail("公司发展时间线需放在公司介绍所在章节")
        if not history_sections:
            history = explanations["history_team"]
            if history["status"] == "supported" or not history["limitations"].strip():
                fail("缺少公司发展时间线；不足两个有据事件时须在 history_team 中说明限制")
            warnings.append("未绘公司发展时间线：人工核查确实不足两个有据事件，不能省略已有沿革资料。")
        if identity_section in people_sections:
            fail("创始人/合伙人介绍需使用独立章节，不能混入公司身份章节")
        if not people_sections:
            warnings.append("未单列人物介绍：核查是否确实无足够公开资料；有材料时应以独立章节介绍创始人/合伙人。")
        if not images:
            warnings.append("未使用真实企业素材：核查官网Logo、产品/门店或官网截图是否可取得并适当使用，不能以占位或生成图冒充。")
    else:
        warnings.append(f"旧版 {content['version']} 阅读稿未通过 1.2 财务、营销、竞争及展示契约；新生成请迁移至 1.2。")
    return {"used_evidence": sorted(used), "chart_count": chart_count, "warnings": warnings,
            "reader_coverage": {"status": "mapped" if current else "legacy_unchecked",
                                "topics": explanations, "business_flow_count": business_flows,
                                "company_timeline_count": len(history_sections), "people_block_count": len(people_sections),
                                "image_count": images, "matrix_count": matrices,
                                "meaning": "只检查必答主题的结构映射；须独立阅读正文并复述，不能据此认定解释充分或事实正确。"}}
