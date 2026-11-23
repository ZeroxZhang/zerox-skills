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

GENERIC_FAMILIES = {
    "serif", "sans-serif", "monospace", "cursive", "fantasy", "system-ui",
    "ui-serif", "ui-sans-serif", "ui-monospace", "ui-rounded", "emoji", "math",
    "fangsong",
}
CJK_FONT_MARKERS = (
    "noto sans sc", "noto serif sc", "noto sans tc", "noto serif tc",
    "noto sans hk", "source han", "pingfang", "hiragino", "microsoft yahei",
    "yahei", "wenquanyi", "lxgw", "zcool", "songti", "simsun", "stheiti",
    "heiti", "kaiti", "fangsong", "sarasa",
)
MONO_MARKERS = (
    "mono", "code", "courier", "consolas", "menlo", "sf mono", "cascadia",
    "jetbrains", "fira", "ibm plex mono", "roboto mono", "space mono",
)
GOOGLE_FONT_URL_RE = re.compile(
    r"https://fonts\.googleapis\.com/css2?[^\s\"'<>)]+", re.IGNORECASE
)


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


def parse_font_families(value: str, variables: Dict[str, str]) -> List[str]:
    resolved = resolve_css_value(value, variables)
    families = []
    for part in resolved.split(","):
        name = part.strip().strip('"').strip("'")
        if name:
            families.append(name)
    return families


def is_cjk_family(name: str) -> bool:
    lowered = name.lower()
    return any(marker in lowered for marker in CJK_FONT_MARKERS)


def is_mono_family(name: str) -> bool:
    lowered = name.lower()
    return any(marker in lowered for marker in MONO_MARKERS)


def parse_google_font_families(text: str) -> List[str]:
    families: List[str] = []
    for url in GOOGLE_FONT_URL_RE.findall(text):
        for match in re.finditer(r"family=([^&\"')]+)", url):
            for part in match.group(1).split("|"):
                name = part.replace("+", " ").strip()
                if ":" in name:
                    name = name.split(":")[0]
                if name and name not in families:
                    families.append(name)
    return families


def has_google_display_swap(text: str) -> bool:
    urls = GOOGLE_FONT_URL_RE.findall(text)
    if not urls:
        return True
    return all("display=swap" in url for url in urls)


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
    content_type: Optional[str] = None,
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
                gradients.append((rule.selector, value))
        if re.fullmatch(r"1(?:\s+1\s+0(?:%|px)?)?", rule.declarations.get("flex", "").strip()):
            flex_ones.append(rule.selector)
        if rule.declarations.get("display", "").strip().lower() == "grid":
            grid_rules.append(rule)
        if rule.declarations.get("position", "").strip().lower() == "absolute":
            absolute_rules.append(rule)

    seen_colors = {rgb for _, rgb in color_values}
    limits = {"B5": 10, "B8": 10, "B9": 12, "B10": 12, "B11": 12}
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

    def is_readability_scrim(gradient: str) -> bool:
        """A single-hue alpha ramp used to keep captions readable over media."""
        colors = [rgb for _, rgb in extract_colors(gradient, variables)]
        if len(colors) < 2 or "to top" not in gradient.lower():
            return False
        return len({rgb for rgb in colors}) == 1

    texture_markers = ("halftone", "grain", "noise", "pattern", "dots", "texture", "screen", "stair")

    def is_texture_pattern(selector: str, gradient: str) -> bool:
        """Halftone dots and grain are print materials, not decorative gradients."""
        lowered = selector.lower()
        return "repeating-" in gradient.lower() or any(
            marker in lowered for marker in texture_markers
        )

    forbidden_gradients = []
    scrims = []
    textures = []
    for selector, gradient in gradients:
        gradient_colors = [rgb for _, rgb in extract_colors(gradient, variables)]
        if any(is_blue_purple(rgb) and not (style_norm == "B9" and rgb in b9_allowed) for rgb in gradient_colors):
            forbidden_gradients.append(gradient)
        elif is_readability_scrim(gradient):
            scrims.append(gradient)
        elif is_texture_pattern(selector, gradient):
            textures.append(gradient)
    if forbidden_gradients:
        errors.append(f"[GRADIENT] Blue/purple gradients are forbidden ({len(forbidden_gradients)} found)")
    if scrims:
        passed.append(f"[GRADIENT] {len(scrims)} readability scrim(s) accepted (single-hue alpha ramp)")
    if textures:
        passed.append(
            f"[GRADIENT] {len(textures)} texture pattern(s) accepted (halftone / grain / repeating fill)"
        )
    if not forbidden_gradients and not scrims and not textures and gradients:
        warnings.append(f"[GRADIENT] Found {len(gradients)} gradient(s); confirm each has an information purpose")
    elif not forbidden_gradients and not scrims and not textures and not gradients:
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
    page_rule = find_rule(
        rules,
        r"(^|,)\s*(?:\.page|\.poster|\.canvas|\.onepager)(?:\b|[.#:\[])",
    )
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

    # ---------------------------------------------------------------- fonts
    font_family_values = [
        value
        for rule in rules
        for key, value in rule.declarations.items()
        if key == "font-family"
    ]
    loaded_families = parse_google_font_families(content)
    if font_family_values:
        missing_generic = []
        for value in font_family_values:
            families = parse_font_families(value, variables)
            if families and families[-1].lower() not in GENERIC_FAMILIES:
                missing_generic.append(value)
        if missing_generic:
            message = (
                "[FONT] font-family must end with a generic family "
                f"(sans-serif/serif/monospace): {missing_generic[0]}"
            )
            if loaded_families:
                errors.append(message)
            else:
                warnings.append(message)
        else:
            passed.append("[FONT] Every font stack ends with a generic family")

        resolved_stacks = " ".join(
            " ".join(parse_font_families(value, variables)) for value in font_family_values
        ).lower()

        if loaded_families:
            unused = [name for name in loaded_families if name.lower() not in resolved_stacks]
            if unused:
                warnings.append(f"[FONT] Web fonts loaded but not referenced in any stack: {', '.join(unused)}")
            else:
                passed.append(f"[FONT] All {len(loaded_families)} loaded web fonts are referenced")

            # A CJK companion family (Noto Sans SC …) pairs with the Latin body
            # face rather than counting as a third voice.
            content_families = [
                name for name in loaded_families
                if not is_mono_family(name) and not is_cjk_family(name)
            ]
            cjk_families = [
                name for name in loaded_families
                if not is_mono_family(name) and is_cjk_family(name)
            ]
            if len(content_families) > 2:
                warnings.append(
                    "[FONT] More than 2 non-monospace web font families: "
                    + ", ".join(content_families)
                )
            else:
                suffix = f" + {len(cjk_families)} CJK" if cjk_families else ""
                passed.append(
                    f"[FONT] {len(content_families)} non-monospace web font families "
                    f"(limit 2){suffix}"
                )

            if not has_google_display_swap(content):
                errors.append("[FONT] Google Fonts URL is missing display=swap; text may stay invisible while loading")
            else:
                passed.append("[FONT] Web font URLs request display=swap")

        visible_text = "".join(checker.text_content)
        if re.search(r"[\u4e00-\u9fff]", visible_text):
            if any(marker in resolved_stacks for marker in CJK_FONT_MARKERS):
                passed.append("[FONT] CJK text has a CJK-capable family in the stack")
            else:
                warnings.append(
                    "[FONT] CJK text detected but no CJK family appears in any font stack; "
                    "Chinese may fall back to an unrelated face"
                )

    # ------------------------------------------------------- type scale
    font_sizes: List[float] = []
    for rule in rules:
        value = rule.declarations.get("font-size", "")
        if not value:
            continue
        resolved = resolve_css_value(value, variables)
        font_sizes.extend(float(number) for number in re.findall(r"(\d+(?:\.\d+)?)px", resolved))
    if len(font_sizes) >= 2 and min(font_sizes) > 0:
        ratio = max(font_sizes) / min(font_sizes)
        poster = (content_type or "").upper() == "T4"
        minimum = 8.0 if poster else 3.0
        if ratio < minimum:
            message = (
                f"[TYPO] Type scale ratio {ratio:.1f}:1 ({max(font_sizes):.0f}px / "
                f"{min(font_sizes):.0f}px) is below {minimum:.0f}:1"
            )
            if poster:
                errors.append(message + " — T4 posters need >= 8:1")
            else:
                warnings.append(message)
        else:
            passed.append(f"[TYPO] Type scale ratio {ratio:.1f}:1")

    radius_numbers = {
        int(number)
        for radius in radii
        for number in re.findall(r"(\d+)px", resolve_css_value(radius, variables))
    }
    radius_limit = 4 if style_norm == "B10" else 3
    if len(radius_numbers) > radius_limit:
        warnings.append(
            f"[CONSISTENCY] Too many border-radius values: {sorted(radius_numbers)} "
            f"(limit {radius_limit} for {style_norm or 'default'})"
        )
    else:
        passed.append(
            f"[CONSISTENCY] Border-radius values are consistent ({len(radius_numbers)} unique, limit {radius_limit})"
        )

    return errors, warnings, passed


def print_report(
    path: Path,
    style: Optional[str],
    size: Optional[str],
    errors: Sequence[str],
    warnings: Sequence[str],
    passed: Sequence[str],
    output_format: str,
    content_type: Optional[str] = None,
) -> None:
    verdict = "FAIL" if errors else "WARN" if warnings else "PASS"
    if output_format == "json":
        print(json.dumps(
            {
                "file": str(path),
                "style": style,
                "size": size,
                "type": content_type,
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
    if content_type:
        print(f"Type: {content_type}")
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
    parser.add_argument(
        "--style",
        choices=sorted(config["styles"], key=lambda code: int(code[1:])),
        help="Design style",
    )
    parser.add_argument("--size", choices=sorted(config["sizes"]), help="Canvas size")
    parser.add_argument("--no-bignum", action="store_true", help="Skip BigNumber requirement (E2)")
    parser.add_argument(
        "--type",
        dest="content_type",
        choices=sorted(config["types"]),
        help="Content type; T4 raises the type-scale floor to 8:1",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()

    try:
        errors, warnings, passed = run_checks(
            args.input, args.style, args.size, args.no_bignum, args.content_type
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)

    print_report(
        args.input, args.style, args.size, errors, warnings, passed, args.format,
        args.content_type,
    )
    raise SystemExit(2 if errors else 1 if warnings else 0)


if __name__ == "__main__":
    main()
