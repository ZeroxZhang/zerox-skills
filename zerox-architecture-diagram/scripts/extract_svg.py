#!/usr/bin/env python3
"""从自包含 HTML 中提取第一段 SVG，并保持其内容不变。"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET


SVG_RE = re.compile(r"<svg\b[\s\S]*?</svg>", re.IGNORECASE)


def extract_svg_text(html_text: str) -> str:
    match = SVG_RE.search(html_text)
    if not match:
        raise ValueError("输入文件中没有找到 <svg>...</svg>")

    svg = match.group(0).strip()
    opening_end = svg.find(">")
    opening = svg[:opening_end]
    if "xmlns=" not in opening:
        svg = svg[:4] + ' xmlns="http://www.w3.org/2000/svg"' + svg[4:]

    # 解析一次，避免输出一个只能靠 HTML 容错机制打开的伪 SVG。
    ET.fromstring(svg)
    return svg + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="从 HTML 提取独立 SVG")
    parser.add_argument("html", type=Path, help="包含内联 SVG 的 HTML 文件")
    parser.add_argument("svg", type=Path, nargs="?", help="输出 SVG 路径；默认与 HTML 同名")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    output = args.svg or args.html.with_suffix(".svg")
    try:
        svg = extract_svg_text(args.html.read_text(encoding="utf-8"))
        output.write_text(svg, encoding="utf-8")
    except (OSError, ValueError, ET.ParseError) as exc:
        print(f"提取失败: {exc}", file=sys.stderr)
        return 2

    print(f"已提取 SVG: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
