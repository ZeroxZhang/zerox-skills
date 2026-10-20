"""按主体、期间和会计口径计算指标；缺失与不适用返回明确原因。"""
import argparse
import math

from common import CONTRACT, cli, emit, fail, finite, iso_date, load_json


METRICS = {
    "revenue", "cost", "net_profit", "operating_cashflow", "current_assets", "current_liabilities",
    "inventory", "prepayments", "assets_begin", "assets_end", "equity_begin", "equity_end",
    "receivables_begin", "receivables_end", "inventory_begin", "inventory_end",
    "payables_begin", "payables_end", "credit_sales", "purchases", "capex",
    "available_cash", "monthly_net_burn", "total_debt", "total_assets",
}


def validate_input(data):
    if not isinstance(data, dict) or not data:
        fail("财务输入为空；请使用 templates/financial-input.json")
    required = ("entity_id", "scope", "period_start", "period_end", "days", "currency", "unit",
                "accounting_basis", "attribute", "audited", "source_ids", "values", "input_evidence")
    for key in required:
        if key not in data or data[key] is None or data[key] == "" or data[key] == []:
            fail(f"财务口径必填：{key}")
    if data["scope"] not in ("consolidated", "standalone", "segment"):
        fail("财务范围必须为 consolidated/standalone/segment")
    if data["attribute"] not in CONTRACT["enums"]["attribute"][:3]:
        fail("财务属性必须为 actual/forecast/estimate")
    start, end = iso_date(data["period_start"]), iso_date(data["period_end"])
    days = finite(data["days"], "期间天数")
    if days != (end - start).days + 1 or days <= 0:
        fail("期间天数必须等于起止日期之差加一")
    if not isinstance(data["audited"], bool):
        fail("audited 必须为布尔值")
    if not isinstance(data["source_ids"], list) or not all(isinstance(x, str) and x for x in data["source_ids"]):
        fail("source_ids 必须为非空来源 ID 数组")
    if not isinstance(data["values"], dict) or not isinstance(data["input_evidence"], dict):
        fail("values/input_evidence 必须为对象")
    if set(data["values"]) - METRICS:
        fail(f"未知财务字段：{sorted(set(data['values']) - METRICS)}")
    for key, value in data["values"].items():
        if value is not None:
            finite(value, key)
            refs = data["input_evidence"].get(key)
            if not isinstance(refs, list) or not refs or not all(isinstance(x, str) and x for x in refs):
                fail(f"{key} 缺少输入证据 ID 数组")


def calculate(data):
    validate_input(data)
    values = data["values"]
    options = {"allow_end_balance": False, "allow_revenue_proxy": False, "allow_cost_proxy": False,
               "quick_deductions": ["inventory", "prepayments"], "near_zero_profit": 0.01,
               "capex_sign": "positive_outflow"}
    supplied = data.get("options", {})
    if not isinstance(supplied, dict) or set(supplied) - set(options):
        fail("未知财务选项")
    options.update(supplied)
    for flag in ("allow_end_balance", "allow_revenue_proxy", "allow_cost_proxy"):
        if not isinstance(options[flag], bool):
            fail(f"{flag} 必须为布尔值")
    if options["capex_sign"] not in ("positive_outflow", "negative_outflow"):
        fail("资本开支符号必须显式定义")
    finite(options["near_zero_profit"], "近零净利润阈值")
    if options["near_zero_profit"] < 0:
        fail("近零阈值不得为负")
    deductions = options["quick_deductions"]
    if not isinstance(deductions, list) or not deductions or len(set(deductions)) != len(deductions) or any(k not in ("inventory", "prepayments") for k in deductions):
        fail("速动扣除项需非空、无重复，并属于 inventory/prepayments")
    results = {}

    def output(name, value, formula, keys, reason=None, approximate=False, status=None, extra_evidence=None):
        if value is not None and not math.isfinite(value):
            fail(f"{name} 计算结果超出有限数值范围")
        results[name] = {
            "value": value, "status": status or ("missing" if value is None else "approximate" if approximate else "calculated"),
            "formula": formula, "inputs": {k: values.get(k) for k in keys},
            "evidence_ids": list(dict.fromkeys([x for k in keys for x in data["input_evidence"].get(k, [])] + (extra_evidence or []))),
            "reason": reason, "attribute": data["attribute"], "applicability": data["scope"],
        }

    def ratio(name, numerator, denominator, keys, formula, multiplier=1, note=None, approx=False):
        if numerator is None or denominator is None:
            output(name, None, formula, keys, "输入缺失；不得用 0 或行业均值替代")
        elif denominator <= 0:
            output(name, None, formula, keys, "分母为零或负数，常规比率不适用", status="not_applicable")
        else:
            output(name, numerator / denominator * multiplier, formula, keys, note, approx)

    def average(prefix):
        first, last = values.get(prefix + "_begin"), values.get(prefix + "_end")
        if first is not None and last is not None:
            return (first + last) / 2, False
        if last is not None and options["allow_end_balance"]:
            return last, True
        return None, False

    revenue, cost = values.get("revenue"), values.get("cost")
    margin = revenue - cost if revenue is not None and cost is not None else None
    ratio("gross_margin", margin, revenue, ["revenue", "cost"], "(收入−成本)/收入")
    ratio("net_margin", values.get("net_profit"), revenue, ["net_profit", "revenue"], "净利润/收入")
    ratio("current_ratio", values.get("current_assets"), values.get("current_liabilities"),
          ["current_assets", "current_liabilities"], "流动资产/流动负债")
    quick_keys = ["current_assets", *deductions, "current_liabilities"]
    quick = None if any(values.get(k) is None for k in ["current_assets", *deductions]) else values["current_assets"] - sum(values[k] for k in deductions)
    ratio("quick_ratio", quick, values.get("current_liabilities"), quick_keys,
          f"(流动资产−{'−'.join(deductions)})/流动负债")
    for name, prefix in (("roa", "assets"), ("roe", "equity")):
        balance, approx = average(prefix)
        ratio(name, values.get("net_profit"), balance, ["net_profit", prefix + "_begin", prefix + "_end"],
              "期间净利润/期间平均余额（未年化）", note="显式以期末余额近似" if approx else None, approx=approx)
    for name, prefix, preferred, proxy, permission in (
        ("receivable_days", "receivables", "credit_sales", "revenue", "allow_revenue_proxy"),
        ("inventory_days", "inventory", "cost", "cost", None),
        ("payable_days", "payables", "purchases", "cost", "allow_cost_proxy"),
    ):
        balance, approx = average(prefix)
        denom = values.get(preferred)
        used = preferred
        notes = ["显式以期末余额近似"] if approx else []
        if denom is None and permission and options[permission]:
            denom, used, approx = values.get(proxy), proxy, True
            notes.append(f"缺少 {preferred}，显式使用 {proxy} 近似")
        ratio(name, balance, denom, [prefix + "_begin", prefix + "_end", used],
              f"平均{prefix}/{used}×实际期间天数({data['days']})",
              multiplier=data["days"], note="；".join(notes) or None, approx=approx)
    days_values = [results[k]["value"] for k in ("receivable_days", "inventory_days", "payable_days")]
    ccc = None if any(x is None for x in days_values) else days_values[0] + days_values[1] - days_values[2]
    output("cash_conversion_cycle", ccc, "应收天数+存货天数−应付天数",
           ["receivables_begin", "receivables_end", "inventory_begin", "inventory_end", "payables_begin", "payables_end", "credit_sales", "purchases", "revenue", "cost"],
           "子指标缺失则不计算；保留各项近似条件",
           any(results[k]["status"] == "approximate" for k in ("receivable_days", "inventory_days", "payable_days")))
    profit = values.get("net_profit")
    if profit is not None and profit <= options["near_zero_profit"]:
        output("cash_profit_ratio", None, "经营现金流/净利润", ["operating_cashflow", "net_profit"],
               "净利润为负或接近零，不能作常规利润质量结论", status="not_applicable")
    else:
        ratio("cash_profit_ratio", values.get("operating_cashflow"), profit,
              ["operating_cashflow", "net_profit"], "经营现金流/净利润")
    capex = values.get("capex")
    if capex is not None:
        if (options["capex_sign"] == "positive_outflow" and capex < 0) or (options["capex_sign"] == "negative_outflow" and capex > 0):
            fail("资本开支数值与声明符号不一致")
    ocf = values.get("operating_cashflow")
    fcf = None if capex is None or ocf is None else ocf - abs(capex)
    output("simplified_fcf", fcf, "经营现金流−资本开支流出绝对额（简化口径，非FCFF/FCFE）",
           ["operating_cashflow", "capex"], f"资本开支符号：{options['capex_sign']}")
    cash, burn = values.get("available_cash"), values.get("monthly_net_burn")
    basis = data.get("cash_burn_basis", {})
    if not isinstance(basis, dict):
        fail("cash_burn_basis 必须为对象")
    cash_keys = ["available_cash", "monthly_net_burn"]
    if cash is not None and cash < 0:
        fail("可用现金不得为负")
    if cash is None or burn is None:
        output("cash_runway_months", None, "可用现金/月均净消耗", cash_keys, "可用现金或月均消耗缺失")
    else:
        for flag in ("cash_excludes_restricted", "includes_capex", "includes_debt_service", "includes_committed_spend"):
            if not isinstance(basis.get(flag), bool):
                fail(f"现金跑道需明确布尔口径：{flag}")
        if not basis.get("basis") or not basis["cash_excludes_restricted"]:
            output("cash_runway_months", None, "可用现金/月均净消耗", cash_keys,
                   "需说明历史/前瞻消耗口径并确认剔除受限资金")
        elif burn <= 0:
            output("cash_runway_months", None, "可用现金/月均净消耗", cash_keys,
                   "当前口径未消耗，不代表永久安全", status="not_applicable")
        else:
            output("cash_runway_months", cash / burn, "剔除受限现金后的可用现金/月均净消耗", cash_keys,
                   f"条件性估算：{basis}；不能直接证明未来生存期限")
            results["cash_runway_months"]["attribute"] = "estimate"
    prior = data.get("prior")
    if prior is None:
        output("revenue_growth", None, "当期收入/上期收入−1", ["revenue"], "缺少可比较上期")
    else:
        validate_input(prior)
        comparable = all(data[k] == prior[k] for k in ("entity_id", "scope", "currency", "unit", "accounting_basis"))
        current_duration = data["days"]
        comparable = comparable and abs(current_duration - prior["days"]) <= 1
        comparable = comparable and prior["period_end"] < data["period_start"]
        comparable = comparable and data["period_start"][5:] == prior["period_start"][5:] and data["period_end"][5:] == prior["period_end"][5:]
        previous = prior["values"].get("revenue")
        refs = prior["input_evidence"].get("revenue", [])
        if not comparable or data["attribute"] != "actual" or prior["attribute"] != "actual":
            output("revenue_growth", None, "可比较当期实际收入/上期实际收入−1", ["revenue"],
                   "主体/期间/单位/实际属性不可比；本脚本仅计算同季同长度的同比")
        elif revenue is None or previous is None:
            output("revenue_growth", None, "当期收入/上期收入−1", ["revenue"], "当期或上期收入缺失")
        elif previous <= 0:
            output("revenue_growth", None, "当期收入/上期收入−1", ["revenue"],
                   "上期收入为零或负数，普通增长率无意义；可单列绝对变化", status="not_applicable")
        else:
            output("revenue_growth", revenue / previous - 1, "当期收入/上期收入−1", ["revenue"],
                   extra_evidence=refs)
        results["revenue_growth"]["prior_revenue"] = previous
        results["revenue_growth"]["prior_evidence_ids"] = refs
    alerts = []
    thresholds = data.get("thresholds", [])
    if not isinstance(thresholds, list):
        fail("thresholds 必须为数组")
    for threshold in thresholds:
        if not isinstance(threshold, dict) or not all(k in threshold for k in ("metric", "operator", "value", "scope", "source")):
            fail("预警阈值需 metric/operator/value/scope/source")
        if threshold["metric"] not in results or threshold["operator"] not in ("lt", "gt"):
            fail("未知预警指标或运算符")
        limit = finite(threshold["value"], "预警阈值")
        if not threshold["scope"] or not threshold["source"]:
            fail("阈值需注明行业/阶段/口径适用范围和来源")
        value = results[threshold["metric"]]["value"]
        if value is not None and ((threshold["operator"] == "lt" and value < limit) or (threshold["operator"] == "gt" and value > limit)):
            alerts.append({**threshold, "observed": value, "meaning": "核查线索，需人工确认适用性；不自动认定舞弊、破产或禁止交易"})
    return {"context": {k: data[k] for k in ("entity_id", "scope", "period_start", "period_end", "days", "currency", "unit", "accounting_basis", "attribute", "audited", "source_ids")},
            "metrics": results, "alerts": alerts,
            "limitations": "计算不验证原始财务真实性；证据 ID 应在项目校验时另行核对。"}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", required=True, help="按 financial-input.json 填写")
    p.add_argument("--output", help="JSON 结果，不默认覆盖")
    args = p.parse_args()
    emit(calculate(load_json(args.input)), args.output)


if __name__ == "__main__":
    raise SystemExit(cli(main))
