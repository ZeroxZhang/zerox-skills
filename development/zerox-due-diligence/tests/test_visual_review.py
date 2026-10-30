"""可视化审阅的编辑启发式、缺失数据边界及无副作用测试。"""
import copy
import json
import sys
import os
import unittest
from pathlib import Path


ROOT = Path(os.environ.get("ZEROX_DD_ROOT", Path(__file__).resolve().parents[3] / "zerox-due-diligence"))
sys.path.insert(0, str(ROOT / "scripts"))

from visual_review import review_visuals  # noqa: E402


def content(*blocks):
    return {"version": "1.2", "sections": [{"id": "company", "title": "合成公司", "blocks": list(blocks)}]}


def explain(topic="identity", text="有资料支持的公司介绍。", status="partial"):
    return {"type": "explanation", "topic": topic, "text": text, "limitations": "", "status": status}


def chart(kind="bar", points=None):
    return {"type": "chart", "chart_type": kind,
            "points": [{"label": "甲", "value": 10}, {"label": "乙", "value": 20}] if points is None else points}


def codes(result):
    return {finding["code"] for row in result["rows"] for finding in row["findings"]} | {
        finding["code"] for finding in result["findings"]
    }


class VisualReviewTests(unittest.TestCase):
    def test_counts_new_numeric_forms_without_treating_structures_as_numbers(self):
        c = content(
            chart("proportion", [{"value": 70}]),
            chart("range", [{"low": 15, "high": 50}, {"low": None, "high": None}]),
            chart("stacked_bar", [{"segments": [{"value": 40}, {"value": 60}]},
                                  {"segments": [{"value": 20}, {"value": 80}]}]),
            chart("waterfall", [{"value": 100, "role": "total"}, {"value": -20, "role": "change"}]),
            {"type": "metrics", "items": [{"value": 7}, {"value": 8}]},
            {"type": "diagram", "nodes": [{"id": "a"}, {"id": "b"}], "edges": []},
            {"type": "process", "items": []}, {"type": "timeline", "items": []},
            {"type": "matrix", "rows": []}, {"type": "image"},
            {"type": "people", "profiles": [{"name": "甲"}, {"name": "乙"}]},
        )
        count = review_visuals(c)["rows"][0]["counts"]
        self.assertEqual((count["quantitative_charts"], count["data_points"],
                          count["known_data_points"], count["numeric_values"]), (4, 7, 6, 9))
        self.assertEqual((count["metric_blocks"], count["metric_items"]), (1, 2))
        for key in ("diagram_blocks", "process_blocks", "timeline_blocks", "matrix_blocks", "images", "people_blocks"):
            self.assertEqual(count[key], 1)
        self.assertEqual(count["people_profiles"], 2)

    def test_long_chinese_and_english_are_explicit_separate_thresholds(self):
        self.assertNotIn("long_prose_run", codes(review_visuals(content({"type": "text", "text": "文" * 599}))))
        self.assertIn("long_prose_run", codes(review_visuals(content({"type": "text", "text": "文" * 600}))))
        self.assertNotIn("long_prose_run", codes(review_visuals(content({"type": "text", "text": "word " * 119}))))
        self.assertIn("long_prose_run", codes(review_visuals(content({"type": "text", "text": "word " * 120}))))

    def test_analysis_splits_long_text_runs(self):
        c = content({"type": "text", "text": "文" * 350}, chart(), {"type": "text", "text": "文" * 350})
        self.assertNotIn("long_prose_run", codes(review_visuals(c)))

    def test_image_and_metrics_do_not_solve_late_analytical_visual(self):
        c = content(explain("identity"), {"type": "image"}, explain("offering"),
                    {"type": "metrics", "items": [{"value": 70}]}, explain("customers_markets"), chart())
        result = review_visuals(c)
        self.assertIn("late_analytical_visual", codes(result))
        self.assertEqual(result["rows"][0]["signals"]["explanations_before_first_analytical_visual"], 3)

    def test_early_diagram_avoids_late_visual_warning(self):
        c = content(explain("identity"), {"type": "diagram"}, explain("offering"),
                    explain("customers_markets"), explain("operating_model"))
        self.assertNotIn("late_analytical_visual", codes(review_visuals(c)))

    def test_dates_references_urls_and_numbered_lists_are_not_operating_numbers(self):
        c = content({"type": "text", "text": (
            "2020年创立，2021-09-02披露，2026/10/20复核。2025年10月13日来源"
            "[E-0001][E-0002][E-0003] https://example.com/123/456/789\n"
            "1. 读材料\n2. 查原件\n3. 复核\nENT-0001 S-0003"
        )})
        result = review_visuals(c)
        self.assertNotIn("numbers_only_in_prose", codes(result))
        self.assertEqual(result["rows"][0]["signals"]["numeric_tokens_in_prose"], 0)

    def test_existing_numbers_need_review_even_with_image_or_metric_cards(self):
        c = content({"type": "text", "text": "营收100万元，利润20万元，毛利率30%。"},
                    {"type": "image"}, {"type": "metrics", "items": [{"value": 100}]})
        self.assertIn("numbers_only_in_prose", codes(review_visuals(c)))

    def test_existing_chart_avoids_generic_numeric_warning(self):
        c = content({"type": "text", "text": "营收100万元，利润20万元，毛利率30%。"}, chart())
        self.assertNotIn("numbers_only_in_prose", codes(review_visuals(c)))

    def test_unknown_explanations_do_not_create_numeric_or_topic_pressure(self):
        c = content(explain("financial_performance", "100、200、300均为待确认的提问编号，数据未知。", "unknown"),
                    explain("marketing", status="unknown"), explain("competition", status="unknown"))
        self.assertEqual(review_visuals(c)["warnings"], [])

    def test_topic_specific_review_is_actionable_and_not_duplicated_as_numeric(self):
        c = content(explain("financial_performance", "营收100万元，利润20万元，毛利率30%。"))
        result = review_visuals(c)
        self.assertIn("topic_without_analytical_visual", codes(result))
        self.assertNotIn("numbers_only_in_prose", codes(result))
        self.assertIn("合成公司（company）", result["warnings"][0])
        self.assertIn("口径矩阵", result["warnings"][0])

    def test_marketing_diagram_and_competition_matrix_are_suitable_without_fake_figures(self):
        for topic, kind in (("marketing", "diagram"), ("competition", "matrix"),
                            ("financial_performance", "matrix")):
            self.assertNotIn("topic_without_analytical_visual",
                             codes(review_visuals(content(explain(topic), {"type": kind}))))

    def test_people_or_image_does_not_satisfy_competition_visual(self):
        self.assertIn("topic_without_analytical_visual",
                      codes(review_visuals(content(explain("competition"), {"type": "image"},
                                                   {"type": "people", "profiles": []}))))

    def test_short_conclusion_can_have_no_visual(self):
        self.assertEqual(review_visuals(content({"type": "callout", "title": "建议", "text": "有条件推进。"}))["warnings"], [])

    def test_dense_table_is_reviewed_but_small_supporting_table_is_not(self):
        dense = {"type": "table", "rows": [["甲", "乙"]] * 5}
        small = {"type": "table", "rows": [["甲", "乙"]] * 2}
        self.assertIn("dense_table_without_synthesis", codes(review_visuals(content(dense))))
        self.assertNotIn("dense_table_without_synthesis", codes(review_visuals(content(small))))
        self.assertNotIn("dense_table_without_synthesis", codes(review_visuals(content(dense, chart()))))

    def test_repeated_chart_type_is_only_an_advisory_not_a_quota(self):
        one_kind = review_visuals(content(chart(), chart(), chart()))
        self.assertIn("single_chart_type", codes(one_kind))
        self.assertIn("可保留", one_kind["findings"][0]["message"])
        self.assertNotIn("single_chart_type", codes(review_visuals(content(chart(), chart()))))
        self.assertNotIn("single_chart_type", codes(review_visuals(content(chart(), chart(), chart("line")))))

    def test_all_null_range_does_not_count_as_known_data(self):
        c = content(chart("range", [{"low": None, "high": None}]))
        count = review_visuals(c)["summary"]["counts"]
        self.assertEqual((count["data_points"], count["known_data_points"], count["numeric_values"]), (1, 0, 0))

    def test_result_is_json_inputs_unchanged_and_legacy_readable(self):
        c = content(explain(), chart())
        c["version"] = "1.1"
        before = copy.deepcopy(c)
        result = review_visuals(c)
        self.assertEqual(c, before)
        self.assertEqual(json.loads(json.dumps(result, ensure_ascii=False, allow_nan=False)), result)
        self.assertIn("不是事实", result["meaning"])
        self.assertEqual(result["summary"]["finding_count"], len(result["warnings"]))

    def test_empty_report_yields_no_invented_warning(self):
        result = review_visuals({"sections": []})
        self.assertEqual(result["rows"], [])
        self.assertEqual(result["warnings"], [])
        self.assertEqual(result["summary"]["section_count"], 0)


if __name__ == "__main__":
    unittest.main()
