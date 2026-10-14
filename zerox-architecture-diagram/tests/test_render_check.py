from __future__ import annotations

from pathlib import Path
import unittest

from scripts.render_check import find_chrome, run_probe


ROOT = Path(__file__).resolve().parents[1]


class RenderedLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        try:
            cls.chrome = find_chrome(None)
        except RuntimeError as exc:
            raise unittest.SkipTest(str(exc))

    def test_standard_template_has_no_rendered_collision(self) -> None:
        report = run_probe(ROOT / "assets" / "template.html", self.chrome, 1440, 900)
        self.assertEqual([], report["issues"])

    def test_presentation_template_has_no_rendered_collision(self) -> None:
        report = run_probe(ROOT / "assets" / "template-presentation.html", self.chrome, 1280, 720)
        self.assertEqual([], report["issues"])


if __name__ == "__main__":
    unittest.main()
