#!/usr/bin/env python3
"""check_content.py 的回归测试。

跑：python3 zerox-storyline/scripts/test_check_content.py
或：python3 -m unittest discover -s zerox-storyline/scripts -v
"""

from __future__ import annotations

import os
import re
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from check_content import (  # noqa: E402
    check_directory,
    extract_numbers,
    parse_cards,
    parse_citations,
    parse_slide_titles,
)

# ---------------------------------------------------------------- 夹具素材

BRIEF = "# 简报\n\n| 受众 | 董事会 |\n"
INDEX = "# 材料索引\n\n| S01 | 纪要 | 精读完成 |\n"
STORYLINE = "# 故事线\n\n中心论点：应进入上海，但必须小店切入。\n"
AUDIT = "# 审计\n\n## 覆盖审计\n\n无未安置卡片。\n"

MS_LINE = "上海核心商圈租金同比 +23%，回本周期从 14 个月拉长到 26 个月〔C001｜S07-p42〕。"
MANUSCRIPT = f"# 标题\n\n## 执行摘要\n\n{MS_LINE}\n"
CLEAN = "# 标题\n\n## 执行摘要\n\n上海核心商圈租金同比 +23%，回本周期从 14 个月拉长到 26 个月。\n"

CARD_C001 = """### C001

- 类型：数据
- 内容：上海核心商圈租金同比 +23%，回本周期从 14 个月拉长到 26 个月
- 含义：大开模式的回本假设不成立
- 来源：S07-p42
- 性质：事实
- 可信度：中 ｜ 依据：第三方报告
- 价值：A
- 主题：成本
"""

CARD_C002 = """### C002

- 类型：事实
- 内容：两家试点店 6 个月复购率 41%
- 含义：留存验证通过
- 来源：S01-表2
- 性质：事实
- 可信度：高 ｜ 依据：内部经营数据
- 价值：B
- 主题：试点
"""

CARDS_OK = f"# 卡片库\n\n{CARD_C001}\n{CARD_C002}"

STORYBOARD_OK = "# 故事板\n\n| 1 | — | 执行摘要 | 租金压力 | C001 | 执行摘要 |\n"

SLIDES_OK = """# 逐页内容

## P01 ｜ — ｜ 执行摘要

**行动标题**：核心商圈租金同比 +23%，回本周期拉长到 26 个月

**正文**

- 核心商圈租金同比 +23%，回本周期从 14 个月拉长到 26 个月〔C001〕
- 试点店 6 个月复购率 41%〔C002〕

**可视化建议**：非数据页，两栏式

**讲者备注**：先讲冲突，再给结论。

**来源**：C001（S07-p42）、C002（S01-表2）

**追溯**：执行摘要
"""


def errors_of(rep) -> str:
    return "\n".join(f.message for f in rep.errors)


def warnings_of(rep) -> str:
    return "\n".join(f.message for f in rep.warnings)


def strip_citations(text: str) -> str:
    return re.sub(r"〔[^〕]*〕", "", text)


class Fixture:
    """在临时目录里搭一个内容包，按需替换某个文件（传 None 表示不写该文件）。"""

    def __init__(self, with_slides: bool = True, with_storyboard: bool = True, **overrides: str | None) -> None:
        self.dir = tempfile.mkdtemp(prefix="storyline-check-")
        files: dict[str, str | None] = {
            "00_brief.md": BRIEF,
            "01_materials_index.md": INDEX,
            "02_info_cards.md": CARDS_OK,
            "03_storyline.md": STORYLINE,
            "04_manuscript.md": MANUSCRIPT,
            "04_manuscript_clean.md": CLEAN,
            "07_audit_report.md": AUDIT,
        }
        if with_slides:
            files["06_slides.md"] = SLIDES_OK
        if with_storyboard:
            files["05_storyboard.md"] = STORYBOARD_OK
        files.update(overrides)
        for name, text in files.items():
            if text is None:
                continue
            with open(os.path.join(self.dir, name), "w", encoding="utf-8") as fh:
                fh.write(text)

    def check(self, **kw):
        return check_directory(self.dir, **kw)


def single_card_package(card_content: str, ms_line: str, clean_line: str | None = None,
                        extra_card: str = "", **kw) -> Fixture:
    """只含一张 C001 的内容稿模式包，用于数字检查。"""
    card = CARD_C001.replace(
        "上海核心商圈租金同比 +23%，回本周期从 14 个月拉长到 26 个月", card_content)
    ms = f"# 标题\n\n## 执行摘要\n\n{ms_line}\n"
    clean = f"# 标题\n\n## 执行摘要\n\n{clean_line if clean_line is not None else strip_citations(ms_line)}\n"
    return Fixture(with_slides=False, with_storyboard=False,
                   **{"02_info_cards.md": f"# 卡片库\n\n{card}\n{extra_card}",
                      "04_manuscript.md": ms,
                      "04_manuscript_clean.md": clean, **kw})


# ---------------------------------------------------------------- 用例

class TestHappyPath(unittest.TestCase):
    def test_clean_package_passes(self):
        rep = Fixture().check()
        self.assertEqual(errors_of(rep), "")
        self.assertEqual(rep.info["cards_by_grade"], {"A": 1, "B": 1, "C": 0})
        self.assertEqual(rep.info["coverage"]["a_placed"], 1)

    def test_content_only_mode_passes_without_slides(self):
        rep = Fixture(with_slides=False, with_storyboard=False).check()
        self.assertEqual(errors_of(rep), "")
        self.assertEqual(rep.info["mode"], "内容稿")

    def test_slides_without_storyboard_is_error(self):
        rep = Fixture(with_storyboard=False).check()
        self.assertIn("05_storyboard.md", errors_of(rep))

    def test_blocking_every_number_makes_numbers_work(self):
        """把卡片内容全部换成不含数字，稿件里的数字立刻报错——证明检查确实在跑。"""
        rep = single_card_package("上海核心商圈租金大幅上涨，回本周期显著拉长",
                                  MS_LINE).check()
        self.assertIn("卡片库里没有的数字", errors_of(rep))


class TestFiles(unittest.TestCase):
    def test_missing_manuscript(self):
        rep = Fixture(**{"04_manuscript.md": None}).check()
        self.assertIn("缺少内容稿母版", errors_of(rep))

    def test_missing_cards(self):
        rep = Fixture(**{"02_info_cards.md": None}).check()
        self.assertIn("缺少信息卡片库", errors_of(rep))

    def test_split_card_files_are_merged(self):
        rep = Fixture(with_slides=False, with_storyboard=False,
                      **{"02_info_cards.md": "# 卡片库\n\n" + CARD_C001,
                         "02_info_cards_S02.md": CARD_C002}).check()
        self.assertEqual(errors_of(rep), "")
        self.assertEqual(rep.info["cards_total"], 2)


class TestCards(unittest.TestCase):
    def test_duplicate_id(self):
        rep = Fixture(**{"02_info_cards.md": CARDS_OK.replace("### C002", "### C001")}).check()
        self.assertIn("卡片 ID 重复", errors_of(rep))

    def test_invalid_grade(self):
        rep = Fixture(**{"02_info_cards.md": CARDS_OK.replace("价值：B", "价值：S")}).check()
        self.assertIn("价值等级非法", errors_of(rep))

    def test_empty_content(self):
        rep = Fixture(**{"02_info_cards.md": CARDS_OK.replace(
            "- 内容：两家试点店 6 个月复购率 41%", "- 内容：")}).check()
        self.assertIn("缺「内容」", errors_of(rep))

    def test_ab_card_without_sowhat_warns(self):
        rep = Fixture(**{"02_info_cards.md": CARDS_OK.replace("- 含义：留存验证通过\n", "")}).check()
        self.assertIn("没有「含义 So what」", warnings_of(rep))

    def test_missing_field_warns(self):
        rep = Fixture(**{"02_info_cards.md": CARDS_OK.replace("- 主题：成本\n", "")}).check()
        self.assertIn("缺字段「主题」", warnings_of(rep))

    def test_c_card_needs_no_sowhat(self):
        cards = CARDS_OK + "\n### C009\n\n- 类型：背景\n- 内容：行业通识\n- 来源：S03\n- 性质：事实\n- 可信度：中 ｜ 依据：报告\n- 价值：C\n- 主题：背景\n"
        rep = Fixture(with_slides=False, with_storyboard=False, **{"02_info_cards.md": cards}).check()
        self.assertNotIn("含义 So what", warnings_of(rep))


class TestCitations(unittest.TestCase):
    def test_dangling_reference(self):
        ms = MANUSCRIPT.replace("C001", "C099")
        rep = Fixture(with_slides=False, with_storyboard=False,
                      **{"04_manuscript.md": ms}).check()
        self.assertIn("悬空引用", errors_of(rep))

    def test_multi_card_citation_parses(self):
        self.assertEqual(parse_citations("增长 8.2%〔C012、C031｜S03-§2.1〕"),
                         [("C012", "S03-§2.1"), ("C031", "S03-§2.1")])

    def test_halfwidth_bar_accepted(self):
        self.assertEqual(parse_citations("〔C012|S03-p12〕"), [("C012", "S03-p12")])


class TestCoverage(unittest.TestCase):
    def _cards_with(self, *extra: str) -> str:
        return CARDS_OK + "\n" + "\n".join(extra)

    A_CARD = ("### C003\n\n- 类型：数据\n- 内容：苏州竞品门店 12 家\n- 含义：区域密度参考\n"
              "- 来源：S05-p3\n- 性质：事实\n- 可信度：中 ｜ 依据：旧 PPT\n- 价值：A\n- 主题：竞争\n")

    def test_a_card_without_placement_is_error(self):
        rep = Fixture(**{"02_info_cards.md": self._cards_with(self.A_CARD)}).check()
        self.assertIn("C003（A 级）没有任何去向", errors_of(rep))

    def test_b_card_without_placement_warns(self):
        slides = SLIDES_OK.replace("- 试点店 6 个月复购率 41%〔C002〕\n", "")
        slides = slides.replace("、C002（S01-表2）", "")
        self.assertNotIn("C002", slides, "夹具没清干净，测试会失真")
        rep = Fixture(**{"06_slides.md": slides}).check()
        self.assertIn("C002（B 级）没有任何去向", warnings_of(rep))

    def test_source_field_counts_as_placement(self):
        """卡片只出现在页面的「来源」字段里也算有去向——它确实被这一页用到了。"""
        rep = Fixture(with_slides=False, **{
            "04_manuscript.md": "# 标题\n\n## 执行摘要\n\n没有引用。\n",
            "04_manuscript_clean.md": "# 标题\n\n## 执行摘要\n\n没有引用。\n",
            "07_audit_report.md": AUDIT + "\n| C001 | A | 正文 §1 | 已用 |\n| C002 | B | 待定池 | 过时 |\n"}).check()
        self.assertEqual(errors_of(rep), "")

    def test_a_card_only_in_audit_is_error(self):
        empty = "# 标题\n\n## 执行摘要\n\n没有引用的正文。\n"
        audit = AUDIT + "\n| C001 | A | 待定 | 未进主线 |\n"
        rep = Fixture(with_slides=False, with_storyboard=False,
                      **{"07_audit_report.md": audit,
                         "04_manuscript.md": empty, "04_manuscript_clean.md": empty}).check()
        self.assertIn("只出现在审计报告里", errors_of(rep))

    def test_a_card_only_in_storyline_is_error(self):
        """结构树里挂了名、但正文与页面都没用上——这正是覆盖审计要抓的丢失。"""
        empty = "# 标题\n\n## 执行摘要\n\n没有引用的正文。\n"
        storyline = STORYLINE + "\n子论点 1.1：租金压力  ← C001（强）\n"
        rep = Fixture(with_slides=False, with_storyboard=False,
                      **{"03_storyline.md": storyline,
                         "04_manuscript.md": empty, "04_manuscript_clean.md": empty}).check()
        self.assertIn("只在故事线里挂了名", errors_of(rep))
        self.assertEqual(rep.info["coverage"]["planned_only"], 1)

    def test_a_card_on_backup_page_counts_as_placed(self):
        cards = self._cards_with(self.A_CARD)
        slides = SLIDES_OK + ("\n## P02 ｜ — ｜ 备用\n\n**行动标题**：苏州竞品密度如何\n\n"
                              "**正文**\n\n- 苏州竞品 12 家〔C003〕\n")
        rep = Fixture(**{"02_info_cards.md": cards, "06_slides.md": slides}).check()
        self.assertEqual(errors_of(rep), "")

    def test_storyboard_placement_counts(self):
        """卡片只出现在故事板（尚未写逐页内容）也算有去向。"""
        storyboard = STORYBOARD_OK + "\n| 9 | 二 | 备用 | 苏州密度 | C003 | §2.3 |\n"
        rep = Fixture(with_slides=False,
                      **{"02_info_cards.md": self._cards_with(self.A_CARD),
                         "05_storyboard.md": storyboard}).check()
        self.assertEqual(errors_of(rep), "")


class TestNumbers(unittest.TestCase):
    def test_unknown_number_is_error(self):
        rep = single_card_package(
            "上海核心商圈租金同比 +23%",
            "租金 +23%〔C001〕，渗透率为 37%。").check()
        self.assertIn("卡片库里没有的数字「37%」", errors_of(rep))

    def test_rounding_tolerated(self):
        rep = single_card_package("租金同比 +23.42%", "租金同比 +23.4%〔C001〕。").check()
        self.assertNotIn("卡片库里没有的数字", errors_of(rep))

    def test_unit_scaling_tolerated(self):
        rep = single_card_package("市场规模 1.2 万亿元", "市场规模 12000 亿元〔C001〕。").check()
        self.assertNotIn("卡片库里没有的数字", errors_of(rep))

    def test_judgment_number_downgrades_to_warning(self):
        rep = single_card_package("租金同比 +23%",
                                  "建议先开 8 家小店（依据 C001）〔C001〕。").check()
        self.assertEqual(errors_of(rep), "")
        self.assertIn("推断或建议类数字「8家」", warnings_of(rep))

    def test_wrong_card_cited_warns(self):
        rep = single_card_package("租金同比 +23%",
                                  "复购率 41% 高于成都 12 个百分点〔C001〕。",
                                  extra_card=CARD_C002).check()
        self.assertIn("不在所引卡片", warnings_of(rep))

    def test_card_ids_are_not_treated_as_data(self):
        self.assertEqual(extract_numbers("见 S03-p12 与 C018、S07-表2"), [])

    def test_clean_version_extra_number_is_error(self):
        rep = single_card_package("租金同比 +23%", "租金 +23%〔C001〕。",
                                  clean_line="租金 +23%，渗透率为 37%。").check()
        self.assertIn("清洁版出现母版没有的数字", errors_of(rep))

    def test_uncited_number_warns(self):
        ms = MANUSCRIPT + "\n上海核心商圈租金同比 +23%，压力显著。\n"
        rep = Fixture(with_slides=False, with_storyboard=False,
                      **{"04_manuscript.md": ms, "04_manuscript_clean.md": strip_citations(ms)}).check()
        self.assertIn("有数字但没有来源标注", warnings_of(rep))

    def test_appendix_numbers_not_flagged(self):
        ms = MANUSCRIPT + "\n## 附录 A · 详细数据\n\n租金 +23%，复购率 41%，客单价 32 元。\n"
        rep = Fixture(with_slides=False, with_storyboard=False,
                      **{"04_manuscript.md": ms, "04_manuscript_clean.md": strip_citations(ms)}).check()
        self.assertNotIn("附录", warnings_of(rep))

    def test_dates_do_not_need_citations(self):
        """「3 月董事会」「2026 年」是叙事脚手架，不该被要求标来源。"""
        ms = MANUSCRIPT + "\n2026 年 3 月的董事会已经定了方向，8 月的邮件又确认了一次。\n"
        rep = Fixture(with_slides=False, with_storyboard=False,
                      **{"04_manuscript.md": ms, "04_manuscript_clean.md": strip_citations(ms)}).check()
        self.assertNotIn("有数字但没有来源标注", warnings_of(rep))

    def test_judgment_line_needs_no_citation(self):
        ms = MANUSCRIPT + "\n建议把 2027 年的扩张上限设为 8 家。\n"
        rep = Fixture(with_slides=False, with_storyboard=False,
                      **{"04_manuscript.md": ms, "04_manuscript_clean.md": strip_citations(ms)}).check()
        self.assertNotIn("有数字但没有来源标注", warnings_of(rep))

    def test_fact_number_without_citation_still_warns(self):
        """日期与建议句之外，事实性数字没来源仍然要报。"""
        ms = MANUSCRIPT + "\n上海门店净利率为 -4.2%，租金占比 26.8%。\n"
        rep = Fixture(with_slides=False, with_storyboard=False,
                      **{"04_manuscript.md": ms, "04_manuscript_clean.md": strip_citations(ms)}).check()
        self.assertIn("有数字但没有来源标注", warnings_of(rep))

    def test_source_like_text_in_body_does_not_break_clean_check(self):
        """母版正文里出现形如 S03-p12 的写法时，两侧剥离对称，不报假错误。"""
        ms = MANUSCRIPT.replace("〔C001｜S07-p42〕", "〔C001｜S07-p42〕（见 S03-p12 附表）")
        rep = Fixture(with_slides=False, with_storyboard=False,
                      **{"04_manuscript.md": ms, "04_manuscript_clean.md": strip_citations(ms)}).check()
        self.assertNotIn("清洁版出现母版没有的数字", errors_of(rep))

    def test_no_numbers_skips_checks(self):
        rep = single_card_package("租金同比 +23%", "渗透率为 37%〔C001〕。").check(check_numbers=False)
        self.assertNotIn("37%", errors_of(rep))


class TestTitles(unittest.TestCase):
    def test_titles_parsed_in_page_order(self):
        slides = SLIDES_OK + SLIDES_OK.replace("P01", "P02")
        rep = Fixture(**{"06_slides.md": slides}).check()
        self.assertEqual([p for p, _ in rep.info["titles"]], ["P01", "P02"])

    def test_missing_titles_warns(self):
        rep = Fixture(**{"06_slides.md": "# 逐页\n\n没有标题字段\n"}).check()
        self.assertIn("没解析到行动标题", warnings_of(rep))

    def test_title_with_halfwidth_colon(self):
        self.assertEqual(parse_slide_titles("## P03 ｜ 一 ｜ 观点+证据\n\n**行动标题**: 租金压力上行\n"),
                         [("P03", "租金压力上行")])


class TestGradeCalibration(unittest.TestCase):
    """A 级是稀缺的：抽不掉主线就降 B。一批卡里全是 A，分级就失去区分度，
    覆盖审计「A 级 100% 有去向」也就变成废话。"""

    def _cards(self, n_a: int, n_b: int) -> str:
        out = ["# 卡片库"]
        for i in range(n_a + n_b):
            grade = "A" if i < n_a else "B"
            out.append(f"\n### C{i + 1:03d}\n\n- 类型：事实\n- 内容：第 {i + 1} 条测试信息\n"
                       f"- 含义：略\n- 来源：S01-p1\n- 性质：事实\n- 可信度：高 ｜ 依据：内部\n"
                       f"- 价值：{grade}\n- 主题：测试\n")
        return "".join(out)

    def test_a_ratio_over_40_percent_warns(self):
        rep = Fixture(with_slides=False, with_storyboard=False,
                      **{"02_info_cards.md": self._cards(15, 10)}).check()
        self.assertIn("分级已失去区分度", warnings_of(rep))

    def test_healthy_ratio_does_not_warn(self):
        rep = Fixture(with_slides=False, with_storyboard=False,
                      **{"02_info_cards.md": self._cards(5, 20)}).check()
        self.assertNotIn("分级已失去区分度", warnings_of(rep))

    def test_small_library_is_not_flagged(self):
        rep = Fixture(with_slides=False, with_storyboard=False,
                      **{"02_info_cards.md": self._cards(3, 2)}).check()
        self.assertNotIn("分级已失去区分度", warnings_of(rep))


class TestTemplateConsistency(unittest.TestCase):
    """卡片模板里的示例必须能被解析器读成 3 张结构完整的卡——模板是用户的抄写样板，
    示例本身不能违反规则（例如 A/B 级卡片不写「含义」）。"""

    def test_info_cards_template_parses(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            os.pardir, "assets", "info-cards-template.md")
        with open(path, encoding="utf-8") as fh:
            cards = parse_cards(fh.read(), "info-cards-template.md")

        self.assertEqual([c.cid for c in cards], ["C001", "C002", "C003", "C174"])
        self.assertEqual([c.grade for c in cards], ["A", "B", "A", "B"])
        for c in cards:
            self.assertTrue(c.fields.get("来源", "").strip(), f"{c.cid} 示例缺「来源」")
            self.assertTrue(c.fields.get("含义", "").strip(),
                            f"{c.cid} 是 {c.grade} 级却没写「含义」——模板会给用户做坏示范")

    def test_derived_card_example_follows_the_contract(self):
        """派生卡片示例必须带「性质=推断」与「派生自 …」的来源——这是它与材料卡片的分界。"""
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            os.pardir, "assets", "info-cards-template.md")
        with open(path, encoding="utf-8") as fh:
            cards = {c.cid: c for c in parse_cards(fh.read(), "t.md")}
        derived = cards["C174"]
        self.assertEqual(derived.fields["性质"], "推断")
        self.assertTrue(derived.fields["来源"].startswith("派生自"), derived.fields["来源"])
        self.assertTrue(re.search(r"[÷×+\-−=]", derived.fields["内容"]),
                        "派生卡片的「内容」栏要写算式，不能只给结论")


class TestParsers(unittest.TestCase):
    def test_multiline_content_is_joined(self):
        cards = parse_cards("### C007\n- 内容：第一行\n  第二行\n- 价值：A\n", "t.md")
        self.assertEqual(cards[0].fields["内容"], "第一行 第二行")
        self.assertEqual(cards[0].grade, "A")

    def test_text_before_first_card_is_ignored(self):
        self.assertEqual(parse_cards("# 卡片库\n\n说明文字\n\n## 一、卡片\n", "t.md"), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
