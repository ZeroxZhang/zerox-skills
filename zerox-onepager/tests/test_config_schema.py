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
        self.assertEqual(set(self.config["styles"]), {f"B{index}" for index in range(1, 12)})
        self.assertEqual(set(self.config["densities"]), {"C1", "C2", "C3"})
        self.assertEqual(set(self.config["types"]), {"T1", "T2", "T3", "T4"})
        self.assertEqual(set(self.config["scenes"]), {f"S{index}" for index in range(1, 7)})
        self.assertEqual(set(self.config["fonts"]["options"]), {f"G{index}" for index in range(1, 8)})

    def test_scene_defaults_reference_known_options(self):
        for key, scene in self.config["scenes"].items():
            defaults = scene["defaults"]
            self.assertIn(defaults["A"], self.config["sizes"], key)
            self.assertIn(defaults["B"], self.config["styles"], key)
            self.assertIn(defaults["C"], self.config["densities"], key)
            self.assertIn(defaults["T"], self.config["types"], key)
            self.assertIn(defaults["E"], self.config["bignumber"], key)
            focus = defaults.get("focus")
            if focus:
                self.assertIn(focus, self.config["types"][defaults["T"]]["focus"], key)
            for required in ("one_liner", "must_have", "avoid", "success"):
                self.assertTrue(scene.get(required), f"{key} missing {required}")

    def test_b10_modes_and_t4_rule(self):
        b10 = self.config["styles"]["B10"]
        self.assertEqual(b10["modes"], ["Dark", "Paper"])
        self.assertEqual(b10["default_mode"], "Dark")
        self.assertEqual(b10["mode_rules"]["T4"], "Dark")

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
        order = self.config["interaction_order"]
        self.assertEqual(order, ["S", "A", "B", "C", "T", "E", "G", "F"])
        self.assertEqual(order[0], "S", "scene must be the first decision")
        for dimension in ("A", "B", "C", "T", "E", "F"):
            self.assertIn(dimension, order, "the original A/B/C/T/E/F protocol is retained")
        self.assertEqual(self.config["signature"]["key"], "F")
        self.assertEqual(self.config["fonts"]["key"], "G")

    def test_font_contract(self):
        fonts = self.config["fonts"]
        self.assertEqual(fonts["default"], "G1")
        self.assertEqual(fonts["max_families"], 2)
        self.assertEqual(fonts["max_weights"], 3)
        self.assertTrue(fonts["fallback_required"])


if __name__ == "__main__":
    unittest.main()
