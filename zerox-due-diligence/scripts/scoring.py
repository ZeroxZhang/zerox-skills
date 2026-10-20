"""将业务适配评分与风险、证据覆盖、研报门槛分别输出。"""
import argparse
import math

from common import CONTRACT, cli, emit, fail, finite, read_project, research_gate, structural_errors


def calculate(rows, rules, threshold=0.8, conflict=False):
    threshold = finite(threshold, "门槛")
    if not 0 <= threshold <= 1:
        fail("门槛应在 0–1 之间")
    weights = rules["weights"]
    if set(rules["critical_dimensions"]) - set(weights):
        fail("关键维度未配置权重")
    if len({r["dimension"] for r in rows}) != len(rows):
        fail("评分维度重复")
    if {r["dimension"] for r in rows} != set(weights):
        fail("评分维度缺失或超出配置；缺失应保留行和原因")
    applicable, covered, weighted = 0.0, 0.0, 0.0
    known, excluded = set(), set()
    for row in rows:
        dim = row["dimension"]
        weight = finite(row["weight"], f"{dim} 权重")
        expected = finite(weights[dim], f"{dim} 配置权重")
        if weight < 0 or expected < 0 or not math.isclose(weight, expected):
            fail(f"{dim} 权重非法或与场景配置不一致")
        score = row["score"]
        if score is not None:
            score = finite(score, f"{dim} 分数")
            if not 1 <= score <= 5:
                fail("分数必须在 1–5 之间")
        if row["applicability"] == "not_applicable":
            if not row["reason"] or score is not None:
                fail("不适用维度需理由且不得评分")
            excluded.add(dim)
            continue
        if row["applicability"] != "applicable":
            fail("适用性枚举错误")
        applicable += weight
        if score is not None:
            if row["coverage_status"] != "sufficient" or not row["evidence_ids"] or not row["anchor"]:
                fail("评分必须有充分证据、锚点和引用")
            if row["confidence"] not in ("high", "medium"):
                fail("低/未知置信度不能作为充分证据评分")
            known.add(dim)
            covered += weight
            weighted += weight * score
        elif not row["reason"]:
            fail("缺失评分需注明原因")
        elif row["coverage_status"] == "sufficient":
            fail("缺失分数不能标记证据充分")
    if len(excluded) == len(rows):
        return {"status": "not_applicable", "coverage": None, "partial_score": None, "overall_score": None,
                "reason": "全部维度有依据地不适用"}
    if applicable <= 0:
        fail("适用权重总和必须大于 0")
    coverage = covered / applicable
    partial = weighted / covered if covered > 0 else None
    missing_critical = set(rules["critical_dimensions"]) - known
    # 关键维度不能仅通过标为不适用消失；如确需变更须明确修改关键维度配置并说明。
    eligible = coverage + 1e-12 >= threshold and not missing_critical and not conflict
    return {"status": "complete" if eligible else "insufficient_evidence", "coverage": coverage,
            "partial_score": partial, "overall_score": partial if eligible else None,
            "missing_critical": sorted(missing_critical), "decision_changing_conflict": conflict,
            "threshold": threshold, "normalized_applicable_weights": {
                r["dimension"]: r["weight"] / applicable for r in rows if r["applicability"] == "applicable"},
            "reason": "满足内部发布门槛" if eligible else "证据不足，暂不提供综合评分；partial_score 仅为已覆盖维度分数"}


def project_score(cfg, data):
    if cfg["purpose"] is None:
        if cfg["published_score"] is not None:
            fail("目的待确认，不得发布场景综合分")
        return {"status": "purpose_pending", "coverage": None, "partial_score": None, "overall_score": None}
    rules = CONTRACT["scoring"]["purposes"][cfg["purpose"]]
    if cfg["scoring_override"]:
        override = cfg["scoring_override"]
        if not isinstance(override, dict) or not override.get("reason"):
            fail("权重/关键维度覆盖必须说明依据")
        if set(override) != {"reason", "weights", "critical_dimensions"}:
            fail("覆盖配置需 reason/weights/critical_dimensions")
        rules = override
    rows = data["scorecard"]
    if any(r["purpose"] != cfg["purpose"] for r in rows):
        fail("评分目的与项目不一致")
    conflicts = any(r["status"] == "open" and r["decision_changing"] for r in data["conflict-register"])
    result = calculate(rows, rules, cfg["scoring_threshold"], conflicts)
    result["research_gate"] = research_gate(cfg, data)
    result["risk_assessment"] = "独立查看 risk-register.csv；商业分数不抵销法定禁止或用户否决条件。"
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", required=True)
    p.add_argument("--output")
    args = p.parse_args()
    cfg, data = read_project(args.project)
    errors = structural_errors(data, cfg)
    if errors:
        fail("；".join(errors))
    emit(project_score(cfg, data), args.output)


if __name__ == "__main__":
    raise SystemExit(cli(main))
