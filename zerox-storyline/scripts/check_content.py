#!/usr/bin/env python3
"""zerox-storyline 内容包检查器。

检查一个内容包（00_brief.md … 07_audit_report.md）的结构、卡片完整性、
引用可解析性、A/B 级卡片覆盖率、库外数字、清洁版一致性，并输出行动标题序列。

它查不了：口径是否可比、证据是否真的支持结论、因果强度与范围词是否被夸大、
图表类型是否匹配比较关系、标题是否真的是那一页的结论。那些必须人工做。

用法：
    python3 check_content.py <任务目录>
    python3 check_content.py <任务目录> --json
    python3 check_content.py <任务目录> --titles      # 只输出行动标题序列
    python3 check_content.py <任务目录> --no-numbers  # 跳过较慢的数字回查

退出码：0 = 无错误；1 = 有错误（警告不影响退出码）。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field

# ---------------------------------------------------------------- 基础工具

FULLWIDTH = str.maketrans("０１２３４５６７８９％", "0123456789%")

UNITS = [
    "%", "个百分点", "万元", "亿元", "美元", "元", "万", "亿",
    "平方米", "平米", "平", "公里", "吨", "件", "张", "台", "户",
    "分钟", "小时", "个月", "年", "月", "天", "个", "家", "人", "次", "倍", "点",
]
UNIT_ALT = "|".join(re.escape(u) for u in sorted(UNITS, key=len, reverse=True))

# 推断 / 建议类表述的标记。这些句子里允许出现卡片库以外的数字（推荐值、目标值、
# 测算结果），因为它们本来就不是材料里的事实数——但必须显式标注，且要写明依据。
JUDGMENT_RE = re.compile(
    r"推断|建议|假设|估算|测算|预测|目标|拟|计划|预算上限"
    r"|不超过|不低于|不高于|至少|至多|上限|下限|以内"
)

# 日期与序号。它们是叙事脚手架，不是数据主张——「3 月董事会」「2026 年」这类写法
# 不应该被要求标注来源，否则正文会被引注淹没。带引用标注时仍照常核对。
DATE_RE = re.compile(
    r"\d{4}\s*[-/年]|\d{1,2}\s*月|\d{1,2}\s*日|第\s*\d+\s*[季度天]|\d{4}\s*H[12]|\d+\s*季度"
)

# 数字 +（可选空格）+ 单位；或带小数点的数字；或 4 位以上整数
NUM_RE = re.compile(
    r"(?<![\d.])(?P<num>\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)"
    r"(?P<gap>\s*)"
    r"(?P<unit>" + UNIT_ALT + r")?"
)

# 算作「信息已安置」的文件。03 是故事线、07 是登记表，两者都不在其中：
# 在结构树里挂名不等于真的写进了正文，在覆盖审计里登记也不等于安置。
PLACEMENT_FILES = {"04_manuscript.md", "05_storyboard.md", "06_slides.md"}

CITATION_RE = re.compile(r"〔([^〕]*?)〕")
CARD_ID_RE = re.compile(r"C\d{1,4}")
# 故事板与审计报告用表格登记去向，卡片 ID 是裸写的（| C001 | A | 待定 |），
# 不带〔〕。覆盖率统计必须把这种写法也算上，否则已登记的去向会被误判成「无去向」。
BARE_CARD_RE = re.compile(r"(?<![A-Za-z0-9])C\d{3,}(?![0-9])")


def strip_references(text: str) -> str:
    """去掉卡片与来源标识，避免把 C012 / S03-p12 里的数字当成数据。"""
    text = CITATION_RE.sub(" ", text)
    text = re.sub(r"\b[CS]\d{1,4}\s*[-–—]\s*[A-Za-z0-9§.表图附录一二三四五六七八九十]*", " ", text)
    text = re.sub(r"\b[CS]\d{1,4}\b", " ", text)
    return text


def to_halfwidth(text: str) -> str:
    return text.translate(FULLWIDTH)


def norm_number(raw: str) -> float | None:
    try:
        return float(raw.replace(",", ""))
    except ValueError:
        return None


def decimals(raw: str) -> int:
    return len(raw.split(".")[1]) if "." in raw else 0


def extract_numbers(text: str, skip_dates: bool = False) -> list[tuple[str, float, str]]:
    """返回 [(原始串, 数值, 单位)]，只保留「像数据」的数字。

    skip_dates=True 时跳过日期与序号（用于「未标注来源」检查）。
    带引用标注的核对不跳过——日期一旦进了论据，也要能回溯。
    """
    half = to_halfwidth(text)
    date_spans = [m.span() for m in DATE_RE.finditer(half)] if skip_dates else []
    out: list[tuple[str, float, str]] = []
    for m in NUM_RE.finditer(half):
        if date_spans and any(s <= m.start() < e for s, e in date_spans):
            continue
        raw, unit = m.group("num"), m.group("unit") or ""
        value = norm_number(raw)
        if value is None:
            continue
        looks_like_data = bool(unit) or "." in raw or len(raw.replace(",", "").split(".")[0]) >= 4
        if looks_like_data:
            out.append((raw, value, unit))
    return out


def numbers_match(a: float, b: float, a_raw: str, b_raw: str, scale: float = 1.0) -> bool:
    """容忍四舍五入、千分位与万/亿换算的比对。"""
    target = b * scale
    d = min(decimals(a_raw), decimals(b_raw))
    tol = 0.5 * (10 ** -d) if d else 0.5
    return abs(a - target) <= max(tol, abs(target) * 1e-9)


def number_known(value: float, raw: str, library: set[tuple[float, str]]) -> bool:
    for lib_value, lib_raw in library:
        for scale in (1.0, 1e4, 1e-4, 1e8, 1e-8):
            if numbers_match(value, lib_value, raw, lib_raw, scale):
                return True
    return False


# ---------------------------------------------------------------- 解析

@dataclass
class Card:
    cid: str
    fields: dict[str, str] = field(default_factory=dict)
    file: str = ""

    @property
    def grade(self) -> str:
        return (self.fields.get("价值") or self.fields.get("value") or "").strip().upper()

    @property
    def content(self) -> str:
        return self.fields.get("内容", "")


CARD_FIELD_RE = re.compile(r"^\s*[-*]\s*([^：:]{1,12})\s*[：:]\s*(.*)$")


def parse_cards(text: str, filename: str) -> list[Card]:
    cards: list[Card] = []
    current: Card | None = None
    last_key: str | None = None
    for line in text.splitlines():
        m = re.match(r"^###\s+(C\d{1,4})\b", line)
        if m:
            current = Card(cid=m.group(1), file=filename)
            last_key = None
            cards.append(current)
            continue
        if re.match(r"^##\s", line):
            current, last_key = None, None
            continue
        if current is None:
            continue
        fm = CARD_FIELD_RE.match(line)
        if fm:
            key, value = fm.group(1).strip(), fm.group(2).strip()
            current.fields[key] = value
            last_key = key
        elif last_key and line.strip():
            current.fields[last_key] = (current.fields[last_key] + " " + line.strip()).strip()
    return cards


def parse_cards_jsonl(path: str) -> list[Card]:
    cards: list[Card] = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            cid = str(obj.pop("id", obj.pop("卡片ID", obj.pop("cid", "")))).strip()
            if cid:
                cards.append(Card(cid=cid, fields={k: str(v) for k, v in obj.items()}, file=os.path.basename(path)))
    return cards


def parse_citations(text: str) -> list[tuple[str, str]]:
    """返回 [(卡片ID, 来源定位)]。"""
    out: list[tuple[str, str]] = []
    for m in CITATION_RE.finditer(text):
        inner = m.group(1)
        parts = re.split(r"[｜|]", inner, maxsplit=1)
        cards = re.split(r"[、,，/]", parts[0])
        locator = parts[1].strip() if len(parts) > 1 else ""
        for c in cards:
            cid = c.strip()
            if CARD_ID_RE.fullmatch(cid):
                out.append((cid, locator))
    return out


def parse_slide_titles(text: str) -> list[tuple[str, str]]:
    """返回 [(页码, 行动标题)]。"""
    out: list[tuple[str, str]] = []
    page = ""
    for line in text.splitlines():
        m = re.match(r"^##\s+(P\d+)\b", line)
        if m:
            page = m.group(1)
            continue
        m = re.match(r"^\s*\*\*行动标题\*\*\s*[：:]\s*(.+?)\s*$", line)
        if m:
            out.append((page, m.group(1)))
    return out


# ---------------------------------------------------------------- 检查

@dataclass
class Finding:
    level: str  # ERROR / WARN
    code: str
    message: str


class Report:
    def __init__(self) -> None:
        self.findings: list[Finding] = []
        self.info: dict = {}

    def error(self, code: str, message: str) -> None:
        self.findings.append(Finding("ERROR", code, message))

    def warn(self, code: str, message: str) -> None:
        self.findings.append(Finding("WARN", code, message))

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.level == "ERROR"]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.level == "WARN"]


REQUIRED = {
    "00_brief.md": "任务简报",
    "01_materials_index.md": "材料索引",
    "03_storyline.md": "故事线",
    "04_manuscript.md": "内容稿母版",
    "04_manuscript_clean.md": "内容稿清洁版",
    "07_audit_report.md": "质量审计报告",
}


def read(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def check_directory(target: str, check_numbers: bool = True) -> Report:
    rep = Report()

    if not os.path.isdir(target):
        rep.error("dir", f"目录不存在：{target}")
        return rep

    files = sorted(os.listdir(target))

    for name, label in REQUIRED.items():
        if name not in files:
            rep.error("missing-file", f"缺少{label}：{name}")

    card_files = [f for f in files if re.match(r"^02_info_cards.*\.md$", f)]
    jsonl_files = [f for f in files if re.match(r"^02_info_cards.*\.jsonl$", f)]
    if not card_files and not jsonl_files:
        rep.error("missing-file", "缺少信息卡片库：02_info_cards.md（或分批文件 / .jsonl）")

    slides_present = "06_slides.md" in files
    storyboard_present = "05_storyboard.md" in files
    if slides_present and not storyboard_present:
        rep.error("missing-file", "有逐页内容但缺少故事板：05_storyboard.md")
    mode = "分页" if (slides_present or storyboard_present) else ("内容稿" if "04_manuscript.md" in files else "未知")
    rep.info["mode"] = mode

    # ---- 卡片
    cards: list[Card] = []
    for f in card_files:
        cards.extend(parse_cards(read(os.path.join(target, f)), f))
    if not card_files:
        for f in jsonl_files:
            cards.extend(parse_cards_jsonl(os.path.join(target, f)))

    seen: dict[str, str] = {}
    for c in cards:
        if c.cid in seen:
            rep.error("dup-card", f"卡片 ID 重复：{c.cid}（{seen[c.cid]} 与 {c.file}）")
        seen[c.cid] = c.file

        if c.grade not in ("A", "B", "C"):
            rep.error("card-grade", f"{c.cid} 价值等级非法或缺失：「{c.grade}」（应为 A/B/C）")
        if not c.content.strip():
            rep.error("card-content", f"{c.cid} 缺「内容」")
        if c.grade in ("A", "B") and not c.fields.get("含义", "").strip():
            rep.warn("card-sowhat", f"{c.cid} 是 {c.grade} 级但没有「含义 So what」")
        for key in ("类型", "来源", "性质", "可信度", "主题"):
            if not c.fields.get(key, "").strip():
                rep.warn("card-field", f"{c.cid} 缺字段「{key}」")

    by_id = {c.cid: c for c in cards}
    rep.info["cards_total"] = len(cards)
    rep.info["cards_by_grade"] = {g: sum(1 for c in cards if c.grade == g) for g in ("A", "B", "C")}

    graded = [c for c in cards if c.grade in ("A", "B", "C")]
    a_count = sum(1 for c in graded if c.grade == "A")
    rep.info["a_ratio"] = round(a_count / len(graded), 3) if graded else 0.0
    if len(graded) >= 20 and a_count / len(graded) >= 0.35:
        rep.warn("grade-calibration",
                 f"A 级占 {a_count}/{len(graded)} = {round(100 * a_count / len(graded))}%，分级已失去区分度。"
                 "A 级的判据是「抽掉它，中心论点或某个关键支撑点会改口」，不是「与决策有关」；"
                 "一批决策材料里 A 级通常在 1/4–1/3 之间；"
                 "过不了这一问的应降为 B。复核见 references/info-extraction.md §3")

    # ---- 引用与覆盖率
    scan_files = [f for f in ("03_storyline.md", "04_manuscript.md", "05_storyboard.md",
                              "06_slides.md", "07_audit_report.md") if f in files]
    cited: dict[str, set[str]] = {c.cid: set() for c in cards}
    dangling: list[tuple[str, str]] = []
    for f in scan_files:
        text = read(os.path.join(target, f))
        ids = {cid for cid, _ in parse_citations(text)} | set(BARE_CARD_RE.findall(text))
        for cid in sorted(ids):
            if cid in by_id:
                cited[cid].add(f)
            else:
                dangling.append((cid, f))

    for cid, f in sorted(set(dangling)):
        rep.error("dangling-ref", f"悬空引用：{f} 引用了不存在的卡片 {cid}")

    # 交付物文件才算「有去向」：03 是故事线（计划），在结构树里挂名不等于正文或页面用上了它。
    # 只在 03 出现的卡片意味着「计划用了但交付物里没落地」，正是覆盖审计要抓的丢失。
    placed, only_audit, planned_only, nowhere = [], [], [], []
    for c in cards:
        if c.grade not in ("A", "B"):
            continue
        where = cited.get(c.cid, set())
        if where & PLACEMENT_FILES:
            placed.append(c.cid)
        elif "07_audit_report.md" in where:
            only_audit.append(c.cid)
        elif "03_storyline.md" in where:
            planned_only.append(c.cid)
        else:
            nowhere.append(c.cid)

    def _flag(cid: str, code: str, msg: str) -> None:
        (rep.error if by_id[cid].grade == "A" else rep.warn)(code, f"{cid}（{by_id[cid].grade} 级）{msg}")

    for cid in nowhere:
        _flag(cid, "coverage", "没有任何去向：既未进稿件与页面，也未在审计报告登记")
    for cid in planned_only:
        _flag(cid, "coverage", "只在故事线里挂了名，未进稿件或页面——结构树排了它，但交付物里没用上")
    for cid in only_audit:
        _flag(cid, "coverage", "只出现在审计报告里，未进正文或页面"
                               + ("——A 级卡片不允许「确认不用」，请说明该降级或主线缺陷"
                                  if by_id[cid].grade == "A" else ""))

    ab = [c for c in cards if c.grade in ("A", "B")]
    rep.info["coverage"] = {
        "ab_total": len(ab),
        "placed": len(placed),
        "only_in_audit": len(only_audit),
        "planned_only": len(planned_only),
        "nowhere": len(nowhere),
        "a_total": sum(1 for c in cards if c.grade == "A"),
        "a_placed": sum(1 for c in cards if c.grade == "A" and c.cid in placed),
    }

    # ---- 数字回查
    library: set[tuple[float, str]] = set()
    for c in cards:
        for raw, value, _ in extract_numbers(c.content + " " + c.fields.get("含义", "")):
            library.add((value, raw))

    if check_numbers:
        run_number_checks(rep, target, files, by_id, library)

    # ---- 行动标题
    titles: list[tuple[str, str]] = []
    if "06_slides.md" in files:
        titles = parse_slide_titles(read(os.path.join(target, "06_slides.md")))
        if not titles:
            rep.warn("titles", "06_slides.md 里没解析到行动标题——检查块头与 **行动标题**： 的格式")
    rep.info["titles"] = titles
    rep.info["slide_count"] = len(titles)

    return rep


def run_number_checks(rep: Report, target: str, files: list[str],
                      by_id: dict[str, Card], library: set[tuple[float, str]]) -> None:
    checked = 0
    lost = 0

    # 1) 稿件与页面里带引用的句子：数字必须能在卡片库里找到
    for name in ("04_manuscript.md", "06_slides.md"):
        if name not in files:
            continue
        text = read(os.path.join(target, name))
        for lineno, line in enumerate(text.splitlines(), 1):
            if "〔" not in line:
                continue
            refs = [cid for cid, _ in parse_citations(line)]
            cited_cards = [by_id[c] for c in refs if c in by_id]
            body = strip_references(line)
            judgment = bool(JUDGMENT_RE.search(body))
            for raw, value, unit in extract_numbers(body):
                checked += 1
                in_library = number_known(value, raw, library)
                if not in_library:
                    if judgment:
                        rep.warn("number-judgment",
                                 f"{name}:{lineno} 推断或建议类数字「{raw}{unit}」不在卡片库中"
                                 f"（引用 {('、'.join(refs) or '无')}）——确认已显式标注为推断并写明依据")
                    else:
                        rep.error("number-unknown",
                                  f"{name}:{lineno} 出现卡片库里没有的数字「{raw}{unit}」"
                                  f"（引用 {('、'.join(refs) or '无')}）")
                        lost += 1
                    continue
                in_cited = any(number_known(value, raw, {(v, r) for r, v, _ in extract_numbers(c.content)})
                               for c in cited_cards)
                if cited_cards and not in_cited:
                    rep.warn("number-mismatch",
                             f"{name}:{lineno} 数字「{raw}{unit}」在库中能找到，但不在所引卡片"
                             f"（{'、'.join(refs)}）的内容里——确认是否引错卡片或口径不同")

    # 2) 未标注来源的数字（限正文与页面正文，避免附录与表格噪音）
    suspects = 0
    for name, marker in (("04_manuscript.md", None), ("06_slides.md", "**正文**")):
        if name not in files:
            continue
        text = read(os.path.join(target, name))
        in_appendix = False
        in_body = marker is None
        for lineno, line in enumerate(text.splitlines(), 1):
            if re.match(r"^#{2,3}\s", line):
                in_appendix = bool(re.search(r"附录|来源清单|术语", line))
                in_body = marker is None or False
            elif marker and re.match(r"^\s*\*\*", line):
                in_body = line.strip().startswith(marker)
            body = strip_references(line)
            if (in_appendix or not in_body or "〔" in line
                    or line.lstrip().startswith(("#", "|", ">"))
                    or JUDGMENT_RE.search(body)):
                continue
            if extract_numbers(body, skip_dates=True):
                suspects += 1
                if suspects <= 15:
                    rep.warn("number-uncited", f"{name}:{lineno} 有数字但没有来源标注——补卡片来源或删除：{line.strip()[:48]}")
    if suspects > 15:
        rep.warn("number-uncited", f"另有 {suspects - 15} 处未标注来源的数字，未逐条列出")

    # 3) 清洁版与母版数字一致性
    if "04_manuscript.md" in files and "04_manuscript_clean.md" in files:
        # 两侧都先剥引用再抽数字：清洁版是母版的机械删标注版，剥离必须对称，
        # 否则母版正文里任何形如 S03-p12 的写法都会造成「清洁版多出数字」的假错误。
        ms = {v for _, v, _ in extract_numbers(strip_references(read(os.path.join(target, "04_manuscript.md"))))}
        clean = {v for _, v, _ in extract_numbers(strip_references(read(os.path.join(target, "04_manuscript_clean.md"))))}
        extra = sorted(clean - ms)
        missing = sorted(ms - clean)
        if extra:
            rep.error("clean-extra", f"清洁版出现母版没有的数字：{extra[:8]}——清洁版只能机械删除标注，不得改写")
        if missing:
            rep.warn("clean-missing", f"母版有而清洁版没有的数字：{missing[:8]}——确认是否为标注内数字")

    rep.info["numbers"] = {"checked": checked, "unknown": lost}


# ---------------------------------------------------------------- 输出

def render(rep: Report, target: str) -> str:
    lines = [f"检查：{os.path.abspath(target)}", f"模式：{rep.info.get('mode', '未知')}", ""]

    grades = rep.info.get("cards_by_grade", {})
    cov = rep.info.get("coverage", {})
    nums = rep.info.get("numbers", {})
    lines += [
        f"卡片：{rep.info.get('cards_total', 0)} 张（A {grades.get('A', 0)} / B {grades.get('B', 0)}"
        f" / C {grades.get('C', 0)}；A 级占比 {round(100 * rep.info.get('a_ratio', 0))}%）",
        f"覆盖率：A 级 {cov.get('a_placed', 0)}/{cov.get('a_total', 0)}"
        f"，A/B 已安置 {cov.get('placed', 0)}/{cov.get('ab_total', 0)}"
        f"，仅故事线挂名 {cov.get('planned_only', 0)}，仅审计登记 {cov.get('only_in_audit', 0)}"
        f"，无去向 {cov.get('nowhere', 0)}",
        f"数字回查：核对 {nums.get('checked', 0)} 个，库外 {nums.get('unknown', 0)} 个",
        f"页数：{rep.info.get('slide_count', 0)} 页",
        "",
    ]

    if rep.errors:
        lines.append(f"错误 {len(rep.errors)} 条：")
        lines += [f"  ✗ {f.message}" for f in rep.errors]
    else:
        lines.append("错误 0 条：结构、引用与覆盖率检查通过。")

    lines.append("")
    if rep.warnings:
        lines.append(f"警告 {len(rep.warnings)} 条（需人工确认，不是自动失败）：")
        lines += [f"  ! {f.message}" for f in rep.warnings]
    else:
        lines.append("警告 0 条。")

    lines += [
        "",
        "脚本查不了，必须人工做：口径是否可比、证据是否真的支持结论、因果强度与范围词是否被夸大、",
        "图表类型是否匹配要表达的比较关系、标题是否真的是那一页的结论、执行摘要能否独立阅读。",
        "自动检查通过 ≠ 审计通过。",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="zerox-storyline 内容包检查器")
    ap.add_argument("target", help="内容包目录（含 00_brief.md … 07_audit_report.md）")
    ap.add_argument("--json", action="store_true", help="输出机器可读结果")
    ap.add_argument("--titles", action="store_true", help="只输出行动标题序列")
    ap.add_argument("--no-numbers", action="store_true", help="跳过数字回查")
    args = ap.parse_args(argv)

    rep = check_directory(args.target, check_numbers=not args.no_numbers)

    if args.titles:
        for page, title in rep.info.get("titles", []):
            print(f"{page}  {title}")
        return 0

    if args.json:
        print(json.dumps({
            "target": os.path.abspath(args.target),
            "mode": rep.info.get("mode"),
            "info": {k: v for k, v in rep.info.items() if k != "titles"},
            "errors": [{"code": f.code, "message": f.message} for f in rep.errors],
            "warnings": [{"code": f.code, "message": f.message} for f in rep.warnings],
            "titles": [{"page": p, "title": t} for p, t in rep.info.get("titles", [])],
            "passed": not rep.errors,
        }, ensure_ascii=False, indent=2))
    else:
        print(render(rep, args.target))

    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
