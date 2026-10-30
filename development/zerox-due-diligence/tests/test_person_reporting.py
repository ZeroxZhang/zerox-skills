"""关联自然人不能被当作企业经营数字主体。"""
import copy
import json
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(os.environ.get("zerox_dd_root", Path(__file__).resolve().parents[3] / "zerox-due-diligence"))
sys.path.insert(0, str(ROOT / "scripts"))
from common import InputError, csv_text, load_json
from check_report import check
from report_model import validate_content
import test_reader_report as fixtures


class PersonReportingTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ReaderReportTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.person = copy.deepcopy(self.fixture.data["entity-map"][0])
        self.person.update(entity_id="ENT-0099", entity_type="person", legal_name="示例商标权利人",
                           registration_id=None, listing_status="unlisted")
        self.fixture.data["entity-map"].append(self.person)

    def test_person_cannot_be_chart_business_entity(self):
        content = copy.deepcopy(self.fixture.content)
        content["sections"][0]["blocks"][0]["entity_id"] = "ENT-0099"
        with self.assertRaisesRegex(InputError, "自然人"):
            validate_content(content, self.fixture.cfg, self.fixture.data)

    def test_project_financial_input_rejects_person_but_accepts_company(self):
        project = self.fixture.project
        (project / "entity-map.csv").write_text(csv_text("entity-map", self.fixture.data["entity-map"]))
        financial = load_json(ROOT / "templates/financial-input.json")
        financial.update(entity_id="ENT-0001", scope="standalone", period_start="2025-01-01",
                         period_end="2025-12-31", days=365, currency="CNY", unit="万元",
                         accounting_basis="合成测试口径", source_ids=["S-0001"],
                         values={"revenue": 10}, input_evidence={"revenue": ["E-0001"]})
        path = project / "financial-input.json"
        path.write_text(json.dumps(financial))
        self.assertEqual(check(project)["errors"], [])
        financial["entity_id"] = "ENT-0099"
        path.write_text(json.dumps(financial))
        self.assertTrue(any("财务输入主体" in error for error in check(project)["errors"]))


if __name__ == "__main__":
    unittest.main()
