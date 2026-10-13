---
name: zerox-thinkcell-charts
description: 生成 think-cell 风格的可编辑 PowerPoint 形状图表、PNG 预览与离线可改字的 HTML，支持 55 种单图、dashboard/facet、推荐校验和 8 套配色。用户要求瀑布图、Mekko、咨询图表、图表选型、JSON 转 PPTX 或可编辑 HTML 时使用。不负责完整报告撰写，不提供 think-cell 插件、Excel 链接或浏览器内数据重算。
---

# zerox-thinkcell-charts

用一份 JSON 描述图表，生成**可编辑 PPTX**（全部是 PowerPoint 原生形状，每个都能单独选中、改色、改字）、**PNG 预览**，以及**可编辑 HTML**（原生 SVG 图形，标题、数据标签与说明可在浏览器改字并保存）。支持单图与 dashboard / facet 拼版；视觉风格参考 think-cell 示例并包含本项目的扩展约定。

## 快速使用
```bash
python3 -m venv .venv && .venv/bin/pip install -r scripts/requirements.txt   # 渲染 PNG 还需要 LibreOffice(soffice) + poppler(pdftoppm)
.venv/bin/python scripts/tc_render.py examples/waterfall.json -o out.pptx --png out_png/ --html out.html
.venv/bin/python scripts/tc_render.py a.json b.json c.json -o deck.pptx --png pngs/ --html deck.html   # 多张合成一个 deck
.venv/bin/python scripts/tc_render.py examples/waterfall.json --html report.html   # 只写 HTML
```
一个 JSON 可以是单个图表对象，也可以是 `{"slides":[...]}`。渲染至少提供 `-o` 或 `--html`；`--png` 仍要求 `-o`。HTML 为离线单文件，无 CDN，不需要 LibreOffice / Poppler；省略 `-o` 时只写 HTML，不改已有 PPTX / PNG。CLI 未指定 `--html` 时保持原有输出。Skill 常规交付 PPTX、PNG、可编辑 HTML 三份；用户明确只要部分格式时按其要求，HTML 不替代前两份。

给真正使用者的「什么时候用、怎么给数据、怎么写 prompt、交付物是什么」见 [README.md · 如何使用与怎么写 prompt](README.md#how-to-use)；多图拼版字段见 [docs/DASHBOARD.md](docs/DASHBOARD.md)。

## 工作流程（给 Agent）
**拿数据 →（未指定图）分析推荐、让用户确认 /（已指定图）校验并报缺 → 选配色 → 渲染 → 交付**

1. **拿数据**：支持 CSV、TSV、Excel、JSON 或粘贴的表格。先存成文件（粘贴内容可以直接用管道传给 `tc_advise.py -`）。
2a. **用户没指定图表** → 运行
   `python scripts/tc_advise.py data.csv [--intent "用户想说明的结论"] -o draft.json --json advise.json`
   - 把报告里的“数据长什么样、可能的结论、1 个首选 + 2 个备选（理由、建议标题、强调点、标记）”用大白话转述给用户，**请用户确认图表和结论**后再继续。
   - **结合自身判断**：规则引擎只看数据形态和关键词，不懂业务语境。下面几种情况要用自己的判断覆盖推荐：
     - 用户的原话、上下文或受众（董事会 / 运营周会）指向另一种图；
     - 数据其实不可加总（例如混了单位）；
     - 自动推断的结论不是用户真正想说的。
   - 覆盖推荐时，在 `docs/CHART_SELECTION.md` 里找对应行，说明理由。
   - 建议标题只是草稿，要改成用户认可的结论式标题；`source` 必须向用户要，不能编。
   - 草稿里空值暂时填了 0，要提醒用户补真实数字。
2b. **用户指定了图表** → 先按 `docs/CATALOG.md` 把数据写进 spec，再运行
   `python scripts/tc_validate.py spec.json`
   - **能做**：继续。
   - **能做但有问题**：把问题和建议告诉用户，由用户决定是否修正。
   - **不能做**：原样告诉用户缺什么、怎么补（含示例格式）、折中办法和替代图，**等用户补数据或同意折中**。不要自己编数据补齐。
3. **选配色**：用户没指定配色时，按下面的“配色选择”询问。
4. **渲染**：常规使用 `tc_render.py spec.json -o out.pptx --png out/ --html out.html [--theme 主题]`，交付三种格式，保持 PPTX / PNG 原有生成方式。用户明确只要部分格式时相应删减参数；至少提供 `-o` 或 `--html`，`--png` 需要 `-o`；只要 HTML 时不要加 `-o` / `--png`。渲染前会**自动校验**：遇到“不能做”会拒绝渲染并用大白话报错；只有用户明确接受折中时才加 `--force`。`--no-validate` 可以跳过校验。
   - 四区要齐：① title（结论式）+ unit；② 数据标签自动生成；③ highlight 圈出重点；④ callouts、footnote、source。
   - 需要标记时加 decorations：CAGR、total_diff、diff、value_line。
4b. **多图拼版**：数据有多个指标 × 多个分组（推荐器会首选 `facet`），或者用户要“一页多图 / 看板 / 分面”时，按 `docs/DASHBOARD.md` 写 `type: dashboard`（自由区域或网格，子图类型可以混用）或 `type: facet`（行×列分面，可共用纵轴）。分段虚线、多层横轴、条件着色（≥时间进度为绿、否则红、对比期为灰）、圈注、箭头、“VS … ±pp”批注都写在子图的 `segments` / `annotations` / `rule` 里。用户给的参考图中如果有真实业务数字，示例一律换成示意数据。
5. **检查后交付用户要求的文件**：PPTX / PNG 通过预览检查标签是否重叠、箭头是否压字、颜色语义是否正确（正向用主色、负向用酒红/红）。HTML 在浏览器目检，实际检查开启编辑 → 修改标题/说明/数据标签/脚注/批注 → 保存 HTML → 重新打开并继续编辑，不能仅凭文件生成就宣称可编辑。另按 `docs/STYLE_SPEC.md` §11 结论页四件套与 §12 易误读护栏自检（结论标题、baseline、例外圈注、source+截止日期；达成率分母、pp vs %、红圈=讨论重点、跨页对齐日期）。

## HTML 编辑边界

- 工具条切换文字编辑；点击文字改写，保存后的 HTML 可再次离线打开并继续编辑。使用说明与示例见 [README.md · 可编辑 HTML](README.md#editable-html) 和 `gallery/editable-demo.html`。
- 只改变当前 HTML 的显示文字，不重新计算数据、不改变柱高等几何信息，也不回写 JSON、PPTX 或 PNG。用户要求变更数值或数据关系时，修改真实源 spec 后重新渲染。
- HTML 是独立附加输出，常规与 PPTX / PNG 一起交付；用户明确只要部分格式时遵从其要求。CLI 保持兼容，未加 `--html` 不自动生成。无需 LibreOffice 或 Poppler，不提供悬浮数据提示、图形拖拽或数据联动。
- 浏览器和 PowerPoint 的字体表现有微差；长文字可能挤压版面，编辑保存后需再次目检。

## 目录
- `scripts/tc_core.py`：绘图引擎（版面分区、第一批 25 种图、装饰、标签防重叠）
- `scripts/tc_dash.py`：多图拼版（dashboard / facet，字段见 `docs/DASHBOARD.md`，示例见 `examples/dashboards/`）
- `scripts/tc_more.py`：第二批 30 种图（共 55 种类型、61 个示例、11 类）
- `scripts/tc_render.py`：PPTX / PNG / HTML CLI（渲染前自动调用 tc_validate；`--html`、`--theme`、`--list-themes`、`--force`、`--no-validate`）
- `scripts/tc_svg.py`、`scripts/tc_html.py`、`assets/html-editor.html`：原生 SVG 转换、单文件 HTML 导出与文字编辑保存界面
- `scripts/tc_advise.py`：数据分析 + 图表推荐（规则引擎，输出中文报告、JSON 和 spec 草稿）
- `scripts/tc_validate.py`：数据充分性校验（55 种图全覆盖）
- `docs/CHART_SELECTION.md`：数据形态 × 表达意图 → 图表 决策表，以及校验项清单（含 §5 经营汇报高频意图）
- `docs/DASHBOARD.md`：多图拼版字段；§7 为经营对账页配方（Scorecard / 量速效三联 / Facet 换维）
- `tests/`：20 个推荐数据集 + 16 个校验用例，`python tests/run_tests.py` 检查原有流程；`python -m unittest discover -s tests -p 'test_*.py'` 检查 SVG / HTML 与全部 72 个示例导出，范围见 `tests/README.md`
- `scripts/make_examples.py`：生成 `examples/*.json`
- `scripts/build_gallery.py`：分类 gallery PPTX/PDF，并重渲染示例 PNG
- `scripts/build_docs.py`：生成 CATALOG 和 HTML 总览
- `docs/CATALOG.md`：图表目录，每个图都有数据格式、样例、适合场景和示例图
- `docs/STYLE_SPEC.md`：版面分区和元素规则（§9 四区；§11 结论页四件套；§12 易误读护栏）
- `docs/AUDIT.md`：61 个示例的四区审核表
- `scripts/audit.py`：历史前后对照审核工具，需显式提供旧示例目录，不是通用测试入口
- `docs/COLORS.md`：配色和取色出处
- `references/SOURCES.csv`、`references/palettes/SOURCES.csv`：外部参考图来源索引；原始截图仅在本地 `references/img/` 与 `references/palettes/` 留存，不进入公开分发，也不是运行依赖。授权范围见 `NOTICE`。
- `examples/`：61 个基础单图（JSON / PNG，分类索引为 `catalog.json`）、5 个 `dashboards/` 拼版、6 个 `ops-report/` 经营对账 spec，合计 72 个图表 spec
- `gallery/`：`thinkcell-gallery.pptx` / `.pdf`（按分类排）、`index.html`（PNG 静态总览）、`editable-demo.html`（可离线改字的 HTML 示例）、`gallery-screenshot.png`

## 已知限制
- PPTX 输出是**形状**，不是 PowerPoint 原生图表对象：可以随意改样式，但改数据要重新生成（不能在 PowerPoint 里"编辑数据"）。
- 标签防重叠是启发式规则（估算文字宽度后上下微移），不能保证零重叠；段太小时直接隐藏标签。
- 第二批中咨询类图（漏斗、热力、矩阵、帕累托、龙卷风、树、KPI 卡、子弹、雷达、TAM、华夫等）think-cell 本身没有，样式属 [约定]。
- 拼版子图目前只支持 4 种 kind（area_stack / lines / column_stack / bars_pair），版面固定为 16:9。参考图如果更宽，会被等比压缩。
- 没有实现：think-cell 那种拖动重排、自动链接 Excel、对数轴。

## 配色选择（调用流程，必须执行）
1. 用户没有指定配色时，**先不要出图**，向用户展示配色选项并询问：列出 8 套主题（名称 + 一句话特征，见 docs/PALETTES.md 总览表），可附上预览图 `gallery/palettes/all-palettes.png`。
2. 用户选定后，在 spec 顶层写 `"theme": "<名称>"`，或命令行加 `--theme <名称>`。
3. 用户说“随便 / 都行 / 你定”，或者没有回答配色问题时，用默认 `consulting_navy`。
4. `python scripts/tc_render.py --list-themes` 列出全部主题。主题只改颜色，不改版面和图表。

可选主题：consulting_navy（默认，海军蓝咨询风）、thinkcell_green（think-cell 经典绿灰）、thinkcell_blue（think-cell 官网蓝阶风）、teal_modern（青绿现代风）、banking_navy_gold（投行深蓝金）、office（Office 默认主题）、mono_smoke（单色渐变）、gray_accent（灰阶+强调红）。
