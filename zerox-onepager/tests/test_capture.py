import argparse
import asyncio
import os
import struct
import tempfile
import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import capture


def browser_available():
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            return os.path.isfile(playwright.chromium.executable_path)
    except Exception:
        return False


class CaptureUnitTests(unittest.TestCase):
    def test_parse_auto_height(self):
        self.assertIsNone(capture.parse_height("auto"))

    def test_parse_positive_height(self):
        self.assertEqual(capture.parse_height("1080"), 1080)

    def test_reject_non_positive_dimensions(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            capture.parse_height("0")
        with self.assertRaises(argparse.ArgumentTypeError):
            capture.positive_int("-1")
        with self.assertRaises(argparse.ArgumentTypeError):
            capture.positive_float("0")

    def test_read_png_dimensions(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.png"
            path.write_bytes(
                b"\x89PNG\r\n\x1a\n"
                + struct.pack(">I", 13)
                + b"IHDR"
                + struct.pack(">II", 2160, 2880)
            )
            self.assertEqual(capture.read_png_dimensions(path), (2160, 2880))

    def test_reject_invalid_png(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.png"
            path.write_bytes(b"not a png")
            with self.assertRaises(ValueError):
                capture.read_png_dimensions(path)


@unittest.skipUnless(browser_available(), "Playwright Chromium is not installed")
class CaptureIntegrationTests(unittest.TestCase):
    def test_auto_height_and_space_in_path(self):
        with tempfile.TemporaryDirectory(prefix="onepager capture ") as directory:
            source = Path(directory) / "input page.html"
            output = Path(directory) / "output image.png"
            source.write_text(
                "<!doctype html><html><head><meta charset='UTF-8'>"
                "<style>html,body{margin:0}.page{width:800px;min-height:1200px}</style>"
                "</head><body><main class='page'><h1>Auto height</h1></main></body></html>",
                encoding="utf-8",
            )
            dimensions = asyncio.run(capture.capture(source, output, 800, None, 1, 10000))
            self.assertEqual(dimensions[0], 800)
            self.assertGreaterEqual(dimensions[1], 1200)
            self.assertEqual(capture.read_png_dimensions(output), dimensions)


if __name__ == "__main__":
    unittest.main()
