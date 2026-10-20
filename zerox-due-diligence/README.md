<p align="center">
  <a href="#zh">简体中文</a> · <a href="#en">English</a>
</p>

<p align="center">
  <a href="https://github.com/ZeroxZhang/zerox-skills"><img src="https://img.shields.io/badge/GitHub-ZeroxZhang%2Fzerox--skills-181717?logo=github" alt="GitHub 仓库"></a>
  <a href="https://github.com/ZeroxZhang/zerox-skills/stargazers"><img src="https://img.shields.io/github/stars/ZeroxZhang/zerox-skills?style=flat" alt="GitHub Stars"></a>
  <a href="./scripts/README.md"><img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python 3.10+"></a>
  <a href="./SKILL.md"><img src="https://img.shields.io/badge/Agent_Skill-Due_Diligence-2563EB" alt="Agent Skill"></a>
</p>

# ZeroX Due Diligence

围绕实际决策开展公司尽调：锁定主体与控制关系，讲清公司、客户、产品和业务运转，再建立从原始资料到判断与行动的可追溯链条。默认交付图文并茂、可离线阅读的 HTML 报告，研究过程与核验记录保存在独立底稿中。

A decision-focused company research skill. Resolve the entity and control relationships, explain the company, customers, products, and how the business works, then connect source evidence to conclusions and actions. Deliver a visual, offline HTML report for readers, with research processes and verification records in a separate audit file.

## 索引 / Index

| 中文 | English |
| --- | --- |
| [核心能力](#zh-capabilities) | [Capabilities](#en-capabilities) |
| [最终报告包含什么](#zh-report) | [What the report contains](#en-report) |
| [安装与使用](#zh-install) | [Installation and use](#en-install) |
| [本地快速开始](#zh-quickstart) | [Local quick start](#en-quickstart) |
| [文件导航](#zh-files) | [Package contents](#en-files) |
| [能力边界](#zh-limits) | [Limits](#en-limits) |

---

<a id="zh"></a>
## 中文

支持**投资、并购、战略/商业合作、客户授信、供应商准入、竞品研究**六类目的，以及 **Quick / Standard / Deep** 三种深度。方法库覆盖十八个模块；单次项目按目的、行业和重要性裁剪。

<a id="zh-capabilities"></a>
### 核心能力

- **实体与控制链**：区分集团、子公司、分部、品牌和签约主体，按基准日处理参股、拟收购、出售及多层控制。
- **官网优先阅读**：目标有官网时，先确认网站归属，再直接阅读公司、产品与价格、团队、沿革、渠道和服务条款等相关页面。官网是重要的一手来源；经营宣传仍按公司自述标注，并结合独立资料核验。
- **强制上市研报流程**：上市公司及其控制子公司必须检索、合法获取并阅读相关最新官方披露、公司跟踪、公司深度与行业研究，补查重大事件。
- **三种“最新”分开**：最新发现、最新取得全文、最新已读分别记录；新报告仅有标题时，旧全文不能让研究被标为完成。
- **证据与未知分开**：来源、证据、声明和关联独立建表；预测、实际、估算和缺口不混用，同源转载不增加独立证据数量。
- **财务与评分有门槛**：缺失不自动补零，现金为零仍正确计算；商业评分、风险和证据充分程度独立呈现。
- **阅读型 HTML 主报告**：浅色留白、蓝色强调、wiki 目录导航；简要摘要后，按公司全貌 → 业务运转 → 增长、市场、财务风险与决策组织正文。
- **公司与业务必须讲清**：11 个理解主题覆盖身份、起源团队、产品、客户、交易、经营分工、收入成本、差异化、财务表现、营销与竞争。发展时间线、基于已有资料的独立人物介绍与业务图帮助理解公司，避免用工商表或宣传术语替代解释。
- **财务、营销与竞争必答**：营收规模、营收构成、毛利率和净利率分别披露主体、期间、来源与缺口；解释营销渠道及获客、转化、复购，按选择依据比较主要竞品。资料不足时逐项说明未知及其影响，不能直接省略这些主题。
- **有依据的图文表达**：关键数字通过可核验图表呈现，附单位、期间、主体、实际/预测属性、来源与数据表；无可靠数据时用定性图解释，不编造数字。
- **真实图片与比较矩阵**：可内嵌真实 logo、官网截图、产品、门店或人物图片，记录出处、本次取得日期、使用范围、图注与替代文字；竞品、渠道和财务比较逐格标注依据。图片和定性矩阵不计作定量图，也不自动证明图片中的宣传。
- **正文与底稿分层**：主报告保留重要判断和限制；模块适用性、完整台账、搜索日志、覆盖记录与请求清单进入独立 `*-audit.md`，正文引用可定位到折叠证据附录。
- **可运行的本地工具**：七个核心 Python CLI、研究与报告内容契约、CSV 台账及离线 HTML 渲染资源。

<a id="zh-report"></a>
### 最终报告包含什么

当前 HTML 内容契约为 **1.2**。主报告按读者理解公司的顺序组织，以下是推荐编排；章节名称和数量可随业务调整，必答主题仍须覆盖。

| 阅读板块 | 需要回答的问题 | 适合的呈现方式 |
| --- | --- | --- |
| 公司介绍与发展 | 它是谁、从何而来、经历了哪些业务与阶段变化？ | 公司画像、同章发展时间线、真实企业素材 |
| 创始人 / 核心合伙人 | 谁创办或经营公司，角色期间、相关经历和具体贡献是什么？ | 有足够公开资料时单设人物章节；区分创始团队与商业合作伙伴 |
| 产品、客户与业务模式 | 卖什么、卖给谁、谁付款、谁供给与交付、怎样形成收入和成本？ | 业务运转图、产品图或渠道示意 |
| 营收与盈利 | 营收规模和结构如何，毛利率、净利率是否有可比依据？ | 指标卡、趋势图、结构图或比较图，分别标明数据口径 |
| 营销与增长 | 通过哪些渠道获客，内容与投放如何作用，转化和复购有何证据？ | 渠道矩阵、营销链路；有可靠数据时绘制效果图表 |
| 主要竞争对手 | 为什么选择这些对手，同一市场与口径下有哪些差异？ | 竞争矩阵、有据的规模或定位比较图 |
| 风险与决策 | 哪些证据支持结论，哪些未知会改变判断，下一步做什么？ | 关键结论、风险说明与行动建议 |

时间线至少包含两个有日期依据的事件；确实不足时说明具体缺口。人物资料不足或真实图片不可得时如实说明，不凑履历、不用生成图冒充企业素材。财务、营销与竞争仍要逐项回答；无可靠数字时保留定性分析和限制，不绘制虚假趋势、份额或排名。

交付包含可直接打开的 `report.html`、完整研究底稿 `report-audit.md`，以及可追溯的 CSV / JSON 台账与材料。主报告保留必要引用、重要限制和折叠证据附录；搜索日志、执行过程、覆盖记录与完整核验表放入底稿。

<a id="zh-install"></a>
### 安装与使用

**当前目录就是 Skill 根目录**，入口是 [SKILL.md](./SKILL.md)。可直接让支持文件读取的 Agent 使用该文件；不需要再创建下层技能目录。

```text
请使用当前目录的 SKILL.md，对「公司法定全称 / 官网 / 注册号」开展尽调。
目的：供应商准入；深度：Standard；基准日：执行当日。
重点：交付连续性、财务状况、预付款风险与集团支持安排。
交付：可离线阅读的 HTML 主报告及独立研究底稿；讲清公司和业务模式，
呈现发展时间线，并逐项分析营收与盈利、营销渠道和主要竞争对手。
```

要让 Codex 自动发现，可把本目录的运行文件复制到 `~/.codex/skills/zerox-due-diligence/`。在当前目录执行下面的可选安装命令；目标已存在会停止，不覆盖已有 Skill：

```bash
python3 - <<'PY'
from pathlib import Path
import shutil

destination = Path.home() / ".codex" / "skills" / "zerox-due-diligence"
destination.mkdir(parents=True, exist_ok=False)
for name in ("SKILL.md", "agents", "references", "schemas", "templates", "scripts", "assets"):
    source = Path(name)
    if source.is_dir():
        shutil.copytree(source, destination / name,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    else:
        shutil.copy2(source, destination / name)
print(destination)
PY
```

安装后调用 `$zerox-due-diligence`。其他支持 `SKILL.md` 的 Agent 可按宿主的技能发现规则安装；并未声明全部宿主均已验证。

<a id="zh-quickstart"></a>
### 本地快速开始

要求 Python 3.10+。核心工具仅使用标准库，不需要 API Key，不会自动联网、购买报告或对外发送文件。

```bash
# 工作区应放在技能包之外；目标路径必须不存在。
python3 scripts/init_project.py \
  --output /tmp/dd-example \
  --target "待核验公司法定全称" \
  --purpose supplier \
  --depth Standard

# 只生成检索计划，尚未执行检索。
python3 scripts/search_plan.py \
  --project /tmp/dd-example \
  --output /tmp/dd-search-plan.json

# 实际研究、填台账和模块后，编辑生成的 report-content.json。
# 先补全公司与业务解释，再从证据中提炼主线及图表。
python3 scripts/build_report.py \
  --project /tmp/dd-example \
  --content /tmp/dd-example/report-content.json \
  --output /tmp/dd-example/reports/report.html

python3 scripts/check_report.py \
  --project /tmp/dd-example \
  --report /tmp/dd-example/reports/report.html
```

初始化只创建待核实工作区和待编辑的报告内容模板；即使提供名称或证券代码，也不会自动标记身份已核实。目的未给出时保留待确认，不计算场景综合分。生成后直接打开 `reports/report.html` 阅读；同目录的 `report-audit.md` 保存完整研究底稿。报告编排与图表规则见 [报告设计](./references/report-design.md)，字段、台账更新、财务计算和退出码见 [CLI 使用说明](./scripts/README.md)。

新建 HTML 使用1.2版内容契约。模板中的11个 `explanation` 主题须各填写一次，可自由安排章节。已知内容给依据，部分已知或未知内容说明具体限制；已有底稿中的基础信息要补回正文，缺证的部分需定向研究，不能虚构补齐。业务流程每步区分证据、公司自述、推断和未知；仅交易机制整体未知且说明原因时可免图。旧1.0/1.1 HTML仅可兼容做草稿检查，重新生成或完成态检查前须迁移。

公司时间线放在公司介绍同章；有足够公开资料时，创始人与核心合伙人另设章节。模板图片必须替换成实际取得的项目内文件，否则删除图片块；本地用户材料可记录材料出处，无需虚构网页 URL。支持 PNG/JPEG/WebP，每张 ≤5 MiB、合计 ≤15 MiB，构建时内嵌为离线内容；不需要图片 CDN，也不支持任意 SVG。

<a id="zh-files"></a>
### 文件导航

| 目录/文件 | 用途 |
| --- | --- |
| [SKILL.md](./SKILL.md) | 触发、主流程、必经门槛与直接索引 |
| [references/workflow.md](./references/workflow.md) | 阶段输入、动作、产出与失败处理 |
| [references/purpose-playbooks.md](./references/purpose-playbooks.md) | 六类目的 × 三种深度 |
| [references/modules/](./references/modules/) | 公司、团队、业务、市场、竞争、阶段、增长、政策、商业、运营、技术、财务、法律、ESG、风险、估值、履约、上市研报 |
| [references/sources/](./references/sources/) | 中外来源目录、来源策略、研报与访谈方法 |
| [schemas/data-contract.json](./schemas/data-contract.json) | 字段、类型、枚举、引用、研报类别、权重和评分锚点 |
| [references/report-design.md](./references/report-design.md) | 正文/底稿分层、编辑方法、图表与视觉验收 |
| [schemas/report-content.schema.json](./schemas/report-content.schema.json) | HTML报告内容与可视化字段契约 |
| [templates/](./templates/) | 配置、十三张CSV台账、HTML内容模型、财务输入、兼容Markdown底稿、资料请求与访谈提纲 |
| [assets/](./assets/) | 随包安装的离线报告样式等渲染资源 |
| [scripts/](./scripts/README.md) | 七个核心 CLI 及共享校验实现 |

<a id="zh-limits"></a>
### 能力边界

报告可由 [check_report.py](./scripts/check_report.py) 做结构、引用与理解主题覆盖检查，但**结构通过不证明事实真实、解释充分或研究结论正确**。交付前需让陌生读者仅靠正文回答“它是谁、卖给谁、怎样经营、怎样赚钱、关键未知是什么”。可交付明确披露未知的有限研究，不能把形式完整包装成研究完成。

核心交付为离线 HTML 主报告、Markdown 研究底稿与 CSV/JSON 台账。渲染器负责呈现已编辑内容，不能自动核验事实或替代分析。未接入 Wind、Choice、iFinD、Bloomberg 等付费数据库，未提供独立 Word/PDF 转换，也不包含自动搜索代理、访谈或交易执行。HTML可通过浏览器打印；交付前仍应检查实际打印效果。来源目录注明实际访问结果和待验证项。没有联网或授权全文时，交付受限研究和补齐路径，不能宣称“最新研报研究已完成”。

---

<a id="en"></a>
## English

Supports six purposes: **investment, acquisition, strategic/commercial partnership, customer credit, supplier qualification, and competitor research**, with **Quick / Standard / Deep** modes. Eighteen research modules are tailored to each project's purpose, industry, and materiality.

<a id="en-capabilities"></a>
### Capabilities

- **Entity and control mapping:** distinguish groups, subsidiaries, segments, brands, and contracting parties; assess minority stakes, pending acquisitions, disposals, and control chains at the research cutoff.
- **Official websites first:** when a target has a website, verify ownership and directly read relevant company, product/pricing, team, history, channel, and terms pages. Treat it as an important primary source; label promotional statements as company claims and check them against independent material.
- **Mandatory listed-company research:** listed targets and controlled subsidiaries require searches, lawful full-text acquisition, and reading of current official disclosures, company updates, in-depth coverage, industry research, and relevant event updates.
- **Three separate freshness states:** latest discovered, latest full text obtained, and latest read. An older full report cannot conceal an inaccessible newer relevant report.
- **Traceable evidence:** separate source, evidence, claim, and relationship ledgers. Keep actuals, forecasts, estimates, and missing information distinct; syndicated copies do not count as independent factual evidence.
- **Financial and scoring safeguards:** missing values are not zero; zero available cash remains a valid input. Business fit, risk, and evidence sufficiency are reported separately.
- **Reader-focused HTML reports:** a light layout with generous spacing, restrained blue accents, and wiki-style navigation. After a short summary, explain the company and how it works before growth, markets, financial risks, and decisions.
- **Company and business understanding:** eleven topics cover identity, origins and team, products, customers, transactions, operations, revenue and costs, differentiation, financial performance, marketing, and competition. A company timeline, a separate people section based on available evidence, and business diagrams support the explanation.
- **Required finance, marketing, and competition coverage:** address revenue scale, revenue mix, gross margin, and net margin individually, with entity scope, periods, sources, and gaps. Explain marketing channels, acquisition, conversion, and retention, and justify competitor selection. Disclose missing evidence and its implications instead of omitting these topics.
- **Evidence-backed visuals:** show key numerical findings in charts with units, periods, entity scope, actual/forecast labels, sources, and readable data tables. Use qualitative diagrams when reliable numbers are unavailable.
- **Real images and comparison matrices:** embed authentic logos, website screenshots, product, store, or people images with provenance, the date obtained for this research, usage scope, captions, and alternative text. Identify the evidence basis of each comparison cell. Images and qualitative matrices are not quantitative charts and do not verify promotional claims.
- **Separate reading and audit layers:** keep material conclusions and limitations in the main report. Put full modules, ledgers, logs, coverage records, and request lists in `*-audit.md`; link citations to a collapsible evidence appendix.
- **Runnable local tools:** seven Python CLIs, research and report-content contracts, CSV ledgers, and offline HTML rendering assets.

<a id="en-report"></a>
### What the report contains

The current HTML content contract is **1.2**. The report follows the reader's path to understanding the company. The structure below is recommended; section names and counts may vary, while required topics remain covered.

| Reading section | Questions it answers | Suitable presentation |
| --- | --- | --- |
| Company and development | What is the company, how did it begin, and how has its business changed? | Company profile, a timeline in the same section, authentic company imagery |
| Founders / core partners | Who founded or runs it, during which periods, with what relevant experience and contributions? | A separate people section when sufficient public material exists; distinguish founding partners from commercial partners |
| Products, customers, and business model | What is sold, to whom, who pays, who supplies and delivers, and how do revenue and costs arise? | Business diagrams, product imagery, or channel diagrams |
| Revenue and profitability | What are revenue scale and mix, and is there comparable evidence for gross and net margins? | Metric cards, trend, composition, or comparison charts with explicit scope |
| Marketing and growth | Which channels acquire customers, how do content and advertising work, and what supports conversion and retention claims? | Channel matrices, marketing flows, and performance charts when reliable data exists |
| Major competitors | Why are these competitors relevant, and how do they differ within comparable markets and definitions? | Competitor matrices and evidence-backed scale or positioning comparisons |
| Risks and decisions | What supports the conclusions, which unknowns could change them, and what should happen next? | Key findings, risk explanations, and recommended actions |

A company timeline needs at least two sourced, dated events; explain a specific shortage when they are unavailable. Disclose insufficient people information or unavailable imagery without inventing biographies or substituting generated company assets. Finance, marketing, and competition still require individual answers. Without reliable numbers, retain qualitative analysis and limitations instead of fabricating trends, shares, or rankings.

Deliverables include a directly readable `report.html`, the full `report-audit.md`, and traceable CSV / JSON ledgers and materials. Keep necessary citations, material limitations, and a collapsible evidence appendix in the main report. Store search logs, execution records, coverage tracking, and full verification tables in the audit file.

<a id="en-install"></a>
### Installation and use

**This directory is the skill root.** Start with [SKILL.md](./SKILL.md); no nested skill directory is needed here.

```text
Use SKILL.md in the current directory to investigate:
Target: legal company name / website / registration number.
Purpose: supplier qualification. Depth: Standard. Cutoff: today's date.
Focus: delivery continuity, financial condition, prepayment exposure,
and actual parent-company support. Write the report in English.
Deliver an offline HTML report and a separate audit file. Explain the company
and business model, show its development timeline, and address revenue and
profitability, marketing channels, and major competitors individually.
```

For Codex discovery, optionally copy the runtime files into `~/.codex/skills/zerox-due-diligence/`. Run the following from this directory. It stops if the destination already exists:

```bash
python3 - <<'PY'
from pathlib import Path
import shutil

destination = Path.home() / ".codex" / "skills" / "zerox-due-diligence"
destination.mkdir(parents=True, exist_ok=False)
for name in ("SKILL.md", "agents", "references", "schemas", "templates", "scripts", "assets"):
    source = Path(name)
    if source.is_dir():
        shutil.copytree(source, destination / name,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    else:
        shutil.copy2(source, destination / name)
print(destination)
PY
```

Then invoke `$zerox-due-diligence`. Other agents that support `SKILL.md` may use their own discovery conventions; compatibility with every host has not been tested. The methodology, templates, and CLI messages are primarily Chinese; the agent can adapt the report language.

<a id="en-quickstart"></a>
### Local quick start

Requires Python 3.10+. Core tools use only the standard library, require no API key, and do not automatically browse, buy reports, or transmit files.

```bash
python3 scripts/init_project.py \
  --output /tmp/dd-example \
  --target "Company legal name to verify" \
  --purpose supplier \
  --depth Standard

python3 scripts/search_plan.py \
  --project /tmp/dd-example \
  --output /tmp/dd-search-plan.json

# After research, explain the company and business in report-content.json, then add analysis and charts.
python3 scripts/build_report.py \
  --project /tmp/dd-example \
  --content /tmp/dd-example/report-content.json \
  --output /tmp/dd-example/reports/report.html

python3 scripts/check_report.py \
  --project /tmp/dd-example \
  --report /tmp/dd-example/reports/report.html
```

Keep research workspaces outside this skill package. Initialization creates pending records; a supplied name or ticker is not verified identity. Search planning does not execute searches. Complete the research, ledgers, and module analyses, then edit `report-content.json` into a reader-focused narrative with verified chart data before building the deliverable. An unspecified purpose stays pending and disables purpose-specific overall scoring.

Open `reports/report.html` directly to read the report. The sibling `report-audit.md` contains the full research record. See the [report design guide](./references/report-design.md) for editorial and chart requirements, and the [CLI guide](./scripts/README.md) for ledger updates, financial inputs, configuration, and exit codes.

New HTML builds require content contract 1.2. Complete each of the eleven `explanation` topics once, arranged into suitable sections. Cite known information and describe specific limitations for partial or unknown answers. Restore relevant facts omitted from existing research; investigate actual evidence gaps rather than inventing answers. Each business-flow step distinguishes evidence, company claims, inference, and unknowns. The diagram may be omitted only when the transaction mechanism is unknown and the reason is explained. Legacy 1.0/1.1 HTML remains readable by draft checks; migrate before rebuilding or requesting completed-mode checks.

Keep the company timeline in the company overview section. Introduce founders and core partners in a separate section when sufficient public material exists. Replace template images with actual project files or remove those blocks; user-provided local materials may cite their provenance without inventing a web URL. PNG/JPEG/WebP files are embedded for offline reading, limited to 5 MiB each and 15 MiB in total; arbitrary SVG and runtime image downloads are unsupported.

<a id="en-files"></a>
### Package contents

| Path | Purpose |
| --- | --- |
| [SKILL.md](./SKILL.md) | Entry point, workflow, mandatory gates, and resource index |
| [references/workflow.md](./references/workflow.md) | Phase inputs, actions, outputs, and failure handling |
| [references/purpose-playbooks.md](./references/purpose-playbooks.md) | Six purposes × three depths |
| [references/modules/](./references/modules/) | Eighteen company, business, industry, financial, legal, operational, and listed-company research modules |
| [references/sources/](./references/sources/) | China/global source directories, research and interview methods |
| [schemas/data-contract.json](./schemas/data-contract.json) | Fields, types, enums, references, research categories, weights, and scoring anchors |
| [references/report-design.md](./references/report-design.md) | Reading/audit layers, editorial guidance, chart rules, and visual review |
| [schemas/report-content.schema.json](./schemas/report-content.schema.json) | HTML report content and visualization fields |
| [templates/](./templates/) | Configuration, thirteen CSV ledgers, HTML content model, financial inputs, legacy Markdown audit reports, requests, and interview outline |
| [assets/](./assets/) | Offline report styles and rendering resources installed with the skill |
| [scripts/](./scripts/README.md) | Seven core CLIs and shared validation |

<a id="en-limits"></a>
### Limits

Reports can be checked for structure, references, and understanding-topic coverage with [check_report.py](./scripts/check_report.py), but **passing does not establish factual truth, sufficient explanation, or correct conclusions.** Before delivery, check whether a new reader can explain who the company is, whom it serves, how it operates, how it earns money, and what remains unknown using only the main report. A limited report may disclose real unknowns; formal completeness must not imply completed research.

Core outputs are an offline HTML reading report, a Markdown audit file, and CSV/JSON ledgers. The renderer presents edited content; it does not verify facts or replace analysis. No paid database integrations, standalone Word/PDF export, automated research crawler, interview execution, or transaction execution are included. Browser printing is available for HTML, and its actual layout still requires review. Source directories distinguish successful entry-page reads from failed or unverified access. Offline or restricted research must disclose limitations and acquisition steps; it cannot claim the latest-report requirement is complete.
