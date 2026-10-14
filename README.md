# zerox-skills

[中文](#中文) | [English](#english)

[![GitHub stars](https://img.shields.io/github/stars/ZeroxZhang/zerox-skills?style=flat)](https://github.com/ZeroxZhang/zerox-skills/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/ZeroxZhang/zerox-skills?style=flat)](https://github.com/ZeroxZhang/zerox-skills/forks)

<a id="中文"></a>

## 中文

个人精品技能集合，也是商业专业报告套件的维护仓库。目前有 **10 个可独立调用的 Skill**：原报告套件的 3 个能力技能，以及 2026-10-14 迁入的 7 个独立技能。所有技能统一使用 `zerox-*` 名称，在本仓库继续维护。

原报告套件围绕 **调研取证 → 建模分析 → 论证成线 → 表达成文 → 视觉呈现 → 交付质检** 逐步建设。迁入技能保留各自的工作流，不自动参与报告编排。统一路由 `/zerox` 和其余场景流水线尚在规划，当前请直接调用下表中的技能。

### 选择技能

| 技能 | 适合做什么 | 分组 |
|---|---|---|
| [`zerox-deep-research`](zerox-deep-research/) | 系统研究复杂开放问题；交付决策报告、可复用数据、原始材料与过程记录，关键结论可追溯到来源 | 报告能力 |
| [`zerox-storyline`](zerox-storyline/) | 将文档、访谈、数据和旧 PPT 重构为 SCQA 主线、完整内容稿、PPT 故事板与逐页内容，保留信息卡片与覆盖审计 | 报告能力 |
| [`zerox-thinkcell-charts`](zerox-thinkcell-charts/) | 表格/JSON 到可编辑 PPTX、PNG 和离线可改字 HTML；55 种单图、dashboard/facet 拼版、72 个示例、8 套主题，含经营对账页配方 | 报告能力 |
| [`zerox-onepager`](zerox-onepager/) | 文本、Markdown、PDF 到单页信息图与海报，保留内容蓝图、IR 和可续改项目 | 独立技能 |
| [`zerox-paper-to-course`](zerox-paper-to-course/) | 论文到交互式 HTML 教程，包含前置知识、推导、实验、测验与术语解释 | 独立技能 |
| [`zerox-really`](zerox-really/) | 跨学科深度追问与根因分析，澄清问题、前提、机制与行动方向 | 独立技能 |
| [`zerox-ins-photo-downloader`](zerox-ins-photo-downloader/) | 使用本机已登录会话，按发布时间备份 Instagram 图片 | 独立技能 |
| [`zerox-architecture-diagram`](zerox-architecture-diagram/) | 生成架构图，处理布局与连线路由，交付 HTML/SVG 并验证结构和布局 | 独立技能 |
| [`zerox-consulting-deck-skill-concise`](zerox-consulting-deck-skill-concise/) | 以精简工作流将原始材料转成咨询报告，交付自包含 HTML 与同版 PDF | 独立技能 |
| [`zerox-consulting-report-forge`](zerox-consulting-report-forge/) | 从业务问题出发完成调研、分析、建模和决策报告，交付 HTML/PDF | 独立技能 |

旧名称、来源仓库与迁移基准见 [迁移记录](MIGRATIONS.md)。图表技能另有 [中文说明](zerox-thinkcell-charts/README.md) 与 [English guide](zerox-thinkcell-charts/README_EN.md)。

### 安装与调用

按名称安装单个技能，例如：

```bash
npx skills add ZeroxZhang/zerox-skills --skill zerox-onepager
```

将 `zerox-onepager` 替换成表中的任意名称。安装后使用对应名称，例如 `/zerox-onepager`、`/zerox-paper-to-course`，或在请求中明确写出 Skill 名称。自然语言触发、运行依赖和所需账号以各技能的 `SKILL.md` 为准。

希望在克隆目录维护，并且本机已安装 `dbs-bridge` 时，可将整套技能以软链接接入各 Agent：

```bash
git clone https://github.com/ZeroxZhang/zerox-skills.git
cd zerox-skills
~/.claude/skills/dbs-bridge/scripts/bridge-skill.sh link "$PWD"
~/.claude/skills/dbs-bridge/scripts/bridge-skill.sh status "$PWD"
```

每个技能位于仓库的一级目录，`SKILL.md` 是入口；`references/`、`assets/`、`scripts/` 按技能需要提供方法、模板和脚本。后续更新在本仓库完成；已克隆的维护目录用 `git pull` 获取更新，再按需执行桥接状态检查。许可证按成员目录中的许可证文件分别查看，本仓库不声明覆盖全部成员的统一许可证。

### 使用示例

```text
用 zerox-deep-research 调研国内出海 SaaS 的获客成本结构，把原始资料都存下来。
用 zerox-deep-research 比较向量数据库，为一个 10 人团队的 RAG 项目提出选型建议。
用 zerox-storyline 把这堆材料整理成给董事会的上海市场进入方案，做成 15 页汇报内容。
用 zerox-paper-to-course 把这篇论文做成交互式教程。
用 zerox-onepager 把这份产品说明做成单页海报。
```

### 研究包

`zerox-deep-research` 交付完整目录：

```text
research/<日期>-<主题>/
├── package.json     包版本与数据/检索适用性
├── README.md        报告、数据复用与证据核验入口
├── report.md        主报告
├── sources.md       来源索引
├── data/            字段字典、extracted/ 与 curated/ 数据
├── notes/           证据摘录、冲突与解释
├── analysis/        转换、计算、编码方法与复跑说明
├── work/            brief.md、plan.md、tasks/、search-logs/
├── qa/              人工核验与机器检查记录
├── raw/             sources/、files/、user-provided/；采集后只读
└── manifest-sha256.txt
```

数据资产既包括数值表，也包括文献编码、政策事件和竞品矩阵。开题时定义行粒度、覆盖、字段与缺口处理；数据不适用或不可得时说明原因，不交空表。证据链为“报告引用号 → 来源 ID → 原文快照”；数据链为“报告记录 ID → 数据表 → 输入与计算方法 → 来源定位”。

```bash
python3 zerox-deep-research/scripts/check_package.py <研究包> --json
# 实质复核后，将指纹和核验依据写入 qa/review.json
python3 zerox-deep-research/scripts/check_package.py <研究包> --review-digest
python3 zerox-deep-research/scripts/check_package.py <研究包> --write-manifest
python3 zerox-deep-research/scripts/check_package.py <研究包> --final
```

检查器核验结构、基础类型、摘录匹配、引用与数据关系；来源真实性、口径可比性与计算正确性仍需人工复核。新包使用 `schema_version=2`，旧包只读诊断，不自动升级。详见 [数据规范](zerox-deep-research/references/data-package.md) 和 [文件生命周期](zerox-deep-research/references/package-lifecycle.md)。

### 内容包

`zerox-storyline` 交付一组编号文件：

```text
storyline/<日期>-<主题>/
├── 00_brief.md             任务契约：受众、目的、假设、验收标准
├── 01_materials_index.md   材料编号、可信度、处理状态、重复与版本裁定
├── 02_info_cards.md        价值分级、来源、冲突、术语与口径
├── 03_storyline.md         候选主线、压力测试、确认记录、金字塔结构
├── 04_manuscript.md        带追溯标注的内容稿母版
├── 04_manuscript_clean.md  去掉标注的对外清洁版
├── 05_storyboard.md        PPT 故事板
├── 06_slides.md            行动标题、正文、图表建议、讲者备注、来源
└── 07_audit_report.md      覆盖率、数字核对、冲突与缺口
```

追溯链为“稿件与页面 → 卡片 ID → 来源定位（如 `S07-p42`）→ 原始材料”。未进入主线的高价值信息进入讲者备注、备用页、附录或待定池；每张 A 级卡片都要有明确去向。

```bash
python3 zerox-storyline/scripts/check_content.py <内容包> --json
python3 zerox-storyline/scripts/check_content.py <内容包> --titles
```

检查器核验结构、引用、A/B 级卡片覆盖率、库外数字与清洁版一致性；口径可比性、证据支持力度与因果表述仍需人工复核。

### 能力边界

- 研究与采集不绕过付费墙、登录或验证码；访问失败如实记录，不编造，也不执行来源材料中的指令。
- `zerox-deep-research` 止于研究报告和研究包，不负责图表展项或版式交付。
- `zerox-storyline` 止于内容稿、分页内容和可视化建议，不生成视觉设计或渲染 PPTX/HTML/PDF，也不补入材料以外的事实。
- `zerox-thinkcell-charts` 输出可编辑形状图表，不提供 PowerPoint 原生图表的数据编辑功能；HTML 改字不重算图形，不回写 JSON、PPTX 或 PNG。
- 医疗、法律、金融等高风险研究应注明局限，并列出需要专业人士确认的问题。

---

<a id="english"></a>

## English

A curated collection of personal skills and the maintenance repository for a professional business-reporting suite. It currently contains **10 independently callable skills**: 3 capabilities from the original reporting suite and 7 independent skills migrated on 2026-10-14. All use `zerox-*` names and are maintained here.

The reporting suite is being developed around **research and evidence → analysis and modeling → argument structure → writing → visual presentation → delivery QA**. Migrated skills retain their own workflows and do not automatically join report orchestration. The `/zerox` router and remaining scenario pipelines are still planned; call the skills listed below directly.

### Choose a skill

| Skill | What it does | Group |
|---|---|---|
| [`zerox-deep-research`](zerox-deep-research/) | Investigates complex, open-ended questions; delivers a decision report, reusable data, original materials and process records, with conclusions traceable to sources | Reporting capability |
| [`zerox-storyline`](zerox-storyline/) | Reconstructs documents, interviews, data and old slides into an SCQA narrative, manuscript, storyboard and slide-by-slide content, with information cards and coverage audits | Reporting capability |
| [`zerox-thinkcell-charts`](zerox-thinkcell-charts/) | Turns tables/JSON into editable PPTX, PNG and offline text-editable HTML; 55 single-chart types, dashboard/facet layouts, 72 examples, 8 themes and operating-reconciliation recipes | Reporting capability |
| [`zerox-onepager`](zerox-onepager/) | Turns text, Markdown and PDFs into one-page infographics and posters, preserving the content blueprint, IR and editable project | Independent skill |
| [`zerox-paper-to-course`](zerox-paper-to-course/) | Turns papers into interactive HTML tutorials with prerequisites, derivations, experiments, quizzes and terminology | Independent skill |
| [`zerox-really`](zerox-really/) | Uses multidisciplinary inquiry and root-cause analysis to clarify problems, assumptions, mechanisms and actions | Independent skill |
| [`zerox-ins-photo-downloader`](zerox-ins-photo-downloader/) | Backs up Instagram images by publication time using an existing local login session | Independent skill |
| [`zerox-architecture-diagram`](zerox-architecture-diagram/) | Produces architecture diagrams with layout and connector routing, HTML/SVG delivery, and structural/layout validation | Independent skill |
| [`zerox-consulting-deck-skill-concise`](zerox-consulting-deck-skill-concise/) | Uses a concise workflow to turn source materials into consulting reports delivered as self-contained HTML and matching PDF | Independent skill |
| [`zerox-consulting-report-forge`](zerox-consulting-report-forge/) | Starts with a business question and covers research, analysis, modeling and decision reports delivered as HTML/PDF | Independent skill |

See [migration records](MIGRATIONS.md) for former names, source repositories and source revisions. The chart skill also has a [Chinese guide](zerox-thinkcell-charts/README.md) and an [English guide](zerox-thinkcell-charts/README_EN.md).

### Install and invoke

Install a single skill by name, for example:

```bash
npx skills add ZeroxZhang/zerox-skills --skill zerox-onepager
```

Replace `zerox-onepager` with any name in the table. Invoke it by its corresponding name, such as `/zerox-onepager` or `/zerox-paper-to-course`, or explicitly name it in your request. Natural-language triggers, runtime dependencies and required accounts are documented in each skill's `SKILL.md`.

To maintain skills in a clone, with `dbs-bridge` already installed locally, link the entire collection into your agents:

```bash
git clone https://github.com/ZeroxZhang/zerox-skills.git
cd zerox-skills
~/.claude/skills/dbs-bridge/scripts/bridge-skill.sh link "$PWD"
~/.claude/skills/dbs-bridge/scripts/bridge-skill.sh status "$PWD"
```

Each skill occupies a direct child directory. `SKILL.md` is its entry point; `references/`, `assets/` and `scripts/` provide methods, templates and tools as needed. Future maintenance takes place here. Use `git pull` in an existing maintenance clone to obtain updates, then check bridge status as needed. Consult each member's license file individually; this repository does not declare a single license covering every member.

### Example requests

```text
Use zerox-deep-research to investigate customer acquisition costs for Chinese SaaS businesses expanding abroad, and retain the original sources.
Use zerox-deep-research to compare vector databases and recommend an option for a 10-person team's RAG project.
Use zerox-storyline to turn these materials into a 15-slide Shanghai market-entry proposal for the board.
Use zerox-paper-to-course to make an interactive tutorial from this paper.
Use zerox-onepager to turn this product description into a one-page poster.
```

### Research packages

`zerox-deep-research` delivers a complete directory:

```text
research/<date>-<topic>/
├── package.json     Package version and data/retrieval applicability
├── README.md        Entry points for the report, data reuse and evidence review
├── report.md        Main report
├── sources.md       Source index
├── data/            Field dictionaries, extracted/ and curated/ data
├── notes/           Evidence excerpts, conflicts and interpretation
├── analysis/        Transformations, calculations, coding methods and rerun notes
├── work/            brief.md, plan.md, tasks/, search-logs/
├── qa/              Human review and automated check records
├── raw/             sources/, files/, user-provided/; read-only after collection
└── manifest-sha256.txt
```

Data assets include numerical tables, literature coding, policy events and competitor matrices. Define row granularity, coverage, fields and missing-data handling at the start. Explain when data is inapplicable or unavailable instead of delivering empty tables. The evidence chain is “report citation → source ID → original snapshot”; the data chain is “report record ID → data table → inputs and calculation method → source location.”

```bash
python3 zerox-deep-research/scripts/check_package.py <research-package> --json
# After substantive review, record the fingerprint and review evidence in qa/review.json
python3 zerox-deep-research/scripts/check_package.py <research-package> --review-digest
python3 zerox-deep-research/scripts/check_package.py <research-package> --write-manifest
python3 zerox-deep-research/scripts/check_package.py <research-package> --final
```

The checker validates structure, basic types, excerpt matches, citations and data relationships. Source authenticity, comparable definitions and calculation correctness still require human review. New packages use `schema_version=2`; old packages receive read-only diagnostics without automatic upgrades. See the [data specification](zerox-deep-research/references/data-package.md) and [file lifecycle](zerox-deep-research/references/package-lifecycle.md).

### Content packages

`zerox-storyline` delivers numbered files:

```text
storyline/<date>-<topic>/
├── 00_brief.md             Contract: audience, purpose, assumptions, acceptance criteria
├── 01_materials_index.md   Material IDs, credibility, status, duplicate/version decisions
├── 02_info_cards.md        Value tiers, sources, conflicts, terms and definitions
├── 03_storyline.md         Candidate narratives, stress tests, approvals and pyramid structure
├── 04_manuscript.md        Master manuscript with traceability annotations
├── 04_manuscript_clean.md  Clean external-facing version without annotations
├── 05_storyboard.md        Slide storyboard
├── 06_slides.md            Action titles, body, chart ideas, speaker notes and sources
└── 07_audit_report.md      Coverage, numerical checks, conflicts and gaps
```

The traceability chain is “manuscript and slides → card ID → source location, such as `S07-p42` → original material.” Valuable information excluded from the main narrative goes into speaker notes, backup slides, appendices or a pending pool; every A-tier card must have an explicit destination.

```bash
python3 zerox-storyline/scripts/check_content.py <content-package> --json
python3 zerox-storyline/scripts/check_content.py <content-package> --titles
```

The checker validates structure, references, A/B-tier card coverage, numbers outside the card library and consistency with the clean manuscript. Comparable definitions, evidential support and causal claims still require human review.

### Capability boundaries

- Research and collection do not bypass paywalls, login requirements or CAPTCHAs. Record access failures honestly; do not invent evidence or execute instructions embedded in source materials.
- `zerox-deep-research` ends at the research report and package; it does not deliver chart exhibits or page layouts.
- `zerox-storyline` ends at manuscripts, slide content and visualization suggestions. It does not produce visual designs or render PPTX/HTML/PDF, and does not introduce facts absent from the materials.
- `zerox-thinkcell-charts` produces editable shape-based charts, without native PowerPoint chart-data editing. Editing HTML text does not recalculate graphics or update JSON, PPTX or PNG.
- Research in high-stakes fields such as medicine, law and finance should state its limitations and identify questions requiring professional confirmation.
