#!/usr/bin/env python3
"""CLI: tc_render.py spec.json [spec2.json ...] -o out.pptx [--png DIR]
spec 可以是单个图表对象，也可以是 {"slides":[...]}。输出可编辑 PPTX；--png 用 LibreOffice 渲染每页 PNG。"""
import sys, json, argparse, subprocess, os, tempfile, shutil, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tc_core, tc_more, tc_validate

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("specs", nargs="+"); ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--png", help="PNG 输出目录（每页一张，文件名 = spec 的 id 或页码）"); ap.add_argument("--dpi", type=int, default=110)
    ap.add_argument("--theme", help="配色主题，覆盖 spec 里的 theme；可选值见 --list-themes")
    ap.add_argument("--force", action="store_true", help="数据校验有致命问题时仍强行渲染（不推荐）")
    ap.add_argument("--no-validate", action="store_true", help="跳过渲染前的数据校验")
    ap.add_argument("--list-themes", action="store_true", help="列出全部配色主题后退出")
    if "--list-themes" in sys.argv:
        for k, v in tc_core.THEMES.items():
            print(f"{k:20s} {v['meta'].get('zh','')}{'  (默认)' if k == tc_core.DEFAULT_THEME else ''}  {' '.join(v['palette'][:6])}")
        return
    a = ap.parse_args()
    if a.theme:
        if a.theme not in tc_core.THEMES: sys.exit(f"未知主题 {a.theme}；可选：{', '.join(tc_core.THEMES)}")
        tc_core.FORCE_THEME = a.theme
    prs = tc_core.new_prs(); ids = []
    for f in a.specs:
        j = json.load(open(f, encoding="utf-8"))
        if isinstance(j, list) or ("slides" not in j and "type" not in j):
            print("skip (not a chart spec):", f); continue
        for s in (j["slides"] if "slides" in j else [j]):
            if not a.no_validate:
                r = tc_validate.validate(s)
                if r["status"] != tc_validate.OK: print(tc_validate.report(r), file=sys.stderr); print(file=sys.stderr)
                if r["status"] == tc_validate.FAIL and not a.force:
                    sys.exit(f"已停止渲染：{f} 的数据不足以画 {s.get('type')}（见上方说明）。补齐数据后重试，或加 --force 强行渲染。")
            tc_core.render(prs, s); ids.append(s.get("id") or os.path.splitext(os.path.basename(f))[0])
    prs.save(a.out); print("PPTX:", a.out)
    if a.png:
        os.makedirs(a.png, exist_ok=True); tmp = tempfile.mkdtemp()
        subprocess.run(["soffice","--headless","--convert-to","pdf","--outdir",tmp,a.out], check=True, capture_output=True)
        pdf = glob.glob(tmp+"/*.pdf")[0]
        subprocess.run(["pdftoppm","-png","-r",str(a.dpi),pdf,tmp+"/p"], check=True)
        pages = sorted(glob.glob(tmp+"/p-*.png"))
        for pid, p in zip(ids, pages):
            shutil.move(p, os.path.join(a.png, f"{pid}.png")); print("PNG:", os.path.join(a.png, f"{pid}.png"))
        shutil.rmtree(tmp)
if __name__ == "__main__": main()
