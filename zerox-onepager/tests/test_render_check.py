import asyncio
import os
import tempfile
import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import render_check


def browser_available():
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            return os.path.isfile(playwright.chromium.executable_path)
    except (ImportError, Exception):
        return False


@unittest.skipUnless(browser_available(), "Playwright Chromium is not installed")
class RenderCheckIntegrationTests(unittest.TestCase):
    def run_fixture(self, body):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.html"
            path.write_text(
                "<!doctype html><html><head><meta charset='UTF-8'>"
                "<style>*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;"
                "overflow:hidden}.page{width:1080px;height:1440px;overflow:hidden}</style>"
                f"</head><body><main class='page'>{body}</main></body></html>",
                encoding="utf-8",
            )
            return asyncio.run(render_check.inspect_render(path, "A4", 10000))

    def test_clean_fixed_canvas(self):
        errors, warnings, _ = self.run_fixture("<h1>Clean page</h1><p>Readable text</p>")
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_text_clipping_is_error(self):
        errors, _, _ = self.run_fixture(
            "<h1>Page</h1><div style='width:20px;height:10px;overflow:hidden;"
            "white-space:nowrap'>This text is intentionally clipped</div>"
        )
        self.assertTrue(any("[OVERFLOW]" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
