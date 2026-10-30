"""扩展图示的语义边界与最终 HTML 回归，均为合成数据。"""
import copy
import json
import re
import sys
import os
import unittest
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(os.environ.get("ZEROX_DD_ROOT", Path(__file__).resolve().parents[3] / "zerox-due-diligence"))
sys.path.insert(0, str(ROOT / "scripts"))

from common import InputError
from check_html_report import inspect_html
from report_html import render, svg_chart
from report_model import validate_content
import test_reader_report as reader_fixtures
from test_reader_report import DocumentProbe


class VisualExhibitTests(unittest.TestCase):
    def setUp(self):
        self.fixture = reader_fixtures.ReaderReportTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.cfg, self.data = self.fixture.cfg, self.fixture.data

    def chart(self, kind):
        chart = self.fixture.chart(kind)
        if kind == "range":
            chart["points"] = [{"label": "报价范围", "low": 15, "high": 50}]
        elif kind == "waterfall":
            chart["points"] = [{"label": "期初", "value": 100, "role": "start"},
                               {"label": "增加", "value": 30, "role": "delta"},
                               {"label": "减少", "value": -20, "role": "delta"},
                               {"label": "期末", "value": 110, "role": "total"}]
        elif kind == "stacked_bar":
            chart["points"] = [{"label": year, "segments": [{"label": "服务", "value": service}, {"label": "产品", "value": product}]}
                               for year, service, product in [("2024", 30, 10), ("2025", 40, 20)]]
        elif kind == "proportion":
            chart.update(unit="%", scale_max=100, points=[{"label": "企业自述客户占比", "value": 70}])
        return chart

    def diagram(self):
        return {"type": "diagram", "title": "合成企业交易关系", "purpose": "business_model", "period": "2025", "entity_id": self.cfg["target_id"], "note": "只表达有据流向，未取得合同细节。", "nodes": [
            {"id": "company", "label": "测试企业", "text": "向客户提供整理服务。", "basis": "evidence", "evidence_ids": ["E-0001"]},
            {"id": "customer", "label": "客户", "text": "提出需求并承担费用。", "basis": "company_claim", "evidence_ids": ["E-0001"]}], "edges": [
            {"source": "company", "target": "customer", "label": "交付整理服务", "flow": "product", "basis": "evidence", "evidence_ids": ["E-0001"]},
            {"source": "customer", "target": "company", "label": "支付服务费用", "flow": "money", "basis": "inference", "evidence_ids": ["E-0001"]}]}

    def content(self, *blocks):
        content = copy.deepcopy(self.fixture.content)
        content["sections"][0]["blocks"] = list(blocks)
        return content

    def validate(self, *blocks):
        return validate_content(self.content(*blocks), self.cfg, self.data)

    def document(self, *blocks):
        return render(self.content(*blocks), self.cfg, self.data, "visual-audit.md")[0]

    def test_all_five_chart_types_render_and_count(self):
        kinds = ("column", "range", "waterfall", "stacked_bar", "proportion")
        for kind in kinds:
            with self.subTest(kind=kind):
                block = self.chart(kind)
                self.assertEqual(self.validate(block)["chart_count"], 1)
                ElementTree.fromstring(svg_chart(block, "chart-1"))
                self.assertIn('<figure class="chart"', self.document(block))

    def test_column_is_distinct_from_original_horizontal_bar(self):
        original = self.chart("bar")
        extended = dict(original, chart_type="column")
        self.assertNotEqual(svg_chart(original, "chart-1"), svg_chart(extended, "chart-1"))
        self.assertIn("纵向柱状比较", svg_chart(extended, "chart-1"))

    def test_column_signed_missing_points(self):
        block = self.chart("column")
        block["points"] = [{"label": "负值", "value": -10}, {"label": "未知", "value": None}, {"label": "零", "value": 0}]
        self.validate(block)
        self.assertIn("-10", self.document(block))
        self.assertIn("未披露", self.document(block))

    def test_single_range_preserves_bounds_without_midpoint(self):
        block = self.chart("range")
        probe = DocumentProbe(self.document(block))
        self.assertIn(["报价范围", "15", "50", "万元", "2024—2025 年", "历史数据", "[E-0001]"], probe.rows)
        self.assertNotIn("32.5", self.document(block))

    def test_range_allows_missing_pair_and_zero_width(self):
        block = self.chart("range")
        block["points"] += [{"label": "同值", "low": 0, "high": 0}, {"label": "未披露", "low": None, "high": None}]
        self.validate(block)
        self.assertIn("区间未披露", self.document(block))

    def test_range_rejects_inverted_half_missing_nonfinite_boolean(self):
        for low, high in [(50, 15), (None, 5), (5, None), (float("inf"), 20), (True, 10), (1, float("nan"))]:
            with self.subTest(low=low, high=high):
                block = self.chart("range")
                block["points"][0].update(low=low, high=high)
                with self.assertRaises(InputError): self.validate(block)

    def test_range_requires_one_known_interval(self):
        block = self.chart("range")
        block["points"][0].update(low=None, high=None)
        with self.assertRaises(InputError): self.validate(block)

    def test_proportion_one_value_has_explicit_scale_no_complement(self):
        block = self.chart("proportion")
        document = self.document(block)
        self.assertIn("灰色轨道仅为量尺", document)
        self.assertIn(["企业自述客户占比", "70", "100", "%", "2024—2025 年", "历史数据", "[E-0001]"], DocumentProbe(document).rows)
        self.assertNotIn("其他客户", document)

    def test_proportion_accepts_nonpercentage_scale_and_null(self):
        block = self.chart("proportion")
        block.update(unit="份（量尺十份）", scale_max=10)
        block["points"] = [{"label": "已知", "value": 3}, {"label": "未知", "value": None}]
        self.validate(block)
        self.assertIn("未披露", self.document(block))

    def test_proportion_rejects_wrong_scale_out_of_bounds_or_all_missing(self):
        for maximum, value in [(0, 0), (-1, 0), (True, 1), (float("inf"), 2), (10, 7), (100, -1), (100, 101), (100, None)]:
            with self.subTest(maximum=maximum, value=value):
                block = self.chart("proportion")
                block["scale_max"] = maximum
                block["points"][0]["value"] = value
                with self.assertRaises(InputError): self.validate(block)
        block = self.chart("proportion")
        del block["scale_max"]
        with self.assertRaises(InputError): self.validate(block)

    def test_proportion_limits_eight_points(self):
        block = self.chart("proportion")
        block["points"] = [{"label": str(i), "value": i} for i in range(9)]
        with self.assertRaises(InputError): self.validate(block)

    def test_waterfall_intermediate_total_is_not_added_twice(self):
        block = self.chart("waterfall")
        block["points"].insert(2, {"label": "中间合计", "value": 130, "role": "total"})
        self.validate(block)
        rows = DocumentProbe(self.document(block)).rows
        self.assertTrue(any(row[:3] == ["减少", "-20", "delta · 变动"] for row in rows))
        self.assertTrue(any(row[:3] == ["期末", "110", "total · 合计"] for row in rows))

    def test_waterfall_float_arithmetic_and_negative_start(self):
        block = self.chart("waterfall")
        block["points"] = [{"label": "起点", "value": -.1, "role": "start"}, {"label": "变动", "value": .3, "role": "delta"}, {"label": "合计", "value": .2, "role": "total"}]
        self.validate(block)
        ElementTree.fromstring(svg_chart(block, "chart-1"))

    def test_waterfall_rejects_wrong_math_missing_values_and_roles(self):
        for mutate in [lambda p:p[-1].update(value=111), lambda p:p[1].update(value=None), lambda p:p[0].update(role="total"), lambda p:p[-1].update(role="delta"), lambda p:p[1].update(role="start"), lambda p:p[2].update(role="other")]:
            block = self.chart("waterfall")
            mutate(block["points"])
            with self.assertRaises(InputError): self.validate(block)

    def test_waterfall_large_totals_cannot_hide_unit_difference(self):
        block = self.chart("waterfall")
        block["points"] = [{"label": "起点", "value": 10**12, "role": "start"}, {"label": "增量", "value": 1, "role": "delta"}, {"label": "合计", "value": 10**12, "role": "total"}]
        with self.assertRaises(InputError): self.validate(block)

    def test_waterfall_limits_twelve_points(self):
        block = self.chart("waterfall")
        block["points"] = [{"label": "初", "value": 1, "role": "start"}] + [{"label": str(i), "value": 1, "role": "delta"} for i in range(11)] + [{"label": "末", "value": 12, "role": "total"}]
        with self.assertRaises(InputError): self.validate(block)

    def test_stacked_preserves_raw_series_values_and_coverage_note(self):
        block = self.chart("stacked_bar")
        document = self.document(block)
        self.assertIn(["2025", "产品", "20", "万元", "2024—2025 年", "历史数据", "[E-0001]"], DocumentProbe(document).rows)
        self.assertIn("整体分母及分类是否完整", document)
        self.assertNotIn("50%", " ".join(" ".join(row) for row in DocumentProbe(document).rows))

    def test_stacked_rejects_missing_negative_mismatched_or_duplicate_series(self):
        for mutation in [lambda p:p[0]["segments"][0].update(value=None), lambda p:p[0]["segments"][0].update(value=-1), lambda p:p[1]["segments"].reverse(), lambda p:p[1]["segments"][0].update(label="不同"), lambda p:p[0]["segments"][0].update(label="产品")]:
            block=self.chart("stacked_bar");mutation(block["points"])
            with self.assertRaises(InputError): self.validate(block)

    def test_stacked_limits_groups_series_and_total_segments(self):
        for groups, count in [(1,2), (9,2), (2,1), (2,7), (5,5)]:
            block=self.chart("stacked_bar")
            block["points"]=[{"label":str(i),"segments":[{"label":str(j),"value":1} for j in range(count)]} for i in range(groups)]
            with self.assertRaises(InputError):self.validate(block)

    def test_stacked_zero_groups_remain_valid(self):
        block = self.chart("stacked_bar")
        for point in block["points"]:
            for segment in point["segments"]:segment["value"]=0
        self.validate(block)
        ElementTree.fromstring(svg_chart(block, "chart-1"))

    def test_new_charts_reject_conflicting_block_and_point_attributes(self):
        for kind in ("column", "range", "waterfall", "stacked_bar", "proportion"):
            block = self.chart(kind)
            point = block["points"][0]
            if kind == "stacked_bar":point=point["segments"][0]
            point.update(kind="forecast",evidence_ids=["E-0002"])
            with self.subTest(kind=kind), self.assertRaises(InputError):self.validate(block)

    def test_mixed_stacked_requires_every_segment_attribute_and_marks_forecast(self):
        block = self.chart("stacked_bar");block["kind"]="mixed"
        with self.assertRaises(InputError):self.validate(block)
        for point in block["points"]:
            point["segments"][0].update(kind="actual",evidence_ids=["E-0001"])
            point["segments"][1].update(kind="forecast",evidence_ids=["E-0002"])
        self.validate(block)
        document=self.document(block)
        self.assertIn('stroke-dasharray="5 4"',document)
        self.assertIn("预测",document)

    def test_actual_rejects_estimate_and_forecast_at_both_levels(self):
        for eid in ("E-0002","E-0003"):
            for location in ("block","point"):
                block=self.chart("range")
                target=block if location=="block" else block["points"][0]
                target["evidence_ids"]=[eid]
                with self.subTest(eid=eid,location=location), self.assertRaises(InputError):self.validate(block)

    def test_unknown_evidence_and_duplicate_labels_rejected(self):
        for kind in ("column","range","waterfall","stacked_bar","proportion"):
            block=self.chart(kind);block["evidence_ids"]=["E-9999"]
            with self.assertRaises(InputError):self.validate(block)
            block=self.chart(kind);block["points"].append(copy.deepcopy(block["points"][0]))
            with self.assertRaises(InputError):self.validate(block)

    def test_diagram_is_not_quantitative_chart(self):
        result=self.validate(self.diagram())
        self.assertEqual(result["chart_count"],0)
        self.assertEqual(result["reader_coverage"]["diagram_count"],1)
        self.assertIn('class="relationship-diagram"',self.document(self.diagram()))

    def test_business_diagram_replaces_business_process_only_with_matching_purpose(self):
        content=self.content(self.diagram())
        content["sections"][1]["blocks"]=[b for b in content["sections"][1]["blocks"] if b["type"]!="process"]
        validate_content(content,self.cfg,self.data)
        content["sections"][0]["blocks"][0]["purpose"]="marketing"
        with self.assertRaises(InputError):validate_content(content,self.cfg,self.data)

    def test_diagram_validates_nodes_endpoints_duplicates_self_and_isolation(self):
        mutations=[lambda b:b["nodes"][1].update(id="company"),lambda b:b["nodes"][0].update(id='bad"id'),lambda b:b["edges"][0].update(target="missing"),lambda b:b["edges"][0].update(target="company"),lambda b:b["edges"].append(copy.deepcopy(b["edges"][0])),lambda b:b["nodes"].append(dict(b["nodes"][0],id="isolated"))]
        for mutation in mutations:
            block=self.diagram();mutation(block)
            with self.assertRaises(InputError):self.validate(block)

    def test_diagram_requires_sources_except_explicit_unknown(self):
        for location in ("nodes","edges"):
            block=self.diagram();block[location][0]["evidence_ids"]=[]
            with self.assertRaises(InputError):self.validate(block)
            block[location][0]["basis"]="unknown"
            self.validate(block)
            self.assertIn("待核实",self.document(block))

    def test_diagram_limits_and_invalid_flow(self):
        for mutation in [lambda b:b.update(nodes=b["nodes"][:1]),lambda b:b.update(edges=[]),lambda b:b["edges"][0].update(flow="other"),lambda b:b["edges"][0].update(basis="fake"),lambda b:b.update(entity_id="ENT-9999")]:
            block=self.diagram();mutation(block)
            with self.assertRaises(InputError):self.validate(block)

    def test_diagram_distinguishes_flow_basis_and_has_full_fallback(self):
        block=self.diagram();block["nodes"][0]["text"]="完整角色解释，仅此处描述交付的具体边界。"
        document=self.document(block)
        self.assertIn('stroke-dasharray="6 4"',document)
        self.assertIn("完整角色解释，仅此处描述交付的具体边界。",document)
        self.assertIn(["客户","测试企业","支付服务费用","资金","分析示意","[E-0001]"],DocumentProbe(document).rows)

    def test_svg_author_text_is_escaped_and_ids_unique(self):
        diagram=self.diagram();diagram["nodes"][0]["label"]='<script>alert("坏")</script>'
        diagram["edges"][0]["label"]='输入 <img onerror="坏"> & 分析'
        chart=self.chart("range");chart["points"][0]["label"]='报价 <script> & "值"'
        document=self.document(chart,diagram,diagram)
        self.assertNotIn('<script>alert',document)
        self.assertNotIn('<img onerror',document)
        ids=re.findall(r'\bid="([^"]+)"',document)
        self.assertEqual(len(ids),len(set(ids)))
        self.assertIn('diagram-1-arrow-product',ids)
        self.assertIn('diagram-2-arrow-product',ids)

    def test_diagram_long_labels_not_truncated(self):
        block=self.diagram()
        label="供应链角色说明"*12
        block["nodes"][0]["label"]=label
        block["edges"][0]["label"]="长期服务合同中的交付与验收关系"*10
        document=self.document(block)
        self.assertIn(label,document)
        self.assertIn(block["edges"][0]["label"],document)
        ElementTree.fromstring(re.search(r'(<svg.*?</svg>)',document,re.S)[1])

    def test_diagram_ids_skip_legacy_sections_and_derived_anchor_collisions(self):
        for sid in ("diagram-1", "diagram-1-title", "diagram-1-desc", "diagram-1-arrow-product", "diagram-1-edge-1", "diagram-1-edge-note-1"):
            content=self.content(self.diagram(),self.diagram())
            content["sections"][0]["id"]=sid
            validate_content(content,self.cfg,self.data)
            document=render(content,self.cfg,self.data,"visual-audit.md")[0]
            ids=re.findall(r'\bid="([^"]+)"',document)
            self.assertEqual(len(ids),len(set(ids)))
            self.assertIn(sid,ids)
            self.assertIn('id="diagram-2"',document)
            self.assertIn('id="diagram-3"',document)

    def test_new_blocks_are_not_accepted_in_old_versions(self):
        for block in (self.diagram(),self.chart("range")):
            content=self.fixture.legacy_content();content["sections"][0]["blocks"]=[block]
            with self.assertRaises(InputError):validate_content(content,self.cfg,self.data)

    def test_new_chart_source_tables_preserve_full_decimal_precision(self):
        block=self.chart("range")
        block["points"][0].update(low=0.1234567,high=0.7654321)
        rows=DocumentProbe(self.document(block)).rows
        self.assertTrue(any(row[:3]==["报价范围","0.1234567","0.7654321"] for row in rows))

    def test_maximum_diagram_and_explicit_size_limits(self):
        block=self.diagram()
        block["nodes"]=[dict(block["nodes"][0],id=f"node-{i}",label=f"角色 {i}") for i in range(6)]
        block["edges"]=[dict(block["edges"][0],source=f"node-{i%6}",target=f"node-{(i+1)%6}",label=f"关系 {i}") for i in range(10)]
        self.validate(block)
        document=self.document(block)
        ElementTree.fromstring(re.search(r'(<svg.*?</svg>)',document,re.S)[1])
        overflow=copy.deepcopy(block)
        overflow["nodes"].append(dict(block["nodes"][0],id="node-6"))
        with self.assertRaises(InputError):self.validate(overflow)
        overflow=copy.deepcopy(block)
        overflow["edges"].append(dict(block["edges"][0],label="第十一条关系"))
        with self.assertRaises(InputError):self.validate(overflow)

    def test_many_columns_use_generated_minimum_width(self):
        block=self.chart("column")
        block["points"]=[{"label":f"类别 {i}","value":i} for i in range(24)]
        self.validate(block)
        svg=svg_chart(block,"chart-1")
        self.assertIn('style="--plot-min-width:2020px"',svg)
        block["points"].append({"label":"超出","value":1})
        with self.assertRaises(InputError):self.validate(block)

    def test_large_integer_range_values_are_not_rounded_through_float(self):
        block=self.chart("range")
        block["points"][0].update(low=9007199254740993,high=9007199254740995)
        rows=DocumentProbe(self.document(block)).rows
        self.assertTrue(any(row[:3]==["报价范围","9,007,199,254,740,993","9,007,199,254,740,995"] for row in rows))

    def test_stacked_decimal_derived_total_has_no_binary_artifact(self):
        block=self.chart("stacked_bar")
        for point in block["points"]:
            point["segments"][0]["value"]=0.1
            point["segments"][1]["value"]=0.2
        svg=svg_chart(block,"chart-1")
        self.assertIn('>0.3</text>',svg)
        self.assertNotIn('0.30000000000000004',svg)

    def test_derived_axis_ticks_do_not_expose_binary_tails(self):
        for kind in ("column", "range"):
            block=self.chart(kind)
            if kind=="column":
                block["points"][0]["value"]=0.1
                block["points"][1]["value"]=0.3
            else:
                block["points"][0].update(low=0.1,high=0.3)
            svg=svg_chart(block,"chart-1")
            self.assertNotIn("0.224999",svg)
            self.assertIn(">0.225</text>",svg)

    def test_diagram_network_has_curved_directional_edges_and_numbered_notes(self):
        block=self.diagram()
        document=self.document(block)
        svg=ElementTree.fromstring(re.search(r'(<svg.*?</svg>)',document,re.S)[1])
        edges=[p for p in svg.iter("path") if "-edge-" in p.get("id","")]
        self.assertEqual(len(edges),2)
        self.assertNotEqual(edges[0].get("d"),edges[1].get("d"))
        self.assertTrue(all(" Q " in edge.get("d") for edge in edges))
        self.assertTrue(all(edge.get("stroke-width")=="2.5" for edge in edges))
        self.assertEqual(len([g for g in svg.iter("g") if g.get("class")=="diagram-network-node"]),2)
        self.assertIn('href="#diagram-1-edge-note-1"',document)
        self.assertIn('id="diagram-1-edge-note-1"',document)
        self.assertIn("环形排列仅为布局",document)
        self.assertLess(float(svg.get("viewBox").split()[-1]),600)

    def test_html_checker_roundtrip_and_diagram_tamper(self):
        blocks=[self.chart(kind) for kind in ("column","range","waterfall","stacked_bar","proportion")]+[self.diagram()]
        path=self.fixture.project / "visual.html"
        (path.parent/"visual-audit.md").write_text("合成测试底稿",encoding="utf-8")
        document=self.document(*blocks);path.write_text(document,encoding="utf-8")
        _,errors,_=inspect_html(path,self.cfg,self.data)
        self.assertEqual(errors,[])
        path.write_text(document.replace('marker-end="url(#diagram-1-arrow-product)"','marker-end="url(#diagram-1-arrow-money)"',1),encoding="utf-8")
        _,errors,_=inspect_html(path,self.cfg,self.data)
        self.assertTrue(any("图形与阅读稿" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
