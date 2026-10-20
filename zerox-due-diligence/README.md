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

围绕实际决策开展公司尽调：先锁定主体与控制关系，再建立从原始资料、证据片段到判断与行动的可追溯链条。

A decision-focused company research skill. Resolve the legal entity and control relationships first, then connect original materials, evidence excerpts, claims, conclusions, and actions.

## 索引 / Index

| 中文 | English |
| --- | --- |
| [核心能力](#zh-capabilities) | [Capabilities](#en-capabilities) |
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
- **强制上市研报流程**：上市公司及其控制子公司必须检索、合法获取并阅读相关最新官方披露、公司跟踪、公司深度与行业研究，补查重大事件。
- **三种“最新”分开**：最新发现、最新取得全文、最新已读分别记录；新报告仅有标题时，旧全文不能让研究被标为完成。
- **证据与未知分开**：来源、证据、声明和关联独立建表；预测、实际、估算和缺口不混用，同源转载不增加独立证据数量。
- **财务与评分有门槛**：缺失不自动补零，现金为零仍正确计算；商业评分、风险和证据充分程度独立呈现。
- **可运行的本地工具**：七个核心 Python CLI、统一 JSON 数据契约、CSV 台账与 Markdown 报告。

<a id="zh-install"></a>
### 安装与使用

**当前目录就是 Skill 根目录**，入口是 [SKILL.md](./SKILL.md)。可直接让支持文件读取的 Agent 使用该文件；不需要再创建下层技能目录。

```text
请使用当前目录的 SKILL.md，对「公司法定全称 / 官网 / 注册号」开展尽调。
目的：供应商准入；深度：Standard；基准日：执行当日。
重点：交付连续性、财务状况、预付款风险与集团支持安排。
```

要让 Codex 自动发现，可把本目录的运行文件复制到 `~/.codex/skills/zerox-due-diligence/`。在当前目录执行下面的可选安装命令；目标已存在会停止，不覆盖已有 Skill：

```bash
python3 - <<'PY'
from pathlib import Path
import shutil

destination = Path.home() / ".codex" / "skills" / "zerox-due-diligence"
destination.mkdir(parents=True, exist_ok=False)
for name in ("SKILL.md", "agents", "references", "schemas", "templates", "scripts"):
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

# 实际研究、填台账和模块后，再组装与检查。
python3 scripts/build_report.py \
  --project /tmp/dd-example \
  --output /tmp/dd-report.md

python3 scripts/check_report.py \
  --project /tmp/dd-example \
  --report /tmp/dd-report.md
```

初始化只创建待核实工作区；即使提供名称或证券代码，也不会自动标记身份已核实。目的未给出时保留待确认，不计算场景综合分。详细字段、台账更新、财务计算和退出码见 [CLI 使用说明](./scripts/README.md)。

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
| [templates/](./templates/) | 配置、十三张 CSV 台账、财务输入、完整/Quick 报告、资料请求与访谈提纲 |
| [scripts/](./scripts/README.md) | 七个核心 CLI 及共享校验实现 |

<a id="zh-limits"></a>
### 能力边界

报告可由 [check_report.py](./scripts/check_report.py) 做结构与引用检查，但**结构通过不证明真实公司事实、财务真实性或研究结论正确**。

核心交付为 Markdown 与 CSV/JSON。未接入 Wind、Choice、iFinD、Bloomberg 等付费数据库，未提供 Word/PDF 转换，也不包含自动搜索代理、访谈或交易执行。来源目录注明实际访问结果和待验证项。没有联网或授权全文时，交付受限研究和补齐路径，不能宣称“最新研报研究已完成”。

---

<a id="en"></a>
## English

Supports six purposes: **investment, acquisition, strategic/commercial partnership, customer credit, supplier qualification, and competitor research**, with **Quick / Standard / Deep** modes. Eighteen research modules are tailored to each project's purpose, industry, and materiality.

<a id="en-capabilities"></a>
### Capabilities

- **Entity and control mapping:** distinguish groups, subsidiaries, segments, brands, and contracting parties; assess minority stakes, pending acquisitions, disposals, and control chains at the research cutoff.
- **Mandatory listed-company research:** listed targets and controlled subsidiaries require searches, lawful full-text acquisition, and reading of current official disclosures, company updates, in-depth coverage, industry research, and relevant event updates.
- **Three separate freshness states:** latest discovered, latest full text obtained, and latest read. An older full report cannot conceal an inaccessible newer relevant report.
- **Traceable evidence:** separate source, evidence, claim, and relationship ledgers. Keep actuals, forecasts, estimates, and missing information distinct; syndicated copies do not count as independent factual evidence.
- **Financial and scoring safeguards:** missing values are not zero; zero available cash remains a valid input. Business fit, risk, and evidence sufficiency are reported separately.
- **Runnable local tools:** seven Python CLIs, a shared JSON data contract, CSV ledgers, and Markdown reports.

<a id="en-install"></a>
### Installation and use

**This directory is the skill root.** Start with [SKILL.md](./SKILL.md); no nested skill directory is needed here.

```text
Use SKILL.md in the current directory to investigate:
Target: legal company name / website / registration number.
Purpose: supplier qualification. Depth: Standard. Cutoff: today's date.
Focus: delivery continuity, financial condition, prepayment exposure,
and actual parent-company support. Write the report in English.
```

For Codex discovery, optionally copy the runtime files into `~/.codex/skills/zerox-due-diligence/`. Run the following from this directory. It stops if the destination already exists:

```bash
python3 - <<'PY'
from pathlib import Path
import shutil

destination = Path.home() / ".codex" / "skills" / "zerox-due-diligence"
destination.mkdir(parents=True, exist_ok=False)
for name in ("SKILL.md", "agents", "references", "schemas", "templates", "scripts"):
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

python3 scripts/build_report.py \
  --project /tmp/dd-example \
  --output /tmp/dd-report.md

python3 scripts/check_report.py \
  --project /tmp/dd-example \
  --report /tmp/dd-report.md
```

Keep research workspaces outside this skill package. Initialization creates pending records; a supplied name or ticker is not verified identity. Search planning does not execute searches. Complete the actual research, ledgers, and module analyses before treating an assembled report as a deliverable. An unspecified purpose stays pending and disables purpose-specific overall scoring.

See the [CLI guide](./scripts/README.md) for ledger updates, financial inputs, configuration, and exit codes.

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
| [templates/](./templates/) | Configuration, thirteen CSV ledgers, financial inputs, full/Quick reports, requests, and interview outline |
| [scripts/](./scripts/README.md) | Seven core CLIs and shared validation |

<a id="en-limits"></a>
### Limits

Reports can be checked for structure and references with [check_report.py](./scripts/check_report.py), but **passing those checks does not establish the truth of real company facts or the correctness of research conclusions.**

Core outputs are Markdown and CSV/JSON. No paid database integrations, Word/PDF export, automated research crawler, interview execution, or transaction execution are included. Source directories distinguish successful entry-page reads from failed or unverified access. Offline or restricted research must disclose limitations and acquisition steps; it cannot claim the latest-report requirement is complete.
