"""生成无外部依赖的阅读型 HTML；所有作者输入转义，图表为可访问的内嵌 SVG。"""
import html
import json
import math
import re
import unicodedata
import textwrap
from urllib.parse import urlsplit

from common import ROOT, CONTRACT, research_gate
from report_model import BASIS, KINDS, validate_content
from report_media import validate_media

COLORS = ["#007aff", "#5856d6", "#34a853", "#d87500", "#af52de", "#65758b"]


def esc(value):
    return html.escape(str(value), quote=True)


def rich(value):
    value = esc(value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", value)
    return re.sub(r"\[(E-\d+)\]", lambda m: f'<a class="citation" href="#ref-{m[1]}" aria-label="证据 {m[1]}">[{m[1]}]</a>', value)


def number(value):
    if value is None:
        return "未披露"
    return f"{value:,.4f}".rstrip("0").rstrip(".") if value % 1 else f"{value:,.0f}"


def citations(ids):
    return " ".join(rich(f"[{eid}]") for eid in ids)


def row_table(columns, rows):
    head = "".join(f'<th scope="col">{rich(col)}</th>' for col in columns)
    body = "".join("<tr>" + "".join(f"<td>{rich(cell)}</td>" for cell in row) + "</tr>" for row in rows)
    return f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def svg_chart(block, chart_id):
    points = block["points"]
    values = [p["value"] for p in points if p["value"] is not None]
    chart_type = block["chart_type"]
    width, height = 820, (90 + 52 * len(points) if chart_type == "bar" else 350)
    shapes = []
    text = lambda x, y, value, cls="axis-label", anchor="start": f'<text x="{x:.2f}" y="{y:.2f}" class="{cls}" text-anchor="{anchor}">{esc(value)}</text>'
    def wrapped_label(x, y, value, limit=20):
        lines, line, units = [], "", 0
        for char in value:
            size = 2 if unicodedata.east_asian_width(char) in ("W", "F") else 1
            if units + size > limit:
                lines.append(line)
                line, units = "", 0
            line += char
            units += size
        lines.append(line)
        if value.isascii():
            lines = textwrap.wrap(value, width=limit) or [value]
        return "".join(text(x, y + (i-(len(lines)-1)/2)*17, line, anchor="end") for i, line in enumerate(lines))
    kind_of = lambda p: p.get("kind", block["kind"])
    # 刻度采用易读间隔，同时保留零基线和原始精确值标签。
    low, high = min(0, min(values)), max(0, max(values))
    raw_step = (high-low)/4 or 1
    magnitude = 10 ** math.floor(math.log10(raw_step))
    step = next(s * magnitude for s in (1, 2, 2.5, 3, 5, 10) if s*magnitude >= raw_step)
    low, high = math.floor(low/step)*step, math.ceil(high/step)*step
    if low == high:
        high += step
    ticks = [low + i*step for i in range(round((high-low)/step)+1)]
    if chart_type == "bar":
        left, right = 174, 702
        span = high - low or 1
        scale = lambda n: left + (n - low) / span * (right - left)
        zero = scale(0)
        for value in ticks:
            x = scale(value)
            shapes.append(f'<line x1="{x}" y1="20" x2="{x}" y2="{height-40}" class="grid-line"/>')
            shapes.append(text(x, height - 14, number(value), anchor="middle"))
        shapes.append(f'<line x1="{zero}" y1="20" x2="{zero}" y2="{height-40}" class="zero-line"/>')
        for i, p in enumerate(points):
            y = 35 + i * 52
            shapes.append(wrapped_label(left - 18, y + 20, p["label"]))
            value = p["value"]
            if value is None:
                shapes.append(text(zero + 9, y + 20, "未披露"))
                continue
            x = scale(value)
            future = kind_of(p) == "forecast"
            color = COLORS[i % len(COLORS)] if block["kind"] != "mixed" else COLORS[0]
            shapes.append(f'<rect x="{min(x,zero)}" y="{y}" width="{abs(x-zero)}" height="30" rx="5" fill="{color}" fill-opacity="{".35" if future else ".9"}" stroke="{color}" stroke-dasharray="{"5 4" if future else "none"}"><title>{esc(p["label"])}：{number(value)} {esc(block["unit"])}；{KINDS[kind_of(p)]}</title></rect>')
            label = number(value) + (" 预测" if future else "")
            shapes.append(text(x + 9 if value >= 0 else zero + 9, y + 21, label, "value-label"))
    elif chart_type == "line":
        left, right, top, bottom = 78, 748, 44, 270
        span = high - low or 1
        sx = lambda i: left + i * (right - left) / (len(points) - 1)
        sy = lambda v: bottom - (v - low) * (bottom - top) / span
        for v in ticks:
            y = sy(v)
            shapes.append(f'<line x1="{left}" y1="{y}" x2="{right}" y2="{y}" class="grid-line"/>')
            shapes.append(text(left - 12, y + 5, number(v), anchor="end"))
        previous = None
        for i, p in enumerate(points):
            x, value = sx(i), p["value"]
            shapes.append(text(x, 310 + (18 if i % 2 else 0), p["label"], anchor="middle"))
            if value is None:
                shapes.append(text(x, bottom - 10, "未披露", anchor="middle"))
                previous = None
                continue
            y = sy(value)
            if previous:
                px, py, pk = previous
                dashed = kind_of(p) == "forecast" or pk == "forecast"
                shapes.append(f'<line x1="{px}" y1="{py}" x2="{x}" y2="{y}" stroke="{COLORS[0]}" stroke-width="3" stroke-dasharray="{"7 5" if dashed else "none"}"/>')
            shapes.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{"white" if kind_of(p) == "forecast" else COLORS[0]}" stroke="{COLORS[0]}" stroke-width="2"><title>{esc(p["label"])}：{number(value)}；{KINDS[kind_of(p)]}</title></circle>')
            shapes.append(text(x, y - 16, number(value) + (" 预测" if kind_of(p) == "forecast" else ""), "value-label", "middle"))
            previous = (x, y, kind_of(p))
    else:
        total = sum(values)
        radius, circumference, offset = 95, 2 * math.pi * 95, 0
        for i, p in enumerate(points):
            length = p["value"] / total * circumference
            color = COLORS[i % len(COLORS)]
            shapes.append(f'<circle cx="220" cy="175" r="{radius}" fill="none" stroke="{color}" stroke-width="36" stroke-dasharray="{length} {circumference-length}" stroke-dashoffset="{-offset}" transform="rotate(-90 220 175)"><title>{esc(p["label"])}：{number(p["value"])} {esc(block["unit"])}</title></circle>')
            y = 74 + i * 39
            shapes.append(f'<rect x="410" y="{y-12}" width="11" height="11" rx="3" fill="{color}"/>')
            shapes.append(text(433, y, p["label"]))
            shapes.append(text(745, y, f'{number(p["value"])} · {p["value"]/total:.1%}', "value-label", "end"))
            offset += length
        shapes.append(text(220, 172, number(total), "donut-total", "middle"))
        shapes.append(text(220, 200, block["unit"], anchor="middle"))
    title = f'<title id="{chart_id}-title">{esc(block["title"])}</title>'
    desc = f'<desc id="{chart_id}-desc">{esc(block["note"])}。详细数值见下方数据表。</desc>'
    return f'<svg viewBox="0 0 {width} {height}" role="img" aria-labelledby="{chart_id}-title {chart_id}-desc">{title}{desc}{"".join(shapes)}</svg>'


def render(content, cfg, data, audit_name, media=None):
    result = validate_content(content, cfg, data)
    media = validate_media(content, {} if media is None else media)
    entities = {r["entity_id"]: r["legal_name"] for r in data["entity-map"]}
    entities["industry"] = "行业口径"
    evidence = {r["evidence_id"]: r for r in data["evidence-ledger"]}
    sources = {r["source_id"]: r for r in data["source-register"]}
    chart_number = 0

    def source_line(ids):
        if not ids:
            return ""
        publishers = list(dict.fromkeys(sources[evidence[eid]["source_id"]]["publisher"] for eid in ids))
        return f'<div class="source-line">来源：{esc(" / ".join(publishers))} {citations(ids)}</div>'

    def block_html(block):
        nonlocal chart_number
        kind = block["type"]
        if kind == "explanation":
            paragraphs = "".join(f'<p class="prose">{rich(p)}</p>' for p in block["text"].split("\n\n"))
            limits = f'<p class="explanation-limit">{rich(block["limitations"])}</p>' if block["limitations"] else ""
            uncited = [eid for eid in block["evidence_ids"] if f"[{eid}]" not in block["text"] + block["limitations"]]
            return f'<div class="explanation" id="topic-{block["topic"]}"><h3>{rich(block["title"])}</h3>{paragraphs}{source_line(uncited)}{limits}</div>'
        if kind == "image":
            asset = media[block["path"]]
            src = f'data:{asset["mime"]};base64,{asset["data"]}'
            origin = f'<a href="{esc(block["source_url"])}" target="_blank" rel="noopener noreferrer">图片来源 ↗</a>' if block["source_url"] else '本地材料 · 来源见证据'
            return f'<figure class="company-image image-{block["role"]}"><h3>{rich(block["title"])}</h3><img src="{src}" alt="{esc(block["alt"])}" loading="lazy" decoding="async"><figcaption><p>{rich(block["caption"])}</p><p class="image-credit">{origin} · 取得于 {esc(block["captured_at"])} · {rich(block["usage_note"])}</p>{source_line(block["evidence_ids"])}</figcaption></figure>'
        if kind == "people":
            profiles = []
            for person in block["profiles"]:
                limit = f'<p class="explanation-limit">{rich(person["limitations"])}</p>' if person["limitations"] else ""
                profiles.append(f'<article class="person"><h4>{rich(person["name"])}</h4><p class="person-role">{rich(person["role"])} · {rich(person["period"])}</p><p>{rich(person["background"])}</p><p>{rich(person["contribution"])}</p>{limit}{source_line(person["evidence_ids"])}</article>')
            return f'<div class="people"><h3>{rich(block["title"])}</h3><div class="people-grid">{"".join(profiles)}</div></div>'
        if kind == "matrix":
            heads = "".join(f'<th scope="col">{rich(label)}</th>' for label in block["columns"])
            rows = []
            for row in block["rows"]:
                cells = []
                for cell in row["cells"]:
                    cells.append(f'<td class="basis-{cell["basis"]}"><p>{rich(cell["text"])}</p><small>{BASIS[cell["basis"]]} {citations(cell["evidence_ids"])}</small></td>')
                rows.append(f'<tr><th scope="row">{rich(row["label"])}</th>{"".join(cells)}</tr>')
            return f'<figure class="comparison-matrix"><figcaption><h3>{rich(block["title"])}</h3></figcaption><div class="table-wrap" tabindex="0" role="region" aria-label="比较矩阵，可横向滚动"><table><thead><tr><th scope="col">比较维度</th>{heads}</tr></thead><tbody>{"".join(rows)}</tbody></table></div><p class="chart-note">{rich(block["note"])}</p></figure>'
        if kind == "text":
            return "".join(f'<p class="prose">{rich(p)}</p>' for p in block["text"].split("\n\n"))
        if kind == "bullets":
            return '<ul class="prose">' + "".join(f"<li>{rich(t)}</li>" for t in block["items"]) + "</ul>"
        if kind == "callout":
            return f'<aside class="callout"><h3>{rich(block["title"])}</h3><p>{rich(block["text"])}</p></aside>'
        if kind == "table":
            return f'<div class="report-table"><h3>{rich(block["title"])}</h3>{row_table(block["columns"],block["rows"])}<p class="chart-note">{rich(block["note"])}</p></div>'
        if kind == "metrics":
            cards = []
            for m in block["items"]:
                cards.append(f'<article class="metric"><p class="metric-label">{rich(m["label"])}</p><p class="metric-value">{number(m["value"])}<span>{esc(m["unit"])}</span></p><p class="metric-note">{esc(m["period"])} · {esc(entities[m["entity_id"]])} · {KINDS[m["kind"]]}<br>{rich(m["note"])}</p>{source_line(m["evidence_ids"])}</article>')
            return f'<div class="metric-grid">{"".join(cards)}</div>'
        if kind == "chart":
            chart_number += 1
            cid = f"chart-{chart_number}"
            rows = [[p["label"], number(p["value"]), block["unit"], p.get("period",block["period"]), KINDS[p.get("kind",block["kind"])], " ".join(f"[{eid}]" for eid in p.get("evidence_ids",block["evidence_ids"]))] for p in block["points"]]
            meta = f'{block["unit"]} · {block["period"]} · {entities[block["entity_id"]]} · {KINDS[block["kind"]]}'
            return f'<figure class="chart" id="{cid}"><figcaption><span class="figure-number">图 {chart_number:02d}</span><h3>{rich(block["title"])}</h3><p class="chart-meta">{esc(meta)}</p></figcaption><div class="chart-plot" tabindex="0" role="region" aria-label="图表，可横向滚动">{svg_chart(block,cid)}</div><p class="chart-note">{rich(block["note"])}</p>{source_line(block["evidence_ids"])}<details class="data-table"><summary>查看图表数据与口径</summary>{row_table(["项目","数值","单位","期间","属性","证据"],rows)}</details></figure>'
        if kind in ("timeline", "process"):
            items = []
            for item in block["items"]:
                date = f'<p class="date">{esc(item["date"])}{" · 计划" if item["status"] == "planned" else ""}</p>' if kind == "timeline" else ""
                basis = item.get("basis")
                tag = f'<span class="flow-basis basis-{basis}">{BASIS[basis]}</span>' if basis else ""
                items.append(f'<article class="status-{item.get("status","completed")}{" basis-"+basis if basis else ""}">{date}{tag}<h4>{rich(item["title"])}</h4><p>{rich(item["text"])}</p>{source_line(item["evidence_ids"])}</article>')
            flow_class = " business-flow" if block.get("purpose") == "business_model" else ""
            conceptual = kind == "process" and block.get("ordering") == "conceptual"
            if conceptual:
                flow_class += " conceptual-flow"
            note = '<p class="chart-note">经营环节关联示意；排列不表示已经核实的执行顺序。</p>' if conceptual else ""
            wrapper = "visual-story business-visual" if block.get("purpose") == "business_model" else "visual-story"
            return f'<div class="{wrapper}"><h3>{rich(block["title"])}</h3>{note}<div class="{kind}{flow_class}">{"".join(items)}</div></div>'
        raise AssertionError(kind)

    nav = ['<a href="#overview">报告概览</a>']
    sections = []
    for n, section in enumerate(content["sections"], 1):
        nav.append(f'<a href="#{section["id"]}"><span>{n:02d}</span>{esc(section["title"])}</a>')
        summary = f'<p class="section-summary">{rich(section["summary"])}</p>' if section.get("summary") else ""
        sections.append(f'<section class="report-section" id="{section["id"]}"><div class="section-number">{n:02d}</div><h2>{esc(section["title"])}</h2>{summary}{"".join(block_html(b) for b in section["blocks"])}</section>')
    refs = []
    for eid in result["used_evidence"]:
        record = evidence[eid]
        source = sources[record["source_id"]]
        url = source["locator"] or ""
        parsed = urlsplit(url)
        link = f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(source["title"])}</a>' if parsed.scheme in ("http","https") and parsed.netloc and not parsed.username else esc(source["title"])
        refs.append(f'<li id="ref-{eid}"><strong>{esc(eid)}</strong> · {link}<p>{esc(source["publisher"])} · {esc(source["published_date"] or "日期未载")} · {esc(record["locator"] or "")}</p><p class="source-limit">{esc(record["limitations"] or "具体支持范围以原件为准。")}</p></li>')
    gate = research_gate(cfg, data)
    scope = rich(content["scope_note"])
    if gate not in ("complete", "not_applicable"):
        scope += " 最新相关研报尚未取得或读完，结论限于现有材料。"
    status = {"draft":"草稿", "limited":"公开材料研究 · 结论有条件", "complete":"研究报告"}[cfg["report_status"]]
    purpose = CONTRACT["scoring"]["purposes"][cfg["purpose"]]["label"] if cfg["purpose"] else "目的待确认"
    css = (ROOT / "assets/report.css").read_text(encoding="utf-8")
    js = (ROOT / "assets/report.js").read_text(encoding="utf-8")
    snapshot = {k: cfg[k] for k in ("target_id", "as_of_date", "purpose", "report_status")}
    envelope = {"content":content,"project":snapshot,"audit_file":audit_name}
    if content["version"] == "1.2":
        envelope["media"] = media
    payload = json.dumps(envelope, ensure_ascii=False,allow_nan=False).replace("<","\\u003c").replace(">","\\u003e").replace("&","\\u0026")
    document = f'''<!doctype html>
<html lang="{content["language"]}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light"><title>{esc(content["title"])}</title><style>{css}</style></head>
<body><a class="skip-link" href="#main">跳转正文</a>
<header class="topbar"><a class="brand" href="#overview"><span class="brand-mark">Z</span> ZEROX <span class="brand-detail">/ RESEARCH</span></a><div class="top-actions"><span>{esc(cfg["as_of_date"])}</span><button type="button" id="toc-toggle" aria-expanded="false" aria-controls="toc">目录</button><button type="button" class="print-button">打印 / PDF</button></div></header>
<div class="layout"><aside class="sidebar" id="toc"><div class="sidebar-label">CONTENTS <span>报告目录</span></div><nav aria-label="报告目录">{"".join(nav)}<a href="#sources">来源与底稿</a></nav><div class="sidebar-foot">{esc(purpose)}<br>{esc(cfg["confidentiality"])}</div></aside>
<main id="main"><header class="hero" id="overview"><p class="eyebrow">ZEROX DUE DILIGENCE / {esc(purpose)}</p><h1>{rich(content["title"])}</h1><p class="subtitle">{rich(content["subtitle"])}</p><div class="meta"><span>{esc(cfg["as_of_date"])}</span><span>{esc(status)}</span></div><p class="lead">{rich(content["summary"])}</p><p class="scope-note">{scope}</p></header>
{"".join(sections)}
<section class="references report-section" id="sources"><div class="section-number">REFERENCE</div><h2>来源与底稿</h2><p class="prose">正文引用可展开到具体出处。研究过程、完整核验台账和补充资料请求保存在独立底稿。</p><a class="audit-link" href="{esc(audit_name)}">打开完整核验底稿 ↗</a><details id="evidence"><summary>参考来源 · {len(refs)} 条证据</summary><ol class="sources">{"".join(refs)}</ol></details></section>
<footer>ZEROX RESEARCH <span>{esc(content["title"])} · {esc(cfg["as_of_date"])}</span></footer></main></div>
<script type="application/json" id="report-data">{payload}</script><script>{js}</script></body></html>'''
    return document, result
