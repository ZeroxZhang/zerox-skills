import asyncio
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import layout_check


def block(top, bottom, content_top=None, content_bottom=None, filled=False):
    content_top = top if content_top is None else content_top
    content_bottom = bottom if content_bottom is None else content_bottom
    return {
        "tag": "div",
        "className": "b",
        "top": top,
        "bottom": bottom,
        "height": bottom - top,
        "contentTop": content_top,
        "contentBottom": content_bottom,
        "filledBg": filled,
    }


TARGETS = {
    "max_gap_ratio": 1.8,
    "max_gap_ratio_hard": 2.4,
    "min_gap_px": 72,
    "max_type_scale": 12,
    "max_type_scale_hard": 15,
    "max_distinct_sizes": 6,
    "max_imbalance": 0.05,
    "air_ratio": [0.22, 0.38],
}


def measure(blocks, sizes, width=1080, height=1440, ink=None):
    return {
        "canvas": {"width": width, "height": height},
        "blocks": blocks,
        "fontSizes": sizes,
        "ink": ink,
    }


class SummarizeTests(unittest.TestCase):
    def test_air_ratio_and_gaps(self):
        blocks = [block(0, 400), block(460, 900), block(960, 1400)]
        metrics = layout_check.summarize(measure(blocks, [16]))
        self.assertEqual(metrics["blocks"], 3)
        self.assertEqual(metrics["inner_gaps"], [60, 60])
        self.assertEqual(metrics["median_gap"], 60)
        expected_air = 1 - (400 + 440 + 440) / 1440
        self.assertAlmostEqual(metrics["air_ratio"], round(expected_air, 3), places=3)

    def test_filled_background_counts_as_ink(self):
        empty = [block(0, 200, 0, 80), block(600, 800, 600, 660)]
        filled = [block(0, 200, 0, 80), block(600, 800, 600, 660, filled=True)]
        plain = layout_check.summarize(measure(empty, [16]))
        band = layout_check.summarize(measure(filled, [16]))
        self.assertGreater(plain["air_ratio"], band["air_ratio"])

    def test_void_detection(self):
        packed = [block(0, 400, content_top=0, content_bottom=120), block(460, 800)]
        metrics = layout_check.summarize(measure(packed, [16]))
        self.assertEqual(len(metrics["voids"]), 1)
        self.assertEqual(metrics["voids"][0]["fill"], 0.3)

    def test_side_by_side_columns_share_the_same_vertical_space(self):
        blocks = [block(0, 600), block(0, 200), block(650, 1000)]
        metrics = layout_check.summarize(measure(blocks, [16], height=1000))
        self.assertEqual(metrics["air_ratio"], 0.05)
        self.assertEqual(metrics["inner_gaps"], [0, 50])

    def test_type_scale_and_imbalance(self):
        metrics = layout_check.summarize(
            measure([block(0, 1400)], [13, 144], ink={"min": 0, "max": 1080})
        )
        self.assertEqual(metrics["scale"], 11.1)
        self.assertEqual(metrics["imbalance"], 0.0)


class SvgLayoutTests(unittest.TestCase):
    def test_svg_paths_fill_drawing_bounds_without_counting_viewport_margins(self):
        from test_render_check import browser_available

        if not browser_available():
            self.skipTest("Playwright Chromium is not installed")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "drawing.html"
            path.write_text(
                '<style>*{margin:0}svg{display:block}</style><main class="poster">'
                '<figure><svg width="800" height="400" viewBox="0 0 400 200">'
                '<defs><text x="2000" y="2000" font-size="500">mask</text>'
                '<text id="headline" x="32" y="120" font-size="36">Page</text>'
                '<g id="nested" transform="scale(.5)"><use href="#headline"/><use href="#nested"/></g></defs>'
                '<use href="#headline"/><use href="#nested"/>'
                '<path d="M30 15h320v130H30z"/></svg><figcaption>Paper</figcaption>'
                '</figure></main>', encoding="utf-8"
            )
            result = asyncio.run(layout_check.measure(path, "A4"))
        self.assertEqual(result["blocks"][0]["contentTop"], 30)
        self.assertEqual(result["fontSizes"], [16, 36, 72])
        self.assertEqual(result["blocks"][0]["contentBottom"], result["blocks"][0]["height"])

    def test_lettering_template_uses_the_displayed_viewbox_scale(self):
        from test_render_check import browser_available

        if not browser_available():
            self.skipTest("Playwright Chromium is not installed")
        drawing = (ROOT / "assets/templates/lettering.svg").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "lettering.html"
            path.write_text(
                '<style>svg{width:320px;display:block}</style><main class="poster">'
                + drawing + '</main>', encoding="utf-8"
            )
            measured = asyncio.run(layout_check.measure(path, "A4"))
        self.assertEqual(measured["fontSizes"], [84])


class ClassifyTests(unittest.TestCase):
    def run_classify(self, metrics):
        return layout_check.classify(metrics, TARGETS)

    def test_hole_is_error(self):
        blocks = [block(0, 300), block(340, 600), block(1300, 1400)]
        errors, _, _ = self.run_classify(layout_check.summarize(measure(blocks, [16])))
        self.assertTrue(any("[LAYOUT] Hole" in error for error in errors))

    def test_uniform_gaps_pass(self):
        blocks = [block(0, 300), block(360, 660), block(720, 1020), block(1080, 1400)]
        errors, warnings, _ = self.run_classify(
            layout_check.summarize(measure(blocks, [16]))
        )
        self.assertEqual([e for e in errors if "Hole" in e], [])
        self.assertEqual([w for w in warnings if "Gap of" in w], [])

    def test_excess_air_is_error(self):
        blocks = [block(0, 300), block(1100, 1400)]
        errors, _, _ = self.run_classify(layout_check.summarize(measure(blocks, [16])))
        self.assertTrue(any("Air covers" in error for error in errors))

    def test_type_cliff_is_error(self):
        blocks = [block(0, 1400)]
        errors, _, _ = self.run_classify(
            layout_check.summarize(measure(blocks, [11, 200]))
        )
        self.assertTrue(any("Type scale is" in error for error in errors))

    def test_too_many_sizes_warn(self):
        blocks = [block(0, 1400)]
        _, warnings, _ = self.run_classify(
            layout_check.summarize(measure(blocks, [11, 13, 15, 17, 22, 38, 96]))
        )
        self.assertTrue(any("distinct font sizes" in warning for warning in warnings))


if __name__ == "__main__":
    unittest.main()
