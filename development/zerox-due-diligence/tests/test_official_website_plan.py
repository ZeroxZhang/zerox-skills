"""检验官网基础任务的依赖、裁剪边界与计划阶段无副作用。"""
import copy
import json
import re
import sys
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(os.environ.get("zerox_dd_root", Path(__file__).resolve().parents[3] / "zerox-due-diligence"))
sys.path.insert(0, str(ROOT / "scripts"))

from common import read_project  # noqa: E402
from init_project import initialize  # noqa: E402
from search_plan import plan  # noqa: E402


class OfficialWebsitePlanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="zerox-site-plan-")
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / "project"
        initialize(self.project, target="合成品牌甲", as_of="2026-10-20", timezone="UTC")
        self.cfg, self.data = read_project(self.project)
        self.data["entity-map"][0]["aliases"] = ["合成目标别名"]
        other = copy.deepcopy(self.data["entity-map"][0])
        other.update(entity_id="ENT-0002", legal_name="合成关联公司乙", aliases=[])
        self.data["entity-map"].append(other)

    @staticmethod
    def official_tasks(result):
        return [task for task in result["tasks"] if task.get("scope") == "target_basics"]

    def test_basic_pages_survive_all_module_exemptions_and_only_target_target(self):
        for scope in self.cfg["module_scope"].values():
            scope.update(status="not_applicable", reason="合成测试中的裁剪")
        tasks = self.official_tasks(plan(self.cfg, self.data))
        self.assertTrue(tasks)
        self.assertEqual({task["entity_id"] for task in tasks}, {self.cfg["target_id"]})
        pages = {task["page_type"] for task in tasks if task.get("page_type")}
        self.assertTrue({"about", "products_pricing", "founders_team", "history_news",
                         "locations_channels", "investor_relations", "terms_identity",
                         "visual_assets"}.issubset(pages))
        self.assertTrue(all(task["status"] == "not_executed" for task in tasks))

    def test_page_reading_depends_on_site_identity_without_invented_urls(self):
        tasks = self.official_tasks(plan(self.cfg, self.data))
        identities = [task for task in tasks if task["task_type"] == "official_site_identity"]
        self.assertEqual(len(identities), 1)
        identity = identities[0]
        self.assertEqual(identity["depends_on"], [])
        self.assertIn("合成目标别名", identity["aliases"])
        self.assertEqual(len({task["task_id"] for task in tasks}), len(tasks))
        for task in tasks:
            self.assertIsNone(task["url"])
            self.assertIsNone(re.search(r"https?://|(?:^|\s)site:|/about(?:\b|/)",
                                        task["query"], re.IGNORECASE))
            if task["task_type"] == "official_site_page":
                self.assertEqual(task["depends_on"], [identity["task_id"]])
                self.assertTrue({"actual_page_url", "authenticity", "published_date",
                                 "information_period", "accessed_date", "access_status",
                                 "locator"}.issubset(task["record_fields"]))

    def test_regular_and_mandatory_research_tasks_remain_available(self):
        target = self.data["entity-map"][0]
        target.update(listing_status="listed", exchange="合成交易所", security_code="TEST-001")
        self.cfg["module_scope"]["18"].update(status="not_applicable", reason="合成裁剪不取消上市触发")
        result = plan(self.cfg, self.data)
        self.assertTrue(self.official_tasks(result))
        ordinary = [task for task in result["tasks"]
                    if task.get("module") == "03" and task.get("alias")]
        research = [task for task in result["tasks"] if task.get("research_entity_id")]
        self.assertTrue(ordinary)
        self.assertTrue(research)
        self.assertTrue(any(task["from"] is not None for task in research))
        self.assertTrue(any(task["from"] is None for task in research))
        self.assertTrue(all(task["status"] == "not_executed" for task in result["tasks"]))
        self.assertTrue(all(task["entity_id"] == self.cfg["target_id"] for task in research))

    def test_offline_plan_does_not_execute_or_change_project_and_inputs(self):
        self.cfg["constraints"]["network"] = "offline"
        cfg_before, data_before = copy.deepcopy(self.cfg), copy.deepcopy(self.data)
        before = {str(p.relative_to(self.project)): p.read_bytes()
                  for p in self.project.rglob("*") if p.is_file()}
        with patch("socket.create_connection", side_effect=AssertionError("计划阶段不应联网")):
            result = plan(self.cfg, self.data)
        after = {str(p.relative_to(self.project)): p.read_bytes()
                 for p in self.project.rglob("*") if p.is_file()}
        self.assertEqual(result["type"], "plan_only")
        self.assertEqual(result["network"], "offline")
        self.assertTrue(all(task["status"] == "not_executed" for task in result["tasks"]))
        self.assertEqual(self.cfg, cfg_before)
        self.assertEqual(self.data, data_before)
        self.assertEqual(before, after)
        self.assertFalse(self.data["search-log"])
        json.dumps(result, ensure_ascii=False, allow_nan=False)


if __name__ == "__main__":
    unittest.main()
