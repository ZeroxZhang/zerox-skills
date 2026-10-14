#!/usr/bin/env python3
"""Static quality checks for generated zerox-onepager HTML.

This checker validates source-level invariants. Rendered geometry checks live in
``render_check.py`` because overflow, clipping, and actual canvas dimensions
cannot be determined reliably from HTML/CSS text alone.

Exit codes:
    0 = PASS
    1 = WARN
    2 = FAIL
"""

import argparse
import colorsys
import json
import re
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

RGB = Tuple[int, int, int]
CONFIG_PATH = Path(__file__).resolve().parents[1] / "references" / "config-schema.json"


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def class_tokens(value: str) -> Sequence[str]:
    return tuple(token for token in value.split() if token)


class HTMLChecker(HTMLParser):
    """Collect structure, text, style blocks, and inline declarations."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.has_charset = False
        self.has_font_import = False
        self.has_h1 = False
        self.has_footer = False
        self.has_bignum = False
        self.style_blocks: List[str] = []
        self.inline_styles: List[Tuple[str, str]] = []
        self.text_content: List[str] = []
        self._in_style = False
        self._in_script = False

    def handle_starttag(self, tag: str, attrs: Sequence[Tuple[str, Optional[str]]]) -> None:
        attrs_dict = {key: value or "" for key, value in attrs}
        tokens = class_tokens(attrs_dict.get("class", ""))

        if tag == "meta" and attrs_dict.get("charset", "").lower() == "utf-8":
            self.has_charset = True
        if tag == "h1":
            self.has_h1 = True
        if tag == "footer" or any("footer" in token for token in tokens):
            self.has_footer = True
        if any(token == "bignum" or token.startswith("bignum-") for token in tokens):
            self.has_bignum = True

        if tag == "link":
            href = attrs_dict.get("href", "").lower()
            if any(host in href for host in ("fonts.googleapis.com", "fonts.gstatic.com", "fontsource")):
                self.has_font_import = True

        inline_style = attrs_dict.get("style", "")
        if inline_style:
            self.inline_styles.append((tag, inline_style))

        if tag == "style":
            self._in_style = True
        elif tag == "script":
            self._in_script = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "style":
            self._in_style = False
        elif tag == "script":
            self._in_script = False

    def handle_data(self, data: str) -> None:
        if self._in_style:
            self.style_blocks.append(data)
            if re.search(
                r"@import[^;]*(fonts\.googleapis\.com|fonts\.gstatic\.com|fontsource)",
                data,
                re.IGNORECASE,
            ):
                self.has_font_import = True
        elif not self._in_script:
            self.text_content.append(data)


@dataclass
class CSSRule:
    selector: str
    declarations: Dict[str, str]


def parse_declarations(content: str) -> Dict[str, str]:
    declarations: Dict[str, str] = {}
    for item in content.split(";"):
        if ":" not in item:
            continue
        key, value = item.split(":", 1)
        key = key.strip().lower()
        value = value.strip()
        if key and value:
            declarations[key] = value
    return declarations


def parse_css_rules(css: str) -> List[CSSRule]:
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    rules: List[CSSRule] = []
    for match in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        selector = match.group(1).strip()
        if selector.startswith("@"):
            continue
        declarations = parse_declarations(match.group(2))
        if declarations:
            rules.append(CSSRule(selector=selector, declarations=declarations))
    return rules


def resolve_css_value(value: str, variables: Dict[str, str], depth: int = 0) -> str:
    if depth > 8:
        return value

    def replace(match: re.Match) -> str:
        name = match.group(1)
        fallback = (match.group(2) or "").lstrip(",").strip()
        resolved = variables.get(name, fallback)
        return resolve_css_value(resolved, variables, depth + 1) if resolved else match.group(0)

    return re.sub(r"var\(\s*(--[\w-]+)\s*(,\s*[^)]+)?\)", replace, value)


def parse_color(color_str: str) -> Optional[RGB]:
    value = color_str.strip().lower()
    named = {
        "black": (0, 0, 0),
        "white": (255, 255, 255),
        "red": (255, 0, 0),
        "transparent": None,
    }
    if value in named:
        return named[value]

    if value.startswith("#"):
        raw = value[1:]
        if len(raw) in (3, 4):
            raw = "".join(char * 2 for char in raw[:3])
        elif len(raw) in (6, 8):
            raw = raw[:6]
        else:
            return None
        try:
            return tuple(int(raw[index:index + 2], 16) for index in (0, 2, 4))  # type: ignore
        except ValueError:
            return None

    rgb_match = re.fullmatch(
        r"rgba?\(\s*([+-]?\d+(?:\.\d+)?%?)\s*[, ]\s*"
        r"([+-]?\d+(?:\.\d+)?%?)\s*[, ]\s*"
        r"([+-]?\d+(?:\.\d+)?%?)(?:\s*[,/]\s*[\d.]+%?)?\s*\)",
        value,
    )
    if rgb_match:
        channels = []
        for channel in rgb_match.groups():
            number = float(channel.rstrip("%"))
            if channel.endswith("%"):
                number = number * 2.55
            channels.append(max(0, min(255, round(number))))
        return tuple(channels)  # type: ignore

    hsl_match = re.fullmatch(
        r"hsla?\(\s*([+-]?\d+(?:\.\d+)?)"
        r"(?:deg)?\s*[, ]\s*([\d.]+)%\s*[, ]\s*([\d.]+)%"
        r"(?:\s*[,/]\s*[\d.]+%?)?\s*\)",
        value,
    )
    if hsl_match:
        hue = float(hsl_match.group(1)) % 360 / 360
        saturation = float(hsl_match.group(2)) / 100
        lightness = float(hsl_match.group(3)) / 100
        red, green, blue = colorsys.hls_to_rgb(hue, lightness, saturation)
        return round(red * 255), round(green * 255), round(blue * 255)
    return None


COLOR_TOKEN_RE = re.compile(
    r"#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)|hsla?\([^)]*\)|\b(?:black|white|red|transparent)\b",
    re.IGNORECASE,
)


def extract_colors(value: str, variables: Dict[str, str]) -> List[Tuple[str, RGB]]:
    resolved = resolve_css_value(value, variables)
    colors: List[Tuple[str, RGB]] = []
    for match in COLOR_TOKEN_RE.finditer(resolved):
        raw = match.group(0)
        rgb = parse_color(raw)
        if rgb is not None:
            colors.append((raw, rgb))
    return colors


def is_blue_purple(rgb: RGB) -> bool:
    red, green, blue = rgb
    maximum = max(rgb)
    blue_dominant = blue > red + 30 and blue > green + 30 and maximum >= 150
    purple = red > 100 and blue > 100 and green < min(red, blue) - 20 and maximum > 150
    known = ((99, 102, 241), (139, 92, 246), (124, 58, 237), (168, 85, 247))
    near_known = any(sum((value - target) ** 2 for value, target in zip(rgb, item)) ** 0.5 < 40 for item in known)
    return blue_dominant or purple or near_known


def is_emoji(character: str) -> bool:
    code = ord(character)
    return any(
        start <= code <= end
        for start, end in (
            (0x1F1E6, 0x1F1FF),
            (0x1F300, 0x1F5FF),
            (0x1F600, 0x1F64F),
            (0x1F680, 0x1F6FF),
            (0x1F900, 0x1F9FF),
            (0x1FA70, 0x1FAFF),
        )
    )


def check_contrast(background: RGB, foreground: RGB) -> float:
    def luminance(rgb: RGB) -> float:
        values = []
        for channel in rgb:
            value = channel / 255
            values.append(value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4)
        return 0.2126 * values[0] + 0.7152 * values[1] + 0.0722 * values[2]

    first, second = luminance(background), luminance(foreground)
    return (max(first, second) + 0.05) / (min(first, second) + 0.05)


def find_rule(rules: Iterable[CSSRule], selector_pattern: str) -> Optional[CSSRule]:
    pattern = re.compile(selector_pattern, re.IGNORECASE)
    for rule in rules:
        if pattern.search(rule.selector):
            return rule
    return None


def declaration_color(
    rule: Optional[CSSRule],
    keys: Sequence[str],
    variables: Dict[str, str],
) -> Optional[RGB]:
    if rule is None:
        return None
    for key in keys:
        value = rule.declarations.get(key)
        if value:
            colors = extract_colors(value, variables)
            if colors:
                return colors[0][1]
    return None


def is_page_level_grid(selector: str) -> bool:
    lowered = selector.lower()
    return any(
        marker in lowered
        for marker in (
            ".page",
            ".main-",
            ".main ",
            ".stacked",
            ".poster",
            ".layout-root",
            ".root-grid",
            "body",
        )
    )


def is_decorative_absolute(rule: CSSRule) -> bool:
    selector = rule.selector.lower()
    pointer_events = rule.declarations.get("pointer-events", "").lower()
    return (
        pointer_events == "none"
        or "::before" in selector
        or "::after" in selector
        or any(marker in selector for marker in ("decor", "background", "kicker", "ornament"))
    )


def collect_css(checker: HTMLChecker) -> Tuple[List[CSSRule], Dict[str, str]]:
    rules: List[CSSRule] = []
    for block in checker.style_blocks:
        rules.extend(parse_css_rules(block))
    for tag, inline in checker.inline_styles:
        rules.append(CSSRule(selector=f"<{tag}>[style]", declarations=parse_declarations(inline)))

    variables: Dict[str, str] = {}
    for rule in rules:
        for key, value in rule.declarations.items():
            if key.startswith("--"):
                variables[key] = value
    return rules, variables


def run_checks(
    html_path: Path,
    style: Optional[str] = None,
    size: Optional[str] = None,
    no_bignum: bool = False,
) -> Tuple[List[str], List[str], List[str]]:
    path = Path(html_path)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    content = path.read_text(encoding="utf-8")
    checker = HTMLChecker()
    checker.feed(content)
    rules, variables = collect_css(checker)

    errors: List[str] = []
    warnings: List[str] = []
    passed: List[str] = []
    style_norm = (style or "").upper()
    size_norm = (size or "").upper()
    config = load_config()
    fixed_height = bool(size_norm and config["sizes"][size_norm]["fixed_height"])

    if checker.has_charset:
        passed.append("[STRUCTURE] UTF-8 charset declared")
    else:
        errors.append("[STRUCTURE] Missing <meta charset='UTF-8'>")
    if checker.has_font_import:
        passed.append("[STRUCTURE] Optional web font loading configured")
    else:
        passed.append("[STRUCTURE] No web font import; system fallback mode")
    if checker.has_h1:
        passed.append("[STRUCTURE] Main heading present")
    else:
        errors.append("[STRUCTURE] Missing main heading (h1)")
    if checker.has_footer:
        passed.append("[STRUCTURE] Footer present")
    else:
        warnings.append("[STRUCTURE] No semantic <footer> or footer class detected")
    if checker.has_bignum:
        passed.append("[BIGNUMBER] BigNumber module present")
    elif no_bignum:
        passed.append("[BIGNUMBER] Skipped because E2 was selected")
    else:
        errors.append("[BIGNUMBER] Missing .bignum or .bignum-* module; use --no-bignum for E2")

    emojis = [char for char in "".join(checker.text_content) if is_emoji(char)]
    if emojis:
        unique = "".join(dict.fromkeys(emojis))
        errors.append(f"[EMOJI] Emoji characters are forbidden in output HTML: {unique[:12]}")
    else:
        passed.append("[EMOJI] No emoji characters detected")

    color_values: List[Tuple[str, RGB]] = []
    shadows: List[str] = []
    radii: List[str] = []
    gradients: List[str] = []
    flex_ones: List[str] = []
    grid_rules: List[CSSRule] = []
    absolute_rules: List[CSSRule] = []
    for rule in rules:
        for property_name, value in rule.declarations.items():
            color_values.extend(extract_colors(value, variables))
            if property_name == "box-shadow":
                shadows.append(value)
            elif property_name == "border-radius":
                radii.append(value)
            elif property_name in ("background", "background-image") and "gradient(" in value.lower():
                gradients.append(value)
        if re.fullmatch(r"1(?:\s+1\s+0(?:%|px)?)?", rule.declarations.get("flex", "").strip()):
            flex_ones.append(rule.selector)
        if rule.declarations.get("display", "").strip().lower() == "grid":
            grid_rules.append(rule)
        if rule.declarations.get("position", "").strip().lower() == "absolute":
            absolute_rules.append(rule)

    seen_colors = {rgb for _, rgb in color_values}
    limits = {"B5": 10, "B8": 10, "B9": 12}
    limit = limits.get(style_norm, 7)
    if len(seen_colors) <= limit:
        passed.append(f"[COLOR] Palette uses {len(seen_colors)} unique colors (limit {limit})")
    else:
        errors.append(f"[COLOR] Palette uses {len(seen_colors)} unique colors; {style_norm or 'default'} limit is {limit}")

    b9_allowed = {
        (66, 133, 244), (26, 115, 232), (25, 103, 210), (234, 67, 53),
        (251, 188, 4), (52, 168, 83), (138, 180, 248), (197, 138, 249),
        (129, 201, 149),
    }
    b7_allowed = {(30, 58, 95), (159, 18, 57)}
    suspicious = []
    for raw, rgb in color_values:
        if not is_blue_purple(rgb):
            continue
        if style_norm == "B9" and rgb in b9_allowed:
            continue
        if style_norm == "B7" and rgb in b7_allowed:
            continue
        suspicious.append(raw)
    if suspicious:
        warnings.append(f"[COLOR] Review blue/purple tones: {', '.join(dict.fromkeys(suspicious))}")
    else:
        passed.append("[COLOR] No unexpected blue/purple tones")

    forbidden_gradients = []
    for gradient in gradients:
        gradient_colors = [rgb for _, rgb in extract_colors(gradient, variables)]
        if any(is_blue_purple(rgb) and not (style_norm == "B9" and rgb in b9_allowed) for rgb in gradient_colors):
            forbidden_gradients.append(gradient)
    if forbidden_gradients:
        errors.append(f"[GRADIENT] Blue/purple gradients are forbidden ({len(forbidden_gradients)} found)")
    elif gradients:
        warnings.append(f"[GRADIENT] Found {len(gradients)} gradient(s); confirm each has an information purpose")
    else:
        passed.append("[GRADIENT] No gradients used")

    glow_shadows = [
        shadow for shadow in shadows
        if re.search(r"(?:^|,)\s*0\s+0\s+\d", shadow) or re.search(r"\d{2,}px.*rgba?\(", shadow)
    ]
    if glow_shadows:
        warnings.append(f"[SHADOW] Found {len(glow_shadows)} potential glow shadow(s)")
    else:
        passed.append("[SHADOW] No glow-like shadows detected")

    if fixed_height and flex_ones:
        errors.append(f"[LAYOUT] flex:1 is forbidden on fixed-height canvas {size_norm}: {', '.join(flex_ones[:4])}")
    elif flex_ones:
        warnings.append(f"[LAYOUT] Review flex:1 usage: {', '.join(flex_ones[:4])}")
    else:
        passed.append("[LAYOUT] No flex:1 usage detected")

    missing_rows = [
        rule.selector for rule in grid_rules
        if fixed_height and is_page_level_grid(rule.selector) and "grid-template-rows" not in rule.declarations
    ]
    if missing_rows:
        errors.append(f"[LAYOUT] Page-level grid missing grid-template-rows on {size_norm}: {', '.join(missing_rows[:6])}")
    elif fixed_height:
        passed.append(f"[LAYOUT] Page-level grids declare rows for {size_norm}")

    non_decorative_absolute = [rule.selector for rule in absolute_rules if not is_decorative_absolute(rule)]
    if non_decorative_absolute:
        warnings.append(
            "[LAYOUT] Absolute positioning needs manual content/decorative review: "
            + ", ".join(non_decorative_absolute[:6])
        )
    else:
        passed.append("[LAYOUT] Absolute positioning is absent or marked decorative")

    body_rule = find_rule(rules, r"(^|,)\s*body\s*(,|$)")
    page_rule = find_rule(rules, r"(^|,)\s*\.page(?:\b|[.#:\[])")
    background = declaration_color(page_rule, ("background-color", "background"), variables)
    if background is None:
        background = declaration_color(body_rule, ("background-color", "background"), variables)
    foreground = declaration_color(page_rule, ("color",), variables)
    if foreground is None:
        foreground = declaration_color(body_rule, ("color",), variables)

    contrast_results = []
    if background and foreground:
        contrast_results.append(("Body text", check_contrast(background, foreground), 4.5))
    bignum_rule = find_rule(rules, r"\.bignum-value\b")
    bignum_color = declaration_color(bignum_rule, ("color",), variables)
    if background and bignum_color:
        contrast_results.append(("BigNumber", check_contrast(background, bignum_color), 4.5))

    if contrast_results:
        for label, ratio, minimum in contrast_results:
            if ratio >= minimum:
                passed.append(f"[CONTRAST] {label}: {ratio:.2f}:1")
            else:
                errors.append(f"[CONTRAST] {label}: {ratio:.2f}:1, below {minimum}:1")
    else:
        warnings.append("[CONTRAST] No resolvable foreground/background pair found")

    radius_numbers = {
        int(number)
        for radius in radii
        for number in re.findall(r"(\d+)px", resolve_css_value(radius, variables))
    }
    if len(radius_numbers) > 3:
        warnings.append(f"[CONSISTENCY] Too many border-radius values: {sorted(radius_numbers)}")
    else:
        passed.append(f"[CONSISTENCY] Border-radius values are consistent ({len(radius_numbers)} unique)")

    return errors, warnings, passed


def print_report(
    path: Path,
    style: Optional[str],
    size: Optional[str],
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
                "style": style,
                "size": size,
                "verdict": verdict,
                "errors": list(errors),
                "warnings": list(warnings),
                "passed": list(passed),
            },
            ensure_ascii=False,
            indent=2,
        ))
        return

    print("=" * 60)
    print("ZEROX-ONEPAGER STATIC QUALITY CHECK")
    print(f"File: {path}")
    if style:
        print(f"Style: {style}")
    if size:
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
    parser = argparse.ArgumentParser(description="Static quality check for zerox-onepager HTML")
    parser.add_argument("input", type=Path, help="Path to input HTML")
    parser.add_argument("--style", choices=sorted(config["styles"]), help="Design style")
    parser.add_argument("--size", choices=sorted(config["sizes"]), help="Canvas size")
    parser.add_argument("--no-bignum", action="store_true", help="Skip BigNumber requirement (E2)")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()

    try:
        errors, warnings, passed = run_checks(args.input, args.style, args.size, args.no_bignum)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)

    print_report(args.input, args.style, args.size, errors, warnings, passed, args.format)
    raise SystemExit(2 if errors else 1 if warnings else 0)


if __name__ == "__main__":
    main()
