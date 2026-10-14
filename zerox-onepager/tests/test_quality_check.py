import tempfile
import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import quality_check


class QualityCheckTests(unittest.TestCase):
    def run_html(self, html, style="B2", size="A1", no_bignum=False):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.html"
            path.write_text(html, encoding="utf-8")
            return quality_check.run_checks(path, style, size, no_bignum)

    @staticmethod
    def document(style, body=None):
        body = body or (
            '<h1>Title</h1><div class="bignum-item">42</div>'
            '<footer>Footer</footer>'
        )
        return (
            '<!doctype html><html><head><meta charset="UTF-8">'
            f"<style>{style}</style></head><body>{body}</body></html>"
        )

    def test_nominal_non_b9_can_pass_without_warnings(self):
        html = self.document(
            "body{color:#111;background:#fff}"
            ".bignum-value{color:#dc2626}"
        )
        errors, warnings, _ = self.run_html(html)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_style_tag_does_not_claim_web_font_import(self):
        checker = quality_check.HTMLChecker()
        checker.feed(self.document("body{color:#111;background:#fff}"))
        self.assertFalse(checker.has_font_import)

    def test_semantic_footer_is_detected(self):
        checker = quality_check.HTMLChecker()
        checker.feed(self.document(""))
        self.assertTrue(checker.has_footer)

    def test_bignum_requires_exact_contract_prefix(self):
        body = '<h1>Title</h1><div class="not-bignum">42</div><footer>Footer</footer>'
        errors, _, _ = self.run_html(
            self.document("body{color:#111;background:#fff}", body)
        )
        self.assertTrue(any("[BIGNUMBER]" in error for error in errors))

    def test_inline_colors_are_analyzed(self):
        body = (
            '<h1>Title</h1><div class="bignum-item" style="color:#6366f1">42</div>'
            "<footer>Footer</footer>"
        )
        _, warnings, _ = self.run_html(
            self.document("body{color:#111;background:#fff}", body)
        )
        self.assertTrue(any("blue/purple" in warning for warning in warnings))

    def test_copyright_symbol_is_not_emoji(self):
        body = '<h1>Title</h1><div class="bignum-item">42</div><footer>© 2026</footer>'
        errors, _, _ = self.run_html(
            self.document("body{color:#111;background:#fff}", body)
        )
        self.assertFalse(any("[EMOJI]" in error for error in errors))

    def test_actual_emoji_is_error(self):
        body = '<h1>Title</h1><div class="bignum-item">42</div><footer>🚀</footer>'
        errors, _, _ = self.run_html(
            self.document("body{color:#111;background:#fff}", body)
        )
        self.assertTrue(any("[EMOJI]" in error for error in errors))

    def test_rgb_with_whitespace_is_parsed(self):
        self.assertEqual(quality_check.parse_color("rgb( 99, 102, 241)"), (99, 102, 241))

    def test_css_variables_are_resolved_for_contrast(self):
        html = self.document(
            ":root{--fg:#777;--bg:#888}"
            "body{color:var(--fg);background:var(--bg)}"
        )
        errors, _, _ = self.run_html(html)
        self.assertTrue(any("[CONTRAST]" in error for error in errors))

    def test_each_page_level_grid_is_checked(self):
        html = self.document(
            "body{color:#111;background:#fff}"
            ".main-grid{display:grid;grid-template-rows:1fr}"
            ".main-bad{display:grid}"
        )
        errors, _, _ = self.run_html(html, size="A2")
        self.assertTrue(any(".main-bad" in error for error in errors))

    def test_css_absolute_position_is_reported(self):
        html = self.document(
            "body{color:#111;background:#fff}"
            ".content-card{position:absolute}"
        )
        _, warnings, _ = self.run_html(html, size="A2")
        self.assertTrue(any("Absolute positioning" in warning for warning in warnings))

    def test_blue_purple_gradient_is_error(self):
        html = self.document(
            "body{color:#111;background:#fff}"
            ".hero{background:linear-gradient(135deg,#6366f1,#a855f7)}"
        )
        errors, _, _ = self.run_html(html)
        self.assertTrue(any("[GRADIENT]" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
