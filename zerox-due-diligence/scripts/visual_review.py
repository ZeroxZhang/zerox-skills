"""按章提供可视化编辑线索；不验证事实、可比性或实际渲染效果。"""
import math
import re


ANALYTICAL_BLOCKS = {"chart", "diagram", "process", "timeline", "matrix"}
PROSE_BLOCKS = {"explanation", "text", "bullets", "callout"}
COUNT_KEYS = (
    "quantitative_charts", "data_points", "known_data_points", "numeric_values",
    "metric_blocks", "metric_items", "diagram_blocks", "process_blocks",
    "timeline_blocks", "matrix_blocks", "images", "people_blocks",
    "people_profiles", "tables", "explanations", "text_blocks",
)
MEANING = (
    "仅为编辑线索，不是事实、可比性、解释充分性或视觉效果认证；"
    "不要求固定图数或图型。未知数据不能补零或造图，已有文字和关系仍可酌情提炼。"
)


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _clean_text(text):
    """移除引用、网址和日期，避免把编号与资料时点当作经营数字。"""
    text = re.sub(r"\[[^\]\n]*\]", " ", text)
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"(?<![A-Za-z0-9])(?:E|S|ENT|C|G|R)-\d+(?!\d)", " ", text)
    text = re.sub(r"(?<!\d)(?:19|20)\d{2}[-/.]\d{1,2}(?:[-/.]\d{1,2})?(?!\d)", " ", text)
    text = re.sub(r"(?:19|20)\d{2}\s*年(?:\s*\d{1,2}\s*月(?:\s*\d{1,2}\s*日)?)?", " ", text)
    text = re.sub(r"(?<![A-Za-z0-9])(?:19|20)\d{2}(?![A-Za-z0-9])", " ", text)
    text = re.sub(r"(?m)^\s*(?:\d+[.)、]|[-*])\s*", "", text)
    return text


def _prose(block):
    kind = block.get("type")
    if kind == "bullets":
        return "\n".join(block.get("items", []))
    if kind in PROSE_BLOCKS:
        return "\n".join(str(block.get(key, "")) for key in ("text", "limitations"))
    return ""


def _length(text):
    clean = _clean_text(text)
    return {
        "chinese_characters": len(re.findall(r"[\u3400-\u4dbf\u4e00-\u9fff]", clean)),
        "english_words": len(re.findall(r"\b[A-Za-z]+(?:['’-][A-Za-z]+)*\b", clean)),
    }


def _number_tokens(text):
    # 数字只是人工复核入口，不推断它们属于同一主体、单位或期间。
    return re.findall(r"(?<![A-Za-z0-9_-])[-+]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?", _clean_text(text))


def _chart_counts(block):
    points = block.get("points", [])
    known, values = 0, 0
    for point in points:
        if block.get("chart_type") == "range":
            found = sum(_is_number(point.get(key)) for key in ("low", "high"))
        elif block.get("chart_type") == "stacked_bar":
            found = sum(_is_number(segment.get("value")) for segment in point.get("segments", []))
        else:
            found = int(_is_number(point.get("value")))
        known += found > 0
        values += found
    return len(points), known, values


def review_visuals(content):
    """返回纯 JSON 可序列化结果；只读取内容，不要求版本或修改输入。"""
    rows, global_findings = [], []
    total = {key: 0 for key in COUNT_KEYS}
    all_chart_types = set()
    for section in content.get("sections", []):
        blocks = section.get("blocks", [])
        counts = {key: 0 for key in COUNT_KEYS}
        topics = []
        topic_states = {}
        chart_types = set()
        findings = []
        longest = {"chinese_characters": 0, "english_words": 0}
        run = ""
        numeric_prose = []
        pre_visual_explanations = 0
        seen_analysis = False
        dense_tables = 0

        def finding(code, message):
            findings.append({"code": code, "message": message})

        def finish_run():
            nonlocal run
            size = _length(run)
            for key in longest:
                longest[key] = max(longest[key], size[key])
            run = ""

        for block in blocks:
            kind = block.get("type")
            if kind in PROSE_BLOCKS:
                run += "\n" + _prose(block)
                # 全未知解释中的“缺多少、缺哪年”不构成可绘数据。
                if not (kind == "explanation" and block.get("status") == "unknown"):
                    numeric_prose.extend(_number_tokens(_prose(block)))
            else:
                finish_run()
            if kind == "explanation":
                counts["explanations"] += 1
                topic = block.get("topic", "")
                if topic:
                    topics.append(topic)
                    topic_states[topic] = block.get("status")
                if not seen_analysis and block.get("status") != "unknown":
                    pre_visual_explanations += 1
            if kind == "text":
                counts["text_blocks"] += 1
            if kind in ANALYTICAL_BLOCKS:
                seen_analysis = True
            if kind == "chart":
                counts["quantitative_charts"] += 1
                if block.get("chart_type"):
                    chart_types.add(block["chart_type"])
                point_count, known_count, value_count = _chart_counts(block)
                counts["data_points"] += point_count
                counts["known_data_points"] += known_count
                counts["numeric_values"] += value_count
            elif kind == "metrics":
                counts["metric_blocks"] += 1
                counts["metric_items"] += len(block.get("items", []))
            elif kind in {"diagram", "process", "timeline", "matrix"}:
                counts[kind + "_blocks"] += 1
            elif kind == "image":
                counts["images"] += 1
            elif kind == "people":
                counts["people_blocks"] += 1
                counts["people_profiles"] += len(block.get("profiles", []))
            elif kind == "table":
                counts["tables"] += 1
                table_rows = block.get("rows", [])
                cells = [str(cell) for row in table_rows for cell in row]
                if len(table_rows) >= 5 or len(cells) >= 16 or sum(map(len, cells)) >= 450:
                    dense_tables += 1
        finish_run()
        analytic_count = sum(counts[key] for key in (
            "quantitative_charts", "diagram_blocks", "process_blocks", "timeline_blocks", "matrix_blocks"
        ))
        if longest["chinese_characters"] >= 600 or longest["english_words"] >= 120:
            finding(
                "long_prose_run",
                "连续正文达到至少600个中文字符或120个英文词。压缩重复说明，"
                "并检查其中已有的比较、关系或步骤能否前移为主视觉；未知内容可直接简写，无需补造图。",
            )
        if pre_visual_explanations >= 3:
            finding(
                "late_analytical_visual",
                f"首个分析图前已有{pre_visual_explanations}个非全未知解释块"
                + ("（本章尚无分析图）" if not analytic_count else "")
                + "。考虑在必要的短介绍后前移最能解释本章问题的图；图片、人物卡和大数字卡不能代替关系或比较。",
            )
        missing_topic_visual = False
        for topic, label, appropriate in (
            ("financial_performance", "财务表现", ("quantitative_charts", "matrix_blocks")),
            ("marketing", "营销", ("quantitative_charts", "diagram_blocks", "process_blocks", "timeline_blocks", "matrix_blocks")),
            ("competition", "竞争", ("quantitative_charts", "diagram_blocks", "matrix_blocks")),
        ):
            if topic in topic_states and topic_states[topic] != "unknown" and not any(counts[key] for key in appropriate):
                action = {
                    "financial_performance": "核查营收、结构及利润数据能否分别图示；仅有异口径材料时可先做口径矩阵，单值可保留指标卡。",
                    "marketing": "将已有渠道、内容、购买触点或活动关系提炼为结构图；没有转化数据时不要画按比例收窄的漏斗。",
                    "competition": "将已查明的竞品与可比维度提炼为矩阵或比较图，未核实格明确保留未知，不能补造评分。",
                }[topic]
                finding("topic_without_analytical_visual", f"{label}主题已有部分材料，但未见对应分析图。{action}")
                missing_topic_visual = True
        if len(numeric_prose) >= 3 and not counts["known_data_points"] and not missing_topic_visual:
            finding(
                "numbers_only_in_prose",
                f"正文剔除引用和日期后仍有{len(numeric_prose)}个数字线索，尚无含数值的定量图。"
                "逐项判断可比性：可比数字转图，单值用指标卡，异口径或方法编号保留文字；该提示不证明存在可绘数据。",
            )
        if dense_tables and not analytic_count:
            finding(
                "dense_table_without_synthesis",
                f"本章有{dense_tables}张较密的文字表且未见分析图。先提炼表中最影响判断的比较或关系，"
                "再决定是否转图、压缩表格或把明细移入附录；无需把无规律资料强行图示。",
            )
        rows.append({
            "section_id": section.get("id", ""),
            "title": section.get("title", ""),
            "topics": topics,
            "chart_types": sorted(chart_types),
            "counts": counts,
            "signals": {
                "longest_prose_run": longest,
                "explanations_before_first_analytical_visual": pre_visual_explanations,
                "numeric_tokens_in_prose": len(numeric_prose),
            },
            "findings": findings,
        })
        for key in total:
            total[key] += counts[key]
        all_chart_types.update(chart_types)
    if total["quantitative_charts"] >= 3 and len(all_chart_types) == 1:
        global_findings.append({
            "code": "single_chart_type",
            "message": "全稿至少3张定量图均使用同一图型。检查变化、构成、区间与比较是否各用了合适表达；"
                       "若确实都回答同类问题可保留，不为多样性更换图型。",
        })
    warnings = [
        f"可视化编辑复核｜{row['title']}（{row['section_id']}）：{item['message']}"
        for row in rows for item in row["findings"]
    ] + [f"可视化编辑复核｜全稿：{item['message']}" for item in global_findings]
    return {
        "version": "1.0",
        "meaning": MEANING,
        "rows": rows,
        "summary": {
            "section_count": len(rows),
            "counts": total,
            "chart_types": sorted(all_chart_types),
            "finding_count": len(warnings),
            "counting_note": (
                "data_points按图的points项目计；区间的一对端点算一项，堆叠的一组算一项。"
                "known_data_points含至少一个有限数值；numeric_values按标量计，区间两端各计一个、堆叠各段各计一个。"
                "指标卡、图片、人物及结构图单独统计，不计入定量图或图中数值。"
            ),
        },
        "findings": global_findings,
        "warnings": warnings,
    }
