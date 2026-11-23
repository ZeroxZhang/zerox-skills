"""来源能力登记、按问题选择和检索日志汇总。全部为合成场景，不联网。"""
import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(os.environ.get("zerox_dd_root", Path(__file__).resolve().parents[3] / "zerox-due-diligence"))
sys.path.insert(0, str(ROOT / "scripts"))

from common import InputError, load_config, load_json, read_project  # noqa: E402
from init_project import initialize  # noqa: E402
from search_plan import plan  # noqa: E402
from source_registry import (default_selection, load_registry, search_log_warnings,  # noqa: E402
                             summarize_search_log, validate_registry)


FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "source-selection-cases.json"


class SourceSelectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="zerox-source-plan-")
        self.addCleanup(self.temp.cleanup)

    def test_registry_is_a_catalog_not_a_connection(self):
        raw = (ROOT / "references" / "sources" / "source-capabilities.json").read_text(encoding="utf-8")
        registry = validate_registry(load_registry())
        ids = {source["capability_id"] for source in registry["sources"]}
        self.assertTrue({"us.ofac.sdn", "un.sc.consolidated", "eu.fsf.consolidated",
                         "uk.ofsi.sanctions_list", "social.weibo.official", "social.douyin",
                         "social.linkedin.public", "social.maimai", "reviews.cn_consumer"} <= ids)
        self.assertTrue(all(source["implementation"]["connector"] is False
                            and source["implementation"]["automated_retrieval"] is False
                            for source in registry["sources"]))
        gsxt = next(source for source in registry["sources"] if source["capability_id"] == "cn.gsxt")
        ofac = next(source for source in registry["sources"] if source["capability_id"] == "us.ofac.sdn")
        self.assertEqual(gsxt["verification"]["result"], "access_blocked")
        self.assertEqual(gsxt["verification"]["date"], "2026-10-20")
        self.assertEqual(gsxt["fallback_capability_id"], "cn.local_registry_credit")
        self.assertIsNone(ofac["verification"]["date"])
        self.assertEqual(ofac["verification"]["result"], "not_executed")
        self.assertTrue(any(path["kind"] == "official_api" and path["available"] == "documented_untested"
                            for path in ofac["access_paths"]))
        self.assertNotIn("已接通", raw)
        self.assertNotIn("本次已调用", raw)
        self.assertEqual(registry["distinct_from"], "source-register")

    def test_template_selection_matches_code_default(self):
        template = load_json(ROOT / "templates" / "project-config.json")["source_selection"]
        self.assertEqual(template, default_selection())

    def test_cases_select_without_executing(self):
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.assertIn("合成", fixture["notice"])
        for case in fixture["cases"]:
            with self.subTest(case=case["id"]):
                result = self.plan_case(case)
                selected = {item["capability_id"]: item["role"] for item in result["source_selection"]["selected"]}
                deferred = {item["capability_id"] for item in result["source_selection"]["deferred"]}
                notes = {item["code"] for item in result["source_selection"]["notes"]}
                tasks = [task for task in result["tasks"] if str(task.get("task_type", "")).startswith("source_")]
                self.assertTrue(all(task["status"] == "not_executed" for task in result["tasks"]))
                self.assertTrue(any(task.get("task_type") == "official_site_identity" for task in result["tasks"]))
                for sid, role in case["expect_roles"].items():
                    self.assertEqual(selected.get(sid), role, selected)
                for sid in case["expect_absent"]:
                    self.assertNotIn(sid, selected)
                for sid in case["expect_deferred"]:
                    self.assertIn(sid, deferred)
                self.assertEqual(any(task["task_type"] == "source_counterevidence" for task in tasks),
                                 case["expect_counterevidence"])
                self.assertTrue(set(case["expect_notes"]) <= notes)
                social = [sid for sid, role in selected.items() if role == "social"]
                self.assertLessEqual(len(social), result["source_selection"]["budgets"]["max_social_tasks"])
                for task in tasks:
                    if task["task_type"] != "source_capability":
                        continue
                    self.assertTrue(task["catalog_verification"]["not_this_project"])
                    self.assertFalse(task["implementation"]["connector"])
                for sid, depends in case.get("expect_depends", {}).items():
                    task = next(item for item in tasks if item.get("capability_id") == sid)
                    self.assertEqual(task["depends_on"], depends)
                if case["expect_counterevidence"]:
                    goal = next(task["goal"] for task in tasks if task["task_type"] == "source_counterevidence")
                    self.assertIn("不满率", goal)
                    self.assertIn("无风险", goal)

    def test_unknown_capability_is_rejected(self):
        result_cfg, data = self.base_project("合成公司甲", "中国大陆")
        result_cfg["source_selection"]["include_capability_ids"] = ["not.a.real.source"]
        with self.assertRaises(InputError):
            plan(result_cfg, data)

    def test_question_can_keep_a_deferred_module_source(self):
        cfg, data = self.base_project("合成公司戊", "中国大陆")
        cfg["focus"] = "产品质量"
        cfg["key_questions"] = [self.question("是否存在行政处罚？")]
        cfg["module_scope"]["13"] = {"status": "not_applicable", "reason": "合成裁剪，只保留问题触发的名单和案件"}
        result = plan(cfg, data)
        court = next(task for task in result["tasks"] if task.get("capability_id") == "cn.court.public_records")
        self.assertEqual(court["status"], "not_executed")
        self.assertEqual(court["module_scope_override"], "not_applicable")
        cfg["module_scope"]["01"] = {"status": "not_applicable", "reason": "合成裁剪无信号的登记任务"}
        skipped = plan(cfg, data)
        self.assertNotIn("cn.gsxt", {item["capability_id"] for item in skipped["source_selection"]["selected"]})

    def test_offline_plan_still_does_not_connect(self):
        cfg, data = self.base_project("合成饮品甲", "中国大陆")
        cfg["focus"] = "消费者零售"
        cfg["key_questions"] = [self.question("用户评价集中在哪些问题？")]
        cfg["constraints"]["network"] = "offline"
        before = copy.deepcopy(data)
        with patch("socket.create_connection", side_effect=AssertionError("计划阶段不应联网")):
            result = plan(cfg, data)
        self.assertEqual(data, before)
        self.assertTrue(result["source_selection"]["selected"])
        self.assertTrue(all(task["status"] == "not_executed" for task in result["tasks"]))
        self.assertEqual(result["network"], "offline")

    def test_existing_example_config_defaults_selection_without_rewriting(self):
        project = ROOT / "examples" / "branch-tea"
        before = (project / "project-config.json").read_bytes()
        loaded = load_config(project)
        self.assertIsNone(loaded["source_selection"]["profile"])
        self.assertEqual(before, (project / "project-config.json").read_bytes())

    def test_search_log_summary_keeps_unrun_work_visible(self):
        rows = [
            {"search_id": "Q-0001", "status": "found", "source_ids": ["S-0001"], "limitations": "合成材料"},
            {"search_id": "Q-0002", "status": "access_blocked", "source_ids": [], "limitations": ""},
            {"search_id": "Q-0003", "status": "not_executed", "source_ids": [], "limitations": "只是计划"},
            {"search_id": "Q-0004", "status": "not_found", "source_ids": [], "limitations": "合成查询没有公开记录"},
        ]
        summary = summarize_search_log(rows)
        self.assertEqual(summary["by_status"]["found"], 1)
        self.assertEqual(summary["retrieved_source_ids"], ["S-0001"])
        self.assertEqual(summary["inaccessible_search_ids"], ["Q-0002"])
        self.assertEqual(summary["not_found_search_ids"], ["Q-0004"])
        self.assertEqual(summary["not_executed_search_ids"], ["Q-0003"])
        self.assertIn("无记录不是无风险", summary["meaning"])
        warnings = " ".join(search_log_warnings(rows))
        self.assertIn("Q-0002", warnings)
        self.assertIn("Q-0003", warnings)

    def plan_case(self, case):
        cfg, data = self.base_project(dirname=case["id"], **case["init"])
        cfg["focus"] = case["focus"]
        cfg["key_questions"] = [self.question(text) for text in case["questions"]]
        if "profile" in case:
            cfg["source_selection"]["profile"] = case["profile"]
        if "budgets" in case:
            cfg["source_selection"]["budgets"].update(case["budgets"])
        if "include" in case:
            cfg["source_selection"]["include_capability_ids"] = case["include"]
        if "exclude" in case:
            cfg["source_selection"]["exclude_capability_ids"] = case["exclude"]
        return plan(cfg, data)

    def base_project(self, target, geography, dirname=None, **kwargs):
        project = Path(self.temp.name) / (dirname or target)
        initialize(project, target=target, geography=geography, as_of="2026-10-20", timezone="UTC", **kwargs)
        return read_project(project)

    @staticmethod
    def question(text):
        return {"kq_id": "KQ-01", "question": text, "why_it_matters": "合成",
                "sub_questions": [], "claim_ids": [], "status": "open", "answer": ""}


if __name__ == "__main__":
    unittest.main()
