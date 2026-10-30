"""估算判定、证据边界和可复算底稿的回归检查。"""
import copy
import itertools
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(os.environ.get("zerox_dd_root", Path(__file__).resolve().parents[3] / "zerox-due-diligence"))
sys.path.insert(0, str(ROOT / "scripts"))
from common import CONTRACT, InputError, dumps
from triangulate import evaluate, triangulate, project_estimates
from build_audit_report import estimate_audit


def fixture():
    data = {name: [] for name in CONTRACT["tables"]}
    data["entity-map"] = [{"entity_id": "ENT-0001", "entity_type": "brand"},
                          {"entity_id": "ENT-0002", "entity_type": "legal_entity"}]
    for i in range(1, 5):
        data["source-register"].append({"source_id": f"S-{i:04}", "origin_group": f"ORIGIN-{i}"})
        data["evidence-ledger"].append({"evidence_id": f"E-{i:04}", "source_id": f"S-{i:04}", "attribute": "actual"})
    spec = {"estimate_id": "EST-01", "metric": "年营收", "entity_id": "ENT-0001", "scope": "brand",
            "period": "2025年", "unit": "亿元", "purpose": "核对规模区间", "claim_id": None, "methods": []}
    for i in (1, 2):
        spec["methods"].append({"method_id": f"M{i}", "name": f"方法{i}", "formula": "x", "inputs": {
            "x": {"low": 1, "base": 1.5, "high": 2, "unit": "亿元", "basis": "evidence",
                  "evidence_ids": [f"E-{i:04}"], "rationale": f"来源{i}提供上下限"}},
            "limitations": "数据覆盖范围待人工核对"})
    return spec, data


def link_claim(spec, data):
    spec["claim_id"] = "C-0001"
    data["claim-register"] = [{"claim_id": "C-0001", "entity_id": spec["entity_id"], "scope": spec["scope"],
                               "label": "【推断】", "attribute": "estimate", "numeric": True, "verification": "pending"}]
    ids = sorted({eid for method in spec["methods"] for item in method["inputs"].values() for eid in item["evidence_ids"]})
    data["claim-evidence"] = [{"link_id": f"CE-{i:04}", "claim_id": "C-0001", "evidence_id": eid,
                               "bridge": "输入按 x 公式计算；2025 年品牌营收，单位亿元，范围由对应原件支持"}
                              for i, eid in enumerate(ids, 1)]


class TriangulationTests(unittest.TestCase):
    def test_overlapping_independent_methods(self):
        spec, data = fixture()
        result = triangulate(spec, data=data)
        self.assertEqual(result["status"], "triangulated")
        self.assertEqual(result["overlap"], {"low": 1, "high": 2})
        self.assertEqual(result["independent_methods"], ["M1", "M2"])
        self.assertEqual(result["presentation"]["kind"], "estimate")

    def test_conflict_cannot_be_hidden_by_method_order(self):
        spec, data = fixture()
        third = copy.deepcopy(spec["methods"][1])
        third.update(method_id="M3", name="同源材料的另一种算法")
        third["inputs"]["x"].update(low=9, base=9.5, high=10)
        spec["methods"].append(third)
        for methods in itertools.permutations(spec["methods"]):
            with self.subTest(order=[m["method_id"] for m in methods]):
                result = triangulate({**spec, "methods": list(methods)}, data=data)
                self.assertEqual(result["status"], "divergent")
                self.assertIsNone(result["overlap"])
                self.assertIn(["M1", "M3"], result["conflicting_methods"])
                self.assertEqual([g["method_ids"] for g in result["independent_groups"]], [["M1", "M2"], ["M1", "M3"]])

    def test_correlated_methods_do_not_artificially_narrow_result(self):
        spec, data = fixture()
        spec["methods"][0]["inputs"]["x"].update(low=1, base=5, high=10)
        spec["methods"][1]["inputs"]["x"].update(low=4, base=6, high=8)
        third = copy.deepcopy(spec["methods"][1])
        third.update(method_id="M3", name="同源的窄区间")
        third["inputs"]["x"].update(low=5, base=6, high=7)
        spec["methods"].append(third)
        result = triangulate(spec, data=data)
        self.assertEqual(result["status"], "triangulated")
        self.assertEqual(result["overlap"], {"low": 4, "high": 8})

    def test_shared_origin_is_not_independent(self):
        spec, data = fixture()
        data["source-register"][1]["origin_group"] = "ORIGIN-1"
        result = triangulate(spec, data=data)
        self.assertEqual(result["status"], "insufficient")
        self.assertIsNone(result["presentation"])

    def test_same_evidence_is_not_independent(self):
        spec, data = fixture()
        spec["methods"][1]["inputs"]["x"]["evidence_ids"] = ["E-0001"]
        self.assertEqual(triangulate(spec, data=data)["status"], "insufficient")

    def test_without_project_is_a_calculation_only(self):
        spec, _ = fixture()
        result = triangulate(spec)
        self.assertEqual(result["status"], "insufficient")
        self.assertIsNone(result["presentation"])
        self.assertEqual(len(result["methods"]), 2)

    def test_assumption_only_never_counts_even_with_context_evidence(self):
        spec, data = fixture()
        for method in spec["methods"]:
            method["inputs"]["x"]["basis"] = "assumption"
        result = triangulate(spec, data=data)
        self.assertEqual(result["status"], "insufficient")
        self.assertIsNone(result["presentation"])

    def test_missing_evidence_source_or_origin_rejected(self):
        for issue in ("evidence", "source", "origin"):
            spec, data = fixture()
            if issue == "evidence":
                data["evidence-ledger"] = []
            elif issue == "source":
                data["source-register"] = []
            else:
                data["source-register"][0]["origin_group"] = ""
            with self.subTest(issue=issue), self.assertRaises(InputError):
                triangulate(spec, data=data)

    def test_claim_entity_and_scope_must_match(self):
        for field, bad in (("entity_id", "ENT-0002"), ("scope", "standalone")):
            spec, data = fixture()
            link_claim(spec, data)
            data["claim-register"][0][field] = bad
            with self.subTest(field=field), self.assertRaisesRegex(InputError, field):
                triangulate(spec, data=data)

    def test_claim_requires_every_input_link_and_bridge(self):
        for issue in ("missing_link", "missing_bridge"):
            spec, data = fixture()
            link_claim(spec, data)
            if issue == "missing_link":
                data["claim-evidence"].pop()
            else:
                data["claim-evidence"][0]["bridge"] = ""
            with self.subTest(issue=issue), self.assertRaises(InputError):
                triangulate(spec, data=data)

    def test_matching_claim_retains_explicit_semantic_review(self):
        spec, data = fixture()
        link_claim(spec, data)
        result = triangulate(spec, data=data)
        self.assertTrue(any("期间（2025年）" in warning and "单位（亿元）" in warning for warning in result["warnings"]))

    def test_insufficient_estimate_cannot_be_verified_claim(self):
        spec, data = fixture()
        spec["methods"] = spec["methods"][:1]
        link_claim(spec, data)
        data["claim-register"][0]["verification"] = "verified"
        with self.assertRaisesRegex(InputError, "独立方法不足"):
            triangulate(spec, data=data)

    def test_natural_person_cannot_be_estimated(self):
        spec, data = fixture()
        data["entity-map"][0]["entity_type"] = "person"
        with self.assertRaisesRegex(InputError, "自然人"):
            triangulate(spec, data=data)

    def test_invalid_or_nonfinite_formula_is_input_error(self):
        for formula in ("x +", "__import__('os')", "x ** 2", "x / 0", "x * 1e309", "x * 1e308 * 1e308"):
            spec, data = fixture()
            spec["methods"][0]["formula"] = formula
            with self.subTest(formula=formula), self.assertRaises(InputError):
                triangulate(spec, data=data)

    def test_factor_and_huge_input_are_finite(self):
        spec, data = fixture()
        spec["methods"][0]["inputs"]["x"].update(low=1e308, base=1e308, high=1e308)
        spec["methods"][0]["unit_factor"] = 10
        with self.assertRaises(InputError):
            triangulate(spec, data=data)
        spec["methods"][0]["inputs"]["x"].update(low=10**1000, base=10**1000, high=10**1000)
        with self.assertRaises(InputError):
            triangulate(spec, data=data)

    def test_audit_contains_inputs_and_supports_recalculation(self):
        spec, data = fixture()
        for method in spec["methods"]:
            method["unit_factor"] = 0.0001
            method["inputs"]["x"].update(low=10000, base=15000, high=20000, unit="万元")
        result = triangulate(spec, data=data)
        for method in result["methods"]:
            ranges = {name: (item["low"], item["high"]) for name, item in method["inputs"].items()}
            interval, _, _ = evaluate(method["formula"], ranges)
            self.assertEqual([value * method["unit_factor"] for value in interval], [method["low"], method["high"]])
        audit = estimate_audit(result)
        for detail in ("10000", "15000", "20000", "0.0001", "万元", "2025年", "亿元", "evidence", "来源1提供上下限", "数据覆盖范围待人工核对", "E-0001"):
            self.assertIn(detail, audit)
        self.assertIn("× 0.0001", result["presentation"]["note"])

    def test_project_estimate_invalid_formula_is_reported(self):
        spec, data = fixture()
        spec["methods"][0]["formula"] = "x +"
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / "estimates"
            directory.mkdir()
            (directory / "bad.json").write_text(dumps(spec), encoding="utf-8")
            errors, _ = project_estimates(tmp, {}, data)
        self.assertEqual(len(errors), 1)
        self.assertIn("公式语法错误", errors[0])

    def test_cli_invalid_formula_returns_standard_error(self):
        spec, _ = fixture()
        spec["methods"][0]["formula"] = "x +"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input.json"
            path.write_text(dumps(spec), encoding="utf-8")
            result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/triangulate.py"), "--input", str(path)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
