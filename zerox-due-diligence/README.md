<p align="center">
  <a href="#zh">中文</a> · <a href="#en">English</a>
</p>

# Zerox Due Diligence

<p>
  <a href="https://github.com/ZeroxZhang/zerox-skills"><img src="https://img.shields.io/badge/GitHub-ZeroxZhang%2Fzerox--skills-181717?logo=github" alt="GitHub repository"></a>
  <a href="https://github.com/ZeroxZhang/zerox-skills/stargazers"><img src="https://img.shields.io/github/stars/ZeroxZhang/zerox-skills?style=flat" alt="GitHub stars"></a>
  <a href="./scripts/README.md"><img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python 3.10+"></a>
  <a href="./SKILL.md"><img src="https://img.shields.io/badge/Agent_Skill-Company_%26_Brand_Research-2563EB" alt="Company and brand research skill"></a>
</p>

**从一个公司或品牌名出发，讲清背后是谁、业务怎样运转、钱从哪里来，以及哪些问题仍无法判断。**

**Start with a company or brand name. Understand who is behind it, how the business works, where its money comes from, and what remains unknown.**

<a id="zh"></a>
## 中文

这是一个面向 AI Agent 的公司与品牌研究技能。它提供研究方法、证据记录、计算和报告工具，帮助 Agent 从原始材料形成可追溯的判断，交付**可离线阅读的 HTML 主报告、独立研究底稿和结构化证据台账**。

可以只为了解一家公司而使用，也可以围绕投资、并购、战略或商业合作、客户授信、供应商准入、竞品研究开展专项。公司研究默认不打综合分；专项评分也只在明确需要时启用。

[看示例](#zh-example) · [研究能力](#zh-capabilities) · [安装与使用](#zh-use) · [运行工具](#zh-tools) · [能力边界](#zh-limits) · [文档导航](#zh-docs)

<a id="zh-example"></a>
### 先看一份完整报告

**枝间茶铺：从消费品牌追溯到经营公司，再研究业务、营销、竞争和营收区间。**

[HTML 主报告](./examples/branch-tea/reports/report.html) · [研究底稿](./examples/branch-tea/reports/report-audit.md) · [示例说明与原材料](./examples/README.md) · [可编辑报告内容](./examples/branch-tea/report-content.json)

在 GitHub 上，HTML 链接展示的是文件源码；下载或克隆仓库后，用浏览器打开即可阅读，无需启动服务。报告内置目录、图表和折叠证据附录，支持桌面、移动端阅读及浏览器打印为 PDF。

示例中的公司、品牌、人物、资料与数字**全部虚构**，仅演示方法。它分别识别品牌、商标权利人、经营公司和控制方，用两种方法得到营收估算区间，并保留未能回答的利润与现金问题，因此状态为 `limited`。估算区间重叠不代表它成为真实财务数据。

<a id="zh-capabilities"></a>
### 它能帮你研究什么

| 你想弄清的问题 | 技能怎样处理 |
| --- | --- |
| **这个品牌背后究竟是谁？** | 从商标、官网归属、用户协议、收款方及产品资料追溯经营主体；区分商标权利人、授权方、代工方、经销方与控制集团，避免把品牌或集团数据当作目标公司数据。 |
| **这家公司怎样经营和赚钱？** | 解释产品、客户、付款人、供应与交付、收入和成本，串起发展时间线与团队角色；分别回答营收规模、构成、毛利率和净利率，未知就说明原因及影响。 |
| **增长、品牌和竞争力有依据吗？** | 分析获客、转化、复购、价格与折扣、用户口碑及替代选择；比较管理层过去的承诺与后续结果，区分公司宣传、用户信号和经营实绩。 |
| **关键数字没有披露怎么办？** | 用门店、渠道、人效、用户或产能等不同方法估算区间；核对输入证据与来源独立性，显式保留假设和方法冲突。缺少独立依据时保留缺口。 |
| **结论经得起追问吗？** | 以 3–5 个关键问题组织研究，比较替代解释并寻找反证；分别记录原始来源、证据、声明及关联，同源转载不重复计算为独立佐证。 |
| **最终能否让人读懂并复核？** | 用业务图、时间线、数据图和比较矩阵解释公司；正文呈现判断、引用和重要限制，完整台账、搜索与阅读记录进入独立底稿。 |

18 个研究模块按目的、行业和问题裁剪，报告章节围绕读者需要组织。通常依次讲清：**公司与发展 → 创始人及核心团队 → 产品、客户与业务模式 → 营收与盈利 → 营销与品牌 → 主要竞争对手 → 风险与下一步**。材料不足的主题说明缺口，不靠凑字数或编造图表补齐。

目标有官网时，先确认归属并直接阅读相关页面。目标或其经营主体上市、受上市公司控制时，必须检索并争取合法取得、阅读相关最新官方披露及公司、行业研报；最新发现、最新全文和最新已读分别记录。

<a id="zh-use"></a>
### 安装与使用

**直接使用仓库文件**

```bash
git clone https://github.com/ZeroxZhang/zerox-skills.git
cd zerox-skills/zerox-due-diligence
```

当前目录就是技能根目录。让支持本地文件读取的 Agent 加载 [SKILL.md](./SKILL.md)，再给出研究对象、目的和重点即可。已有本地仓库时直接进入该目录。

**安装到 Codex**

下面的可选命令将运行文件和完整示例复制到 `~/.codex/skills/zerox-due-diligence/`。从技能根目录运行；目标已存在时停止，不覆盖已有安装。

<details>
<summary>展开安装命令（Python 3.10+）</summary>

```bash
python3 - <<'PY'
from pathlib import Path
import shutil

names = ("SKILL.md", "agents", "references", "schemas", "templates", "scripts", "assets", "examples")
missing = [name for name in names if not Path(name).exists()]
if missing:
    raise SystemExit(f"Incomplete skill package: {missing}")
destination = Path.home() / ".codex" / "skills" / "zerox-due-diligence"
destination.mkdir(parents=True, exist_ok=False)
try:
    for name in names:
        source = Path(name)
        if source.is_dir():
            shutil.copytree(source, destination / name,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        else:
            shutil.copy2(source, destination / name)
except Exception:
    shutil.rmtree(destination)
    raise
print(destination)
PY
```

</details>

安装后用 `$zerox-due-diligence` 调用。其他支持 `SKILL.md` 的 Agent 按各自宿主规则安装；本项目不宣称所有宿主均已验证。

**可以这样提问**

```text
使用 $zerox-due-diligence 全面研究「公司法定名称 / 官网」。
目的：公司研究；深度：Standard；基准日：执行当日。
重点讲清业务模式、客户为何购买、营收与盈利、营销渠道和主要竞争对手。
交付可离线阅读的 HTML 报告及独立研究底稿。
```

```text
使用 $zerox-due-diligence 研究品牌「品牌名」。
先查明商标权利人、经营公司和控制方，再研究它怎样经营和赚钱。
补充用户口碑、定价与折扣；没有披露的关键数字，评估能否有依据地估算。
```

```text
使用 $zerox-due-diligence 评估「公司名」能否成为我们的核心供应商。
重点：交付与质量是否稳定、预付款风险、关键依赖和替代供应安排。
按 Standard 深度研究，说明目前能判断什么、还需取得哪些材料。
```

研究深度与资料访问权限分开选择：

| 深度 | 适合的研究范围 |
| --- | --- |
| **Quick** | 建立简要公司画像，回答最重要的问题，识别关键变化、重大风险与未知。 |
| **Standard** | 展开重点业务、历史变化、竞争和财务机制，对关键判断交叉验证。 |
| **Deep** | 沿关键问题增加历史跨度及业务、客户、区域粒度，做更细核验与情景分析。 |

深度不按篇幅或搜索次数定义。选择 Deep 不会自动获得数据库、访谈或数据室权限；关键材料缺失仍会限制结论。详细裁剪见[目的与深度说明](./references/purpose-playbooks.md)。

<a id="zh-tools"></a>
### 运行本地工具

核心脚本要求 **Python 3.10+，仅使用标准库**。它们负责记录、计算、渲染和检查；实际检索、阅读与判断由 Agent 执行。

**先复现示例**：下面的 macOS / Linux 命令把示例复制到新临时目录，再重建与检查报告；不会改写仓库中的示例。

```bash
demo_dir="$(mktemp -d "${TMPDIR:-/tmp}/zerox-dd-demo.XXXXXX")"
cp -R examples/branch-tea "$demo_dir/project"
python3 scripts/build_report.py \
  --project "$demo_dir/project" \
  --content "$demo_dir/project/report-content.json" \
  --output "$demo_dir/project/reports/report.html" --overwrite
python3 scripts/check_report.py \
  --project "$demo_dir/project" \
  --report "$demo_dir/project/reports/report.html" --mode draft
printf '\nReport: %s\n' "$demo_dir/project/reports/report.html"
```

预期 `draft` 检查无错误，报告仍为受限状态。关于真实企业图片缺失及口径人工复核的提示是预期行为，详见[示例说明](./examples/README.md)。

**开始真实研究**：从技能根目录创建包外工作区，输出路径必须尚不存在。

```bash
python3 scripts/init_project.py \
  --output /tmp/zerox-dd-company \
  --target "待核验公司法定名称" \
  --purpose company_research --depth Standard

# 先编辑 project-config.json 中的 key_questions，再生成检索计划。
python3 scripts/search_plan.py \
  --project /tmp/zerox-dd-company \
  --output /tmp/zerox-dd-company/search-plan.json
```

品牌目标加 `--target-type brand`。初始化只建立待核实台账和待编辑模板，检索计划也不代表已经搜索。接下来按[工作流](./references/workflow.md)完成资料获取、证据记录和分析，再编辑 `report-content.json`、构建主报告及底稿。台账、财务计算、区间估算与完整命令见 [CLI 使用说明](./scripts/README.md)。

<a id="zh-limits"></a>
### 能力边界

- **有证据才下结论。** 实际、预测、估算和未知分别标注；估算区间来自输入假设与区间运算，不是统计置信区间，也不是审计后的财务数据。
- **脚本不替代研究。** 工具不自动联网搜索、购买资料或执行访谈，不自带付费数据库；资料访问取决于 Agent 环境及已有授权。
- **检查通过不等于研究完成。** 自动检查覆盖结构、引用和部分一致性；原文含义、可比口径、因果解释与结论仍须实质复核。关键问题无法回答时保留受限状态，资料获取与阅读覆盖另行记录。
- **图文必须有依据。** 使用真实企业图片时记录来源与使用范围；虚构示例不拿生成图片冒充真实素材。HTML 可离线阅读，PDF 通过浏览器打印生成，不提供原生 Word 导出。

<a id="zh-docs"></a>
### 文档导航

| 文档 | 用途 |
| --- | --- |
| [技能入口](./SKILL.md) · [完整工作流](./references/workflow.md) | Agent 执行顺序、研究模块与质量要求。 |
| [品牌追溯](./references/brand-to-company.md) · [区间估算](./references/estimation-triangulation.md) | 品牌与公司关系、估算依据及独立性规则。 |
| [CLI 说明](./scripts/README.md) | 初始化、台账、计算、构建与检查命令。 |
| [报告设计](./references/report-design.md) · [视觉配方](./references/visual-examples.json) | 章节组织、图文选择与可改写的图表示例。 |
| [台账契约](./schemas/data-contract.json) · [报告内容契约](./schemas/report-content.schema.json) | CSV / JSON 字段与约束；当前报告内容版本为 1.2。 |
| [完整示例](./examples/README.md) · [开发与回归测试](../development/zerox-due-diligence/README.md) | 示例复现、测试范围与运行方法；测试目录不随技能安装。 |

---

<a id="en"></a>
## English

This is a company and brand research skill for AI agents. It provides research methods, evidence records, calculation tools, and report generation to turn source materials into traceable conclusions. Deliverables include an **offline HTML report, a separate research audit file, and structured evidence ledgers**.

Use it simply to understand a business, or add a specific purpose: investment, acquisition, strategic or commercial partnership, customer credit, supplier qualification, or competitor research. General company research does not produce an overall score; scoring for a specific purpose is opt-in.

[Example](#en-example) · [Capabilities](#en-capabilities) · [Installation and use](#en-use) · [Local tools](#en-tools) · [Limits](#en-limits) · [Documentation](#en-docs)

<a id="en-example"></a>
### Start with a complete report

**Branch Tea: trace a consumer brand to its operating company, then examine its business, marketing, competition, and estimated revenue range.**

[HTML report](./examples/branch-tea/reports/report.html) · [Research audit file](./examples/branch-tea/reports/report-audit.md) · [Example guide and source materials](./examples/README.md) · [Editable report content](./examples/branch-tea/report-content.json)

GitHub displays the HTML source. Download or clone the repository, then open the file in a browser; no server is needed. The report includes navigation, charts, and a collapsible evidence appendix. It supports desktop and mobile reading, plus browser printing to PDF.

Every company, brand, person, source, and figure in this example is **fictional**. It separates the brand, trademark owner, operating company, and controlling entity, and estimates revenue using two methods. Profit and cash questions remain unanswered, so the report stays `limited`. Overlapping estimates do not turn assumptions into real financial results.

<a id="en-capabilities"></a>
### What you can investigate

| Your question | How the skill approaches it |
| --- | --- |
| **Who is actually behind this brand?** | Trace trademarks, website ownership, user agreements, payment recipients, and product records to the operating entity. Distinguish trademark owners, licensors, manufacturers, distributors, and controlling groups without mixing brand, group, and company data. |
| **How does this business operate and make money?** | Explain products, customers, payers, supply, delivery, revenue, and costs alongside company history and team roles. Address revenue scale, composition, gross margin, and net margin separately, including what is unknown and why it matters. |
| **What supports its growth, brand, and competitive position?** | Examine acquisition, conversion, retention, pricing, discounts, customer feedback, and alternatives. Compare past management commitments with subsequent results, keeping promotion, customer signals, and operating results distinct. |
| **What if important figures are undisclosed?** | Estimate ranges through different methods, such as stores, channels, workforce, users, or capacity. Check input evidence and source independence, retain assumptions, and expose conflicting methods. Leave a gap when independent support is insufficient. |
| **Can the conclusions withstand scrutiny?** | Organize research around 3–5 key questions, compare alternative explanations, and seek counterevidence. Track original sources, evidence, claims, and links separately; republication of one source does not create independent corroboration. |
| **Can a reader understand and verify the result?** | Explain the company with business diagrams, timelines, data charts, and comparison matrices. Keep conclusions, citations, and material limitations in the report; place full ledgers, search records, and reading notes in the audit file. |

The 18 research modules are selected by purpose, industry, and question. Report chapters follow the reader's needs, typically covering **company and history → founders and key team → products, customers, and business model → revenue and profitability → marketing and brand → major competitors → risks and next steps**. Missing evidence is stated, rather than filled with extra prose or invented charts.

When an official website exists, verify its ownership and read the relevant pages directly. If the target or its operating entity is listed or controlled by a listed company, research must search for and seek lawful access to the latest relevant official disclosures, company research, and industry reports. Track the latest discovered, full-text, and actually read materials separately.

<a id="en-use"></a>
### Installation and use

**Use the repository files directly**

```bash
git clone https://github.com/ZeroxZhang/zerox-skills.git
cd zerox-skills/zerox-due-diligence
```

This directory is the skill root. Ask an agent with local file access to load [SKILL.md](./SKILL.md), then provide the research target, purpose, and priorities. If you already have a clone, enter its skill directory directly.

**Install in Codex**

The optional command below copies runtime files and the complete example to `~/.codex/skills/zerox-due-diligence/`. Run it from the skill root. It stops if the destination already exists and does not overwrite an installed skill.

<details>
<summary>Show installation command (Python 3.10+)</summary>

```bash
python3 - <<'PY'
from pathlib import Path
import shutil

names = ("SKILL.md", "agents", "references", "schemas", "templates", "scripts", "assets", "examples")
missing = [name for name in names if not Path(name).exists()]
if missing:
    raise SystemExit(f"Incomplete skill package: {missing}")
destination = Path.home() / ".codex" / "skills" / "zerox-due-diligence"
destination.mkdir(parents=True, exist_ok=False)
try:
    for name in names:
        source = Path(name)
        if source.is_dir():
            shutil.copytree(source, destination / name,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        else:
            shutil.copy2(source, destination / name)
except Exception:
    shutil.rmtree(destination)
    raise
print(destination)
PY
```

</details>

Invoke it with `$zerox-due-diligence` after installation. Other agents that support `SKILL.md` should follow their host's discovery rules; this project does not claim verified compatibility with every host.

**Example requests**

```text
Use $zerox-due-diligence to research “legal company name / official website”.
Purpose: company research. Depth: Standard. As of: today.
Explain its business model, why customers buy, revenue and profitability,
marketing channels, and major competitors.
Deliver an offline HTML report and a separate research audit file.
```

```text
Use $zerox-due-diligence to research the brand “brand name”.
Identify its trademark owner, operating company, and controlling entity first,
then explain how it operates and makes money. Include customer feedback,
pricing, and discounts; assess whether undisclosed figures can be estimated
with evidence.
```

```text
Use $zerox-due-diligence to assess “company name” as a core supplier.
Focus on delivery and quality stability, prepayment risk, key dependencies,
and alternative supply arrangements. Use Standard depth and explain what
can be concluded now and which materials are still needed.
```

Choose research depth separately from access permissions:

| Depth | Research scope |
| --- | --- |
| **Quick** | Build a concise company profile, answer the most important questions, and identify key changes, material risks, and unknowns. |
| **Standard** | Examine major businesses, historical changes, competition, and financial mechanisms, with cross-checks of key conclusions. |
| **Deep** | Extend historical coverage and business, customer, or regional detail around key questions, with closer verification and scenario analysis. |

Depth is not measured by page length or search count. Deep does not automatically grant database, interview, or data-room access; missing critical materials still limit conclusions. See [purpose and depth guidance](./references/purpose-playbooks.md).

<a id="en-tools"></a>
### Run the local tools

Core scripts require **Python 3.10+ and only the standard library**. They manage records, calculate, render, and check; the agent performs the actual search, reading, and judgment.

**Reproduce the example first.** These macOS / Linux commands copy it to a new temporary directory, then rebuild and check the report without changing the repository example.

```bash
demo_dir="$(mktemp -d "${TMPDIR:-/tmp}/zerox-dd-demo.XXXXXX")"
cp -R examples/branch-tea "$demo_dir/project"
python3 scripts/build_report.py \
  --project "$demo_dir/project" \
  --content "$demo_dir/project/report-content.json" \
  --output "$demo_dir/project/reports/report.html" --overwrite
python3 scripts/check_report.py \
  --project "$demo_dir/project" \
  --report "$demo_dir/project/reports/report.html" --mode draft
printf '\nReport: %s\n' "$demo_dir/project/reports/report.html"
```

Expect no errors in `draft` mode; the report remains limited. Notices about missing real company images and manual review of comparable definitions are expected. See the [example guide](./examples/README.md).

**Start real research.** From the skill root, create a workspace outside the package. The output path must not already exist.

```bash
python3 scripts/init_project.py \
  --output /tmp/zerox-dd-company \
  --target "Legal company name to verify" \
  --purpose company_research --depth Standard

# Edit key_questions in project-config.json before generating the search plan.
python3 scripts/search_plan.py \
  --project /tmp/zerox-dd-company \
  --output /tmp/zerox-dd-company/search-plan.json
```

Add `--target-type brand` for a brand target. Initialization creates unverified records and editable templates; a search plan does not mean searches have been performed. Follow the [workflow](./references/workflow.md) to obtain materials, record evidence, and complete analysis, then edit `report-content.json` and build the report and audit file. See the [CLI guide](./scripts/README.md) for ledgers, financial calculations, range estimation, and full commands.

<a id="en-limits"></a>
### Limits

- **Conclusions require evidence.** Actuals, forecasts, estimates, and unknowns are labeled separately. Estimated ranges reflect input assumptions and interval arithmetic; they are neither statistical confidence intervals nor audited financial results.
- **Scripts do not replace research.** They do not automatically search the web, buy materials, or conduct interviews, and include no paid database access. Available materials depend on the agent's environment and granted permissions.
- **Passing checks does not mean research is complete.** Automated checks cover structure, references, and some consistency rules. Source meaning, comparable definitions, causal explanations, and conclusions still need substantive review. Unanswerable key questions keep the report limited; material access and reading coverage are recorded separately.
- **Visuals need support.** Real company images require source and usage records; fictional examples do not pass generated images off as real assets. HTML works offline, PDF comes from browser printing, and native Word export is not provided.

<a id="en-docs"></a>
### Documentation

| Document | Purpose |
| --- | --- |
| [Skill entry](./SKILL.md) · [Full workflow](./references/workflow.md) | Agent execution order, research modules, and quality requirements. |
| [Brand tracing](./references/brand-to-company.md) · [Range estimation](./references/estimation-triangulation.md) | Brand-to-company relationships, estimation support, and independence rules. |
| [CLI guide](./scripts/README.md) | Initialization, ledgers, calculations, report building, and checking. |
| [Report design](./references/report-design.md) · [Visual recipes](./references/visual-examples.json) | Chapter structure, visual choices, and adaptable chart examples. |
| [Ledger contract](./schemas/data-contract.json) · [Report content contract](./schemas/report-content.schema.json) | CSV / JSON fields and constraints; current report content version: 1.2. |
| [Complete example](./examples/README.md) · [Development and regression tests](../development/zerox-due-diligence/README.md) | Example reproduction, test coverage, and test commands. Tests are excluded from skill installation. |
