"""阅读型报告的独立回归测试；仅使用临时目录中的合成资料。"""
import copy
import json
import re
import sys
import os
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(os.environ.get("ZEROX_DD_ROOT", Path(__file__).resolve().parents[3] / "zerox-due-diligence"))
sys.path.insert(0, str(ROOT / "scripts"))

from common import InputError, csv_text, read_project, record  # noqa: E402
from check_html_report import inspect_html  # noqa: E402
from check_report import check  # noqa: E402
from init_project import initialize  # noqa: E402
from reader_report import build  # noqa: E402
from report_html import render, svg_chart  # noqa: E402
from report_model import validate_content  # noqa: E402


class DocumentProbe(HTMLParser):
    """检查最终 HTML 元素和表格值，避免仅匹配转义后的字符串。"""

    def __init__(self, document):
        super().__init__()
        self.elements = []
        self.rows = []
        self._row = None
        self._cell = None
        self.feed(document)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))
        if tag == "tr":
            self._row = []
        elif tag in ("td", "th"):
            self._cell = ""

    def handle_data(self, data):
        if self._cell is not None:
            self._cell += data

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._cell is not None:
            self._row.append(self._cell)
            self._cell = None
        elif tag == "tr" and self._row is not None:
            self.rows.append(self._row)
            self._row = None


class ReaderReportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="zerox-reader-test-")
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / "synthetic-project"
        initialize(self.project, target="合成测试企业", as_of="2026-10-20", timezone="UTC")
        cfg, data = read_project(self.project)
        source = record("source-register", {
            "source_id": "S-0001",
            "title": "合成数据说明",
            "source_type": "other",
            "publisher": "独立测试",
            "published_date": "2026-01-15",
            "accessed_date": "2026-10-20",
            "locator": "https://example.invalid/synthetic-data",
            "grade": "D",
            "origin_group": "synthetic-fixture",
            "access_status": "full_text",
            "authenticity": "checked",
            "authorization": "仅测试，无真实商业资料",
            "time_scope": "as_of",
        })
        evidence = []
        for index, attribute in enumerate(("actual", "forecast", "estimate"), 1):
            evidence.append(record("evidence-ledger", {
                "evidence_id": f"E-{index:04d}",
                "source_id": "S-0001",
                "entity_id": cfg["target_id"],
                "module": "07",
                "locator": f"合成资料第 {index} 行",
                "excerpt": "仅用于验证报告处理逻辑，不能作为真实事实。",
                "period_start": "2025-01-01" if attribute != "forecast" else "2027-01-01",
                "period_end": "2025-12-31" if attribute != "forecast" else "2027-12-31",
                "geography": "测试地区",
                "currency": "CNY",
                "unit": "万元",
                "accounting_basis": "测试口径",
                "scope": "standalone",
                "attribute": attribute,
                "numeric": True,
                "value": 10 * index,
                "limitations": "完全合成的测试数据",
            }))
        for table, rows in (("source-register", [source]), ("evidence-ledger", evidence)):
            (self.project / f"{table}.csv").write_text(csv_text(table, rows), encoding="utf-8")
        self.cfg, self.data = read_project(self.project)
        self.content = {
            "version": "1.2",
            "title": "合成企业研究报告",
            "subtitle": "用于独立检验阅读稿结构",
            "language": "zh-CN",
            "summary": "有条件的综合判断。[E-0001]",
            "scope_note": "本报告仅为合成测试，不含真实企业结论。",
            "sections": [{
                "id": "operating-profile",
                "title": "业务发展与经营质量",
                "summary": "下列数据用于验证呈现行为。",
                "blocks": [self.chart()],
            }, {
                "id": "company-business",
                "title": "公司与业务怎样运转",
                "blocks": [
                    self.explanation("identity", "公司身份", "这是一家仅供测试的服务企业。"),
                    self.explanation("history_team", "起源与团队", "测试企业由合成团队创办。"),
                    self.explanation("offering", "产品与需求", "它向客户提供合成的数据整理服务。"),
                    self.explanation("customers_markets", "客户与市场", "使用和付款均由测试客户负责。"),
                    self.explanation("transaction_flow", "一笔业务怎样发生", "客户委托整理，企业交付结果后收款。"),
                    self.explanation("operating_model", "经营分工", "合成团队自行执行整理与交付。"),
                    self.explanation("revenue_costs", "收入与成本", "收入来自整理服务费，主要成本为团队人工。"),
                    self.explanation("differentiation", "客户选择及边界", "服务按测试客户需求调整，实际优势未用于商业判断。"),
                    self.explanation("financial_performance", "收入规模与利润质量", "仅有合成收入测试值，营收结构及利润率没有真实企业资料。"),
                    self.explanation("marketing", "营销与客户转化", "合成企业通过演示接触客户，转化效果只用于测试。"),
                    self.explanation("competition", "主要竞争对象", "测试企业与另一合成服务商面向相同的资料整理需求。"),
                    self.history(),
                    self.business_flow(),
                ],
            }],
        }

    def history(self):
        return {"type": "timeline", "title": "合成企业发展", "purpose": "company_history", "items": [
            {"date": "2024 年", "title": "创立", "text": "合成企业开始提供测试服务。", "status": "completed", "evidence_ids": ["E-0001"]},
            {"date": "2025 年", "title": "扩展", "text": "合成企业增加资料整理服务。", "status": "completed", "evidence_ids": ["E-0001"]}]}

    def people(self):
        return {"type": "people", "title": "创始人与合伙人", "profiles": [{"name": "合成人物甲", "role": "测试创始人", "period": "2024 年至测试截止日", "background": "合成的岗位相关经历。", "contribution": "组织资料整理服务；仅合成测试。", "limitations": "当前职责未经真实核验。", "evidence_ids": ["E-0001"]}]}

    def matrix(self):
        return {"type": "matrix", "purpose": "competition", "title": "合成企业对照", "columns": ["测试企业", "合成竞品"], "rows": [{"label": "服务范围", "cells": [
            {"text": "资料整理", "basis": "evidence", "evidence_ids": ["E-0001"]},
            {"text": "尚未取得产品范围。", "basis": "unknown", "evidence_ids": []}]}], "note": "合成事实矩阵，不包含市场评分。"}

    def image_block(self):
        import base64
        path = self.project / "materials/logo.png"
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4z8DwHwAFgAI/ScLbtAAAAABJRU5ErkJggg=="))
        return {"type": "image", "role": "logo", "path": "materials/logo.png", "title": "合成测试标识", "alt": "一个仅作媒体测试的像素", "caption": "合成图像，不能当作真实企业标识。", "source_url": "https://example.invalid/test-logo", "captured_at": "2026-10-20", "usage_note": "合成测试素材", "evidence_ids": ["E-0001"]}

    def explanation(self, topic, title, text):
        return {
            "type": "explanation",
            "topic": topic,
            "title": title,
            "text": text,
            "status": "supported",
            "evidence_ids": ["E-0001"],
            "limitations": "",
        }

    def business_flow(self):
        return {
            "type": "process",
            "purpose": "business_model",
            "title": "合成业务从委托到回款",
            "items": [
                {"title": "客户提出需求", "text": "客户委托整理合成资料。",
                 "basis": "evidence", "evidence_ids": ["E-0001"]},
                {"title": "交付并收款", "text": "企业交付整理结果，客户支付服务费。",
                 "basis": "evidence", "evidence_ids": ["E-0001"]},
            ],
        }

    def explanation_in(self, content, topic):
        return next(block for section in content["sections"] for block in section["blocks"]
                    if block["type"] == "explanation" and block["topic"] == topic)

    def legacy_content(self):
        content = copy.deepcopy(self.content)
        content["version"] = "1.0"
        content["sections"] = content["sections"][:1]
        return content

    def chart(self, chart_type="bar", values=(10, 20)):
        return {
            "type": "chart",
            "chart_type": chart_type,
            "title": "合成指标变化",
            "unit": "万元",
            "period": "2024—2025 年",
            "entity_id": self.cfg["target_id"] if hasattr(self, "cfg") else "ENT-0001",
            "kind": "actual",
            "evidence_ids": ["E-0001"],
            "note": "均为合成测试数值，无法用于判断真实企业。",
            "points": [{"label": f"项目 {index + 1}", "value": value}
                       for index, value in enumerate(values)],
        }

    def metric(self, kind="actual", evidence_id="E-0001"):
        return {
            "type": "metrics",
            "items": [{
                "label": "测试指标",
                "value": 10,
                "unit": "万元",
                "period": "2025 年",
                "entity_id": self.cfg["target_id"],
                "kind": kind,
                "evidence_ids": [evidence_id],
                "note": "合成测试数值",
            }],
        }

    def content_with(self, block):
        content = copy.deepcopy(self.content)
        content["sections"][0]["blocks"] = [block]
        return content

    def validate(self, content=None):
        return validate_content(content or self.content, self.cfg, self.data)

    def render(self, content=None):
        return render(content or self.content, self.cfg, self.data, "report-audit.md")[0]

    def test_conceptual_flow_has_distinct_rendering_without_changing_facts(self):
        block = self.business_flow()
        block["ordering"] = "conceptual"
        content = self.content_with(block)
        self.validate(content)
        probe = DocumentProbe(self.render(content))
        self.assertTrue(any("conceptual-flow" in a.get("class", "").split() for _, a in probe.elements))
        self.assertIn(block["items"][0]["text"], self.render(content))
        self.assertNotIn("conceptual-flow", " ".join(a.get("class", "") for _, a in DocumentProbe(self.render()).elements))

    def test_invalid_process_ordering_is_rejected(self):
        block = self.business_flow()
        block["ordering"] = "assumed"
        with self.assertRaisesRegex(InputError, "ordering"):
            self.validate(self.content_with(block))

    def test_mandatory_financial_marketing_competition_topics_cannot_be_omitted(self):
        for topic in ("financial_performance", "marketing", "competition"):
            content = copy.deepcopy(self.content)
            content["sections"][1]["blocks"].remove(self.explanation_in(content, topic))
            with self.subTest(topic=topic), self.assertRaisesRegex(InputError, topic):
                self.validate(content)

    def test_history_timeline_requires_two_events_in_company_section(self):
        content = copy.deepcopy(self.content)
        timeline = next(b for b in content["sections"][1]["blocks"] if b["type"] == "timeline")
        content["sections"][1]["blocks"].remove(timeline)
        with self.assertRaisesRegex(InputError, "公司发展时间线"):
            self.validate(content)
        content["sections"][0]["blocks"].append(timeline)
        with self.assertRaisesRegex(InputError, "公司介绍所在章节"):
            self.validate(content)
        timeline["items"].pop()
        with self.assertRaises(InputError):
            self.validate(content)

    def test_unavailable_history_requires_visible_limit_and_warning(self):
        content = copy.deepcopy(self.content)
        content["sections"][1]["blocks"] = [b for b in content["sections"][1]["blocks"] if b["type"] != "timeline"]
        self.explanation_in(content, "history_team").update(status="partial", limitations="只取得成立年份，后续有日期事件不足两个。")
        r = self.validate(content)
        self.assertTrue(any("不足两个有据事件" in w for w in r["warnings"]))
        self.assertIn("后续有日期事件不足两个", self.render(content))

    def test_company_timeline_cannot_turn_forecast_into_completed_event(self):
        content = copy.deepcopy(self.content)
        timeline = next(b for b in content["sections"][1]["blocks"] if b["type"] == "timeline")
        timeline["items"][1]["evidence_ids"] = ["E-0002"]
        with self.assertRaisesRegex(InputError, "预测事件"):
            self.validate(content)
        timeline["items"][1]["status"] = "planned"
        self.validate(content)

    def test_people_need_independent_section_and_source(self):
        content = copy.deepcopy(self.content)
        person = self.people()
        content["sections"][1]["blocks"].append(person)
        with self.assertRaisesRegex(InputError, "独立章节"):
            self.validate(content)
        content["sections"][1]["blocks"].pop()
        content["sections"].append({"id": "founders", "title": "创始合伙团队", "blocks": [person]})
        self.assertEqual(self.validate(content)["reader_coverage"]["people_block_count"], 1)
        self.assertIn("合成人物甲", self.render(content))
        person["profiles"][0]["evidence_ids"] = []
        with self.assertRaises(InputError):
            self.validate(content)

    def test_matrix_preserves_unknown_without_counting_as_quantitative_chart(self):
        content = self.content_with(self.matrix())
        r = self.validate(content)
        self.assertEqual(r["chart_count"], 0)
        self.assertEqual(r["reader_coverage"]["matrix_count"], 1)
        probe = DocumentProbe(self.render(content))
        self.assertTrue(any(a.get("scope") == "row" for _, a in probe.elements))
        self.assertIn("尚未取得产品范围。", self.render(content))

    def test_matrix_rejects_missing_columns_or_unsupported_assertion(self):
        for defect in ("shape", "reference", "basis"):
            block = self.matrix()
            if defect == "shape": block["rows"][0]["cells"].pop()
            elif defect == "reference": block["rows"][0]["cells"][0]["evidence_ids"] = []
            else: block["rows"][0]["cells"][0]["basis"] = "guaranteed"
            with self.subTest(defect=defect), self.assertRaises(InputError):
                self.validate(self.content_with(block))

    def test_image_is_embedded_offline_and_inspected_without_original_file(self):
        block = self.image_block()
        output = self.project / "reports/report.html"
        build(self.project, output, content=self.content_with(block))
        doc = output.read_text()
        probe = DocumentProbe(doc)
        imgs = [a for tag, a in probe.elements if tag == "img"]
        self.assertEqual(len(imgs), 1)
        self.assertTrue(imgs[0]["src"].startswith("data:image/png;base64,"))
        self.assertEqual(imgs[0]["alt"], block["alt"])
        (self.project / block["path"]).unlink()
        _, errors, _ = inspect_html(output, self.cfg, self.data)
        self.assertEqual(errors, [])
        output.write_text(doc.replace(imgs[0]["src"], "https://example.invalid/remote.png", 1))
        _, errors, _ = inspect_html(output, self.cfg, self.data)
        self.assertTrue(errors)

    def test_user_provided_local_image_keeps_attribution_without_invented_url(self):
        block = self.image_block()
        block.update(source_url="", usage_note="用户提供的合成测试素材，原始制作日期未知。")
        output = self.project / "reports/report.html"
        build(self.project, output, content=self.content_with(block))
        text, errors, _ = inspect_html(output, self.cfg, self.data)
        self.assertEqual(errors, [])
        self.assertIn("来源见证据", text)
        self.assertNotIn('href=""', output.read_text())

    def test_image_invalid_metadata_or_missing_file_does_not_publish(self):
        for defect in ("url", "date", "missing"):
            block = self.image_block()
            if defect == "url": block["source_url"] = "javascript:alert(1)"
            elif defect == "date": block["captured_at"] = "2026-02-31"
            else: (self.project / block["path"]).unlink()
            output = self.project / "reports/report.html"
            with self.subTest(defect=defect), self.assertRaises(InputError):
                build(self.project, output, content=self.content_with(block))
            self.assertFalse(output.exists())
            self.assertFalse(output.with_name("report-audit.md").exists())

    def test_legacy_11_draft_remains_readable_but_cannot_build(self):
        content = copy.deepcopy(self.content)
        content["version"] = "1.1"
        content["sections"][1]["blocks"] = [b for b in content["sections"][1]["blocks"] if b.get("topic") not in ("financial_performance", "marketing", "competition") and b["type"] != "timeline"]
        r = self.validate(content)
        self.assertEqual(r["reader_coverage"]["status"], "legacy_unchecked")
        output = self.project / "reports/report.html"
        output.write_text(self.render(content))
        output.with_name("report-audit.md").write_text("历史测试底稿")
        _, errors, warnings = inspect_html(output, self.cfg, self.data)
        self.assertEqual(errors, [])
        self.assertTrue(any("旧版 1.1" in w for w in warnings))
        with self.assertRaises(InputError):
            build(self.project, output, content=content, overwrite=True)

    def test_valid_chart_counts_and_collects_evidence(self):
        result = self.validate()
        self.assertEqual(result["chart_count"], 1)
        self.assertEqual(result["used_evidence"], ["E-0001"])

    def test_reader_coverage_maps_explanations_to_visible_anchors(self):
        result = self.validate()
        expected = {"identity", "history_team", "offering", "customers_markets",
                    "transaction_flow", "operating_model", "revenue_costs", "differentiation",
                    "financial_performance", "marketing", "competition"}
        self.assertEqual(set(result["reader_coverage"]["topics"]), expected)
        self.assertEqual(result["reader_coverage"]["business_flow_count"], 1)
        probe = DocumentProbe(self.render())
        ids = [attrs["id"] for _, attrs in probe.elements if "id" in attrs]
        for topic in expected:
            self.assertEqual(ids.count(f"topic-{topic}"), 1)
            self.assertEqual(result["reader_coverage"]["topics"][topic]["section_id"], "company-business")

    def test_missing_understanding_topic_is_rejected(self):
        content = copy.deepcopy(self.content)
        content["sections"][1]["blocks"].remove(self.explanation_in(content, "offering"))
        with self.assertRaisesRegex(InputError, "遗漏理解主题.*offering"):
            self.validate(content)

    def test_duplicate_topic_across_chapters_is_rejected(self):
        content = copy.deepcopy(self.content)
        content["sections"][0]["blocks"].append(copy.deepcopy(self.explanation_in(content, "identity")))
        with self.assertRaisesRegex(InputError, "理解主题重复.*identity"):
            self.validate(content)

    def test_supported_and_partial_explanations_need_evidence(self):
        for status in ("supported", "partial"):
            with self.subTest(status=status):
                content = copy.deepcopy(self.content)
                self.explanation_in(content, "revenue_costs").update(
                    status=status, evidence_ids=[], limitations="未取得实际成本明细，无法判断盈利水平。")
                with self.assertRaisesRegex(InputError, "revenue_costs 证据"):
                    self.validate(content)

    def test_partial_and_unknown_explanations_need_specific_limitations(self):
        for status in ("partial", "unknown"):
            for limitations in ("", "  "):
                with self.subTest(status=status, limitations=limitations):
                    content = copy.deepcopy(self.content)
                    self.explanation_in(content, "operating_model").update(
                        status=status, limitations=limitations)
                    with self.assertRaisesRegex(InputError, "operating_model 未知范围与影响"):
                        self.validate(content)

    def test_unknown_explanation_can_disclose_gap_without_fabricated_evidence(self):
        content = copy.deepcopy(self.content)
        self.explanation_in(content, "history_team").update(
            text="未取得创立背景和团队履历材料。",
            status="unknown", evidence_ids=[],
            limitations="尚不能解释团队形成及经验，合作评估需另行核验。")
        result = self.validate(content)
        self.assertEqual(result["reader_coverage"]["topics"]["history_team"]["status"], "unknown")
        self.assertEqual(result["reader_coverage"]["topics"]["history_team"]["evidence_ids"], [])
        document = self.render(content)
        self.assertIn("未取得创立背景和团队履历材料。", document)
        self.assertIn("尚不能解释团队形成及经验，合作评估需另行核验。", document)

    def test_recommendation_flow_cannot_replace_business_flow(self):
        content = copy.deepcopy(self.content)
        content["sections"][1]["blocks"][-1]["purpose"] = "recommendation"
        with self.assertRaisesRegex(InputError, "缺少 purpose=business_model"):
            self.validate(content)

    def test_unknown_transaction_can_omit_business_flow_with_visible_limit_and_warning(self):
        content = copy.deepcopy(self.content)
        content["sections"][1]["blocks"].pop()
        self.explanation_in(content, "transaction_flow").update(
            text="现有材料未说明交易怎样形成或完成。",
            status="unknown", evidence_ids=[],
            limitations="无法确认签约、交付和收款角色，因此暂不绘制目标公司的业务过程图。")
        result = self.validate(content)
        self.assertEqual(result["reader_coverage"]["business_flow_count"], 0)
        self.assertTrue(any("免画业务图" in warning for warning in result["warnings"]))
        document = self.render(content)
        self.assertIn("因此暂不绘制目标公司的业务过程图", document)
        probe = DocumentProbe(document)
        self.assertFalse(any("business-flow" in attrs.get("class", "").split()
                             for _, attrs in probe.elements))

    def test_partial_transaction_still_requires_business_flow(self):
        content = copy.deepcopy(self.content)
        content["sections"][1]["blocks"].pop()
        self.explanation_in(content, "transaction_flow").update(
            status="partial", limitations="支付账期未知，但委托和交付方式已有材料支持。")
        with self.assertRaisesRegex(InputError, "缺少 purpose=business_model"):
            self.validate(content)

    def test_business_flow_requires_two_steps_and_basis_per_step(self):
        content = copy.deepcopy(self.content)
        content["sections"][1]["blocks"][-1]["items"].pop()
        with self.assertRaisesRegex(InputError, "业务过程图.*至少 2"):
            self.validate(content)
        content = copy.deepcopy(self.content)
        del content["sections"][1]["blocks"][-1]["items"][0]["basis"]
        with self.assertRaisesRegex(InputError, "缺少.*basis"):
            self.validate(content)

    def test_known_flow_basis_requires_evidence(self):
        for basis in ("evidence", "company_claim", "inference"):
            with self.subTest(basis=basis):
                content = copy.deepcopy(self.content)
                content["sections"][1]["blocks"][-1]["items"][0].update(basis=basis, evidence_ids=[])
                with self.assertRaisesRegex(InputError, "process 证据"):
                    self.validate(content)

    def test_unknown_flow_step_renders_its_status_without_fabricated_reference(self):
        content = copy.deepcopy(self.content)
        content["sections"][1]["blocks"][-1]["items"][1].update(
            basis="unknown", evidence_ids=[], text="付款时点未取得资料，尚不能确认回款周期。")
        result = self.validate(content)
        self.assertEqual(result["used_evidence"], ["E-0001"])
        document = self.render(content)
        probe = DocumentProbe(document)
        self.assertTrue(any(tag == "span" and attrs.get("class") == "flow-basis basis-unknown"
                            for tag, attrs in probe.elements))
        self.assertIn("付款时点未取得资料，尚不能确认回款周期。", document)
        self.assertIn(">待核实</span>", document)

    def test_explanation_and_flow_unknowns_still_reject_nonexistent_references(self):
        for kind in ("explanation", "process"):
            with self.subTest(kind=kind):
                content = copy.deepcopy(self.content)
                if kind == "explanation":
                    self.explanation_in(content, "history_team").update(
                        status="unknown", evidence_ids=["E-9999"], limitations="团队资料尚未核实。")
                else:
                    content["sections"][1]["blocks"][-1]["items"][0].update(
                        basis="unknown", evidence_ids=["E-9999"])
                with self.assertRaisesRegex(InputError, "引用不存在"):
                    self.validate(content)

    def test_unedited_explanation_template_cannot_be_published(self):
        content = copy.deepcopy(self.content)
        self.explanation_in(content, "identity")["text"] = "{{待填写：公司介绍}}"
        output = self.project / "reports/report.html"
        with self.assertRaisesRegex(InputError, "残留模板占位符"):
            build(self.project, output, content=content)
        self.assertFalse(output.exists())
        self.assertFalse(output.with_name("report-audit.md").exists())

    def test_explanation_fields_are_escaped_without_creating_active_elements(self):
        content = copy.deepcopy(self.content)
        payload = '</script><script>window.injected = 1</script><img src=x onerror="alert(1)">'
        self.explanation_in(content, "identity").update(
            title=payload, text=payload, status="partial", limitations=payload)
        document = self.render(content)
        probe = DocumentProbe(document)
        self.assertFalse(any(tag == "img" for tag, _ in probe.elements))
        self.assertEqual(sum(tag == "script" for tag, _ in probe.elements), 2)
        self.assertFalse(any(any(key.startswith("on") for key in attrs) for _, attrs in probe.elements))
        self.assertIn("&lt;img", document)
        self.assertIn("\\u003c/script\\u003e", document)
        self.assertNotIn("<script>window.injected", document)
        self.assertTrue(any(attrs.get("id") == "topic-identity" for _, attrs in probe.elements))

    def test_unknown_inline_reference_is_rejected(self):
        content = copy.deepcopy(self.content)
        content["summary"] = "未知引用不能混入正文。[E-9999]"
        with self.assertRaisesRegex(InputError, "引用不存在"):
            self.validate(content)

    def test_unknown_chart_and_point_references_are_rejected(self):
        for location in ("chart", "point"):
            with self.subTest(location=location):
                block = self.chart()
                target = block if location == "chart" else block["points"][0]
                target["evidence_ids"] = ["E-9999"]
                with self.assertRaisesRegex(InputError, "引用不存在"):
                    self.validate(self.content_with(block))

    def test_missing_line_point_stays_null_and_does_not_bridge_gap(self):
        block = self.chart("line", (10, None, 30))
        document = self.render(self.content_with(block))
        probe = DocumentProbe(document)
        self.assertIn(["项目 2", "未披露", "万元", "2024—2025 年", "历史数据", "[E-0001]"], probe.rows)
        svg = DocumentProbe(svg_chart(block, "chart-test"))
        segments = [attrs for tag, attrs in svg.elements
                    if tag == "line" and attrs.get("stroke") and attrs.get("class") != "grid-line"]
        self.assertEqual(segments, [], "缺失期间不能被连续实线跨过")
        payload = json.loads(re.search(r'<script type="application/json" id="report-data">(.*?)</script>',
                                       document, re.S).group(1))
        self.assertIsNone(payload["content"]["sections"][0]["blocks"][0]["points"][1]["value"])

    def test_missing_bar_point_does_not_generate_zero_bar(self):
        block = self.chart("bar", (10, None, 30))
        self.validate(self.content_with(block))
        probe = DocumentProbe(svg_chart(block, "chart-test"))
        bars = [attrs for tag, attrs in probe.elements if tag == "rect"]
        self.assertEqual(len(bars), 2)
        self.assertNotIn("0", [attrs.get("width") for attrs in bars])

    def test_chart_requires_two_known_values(self):
        for values in ((None, None), (10, None)):
            with self.subTest(values=values), self.assertRaisesRegex(InputError, "不足两个"):
                self.validate(self.content_with(self.chart(values=values)))

    def test_donut_rejects_negative_missing_and_zero_total(self):
        for values in ((-1, 3), (None, 3), (0, 0)):
            with self.subTest(values=values), self.assertRaises(InputError):
                self.validate(self.content_with(self.chart("donut", values)))

    def test_signed_bar_values_are_valid_and_visible(self):
        block = self.chart("bar", (-10, 20))
        self.validate(self.content_with(block))
        probe = DocumentProbe(svg_chart(block, "chart-test"))
        self.assertTrue(any(attrs.get("class") == "zero-line" for _, attrs in probe.elements))
        self.assertIn("-10", self.render(self.content_with(block)))

    def test_nonfinite_and_boolean_values_are_rejected(self):
        for value in (True, float("nan"), float("inf"), -float("inf")):
            with self.subTest(value=value), self.assertRaises(InputError):
                self.validate(self.content_with(self.chart(values=(10, value))))

    def test_forecast_evidence_cannot_become_actual_chart(self):
        block = self.chart()
        block["evidence_ids"] = ["E-0002"]
        with self.assertRaisesRegex(InputError, "预测"):
            self.validate(self.content_with(block))

    def test_forecast_evidence_cannot_become_actual_metric(self):
        with self.assertRaises(InputError):
            self.validate(self.content_with(self.metric(evidence_id="E-0002")))

    def test_estimate_evidence_cannot_become_actual_chart(self):
        block = self.chart()
        block["evidence_ids"] = ["E-0003"]
        with self.assertRaises(InputError):
            self.validate(self.content_with(block))

    def test_estimate_evidence_cannot_become_actual_metric(self):
        with self.assertRaises(InputError):
            self.validate(self.content_with(self.metric(evidence_id="E-0003")))

    def test_mixed_chart_requires_point_attributes(self):
        block = self.chart()
        block["kind"] = "mixed"
        with self.assertRaisesRegex(InputError, "kind"):
            self.validate(self.content_with(block))

    def test_forecast_line_has_dashed_segment_and_visible_label(self):
        block = self.chart("line")
        block["kind"] = "mixed"
        block["points"][0].update(kind="actual", evidence_ids=["E-0001"])
        block["points"][1].update(kind="forecast", period="2027 年", evidence_ids=["E-0002"])
        document = self.render(self.content_with(block))
        probe = DocumentProbe(document)
        self.assertIn(["项目 2", "20", "万元", "2027 年", "预测", "[E-0002]"], probe.rows)
        self.assertTrue(any(tag == "line" and attrs.get("stroke-dasharray") not in (None, "none")
                            for tag, attrs in probe.elements))
        self.assertIn("20 预测", document)

    def test_author_text_cannot_create_html_or_script_elements(self):
        content = copy.deepcopy(self.content)
        payload = '</script><script>window.injected = 1</script><img src=x onerror="alert(1)">'
        content["title"] = payload
        content["summary"] = payload
        content["sections"][0]["blocks"][0]["title"] = payload
        content["sections"][0]["blocks"][0]["points"][0]["label"] = payload
        self.data["source-register"][0]["title"] = payload
        document = self.render(content)
        probe = DocumentProbe(document)
        self.assertFalse(any(tag == "img" for tag, _ in probe.elements))
        scripts = [attrs for tag, attrs in probe.elements if tag == "script"]
        self.assertEqual(len(scripts), 2, "仅允许一个数据快照和一个自带交互脚本")
        self.assertFalse(any(any(key.startswith("on") for key in attrs) for _, attrs in probe.elements))
        self.assertIn("&lt;img", document)
        self.assertIn("\\u003c/script\\u003e", document)
        self.assertNotIn("<script>window.injected", document)

    def test_unsafe_source_url_is_never_clickable(self):
        for url in ("javascript:alert(1)", "data:text/html,<script>alert(1)</script>",
                    "https://user:password@example.invalid/private"):
            with self.subTest(url=url):
                self.data["source-register"][0]["locator"] = url
                probe = DocumentProbe(self.render())
                self.assertFalse(any(attrs.get("href") == url for tag, attrs in probe.elements if tag == "a"))

    def test_chart_has_accessible_svg_and_sourced_data_table(self):
        probe = DocumentProbe(self.render())
        svgs = [attrs for tag, attrs in probe.elements if tag == "svg"]
        self.assertEqual(len(svgs), 1)
        self.assertEqual(svgs[0]["role"], "img")
        self.assertIn("chart-1-title", svgs[0]["aria-labelledby"])
        self.assertIn("chart-1-desc", svgs[0]["aria-labelledby"])
        self.assertTrue(any(tag == "details" and attrs.get("class") == "data-table"
                            for tag, attrs in probe.elements))
        self.assertIn(["项目", "数值", "单位", "期间", "属性", "证据"], probe.rows)
        self.assertIn(["项目 1", "10", "万元", "2024—2025 年", "历史数据", "[E-0001]"], probe.rows)

    def test_process_chapter_titles_are_rejected_in_main_report(self):
        for title in ("检索日志", "研究完成范围", "评分覆盖", "资料请求清单", "Search log"):
            with self.subTest(title=title):
                content = copy.deepcopy(self.content)
                content["sections"][0]["title"] = title
                with self.assertRaisesRegex(InputError, "过程章节"):
                    self.validate(content)

    def test_repeated_reserved_or_unsafe_section_ids_are_rejected(self):
        for sid in ("overview", "sources", "chart-1", "topic-identity", "topic-custom", 'x" onclick="evil', "UPPER"):
            with self.subTest(sid=sid):
                content = copy.deepcopy(self.content)
                content["sections"][0]["id"] = sid
                with self.assertRaises(InputError):
                    self.validate(content)
        content = copy.deepcopy(self.content)
        content["sections"].append(copy.deepcopy(content["sections"][0]))
        with self.assertRaises(InputError):
            self.validate(content)

    def test_qualitative_content_does_not_count_as_quantitative_chart(self):
        block = {
            "type": "timeline",
            "title": "业务里程碑",
            "items": [{"title": "计划节点", "text": "尚待执行", "date": "2027 年",
                       "status": "planned", "evidence_ids": ["E-0002"]}],
        }
        result = self.validate(self.content_with(block))
        self.assertEqual(result["chart_count"], 0)
        self.assertTrue(result["warnings"])

    def test_html_build_produces_reader_and_separate_audit(self):
        output = self.project / "reports/report.html"
        result = build(self.project, output, content=self.content)
        audit = output.with_name("report-audit.md")
        self.assertEqual(result["artifact_role"], "reader_report")
        self.assertTrue(output.is_file())
        self.assertTrue(audit.is_file())
        self.assertIn('href="report-audit.md"', output.read_text())
        self.assertIn("模块 01", audit.read_text())
        self.assertNotIn("模块 01", output.read_text())
        self.assertEqual(result["visual_review"]["summary"]["counts"]["quantitative_charts"], 1)
        self.assertIn("逐章可视化编辑复核", audit.read_text())
        self.assertNotIn("逐章可视化编辑复核", output.read_text())
        checked = check(self.project, output)
        self.assertEqual(checked["visual_review"], result["visual_review"])
        self.assertEqual(checked["status"], "structure_passed")

    def test_html_content_is_required_without_writing_output(self):
        output = self.project / "reports/report.html"
        with self.assertRaisesRegex(InputError, "--content"):
            build(self.project, output)
        self.assertFalse(output.exists())
        self.assertFalse(output.with_name("report-audit.md").exists())

    def test_legacy_content_cannot_build_new_html_or_leave_partial_outputs(self):
        output = self.project / "reports/report.html"
        with self.assertRaisesRegex(InputError, "新 HTML.*version=1.2"):
            build(self.project, output, content=self.legacy_content())
        self.assertFalse(output.exists())
        self.assertFalse(output.with_name("report-audit.md").exists())

    def test_legacy_html_draft_inspection_warns_and_completed_inspection_rejects(self):
        output = self.project / "reports/report.html"
        output.write_text(self.render(self.legacy_content()), encoding="utf-8")
        output.with_name("report-audit.md").write_text("历史合成研究底稿", encoding="utf-8")
        _, errors, warnings = inspect_html(output, self.cfg, self.data)
        self.assertEqual(errors, [])
        self.assertTrue(any("旧版 1.0" in warning for warning in warnings))
        _, errors, _ = inspect_html(output, self.cfg, self.data, require_current=True)
        self.assertTrue(any("完成态报告必须使用 1.2" in error for error in errors))
        completed = check(self.project, output, mode="completed")
        self.assertTrue(any("完成态报告必须使用 1.2" in error for error in completed["errors"]))

    def test_existing_reader_or_audit_is_preflighted_without_overwrite(self):
        for suffix in ("report.html", "report-audit.md"):
            with self.subTest(existing=suffix):
                output = self.project / "reports/report.html"
                existing = output.with_name(suffix)
                existing.write_text("原有文件不得改变", encoding="utf-8")
                try:
                    with self.assertRaisesRegex(InputError, "--overwrite"):
                        build(self.project, output, content=self.content)
                    self.assertEqual(existing.read_text(), "原有文件不得改变")
                    other = output.with_name("report-audit.md") if existing == output else output
                    self.assertFalse(other.exists())
                finally:
                    existing.unlink()

    def test_explicit_overwrite_updates_both_outputs(self):
        output = self.project / "reports/report.html"
        audit = output.with_name("report-audit.md")
        output.write_text("旧正文", encoding="utf-8")
        audit.write_text("旧底稿", encoding="utf-8")
        build(self.project, output, content=self.content, overwrite=True)
        self.assertIn("<!doctype html>", output.read_text())
        self.assertNotEqual(audit.read_text(), "旧底稿")

    def test_invalid_content_preserves_existing_outputs_even_with_overwrite(self):
        output = self.project / "reports/report.html"
        audit = output.with_name("report-audit.md")
        output.write_text("旧正文", encoding="utf-8")
        audit.write_text("旧底稿", encoding="utf-8")
        content = copy.deepcopy(self.content)
        content["summary"] = "错误引用。[E-9999]"
        with self.assertRaises(InputError):
            build(self.project, output, content=content, overwrite=True)
        self.assertEqual(output.read_text(), "旧正文")
        self.assertEqual(audit.read_text(), "旧底稿")

    def test_audit_generation_failure_does_not_publish_partial_pair(self):
        output = self.project / "reports/report.html"
        (self.project / "modules/01-a.md").write_text("测试版本甲", encoding="utf-8")
        (self.project / "modules/01-b.md").write_text("测试版本乙", encoding="utf-8")
        with self.assertRaisesRegex(InputError, "多个候选版本"):
            build(self.project, output, content=self.content)
        self.assertFalse(output.exists())
        self.assertFalse(output.with_name("report-audit.md").exists())

    def test_legacy_markdown_remains_explicit_audit_output(self):
        output = self.project / "reports/legacy.md"
        result = build(self.project, output, sections={"summary": "兼容旧调用的测试摘要"})
        self.assertEqual(result["artifact_role"], "audit_workpaper")
        self.assertIn("兼容旧调用的测试摘要", output.read_text())
        self.assertIn("模块 01", output.read_text())
        with self.assertRaises(InputError):
            build(self.project, output.with_name("wrong.md"), content=self.content)

    def test_html_rejects_legacy_sections_and_unknown_output_extension(self):
        for name, extra in (("report.html", {"sections": {"summary": "旧参数"}}),
                            ("report.txt", {})):
            with self.subTest(name=name), self.assertRaises(InputError):
                build(self.project, self.project / "reports" / name, content=self.content, **extra)

    def test_html_checker_accepts_generated_report_with_audit(self):
        output = self.project / "reports/report.html"
        build(self.project, output, content=self.content)
        text, errors, warnings = inspect_html(output, self.cfg, self.data)
        self.assertEqual(errors, [])
        self.assertIn("合成企业研究报告", text)
        self.assertTrue(all("未单列人物" in w or "未使用真实企业素材" in w or "可视化编辑复核｜" in w for w in warnings), warnings)

    def test_html_checker_rejects_visible_text_or_svg_tampering(self):
        output = self.project / "reports/report.html"
        build(self.project, output, content=self.content)
        original = output.read_text(encoding="utf-8")
        variants = {
            "正文": original.replace("有条件的综合判断。", "未经支持的确定断言。", 1),
            "图形": re.sub(r'(<rect\b[^>]*\bwidth=")[^"]*(")', r"\g<1>1\g<2>", original, count=1),
        }
        for kind, changed in variants.items():
            with self.subTest(kind=kind):
                self.assertNotEqual(original, changed)
                output.write_text(changed, encoding="utf-8")
                _, errors, _ = inspect_html(output, self.cfg, self.data)
                self.assertTrue(any("可见正文或图形" in error for error in errors), errors)

    def test_html_checker_rejects_payload_project_mismatch(self):
        output = self.project / "reports/report.html"
        build(self.project, output, content=self.content)
        original = output.read_text(encoding="utf-8")
        pattern = r'(<script type="application/json" id="report-data">)(.*?)(</script>)'
        match = re.search(pattern, original, re.S)
        payload = json.loads(match.group(2))
        payload["project"]["as_of_date"] = "2026-10-19"
        changed = re.sub(pattern, lambda m: m.group(1) + json.dumps(payload, ensure_ascii=False) + m.group(3),
                         original, count=1, flags=re.S)
        output.write_text(changed, encoding="utf-8")
        _, errors, _ = inspect_html(output, self.cfg, self.data)
        self.assertTrue(any("与项目不一致" in error for error in errors), errors)

    def test_html_checker_rejects_missing_audit_file(self):
        output = self.project / "reports/report.html"
        build(self.project, output, content=self.content)
        output.with_name("report-audit.md").unlink()
        _, errors, _ = inspect_html(output, self.cfg, self.data)
        self.assertTrue(any("独立核验底稿不存在" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
