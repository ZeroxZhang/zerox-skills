#!/usr/bin/env python3
"""Composition-level layout checks for generated zerox-onepager HTML.

quality_check.py validates source-level invariants and render_check.py
validates geometry (size, clipping, overflow). Neither can tell you that a page
is *badly composed*: content packed at the top of each band, one huge hole
between two blocks, or a type scale so wide it reads as a document.

This checker measures the rendered composition and reports:

* [LAYOUT] hole   - one gap clearly larger than the rhythm of the page
* [LAYOUT] void   - a block whose content fills less than half its own box
* [LAYOUT] air    - vertical space not covered by content extents or filled bands
* [TYPO] scale    - too many distinct sizes, or an extreme max:min ratio
* [BALANCE] mass  - the ink is visibly off-centre horizontally

Exit codes:
    0 = PASS
    1 = WARN
    2 = FAIL
"""

import argparse
import asyncio
import json
import statistics
import sys
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

CONFIG_PATH = Path(__file__).resolve().parents[1] / "references" / "config-schema.json"

BLOCK_SELECTOR = ".poster, .page, .canvas, .onepager"

MEASURE_JS = """
() => {
  const root = document.querySelector(%s) || document.body;

  const isVisible = (element) => {
    const style = getComputedStyle(element);
    if (style.display === 'none' || style.visibility === 'hidden') return false;
    if (parseFloat(style.opacity || '1') === 0) return false;
    const rect = element.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0;
  };

  const isFlow = (element) => {
    const position = getComputedStyle(element).position;
    return position !== 'absolute' && position !== 'fixed';
  };

  const media = new Set(['img', 'svg', 'hr', 'canvas', 'video', 'picture']);
  const hasOwnText = (element) => [...element.childNodes].some(
    (node) => node.nodeType === Node.TEXT_NODE && node.textContent.trim()
  );

  // The SVG viewport may contain a large unpainted margin. Map the drawing's
  // bounds (in viewBox units) into CSS pixels, respecting letterboxing and
  // transforms. As with other DOM bounds this is an extent, not pixel coverage.
  const mediaBounds = (element) => {
    const viewport = element.getBoundingClientRect();
    if (!(element instanceof SVGSVGElement)) return viewport;

    const box = element.getBBox();
    const matrix = element.getScreenCTM();
    if (!matrix || (!box.width && !box.height)) return null;
    const points = [
      new DOMPoint(box.x, box.y),
      new DOMPoint(box.x + box.width, box.y),
      new DOMPoint(box.x, box.y + box.height),
      new DOMPoint(box.x + box.width, box.y + box.height)
    ].map((point) => point.matrixTransform(matrix));
    const bounds = {
      left: Math.min(...points.map((p) => p.x)),
      right: Math.max(...points.map((p) => p.x)),
      top: Math.min(...points.map((p) => p.y)),
      bottom: Math.max(...points.map((p) => p.y))
    };
    const style = getComputedStyle(element);
    if (style.overflowX !== 'visible') {
      bounds.left = Math.max(viewport.left, bounds.left);
      bounds.right = Math.min(viewport.right, bounds.right);
    }
    if (style.overflowY !== 'visible') {
      bounds.top = Math.max(viewport.top, bounds.top);
      bounds.bottom = Math.min(viewport.bottom, bounds.bottom);
    }
    return bounds.left <= bounds.right && bounds.top <= bounds.bottom ? bounds : null;
  };

  // Measure text and graphics within a normal-flow band. SVG paths, masks
  // and glyph definitions are parts of one picture, not independent blocks.
  const contentExtent = (block) => {
    const rect = block.getBoundingClientRect();
    const bounds = [];
    const walk = (element) => {
      if (media.has(element.localName)) {
        const painted = mediaBounds(element);
        if (painted) bounds.push(painted);
        return;
      }
      if (hasOwnText(element)) bounds.push(element.getBoundingClientRect());
      for (const child of element.children) {
        if (isVisible(child) && (isFlow(child) || child instanceof SVGSVGElement)) walk(child);
      }
    };
    walk(block);
    if (!bounds.length) {
      // CSS-only illustrations have no text/media leaves.
      const hasSvg = block instanceof SVGSVGElement || block.querySelector('svg');
      return { top: rect.top, bottom: hasSvg ? rect.top : rect.bottom };
    }
    return {
      top: Math.max(rect.top, Math.min(...bounds.map((b) => b.top))),
      bottom: Math.min(rect.bottom, Math.max(...bounds.map((b) => b.bottom)))
    };
  };

  const rootRect = root.getBoundingClientRect();
  const rootBg = getComputedStyle(root).backgroundColor;
  const blocks = Array.from(root.children)
    .filter((element) => isVisible(element) && isFlow(element))
    .map((element) => {
      const rect = element.getBoundingClientRect();
      const extent = contentExtent(element);
      return {
        tag: element.tagName.toLowerCase(),
        className: typeof element.className === 'string' ? element.className : '',
        top: rect.top - rootRect.top,
        bottom: rect.bottom - rootRect.top,
        height: rect.height,
        contentTop: extent.top - rootRect.top,
        contentBottom: extent.bottom - rootRect.top,
        // A block painted with its own background is ink, not air: a full-bleed
        // colour band fills space by definition.
        filledBg: (() => {
          const bg = getComputedStyle(element).backgroundColor;
          return bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent' && bg !== rootBg;
        })()
      };
    })
    .sort((a, b) => a.top - b.top);

  const sizes = new Set();
  const inkLeft = [];
  const inkRight = [];
  const svgTextNames = ['text', 'tspan', 'textPath'];
  const addTypeSize = (element, matrix) => {
    const px = parseFloat(getComputedStyle(element).fontSize);
    const scale = matrix ? Math.hypot(matrix.c, matrix.d) : 1;
    sizes.add(Math.round(px * scale * 10) / 10);
  };

  // The instance tree of <use> is browser-private. Follow local references
  // through painted groups, composing their transforms with the viewport CTM.
  const visitInstance = (node, matrix, ancestors) => {
    if (!node || ancestors.has(node)) return;
    const tag = node.localName;
    if (tag !== 'g' && tag !== 'use' && !svgTextNames.includes(tag)) return;
    const style = getComputedStyle(node);
    if (style.display === 'none' || style.opacity === '0') return;
    if (style.transform !== 'none') matrix = matrix.multiply(new DOMMatrix(style.transform));
    if (svgTextNames.includes(tag) && hasOwnText(node) && style.visibility !== 'hidden') {
      addTypeSize(node, matrix);
    }
    ancestors.add(node);
    if (tag === 'use') {
      const ref = node.href.baseVal;
      if (ref.startsWith('#')) visitInstance(document.getElementById(ref.slice(1)), matrix, ancestors);
    } else {
      for (const child of node.children) visitInstance(child, matrix, ancestors);
    }
    ancestors.delete(node);
  };

  Array.from(root.querySelectorAll('*')).forEach((element) => {
    const isSvgChild = element instanceof SVGElement && !(element instanceof SVGSVGElement);
    const isUse = isSvgChild && element.localName === 'use';
    if (isSvgChild && !svgTextNames.includes(element.localName) && !isUse) return;
    if (isSvgChild && element.closest('defs, symbol, mask, clipPath, pattern, marker')) return;
    if (!isVisible(element)) return;
    if (isUse) {
      const href = element.href.baseVal;
      const matrix = element.getScreenCTM();
      if (matrix && href.startsWith('#')) {
        visitInstance(document.getElementById(href.slice(1)), DOMMatrix.fromMatrix(matrix), new Set());
      }
      return;
    }
    const text = hasOwnText(element);
    if (text) addTypeSize(element, isSvgChild ? element.getScreenCTM() : null);
    const measuredMedia = media.has(element.localName) && element.localName !== 'hr';
    if (!text && !measuredMedia) return;
    const rect = measuredMedia ? mediaBounds(element) : element.getBoundingClientRect();
    if (rect && rect.right > rect.left) {
      inkLeft.push(rect.left - rootRect.left);
      inkRight.push(rect.right - rootRect.left);
    }
  });

  return {
    canvas: { width: rootRect.width, height: rootRect.height },
    blocks: blocks,
    fontSizes: Array.from(sizes).sort((a, b) => a - b),
    ink: inkLeft.length
      ? { min: Math.min.apply(null, inkLeft), max: Math.max.apply(null, inkRight) }
      : null
  };
}
"""


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def summarize(measurement: Dict) -> Dict:
    """Turn raw DOM measurements into composition metrics."""
    canvas = measurement["canvas"]
    blocks = measurement["blocks"]
    canvas_height = float(canvas["height"]) or 1.0

    inner_gaps: List[float] = []
    if blocks:
        previous_bottom = blocks[0]["bottom"]
        for current in blocks[1:]:
            inner_gaps.append(max(0.0, current["top"] - previous_bottom))
            previous_bottom = max(previous_bottom, current["bottom"])

    # Side-by-side columns and overlapping layers can occupy the same rows.
    # Count each vertical interval once, as for a single-column composition.
    intervals = sorted(
        (block["top"], block["bottom"]) if block.get("filledBg")
        else (block["contentTop"], block["contentBottom"])
        for block in blocks
    )
    covered = 0.0
    last_bottom = 0.0
    for top, bottom in intervals:
        bottom = min(bottom, canvas_height)
        covered += max(0.0, bottom - max(top, last_bottom))
        last_bottom = max(last_bottom, bottom)
    air_ratio = 1.0 - covered / canvas_height

    voids = []
    for block in blocks:
        if block.get("filledBg"):
            continue
        extent = max(0.0, block["contentBottom"] - block["contentTop"])
        if block["height"] >= 110 and extent / block["height"] < 0.55:
            voids.append({
                "block": block["className"] or block["tag"],
                "height": round(block["height"]),
                "fill": round(extent / block["height"], 2),
            })

    sizes = [value for value in measurement.get("fontSizes", []) if value > 0]
    scale = (max(sizes) / min(sizes)) if len(sizes) >= 2 else 1.0

    ink = measurement.get("ink")
    imbalance = None
    if ink:
        center = (ink["min"] + ink["max"]) / 2
        width = float(canvas["width"]) or 1.0
        imbalance = abs(center - width / 2) / width

    # The largest gap must not define the rhythm it is measured against,
    # otherwise a single hole inflates the median and hides itself.
    rhythm_gap = 0.0
    if len(inner_gaps) >= 2:
        rhythm_gap = statistics.median(sorted(inner_gaps)[:-1])
    elif inner_gaps:
        rhythm_gap = inner_gaps[0]

    return {
        "canvas": canvas,
        "blocks": len(blocks),
        "inner_gaps": [round(gap, 1) for gap in inner_gaps],
        "median_gap": round(statistics.median(inner_gaps), 1) if inner_gaps else 0.0,
        "rhythm_gap": round(rhythm_gap, 1),
        "max_gap": round(max(inner_gaps), 1) if inner_gaps else 0.0,
        "air_ratio": round(air_ratio, 3),
        "voids": voids,
        "font_sizes": sizes,
        "scale": round(scale, 1),
        "imbalance": None if imbalance is None else round(imbalance, 3),
    }


def classify(metrics: Dict, targets: Dict) -> Tuple[List[str], List[str], List[str]]:
    """Compare metrics against the composition contract."""
    errors: List[str] = []
    warnings: List[str] = []
    passed: List[str] = []

    gap_ratio = float(targets.get("max_gap_ratio", 1.8))
    gap_hard = float(targets.get("max_gap_ratio_hard", 2.4))
    min_gap = float(targets.get("min_gap_px", 72))
    max_scale = float(targets.get("max_type_scale", 12))
    scale_hard = float(targets.get("max_type_scale_hard", 15))
    max_sizes = int(targets.get("max_distinct_sizes", 6))
    imbalance_limit = float(targets.get("max_imbalance", 0.05))

    median_gap = metrics.get("rhythm_gap") or metrics["median_gap"] or min_gap
    max_gap = metrics["max_gap"]
    if max_gap > max(min_gap, median_gap * gap_hard):
        errors.append(
            "[LAYOUT] Hole of %.0fpx between blocks; page rhythm is %.0fpx. "
            "Redistribute content instead of leaving a gap." % (max_gap, median_gap)
        )
    elif max_gap > max(min_gap, median_gap * gap_ratio):
        warnings.append(
            "[LAYOUT] Gap of %.0fpx is %.1fx the %.0fpx rhythm; "
            "confirm the asymmetry is intentional"
            % (max_gap, max_gap / (median_gap or 1), median_gap)
        )
    else:
        passed.append(
            "[LAYOUT] Gaps stay within rhythm (max %.0fpx, median %.0fpx)"
            % (max_gap, median_gap)
        )

    if metrics["voids"]:
        detail = ", ".join(
            "%s %dpx filled %d%%"
            % (item["block"], item["height"], int(item["fill"] * 100))
            for item in metrics["voids"][:3]
        )
        warnings.append("[LAYOUT] Content fills less than 55%% of its block: " + detail)
    else:
        passed.append("[LAYOUT] Every block is filled by its own content")

    low, high = targets.get("air_ratio", [0.22, 0.38])
    air = metrics["air_ratio"]
    if air > high:
        errors.append(
            "[LAYOUT] Air covers %.0f%% of the canvas; the target for this density is "
            "%.0f-%.0f%%. This is empty space, not whitespace."
            % (air * 100, low * 100, high * 100)
        )
    elif air < low:
        warnings.append(
            "[LAYOUT] Air covers %.0f%% of the canvas; target is %.0f-%.0f%%. "
            "The page may read as cramped." % (air * 100, low * 100, high * 100)
        )
    else:
        passed.append(
            "[LAYOUT] Air ratio %.0f%% is inside %.0f-%.0f%%"
            % (air * 100, low * 100, high * 100)
        )

    if metrics["scale"] > scale_hard:
        errors.append(
            "[TYPO] Type scale is %.1f:1 (%.0fpx to %.0fpx); cap is %.0f:1. "
            "A jump this wide reads as two different documents."
            % (
                metrics["scale"],
                max(metrics["font_sizes"]),
                min(metrics["font_sizes"]),
                scale_hard,
            )
        )
    elif metrics["scale"] > max_scale:
        warnings.append(
            "[TYPO] Type scale is %.1f:1; recommended cap is %.0f:1"
            % (metrics["scale"], max_scale)
        )
    else:
        passed.append("[TYPO] Type scale %.1f:1 within %.0f:1" % (metrics["scale"], max_scale))

    if len(metrics["font_sizes"]) > max_sizes:
        warnings.append(
            "[TYPO] %d distinct font sizes; cap is %d. Values: %s"
            % (len(metrics["font_sizes"]), max_sizes, metrics["font_sizes"])
        )
    else:
        passed.append(
            "[TYPO] %d distinct font sizes (limit %d)"
            % (len(metrics["font_sizes"]), max_sizes)
        )

    if metrics["imbalance"] is not None:
        if metrics["imbalance"] > imbalance_limit:
            warnings.append(
                "[BALANCE] Ink centre is %.1f%% off the canvas centre; limit is %.0f%%"
                % (metrics["imbalance"] * 100, imbalance_limit * 100)
            )
        else:
            passed.append(
                "[BALANCE] Ink centre is %.1f%% off centre" % (metrics["imbalance"] * 100)
            )

    return errors, warnings, passed


async def measure(html_path: Path, size: str, timeout: int = 30000) -> Dict:
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
    width = int(size_config["width"])
    height = None if size_config["height"] == "auto" else int(size_config["height"])

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page(
            viewport={"width": width, "height": height or 900}, device_scale_factor=1
        )
        await page.goto(path.as_uri(), wait_until="domcontentloaded", timeout=timeout)
        try:
            await page.wait_for_function(
                "document.fonts ? document.fonts.status === 'loaded' : true",
                timeout=timeout,
            )
        except Exception:
            pass
        measurement = await page.evaluate(MEASURE_JS % json.dumps(BLOCK_SELECTOR))
        await browser.close()
    return measurement


def print_report(
    path: Path,
    size: str,
    density: str,
    style: str,
    metrics: Dict,
    errors: Sequence[str],
    warnings: Sequence[str],
    passed: Sequence[str],
    output_format: str,
) -> None:
    verdict = "FAIL" if errors else "WARN" if warnings else "PASS"
    if output_format == "json":
        print(json.dumps(
            {
                "file": str(path),
                "size": size,
                "density": density,
                "style": style,
                "verdict": verdict,
                "metrics": metrics,
                "errors": list(errors),
                "warnings": list(warnings),
                "passed": list(passed),
            },
            ensure_ascii=False,
            indent=2,
        ))
        return

    print("=" * 60)
    print("ZEROX-ONEPAGER LAYOUT COMPOSITION CHECK")
    print(f"File: {path}")
    print(f"Size: {size}   Density: {density}   Style: {style}")
    print("=" * 60)
    print(
        "blocks=%d  air=%.0f%%  max_gap=%.0fpx  scale=%.1f:1"
        % (
            metrics["blocks"],
            metrics["air_ratio"] * 100,
            metrics["max_gap"],
            metrics["scale"],
        )
    )
    for heading, values, marker in (
        ("ERRORS", errors, "X"),
        ("WARNINGS", warnings, "!"),
        ("PASSED", passed, "OK"),
    ):
        if not values and heading != "PASSED":
            continue
        print()
        print(f"{heading} ({len(values)})")
        for value in values:
            print(f"  [{marker}] {value}")
    print()
    print(f"VERDICT: {verdict}")


def main() -> None:
    config = load_config()
    parser = argparse.ArgumentParser(
        description="Composition check for zerox-onepager HTML (holes, voids, air, scale)"
    )
    parser.add_argument("input", type=Path)
    parser.add_argument("--size", required=True, choices=sorted(config["sizes"]))
    parser.add_argument("--density", choices=sorted(config["densities"]), default="C2")
    parser.add_argument(
        "--style",
        choices=sorted(config["styles"], key=lambda code: int(code[1:])),
        default="",
        help="Design style; applies its layout_override when present",
    )
    parser.add_argument("--timeout", type=int, default=30000)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()

    targets = dict(config["layout"])
    targets["air_ratio"] = config["layout"]["air_ratio"][args.density]
    style_config = config["styles"].get(args.style) or {}
    override = style_config.get("layout_override") or {}
    for key, value in override.items():
        if key == "air_ratio":
            targets["air_ratio"] = value[args.density]
        else:
            targets[key] = value

    try:
        measurement = asyncio.run(measure(args.input, args.size, args.timeout))
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)

    metrics = summarize(measurement)
    errors, warnings, passed = classify(metrics, targets)
    print_report(
        args.input, args.size, args.density, args.style or "default",
        metrics, errors, warnings, passed, args.format,
    )
    raise SystemExit(2 if errors else 1 if warnings else 0)


if __name__ == "__main__":
    main()
