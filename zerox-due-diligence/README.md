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

全面理解公司或品牌的业务、客户、竞争与经营变化，并按具体商业目的开展专项尽调。用户给的是品牌名时，先追溯品牌背后的商标权利人、经营主体与控制集团，再研究公司并补充品牌认知、口碑与定价。锁定主体与控制关系，从原始资料验证关键问题和反证，对未披露的关键数字做有约束的三角估算，形成可追溯判断。默认交付图文并茂、可离线阅读的 HTML 报告，研究过程与核验记录保存在独立底稿中。

A company and brand research skill for understanding a business, its customers, competition, and operating changes, with additional due diligence for specific commercial purposes. When given a brand name, trace the trademark owner, operating company, and controlling group behind it, then research the company and add brand awareness, reviews, and pricing. Resolve entities and control, test key questions against alternatives and source evidence, triangulate undisclosed figures under explicit constraints, and form traceable conclusions. Deliver a visual, offline HTML report with research and verification records in a separate audit file.

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

支持正式的**公司研究**目的，无需先有交易意图；投资、并购、战略/商业合作、客户授信、供应商准入和竞品研究加载各自专项。**Quick / Standard / Deep** 按覆盖范围、历史跨度、拆分粒度与验证强度区分，资料访问权限单独记录。十八个模块按问题、行业和重要性裁剪。

<a id="zh-capabilities"></a>
### 核心能力

- **实体与控制链**：区分集团、子公司、分部、品牌和签约主体，按基准日处理参股、拟收购、出售及多层控制。
- **从品牌追溯到公司**：品牌不是法律主体。从商标登记、网站与 App 备案、用户协议与收款方、店铺资质、产品标签与备案、特许经营和集团披露中找出商标权利人、经营主体、被授权方、代工方与经销方，分别建档；查明经营主体之前，控制链与上市关系保持待核实。
- **品牌健康**：消费品牌补充搜索与社媒关注度、用户口碑主题、价格与折扣、定位与实际的对照；这些信号解释营销与竞争，不当作收入证据。
- **关键问题驱动**：开工时写下 3–5 个决定判断的问题并拆成可检验的子问题，研究以回答它们为主线；完成前每个问题都要有回答或说明无法回答的原因，决策部分对照有来源的主流看法说明自己的判断；一致时说明依据，不强造分歧。
- **有约束的估算**：未披露的营收、规模或份额可用门店、人效、渠道、用户、产能等至少两种独立方法估出区间，脚本用区间运算检查方法独立性与结果是否重叠；结果始终标为推断，不与实际数据混用。
- **管理层言行一致**：整理管理层历次公开的目标与指引，对照后来的实际结果。
- **官网优先阅读**：目标有官网时，先确认网站归属，再直接阅读公司、产品与价格、团队、沿革、渠道和服务条款等相关页面，并用网页存档还原历史变化。官网是重要的一手来源；经营宣传仍按公司自述标注，并结合独立资料核验。
- **关键解释验证**：先建立公司全貌，再比较当前解释与其他可能解释，寻找区分证据及改变判断的条件；客户失败样本、资源配置、行业传导、盈利质量和外部暴露纳入现有模块。
- **上市研报研究**：上市公司及其控制子公司必须检索，并争取合法获取、阅读相关最新官方披露、公司跟踪、公司深度与行业研究，补查重大事件。
- **资料覆盖与研究范围分开**：最新发现、最新全文、最新已读分别记录，旧全文不冒充最新资料。经过关键结论与剩余缺口影响复核，可结束约定范围；妨碍回答核心问题的缺口仍使研究受限。
- **证据与未知分开**：来源、证据、声明和关联独立建表；预测、实际、估算和缺口不混用，同源转载不增加独立证据数量。
- **财务与可选评分**：缺失不自动补零，现金为零仍正确计算。公司研究不发布综合分，商业专项默认也不评分；启用时先明确项目权重与不可缺维度，分数、风险和证据充分程度独立呈现。
- **阅读型 HTML 主报告**：浅色留白、蓝色强调、wiki 目录导航；简要摘要后，按公司全貌 → 业务运转 → 增长、市场、财务风险与决策组织正文。
- **公司与业务必须讲清**：11 个理解主题覆盖身份、起源团队、产品、客户、交易、经营分工、收入成本、差异化、财务表现、营销与竞争。发展时间线、基于已有资料的独立人物介绍与业务图帮助理解公司，避免用工商表或宣传术语替代解释。
- **财务、营销与竞争必答**：营收规模、营收构成、毛利率和净利率分别披露主体、期间、来源与缺口；解释营销渠道及获客、转化、复购，按选择依据比较主要竞品。资料不足时逐项说明未知及其影响，不能直接省略这些主题。
- **有依据的图文表达**：关键数字通过可核验图表呈现，附单位、期间、主体、实际/预测属性、来源与数据表；无可靠数据时用定性图解释，不编造数字。
- **先选主图，再组织解释**：逐章采用简短导读、主视觉与分析交错的编排。内置八种数据图，覆盖柱状、横向条形、折线、环形、比例条、区间、瀑布和堆叠；业务、资金、渠道与控制关系另用有据关系图呈现。
- **可视化遗漏检查**：构建与检查返回 `visual_review`，提示连续长文、埋藏数字和核心主题缺少视觉等编辑机会，摘要进入研究底稿。分别统计定量图、结构图、指标、图片和人物；不把装饰图片或文字卡当作数字已被图示。
- **真实图片与比较矩阵**：可内嵌真实 logo、官网截图、产品、门店或人物图片，记录出处、本次取得日期、使用范围、图注与替代文字；竞品、渠道和财务比较逐格标注依据。图片和定性矩阵不计作定量图，也不自动证明图片中的宣传。
- **正文与底稿分层**：主报告保留重要判断和限制；模块适用性、完整台账、搜索日志、覆盖记录与请求清单进入独立 `*-audit.md`，正文引用可定位到折叠证据附录。
- **可运行的本地工具**：八个核心 Python CLI（含三角估算）、研究与报告内容契约、CSV 台账、离线 HTML 渲染资源，以及一个虚构品牌的完整示范项目。

<a id="zh-report"></a>
### 最终报告包含什么

当前 HTML 内容契约为 **1.2**。主报告按读者理解公司的顺序组织，以下是推荐编排；章节名称和数量可随业务调整，必答主题仍须覆盖。

| 阅读板块 | 需要回答的问题 | 适合的呈现方式 |
| --- | --- | --- |
| 公司介绍与发展 | 它是谁、从何而来、经历了哪些业务与阶段变化？品牌目标先回答品牌背后是谁 | 公司画像、同章发展时间线、品牌—主体关系图、真实企业素材 |
| 创始人 / 核心合伙人 | 谁创办或经营公司，角色期间、相关经历和具体贡献是什么？ | 有足够公开资料时单设人物章节；区分创始团队与商业合作伙伴 |
| 产品、客户与业务模式 | 卖什么、卖给谁、谁付款、谁供给与交付、怎样形成收入和成本？ | 业务运转图、产品图或渠道示意 |
| 营收与盈利 | 营收规模和结构如何，毛利率、净利率是否有可比依据？未披露时估算区间是多少？ | 指标卡、趋势图、结构图或比较图；估算用区间图，分别标明数据口径 |
| 营销、增长与品牌 | 通过哪些渠道获客，内容与投放如何作用，转化和复购有何证据？品牌关注度、口碑与价格表现如何？ | 渠道矩阵、营销链路、关注度趋势、口碑主题与价格带图 |
| 主要竞争对手 | 为什么选择这些对手，同一市场与口径下有哪些差异？ | 竞争矩阵、有据的规模或定位比较图 |
| 风险与决策 | 关键问题的答案是什么，哪些判断与主流看法不同，哪些未知会改变判断，下一步做什么？ | 关键结论、差异化观点、风险说明与行动建议 |

时间线至少包含两个有日期依据的事件；确实不足时说明具体缺口。人物资料不足或真实图片不可得时如实说明，不凑履历、不用生成图冒充企业素材。财务、营销与竞争仍要逐项回答；无可靠数字时保留定性分析和限制，不绘制虚假趋势、份额或排名。

可视化按材料选择：一个有依据的客户比例也可用量尺条，一个价格上下界可用区间图；完整营收拆分可用堆叠，收入到利润的完整增减可用瀑布。没有转化数据仍能展示真实营销渠道关系，但不能画虚假的转化漏斗。默认模板将主图前置，[视觉配方](./references/visual-examples.json)提供可改写的字段示例。新增图型保持 1.2 内容兼容。

交付包含可直接打开的 `report.html`、完整研究底稿 `report-audit.md`，以及可追溯的 CSV / JSON 台账与材料。主报告保留必要引用、重要限制和折叠证据附录；搜索日志、执行过程、覆盖记录与完整核验表放入底稿。

<a id="zh-install"></a>
### 安装与使用

**当前目录就是 Skill 根目录**，入口是 [SKILL.md](./SKILL.md)。可直接让支持文件读取的 Agent 使用该文件；不需要再创建下层技能目录。

```text
请使用当前目录的 SKILL.md，全面研究「公司法定全称 / 官网 / 注册号」。
目的：公司研究；深度：Standard；基准日：执行当日。
重点：客户为何购买或流失、行业与竞争变化、组织执行、盈利与现金形成机制。
交付：可离线阅读的 HTML 主报告及独立研究底稿；讲清公司和业务模式，
呈现发展时间线，并逐项分析营收与盈利、营销渠道和主要竞争对手。
```

只知道品牌名时可以直接说：

```text
请使用当前目录的 SKILL.md 研究品牌「品牌名」：查明背后的公司和控制方，
再讲清它怎样经营和赚钱，补充品牌口碑与定价，交付 HTML 报告。
```

要让 Codex 自动发现，可把本目录的运行文件复制到 `~/.codex/skills/zerox-due-diligence/`。在当前目录执行下面的可选安装命令；目标已存在会停止，不覆盖已有 Skill：

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

安装后调用 `$zerox-due-diligence`。其他支持 `SKILL.md` 的 Agent 可按宿主的技能发现规则安装；并未声明全部宿主均已验证。

<a id="zh-quickstart"></a>
### 本地快速开始

要求 Python 3.10+。核心工具仅使用标准库，不需要 API Key，不会自动联网、购买报告或对外发送文件。

```bash
# 工作区应放在技能包之外；目标路径必须不存在。用户给的是品牌名时加 --target-type brand。
python3 scripts/init_project.py \
  --output /tmp/dd-example \
  --target "待核验公司法定全称" \
  --purpose company_research \
  --depth Standard

# 在 project-config.json 的 key_questions 写下关键问题，再生成检索计划（尚未执行检索）。
python3 scripts/search_plan.py \
  --project /tmp/dd-example \
  --output /tmp/dd-search-plan.json

# 未披露的关键数字：复制 templates/estimate-input.json 到 estimates/ 填写后估算区间。
python3 scripts/triangulate.py \
  --input /tmp/dd-example/estimates/EST-01-营收.json \
  --project /tmp/dd-example

# 实际研究、填台账和模块后，编辑生成的 report-content.json。
# 按读者问题和证据先选主图，再把公司、业务及分析解释编排到对应图旁。
python3 scripts/build_report.py \
  --project /tmp/dd-example \
  --content /tmp/dd-example/report-content.json \
  --output /tmp/dd-example/reports/report.html

python3 scripts/check_report.py \
  --project /tmp/dd-example \
  --report /tmp/dd-example/reports/report.html
```

初始化只创建待核实工作区和待编辑的报告内容模板；提供名称或证券代码不代表身份已核实。评分默认关闭，专项需要时用 `--enable-scoring` 初始化。研究范围完成须回答全部关键问题、填写 `completion_review` 并通过检查；它不改写研报资料覆盖状态。生成后打开 `reports/report.html`；同目录 `report-audit.md` 保存底稿。报告编排见[报告设计](./references/report-design.md)，配置与检查见 [CLI 使用说明](./scripts/README.md)，完整示范见 [examples/](./examples/README.md)。

<a id="zh-files"></a>
### 文件导航

本目录以可直接安装的技能发布，包含使用说明、运行脚本、参考资料、数据契约、模板、渲染资源与虚构示范项目。可复用回归测试单独维护在仓库开发区，不复制到安装目录。真实研究工作区、评估记录、调试材料及运行日志不进入公开版本；示例 HTML 是随包交付的演示文件。

| 目录/文件 | 用途 |
| --- | --- |
| [SKILL.md](./SKILL.md) | 触发、主流程、必经门槛与直接索引 |
| [references/workflow.md](./references/workflow.md) | 阶段输入、关键问题、深度裁剪、并行分工与失败处理 |
| [references/purpose-playbooks.md](./references/purpose-playbooks.md) | 公司研究基础、六类专项与三种深度 |
| [references/brand-to-company.md](./references/brand-to-company.md) | 品牌目标的追溯路径、角色关系与报告写法 |
| [references/estimation-triangulation.md](./references/estimation-triangulation.md) | 未披露数字的多方法区间估算与呈现边界 |
| [references/modules/](./references/modules/) | 公司、团队、业务、市场、竞争、阶段、增长、政策、商业与品牌、运营、技术、财务、法律、ESG、风险、估值、履约、上市研报 |
| [references/sources/](./references/sources/) | 中外来源目录、来源策略、研报与访谈方法 |
| [schemas/data-contract.json](./schemas/data-contract.json) | 字段、类型、枚举、引用、品牌角色、研报类别、权重和评分锚点 |
| [references/report-design.md](./references/report-design.md) | 正文/底稿分层、编辑方法、图表与视觉验收 |
| [schemas/report-content.schema.json](./schemas/report-content.schema.json) | HTML报告内容与可视化字段契约 |
| [templates/](./templates/) | 配置、十三张CSV台账、HTML内容模型、估算输入、财务输入、兼容Markdown底稿、资料请求与访谈提纲 |
| [examples/](./examples/README.md) | 虚构品牌的完整示范项目：台账、估算、内容模型与渲染出的报告 |
| [assets/](./assets/) | 随包安装的离线报告样式等渲染资源 |
| [scripts/](./scripts/README.md) | 八个核心 CLI 及共享校验实现 |
| [开发区测试](../development/zerox-due-diligence/README.md) | 在仓库根目录运行 `python3 -m unittest discover -s development/zerox-due-diligence/tests`；安装包不包含测试 |

<a id="zh-limits"></a>
### 能力边界

报告可由 [check_report.py](./scripts/check_report.py) 做结构、引用与理解主题覆盖检查，但**结构通过不证明事实真实、解释充分或研究结论正确**。交付前需让陌生读者仅靠正文回答“它是谁、卖给谁、怎样经营、怎样赚钱、关键未知是什么”。可交付明确披露未知的有限研究，不能把形式完整包装成研究完成。

核心交付为离线 HTML 主报告、Markdown 研究底稿与 CSV/JSON 台账。渲染器负责呈现已编辑内容，不能自动核验事实或替代分析。未接入 Wind、Choice、iFinD、Bloomberg 等付费数据库，未提供独立 Word/PDF 转换，也不包含自动搜索代理、访谈或交易执行。HTML可通过浏览器打印；交付前仍应检查实际打印效果。来源目录注明实际访问结果和待验证项。没有联网或授权全文时，交付受限研究和补齐路径，不能宣称“最新研报研究已完成”。

---

<a id="en"></a>
## English

Supports **company research** as a confirmed purpose without requiring a transaction. Investment, acquisition, strategic/commercial partnership, customer credit, supplier qualification, and competitor research add their own specialist questions. **Quick / Standard / Deep** differ in coverage, history, granularity, and verification strength; access permissions are recorded separately. Eighteen modules are tailored to the questions, industry, and materiality.

<a id="en-capabilities"></a>
### Capabilities

- **Entity and control mapping:** distinguish groups, subsidiaries, segments, brands, and contracting parties; assess minority stakes, pending acquisitions, disposals, and control chains at the research cutoff.
- **From brand to company:** a brand is not a legal entity. Trace trademark registrations, website and app filings, user terms and payees, store licenses, product labels and filings, franchising, and group disclosures to identify the trademark holder, operator, licensees, manufacturers, and distributors as separate records. Control and listing status stay pending until the operator is confirmed.
- **Brand health:** for consumer brands, add search and social attention, review themes, pricing and discounts, and positioning versus reality. These signals explain marketing and competition; they are not revenue evidence.
- **Key-question driven:** write 3–5 decisive questions at kickoff and break them into testable sub-questions. Before completion, each question needs an answer or an explained reason it cannot be answered, and the decision section states where the view differs from consensus.
- **Constrained estimation:** estimate undisclosed revenue, scale, or share with at least two independent methods such as stores, productivity, channels, users, or capacity. The script uses interval arithmetic to check method independence and overlap; results stay labeled as inferences and never mix with actuals.
- **Management say-do record:** compare management's past public targets and guidance with later results.
- **Official websites first:** when a target has a website, verify ownership and directly read relevant company, product/pricing, team, history, channel, and terms pages, using web archives to reconstruct historical changes. Treat it as an important primary source; label promotional statements as company claims and check them against independent material.
- **Question-led verification:** establish a broad company view, compare plausible explanations, and identify evidence that distinguishes them and would change the conclusion. Existing modules cover unsuccessful customer outcomes, resource allocation, industry transmission, earnings quality, and external exposures.
- **Listed-company research:** listed targets and controlled subsidiaries require searches and efforts to lawfully obtain and read current official disclosures, company updates, in-depth coverage, industry research, and relevant event updates.
- **Separate source coverage from scope completion:** record latest discovered, full text obtained, and read without presenting older material as current. Complete the agreed scope only after reviewing key conclusions and remaining gap impacts; gaps blocking core questions keep the research limited.
- **Traceable evidence:** separate source, evidence, claim, and relationship ledgers. Keep actuals, forecasts, estimates, and missing information distinct; syndicated copies do not count as independent factual evidence.
- **Financial and optional scoring safeguards:** missing values are not zero; zero available cash remains valid. Company research has no overall score, and commercial purposes default to scoring off. Enable scoring only after defining project weights and indispensable dimensions; keep scores, risks, and evidence sufficiency separate.
- **Reader-focused HTML reports:** a light layout with generous spacing, restrained blue accents, and wiki-style navigation. After a short summary, explain the company and how it works before growth, markets, financial risks, and decisions.
- **Company and business understanding:** eleven topics cover identity, origins and team, products, customers, transactions, operations, revenue and costs, differentiation, financial performance, marketing, and competition. A company timeline, a separate people section based on available evidence, and business diagrams support the explanation.
- **Required finance, marketing, and competition coverage:** address revenue scale, revenue mix, gross margin, and net margin individually, with entity scope, periods, sources, and gaps. Explain marketing channels, acquisition, conversion, and retention, and justify competitor selection. Disclose missing evidence and its implications instead of omitting these topics.
- **Evidence-backed visuals:** show key numerical findings in charts with units, periods, entity scope, actual/forecast labels, sources, and readable data tables. Use qualitative diagrams when reliable numbers are unavailable.
- **Choose the main visual before writing:** interleave a short introduction, the main visual, and analysis within each section. Eight data charts cover vertical and horizontal bars, lines, donuts, proportions, ranges, waterfalls, and stacked bars. Sourced relationship diagrams explain business, money, channels, and control relationships.
- **Visual omission review:** building and checking return `visual_review`, which flags editorial opportunities such as long prose, buried numbers, and core topics without suitable visuals. Its summary goes into the audit file. Quantitative charts, structural diagrams, metrics, images, and people are counted separately; decorative imagery and text cards do not establish numerical coverage.
- **Real images and comparison matrices:** embed authentic logos, website screenshots, product, store, or people images with provenance, the date obtained for this research, usage scope, captions, and alternative text. Identify the evidence basis of each comparison cell. Images and qualitative matrices are not quantitative charts and do not verify promotional claims.
- **Separate reading and audit layers:** keep material conclusions and limitations in the main report. Put full modules, ledgers, logs, coverage records, and request lists in `*-audit.md`; link citations to a collapsible evidence appendix.
- **Runnable local tools:** eight core Python CLIs (including triangulation), research and report-content contracts, CSV ledgers, offline HTML rendering assets, and a complete fictional brand example project.

<a id="en-report"></a>
### What the report contains

The current HTML content contract is **1.2**. The report follows the reader's path to understanding the company. The structure below is recommended; section names and counts may vary, while required topics remain covered.

| Reading section | Questions it answers | Suitable presentation |
| --- | --- | --- |
| Company and development | What is the company, how did it begin, and how has its business changed? For brand targets, who is behind the brand? | Company profile, a timeline in the same section, a brand–entity relationship diagram, authentic company imagery |
| Founders / core partners | Who founded or runs it, during which periods, with what relevant experience and contributions? | A separate people section when sufficient public material exists; distinguish founding partners from commercial partners |
| Products, customers, and business model | What is sold, to whom, who pays, who supplies and delivers, and how do revenue and costs arise? | Business diagrams, product imagery, or channel diagrams |
| Revenue and profitability | What are revenue scale and mix, and is there comparable evidence for gross and net margins? If undisclosed, what is the estimated range? | Metric cards, trend, composition, or comparison charts with explicit scope; estimates use range charts |
| Marketing, growth, and brand | Which channels acquire customers, how do content and advertising work, and what supports conversion and retention claims? How do brand attention, reviews, and pricing perform? | Channel matrices, marketing flows, attention trends, review themes, and price-band charts |
| Major competitors | Why are these competitors relevant, and how do they differ within comparable markets and definitions? | Competitor matrices and evidence-backed scale or positioning comparisons |
| Risks and decisions | What are the answers to the key questions, which judgments differ from consensus, which unknowns could change them, and what should happen next? | Key findings, contrarian views, risk explanations, and recommended actions |

A company timeline needs at least two sourced, dated events; explain a specific shortage when they are unavailable. Disclose insufficient people information or unavailable imagery without inventing biographies or substituting generated company assets. Finance, marketing, and competition still require individual answers. Without reliable numbers, retain qualitative analysis and limitations instead of fabricating trends, shares, or rankings.

Choose visuals from the available material: a single sourced customer proportion can use a scale bar, and a price interval can use a range chart. Complete revenue breakdowns suit stacked bars; complete changes from revenue to profit suit a waterfall. Real marketing relationships can still be shown without conversion data, but fabricated conversion funnels cannot. The default template brings visuals forward, and [visual recipes](./references/visual-examples.json) provide editable field examples. The additional chart types remain compatible with content version 1.2.

Deliverables include a directly readable `report.html`, the full `report-audit.md`, and traceable CSV / JSON ledgers and materials. Keep necessary citations, material limitations, and a collapsible evidence appendix in the main report. Store search logs, execution records, coverage tracking, and full verification tables in the audit file.

<a id="en-install"></a>
### Installation and use

**This directory is the skill root.** Start with [SKILL.md](./SKILL.md); no nested skill directory is needed here.

```text
Use SKILL.md in the current directory to investigate:
Target: legal company name / website / registration number.
Purpose: company research. Depth: Standard. Cutoff: today's date.
Focus: customer purchase and churn, industry and competitive changes,
organizational execution, and earnings and cash generation. Write in English.
Deliver an offline HTML report and a separate audit file. Explain the company
and business model, show its development timeline, and address revenue and
profitability, marketing channels, and major competitors individually.
```

When only a brand name is known:

```text
Use SKILL.md in the current directory to research the brand "Brand name":
identify the company and controlling party behind it, explain how it operates
and earns money, add brand reviews and pricing, and deliver an HTML report.
```

For Codex discovery, optionally copy the runtime files into `~/.codex/skills/zerox-due-diligence/`. Run the following from this directory. It stops if the destination already exists:

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

Then invoke `$zerox-due-diligence`. Other agents that support `SKILL.md` may use their own discovery conventions; compatibility with every host has not been tested. The methodology, templates, and CLI messages are primarily Chinese; the agent can adapt the report language.

<a id="en-quickstart"></a>
### Local quick start

Requires Python 3.10+. Core tools use only the standard library, require no API key, and do not automatically browse, buy reports, or transmit files.

```bash
# Keep the workspace outside this package; the output path must not exist. Add --target-type brand for a brand name.
python3 scripts/init_project.py \
  --output /tmp/dd-example \
  --target "Company legal name to verify" \
  --purpose company_research \
  --depth Standard

# Write key_questions in project-config.json, then generate the search plan (no searches are executed).
python3 scripts/search_plan.py \
  --project /tmp/dd-example \
  --output /tmp/dd-search-plan.json

# Undisclosed key figures: copy templates/estimate-input.json into estimates/, fill it, then estimate a range.
python3 scripts/triangulate.py \
  --input /tmp/dd-example/estimates/EST-01-revenue.json \
  --project /tmp/dd-example

# After research, choose visuals for each reader question, then interleave explanations and analysis in report-content.json.
python3 scripts/build_report.py \
  --project /tmp/dd-example \
  --content /tmp/dd-example/report-content.json \
  --output /tmp/dd-example/reports/report.html

python3 scripts/check_report.py \
  --project /tmp/dd-example \
  --report /tmp/dd-example/reports/report.html
```

Keep research workspaces outside this skill package. Initialization creates unverified records; a name or ticker is not verified identity. Search planning does not execute searches. Use `company_research` when the purpose is understanding the company; only a genuinely unspecified purpose stays pending. Scoring defaults to off; commercial projects can initialize with `--enable-scoring`, then confirm a project-specific `scoring_override`. Scope completion requires answering every key question, a checked `completion_review`, and passing checks; it does not change research-source coverage. Complete the research and ledgers, then edit `report-content.json` before building the deliverable.

Open `reports/report.html` directly to read the report. The sibling `report-audit.md` contains the full research record. See the [report design guide](./references/report-design.md) for editorial and chart requirements, the [CLI guide](./scripts/README.md) for ledger updates, financial inputs, configuration, and exit codes, and [examples/](./examples/README.md) for a complete worked project.

New HTML builds require content contract 1.2. Complete each of the eleven `explanation` topics once, arranged into suitable sections. Cite known information and describe specific limitations for partial or unknown answers. Restore relevant facts omitted from existing research; investigate actual evidence gaps rather than inventing answers. Each business-flow step distinguishes evidence, company claims, inference, and unknowns. The diagram may be omitted only when the transaction mechanism is unknown and the reason is explained. Legacy 1.0/1.1 HTML remains readable by draft checks; migrate before rebuilding or requesting completed-mode checks.

Keep the company timeline in the company overview section. Introduce founders and core partners in a separate section when sufficient public material exists. Replace template images with actual project files or remove those blocks; user-provided local materials may cite their provenance without inventing a web URL. PNG/JPEG/WebP files are embedded for offline reading, limited to 5 MiB each and 15 MiB in total; arbitrary SVG and runtime image downloads are unsupported.

<a id="en-files"></a>
### Package contents

This directory is published as an installable skill containing usage instructions, runtime scripts, references, schemas, templates, rendering assets, and a fictional example project. Reusable regression tests live in the repository development area and are excluded from installation. Real research workspaces, evaluation records, debug artifacts, and execution logs stay outside the public release; the example HTML is a shipped demonstration.

| Path | Purpose |
| --- | --- |
| [SKILL.md](./SKILL.md) | Entry point, workflow, mandatory gates, and resource index |
| [references/workflow.md](./references/workflow.md) | Phase inputs, key questions, depth tailoring, parallel work, and failure handling |
| [references/purpose-playbooks.md](./references/purpose-playbooks.md) | Company research foundation, six specialist purposes, and three depths |
| [references/brand-to-company.md](./references/brand-to-company.md) | Tracing paths, role relationships, and reporting for brand targets |
| [references/estimation-triangulation.md](./references/estimation-triangulation.md) | Multi-method range estimates for undisclosed figures and presentation limits |
| [references/modules/](./references/modules/) | Eighteen company, business, brand, industry, financial, legal, operational, and listed-company research modules |
| [references/sources/](./references/sources/) | China/global source directories, research and interview methods |
| [schemas/data-contract.json](./schemas/data-contract.json) | Fields, types, enums, references, brand roles, research categories, weights, and scoring anchors |
| [references/report-design.md](./references/report-design.md) | Reading/audit layers, editorial guidance, chart rules, and visual review |
| [schemas/report-content.schema.json](./schemas/report-content.schema.json) | HTML report content and visualization fields |
| [templates/](./templates/) | Configuration, thirteen CSV ledgers, HTML content model, estimate inputs, financial inputs, legacy Markdown audit reports, requests, and interview outline |
| [examples/](./examples/README.md) | A complete fictional brand project: ledgers, estimates, content model, and the rendered report |
| [assets/](./assets/) | Offline report styles and rendering resources installed with the skill |
| [scripts/](./scripts/README.md) | Eight core CLIs and shared validation |
| [Development tests](../development/zerox-due-diligence/README.md) | From the repository root: `python3 -m unittest discover -s development/zerox-due-diligence/tests`; tests are excluded from installation |

<a id="en-limits"></a>
### Limits

Reports can be checked for structure, references, and understanding-topic coverage with [check_report.py](./scripts/check_report.py), but **passing does not establish factual truth, sufficient explanation, or correct conclusions.** Before delivery, check whether a new reader can explain who the company is, whom it serves, how it operates, how it earns money, and what remains unknown using only the main report. A limited report may disclose real unknowns; formal completeness must not imply completed research.

Core outputs are an offline HTML reading report, a Markdown audit file, and CSV/JSON ledgers. The renderer presents edited content; it does not verify facts or replace analysis. No paid database integrations, standalone Word/PDF export, automated research crawler, interview execution, or transaction execution are included. Browser printing is available for HTML, and its actual layout still requires review. Source directories distinguish successful entry-page reads from failed or unverified access. Offline or restricted research must disclose limitations and acquisition steps; it cannot claim the latest-report requirement is complete.
