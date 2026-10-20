"""扩展的离线 SVG 图表与关系图；保留真实数值、口径和可访问文本。"""
import html
import math
import unicodedata
from decimal import Decimal, localcontext

from report_model import BASIS, KINDS

COLORS = ["#007aff", "#5856d6", "#248a3d", "#d87500", "#af52de", "#65758b"]
FLOWS = {"product": ("产品 / 服务", "#007aff"), "money": ("资金", "#248a3d"),
         "information": ("信息", "#5856d6"), "relationship": ("关系", "#65758b")}
ROLES = {"start": "起点", "delta": "变动", "total": "合计"}


def esc(value):
    return html.escape(str(value), quote=True)


def number(value):
    if value is None:
        return "未披露"
    if isinstance(value, int):
        return format(value, ",d")
    if isinstance(value, Decimal):
        if value == value.to_integral_value():
            return format(value, ",.0f")
        return format(value, ",f").rstrip("0").rstrip(".")
    return f"{value:,}" if value % 1 else f"{value:,.0f}"


def axis_number(value):
    """刻度为派生量，保留四位有效数字；原始值标签和数据表不使用此格式。"""
    compact = format(value, ".4g")
    return compact if "e" in compact.lower() else number(Decimal(compact))


def decimal_sum(values):
    # 支持有限双精度范围两端的数值相加，避免大整数差额或小数增量被舍入。
    with localcontext() as arithmetic:
        arithmetic.prec = 700
        return sum((Decimal(str(value)) for value in values), Decimal(0))


def lines(value, limit=24):
    """按视觉字符宽度换行，不截断长中文或连续网址。"""
    result, line, size = [], "", 0
    for char in str(value):
        width = 2 if unicodedata.east_asian_width(char) in ("W", "F") else 1
        if char == "\n" or (line and size + width > limit):
            result.append(line)
            line, size = "", 0
        if char != "\n":
            line += char
            size += width
    if line or not result:
        result.append(line)
    return result


def text(x, y, value, cls="axis-label", anchor="start"):
    return f'<text x="{x:.2f}" y="{y:.2f}" class="{cls}" text-anchor="{anchor}">{esc(value)}</text>'


def wrapped(x, y, value, limit=24, cls="axis-label", anchor="start", step=18):
    return "".join(text(x, y + index * step, line, cls, anchor)
                   for index, line in enumerate(lines(value, limit)))


def frame(block, identity, width, height, shapes, description):
    sizing = f' style="--plot-min-width:{width}px"' if block.get("chart_type") in ("column", "waterfall") and width > 820 else ""
    return (f'<svg viewBox="0 0 {width} {height}"{sizing} role="img" aria-labelledby="{identity}-title {identity}-desc">'
            f'<title id="{identity}-title">{esc(block["title"])}</title>'
            f'<desc id="{identity}-desc">{esc(description)}。{esc(block["note"])}。原始数据与依据见下方。</desc>'
            + "".join(shapes) + '</svg>')


def bounds(values, zero=True):
    low, high = min(values), max(values)
    if zero:
        low, high = min(low, 0), max(high, 0)
    if low == high:
        high = low + max(abs(low) * .1, 1)
    return low, high


def suffix(point, block):
    kind = point.get("kind", block["kind"])
    return "" if kind == "actual" else " · " + KINDS[kind]


def point_style(point, block, color):
    forecast = point.get("kind", block["kind"]) == "forecast"
    return f'fill="{color}" fill-opacity="{".3" if forecast else ".88"}" stroke="{color}" stroke-dasharray="{"5 4" if forecast else "none"}"'


def horizontal_axis(shapes, low, high, left, right, top, bottom):
    scale = lambda value: float(left + (value - low) / (high - low) * (right - left))
    for index in range(5):
        value = low + (high - low) * index / 4
        x = scale(value)
        shapes.append(f'<line x1="{x}" y1="{top}" x2="{x}" y2="{bottom}" class="grid-line"/>')
        shapes.append(text(x, bottom + 23, axis_number(value), anchor="middle"))
    return scale


def range_chart(block, identity):
    points, shapes = block["points"], []
    row_heights = [max(74, 20 + 18 * len(lines(p["label"], 20))) for p in points]
    bottom = 24 + sum(row_heights)
    values = [p[k] for p in points for k in ("low", "high") if p[k] is not None]
    low, high = bounds(values)
    scale = horizontal_axis(shapes, low, high, 175, 625, 18, bottom)
    y = 24
    for point, row_height in zip(points, row_heights):
        middle = y + row_height / 2
        wrapped_y = middle - (len(lines(point["label"], 20)) - 1) * 9
        shapes.append(wrapped(154, wrapped_y, point["label"], 20, anchor="end"))
        if point["low"] is None:
            shapes.append(text(190, middle, "区间未披露"))
        else:
            x1, x2 = scale(point["low"]), scale(point["high"])
            dashed = "5 4" if point.get("kind", block["kind"]) == "forecast" else "none"
            shapes.append(f'<line x1="{x1}" y1="{middle-5}" x2="{x2}" y2="{middle-5}" stroke="{COLORS[0]}" stroke-width="7" stroke-linecap="round" stroke-dasharray="{dashed}"/>')
            for x in (x1, x2):
                shapes.append(f'<circle cx="{x}" cy="{middle-5}" r="5" fill="white" stroke="{COLORS[0]}" stroke-width="2"/>')
            shapes.append(text(650, middle, f'{number(point["low"])}–{number(point["high"])}', "value-label"))
            if suffix(point, block):
                shapes.append(text(650, middle + 19, suffix(point, block).lstrip(" ·")))
        y += row_height
    return frame(block, identity, 820, bottom + 48, shapes, "区间上下界；未绘制无依据的中点，缺失区间留空")


def proportion_chart(block, identity):
    shapes, points = [], block["points"]
    heights = [max(78, 30 + len(lines(p["label"], 20)) * 18) for p in points]
    bottom = 28 + sum(heights)
    left, right = 180, 650
    scale = lambda value: left + value / block["scale_max"] * (right - left)
    shapes.extend((text(left, bottom + 16, "0"), text(right, bottom + 16, number(block["scale_max"]), anchor="end")))
    y = 28
    for point, row_height in zip(points, heights):
        middle = y + row_height / 2
        shapes.append(wrapped(160, middle - (len(lines(point["label"], 20)) - 1) * 9, point["label"], 20, anchor="end"))
        if point["value"] is None:
            shapes.append(text(left, middle, "未披露"))
        else:
            shapes.append(f'<rect x="{left}" y="{middle-20}" width="{right-left}" height="26" rx="5" fill="#eef1f5"/>')
            shapes.append(f'<rect x="{left}" y="{middle-20}" width="{scale(point["value"])-left}" height="26" rx="5" {point_style(point,block,COLORS[0])}/>')
            shapes.append(text(672, middle, number(point["value"]), "value-label"))
            if suffix(point, block):
                shapes.append(text(left, middle + 25, suffix(point, block).lstrip(" ·")))
        y += row_height
    shapes.append(text(left, bottom + 39, "灰色轨道仅为量尺，不代表另一类别或未列人群。"))
    return frame(block, identity, 820, bottom + 62, shapes, "单值比例按明确量尺展示；不计算或命名互补类别")


def column_chart(block, identity):
    points, shapes = block["points"], []
    width = max(820, 100 + 80 * len(points))
    left, right, top, bottom = 75, width - 30, 50, 290
    low, high = bounds([p["value"] for p in points if p["value"] is not None])
    sy = lambda value: float(bottom - (value - low) / (high - low) * (bottom - top))
    for index in range(5):
        value = low + (high - low) * index / 4
        y = sy(value)
        shapes.append(f'<line x1="{left}" y1="{y}" x2="{right}" y2="{y}" class="grid-line"/>')
        shapes.append(text(left - 12, y + 5, axis_number(value), anchor="end"))
    zero = sy(0)
    shapes.append(f'<line x1="{left}" y1="{zero}" x2="{right}" y2="{zero}" class="zero-line"/>')
    step, bar_width = (right-left) / len(points), min(58, (right-left) / len(points) * .65)
    for index, point in enumerate(points):
        x = left + (index+.5)*step
        value = point["value"]
        if value is None:
            shapes.append(text(x, bottom-12, "未披露", anchor="middle"))
        else:
            end = sy(value)
            shapes.append(f'<rect x="{x-bar_width/2}" y="{min(zero,end)}" width="{bar_width}" height="{max(abs(zero-end),1)}" rx="3" {point_style(point,block,COLORS[0])}/>')
            shapes.append(text(x,end-12 if value>=0 else end+20,number(value),"value-label","middle"))
        shapes.append(wrapped(x,bottom+40,point["label"],12,anchor="middle"))
        if suffix(point,block):
            shapes.append(text(x,bottom+45+18*len(lines(point["label"],12)),suffix(point,block).lstrip(" ·"),anchor="middle"))
    height = bottom+90+max(len(lines(p["label"],12)) for p in points)*18
    return frame(block,identity,width,height,shapes,"纵向柱状比较；正负值保留零基线，未知值留空，预测使用淡色虚线边框")


def waterfall_chart(block, identity):
    points, shapes, spans = block["points"], [], []
    running = Decimal(0)
    for point in points:
        if point["role"] == "delta":
            start, running = running, decimal_sum((running, point["value"]))
            spans.append((start, running))
        else:
            running = Decimal(str(point["value"]))
            spans.append((Decimal(0), running))
    width = max(820, 100 + 88 * len(points))
    left, right, top, bottom = 75, width - 30, 50, 290
    low, high = bounds([value for span in spans for value in span])
    sy = lambda value: float(bottom - (value - low) / (high - low) * (bottom - top))
    for index in range(5):
        value = low + (high - low) * index / 4
        y = sy(value)
        shapes.append(f'<line x1="{left}" y1="{y}" x2="{right}" y2="{y}" class="grid-line"/>')
        shapes.append(text(left - 12, y + 5, axis_number(value), anchor="end"))
    step, bar_width = (right - left) / len(points), min(58, (right-left) / len(points) * .65)
    for index, (point, span) in enumerate(zip(points, spans)):
        x = left + (index + .5) * step
        a, b = span
        y1, y2 = sy(a), sy(b)
        color = COLORS[0] if point["role"] != "delta" else ("#248a3d" if point["value"] >= 0 else "#c44d3b")
        shapes.append(f'<rect x="{x-bar_width/2}" y="{min(y1,y2)}" width="{bar_width}" height="{max(abs(y1-y2),1)}" rx="3" {point_style(point,block,color)}/>')
        value = ("+" if point["role"] == "delta" and point["value"] > 0 else "") + number(point["value"])
        shapes.append(text(x, min(y1,y2)-12, value, "value-label", "middle"))
        shapes.append(wrapped(x, bottom+27, point["label"], 12, anchor="middle"))
        label_y = bottom + 32 + 18 * len(lines(point["label"], 12))
        shapes.append(text(x, label_y, ROLES[point["role"]], anchor="middle"))
        if suffix(point,block):
            shapes.append(text(x,label_y+19,suffix(point,block).lstrip(" ·"),anchor="middle"))
        if index < len(points)-1:
            shapes.append(f'<line x1="{x+bar_width/2}" y1="{y2}" x2="{x+step-bar_width/2}" y2="{y2}" stroke="#a3aab4" stroke-width="1" stroke-dasharray="3 3"/>')
    height = bottom + 80 + max(len(lines(p["label"], 12)) for p in points) * 18
    return frame(block, identity, width, height, shapes, "瀑布分解中变动项保留正负号；合计只核对已列项目的算术，不能证明原因完整")


def stacked_chart(block, identity):
    points, shapes = block["points"], []
    legend_y = 22
    for index, segment in enumerate(points[0]["segments"]):
        shapes.append(f'<rect x="175" y="{legend_y-11}" width="12" height="12" rx="2" fill="{COLORS[index]}"/>')
        shapes.append(wrapped(198, legend_y, segment["label"], 70, "chart-legend"))
        legend_y += max(25, len(lines(segment["label"], 70)) * 18 + 7)
    row_heights = []
    summaries = []
    for point in points:
        summary = "；".join(f'{s["label"]} {number(s["value"])}{suffix(s,block)}' for s in point["segments"])
        summaries.append(summary)
        row_heights.append(max(90, 65 + 18 * len(lines(summary, 72)), 25 + 18 * len(lines(point["label"],20))))
    bottom = legend_y + 15 + sum(row_heights)
    high = max(decimal_sum(s["value"] for s in p["segments"]) for p in points) or Decimal(1)
    scale = horizontal_axis(shapes, Decimal(0), high, 175, 700, legend_y+5, bottom)
    y = legend_y + 30
    for point, row_height, summary in zip(points, row_heights, summaries):
        shapes.append(wrapped(154, y+21, point["label"], 20, anchor="end"))
        total = Decimal(0)
        for index, segment in enumerate(point["segments"]):
            start = total
            total = decimal_sum((total, segment["value"]))
            x, end = scale(start), scale(total)
            shapes.append(f'<rect x="{x}" y="{y}" width="{end-x}" height="30" {point_style(segment,block,COLORS[index])}><title>{esc(segment["label"])}：{number(segment["value"])}；{KINDS[segment.get("kind",block["kind"])]}</title></rect>')
        shapes.append(text(720,y+21,number(total),"value-label"))
        shapes.append(wrapped(175,y+53,summary,72))
        y += row_height
    return frame(block, identity, 820, bottom+47, shapes, "堆叠各分项使用统一量尺；分项加总和整体分母是否完整必须由原始来源证明")


def svg_extended_chart(block, identity):
    return {"column": column_chart, "range": range_chart, "waterfall": waterfall_chart,
            "stacked_bar": stacked_chart, "proportion": proportion_chart}[block["chart_type"]](block, identity)


def chart_rows(block):
    """数据表只呈现原始值，不把区间中点、未知互补值写成数据。"""
    chart_type = block["chart_type"]
    columns = {"range": ["项目", "下界", "上界"], "waterfall": ["项目", "原始值", "角色"],
               "stacked_bar": ["组别", "系列", "原始值"], "proportion": ["项目", "原始值", "量尺上限"]}.get(chart_type, ["项目", "数值"])
    rows = []
    for point in block["points"]:
        parts = point["segments"] if chart_type == "stacked_bar" else [point]
        for part in parts:
            if chart_type == "range":
                row = [point["label"], number(point["low"]), number(point["high"])]
            elif chart_type == "waterfall":
                row = [point["label"], number(point["value"]), f'{point["role"]} · {ROLES[point["role"]]}']
            elif chart_type == "stacked_bar":
                row = [point["label"], part["label"], number(part["value"])]
            elif chart_type == "proportion":
                row = [point["label"], number(point["value"]), number(block["scale_max"])]
            else:
                row = [point["label"], number(point["value"])]
            row += [block["unit"], point.get("period",block["period"]), KINDS[part.get("kind",block["kind"])],
                    " ".join(f'[{eid}]' for eid in part.get("evidence_ids",block["evidence_ids"]))]
            rows.append(row)
    return columns + ["单位", "期间", "属性", "证据"], rows


def svg_diagram(block, identity):
    """环形角色总览保留真实方向；边编号关联图外清单，布局不表示层级。"""
    shapes, nodes = [], {node["id"]: node for node in block["nodes"]}
    node_list = list(nodes.values())
    index_of = {node["id"]: index for index, node in enumerate(node_list)}
    groups = {}
    for index, edge in enumerate(block["edges"]):
        pair = tuple(sorted((edge["source"], edge["target"]), key=index_of.get))
        groups.setdefault(pair, []).append(index)
    # 多条同端点关系增加纵向空间，避免在两节点场景中挤在一条线附近。
    extra = max(0, max(len(group) for group in groups.values()) - 4) * 18
    center_y = (150 if len(nodes) == 2 else 245) + extra
    graph_bottom = (270 if len(nodes) == 2 else 465) + extra * 2
    height = graph_bottom + 80
    positions = {}
    for index, node in enumerate(node_list):
        if len(nodes) == 2:
            positions[node["id"]] = (185 + index * 450, center_y)
        else:
            angle = -math.pi/2 + 2*math.pi*index/len(nodes)
            positions[node["id"]] = (410 + 295*math.cos(angle), center_y + 160*math.sin(angle))
    shapes.append('<defs>' + ''.join(
        f'<marker id="{identity}-arrow-{flow}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{color}"/></marker>'
        for flow, (_, color) in FLOWS.items()) + '</defs>')

    def boundary(center, toward):
        dx, dy = toward[0]-center[0], toward[1]-center[1]
        factor = min(89/abs(dx) if dx else float("inf"), 52/abs(dy) if dy else float("inf"))
        length = math.hypot(dx, dy)
        return (center[0]+dx*(factor+7/length), center[1]+dy*(factor+7/length))

    def along(start, control, end, t):
        return ((1-t)**2*start[0]+2*(1-t)*t*control[0]+t*t*end[0],
                (1-t)**2*start[1]+2*(1-t)*t*control[1]+t*t*end[1])

    curves = []
    for index, edge in enumerate(block["edges"]):
        pair = tuple(sorted((edge["source"], edge["target"]), key=index_of.get))
        canonical_start, canonical_end = (positions[nid] for nid in pair)
        dx, dy = canonical_end[0]-canonical_start[0], canonical_end[1]-canonical_start[1]
        distance = math.hypot(dx,dy)
        nx, ny = -dy/distance, dx/distance
        middle = ((canonical_start[0]+canonical_end[0])/2, (canonical_start[1]+canonical_end[1])/2)
        group = groups[pair]
        offset = 0
        if len(group) > 1:
            desired = (len(group)-1)*36
            lower, upper = -desired, desired
            for position, direction, minimum, maximum in ((middle[0],nx,40,780),(middle[1],ny,30,graph_bottom-15)):
                if direction:
                    limits = sorted(((minimum-position)/direction,(maximum-position)/direction))
                    lower,upper = max(lower,limits[0]), min(upper,limits[1])
            offset = lower + (upper-lower)*group.index(index)/(len(group)-1)
        control = (middle[0]+nx*offset,middle[1]+ny*offset)
        start = boundary(positions[edge["source"]],control)
        end = boundary(positions[edge["target"]],control)
        dashed = "6 4" if edge["basis"] in ("unknown","inference") else "none"
        flow_label,color = FLOWS[edge["flow"]]
        description = f'{nodes[edge["source"]]["label"]} → {nodes[edge["target"]]["label"]}：{edge["label"]}；{flow_label}；{BASIS[edge["basis"]]}'
        path = f'M {start[0]:.2f} {start[1]:.2f} Q {control[0]:.2f} {control[1]:.2f} {end[0]:.2f} {end[1]:.2f}'
        shapes.append(f'<path id="{identity}-edge-{index+1}" d="{path}" fill="none" stroke="{color}" stroke-width="2.5" stroke-dasharray="{dashed}" marker-end="url(#{identity}-arrow-{edge["flow"]})"><title>{esc(description)}</title></path>')
        curves.append((start,control,end,nx,ny,color))
    # 编号沿曲线避让已画编号与角色框；不借编号暗示发生顺序。
    placed = []
    for index, (start,control,end,nx,ny,color) in enumerate(curves,1):
        selected = None
        for t in (.5,.35,.65,.25,.75,.18,.82):
            point = along(start,control,end,t)
            for shift in (0,20,-20,36,-36):
                candidate = (point[0]+nx*shift,point[1]+ny*shift)
                clear_nodes = all(abs(candidate[0]-x)>108 or abs(candidate[1]-y)>71 for x,y in positions.values())
                clear_labels = all(math.hypot(candidate[0]-x,candidate[1]-y)>32 for x,y in placed)
                if 18<candidate[0]<802 and 18<candidate[1]<graph_bottom-5 and clear_nodes and clear_labels:
                    selected=(candidate,point)
                    break
            if selected:
                break
        if not selected:
            point=along(start,control,end,.5)
            selected=(point,point)
        (x,y),(px,py)=selected
        placed.append((x,y))
        if math.hypot(x-px,y-py)>1:
            shapes.append(f'<line x1="{px:.2f}" y1="{py:.2f}" x2="{x:.2f}" y2="{y:.2f}" stroke="{color}" stroke-width="1"/>')
        shapes.append(f'<a href="#{identity}-edge-note-{index}" aria-label="查看关系 {index:02d}"><circle cx="{x:.2f}" cy="{y:.2f}" r="13" fill="white" stroke="{color}" stroke-width="1.5"/>'
                      f'<text x="{x:.2f}" y="{y+4:.2f}" text-anchor="middle" fill="{color}" font-size="11" font-weight="650">{index:02d}</text></a>')
    for node in node_list:
        x,y=positions[node["id"]]
        label_lines=lines(node["label"],18)
        display=label_lines[:3]
        if len(label_lines)>3:
            display[-1]=display[-1]+"…"
        dashed = ' stroke-dasharray="6 4"' if node["basis"] in ("unknown","inference") else ''
        shapes.append(f'<g class="diagram-network-node"><title>{esc(node["label"])}</title><rect x="{x-89:.2f}" y="{y-52:.2f}" width="178" height="104" rx="15" fill="#f5f7fa" stroke="#b8c6d7"{dashed}/>')
        for line_index,line in enumerate(display):
            shapes.append(text(x,y-4-(len(display)-1)*9+line_index*18,line,"diagram-node-label","middle"))
        shapes.append(text(x,y+33,BASIS[node["basis"]],"diagram-basis","middle"))
        shapes.append('</g>')
    for index,(flow,(label,color)) in enumerate(FLOWS.items()):
        x=32+index*198
        shapes.append(f'<line x1="{x}" y1="{graph_bottom+18}" x2="{x+28}" y2="{graph_bottom+18}" stroke="{color}" stroke-width="2.5" marker-end="url(#{identity}-arrow-{flow})"/>')
        shapes.append(text(x+39,graph_bottom+23,label,"diagram-basis"))
    shapes.append(text(32,graph_bottom+55,"环形排列仅为布局；编号对应下方关系，不表示层级、规模或发生顺序。","diagram-basis"))
    return frame(block,identity,820,height,shapes,"角色之间的有向关系总览；编号对应下方逐条关系清单。箭头等粗，不表示金额或数量；分析推断与待核实关系为虚线")
