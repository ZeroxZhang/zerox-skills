#!/usr/bin/env python3
"""使用本机 Chromium/Chrome 检查真实字体与页面布局。"""

from __future__ import annotations

import argparse
import html
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

try:
    from .extract_svg import extract_svg_text
except ImportError:  # 直接以脚本运行时，scripts 不是包上下文。
    from extract_svg import extract_svg_text


REPORT_RE = re.compile(
    r'<pre id="architecture-layout-report"[^>]*>([\s\S]*?)</pre>',
    re.IGNORECASE,
)


PROBE = r"""
<script>
(() => {
  const report = { issues: [], metrics: {} };
  const svg = document.querySelector('svg');
  const numberList = value => (value || '').split(/[\s,]+/).filter(Boolean).map(Number);
  const parseBox = element => {
    const [x, y, width, height] = numberList(element.dataset.bbox);
    return { x, y, width, height, right: x + width, bottom: y + height };
  };
  const actualBox = element => {
    const box = element.getBBox();
    return { x: box.x, y: box.y, width: box.width, height: box.height,
      right: box.x + box.width, bottom: box.y + box.height };
  };
  const contains = (outer, inner, epsilon = 0.5) =>
    inner.x >= outer.x - epsilon && inner.y >= outer.y - epsilon &&
    inner.right <= outer.right + epsilon && inner.bottom <= outer.bottom + epsilon;
  const intersects = (a, b, padding = 0) =>
    a.x - padding < b.right && b.x < a.right + padding &&
    a.y - padding < b.bottom && b.y < a.bottom + padding;
  const push = (code, message) => report.issues.push({ level: 'error', code, message });

  if (!svg) {
    push('RENDER_SVG', '页面中没有 SVG');
  } else {
    const components = [...svg.querySelectorAll('[data-role="component"]')];
    const routes = [...svg.querySelectorAll('[data-role="edge-route"]')];
    const labels = [...svg.querySelectorAll('[data-role="edge-label"]')];
    const semanticBoxes = [...svg.querySelectorAll('[data-bbox]')];

    if (components.length === 0) {
      push('RENDER_SEMANTIC_COMPONENTS', '没有可检查的 data-role="component"');
    }
    if (routes.length === 0) {
      push('RENDER_SEMANTIC_ROUTES', '没有可检查的 data-role="edge-route"');
    }

    for (const component of components) {
      const planned = parseBox(component);
      const actual = actualBox(component);
      if (!contains(planned, actual)) {
        push('RENDER_COMPONENT_OVERFLOW', `${component.dataset.id} 的真实内容超出计划 bbox`);
      }
    }

    const actualLabels = labels.map(label => ({
      id: label.dataset.edgeId,
      planned: parseBox(label),
      actual: actualBox(label),
    }));
    for (const label of actualLabels) {
      if (!contains(label.planned, label.actual, 1)) {
        push('RENDER_LABEL_BBOX', `${label.id} 的真实文字超出 data-bbox`);
      }
      for (const component of components) {
        if (intersects(label.actual, parseBox(component), 4)) {
          push('RENDER_LABEL_NODE', `${label.id} 与组件 ${component.dataset.id} 的真实边界冲突`);
        }
      }
    }
    for (let i = 0; i < actualLabels.length; i += 1) {
      for (let j = i + 1; j < actualLabels.length; j += 1) {
        if (intersects(actualLabels[i].actual, actualLabels[j].actual, 4)) {
          push('RENDER_LABEL_LABEL', `${actualLabels[i].id} 与 ${actualLabels[j].id} 的真实文字冲突`);
        }
      }
    }

    const [minX, minY, width, height] = numberList(svg.getAttribute('viewBox'));
    const viewBox = { x: minX, y: minY, width, height, right: minX + width, bottom: minY + height };
    for (const element of semanticBoxes) {
      if (!contains(viewBox, actualBox(element))) {
        push('RENDER_VIEWBOX', `${element.dataset.role || element.tagName} 的真实内容超出 viewBox`);
      }
    }
    report.metrics.svgFontFamily = getComputedStyle(svg).fontFamily;
    report.metrics.componentCount = components.length;
    report.metrics.routeCount = routes.length;
    report.metrics.edgeLabelCount = labels.length;
  }

  report.metrics.viewport = { width: innerWidth, height: innerHeight };
  report.metrics.document = {
    clientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
    clientHeight: document.documentElement.clientHeight,
    scrollHeight: document.documentElement.scrollHeight,
  };
  if (document.documentElement.scrollWidth > document.documentElement.clientWidth + 1) {
    push('PAGE_HORIZONTAL_OVERFLOW', '页面级横向溢出；横向滚动应只发生在 diagram-scroll 内');
  }

  const output = document.createElement('pre');
  output.id = 'architecture-layout-report';
  output.hidden = true;
  output.textContent = JSON.stringify(report);
  document.body.append(output);
})();
</script>
"""


def find_chrome(explicit: str | None) -> str:
    candidates = [
        explicit,
        os.environ.get("CHROME_PATH"),
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    raise RuntimeError("未找到 Chrome/Chromium；可用 --chrome 或 CHROME_PATH 指定")


def build_probe_page(input_path: Path) -> str:
    text = input_path.read_text(encoding="utf-8")
    if input_path.suffix.lower() in {".html", ".htm"} or "<html" in text[:500].lower():
        if "</body>" not in text.lower():
            raise ValueError("HTML 缺少 </body>")
        return re.sub(
            r"</body>",
            lambda _: PROBE + "\n</body>",
            text,
            count=1,
            flags=re.IGNORECASE,
        )
    svg = extract_svg_text(text)
    return f"<!doctype html><html><body style='margin:0'>{svg}{PROBE}</body></html>"


def run_probe(input_path: Path, chrome: str, width: int, height: int) -> dict:
    page = build_probe_page(input_path)
    with tempfile.TemporaryDirectory(prefix="architecture-render-check-") as directory:
        temp_dir = Path(directory)
        page_path = temp_dir / "probe.html"
        page_path.write_text(page, encoding="utf-8")
        command = [
            chrome,
            "--headless",
            "--disable-gpu",
            "--disable-extensions",
            "--no-first-run",
            "--virtual-time-budget=1000",
            f"--window-size={width},{height}",
            "--dump-dom",
            page_path.resolve().as_uri(),
        ]
        result = subprocess.run(command, check=False, capture_output=True, text=True, timeout=15)
        if result.returncode != 0:
            raise RuntimeError(f"Chrome 执行失败 ({result.returncode}): {result.stderr.strip()}")
        match = REPORT_RE.search(result.stdout)
        if not match:
            raise RuntimeError("Chrome 输出中没有布局报告")
        return json.loads(html.unescape(match.group(1)))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="用真实浏览器字体检查架构图布局")
    parser.add_argument("input", type=Path, help="HTML 或 SVG 文件")
    parser.add_argument("--width", type=int, default=1440, help="视口宽度")
    parser.add_argument("--height", type=int, default=900, help="视口高度")
    parser.add_argument("--chrome", help="Chrome/Chromium 可执行文件路径")
    parser.add_argument("--json", action="store_true", help="输出完整 JSON")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        report = run_probe(args.input, find_chrome(args.chrome), args.width, args.height)
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        print(f"渲染检查失败: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif report["issues"]:
        for issue in report["issues"]:
            print(f"{issue['level'].upper()} [{issue['code']}] {issue['message']}")
        print(f"SUMMARY {args.input} — {len(report['issues'])} rendered issue(s)")
    else:
        viewport = report["metrics"]["viewport"]
        print(f"PASS {args.input} — 浏览器布局通过 ({viewport['width']}×{viewport['height']})")
    return 1 if report["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
