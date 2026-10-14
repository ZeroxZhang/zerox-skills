#!/usr/bin/env python3
"""Browser-backed geometry checks for generated zerox-onepager HTML."""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import List, Optional, Tuple

CONFIG_PATH = Path(__file__).resolve().parents[1] / "references" / "config-schema.json"


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


async def inspect_render(
    html_path: Path,
    size: str,
    timeout: int = 30000,
) -> Tuple[List[str], List[str], List[str]]:
    path = Path(html_path).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    if timeout <= 0:
        raise ValueError("timeout must be greater than zero")

    try:
        from playwright.async_api import async_playwright
    except ImportError as error:
        raise RuntimeError(
            "Playwright is not installed. Run: bash scripts/install_deps.sh"
        ) from error

    config = load_config()
    size_config = config["sizes"][size]
    expected_width = int(size_config["width"])
    expected_height: Optional[int] = (
        None if size_config["height"] == "auto" else int(size_config["height"])
    )

    errors: List[str] = []
    warnings: List[str] = []
    passed: List[str] = []
    failed_requests: List[str] = []
    page_errors: List[str] = []

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page(
            viewport={"width": expected_width, "height": expected_height or 800},
            device_scale_factor=1,
        )
        page.on("requestfailed", lambda request: failed_requests.append(request.url))
        page.on("pageerror", lambda error: page_errors.append(str(error)))

        await page.goto(path.as_uri(), wait_until="domcontentloaded", timeout=timeout)
        try:
            await page.wait_for_function(
                "document.fonts ? document.fonts.status === 'loaded' : true",
                timeout=timeout,
            )
        except Exception as error:
            errors.append(f"[FONT] Fonts did not reach loaded state: {error}")

        metrics = await page.evaluate(
            """() => {
                const root = document.querySelector('.page') || document.body;
                const rootRect = root.getBoundingClientRect();
                const candidates = [...root.querySelectorAll('*')].filter((element) => {
                    const style = getComputedStyle(element);
                    const rect = element.getBoundingClientRect();
                    if (style.display === 'none' || style.visibility === 'hidden') return false;
                    if (rect.width === 0 || rect.height === 0) return false;
                    if (['STYLE', 'SCRIPT', 'SYMBOL', 'DEFS'].includes(element.tagName)) return false;
                    return true;
                });

                const textOverflow = candidates.filter((element) => {
                    if (!(element.textContent || '').trim()) return false;
                    if ([...element.children].some((child) => (child.textContent || '').trim())) return false;
                    const style = getComputedStyle(element);
                    const clipsX = ['hidden', 'clip'].includes(style.overflowX);
                    const clipsY = ['hidden', 'clip'].includes(style.overflowY);
                    return (clipsX && element.scrollWidth > element.clientWidth + 1) ||
                           (clipsY && element.scrollHeight > element.clientHeight + 1);
                }).map((element) => ({
                    tag: element.tagName.toLowerCase(),
                    className: typeof element.className === 'string' ? element.className : '',
                    text: (element.textContent || '').trim().slice(0, 40)
                }));

                const outOfBounds = candidates.filter((element) => {
                    const style = getComputedStyle(element);
                    if (style.position === 'absolute' || style.position === 'fixed') return false;
                    if (!(element.textContent || '').trim()) return false;
                    const rect = element.getBoundingClientRect();
                    return rect.left < rootRect.left - 1 ||
                           rect.right > rootRect.right + 1 ||
                           rect.top < rootRect.top - 1 ||
                           rect.bottom > rootRect.bottom + 1;
                }).map((element) => ({
                    tag: element.tagName.toLowerCase(),
                    className: typeof element.className === 'string' ? element.className : '',
                    text: (element.textContent || '').trim().slice(0, 40)
                }));

                return {
                    rootWidth: rootRect.width,
                    rootHeight: rootRect.height,
                    documentWidth: document.documentElement.scrollWidth,
                    documentHeight: document.documentElement.scrollHeight,
                    textOverflow,
                    outOfBounds
                };
            }"""
        )
        await browser.close()

    if abs(metrics["rootWidth"] - expected_width) > 1:
        errors.append(
            f"[CANVAS] Root width is {metrics['rootWidth']}px; expected {expected_width}px"
        )
    else:
        passed.append(f"[CANVAS] Root width matches {expected_width}px")

    if expected_height is not None:
        if abs(metrics["rootHeight"] - expected_height) > 1:
            errors.append(
                f"[CANVAS] Root height is {metrics['rootHeight']}px; expected {expected_height}px"
            )
        else:
            passed.append(f"[CANVAS] Root height matches {expected_height}px")
        if metrics["documentWidth"] > expected_width + 1 or metrics["documentHeight"] > expected_height + 1:
            errors.append(
                "[CANVAS] Fixed canvas produces document scroll overflow: "
                f"{metrics['documentWidth']}x{metrics['documentHeight']}"
            )
        else:
            passed.append("[CANVAS] Fixed canvas has no document scroll overflow")
    elif metrics["rootHeight"] <= 0:
        errors.append("[CANVAS] Auto-height canvas has no measurable height")
    else:
        passed.append(f"[CANVAS] Auto-height canvas is {metrics['rootHeight']}px tall")

    if metrics["textOverflow"]:
        examples = ", ".join(
            f"{item['tag']}.{item['className']}" for item in metrics["textOverflow"][:5]
        )
        errors.append(f"[OVERFLOW] Text is clipped in {len(metrics['textOverflow'])} element(s): {examples}")
    else:
        passed.append("[OVERFLOW] No text clipping detected")

    if metrics["outOfBounds"]:
        examples = ", ".join(
            f"{item['tag']}.{item['className']}" for item in metrics["outOfBounds"][:5]
        )
        errors.append(
            f"[BOUNDARY] {len(metrics['outOfBounds'])} normal-flow element(s) exceed the canvas: {examples}"
        )
    else:
        passed.append("[BOUNDARY] Normal-flow content stays inside the canvas")

    if page_errors:
        errors.append(f"[PAGE] JavaScript errors: {'; '.join(page_errors[:3])}")
    else:
        passed.append("[PAGE] No JavaScript page errors")

    if failed_requests:
        warnings.append(
            f"[NETWORK] {len(failed_requests)} resource request(s) failed; system font fallback may be active"
        )
    else:
        passed.append("[NETWORK] No failed resource requests")

    return errors, warnings, passed


def print_report(
    path: Path,
    size: str,
    errors: List[str],
    warnings: List[str],
    passed: List[str],
    output_format: str,
) -> None:
    verdict = "FAIL" if errors else "WARN" if warnings else "PASS"
    if output_format == "json":
        print(json.dumps(
            {
                "file": str(path),
                "size": size,
                "verdict": verdict,
                "errors": errors,
                "warnings": warnings,
                "passed": passed,
            },
            ensure_ascii=False,
            indent=2,
        ))
        return

    print("=" * 60)
    print("ZEROX-ONEPAGER RENDER QUALITY CHECK")
    print(f"File: {path}")
    print(f"Size: {size}")
    print("=" * 60)
    for heading, values, marker in (
        ("ERRORS", errors, "X"),
        ("WARNINGS", warnings, "!"),
        ("PASSED", passed, "OK"),
    ):
        if not values and heading != "PASSED":
            continue
        print(f"\n{heading} ({len(values)})")
        for value in values:
            print(f"  [{marker}] {value}")
    print(f"\nVERDICT: {verdict}")


def main() -> None:
    config = load_config()
    parser = argparse.ArgumentParser(description="Rendered geometry check for zerox-onepager HTML")
    parser.add_argument("input", type=Path)
    parser.add_argument("--size", required=True, choices=sorted(config["sizes"]))
    parser.add_argument("--timeout", type=int, default=30000)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()

    try:
        errors, warnings, passed = asyncio.run(inspect_render(args.input, args.size, args.timeout))
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)

    print_report(args.input, args.size, errors, warnings, passed, args.format)
    raise SystemExit(2 if errors else 1 if warnings else 0)


if __name__ == "__main__":
    main()
