"""用多种独立方法估算未披露指标的区间，检查方法独立性与结果重叠；结果始终是推断。"""
import argparse
import ast
import copy
import itertools
import math
import re
from pathlib import Path

from common import CONTRACT, InputError, cli, emit, fail, finite as common_finite, indices, load_json, read_project

TOP_FIELDS = {"estimate_id", "metric", "entity_id", "scope", "period", "unit", "purpose", "claim_id", "methods"}
METHOD_FIELDS = {"method_id", "name", "formula", "inputs", "limitations"}
INPUT_FIELDS = {"low", "base", "high", "unit", "basis", "evidence_ids", "rationale"}
STATUS_NAMES = {"triangulated": "多方法交叉印证", "divergent": "方法结果分歧", "insufficient": "独立方法不足"}
MEANING = "估算是本项目的推断，不是披露数据；区间来自输入上下限的组合，不是统计置信区间。"


def finite(value, label="数值"):
    try:
        return common_finite(value, label)
    except OverflowError:
        fail(f"{label} 超出可计算的有限数值范围")


def text(value, label):
    if not isinstance(value, str) or not value.strip():
        fail(f"{label} 必须为非空文字")
    if "{{" in value or "}}" in value:
        fail(f"{label} 残留模板占位符")
    return value


def significant(value, digits=3):
    """按有效数字取整，避免呈现比方法精度更细的数字。"""
    value = finite(value, "估算结果")
    if value == 0:
        return 0.0
    return round(value, digits - 1 - math.floor(math.log10(abs(value))))


def interval(op, left, right):
    """闭区间四则运算；除数区间含零时没有有界结果。"""
    (a, b), (c, d) = left, right
    if isinstance(op, ast.Add):
        return a + c, b + d
    if isinstance(op, ast.Sub):
        return a - d, b - c
    if isinstance(op, ast.Div):
        if c <= 0 <= d:
            fail("公式除数的区间包含 0，无法得到有界估算")
        c, d = 1 / d, 1 / c
    products = (a * c, a * d, b * c, b * d)
    return min(products), max(products)


def evaluate(formula, ranges):
    """只允许输入名、数字、括号和四则运算，不执行任意代码。"""
    try:
        tree = ast.parse(formula, mode="eval")
    except (SyntaxError, ValueError, TypeError, RecursionError):
        fail(f"公式语法错误：{formula}")
    names, constants = set(), []

    def walk(node):
        if isinstance(node, ast.Expression):
            return walk(node.body)
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
            return interval(node.op, walk(node.left), walk(node.right))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            low, high = walk(node.operand)
            return -high, -low
        if isinstance(node, ast.Name):
            if node.id not in ranges:
                fail(f"公式使用了未定义的输入：{node.id}")
            names.add(node.id)
            return ranges[node.id]
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            value = finite(node.value, "公式常数")
            constants.append(value)
            return value, value
        fail(f"公式只允许输入名、数字、括号和 + - * /：{formula}")

    try:
        result = tuple(finite(x, "公式结果") for x in walk(tree))
    except (ValueError, OverflowError, ZeroDivisionError, RecursionError) as exc:
        fail(str(exc))
    return result, names, constants


def check_input(name, item, label):
    if not isinstance(item, dict) or set(item) != INPUT_FIELDS:
        fail(f"{label} 需 {sorted(INPUT_FIELDS)}")
    values = []
    for key in ("low", "base", "high"):
        if item[key] is None:
            fail(f"{label}.{key} 缺失；没有依据就不要估算，改为登记缺口")
        values.append(finite(item[key], f"{label}.{key}"))
    if not values[0] <= values[1] <= values[2]:
        fail(f"{label} 需满足 low ≤ base ≤ high")
    text(item["unit"], f"{label}.unit")
    text(item["rationale"], f"{label}.rationale")
    if item["basis"] not in ("evidence", "assumption"):
        fail(f"{label}.basis 需为 evidence 或 assumption")
    ids = item["evidence_ids"]
    if (not isinstance(ids, list)
            or not all(isinstance(x, str) and re.fullmatch(r"E-[0-9]{4,}", x) for x in ids)
            or len(ids) != len(set(ids))):
        fail(f"{label}.evidence_ids 必须为不重复的证据 ID 数组")
    if item["basis"] == "evidence" and not ids:
        fail(f"{label} 标为 evidence 但没有证据 ID")
    return values


def triangulate(spec, cfg=None, data=None):
    warnings = []
    if not isinstance(spec, dict) or set(spec) != TOP_FIELDS:
        fail(f"估算文件需包含且仅包含 {sorted(TOP_FIELDS)}")
    if not isinstance(spec["estimate_id"], str) or not re.fullmatch(r"EST-[0-9]{2,}", spec["estimate_id"]):
        fail("estimate_id 格式为 EST-01")
    for key in ("metric", "period", "unit", "purpose"):
        text(spec[key], key)
    if not isinstance(spec["entity_id"], str) or not re.fullmatch(r"ENT-[0-9]{4,}", spec["entity_id"]):
        fail("entity_id 需为主体 ID，如 ENT-0001")
    if spec["scope"] not in [s for s in CONTRACT["enums"]["scope"] if s != "not_applicable"]:
        fail("scope 需为 consolidated / standalone / segment / brand")
    if spec["claim_id"] is not None and not (isinstance(spec["claim_id"], str) and re.fullmatch(r"C-[0-9]{4,}", spec["claim_id"])):
        fail("claim_id 需为声明 ID 或 null")
    methods = spec["methods"]
    if not isinstance(methods, list) or not 1 <= len(methods) <= 6:
        fail("methods 需为 1–6 种方法")
    idx = indices(data) if data else None
    if idx:
        if spec["entity_id"] not in idx["entity-map"]:
            fail(f"估算主体不存在：{spec['entity_id']}")
        if idx["entity-map"][spec["entity_id"]].get("entity_type") == "person":
            fail("自然人仅用于相关角色与控制关系，不能作为商业指标估算对象")
    else:
        warnings.append("未提供 --project：只能试算区间，无法核对证据存在和来源独立性，状态保持 insufficient，不能直接进入报告。")
    results, seen = [], set()
    for method in methods:
        if not isinstance(method, dict) or not METHOD_FIELDS <= set(method) <= METHOD_FIELDS | {"unit_factor"}:
            fail(f"方法需 {sorted(METHOD_FIELDS)}，可选 unit_factor")
        mid = method["method_id"]
        if not isinstance(mid, str) or not re.fullmatch(r"M[0-9]+", mid) or mid in seen:
            fail(f"method_id 非法或重复：{mid!r}")
        seen.add(mid)
        for key in ("name", "formula", "limitations"):
            text(method[key], f"{mid}.{key}")
        factor = finite(method.get("unit_factor", 1), f"{mid}.unit_factor")
        if factor <= 0:
            fail(f"{mid}.unit_factor 必须为正数")
        if not isinstance(method["inputs"], dict) or not method["inputs"]:
            fail(f"{mid}.inputs 不能为空")
        ranges, bases, evidence_ids, assumptions = {}, {}, [], []
        for name, item in method["inputs"].items():
            if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
                fail(f"{mid} 输入名需为英文标识符：{name}")
            low, base, high = check_input(name, item, f"{mid}.{name}")
            ranges[name], bases[name] = (low, high), (base, base)
            evidence_ids.extend(item["evidence_ids"])
            if item["basis"] == "assumption":
                assumptions.append(name)
        (low, high), used, constants = evaluate(method["formula"], ranges)
        (base, _), _, _ = evaluate(method["formula"], bases)
        unused = set(ranges) - used
        if unused:
            fail(f"{mid} 有未进入公式的输入：{sorted(unused)}")
        if constants:
            warnings.append(f"{mid} 公式含常数 {constants}：只应是单位换算，经营假设请改为带依据的输入。")
        evidence_ids = list(dict.fromkeys(evidence_ids))
        groups = set()
        if idx:
            for eid in evidence_ids:
                evidence = idx["evidence-ledger"].get(eid)
                if not evidence:
                    fail(f"{mid} 引用的证据不存在：{eid}")
                source = idx["source-register"].get(evidence["source_id"])
                if not source or not isinstance(source.get("origin_group"), str) or not source["origin_group"].strip():
                    fail(f"{mid} 的证据 {eid} 缺少有效来源或同源组，不能核对独立性")
                groups.add(source["origin_group"])
                if evidence["attribute"] == "forecast":
                    warnings.append(f"{mid} 使用了预测证据 {eid}；估算历史期间时须说明为何适用。")
        backed = len(assumptions) < len(ranges)
        if not backed:
            warnings.append(f"{mid} 的输入全部是假设，不能作为三角验证的一条独立方法。")
        results.append({"method_id": mid, "name": method["name"], "formula": method["formula"],
                        "unit_factor": factor, "inputs": copy.deepcopy(method["inputs"]),
                        "low": finite(low * factor, f"{mid} 换算结果"), "base": finite(base * factor, f"{mid} 换算结果"),
                        "high": finite(high * factor, f"{mid} 换算结果"), "evidence_ids": sorted(evidence_ids),
                        "origin_groups": sorted(groups), "assumption_inputs": assumptions,
                        "evidence_backed": backed, "limitations": method["limitations"]})

    def independent(a, b):
        return (idx is not None and not set(a["evidence_ids"]) & set(b["evidence_ids"])
                and not set(a["origin_groups"]) & set(b["origin_groups"]))

    results.sort(key=lambda m: m["method_id"])
    backed = [m for m in results if m["evidence_backed"]]
    # 保留所有极大独立组，不挑第一个组合；相关方法不能重复收窄区间。
    groups = []
    for size in range(2, len(backed) + 1):
        for group in itertools.combinations(backed, size):
            if (all(independent(a, b) for a, b in itertools.combinations(group, 2))
                    and not any(m not in group and all(independent(m, a) for a in group) for m in backed)):
                low, high = max(m["low"] for m in group), min(m["high"] for m in group)
                groups.append({"method_ids": [m["method_id"] for m in group],
                               "overlap": {"low": low, "high": high} if low <= high else None})
    groups.sort(key=lambda g: g["method_ids"])
    conflicts = [[a["method_id"], b["method_id"]] for a, b in itertools.combinations(backed, 2)
                 if max(a["low"], b["low"]) > min(a["high"], b["high"])]
    for method in results:
        method["independent_of"] = [m["method_id"] for m in results
                                    if m is not method and m["evidence_backed"] and method["evidence_backed"] and independent(method, m)]
    overlap = None
    if groups:
        status = "divergent" if conflicts else "triangulated"
        if status == "triangulated":
            # 多组独立验证时取各组重叠区间的外包络，不任取较窄的一组。
            overlap = {"low": min(g["overlap"]["low"] for g in groups),
                       "high": max(g["overlap"]["high"] for g in groups)}
    else:
        status = "insufficient"
    envelope = {"low": min(m["low"] for m in results), "high": max(m["high"] for m in results)}
    if envelope["low"] > 0 and envelope["high"] / envelope["low"] > 3:
        warnings.append("各方法区间上下限相差超过3倍，结论区分力有限；考虑补充证据收窄关键输入。")
    if status == "divergent":
        warnings.append(f"有证据方法的区间存在分歧 {conflicts}：不能选取一致的组合掩盖冲突，也不能取平均；正文分别列出并解释分歧。")
    if status == "insufficient":
        warnings.append("没有两种互相独立且有证据支撑的方法：不能作为三角验证结果呈现，补充证据或登记缺口。")
    if idx and spec["claim_id"]:
        claim = idx["claim-register"].get(spec["claim_id"])
        if not claim:
            fail(f"估算关联的声明不存在：{spec['claim_id']}")
        if claim["label"] != "【推断】" or claim["attribute"] != "estimate" or not claim["numeric"]:
            fail(f"{spec['claim_id']}：估算声明须为【推断】、attribute=estimate、numeric=true")
        for key in ("entity_id", "scope"):
            if claim.get(key) != spec[key]:
                fail(f"{spec['claim_id']}：估算与声明的 {key} 不一致；先统一估算输出口径，不能借关联跨越主体或范围")
        input_ids = {eid for method in results for eid in method["evidence_ids"]}
        links = [link for link in data["claim-evidence"] if link["claim_id"] == spec["claim_id"]]
        for eid in sorted(input_ids):
            matched = [link for link in links if link["evidence_id"] == eid]
            if not matched:
                fail(f"{spec['claim_id']}：估算输入 {eid} 未在 claim-evidence 关联")
            if not any(isinstance(link.get("bridge"), str) and link["bridge"].strip() for link in matched):
                fail(f"{spec['claim_id']}：输入 {eid} 缺少 bridge；须说明公式、期间、单位换算及适用边界")
        warnings.append(f"{spec['claim_id']}：机器只核对主体、范围和关联完整性；须人工对照声明正文与估算的期间（{spec['period']}）、单位（{spec['unit']}）及各 bridge 是否一致。")
        if status == "insufficient" and claim["verification"] == "verified":
            fail(f"{spec['claim_id']}：独立方法不足的估算不能标为已核实")
    elif spec["claim_id"] is None:
        warnings.append("尚未关联声明：进入报告前在 claim-register 登记【推断】声明并填写 claim_id。")

    points = [{"label": f'{m["method_id"]} {m["name"]}', "low": significant(m["low"]), "high": significant(m["high"]),
               "evidence_ids": m["evidence_ids"]} for m in backed if m["evidence_ids"]]
    independent_ids = sorted({mid for g in groups for mid in g["method_ids"]})
    if overlap:
        ids = sorted({e for m in backed if m["method_id"] in independent_ids for e in m["evidence_ids"]})
        points.append({"label": "独立验证组重叠区间的保守包络", "low": significant(overlap["low"]), "high": significant(overlap["high"]),
                       "evidence_ids": ids})
    formulas = "；".join(f'{m["method_id"]} = ({m["formula"]}) × {m["unit_factor"]:g}' for m in results)
    presentation = None
    if points and status != "insufficient":
        presentation = {
            "type": "chart", "chart_type": "range",
            "title": f'{spec["metric"]}估算区间：{STATUS_NAMES[status]}',
            "unit": spec["unit"], "period": spec["period"], "entity_id": spec["entity_id"], "kind": "estimate",
            "evidence_ids": list(dict.fromkeys(e for point in points for e in point["evidence_ids"])),
            "note": f"本项目估算，不是披露数据。{formulas}。区间由输入上下限组合得出，不是统计置信区间；主要假设见底稿 {spec['estimate_id']}。",
            "points": points,
        }
    return {"estimate_id": spec["estimate_id"], "metric": spec["metric"], "entity_id": spec["entity_id"],
            "scope": spec["scope"], "period": spec["period"], "unit": spec["unit"], "purpose": spec["purpose"], "claim_id": spec["claim_id"],
            "status": status, "status_name": STATUS_NAMES[status],
            "independent_methods": independent_ids, "independent_groups": groups,
            "conflicting_methods": conflicts, "overlap": overlap, "envelope": envelope,
            "methods": results, "label": "【推断】", "attribute": "estimate",
            "presentation": presentation,
            "warnings": sorted(warnings), "meaning": MEANING}


def project_estimates(project, cfg, data):
    """检查工作区 estimates/ 下的全部估算文件，供 check_report 汇总。"""
    errors, warnings, seen = [], [], set()
    for path in sorted((Path(project) / "estimates").glob("*.json")):
        try:
            result = triangulate(load_json(path), cfg, data)
        except (InputError, ValueError, TypeError, KeyError) as exc:
            errors.append(f"估算 {path.name}：{exc}")
            continue
        if result["estimate_id"] in seen:
            errors.append(f"估算 ID 重复：{result['estimate_id']}")
        seen.add(result["estimate_id"])
        warnings.extend(f"估算 {result['estimate_id']}：{w}" for w in result["warnings"])
    return errors, warnings


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", required=True, help="估算输入 JSON，模板见 templates/estimate-input.json")
    p.add_argument("--project", help="工作区；提供时核对证据、同源组与关联声明")
    p.add_argument("--output", help="可选 JSON 输出路径，默认标准输出，不覆盖")
    args = p.parse_args()
    cfg, data = read_project(args.project) if args.project else (None, None)
    result = triangulate(load_json(args.input), cfg, data)
    emit(result, args.output)
    return 1 if result["status"] == "insufficient" else 0


if __name__ == "__main__":
    raise SystemExit(cli(main))
