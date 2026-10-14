# 交付契约：任务合同、门禁与同版产物

**什么时候读这一份**：S1 开工登记任务合同时，以及 S6 交付时。

**读完要能做到**：写出正确的 `task.json`、按合同安排复核、生成能被聚合的门禁产物、把 HTML 与 PDF 同版交付出去。

**这份文件是 `task.json` 字段与 `review` 结构的唯一来源。** 其他文件只引用，不重复定义。

## task.json：唯一的任务合同

制作前把它写进任务目录。它同时驱动装配参数、复核要求和交付校验，所以**先写它，再动手**。

```json
{
  "version": 1,
  "workMode": "editorial",
  "complexity": "simple",
  "majorConclusion": false,
  "mode": "reading",
  "theme": "mckinsey",
  "typography": "serif-report-bold",
  "ratio": "16x9",
  "kind": "fragment",
  "pages": {"record": "pages.json"},
  "critical": []
}
```

开工时 `pages.record` 先按此占位，指向 S3 产出的 `pages.json`；装配时文件必须已存在且与成稿逐页一致。给 `sha256` 时必须与文件实际摘要相符，不给则由装配器读取填入。

字段含义：

| 字段 | 取值 | 含义 |
|---|---|---|
| `version` | `1` | 合同版本，目前只接受 1 |
| `workMode` | `editorial` / `analytical` / `exploratory` | 决定分析深度与必要工作；选择依据见[分析](analysis.md) |
| `complexity` | `simple` / `complex` | **未判断时按 `complex`**；`simple` 必须是真实判断，不能为绕过复核而填。判据是任务范围而不是材料多少：材料多但只需按原文重新组织、不做新研究也不做新推理时可以是 simple；一旦需要新的计算、新的方法选择或新的结论就必须 complex |
| `majorConclusion` | `true` / `false` | 是否承载重大结论或建议，必须明确写出 boolean |
| `mode` | `reading` / `presentation` | 深度研究、预读用 reading；现场讲述用 presentation。正文页的类名要与它一致 |
| `theme` | `mckinsey` / `bcg` / `accenture` | 必须是 `assets/deck-themes.js` 里已注册的名字 |
| `typography` | 已注册的字体预设名 | 必须是 `assets/deck-typography.js` 里已注册的名字；不能提供嵌入字体的系统字体预设会被静态装配拒绝 |
| `ratio` | `16x9` / `4x3` | 4:3 需要重新布局，不是等比缩放 |
| `kind` | `report` / `fragment` / `collection` | **只控制首尾编排，不决定风险。** 不能用 fragment 绕过风险复核，也不让简单的完整稿重做复杂研究 |
| `planner` | `{mode, record?, sha256?, reason?}` | 不采用外部专家可省略，默认为 direct；使用时见下 |
| `pages` | `{record, sha256?}` | S3 的逐页形式声明（pages.json）。`record` 相对 `task.json` 解析；给了 `sha256` 就要与文件实际摘要一致。**传了合同的装配缺这一项直接失败**，见下 |
| `critical` | 数组，可为空 | 少量会改变判断的关键语义声明，见下 |
| `densityPolicy` | 否 | `compact`（默认）／`normal`。**紧凑是本技能的默认交付形态**：`compact` 下，展品区底部余量与模块间空白按占比升级为错误（见[验收](qa.md)），封面、封底、参考资料按设计豁免。要松排版的稿子必须显式写 `normal`，不能靠不写来默认松 |

**派生规则**：`complexity === "complex"` 或 `majorConclusion === true` 时，复核要求派生为 independent，否则为 author。不要手填与风险冲突的 `reviewPolicy`——填了且冲突会被直接拒绝。

`fragment` 是单篇片段，`collection` 是多篇合集演示——两者都不要求首尾页；只有 `report` 才按首尾规则编排。`report` 只是声明：封面、参考资料、封底仍由作者按[首尾页面](bookends.md)提供，装配器不自动补页。

### planner

仅采用[可选专家](planner.md)时需要其交接记录；内置选型不生成 plan JSON。

| mode | 什么时候用 | 必须补什么 |
|---|---|---|
| `direct` | 按内置图表方法选型，未采用外部 planner | 无；默认值，无需显式填写 |
| `used` | 实际采用了 planner 的选型 | `record`（相对 `task.json` 的路径）与 `sha256`（64 位十六进制）。装配时校验并把路径换算为相对输出 HTML 的路径；未给 sha256 时装配器读取真实文件填入 |
| `unavailable` | planner 在当前环境确实不可用 | `reason` 说明实际限制 |

**不能把"已经采用但记录缺失"改写成 `direct`。** 只做到 S3 是阶段范围，不是环境不可用；续作时重新决定并更新。

### pages：逐页形式声明

`pages.json` 是 S3 的机器可读产物：**内容和它的组织形式一起定下来**，而不是先写标题、实现阶段再临场找图。装配器用它和成稿逐页对账，QA 用它出全篇形式清单，交付门禁要求它 `PASS`。

```json
{
  "version": 1,
  "familyDiversityReason": "本稿主线是同一批对象在同一量尺上的排序变迁，多数页共用长度编码；只有三家平台有可比的季度序列，已单独成页。",
  "unusedFamilies": {
    "distribution": "公开材料只有均值与总量，没有原始观测，不从均值伪造分布",
    "hierarchy": "本稿没有需要逐层拆分的总体"
  },
  "pages": [
    {
      "page": 3,
      "proves": "商超是净下滑的主要来源，电商只抵消约三分之一",
      "form": "kit.waterfall",
      "regions": [
        {"slot": "main", "span": 7, "form": "kit.waterfall", "role": "primary"},
        {"slot": "aside", "span": 5, "form": "kit.dumbbell", "role": "support"}
      ],
      "annotations": [{"id": "a-sc", "on": "bar:商超", "kind": "delta", "text": "主要拖累 {value}"}]
    }
  ]
}
```

| 字段 | 必填 | 含义 |
|---|---|---|
| `page` | 是 | 正文页序，从 1 连续；封面/参考资料/封底不登记 |
| `proves` | 是 | 这一页要让读者看出的**一个**关系；与 `data-proves` 一致时会被核对 |
| `form` | 是 | 本页主实现入口，取自 `assets/deck-forms.js`；未封装的 ECharts 或手写 SVG 用 svg.custom，不限制实际图型 |
| `visual` | 通用 SVG 时填写 | 实际表达名称，如 ecdf、forest、adjacency-matrix；相同图型跨页同名。可用于其他入口，regions 也可填写。成稿对应 data-visual |
| `regions` | 否 | 一页多展品时写明分区；必须恰好一个 `role:"primary"` 且与 `form` 一致；主区写了 visual 时须与 page.visual 相同。它不生成布局，只做声明——写法与分区规则见[单页布局选型](layouts.md) |
| `encodingFamily` | svg.custom 时是 | 这一页**实际**落在哪个编码族（`comparison`/`trend`/`composition`/`distribution`/`correlation`/`flow`/`hierarchy`/`kpi`/`diagram`/`table`）。`visual` 是表达名称，这个是分布记账的族——不填就会被记成 `custom`，那一族在丰富度账面上等于不存在。只用于 `svg.custom`；已登记形式的族由 `form` 决定，重复声明会被拒绝 |
| `annotations` | 否 | 图上的旁解读，见[证据与表达](exhibits.md)的"旁解读"一节。每项需要 `id`（成稿对账与复核引用都靠它）。声明了就必须在成稿里真的出现同名 `data-annotation-id`，画了没声明同样报错 |
| `annotationMode` | 手摆时写 | 取 `"manual"`。`annotation:'layer'` 的形式由通用标注层自动摆位，不写；其余形式要写旁解读必须显式声明手摆并承担目视验收——**不再按形式族一律拒绝**，那样会把作者推回少数可标注形式，反而压低了编码族多样性。已接入通用层的形式写它会被拒绝 |
| `repetitionReason` | 视情况 | 同一表达第 3 次起、或连续 3 页相同表达时写；有 visual 按 visual，否则按 form |

**族分布的两条交代。** 它们不是图型配额，是"你注意到了并说得出为什么"：

- `familyDiversityReason`（顶层）：**单族占展品页 30% 以上且至少 4 页**时必填。占比以展品页为分母——结构化文字页是兜底，不算展品。按名称计数抓不住"七页长度编码散在五个 form 名下"，所以这一条按族算。
- `unusedFamilies`（顶层）：**展品页达到 8 页**时必填，逐族说明每个缺席的展品族为什么整族没出现。缺席在计数表里是看不见的，而"有数据却没画"恰恰是最容易漏的一类——真实跑批中出现过"手上已有季度序列却没做时间序列"。理由要写依据（没有多期序列／没有守恒流量／没有原始观测等）；声明某族没用上而稿子里其实有，会被当场拒绝。

**没有降级字段。** 容量不足时改的是布局、分面、模块高度或绘制路径，不是表达类型；写了 `fallback` 会被直接拒绝。装配后的 QA 还会核对声明为图形实现（`kind:'svg'`）的形式在成稿里确实出现了 SVG，只有表格就报错。

成稿每页必须显式声明 `data-form`（封面、参考资料、封底、分隔页除外），取值与 `pages.json` 一致；**没有静默默认值**，缺了或写了枚举以外的名字装配直接失败。`pages.json` 声明 `visual` 时，成稿须声明相同 `data-visual`，否则对账失败。`data-proves` 可选，写了就必须与 `pages.json` 的 `proves` 一致。

成稿里出现的每个 `data-annotation-id` 都要在 `pages.json` 有对应声明，反之亦然；正文里的 `P<n>` 与 `<n> 页正文` 会被抽出来核对——**插页、删页或分章调整之后，这类跨页引用最容易悄悄失准，而它本来是可以机械查的**，不该留给人工复核去发现。

**反单调不是图型配额。** 规则只有一条：**重复必须是被解释的决定，不能是默认**。同一表达第 3 次出现、或连续三页相同表达，作者必须写一句 `repetitionReason` 说明为什么这里还是它；族层面的两条交代（`familyDiversityReason`、`unusedFamilies`）同理。它们不规定用几种图、不因数量给页面定级，也不替代"这条形式是否真的适合本页证明责任"的判断——那是 S3 的取舍和 S5 的目视验收。

### critical：少量关键语义

只登记会改变理解或判断的内容，不登记普通句子：关键数字及其单位与分母、适用期间、否定或成立条件、事实/预测/假设的身份、会改变建议的反证。空数组不证明没有关键风险，识别责任仍在作者。

每项形如 `{"id": "唯一标识", "text": "原文限定", "target": "可选，对象 id"}`。`id` 与 `target` 用字母开头的标识符，`id` 不能重复，`text` 必须非空。

声明只有落到页面上才能被核对：HTML 一侧用 `data-critical-id`（对应 `id`）和 `data-critical-for`（关联对象）标在真实对象上，用法见[精度与标注](precision.md)。只写进 task.json 而没有落到 DOM 的声明会被判为未落实。

它检查的是**已声明的关键内容**在屏幕、打印和实际 PDF 里是否仍然存在、位置是否正确；audit 会标注为 `DECLARED_ONLY`，它不覆盖未声明的业务语义。

## 装配：把自由页面接回引擎

作者只写 `pages.html`：每页一个完整的顶层 `<section class="slide reading" data-frame-boundary="integrated">…</section>`，可以自由使用 HTML、表格、内联 SVG 和自己的布局 CSS。示例里的 reading 与 integrated 是作者选择，要按实际页面决定。片段里可以带 `style`，也可以另给 CSS 文件。

```sh
node scripts/assemble_deck.cjs /任务/pages.html /任务/deck.html \
  --css /任务/page.css --title "报告标题" --contract /任务/task.json
```

| 参数 | 取值 | 说明 |
|---|---|---|
| `--contract` | 任务合同路径 | 主路径。统一模式、主题、字体、画幅、kind、风险与 planner 记录 |
| `--css` | 自定义 CSS 路径 | 作者样式排在公共默认样式之后 |
| `--title` | 报告标题 | 写入文档标题 |
| `--kind` | `fragment` / `report` / `collection` | 覆盖合同里的 kind |
| `--theme` / `--typography` / `--ratio` | 已注册的主题名、字体预设名、`16x9`/`4x3` | 显式覆盖；与合同冲突时应当修正输入 |

不传合同的兼容调用会采用保守的 `complex` 默认值，不能据此绕过独立复核。

装配器用 Chromium 解析 HTML/SVG，验证独立页结构后替换引擎唯一的 `#stage`，保留导航、缩放、深链、打印和已验收 PDF 下载接口。它只补缺失的母版节点；**每页必须由作者显式选择合法的 `data-frame-boundary`**，首尾页可用 `data-frame="off"` 配合 `space`。缺失或非法边界会失败，不自动选择横线。合同与显式主题/字体参数冲突时应当修正输入，不能静默接受。

**静态装配只接受内联 SVG 与 `data:` 资源。** 以下会明确失败：`script`、`canvas`、`.chart`、`data-opt`/`data-recipe`、事件处理器、外部图片/样式/字体、`@import`、重复或引擎保留的 id、嵌套 slide、未闭合的 section、完整 HTML 输入。动态图表先沿 `render_echarts_svg.cjs` 等入口渲染成内联 SVG；内嵌位图用 base64 data URL，SVG 直接内联以继承报告字体。CSS 里的外部 URL 与 `@import` 要先内联，普通来源超链接可以保留。

主题、公共布局、共享几何、母版和字体都通过现有 `apply_theme.cjs` 装配（其中已调用 `pack_fonts.cjs`），没有第二份样式实现。只有静态路线会去掉不使用的 ECharts 与在线图标加载器；正文的中文、西文和内联 SVG 文字进入最终字体子集。构建需要与 QA 相同的 Playwright/Chrome、Python/fontTools 和本地字体资产，可用 `PLAYWRIGHT_MODULE`、`CHROME_CHANNEL`、`FONT_PYTHON` 指向已配置的运行时。

API：`await assemble({pagesFile, outputFile, contractFile?, cssFile?, title?, kind?, theme?, typography?, ratio?})`。成功返回 `{status:"assembled", output, pages, theme, typography, kind, ratio, sha256, route:"static-html-svg"}`；失败不写输出。

装配器不计算数据、不排查视觉碰撞、不宣称最终 PDF 已经通过。它只保证接回成功，之后仍要继续成稿 QA 与实际看图。

### 动态路线

不走静态装配时：用 `apply_theme.cjs` 初始化，编辑或在 SSR/资源内联之后，用 `pack_fonts.cjs` 定稿；新增文字要重新打包字体。两条路线都要继续成稿 QA 与实际看图。

## 交付门禁链

链式的，断任何一环都不能正式交付：

1. **装配**——`assemble_deck.cjs` 把任务合同写进 HTML，并声明 `data-reliability-version="2"` 与 `data-deck-kind`。传了合同时逐页 `data-form` 必须存在、取值合法，并与 `pages.json` 一一对应；缺 `pages` 或缺声明直接失败。
2. **工程与证据**——`node scripts/qa_deck.cjs /任务/deck.html /任务/renders` 生成 `audit.json` 与真实的双媒介逐页证据。audit 必须 `geometryStatus === "PASS"` 且 `errors` 为空；缺少任一媒介的任一页证据都会失败。audit 同时给出 `pagesCheck` 与 `pagesInventory`（全篇形式与族的分布、最长连续段）。**只有 `tier` 为 `acceptance` 的 audit 能进入这条链**：迭代档（`--tier iteration --pages <页>`，必须点名页码）与冒烟档（`--tier smoke`）是制作期的自查工具，`acceptance.complete` 为 `false` 并列出没跑的检查，`package_delivery` 与有限继承都会拒绝它们。
3. **审查归属**——`review` 必须 `status: "complete"`，证据 id 取自本次 `audit.evidenceManifest.entries`，并绑定当前 HTML、PDF 与 audit 的摘要。审查者要读 `pagesInventory`，对"全篇是否重复同一弱结构"给出具体判断。
4. **打包**——`package_delivery.cjs` 复核页数、SHA-256、任务合同与证据归属；`pagesCheck` 不是 `PASS` 时拒绝正式打包，只能用 `--preview`。内嵌 PDF 的字节必须等于独立 PDF。

**工程通过不代表已经审过内容或视觉。** audit 里的 `visualStatus` 只会是 `NOT_REVIEWED`——它明确说明自动检查没有看图。

## review：现行结构

```json
{
  "schemaVersion": 3,
  "status": "incomplete",
  "reviewer": "实际审查者",
  "independence": "author",
  "isolation": "same-session",
  "htmlSha256": "audit.htmlArtifact.sha256",
  "pdfSha256": "audit.pdfArtifact.sha256",
  "auditSha256": "对 audit 解析对象执行 hash(stable(audit)) 的实际值",
  "checks": {
    "analysis": {"status": "not_reviewed", "basis": ""},
    "evidence": {"status": "not_reviewed", "basis": ""},
    "visual": {"status": "not_reviewed", "basis": ""}
  },
  "coverage": [],
  "warningReview": [],
  "issues": []
}
```

**这是未完成结构，不是通过样例。** 实际检查之后再填 `basis`、`coverage` 和结论。

- `status` 最终必须是 `complete`。
- `htmlSha256` 与 `pdfSha256` 取 audit 的产物摘要。`auditSha256` 是对 audit **解析对象**做的规范化摘要，**不是 `audit.json` 的原始字节摘要**；算法由 `scripts/report_contract.cjs` 的 `hash` 与 `stable` 提供。
- `checks.analysis` 与 `checks.evidence` 为 `pass`，或有实际理由的 `not_applicable`；`checks.visual` **必须是实际看图后的 `pass`**。三项都要有非空 `basis`，写清实际看到什么、依据是什么。
- **`checks.*.status` 说的是"这一层检查做完了、依据写在 basis 里"，不是"这一层没问题"。** 发现的问题一律进 `issues`，用 severity/status 表达，不要试图用 checks 表达好坏——这里没有 `fail` 取值，硬凑一个只会盖掉问题。`issues` 里的 major/blocking 必须 `resolved` 才能交付，这条由聚合与校验器强制，比 checks 更硬。
- **`basis` 要写实际做了什么**（看了哪些页、复算了哪些数、核到哪一条），不写"已检查，无问题"。它是复核的取证记录，不是结论摘要。

### isolation：独立性不只是一个名字

`independence` 说的是"挂了谁的身份"，`isolation` 说的是"它在什么上下文里做的"，两者都要写：

| 取值 | 含义 |
|---|---|
| `fresh-context` | 独立的执行者，未继承作者的推理与工具历史 |
| `fork` | 分叉自作者会话，带着作者的判断去找问题 |
| `same-session` | 作者本人 |

**`independence: "independent"` 要求 `isolation: "fresh-context"`**，其余取值会被拒绝。真实跑批里出现过复核者继承了作者全部上下文、却照样自报 `independent` 的情形——带着作者的结论去找问题，找到的多半只是作者已经怀疑过的那些。

这一条不能机器证明，它是自述。把沉默的疏漏变成一个必须显式写下的取值，意义在于：**"声称独立"由此成为一句可以被人追问的具体话**，而不是一个默认成立的空洞。写 `fork` 时不要硬凑 `independent`——把 `independence` 如实降为 `author`，再说明为什么没做独立复核，比一个假的独立更可信。
- `independence` 为 `author` 或 `independent`。不能由脚本预填通过判断。

### coverage

每项包含 `reviewer`、`independence`、四层 `layers`（`page`、`exhibit`、`annotation`、`typography`）、`htmlPages`、`pdfPages`，以及 `evidence`：

```json
"evidence": [{"id": "html:实际pageId"}, {"id": "pdf:实际pageId"}]
```

- 证据 `id` **必须从本次 `audit.evidenceManifest.entries` 里选**，媒介与页号要逐一匹配。
- 不能用一张截图覆盖多页，也不能用 HTML 图充当 PDF 证据。
- `htmlPages` 与 `pdfPages` 必须与所引证据的媒介和页号集合完全一致。
- 同一份真实图像可以被作者和独立审查者分别引用，不需要重复生成截图。
- 复杂任务由作者与独立角色**各自覆盖全页、两种媒介**；简单任务由作者覆盖全页、两种媒介。**作者结果不能填补独立结果的缺失。**
- 同一角色内部可以合并分工结果，但作者与独立审查者的身份不能重叠。

#### 逐页取证：`attestation`

引用一张哈希正确的图，与真的打开看过它，在校验器眼里原本完全一样——这正是真实跑批中"申报 56 条证据、实际读了 11 张图"能全链绿灯的原因。所以每条 coverage 都要带 `attestation`：

```json
"attestation": [
  {"page": 3, "note": "第 3 页三条柱里最右那根明显低一截，页脚来源占了两行"},
  {"page": 4, "note": "第 4 页四格中左下格是空的，右上格有加底色"}
]
```

- **每次覆盖了哪几页，就要逐页写一条**。声称看过却没写、或写了没覆盖到，都会被点名，并把缺的页列出来。
- **写只能来自实际所见的短记录**——图上哪个位置空着、哪两根柱几乎等高、哪条线断了、标签有没有压到图元。写从 HTML 源码就能读到的东西不算：那证明不了你打开过图。
- **全篇不得重复**。一条复制到底会被直接拦下——这不是文风要求，是"逐页"的字面含义。
- 它仍然是自述，校验器不能证明你真的看了。它的作用是把作假的成本抬到"不如真看一遍"，并把一组具体、可被人抽查的断言留在记录里。**抽查由人做，这条不能被自动化替代。**

#### 未变页怎么引用旧审查：`inheritedFrom`

修完一页重跑验收档时，不必把没动过的页重新看一遍。做法是**产出一份新的 review**（顶层摘要绑定本次 audit 的新哈希），在 coverage 条目上声明它继承自哪一次审查：

```json
{
  "reviewer": "independent-reviewer-5",
  "independence": "independent",
  "layers": ["page", "exhibit", "annotation", "typography"],
  "htmlPages": [1, 2, 3, 5],
  "pdfPages": [1, 2, 3, 5],
  "evidence": [{"id": "html:page-1"}, {"id": "html:page-2"}],
  "inheritedFrom": {
    "basis": "本轮只改了第 4 页的图注，其余三页的 DOM、命中样式与渲染图摘要经核对未变",
    "audit": {"path": "renders/audit.json", "sha256": "上一轮 audit 的摘要"},
    "review": {"path": "renders/independent.json", "sha256": "上一轮 review 的摘要"}
  }
}
```

校验器会逐条比对两轮 audit 里同一证据的 `pageSha256`、`pageStyleSha256`、`dependenciesSha256`、`sha256` 与页号——**任何一项变了就拒绝继承，那一页必须重新看**。旧审查者本人要覆盖过该条证据，旧的未决问题也要被本次完整保留。文案上写"其余页未变"不算数：**能不能继承由摘要决定，不由说明决定**。

> **当前实现的限制（实测，2026-09-19）**：这条路现在走不通，两个都来自 `review_contract.cjs` 自身的实现方式，不是用法问题。
>
> 1. **audit 记录的是产物绝对路径**，校验时 `path.resolve(归档目录, 绝对路径)` 会原样回到原位置核原件。所以就地重建 deck 之后，继承必然失败；**把 audit 与产物一起留档也不管用——留档副本不会被核到**。可用的归档件必须在留档时重写产物路径并重新记录摘要。
> 2. 旧审查会被**递归校验且不按 `partial` 放行**，因此它得像终稿一样两角色齐全、并绑定在同一份（重写过路径的）留档 audit 上。中途某一轮的 `independent.json` 达不到这个要求。
>
> 在此之前，**单页返工仍要按完整覆盖重做复核**；`make_review.cjs --inherit` 会在动手前把这两种情况直接拦下并说明原因，而不是让你写完一份复核才在 `aggregate_reviews` 里收到"旧产物缺失/已修改"。要真正兑现"返工只作废受影响的那一页"，需要补一个归档步骤：每轮复核通过时产出重写过路径、重记摘要的留档件。

页面改造落在哪些页、`pageStyleSha256` 的归页规则、以及"判不准时宁可多失效"的边界，见下面的"有限继承"。**注意 `:root`、`body`、`*`、`@media` 这类判不出作用域的样式一改就是全篇失效**，那时所有页都要重看。

### warningReview

`audit.warnings` 里的每一条"需目视判断"都要在这里被处置过：

```json
"warningReview": [{"warning": "audit.warnings 里的原文", "status": "accepted|fixed", "note": "接受的理由，或改在哪一页"}]
```

- `warning` 取 `audit.warnings` 的**原文**，逐条对应；少一条就会被点名拒绝，多一条没有意义。
- `accepted` 表示看过之后判断它不构成问题，`note` 要写清凭什么这样判断（例如"已按实际尺寸看过，两行是该页标题的必要断行"）；`fixed` 表示已修，写清改在哪里并已重跑验收档。
- 多位审查者可以各处置一部分，聚合时取并集；覆盖不全会由审查合同拦住。
- 这不是新的通过项：告警本身仍不阻塞交付，**被拦住的是"没人处置"**。audit 没有告警时留空数组即可。

### issues

每项形如 `{"severity": "minor|major|blocking", "status": "open|resolved", "description": "..."}`。**major 与 blocking 必须 resolved 才能交付。** 没有问题也要给出空数组，明确表示检查过。

### 有限继承

**怎么把它写出来见上面"未变页怎么引用旧审查：`inheritedFrom`"**——字段结构与最小示例在那里。这一节说的是边界：哪些页算"未变"。

局部修改之后，只有同时满足全部条件的未变范围才可以引用旧审查：

- 该页的页面内容、命中该页的样式作用域、公共依赖（字体、脚本、按引擎比）、渲染图像和页序经核对均未变；
- 旧 audit、旧 review 与两份产物文件的摘要仍然一致，且旧 audit 的工程检查通过、**`tier` 是 `acceptance`**；
- 旧审查者本人覆盖过该条证据；旧的未决问题被本次完整保留。

**失效半径按页算。** `evidenceManifest` 里每条证据带三个逐页摘要：`pageSha256`（该页 DOM 内容）、`pageStyleSha256`（能命中该页的样式规则）和 `sha256`（该页实际渲染图字节），共同的 `dependenciesSha256` 只覆盖 deck 级身份、字体、脚本与**判不出作用域的样式**。所以改第 5 页的样式只作废第 5 页，其他页照常继承。

这条半径的边界要说清：`pageStyleSha256` 由浏览器逐条选择器判定——只有当一条规则**能证明**命中的元素全部落在某张幻灯片内时才归该页。`:root`、`body`、`*`、伪元素、任何非普通样式规则（`@media`、`@font-face`、`@keyframes`、`@page` 等）、读不到 `cssRules` 的外部样式表，以及当前匹配不到任何元素的规则，一律归公共依赖，一改就全篇失效。判不准时宁可多失效，不会漏失效。

任一条不能证明，就复验该页。**公共样式或共享依赖变化不能因为"源文字没改"而跳过。** 旧 major 的"已修"还需要本次证据，不能只把状态改成 resolved。不得给旧截图换上当前哈希来冒认本次看图。

### 聚合与打包

```sh
# 先出骨架：证据 id、告警原文、绑定摘要由工具填好，人只填判断
node scripts/make_review.cjs /任务/renders/audit.json /任务/renders/author.json --role author --reviewer 作者名
node scripts/make_review.cjs /任务/renders/audit.json /任务/renders/independent.json --role independent --reviewer 独立复核者名
# 只改了几页时，让未变的页继承旧审查；工具会按逐页摘要判出哪些能继承、哪些必须重看
node scripts/make_review.cjs /任务/renders/audit.json /任务/renders/independent.json --role independent --reviewer 名 --inherit /旧/audit.json /旧/independent.json

node scripts/aggregate_reviews.cjs /任务/renders/audit.json /任务/renders/review.json /任务/renders/author.json
# 派生为 independent 的任务再追加 /任务/renders/independent.json
node scripts/package_delivery.cjs /任务/deck.html /任务/renders/deck.pdf /任务/delivery 报告名
```

`make_review.cjs` 已经存在的输出不会覆盖，除非加 `--force`——那是一份填过判断的记录，不该被骨架盖掉。骨架里的 `status` 是 `incomplete`、`checks` 是 `not_reviewed`，占位不填会被聚合点名；**它替你做的是抄写，不是判断**。

简单任务不提供独立结果参数。输入必须是真实的结构化 JSON；聚合结果 `incomplete` 时要补查，不能把自然语言、缺项或错误格式当成空问题。作者与独立审查使用同一套结构，**不能用 Markdown 报告替代聚合输入**。

打包默认拒绝覆盖已存在的交付文件，确认替换时加 `--force`。

## 未做完：只用预览

审查还没做完时，在打包命令加 `--preview`：输出名、标题与元信息都会标成预览，不能称正式通过。预览仍然要通过工程与文件一致性底线，只是不检查 review。

## 旧格式与新稿

旧格式的审查只在兼容路径下被接受，不是新稿示例。不要删除版本属性或任务合同来降级绕过检查；迁移后要执行现行 QA 与审查。

## 一致性与变更

打包会核对当前 HTML/PDF 的路径、页数、SHA-256、audit 与 review；内嵌 PDF 必须逐字节等于独立 PDF，且不更改正文。修改文字、数据、主题、字体或页序之后，重建受影响的产物并复核；只有满足有限继承的未变范围可以引用旧审查。后续反馈推翻旧验收时，保留原记录并明确撤回范围，不继续引用旧结论。

交付给两个可打开的文件、页数、验证状态和实际限制。下载按钮提供已验收的 PDF，浏览器打印只是临时用途。交付层改动跑 `test_delivery.cjs`，QA 规则改动跑 `test_qa_policy.cjs`，证据归属或失效半径改动跑 `test_review_inheritance.cjs` 与 `test_evidence_scope.cjs`；常规制稿只做受影响成稿检查与实际复核。
