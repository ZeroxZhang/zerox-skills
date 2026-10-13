"""生成 examples/dashboards/*.json（多图拼版示例；全部为示意数据，与参考图的真实数字无关）。"""
import json, os, random
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "examples", "dashboards")
os.makedirs(R, exist_ok=True)
TEAMS = {"Team A": "#0070C0", "Team B": "#EA6A06", "Team C": "#4EA72E", "Others": "#BFBFBF", "Overall": "#000000", "Team D": "#E8B400"}
def save(n, sp): json.dump(sp, open(f"{R}/{n}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
X9 = ["25-Q1", "25-Q2", "25-Q3", "25/10", "25/11", "25/12", "26/1", "26/2", "26/3"]
SEG = [{"from": 0, "to": 2, "label": "By Q"}, {"from": 3, "to": 8, "label": "By M"}]

# ---------- 1. 三栏：堆叠面积 + 折线组 / 堆叠面积 + 同比折线 ----------
rev = {"Team A": [2.0, 2.8, 3.5, 3.8, 4.2, 4.7, 4.0, 4.3, 4.6], "Team B": [1.8, 2.1, 2.6, 3.0, 3.4, 3.6, 3.3, 3.7, 3.9],
       "Team C": [0.1, 0.1, 0.2, 0.2, 0.2, 0.3, 0.2, 0.3, 0.3], "Others": [2.5, 2.9, 3.5, 4.1, 4.6, 5.1, 5.2, 5.5, 5.6]}
gmv = {"Team A": [14, 17, 20, 23, 26, 30, 28, 31, 30], "Team B": [18, 20, 24, 30, 34, 36, 35, 38, 38],
       "Team C": [1, 1, 2, 2, 2, 2, 2, 2, 2], "Others": [62, 66, 71, 78, 86, 98, 102, 106, 104]}
astr = {"Team A": [14.1, 15.2, 15.8, 15.0, 15.4, 15.0, 14.0, 13.8, 14.5], "Overall": [11.6, 12.3, 12.8, 12.4, 12.3, 12.2, 11.5, 11.6, 12.0],
        "Team B": [9.6, 9.9, 10.2, 10.0, 10.1, 9.7, 9.4, 9.8, 10.0], "Others": [4.0, 4.4, 4.9, 5.1, 5.2, 5.1, 5.1, 5.2, 5.3]}
yoy = {"Others": [128, 125, 114, 102, 110, 116, 125, 112, 87], "Team A": [155, 168, 171, 150, 158, 142, 126, 129, 83], "Team B": [124, 102, 100, 96, 101, 96, 104, 99, 79]}
def S(dct, keys=None): return [{"name": k, "values": dct[k]} for k in (keys or dct)]
save("dash_three_column", {
 "id": "dash_three_column", "type": "dashboard", "palette": "ops_bright", "series_colors": TEAMS,
 "title_tag": {"text": "Region-A", "fill": "yellow"}, "title": "Daily Revenue & YoY & Daily GMV & Ad-share% by Teams [$Mn/%]",
 "source": "Illustrative data (not real figures)", "footnotes": [[{"text": "YoY: Team performance dataset "}, {"text": "(Daily Latest Binding)", "color": "red", "bold": True}], "Limited to shops with ad revenue in the respective month"],
 "panels": [
  {"box": [0, 0, 0.36, 1], "title": "Daily Revenue ($Mn)", "title_style": "red",
   "chart": {"kind": "area_stack", "data": {"categories": X9, "series": S(rev)}, "segments": SEG, "decimals": 1, "font_size": 7}},
  {"box": [0.375, 0, 0.30, 0.37], "title": "Ad-share%", "title_style": "red",
   "chart": {"kind": "lines", "data": {"categories": X9, "series": S(astr)}, "suffix": "%", "decimals": 1, "segments": SEG, "font_size": 6.5, "line_width": 1.25,
             "annotations": [{"type": "arrow", "from": [0.62, 0.12], "to": [0.72, 0.3]}]}},
  {"box": [0.375, 0.39, 0.30, 0.61], "title": "Daily GMV of Advertised Shops ($Mn)", "title_style": "red",
   "chart": {"kind": "area_stack", "data": {"categories": X9, "series": S(gmv)}, "font_size": 6.5, "decimals": 0}},
  {"box": [0.69, 0, 0.31, 1], "title": "Revenue YoY", "title_style": "red",
   "chart": {"kind": "lines", "data": {"categories": X9, "series": [dict(name="Others", values=yoy["Others"], label_pos="below"), dict(name="Team A", values=yoy["Team A"]), dict(name="Team B", values=yoy["Team B"], label_pos="below")]},
             "suffix": "%", "smooth": True, "segments": SEG, "font_size": 7, "pad_hi": 2.2, "pad_lo": 2.2}}]})

# ---------- 2. 同类布局 + 红圈 ----------
X9b = ["25-Q1", "25-Q2", "25-Q3", "25-10", "25-11", "25-12", "26-01", "26-02", "26-03"]
SEG3 = [{"from": 0, "to": 2, "label": "By Q"}, {"from": 3, "to": 5, "label": "By M"}, {"from": 6, "to": 8, "label": "2026 By M"}]
rev2 = {"Team A": [1.8, 2.3, 2.6, 2.9, 4.5, 3.9, 2.8, 3.0, 3.6], "Team C": [0.1, 0.1, 0.2, 0.2, 0.9, 0.6, 0.6, 0.8, 0.9],
        "Team B": [0.05, 0.1, 0.1, 0.1, 0.2, 0.2, 0.2, 0.2, 0.2], "Others": [1.9, 2.4, 3.0, 3.4, 5.4, 4.6, 3.5, 4.0, 4.4]}
gmv2 = {"Team A": [15, 17, 21, 23, 34, 32, 23, 25, 29], "Team C": [0.5, 1, 1, 1, 2, 2, 2, 2, 3], "Team B": [0.5, 0.5, 0.5, 0.5, 1, 1, 1, 1, 1], "Others": [13, 13, 16, 18, 26, 23, 18, 20, 21]}
astr2 = {"Others": [13.5, 16.8, 17.2, 18.4, 19.8, 19.1, 18.6, 19.8, 19.4], "Overall": [12.0, 13.6, 13.8, 13.8, 15.0, 13.7, 13.6, 14.2, 14.4], "Team A": [11.5, 12.9, 12.3, 12.4, 13.0, 11.9, 11.8, 11.8, 12.1]}
yoy2 = {"Overall": [160, 110, 111, 106, 128, 103, 99, 116, 105], "Others": [220, 145, 134, 120, 135, 134, 117, 121, 104], "Team A": [144, 95, 83, 80, 89, 70, 65, 72, 70]}
save("dash_three_column_circle", {
 "id": "dash_three_column_circle", "type": "dashboard", "palette": "ops_bright", "series_colors": dict(TEAMS, **{"Others": "#BFBFBF"}),
 "title_tag": {"text": "Region-B", "fill": "yellow"}, "title": "Daily Revenue & YoY & Daily GMV & Ad-share% by Teams [$Mn/%]",
 "source": "Illustrative data (not real figures)",
 "panels": [
  {"box": [0, 0, 0.36, 1], "title": "Daily Revenue/$Mn", "chart": {"kind": "area_stack", "data": {"categories": X9b, "series": S(rev2)}, "segments": SEG3, "decimals": 1, "font_size": 7}},
  {"box": [0.375, 0, 0.30, 0.42], "title": "Ad-share/%", "chart": {"kind": "lines", "data": {"categories": X9b, "series": [dict(name="Others", values=astr2["Others"]), dict(name="Overall", values=astr2["Overall"]), dict(name="Team A", values=astr2["Team A"], label_pos="below")]},
     "suffix": "%", "decimals": 1, "segments": SEG3, "font_size": 6.5, "line_width": 1.25,
     "annotations": [{"type": "circle", "series": "Team A", "points": [6, 7, 8], "label_pos": "below", "w": 0.5, "h": 0.22}]}},
  {"box": [0.375, 0.44, 0.30, 0.56], "title": "Daily GMV/$Mn", "chart": {"kind": "area_stack", "data": {"categories": X9b, "series": S(gmv2)}, "segments": SEG3, "font_size": 6.5}},
  {"box": [0.69, 0, 0.31, 1], "title": "YoY/%", "chart": {"kind": "lines", "data": {"categories": X9b, "series": [dict(name="Others", values=yoy2["Others"]), dict(name="Overall", values=yoy2["Overall"], label_pos="below"), dict(name="Team A", values=yoy2["Team A"], label_pos="below")]},
     "suffix": "%", "smooth": True, "segments": SEG3, "font_size": 7}}]})

# ---------- 3. 分面网格：6 国家 × 4 指标 ----------
random.seed(7)
C6 = ["Country 1", "Country 2", "Country 3", "Country 4", "Country 5", "Country 6"]; X7 = ["W1", "W2", "W3", "W4", "W5", "W6", "W7"]
def walk(b, n=7, s=0.06): v = [b]; [v.append(round(v[-1]*(1+random.uniform(-s, s)), 0)) for _ in range(n-1)]; return v
def cell_rev(scale):
    return {"categories": X7, "series": [{"name": n, "values": walk(b*scale)} for n, b in [("Team A", 500), ("Team B", 300), ("Team C", 40), ("Others", 700)]]}
cells = [[], [], [], []]
for j, sc in enumerate([1.0, 1.2, 1.4, 0.8, 0.6, 0.3]):
    r = cell_rev(sc); cells[0].append(r); cells[1].append(r)
    cells[2].append({"categories": X7, "series": [{"name": "Others", "values": walk(15000*sc, s=0.03)}, {"name": "Team A", "values": walk(4000*sc, s=0.03)}, {"name": "Team B", "values": walk(900*sc, s=0.03)}]})
    cells[3].append({"categories": X7, "series": [{"name": "Team C", "values": walk(390, s=0.05)}, {"name": "Team B", "values": walk(250, s=0.05)}, {"name": "Team A", "values": walk(110, s=0.05)}, {"name": "Others", "values": walk(30, s=0.05)}]})
save("facet_country_metric", {
 "id": "facet_country_metric", "type": "facet", "palette": "ops_bright", "series_colors": TEAMS,
 "title_tag": {"text": "Region-A", "fill": "yellow"}, "title": [{"text": "Revenue & Active Shops & ARPA "}, {"text": "by Country"}],
 "source": "Illustrative data (not real figures)",
 "cols": C6, "rows": [
  {"label": "Daily Rev\n($K)", "chart": {"kind": "area_stack", "font_size": 5, "show_share": True, "min_label_h": 0.12, "totals": True, "x_labels": False}},
  {"label": "Daily Rev\nShare", "chart": {"kind": "area_stack", "percent": True, "font_size": 5, "x_labels": False, "segment_labels": True}},
  {"label": "#Active Shops", "chart": {"kind": "lines", "font_size": 5, "x_labels": False, "shared_y": "none", "line_width": 1}},
  {"label": "Active Shop\nDaily ARPA", "chart": {"kind": "lines", "font_size": 5, "line_width": 1, "x_label_size": 5}}],
 "cells": cells, "row_header_w": 1.35, "legend_w": 0.8})

# ---------- 4. 8 分面成对条形：时间进度线 + 红绿条件色 ----------
teams = ["Total", "Team A", "Team B", "Team C", "Web", "Branding"]; levers = ["Lever 1", "Lever 2", "Lever 3", "Lever 4", "Lever 5", "Lever 6", "Lever 7", "Lever 8"]
random.seed(11); cells4 = []
for i, t in enumerate(teams):
    row = []
    for j, l in enumerate(levers):
        if j == 7 and i > 0: row.append(None); continue
        v = round(random.uniform(30, 62), 1); c = round(random.uniform(35, 70), 1)
        if (i, j) in [(2, 3), (2, 6), (3, 6)]: v = round(random.uniform(68, 99), 1) if (i, j) == (2, 3) else 190.0 + 20*i
        row.append({"value": v, "compare": c})
    cells4.append(row)
save("facet_target_bars", {
 "id": "facet_target_bars", "type": "facet", "title": "Business Unit | 2026Q1 | Target Achievement by Team by Lever (Update to 02-28)",
 "title_bold": False, "title_size": 18, "source": "Illustrative data (not real figures)",
 "note": [{"text": "Red/green = 26Q1 achievement (red = behind time progress, green = ahead)\nGray = 25Q1 achievement"}],
 "cols": levers, "col_header_style": "plain", "col_header_align": "l", "col_header_size": 10, "row_header_style": "right", "row_header_w": 1.0, "legend_w": 0.25,
 "separators": None, "bottom_h": 0.25,
 "rows": [{"label": t, "chart": {"kind": "bars_pair", "rule": {"threshold": 65.6, "ge": "green", "lt": "red", "compare": "gray"}, "x_max": 80, "font_size": 6.5, "bar_h": 0.26}} for t in teams],
 "cells": cells4})

# ---------- 5. 三层共用横轴：同比曲线 / 占比曲线+通道+批注 / 堆叠柱 ----------
N13 = ["a.23 Mid-Mar", "b.23 Pre-sale", "c.23 Main", "d.23 Return", "e.23 Off-peak", "f.23 Double-11", "g.23 D11 Return", "h.23 Dec", "i.24 Mar", "j.24 Mid-Mar", "k.24 Pre-sale", "l.24 Main", "m.24 Return"]
N = len(N13)
yoyA = [195, 158, 150, 125, 118, 121, 126, 158, 26, 58, 40, 35, 37]; yoyB = [56, 54, 66, 40, 60, 73, 70, 84, 30, 41, 34, 28, 32]
share = [37.9, 36.4, 35.1, 39.0, 40.0, 36.2, 42.1, 41.4, 36.8, 43.0, 39.4, 37.0, 40.1]
selfs = [2.1, 2.4, 2.4, 2.3, 2.9, 3.2, 3.5, 3.3, 2.9, 3.1, 3.4, 3.2, 3.1]; nons = [3.3, 3.9, 4.3, 3.4, 4.3, 5.7, 5.1, 4.9, 5.2, 4.5, 5.5, 5.6, 4.5]
off = [0, 3, 4, 8, 9]   # 平销节点用浅色
segs5 = [{"from": 0, "to": 7, "label": "2023"}, {"from": 8, "to": 12, "label": "2024"}]
PAD = {"l": 0.25, "r": 1.25}
save("dash_shared_axis_layers", {
 "id": "dash_shared_axis_layers", "type": "dashboard", "title": [{"text": "Self-serve vs Managed  ", "color": "#000000"}, {"text": "Daily Spend & Mid-funnel Share by Event", "color": "#4472C0"}, {"text": " (to 6/30)", "color": "#000000"}],
 "source": "Illustrative data (not real figures)", "pad": PAD,
 "panels": [
  {"box": [0, 0, 1, 0.26], "chart": {"kind": "lines", "data": {"categories": N13, "series": [{"name": "Self-serve YoY", "values": yoyA}, {"name": "Managed YoY", "values": yoyB, "label_pos": "below"}]},
     "suffix": "%", "smooth": True, "x_labels": False, "font_size": 7.5, "line_width": 1.25, "baseline": False, "legend_size": 7.5}},
  {"box": [0, 0.27, 1, 0.27], "chart": {"kind": "lines", "data": {"categories": N13, "series": [{"name": "Mid-funnel share\n(non-home)", "values": share}]},
     "suffix": "%", "decimals": 1, "smooth": True, "x_labels": False, "font_size": 7.5, "line_width": 1.25, "baseline": False, "pad_hi": 2.4, "pad_lo": 2.4, "legend_size": 7.5,
     "segments": segs5, "segment_style": {"color": "#7F7F7F", "italic": True, "bold": False, "size": 8.5},
     "annotations": [{"type": "channel", "series": "Mid-funnel share\n(non-home)", "offset": 3.6, "color": "#7F7F7F"},
       {"type": "circle", "series": "Mid-funnel share\n(non-home)", "points": [1], "color": "green", "w": 0.5, "h": 0.24}, {"type": "circle", "series": "Mid-funnel share\n(non-home)", "points": [2], "color": "green", "w": 0.5, "h": 0.24},
       {"type": "circle", "series": "Mid-funnel share\n(non-home)", "points": [3], "color": "green", "w": 0.5, "h": 0.24},
       {"type": "circle", "series": "Mid-funnel share\n(non-home)", "points": [10], "color": "red", "w": 0.5, "h": 0.24}, {"type": "circle", "series": "Mid-funnel share\n(non-home)", "points": [11], "color": "red", "w": 0.5, "h": 0.24},
       {"type": "circle", "series": "Mid-funnel share\n(non-home)", "points": [12], "color": "red", "w": 0.5, "h": 0.24},
       {"type": "note", "text": "VS off-peak", "value": -1.5, "series": "Mid-funnel share\n(non-home)", "point": 0, "dx": 0.1, "dy": -0.45},
       {"type": "note", "text": "VS off-peak", "value": -3.0, "series": "Mid-funnel share\n(non-home)", "point": 1, "dx": 0.25, "dy": -0.5},
       {"type": "note", "text": "VS off-peak", "value": 0.9, "series": "Mid-funnel share\n(non-home)", "point": 3, "dx": 0.05, "dy": 0.42},
       {"type": "note", "text": "VS off-peak", "value": -3.8, "series": "Mid-funnel share\n(non-home)", "point": 10, "dx": 0.0, "dy": -0.5},
       {"type": "note", "text": "VS off-peak", "value": -6.2, "series": "Mid-funnel share\n(non-home)", "point": 11, "dx": 0.0, "dy": -0.42},
       {"type": "note", "text": "VS off-peak", "value": -3.1, "series": "Mid-funnel share\n(non-home)", "point": 12, "dx": 0.0, "dy": -0.5},
       {"type": "arrow", "from": [0.165, 0.5], "to": [0.21, 0.62]}, {"type": "arrow", "from": [0.775, 0.42], "to": [0.83, 0.55]}]}},
  {"box": [0, 0.55, 1, 0.45], "chart": {"kind": "column_stack", "data": {"categories": N13, "series": [
       {"name": "Self-serve spend", "values": selfs, "point_colors": ["#9CAECC" if i in off else "#4472C0" for i in range(N)]},
       {"name": "Managed spend", "values": nons, "point_colors": ["#D9D9D9" if i in off else "#A6A6A6" for i in range(N)]}]},
     "decimals": 1, "font_size": 7.5, "x_label_size": 6, "x_label_bold": False, "legend_size": 7.5, "segments": [{"from": 0, "to": 7}, {"from": 8, "to": 12}]}}],
 "series_colors": {"Self-serve YoY": "#4472C0", "Managed YoY": "#ED7D31", "Mid-funnel share\n(non-home)": "#6F9FD8", "Self-serve spend": "#4472C0", "Managed spend": "#A6A6A6"}})
print("ok")
