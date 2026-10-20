"""共享数据契约、实体关系、台账校验和安全文件操作。仅依赖标准库。"""
from __future__ import annotations

import csv
import io
import json
import math
import os
import re
import sys
import tempfile
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class InputError(ValueError):
    """用户可修复的输入或契约错误。"""


def load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"),
                          parse_constant=lambda x: fail(f"非法数值：{x}"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise InputError(f"无法读取 JSON {path}：{exc}") from exc


def fail(message):
    raise InputError(message)


CONTRACT = load_json(ROOT / "schemas/data-contract.json")


def finite(value, label="数值"):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        fail(f"{label} 必须为有限数值，不能为布尔值")
    return float(value)


def iso_date(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        fail(f"非法日期：{value!r}，应为 YYYY-MM-DD")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise InputError(f"非法日期：{value}") from exc


def iso_time(value):
    try:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            fail("日期时间必须包含时区")
        return parsed
    except (ValueError, TypeError) as exc:
        raise InputError(f"非法日期时间：{value}") from exc


def dumps(value):
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def safe_write(path, text, overwrite=False):
    """新文件用独占创建；显式覆盖先写临时文件，再原子替换。"""
    path = Path(path)
    if not overwrite:
        with path.open("x", encoding="utf-8", newline="") as handle:
            handle.write(text)
        return
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="",
                                     dir=path.parent, delete=False) as handle:
        temp = Path(handle.name)
        handle.write(text)
    try:
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def emit(value, output=None, overwrite=False):
    content = dumps(value)
    if output:
        safe_write(output, content, overwrite)
    else:
        print(content, end="")


def cli(main):
    try:
        return main() or 0
    except (InputError, OSError, UnicodeError, csv.Error) as exc:
        print(dumps({"status": "error", "error": str(exc)}), file=sys.stderr, end="")
        return 2


def decode(value, spec):
    if value is None or value == "":
        return None
    kind = spec["type"]
    if kind in ("list", "ids", "dates", "object"):
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as exc:
                raise InputError("多值必须为 JSON 数组，对象必须为 JSON 对象") from exc
        expected = dict if kind == "object" else list
        if not isinstance(value, expected):
            fail(f"期望 {kind}")
        if kind != "object":
            if not all(isinstance(x, str) and x for x in value):
                fail("数组元素必须为非空字符串")
            if len(value) != len(set(value)):
                fail("数组不得有重复项")
            if kind == "dates":
                for x in value:
                    iso_date(x)
            if spec.get("item_enum") and any(x not in CONTRACT["enums"][spec["item_enum"]] for x in value):
                fail("数组中有非法枚举")
    elif kind == "bool":
        if isinstance(value, bool):
            return value
        if value not in ("true", "false"):
            fail("布尔值只能是 true/false")
        return value == "true"
    elif kind == "number":
        if isinstance(value, str):
            try:
                value = float(value)
            except ValueError as exc:
                raise InputError("非法数字") from exc
        value = finite(value)
        if "minimum" in spec and value < spec["minimum"]:
            fail(f"数值不得小于 {spec['minimum']}")
        if "maximum" in spec and value > spec["maximum"]:
            fail(f"数值不得大于 {spec['maximum']}")
    else:
        if not isinstance(value, str):
            fail("应为字符串")
        if kind == "date":
            iso_date(value)
        elif kind == "datetime":
            iso_time(value)
        elif kind == "enum":
            allowed = spec.get("values", CONTRACT["enums"].get(spec.get("enum"), []))
            if value not in allowed:
                fail(f"非法枚举 {value}；允许：{allowed}")
        elif kind == "module" and value not in [f"{n:02}" for n in range(1, 19)]:
            fail("模块必须为 01–18")
        if spec.get("pattern") and not re.fullmatch(spec["pattern"], value):
            fail(f"ID 格式错误：{value}")
    return value


def record(table, raw):
    definition = CONTRACT["tables"][table]
    if not isinstance(raw, dict):
        fail(f"{table} 记录应为对象")
    extra = set(raw) - set(definition["fields"])
    if extra:
        fail(f"{table} 未知字段：{sorted(extra)}")
    row = {}
    for key, spec in definition["fields"].items():
        try:
            value = decode(raw.get(key), spec)
            if spec["required"] and (value is None or value == [] or value == {}):
                fail("必填值缺失")
            row[key] = value
        except InputError as exc:
            raise InputError(f"{table}.{key}：{exc}") from exc
    for condition in definition["conditions"]:
        expected = {k: decode(v, definition["fields"][k]) for k, v in condition["if"].items()}
        if all(row[k] == v for k, v in expected.items()):
            for key in condition["required"]:
                if row[key] is None or row[key] == [] or row[key] == "":
                    fail(f"{table}.{key}：条件必填（{condition['if']}）")
    for start, end in (("period_start", "period_end"), ("effective_from", "effective_to"),
                       ("listing_start", "listing_end"), ("published_date", "revised_date")):
        if row.get(start) and row.get(end) and row[start] > row[end]:
            fail(f"{table} 日期顺序错误：{start} > {end}")
    return row


def csv_text(table, rows):
    fields = list(CONTRACT["tables"][table]["fields"])
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    for row in rows:
        encoded = {}
        for key in fields:
            value = row.get(key)
            encoded[key] = ("" if value is None else
                            json.dumps(value, ensure_ascii=False, allow_nan=False)
                            if isinstance(value, (list, dict, bool)) else value)
        writer.writerow(encoded)
    return handle.getvalue()


def read_table(project, table):
    path = Path(project) / f"{table}.csv"
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle, strict=True)
            if reader.fieldnames != list(CONTRACT["tables"][table]["fields"]):
                fail(f"{path} 表头与契约不一致或文件为空")
            rows = []
            for line, raw in enumerate(reader, 2):
                try:
                    if None in raw or any(v is None for v in raw.values()):
                        fail("CSV 列数错误")
                    rows.append(record(table, raw))
                except InputError as exc:
                    raise InputError(f"{path}:{line}：{exc}") from exc
            return rows
    except csv.Error as exc:
        raise InputError(f"{path} CSV 损坏：{exc}") from exc


def load_config(project):
    cfg = load_json(Path(project) / "project-config.json")
    baseline = load_json(ROOT / "templates/project-config.json")
    # 兼容旧项目只补新增的安全默认值；不写盘，也不据已有评分推定启用。
    if isinstance(cfg, dict):
        for key in ("scoring_enabled", "completion_review"):
            cfg.setdefault(key, baseline[key])
    if not isinstance(cfg, dict) or set(cfg) != set(baseline):
        fail("项目配置字段与模板不一致")
    for key in ("target", "target_id", "timezone", "version", "confidentiality"):
        if not isinstance(cfg[key], str) or not cfg[key].strip():
            fail(f"配置 {key} 必须为非空字符串")
    for key in ("materials", "control_evidence_ids", "industry_keywords", "languages", "events",
                "category_exemptions", "completed_actions"):
        if not isinstance(cfg[key], list):
            fail(f"配置 {key} 必须为数组")
    for key in ("control_evidence_ids", "industry_keywords", "languages"):
        if not all(isinstance(x, str) and x for x in cfg[key]):
            fail(f"配置 {key} 必须为字符串数组")
    if not isinstance(cfg["constraints"], dict) or not isinstance(cfg["module_scope"], dict):
        fail("constraints/module_scope 必须为对象")
    if cfg["constraints"].get("network") not in ("unknown", "online", "offline"):
        fail("network 必须为 unknown/online/offline")
    if not all(isinstance(e, dict) for e in cfg["category_exemptions"]):
        fail("category_exemptions 元素必须为对象")
    if cfg["contract_version"] != CONTRACT["version"]:
        fail("数据契约版本不匹配")
    iso_date(cfg["as_of_date"])
    if cfg["purpose"] is not None and cfg["purpose"] not in CONTRACT["enums"]["purpose"]:
        fail("未知研究目的")
    if cfg["purpose_status"] != ("pending" if cfg["purpose"] is None else "confirmed"):
        fail("purpose 与 purpose_status 不一致")
    if cfg["depth"] not in CONTRACT["enums"]["depth"]:
        fail("未知深度")
    for key in ("historical", "control_chain_checked", "peer_required", "declared_complete", "scoring_enabled"):
        if not isinstance(cfg[key], bool):
            fail(f"{key} 必须为布尔值")
    if cfg["scoring_enabled"] and cfg["purpose"] not in CONTRACT["scoring"]["purposes"]:
        fail("只有已明确的决策目的可启用评分；公司研究不评分")
    review = cfg["completion_review"]
    if review is not None:
        if not isinstance(review, dict) or set(review) != {"scope", "key_claim_ids", "gap_assessments", "reviewed_at"}:
            fail("completion_review 需 scope/key_claim_ids/gap_assessments/reviewed_at")
        if not isinstance(review["scope"], str) or not review["scope"].strip():
            fail("完成审核必须说明约定研究范围")
        keys = review["key_claim_ids"]
        if (not isinstance(keys, list) or not keys
                or not all(isinstance(x, str) and re.fullmatch(r"C-[0-9]{4,}", x) for x in keys)
                or len(keys) != len(set(keys))):
            fail("key_claim_ids 必须为不重复的关键声明 ID 数组")
        iso_time(review["reviewed_at"])
        if not isinstance(review["gap_assessments"], list):
            fail("gap_assessments 必须为数组")
        seen = set()
        for item in review["gap_assessments"]:
            if not isinstance(item, dict) or set(item) != {"gap_id", "impact", "disposition"}:
                fail("缺口评估需 gap_id/impact/disposition")
            gid = item["gap_id"]
            if not isinstance(gid, str) or not re.fullmatch(r"G-[0-9]{4,}", gid) or gid in seen:
                fail("缺口评估 ID 非法或重复")
            seen.add(gid)
            if not isinstance(item["impact"], str) or not item["impact"].strip():
                fail("缺口评估必须说明对结论的具体影响")
            if item["disposition"] not in CONTRACT["enums"]["gap_disposition"]:
                fail("缺口评估 disposition 非法")
    if cfg["report_status"] not in ("draft", "limited", "complete"):
        fail("报告状态错误")
    if cfg["research_gate"] not in CONTRACT["enums"]["gate"]:
        fail("研报门槛状态错误")
    if cfg["listing_trigger"] not in ("pending", "triggered", "not_triggered"):
        fail("上市触发状态错误")
    if cfg["identity_status"] not in ("pending", "resolved", "ambiguous"):
        fail("主体状态错误")
    threshold = finite(cfg["scoring_threshold"], "覆盖率门槛")
    if not 0 <= threshold <= 1:
        fail("覆盖率门槛必须在 0–1 之间")
    if cfg["last_refresh_at"]:
        iso_time(cfg["last_refresh_at"])
    if set(cfg["module_scope"]) != {f"{i:02}" for i in range(1, 19)}:
        fail("module_scope 必须记录全部十八模块")
    for key, value in cfg["module_scope"].items():
        if not isinstance(value, dict) or value.get("status") not in ("pending", "applicable", "not_applicable"):
            fail(f"模块 {key} 状态错误")
        if value["status"] == "not_applicable" and not value.get("reason"):
            fail(f"模块 {key} 不适用必须给理由")
    for event in cfg["events"]:
        if not isinstance(event, dict) or not all(event.get(k) for k in ("date", "entity_id", "description")):
            fail("事件必须包含 date/entity_id/description")
        iso_date(event["date"])
        if event["date"] > cfg["as_of_date"]:
            fail("基准日之后的事件不得作为当时已知事件")
    return cfg


def read_project(project):
    return load_config(project), {table: read_table(project, table) for table in CONTRACT["tables"]}


def indices(data):
    return {table: {r[CONTRACT["tables"][table]["primary_key"]]: r for r in rows}
            for table, rows in data.items()}


def structural_errors(data, cfg=None):
    errors = []
    idx = indices(data)
    for table, rows in data.items():
        pk = CONTRACT["tables"][table]["primary_key"]
        if len(idx[table]) != len(rows):
            errors.append(f"{table}：重复 ID")
        for row in rows:
            for key, spec in CONTRACT["tables"][table]["fields"].items():
                if spec.get("ref"):
                    value = row[key]
                    values = (value or []) if spec["type"] == "ids" else ([value] if value else [])
                    for item in values:
                        if item not in idx[spec["ref"]]:
                            errors.append(f"{table}.{row[pk]}.{key}：引用不存在 {item}")
    if cfg:
        if cfg["target_id"] not in idx["entity-map"]:
            errors.append("配置 target_id 不存在")
        for eid in cfg["control_evidence_ids"]:
            if eid not in idx["evidence-ledger"]:
                errors.append(f"控制链依据不存在：{eid}")
        for event in cfg["events"]:
            if event["entity_id"] not in idx["entity-map"]:
                errors.append(f"事件主体不存在：{event['entity_id']}")
    return errors


def listed_entities(cfg, data):
    """沿有证据的有效控制边向上追溯；参股和拟议交易不能触发控制。"""
    idx = indices(data)
    entities = idx["entity-map"]
    target = cfg["target_id"]
    seen, listed, pending = set(), [], False
    todo = [target]
    when = cfg["as_of_date"]
    while todo:
        entity_id = todo.pop()
        if entity_id in seen:
            continue
        seen.add(entity_id)
        entity = entities.get(entity_id)
        if not entity:
            pending = True
            continue
        if entity["identity_status"] != "resolved" or entity["listing_status"] == "unknown":
            pending = True
        status = entity["listing_status"]
        active_listing = (status == "listed" or (status == "delisted" and entity["listing_start"] and entity["listing_end"]))
        active_listing = active_listing and (not entity["listing_start"] or entity["listing_start"] <= when)
        active_listing = active_listing and (not entity["listing_end"] or when < entity["listing_end"])
        if active_listing:
            listed.append(entity_id)
        for edge in data["entity-relations"]:
            if edge["child_id"] != entity_id or edge["relation_type"] not in CONTRACT["research"]["control_relations"]:
                continue
            if edge["state"] == "proposed" or edge["effective_from"] > when or (edge["effective_to"] and when >= edge["effective_to"]):
                continue
            if edge["verification"] != "verified":
                pending = True
                continue
            todo.append(edge["parent_id"])
    pending = pending or not cfg["control_chain_checked"] or not cfg["control_evidence_ids"]
    return sorted(listed), pending


def project_events(cfg, data):
    """补充台账已知的新财报事件，不替代分析者识别其他重大事件。"""
    events = list(cfg["events"])
    reports = [r for r in data["research-register"] if r["report_date"] <= cfg["as_of_date"]
               and r["relevance"] != "excluded"]
    for official in reports:
        if not set(official["categories"]) & {"official_annual", "official_interim", "official_event"}:
            continue
        updates = [r["report_date"] for r in reports if "company_update" in r["categories"]
                   and r["coverage_entity_id"] == official["coverage_entity_id"]]
        if updates and official["report_date"] > max(updates):
            event = {"date": official["report_date"], "entity_id": official["coverage_entity_id"],
                     "description": "台账已知的新官方披露：" + official["title"]}
            if not any(e["date"] == event["date"] and e["entity_id"] == event["entity_id"] for e in events):
                events.append(event)
    return events


def requirements(cfg, data):
    listed, pending = listed_entities(cfg, data)
    required = []
    for entity in listed:
        cats = list(CONTRACT["research"]["base_categories"])
        # 目标事件可能影响母公司对其业务的研究，均需补查。
        if project_events(cfg, data):
            cats.extend(CONTRACT["research"]["event_categories"])
        if cfg["peer_required"]:
            cats.append(CONTRACT["research"]["peer_category"])
        for category in cats:
            exempt = next((e for e in cfg["category_exemptions"]
                           if e.get("entity_id") == entity and e.get("category") == category), None)
            # 仅允许官方中期披露在制度不适用或尚无该期时提出有证据的例外。
            if exempt and category == "official_interim" and exempt.get("reason") and exempt.get("evidence_ids"):
                continue
            required.append((cfg["target_id"], entity, category))
    return required, pending


def candidates(coverage, data, as_of):
    sources = indices(data)["source-register"]
    rows = [r for r in data["research-register"]
            if r["target_id"] == coverage["target_id"]
            and r["coverage_entity_id"] == coverage["research_entity_id"]
            and coverage["category"] in r["categories"] and r["relevance"] != "excluded"
            and r["report_date"] <= as_of
            and sources.get(r["source_id"], {}).get("time_scope") == "as_of"]
    superseded = {r["supersedes_id"] for r in rows if r["supersedes_id"]}
    rows = [r for r in rows if r["research_id"] not in superseded]
    return sorted(rows, key=lambda r: (r["report_date"], r["research_id"]), reverse=True)


def coverage_state(row, data, cfg):
    reports = candidates(row, data, cfg["as_of_date"])
    if not reports:
        return "incomplete"
    latest_date = reports[0]["report_date"]
    # 同日多机构报告和同日修订不按字符串版本号随意选一份完成。
    superseded = {r["supersedes_id"] for r in reports if r["supersedes_id"]}
    latest = [r for r in reports if r["report_date"] == latest_date and r["research_id"] not in superseded]
    any_read = any(r["access_status"] == "full_text" and r["reading_status"] == "analyzed" for r in reports)
    complete = all(r["access_status"] == "full_text" and r["reading_status"] == "analyzed"
                   and r["relevance"] == "direct" for r in latest)
    events = {e["date"] for e in project_events(cfg, data)}
    covered_events = set().union(*(set(r["event_dates"] or []) for r in latest))
    # 框架与历史年报不要求重写；事件专门项负责覆盖新事件。
    event_ok = row["category"] not in ("event_update", "official_event") or events <= covered_events
    gap = indices(data)["gap-register"].get(row["gap_id"])
    complete = (complete and event_ok and row["search_status"] == "found"
                and bool(row["search_ids"]) and bool(row["latestness_checked_at"])
                and row["event_coverage"] in ("covered", "not_applicable")
                and (not gap or gap["status"] == "closed"))
    return "complete" if complete else "partial" if any_read else "incomplete"


def research_gate(cfg, data):
    required, pending = requirements(cfg, data)
    if not required:
        return "incomplete" if pending else "not_applicable"
    states = []
    for key in required:
        rows = [r for r in data["research-coverage"]
                if (r["target_id"], r["research_entity_id"], r["category"]) == key]
        states.append(coverage_state(rows[0], data, cfg) if len(rows) == 1 else "incomplete")
    if (not pending and cfg["constraints"].get("network") == "online"
            and states and all(s == "complete" for s in states)):
        return "complete"
    if any(s in ("complete", "partial") for s in states):
        return "partial"
    return "incomplete"


def completion_errors(cfg, data):
    """验证约定范围完成的必要记录；不把资料覆盖不足改成已取得。"""
    errors = []
    idx = indices(data)
    review = cfg.get("completion_review")
    if not review:
        return ["约定范围完成需要 completion_review；旧项目须补关键结论和缺口影响审核"]
    if cfg["purpose"] is None:
        errors.append("目的仍待确认，不能确认约定研究范围完成")
    _, pending = requirements(cfg, data)
    if pending:
        errors.append("主体或控制链仍未核实，不能确认研究范围完成")
    keys = set(review["key_claim_ids"])
    for cid in keys:
        claim = idx["claim-register"].get(cid)
        if not claim:
            errors.append(f"完成审核引用不存在的关键声明：{cid}")
            continue
        if (claim["verification"] != "verified" or claim["confidence"] not in ("high", "medium")
                or claim["label"] in ("【缺口】", "【待核实】")):
            errors.append(f"{cid}：关键结论尚未核实；未知事项应保留缺口，阻断核心问题时保持 limited")
        support = [r for r in data["claim-evidence"]
                   if r["claim_id"] == cid and r["relation"] == "supports"
                   and r["evidence_id"] in idx["evidence-ledger"]]
        if not support:
            errors.append(f"{cid}：完成审核的关键结论缺少直接支持证据")
    for claim in data["claim-register"]:
        refuted = (claim["verification"] == "refuted"
                   and claim["confidence"] in ("high", "medium")
                   and bool((claim["counterevidence"] or "").strip())
                   and not (claim["unresolved"] or "").strip()
                   and any(r["claim_id"] == claim["claim_id"] and r["relation"] == "contradicts"
                           and r["evidence_id"] in idx["evidence-ledger"] for r in data["claim-evidence"]))
        if claim["materiality"] == "critical" and claim["claim_id"] not in keys and not refuted:
            errors.append(f"{claim['claim_id']}：关键重大声明不能遗漏于完成审核")
    for conflict in data["conflict-register"]:
        if conflict["status"] == "open" and conflict["decision_changing"]:
            errors.append(f"{conflict['conflict_id']}：存在会改变结论的未解决冲突")
    assessments = {r["gap_id"]: r for r in review["gap_assessments"]}
    open_gaps = {r["gap_id"]: r for r in data["gap-register"] if r["status"] == "open"}
    for gid in set(assessments) - set(open_gaps):
        errors.append(f"{gid}：完成审核的缺口不存在或已关闭，应更新审核")
    for gid, gap in open_gaps.items():
        assessment = assessments.get(gid)
        if not assessment:
            errors.append(f"{gid}：开放缺口未评估对约定范围的影响")
        elif assessment["disposition"] == "blocks_completion" or gap["materiality"] == "critical":
            errors.append(f"{gid}：缺口阻断约定核心问题，研究应保持 limited")
    for coverage in data["research-coverage"]:
        if not coverage["required"]:
            continue
        logs = [idx["search-log"].get(qid) for qid in coverage["search_ids"] or []]
        if (coverage["search_status"] == "not_executed" or not logs
                or any(not row or row["status"] == "not_executed" for row in logs)):
            errors.append(f"{coverage['coverage_id']}：必需研报检索没有真实执行记录")
        if not coverage["latestness_checked_at"]:
            errors.append(f"{coverage['coverage_id']}：缺少最新性复查记录")
    if cfg.get("declared_complete"):
        if open_gaps:
            errors.append("仍有开放缺口，不得声明全部任务完成")
        if any(action.get("status") != "completed" for action in cfg["completed_actions"]):
            errors.append("仍有计划动作，不得声明全部任务完成")
    return errors


def semantic_errors(cfg, data):
    errors = []
    idx = indices(data)
    when = cfg["as_of_date"]
    for source in data["source-register"]:
        published = source["revised_date"] or source["published_date"]
        if published > source["accessed_date"]:
            errors.append(f"{source['source_id']}：访问早于发布/修订")
        if source["time_scope"] == "as_of" and published > when:
            errors.append(f"{source['source_id']}：历史截止日后资料未隔离")
    for evidence in data["evidence-ledger"]:
        source = idx["source-register"].get(evidence["source_id"], {})
        if source.get("access_status") in ("metadata_only", "access_blocked", "unreadable"):
            errors.append(f"{evidence['evidence_id']}：不可读来源不能形成正文证据")
        if evidence["numeric"] and evidence["scope"] == "not_applicable":
            errors.append(f"{evidence['evidence_id']}：定量证据缺少实体范围")
        if evidence["attribute"] == "actual" and evidence["period_end"] and evidence["period_end"] > when:
            errors.append(f"{evidence['evidence_id']}：未来期间标为实际")
    for claim in data["claim-register"]:
        if claim["label"] == "【数据】" and claim["attribute"] != "actual":
            errors.append(f"{claim['claim_id']}：预测/估算不能标为实际【数据】")
        if claim["numeric"] and claim["scope"] == "not_applicable":
            errors.append(f"{claim['claim_id']}：定量声明缺少实体范围")
        links = [r for r in data["claim-evidence"] if r["claim_id"] == claim["claim_id"] and r["relation"] == "supports"]
        if claim["verification"] == "verified" and not links:
            errors.append(f"{claim['claim_id']}：已核实声明没有支持证据")
        if claim["verification"] == "refuted":
            contradictions = [r for r in data["claim-evidence"]
                              if r["claim_id"] == claim["claim_id"] and r["relation"] == "contradicts"]
            if not contradictions or not (claim["counterevidence"] or "").strip():
                errors.append(f"{claim['claim_id']}：已推翻声明需反驳证据关联和 counterevidence 驳回依据")
            if claim["confidence"] not in ("high", "medium") or (claim["unresolved"] or "").strip():
                errors.append(f"{claim['claim_id']}：驳回判断须有高/中置信且无未解决问题")
            links += contradictions
        entity = idx["entity-map"].get(claim["entity_id"], {})
        if claim["verification"] in ("verified", "refuted") and entity.get("identity_status") != "resolved":
            errors.append(f"{claim['claim_id']}：主体未锁定不能形成确定结论")
        for link in links:
            evidence = idx["evidence-ledger"].get(link["evidence_id"], {})
            source = idx["source-register"].get(evidence.get("source_id"), {})
            if source.get("time_scope") == "retrospective":
                errors.append(f"{claim['claim_id']}：事后资料不得用于确认或驳回时点结论")
            if claim["attribute"] == "actual" and evidence.get("attribute") in ("forecast", "estimate"):
                errors.append(f"{claim['claim_id']}：预测/估算证据被用作实际数据")
            if claim["numeric"] and (claim["entity_id"] != evidence.get("entity_id") or claim["scope"] != evidence.get("scope")):
                if not link["bridge"] or claim["label"] != "【推断】":
                    errors.append(f"{claim['claim_id']}：集团/分部与目标数据越界，需桥接依据及推断标签")
    for research in data["research-register"]:
        rid = research["research_id"]
        source = idx["source-register"].get(research["source_id"], {})
        if research["access_status"] != source.get("access_status"):
            errors.append(f"{rid}：报告与来源获取状态不一致")
        if research["report_date"] != (source.get("revised_date") or source.get("published_date")):
            errors.append(f"{rid}：报告日期须对应原始发布/修订日期，不能使用收录日期")
        if research["reading_status"] == "analyzed" and research["access_status"] != "full_text":
            errors.append(f"{rid}：仅摘要/元数据/片段不能标记全文已读")
        if set(research["categories"]) != set(research["category_relevance"]):
            errors.append(f"{rid}：逐类别相关性说明缺失")
        if any(not isinstance(v, str) or not v.strip() for v in research["category_relevance"].values()):
            errors.append(f"{rid}：类别相关性必须为非空文字")
        if research["data_cutoff"] and research["data_cutoff"] > research["report_date"]:
            errors.append(f"{rid}：历史数据截止日晚于报告日期")
        prior = idx["research-register"].get(research["supersedes_id"])
        if prior and (prior["report_date"] > research["report_date"] or prior["research_id"] == rid
                      or prior["publisher"] != research["publisher"]
                      or prior["coverage_entity_id"] != research["coverage_entity_id"]):
            errors.append(f"{rid}：修订替代关系不合理")
    for edge in data["entity-relations"]:
        if edge["parent_id"] == edge["child_id"]:
            errors.append(f"{edge['relation_id']}：不能自我控制")
    # 生效控制图不能含循环；股权交叉持有可保留为非控制关系。
    adjacency = {}
    for edge in data["entity-relations"]:
        if (edge["relation_type"] in CONTRACT["research"]["control_relations"]
                and edge["verification"] == "verified" and edge["state"] != "proposed"
                and edge["effective_from"] <= when
                and (not edge["effective_to"] or when < edge["effective_to"])):
            adjacency.setdefault(edge["parent_id"], []).append(edge["child_id"])
    visiting, visited = set(), set()
    def cycle(node):
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        if any(cycle(child) for child in adjacency.get(node, [])):
            return True
        visiting.remove(node)
        visited.add(node)
        return False
    if any(cycle(node) for node in adjacency):
        errors.append("有效控制图存在循环，需核实关系性质")
    for exemption in cfg["category_exemptions"]:
        if exemption.get("category") != "official_interim" or not exemption.get("reason") or not exemption.get("evidence_ids"):
            errors.append("研报必读类别不允许因难以获取而豁免")
        for eid in exemption.get("evidence_ids", []):
            if eid not in idx["evidence-ledger"]:
                errors.append(f"官方披露不适用依据不存在：{eid}")
    return errors


def research_errors(cfg, data):
    errors = []
    required, _ = requirements(cfg, data)
    keys = [(r["target_id"], r["research_entity_id"], r["category"]) for r in data["research-coverage"]]
    for key in required:
        if keys.count(key) != 1:
            errors.append(f"必读类别缺少覆盖项或重复：{key}")
    pairs = [("latest_discovered_id", "latest_discovered_for", lambda r: True),
             ("latest_fulltext_id", "latest_fulltext_for", lambda r: r["access_status"] == "full_text"),
             ("latest_read_id", "latest_read_for", lambda r: r["access_status"] == "full_text" and r["reading_status"] == "analyzed")]
    idx = indices(data)
    for row in data["research-coverage"]:
        cid = row["coverage_id"]
        if (row["target_id"], row["research_entity_id"], row["category"]) in required and not row["required"]:
            errors.append(f"{cid}：强制类别不得标记为可选")
        reports = candidates(row, data, cfg["as_of_date"])
        if reports and row["latestness_checked_at"]:
            if iso_time(row["latestness_checked_at"]).date().isoformat() < reports[0]["report_date"]:
                errors.append(f"{cid}：最新性复查早于已发现的最新报告")
        for field, marker, predicate in pairs:
            eligible = [r for r in reports if predicate(r)]
            selected = idx["research-register"].get(row[field])
            if eligible:
                if not selected or selected not in eligible or selected["report_date"] != eligible[0]["report_date"]:
                    errors.append(f"{cid}.{field}：未指向截至基准日发现的最新适用报告")
            elif row[field]:
                errors.append(f"{cid}.{field}：没有匹配报告")
            for research in data["research-register"]:
                marked = cid in (research[marker] or [])
                if marked != (row[field] == research["research_id"]):
                    errors.append(f"{cid}：覆盖指针与 {research['research_id']}.{marker} 不一致")
        state = coverage_state(row, data, cfg)
        if row["gate_status"] != state and row["required"]:
            errors.append(f"{cid}：登记门槛 {row['gate_status']} 与实际状态 {state} 不一致")
        if row["required"] and state != "complete":
            gap = idx["gap-register"].get(row["gap_id"])
            if not gap or gap["status"] != "open":
                errors.append(f"{cid}：未满足必读类别，必须登记开放缺口")
        if row["search_status"] != "not_executed" and not row["search_ids"]:
            errors.append(f"{cid}：宣称检索已执行却无检索记录")
        for qid in row["search_ids"] or []:
            if idx["search-log"].get(qid, {}).get("status") == "not_executed":
                errors.append(f"{cid}：计划不能冒充已执行检索")
    gate = research_gate(cfg, data)
    if cfg["research_gate"] == "complete" and gate != "complete":
        errors.append("未完成研报门槛却宣称完成")
    if cfg["declared_complete"] and gate not in ("complete", "not_applicable"):
        errors.append("未完成强制研报任务却宣称全部完成")
    return errors


def next_id(rows, field, prefix):
    values = [int(r[field].split("-")[-1]) for r in rows if r.get(field)]
    return f"{prefix}-{max(values, default=0) + 1:04}"


def sync_coverage(cfg, data):
    """仅根据已有台账推导状态；不会执行检索、读取报告或关闭缺口。"""
    required, pending = requirements(cfg, data)
    for target, entity, category in required:
        existing = next((r for r in data["research-coverage"]
                         if (r["target_id"], r["research_entity_id"], r["category"]) == (target, entity, category)), None)
        if existing:
            existing["required"] = True
            continue
        gid = next_id(data["gap-register"], "gap_id", "G")
        cid = next_id(data["research-coverage"], "coverage_id", "RC")
        data["gap-register"].append(record("gap-register", {
            "gap_id": gid, "needed": f"取得并阅读 {CONTRACT['research']['category_names'][category]}",
            "module": "18", "entity_id": target, "reason": "not_executed", "materiality": "major",
            "acquisition_path": "原始机构、合法公开全文或用户授权渠道；记录实际尝试",
            "priority": "P0", "owner_role": "研究负责人", "status": "open"}))
        data["research-coverage"].append(record("research-coverage", {
            "coverage_id": cid, "target_id": target, "research_entity_id": entity, "category": category,
            "required": True, "reason": "上市主体或有效控制链触发", "search_status": "not_executed",
            "event_coverage": "pending" if project_events(cfg, data) else "not_applicable",
            "gate_status": "incomplete", "gap_id": gid}))
    for research in data["research-register"]:
        for field in ("latest_discovered_for", "latest_fulltext_for", "latest_read_for"):
            research[field] = []
    for row in data["research-coverage"]:
        reports = candidates(row, data, cfg["as_of_date"])
        for field, marker, predicate in [
            ("latest_discovered_id", "latest_discovered_for", lambda r: True),
            ("latest_fulltext_id", "latest_fulltext_for", lambda r: r["access_status"] == "full_text"),
            ("latest_read_id", "latest_read_for", lambda r: r["access_status"] == "full_text" and r["reading_status"] == "analyzed")]:
            eligible = [r for r in reports if predicate(r)]
            row[field] = eligible[0]["research_id"] if eligible else None
            if eligible:
                eligible[0][marker].append(row["coverage_id"])
        row["gate_status"] = coverage_state(row, data, cfg)
    cfg["listing_trigger"] = "triggered" if required else "pending" if pending else "not_triggered"
    cfg["research_gate"] = research_gate(cfg, data)
    return cfg, data


def save_project(project, cfg, data):
    """写入前完整序列化；调用者必须先验证。多表写入不是数据库事务。"""
    project = Path(project)
    payloads = {f"{table}.csv": csv_text(table, rows) for table, rows in data.items()}
    payloads["project-config.json"] = dumps(cfg)
    # 更新台账时创建不可覆盖的快照，避免批量更新中断后失去原内容。
    backup = Path(tempfile.mkdtemp(prefix=".ledger-backup-", dir=project))
    for name, content in payloads.items():
        source = project / name
        if source.exists():
            safe_write(backup / name, source.read_text(encoding="utf-8"))
    for name, content in payloads.items():
        safe_write(project / name, content, overwrite=True)
    return backup
