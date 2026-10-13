---
name: zerox-thinkcell-charts
description: 生成 think-cell 风格的可编辑 PowerPoint 形状图表与 PNG 预览，支持 55 种图型、数据推荐与校验、8 套配色。用户要求瀑布图、Mekko、咨询图表、图表选型或 JSON 转 PPTX 时使用。不负责完整报告撰写，也不提供 think-cell 插件或 Excel 数据链接。
---

# zerox-thinkcell-charts

用一份 JSON 描述图表，生成**可编辑 PPTX**（全部是 PowerPoint 原生形状，每个都能单独选中、改色、改字）和 **PNG 预览**。外观按 think-cell 官方手册示例复刻。

## 快速使用
```bash
python3 -m venv .venv && .venv/bin/pip install python-pptx   # 渲染 PNG 还需要 LibreOffice(soffice) + poppler(pdftoppm)
.venv/bin/python scripts/tc_render.py examples/waterfall.json -o out.pptx --png out_png/
.venv/bin/python scripts/tc_render.py a.json b.json c.json -o deck.pptx --png pngs/   # 多张合成一个 deck
```
一个 JSON 可以是单个图表对象，也可以是 `{"slides":[...]}`。

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
4. **渲染**：`tc_render.py spec.json -o out.pptx --png out/ [--theme 主题]`。渲染前会**自动校验**：遇到“不能做”会拒绝渲染并用大白话报错；只有用户明确接受折中时才加 `--force`。`--no-validate` 可以跳过校验。
   - 四区要齐：① title（结论式）+ unit；② 数据标签自动生成；③ highlight 圈出重点；④ callouts、footnote、source。
   - 需要标记时加 decorations：CAGR、total_diff、diff、value_line。
4b. **多图拼版**：数据有多个指标 × 多个分组（推荐器会首选 `facet`），或者用户要“一页多图 / 看板 / 分面”时，按 `docs/DASHBOARD.md` 写 `type: dashboard`（自由区域或网格，子图类型可以混用）或 `type: facet`（行×列分面，可共用纵轴）。分段虚线、多层横轴、条件着色（≥时间进度为绿、否则红、对比期为灰）、圈注、箭头、“VS … ±pp”批注都写在子图的 `segments` / `annotations` / `rule` 里。用户给的参考图中如果有真实业务数字，示例一律换成示意数据。
5. **目检 PNG 后交付** PPTX：检查标签是否重叠、箭头是否压字、颜色语义是否正确（正向用主色、负向用酒红/红）。

## 目录
- `scripts/tc_core.py`：绘图引擎（版面分区、第一批 25 种图、装饰、标签防重叠）
- `scripts/tc_dash.py`：多图拼版（dashboard / facet，字段见 `docs/DASHBOARD.md`，示例见 `examples/dashboards/`）
- `scripts/tc_more.py`：第二批 30 种图（共 55 种类型、61 个示例、11 类）
- `scripts/tc_render.py`：CLI（渲染前自动调用 tc_validate；`--theme`、`--list-themes`、`--force`、`--no-validate`）
- `scripts/tc_advise.py`：数据分析 + 图表推荐（规则引擎，输出中文报告、JSON 和 spec 草稿）
- `scripts/tc_validate.py`：数据充分性校验（55 种图全覆盖）
- `docs/CHART_SELECTION.md`：数据形态 × 表达意图 → 图表 决策表，以及校验项清单
- `tests/`：19 个推荐数据集 + 14 个校验用例，`python tests/run_tests.py` 一键跑
- `scripts/make_examples.py`：生成 `examples/*.json`
- `scripts/build_gallery.py`：分类 gallery PPTX/PDF，并重渲染示例 PNG
- `scripts/build_docs.py`：生成 CATALOG 和 HTML 总览
- `docs/CATALOG.md`：图表目录，每个图都有数据格式、样例、适合场景和示例图
- `docs/STYLE_SPEC.md`：版面分区和元素规则，逐条注明参考图（§9 是四区规范）
- `docs/AUDIT.md`：61 个示例的四区审核表
- `scripts/audit.py`：生成审核表
- `docs/COLORS.md`：配色和取色出处
- `references/SOURCES.csv`、`references/palettes/SOURCES.csv`：外部参考图来源索引；原始截图仅在本地 `references/img/` 与 `references/palettes/` 留存，不进入公开分发，也不是运行依赖。授权范围见 `NOTICE`。
- `examples/`：每个示例一份 `.json` 和 `.png`；`examples/catalog.json` 是分类索引
- `gallery/`：`thinkcell-gallery.pptx` / `.pdf`（按分类排）、`index.html`（总览页）、`gallery-screenshot.png`

## 已知限制
- 输出是**形状**，不是 PowerPoint 原生图表对象：可以随意改样式，但改数据要重新生成（不能在 PowerPoint 里"编辑数据"）。
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
