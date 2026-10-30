"""品牌入口、关联自然人、关键问题与研究裁剪的行为回归；全部资料为合成。"""
import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(os.environ.get("ZEROX_DD_ROOT", Path(__file__).resolve().parents[3] / "zerox-due-diligence"))
sys.path.insert(0, str(ROOT / "scripts"))

from common import (CONTRACT, InputError, brand_resolution, candidates, check_key_questions, completion_errors,
                    dumps, edge_active, listed_entities, load_config, load_json, read_project, record,
                    semantic_errors, structural_errors, sync_coverage)
from init_project import initialize
from search_plan import plan


def entity(number, kind="legal_entity", **changes):
    raw = {"entity_id": f"ENT-{number:04}", "legal_name": f"合成主体{number}",
           "entity_type": kind, "identity_status": "resolved", "listing_status": "unlisted",
           "evidence_ids": ["E-0001"], "registration_id": "" if kind == "person" else f"synthetic-{number}",
           "identity_notes": "合成公开登记和任职记录相互对应，已区分同名者"}
    raw.update(changes)
    return record("entity-map", raw)


def relation(number, parent, child, kind, **changes):
    raw = {"relation_id": f"REL-{number:04}", "parent_id": parent, "child_id": child,
           "relation_type": kind, "control_basis": "仅用于回归的合成关系依据",
           "effective_from": "2025-01-01", "state": "current", "verification": "verified",
           "evidence_ids": ["E-0001"]}
    raw.update(changes)
    return record("entity-relations", raw)


def question(status="answered", **changes):
    item = {"kq_id": "KQ-01", "question": "品牌经营责任由谁承担？", "why_it_matters": "决定合同及财务口径",
            "sub_questions": ["谁销售并收款？"], "claim_ids": ["C-0001"],
            "status": status, "answer": "合成公司承担经营责任，商标由关联自然人持有。"}
    item.update(changes)
    return item


class ResearchWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dd-workflow-regression-")
        self.addCleanup(self.temp.cleanup)
        self.cfg = load_json(ROOT / "templates/project-config.json")
        self.cfg.update(target="合成品牌", target_id="ENT-0001", purpose="company_research",
                        purpose_status="confirmed", as_of_date="2026-10-20", identity_status="resolved",
                        control_chain_checked=True, control_evidence_ids=["E-0001"],
                        key_questions=[question()], completion_review={
                            "scope": "查明品牌背后的经营公司和商标权利人",
                            "key_claim_ids": ["C-0001"], "gap_assessments": [],
                            "reviewed_at": "2026-10-20T12:00:00+08:00"})
        for item in self.cfg["module_scope"].values():
            item.update(status="applicable", reason="本次范围内")
        self.data = {name: [] for name in CONTRACT["tables"]}
        self.data["entity-map"] = [entity(1, "brand"), entity(2), entity(3, "person")]
        self.data["entity-relations"] = [
            relation(1, "ENT-0002", "ENT-0001", "operator"),
            relation(2, "ENT-0003", "ENT-0001", "trademark_holder"),
            relation(3, "ENT-0003", "ENT-0002", "control")]
        self.data["source-register"] = [record("source-register", {
            "source_id": "S-0001", "title": "合成公开资料", "source_type": "other", "publisher": "回归测试",
            "published_date": "2026-10-01", "accessed_date": "2026-10-20", "locator": "https://example.invalid/test",
            "grade": "D", "origin_group": "synthetic", "access_status": "full_text", "authenticity": "checked",
            "authorization": "仅测试", "time_scope": "as_of"})]
        self.data["evidence-ledger"] = [record("evidence-ledger", {
            "evidence_id": "E-0001", "source_id": "S-0001", "entity_id": "ENT-0001", "module": "01",
            "locator": "第1段", "excerpt": "完全合成，说明品牌、公司与权利人关系。",
            "scope": "not_applicable", "attribute": "not_applicable", "numeric": False})]
        self.data["claim-register"] = [record("claim-register", {
            "claim_id": "C-0001", "statement": "合成公司承担经营责任，关联人持有商标。", "label": "【事实】",
            "entity_id": "ENT-0001", "module": "01", "materiality": "critical", "verification": "verified",
            "confidence": "high", "attribute": "not_applicable", "numeric": False, "scope": "not_applicable"})]
        self.data["claim-evidence"] = [record("claim-evidence", {
            "link_id": "CE-0001", "claim_id": "C-0001", "evidence_id": "E-0001", "relation": "supports",
            "applicable_scope": "合成品牌主体及角色"})]

    def write_config(self, cfg=None):
        project = Path(self.temp.name)
        (project / "project-config.json").write_text(dumps(cfg or self.cfg), encoding="utf-8")
        return project

    def test_person_holder_and_controller_support_company_research(self):
        self.assertEqual(brand_resolution(self.cfg, self.data)["holding"], ["ENT-0003"])
        self.assertEqual(brand_resolution(self.cfg, self.data)["operating"], ["ENT-0002"])
        self.assertEqual(listed_entities(self.cfg, self.data), ([], False))
        self.assertEqual(structural_errors(self.data, self.cfg), [])
        self.assertEqual(semantic_errors(self.cfg, self.data), [])
        self.assertEqual(completion_errors(self.cfg, self.data), [])

    def test_person_identity_requires_evidence_and_disambiguation_without_registration(self):
        self.assertIsNone(entity(3, "person")["registration_id"])
        for changes in ({"identity_notes": ""}, {"evidence_ids": []}, {"registration_id": "made-up"}):
            with self.subTest(changes=changes), self.assertRaises(InputError):
                entity(3, "person", **changes)
        with self.assertRaises(InputError):
            entity(2, registration_id="")

    def test_person_cannot_have_listing_or_security_fields(self):
        for changes in ({"listing_status": "listed", "exchange": "X", "security_code": "123"},
                        {"listing_status": "unknown"}, {"security_class": "A"},
                        {"listing_start": "2020-01-01"}):
            with self.subTest(changes=changes), self.assertRaises(InputError):
                entity(3, "person", **changes)

    def test_person_is_not_a_research_target(self):
        self.cfg["target_id"] = "ENT-0003"
        self.assertTrue(any("不能作为" in e for e in structural_errors(self.data, self.cfg)))
        output = Path(self.temp.name) / "person"
        with self.assertRaises(InputError):
            initialize(output, "关联人", target_type="person")
        self.assertFalse(output.exists())

    def test_person_cannot_be_brand_operator_or_brand_of(self):
        for kind in ("operator", "brand_of"):
            with self.subTest(kind=kind):
                self.data["entity-relations"][0] = relation(1, "ENT-0003", "ENT-0001", kind)
                self.assertTrue(any("品牌角色的上层" in e for e in semantic_errors(self.cfg, self.data)))
                self.assertEqual(brand_resolution(self.cfg, self.data)["operating"], [])

    def test_subbrand_follows_brand_until_operating_company(self):
        self.data["entity-map"].append(entity(4, "brand"))
        self.data["entity-relations"] = [relation(1, "ENT-0004", "ENT-0001", "brand_of"),
                                        relation(2, "ENT-0002", "ENT-0004", "operator"),
                                        relation(3, "ENT-0003", "ENT-0004", "trademark_holder")]
        roles = brand_resolution(self.cfg, self.data)
        self.assertEqual(roles["operating"], ["ENT-0002"])
        self.assertEqual(roles["holding"], ["ENT-0003"])
        self.assertEqual(semantic_errors(self.cfg, self.data), [])
        self.data["entity-relations"] = self.data["entity-relations"][:1]
        self.assertEqual(brand_resolution(self.cfg, self.data)["operating"], [])
        self.assertTrue(listed_entities(self.cfg, self.data)[1])

    def test_verified_relation_does_not_resolve_pending_endpoint(self):
        for index in (0, 1, 2):
            with self.subTest(index=index):
                data = copy.deepcopy(self.data)
                data["entity-map"][index]["identity_status"] = "pending"
                roles = brand_resolution(self.cfg, data)
                self.assertTrue(roles["unverified_relations"])
                self.assertTrue(listed_entities(self.cfg, data)[1])
                self.assertTrue(completion_errors(self.cfg, data))

    def test_brand_cycle_is_rejected(self):
        self.data["entity-map"].append(entity(4, "brand"))
        self.data["entity-relations"] += [relation(4, "ENT-0004", "ENT-0001", "brand_of"),
                                         relation(5, "ENT-0001", "ENT-0004", "brand_of")]
        self.assertTrue(any("循环" in e for e in semantic_errors(self.cfg, self.data)))

    def test_authorization_and_supply_roles_do_not_trigger_listed_control(self):
        self.data["entity-map"].append(entity(4, listing_status="listed", exchange="TEST", security_code="123"))
        for kind in ("licensee", "manufacturer", "distributor", "minority", "joint_control"):
            with self.subTest(kind=kind):
                self.data["entity-relations"] = self.data["entity-relations"][:3] + [
                    relation(4, "ENT-0004", "ENT-0001", kind)]
                self.assertEqual(listed_entities(self.cfg, self.data), ([], False))
                self.assertNotIn("ENT-0004", brand_resolution(self.cfg, self.data)["operating"])

    def test_effective_operator_control_triggers_listed_research(self):
        self.data["entity-map"].append(entity(4, listing_status="listed", exchange="TEST", security_code="123"))
        self.data["entity-relations"].append(relation(4, "ENT-0004", "ENT-0002", "control"))
        self.assertEqual(listed_entities(self.cfg, self.data), (["ENT-0004"], False))
        self.cfg["module_scope"]["18"] = {"status": "deferred", "reason": "本次时间有限"}
        self.assertTrue(any("模块18" in e for e in semantic_errors(self.cfg, self.data)))

    def test_ended_and_proposed_roles_cannot_resolve_brand(self):
        for changes in ({"effective_to": self.cfg["as_of_date"]}, {"state": "proposed"},
                        {"effective_from": "2027-01-01"}, {"verification": "pending"}):
            with self.subTest(changes=changes):
                self.data["entity-relations"][0] = relation(1, "ENT-0002", "ENT-0001", "operator", **changes)
                self.assertEqual(brand_resolution(self.cfg, self.data)["operating"], [])
                self.assertTrue(listed_entities(self.cfg, self.data)[1])

    def test_questions_reject_bad_ids_and_unhashable_claims(self):
        for items in ([question(kq_id="Q-1")], [question(), question()],
                      [question(claim_ids=[{}])], [question(claim_ids=["C-0001", "C-0001"])],
                      [question(sub_questions=[""])], {"KQ-01": "not-an-array"}):
            with self.subTest(items=items), self.assertRaises(InputError):
                check_key_questions(items)

    def test_answered_question_needs_answer_and_supporting_claim(self):
        for item in (question(answer=" "), question(claim_ids=[]), question("unanswerable", answer="")):
            with self.subTest(item=item), self.assertRaises(InputError):
                check_key_questions([item])

    def test_unanswered_or_unanswerable_questions_block_completion(self):
        for status in ("open", "unanswerable"):
            self.cfg["key_questions"] = [question(status)]
            self.assertTrue(any("KQ-01" in e for e in completion_errors(self.cfg, self.data)))
        self.cfg["key_questions"] = []
        self.assertTrue(any("key_questions" in e for e in completion_errors(self.cfg, self.data)))

    def test_answer_with_limits_can_complete_only_with_verified_claim(self):
        self.cfg["key_questions"] = [question("answered_with_limits")]
        self.assertEqual(completion_errors(self.cfg, self.data), [])
        self.data["claim-register"][0]["verification"] = "pending"
        self.assertTrue(any("KQ-01" in e for e in completion_errors(self.cfg, self.data)))

    def test_question_missing_claim_reference_is_structural_error(self):
        self.cfg["key_questions"][0]["claim_ids"] = ["C-9999"]
        self.assertTrue(any("KQ-01" in e for e in structural_errors(self.data, self.cfg)))

    def test_deferred_core_module_is_rejected_and_noncore_is_allowed(self):
        self.cfg["module_scope"]["16"] = {"status": "deferred", "reason": "公司研究不开展交易估值"}
        self.assertEqual(semantic_errors(self.cfg, self.data), [])
        self.cfg["module_scope"]["12"] = {"status": "deferred", "reason": "缺财务数据"}
        self.assertTrue(any("模块 12" in e for e in semantic_errors(self.cfg, self.data)))

    def test_deferred_requires_nonblank_reason(self):
        self.cfg["module_scope"]["16"] = {"status": "deferred", "reason": "  "}
        with self.assertRaises(InputError):
            load_config(self.write_config())

    def test_old_config_defaults_are_read_only(self):
        old = copy.deepcopy(self.cfg)
        old["contract_version"] = "1.0.0"
        for key in ("key_questions", "completion_review", "scoring_enabled"):
            old.pop(key)
        project = self.write_config(old)
        before = (project / "project-config.json").read_bytes()
        loaded = load_config(project)
        self.assertEqual(loaded["key_questions"], [])
        self.assertIsNone(loaded["completion_review"])
        self.assertFalse(loaded["scoring_enabled"])
        self.assertEqual(before, (project / "project-config.json").read_bytes())

    def test_brand_initialization_is_pending_and_does_not_claim_research(self):
        project = Path(self.temp.name) / "brand"
        result = initialize(project, "合成品牌", target_type="brand", purpose="company_research", as_of="2026-10-20")
        cfg, data = read_project(project)
        self.assertEqual(result["target_type"], "brand")
        self.assertEqual(data["entity-map"][0]["entity_type"], "brand")
        self.assertEqual(cfg["listing_trigger"], "pending")
        self.assertEqual(cfg["key_questions"], [])
        self.assertEqual(data["search-log"], [])
        self.assertEqual(data["scorecard"], [])
        self.assertTrue((project / "estimates").is_dir())
        before = (project / "project-config.json").read_bytes()
        with self.assertRaises(InputError):
            initialize(project, "另一个目标")
        self.assertEqual(before, (project / "project-config.json").read_bytes())

    def test_plan_prioritizes_questions_and_keeps_execution_logs_empty(self):
        self.cfg["key_questions"] = [question("open", answer="", claim_ids=[])]
        before = copy.deepcopy(self.data)
        result = plan(self.cfg, self.data)
        self.assertEqual(result["tasks"][0]["task_type"], "key_question")
        self.assertEqual(result["tasks"][0]["sub_questions"], ["谁销售并收款？"])
        self.assertTrue(all(t["status"] == "not_executed" for t in result["tasks"]))
        self.assertEqual(self.data, before)
        traces = [t for t in result["tasks"] if t["task_type"] == "brand_trace"]
        resolution = next(t for t in result["tasks"] if t["task_type"] == "brand_resolution")
        self.assertEqual(len(traces), 7)
        self.assertEqual(set(resolution["depends_on"]), {t["task_id"] for t in traces})

    def test_plan_skips_deferred_candidates_but_preserves_official_basics(self):
        self.cfg["module_scope"]["16"] = {"status": "deferred", "reason": "不研究估值"}
        tasks = plan(self.cfg, self.data)["tasks"]
        self.assertFalse(any(t.get("module") == "16" and t["task_type"] == "keyword_candidate" for t in tasks))
        self.assertTrue(any(t["task_type"] == "official_site_page" for t in tasks))

    def test_person_plan_is_limited_to_target_company_roles(self):
        tasks = [t for t in plan(self.cfg, self.data)["tasks"] if t.get("entity_id") == "ENT-0003"]
        self.assertEqual({t["module"] for t in tasks}, {"01", "02", "13"})
        self.assertTrue(all('"合成品牌"' in t["query"] for t in tasks))
        self.assertTrue(all("不调查无关私人信息" in t["goal"] for t in tasks))

    def test_company_entry_does_not_receive_brand_trace_tasks(self):
        self.cfg["target_id"] = "ENT-0002"
        tasks = plan(self.cfg, self.data)["tasks"]
        self.assertFalse(any(t["task_type"] in ("brand_trace", "brand_resolution") for t in tasks))
        self.assertTrue(any(t["task_type"] == "guidance_tracking" for t in tasks))

    def undated_source(self, **changes):
        raw = {**self.data["source-register"][0], "published_date": None,
               "grade_reason": "页面未载明发布日期；仅证明访问当日可读，不能推定此前已发布。"}
        raw.update(changes)
        return record("source-register", raw)

    def research_record(self, **changes):
        raw = {"research_id": "R-0001", "source_id": "S-0001", "publisher": "回归测试",
               "title": "合成公司研报", "categories": ["company_update"],
               "category_relevance": {"company_update": "合成经营更新"},
               "target_id": "ENT-0001", "coverage_entity_id": "ENT-0002",
               "report_date": "2026-10-01", "version": "1", "access_status": "full_text",
               "reading_status": "unread", "relevance": "direct"}
        raw.update(changes)
        return record("research-register", raw)

    def test_undated_source_can_support_observed_current_information(self):
        self.data["source-register"] = [self.undated_source()]
        self.assertIsNone(self.data["source-register"][0]["published_date"])
        self.assertEqual(semantic_errors(self.cfg, self.data), [])
        self.assertEqual(completion_errors(self.cfg, self.data), [])

    def test_undated_source_requires_explained_date_limitation(self):
        for reason in (None, "", " "):
            with self.subTest(reason=reason), self.assertRaises(InputError):
                self.undated_source(grade_reason=reason)

    def test_unknown_dates_accessed_after_cutoff_must_be_isolated(self):
        self.data["source-register"] = [self.undated_source(accessed_date="2026-10-21")]
        self.assertTrue(any("须标 retrospective" in e for e in semantic_errors(self.cfg, self.data)))
        self.data["source-register"][0]["time_scope"] = "retrospective"
        errors = semantic_errors(self.cfg, self.data)
        self.assertFalse(any("须标 retrospective" in e for e in errors))
        self.assertTrue(any("事后资料" in e for e in errors))
        # 资料可保留作回溯背景，但不能支持基准日的确定判断。
        self.data["claim-register"][0]["verification"] = "pending"
        self.data["claim-evidence"][0]["relation"] = "context"
        self.assertEqual(semantic_errors(self.cfg, self.data), [])

    def test_undated_source_accessed_before_cutoff_is_available_as_of(self):
        self.data["source-register"] = [self.undated_source(accessed_date="2026-10-19")]
        self.assertEqual(semantic_errors(self.cfg, self.data), [])

    def test_real_revision_date_can_establish_source_date(self):
        self.data["source-register"] = [self.undated_source(revised_date="2026-10-01", accessed_date="2026-10-21")]
        self.assertEqual(semantic_errors(self.cfg, self.data), [])
        self.data["source-register"][0]["revised_date"] = "2026-10-22"
        errors = semantic_errors(self.cfg, self.data)
        self.assertTrue(any("访问早于" in e for e in errors))
        self.assertTrue(any("截止日后资料未隔离" in e for e in errors))

    def test_known_source_dates_keep_existing_chronology_checks(self):
        self.data["source-register"][0]["published_date"] = "2026-10-21"
        errors = semantic_errors(self.cfg, self.data)
        self.assertTrue(any("访问早于" in e for e in errors))
        self.assertTrue(any("截止日后资料未隔离" in e for e in errors))
        with self.assertRaises(InputError):
            self.undated_source(published_date="未知")

    def test_undated_research_cannot_invent_report_date_or_rank_latest(self):
        self.data["source-register"] = [self.undated_source()]
        self.data["research-register"] = [self.research_record()]
        coverage = {"target_id": "ENT-0001", "research_entity_id": "ENT-0002", "category": "company_update"}
        self.assertTrue(any("报告日期须对应" in e for e in semantic_errors(self.cfg, self.data)))
        self.assertEqual(candidates(coverage, self.data, self.cfg["as_of_date"]), [])
        with self.assertRaises(InputError):
            self.research_record(report_date=None)
        self.data["source-register"][0]["revised_date"] = "2026-10-01"
        self.assertEqual([r["research_id"] for r in candidates(coverage, self.data, self.cfg["as_of_date"])], ["R-0001"])
        self.assertEqual(semantic_errors(self.cfg, self.data), [])

    def test_control_lead_without_start_date_keeps_listing_pending(self):
        self.cfg["target_id"] = "ENT-0002"
        self.data["entity-map"].append(entity(4, listing_status="listed", exchange="TEST", security_code="123"))
        self.data["entity-relations"].append(relation(4, "ENT-0004", "ENT-0002", "control",
                                                       verification="pending", effective_from=None))
        self.assertEqual(semantic_errors(self.cfg, self.data), [])
        self.assertEqual(listed_entities(self.cfg, self.data), ([], True))
        sync_coverage(self.cfg, self.data)
        self.assertEqual(self.cfg["listing_trigger"], "pending")
        self.assertEqual(self.cfg["research_gate"], "incomplete")

    def test_undated_operator_lead_does_not_resolve_brand(self):
        self.data["entity-relations"][0] = relation(1, "ENT-0002", "ENT-0001", "operator",
                                                    verification="pending", effective_from=None)
        self.assertEqual(semantic_errors(self.cfg, self.data), [])
        roles = brand_resolution(self.cfg, self.data)
        self.assertEqual(roles["operating"], [])
        self.assertIn("REL-0001", roles["unverified_relations"])
        self.assertTrue(listed_entities(self.cfg, self.data)[1])
        self.assertTrue(any("经营主体" in e for e in completion_errors(self.cfg, self.data)))

    def test_verified_relation_still_requires_start_date_and_evidence(self):
        for changes in ({"effective_from": None}, {"evidence_ids": []}):
            with self.subTest(changes=changes), self.assertRaises(InputError):
                relation(1, "ENT-0002", "ENT-0001", "operator", **changes)

    def test_pending_unknown_start_preserves_proposed_end_and_known_start_boundaries(self):
        self.cfg["target_id"] = "ENT-0002"
        self.data["entity-map"].append(entity(4, listing_status="listed", exchange="TEST", security_code="123"))
        for changes in ({"state": "proposed"}, {"effective_to": "2026-10-19"},
                        {"effective_to": self.cfg["as_of_date"]}):
            with self.subTest(changes=changes):
                edge = relation(4, "ENT-0004", "ENT-0002", "control", verification="pending",
                                effective_from=None, **changes)
                self.data["entity-relations"] = self.data["entity-relations"][:3] + [edge]
                self.assertFalse(edge_active(edge, self.cfg["as_of_date"]))
                self.assertEqual(listed_entities(self.cfg, self.data), ([], False))
        edge = relation(4, "ENT-0004", "ENT-0002", "control", effective_from="2026-10-20", effective_to="2026-10-21")
        self.assertFalse(edge_active(edge, "2026-10-19"))
        self.assertTrue(edge_active(edge, "2026-10-20"))
        self.assertFalse(edge_active(edge, "2026-10-21"))


if __name__ == "__main__":
    unittest.main()
