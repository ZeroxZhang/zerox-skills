import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ConfigSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads(
            (ROOT / "references" / "config-schema.json").read_text(encoding="utf-8")
        )

    def test_public_option_sets(self):
        self.assertEqual(set(self.config["sizes"]), {"A1", "A2", "A3", "A4"})
        self.assertEqual(set(self.config["styles"]), {f"B{index}" for index in range(1, 10)})
        self.assertEqual(set(self.config["densities"]), {"C1", "C2", "C3"})
        self.assertEqual(set(self.config["types"]), {"T1", "T2", "T3", "T4"})

    def test_fixed_height_contract(self):
        self.assertFalse(self.config["sizes"]["A1"]["fixed_height"])
        for size in ("A2", "A3", "A4"):
            self.assertTrue(self.config["sizes"][size]["fixed_height"])

    def test_t4_forces_b9_poster_mode(self):
        b9 = self.config["styles"]["B9"]
        self.assertIn("Poster", b9["modes"])
        self.assertEqual(b9["mode_rules"]["T4"], "Poster")

    def test_missing_verified_data_falls_back_to_e2(self):
        self.assertEqual(
            self.config["bignumber"]["missing_verified_data_fallback"],
            "E2",
        )

    def test_interaction_protocol_keeps_all_dimensions(self):
        self.assertEqual(
            self.config["interaction_order"],
            ["A", "B", "C", "T", "E", "F"],
        )
        self.assertEqual(self.config["signature"]["key"], "F")


if __name__ == "__main__":
    unittest.main()
