#!/usr/bin/env python3
"""Fail-closed HTML to PNG capture for zerox-onepager."""

import argparse
import asyncio
import os
import struct
import sys
import tempfile
from pathlib import Path
from typing import Optional, Tuple


def parse_height(value: str) -> Optional[int]:
    if value.lower() == "auto":
        return None
    try:
        height = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("height must be a positive integer or 'auto'") from error
    if height <= 0:
        raise argparse.ArgumentTypeError("height must be greater than zero")
    return height


def positive_int(value: str) -> int:
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("value must be greater than zero")
    return number


def positive_float(value: str) -> float:
    number = float(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("value must be greater than zero")
    return number


def read_png_dimensions(path: Path) -> Tuple[int, int]:
    with path.open("rb") as file:
        header = file.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"Output is not a valid PNG: {path}")
    return struct.unpack(">II", header[16:24])


async def capture(
    input_path: Path,
    output_path: Path,
    width: int,
    height: Optional[int],
    scale: float,
    timeout: int,
) -> Tuple[int, int]:
    source = Path(input_path).resolve()
    destination = Path(output_path).resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Input file not found: {source}")

    try:
        from playwright.async_api import async_playwright
    except ImportError as error:
        raise RuntimeError(
            "Playwright is not installed. Run: bash scripts/install_deps.sh"
        ) from error

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Optional[Path] = None
    page_height = height or 800

    try:
        with tempfile.NamedTemporaryFile(
            prefix=f".{destination.stem}-",
            suffix=".png",
            dir=destination.parent,
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page(
                viewport={"width": width, "height": page_height},
                device_scale_factor=scale,
            )
            failed_requests = []
            page_errors = []
            page.on("requestfailed", lambda request: failed_requests.append(request.url))
            page.on("pageerror", lambda error: page_errors.append(str(error)))

            await page.goto(source.as_uri(), wait_until="domcontentloaded", timeout=timeout)
            await page.wait_for_function(
                "document.fonts ? document.fonts.status === 'loaded' : true",
                timeout=timeout,
            )
            await page.wait_for_timeout(250)

            if page_errors:
                raise RuntimeError(f"Page JavaScript error: {page_errors[0]}")

            if height is None:
                actual_height = int(await page.evaluate("document.documentElement.scrollHeight"))
                if actual_height <= 0:
                    raise RuntimeError("Rendered page has no measurable height")
                await page.screenshot(path=str(temporary_path), full_page=True, type="png")
            else:
                actual_height = height
                await page.screenshot(
                    path=str(temporary_path),
                    full_page=False,
                    clip={"x": 0, "y": 0, "width": width, "height": height},
                    type="png",
                )
            await browser.close()

            if failed_requests:
                print(
                    f"WARN: {len(failed_requests)} resource request(s) failed; "
                    "system font fallback may have been used.",
                    file=sys.stderr,
                )

        png_width, png_height = read_png_dimensions(temporary_path)
        expected_width = round(width * scale)
        expected_height = round(actual_height * scale)
        if (png_width, png_height) != (expected_width, expected_height):
            raise RuntimeError(
                "PNG dimensions do not match the requested viewport and scale: "
                f"got {png_width}x{png_height}, expected {expected_width}x{expected_height}"
            )

        os.replace(temporary_path, destination)
        temporary_path = None
        return png_width, png_height
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Capture HTML as a validated PNG image")
    parser.add_argument("input", type=Path, help="Path to input HTML")
    parser.add_argument("--output", "-o", type=Path, required=True, help="Path to output PNG")
    parser.add_argument("--width", "-w", type=positive_int, required=True, help="CSS viewport width")
    parser.add_argument(
        "--height",
        type=parse_height,
        default=None,
        help="CSS viewport height, or 'auto' (default)",
    )
    parser.add_argument("--scale", "-s", type=positive_float, default=2.0)
    parser.add_argument("--timeout", "-t", type=positive_int, default=30000)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        png_width, png_height = asyncio.run(
            capture(args.input, args.output, args.width, args.height, args.scale, args.timeout)
        )
    except (OSError, RuntimeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)

    print(f"OK: Screenshot saved to {args.output}")
    print(f"    PNG dimensions: {png_width}px x {png_height}px")
    print(f"    CSS viewport: {args.width}px x {args.height or 'auto'} (scale: {args.scale}x)")


if __name__ == "__main__":
    main()
