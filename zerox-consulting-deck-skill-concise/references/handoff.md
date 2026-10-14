# 切分与交接：单页制作与独立复核

要并行制作，或要安排未参与制作的独立复核时读。读完要能：把一份报告切成互不依赖的单页任务派出去、把复核任务交出去，并由主会话统一收口。

下面两个模板都是**自包含**的：连模板带一页简报交出去，对方不必再读本技能的其他文件，就能产出合规结果。

## 主会话编排

- **什么时候委派**：任务能独立判断、输入能一次给齐，且委派确实省时或提升质量。共享状态、连续决策和简单编辑由主会话直接做；每个委派任务要有明确输入、输出路径与完成判据，各自约定输出路径以免多人改同一文件。
- 独立证据任务与独立分析任务可以并行；制作所依赖的结论要先完成相应分析，必要时返回修订。
- S2 的独立分析复核与 S6 的成稿独立复核职责不同：复杂任务两者都需要；简单 editorial 可先由作者核对并如实记录范围。
- 主会话保留综合责任，抽查返回依据，不直接采信代理摘要；代理可以质疑假设与结论，但不能靠角色资历压制证据。
- **最终结论由主会话汇总并验证。** 修复后只复验受影响任务与传播到的页面，新问题显示系统性缺陷时才扩大检查；没有代理工具时由主会话执行，并如实记录独立复核未执行。

## 模板一 · 单页制作契约

派发单页时把下面整段交给执行者，替换花括号内容。

```text
你是本报告的其中一页制作者，只做第 {页码} 页。

【本页简报】
主张：{本页主判断，一句话}
读者要看清的关系：{…}
实现入口（data-form）：{pages.json 中本页的 form 值}
实际图型（data-visual）：{pages.json 声明 visual 时原样填写；它不受组件清单限制}
主证据与互补内容：{…}
关键数字、单位与口径：{…}
来源与边界：{…}
用户明确要求：{构图／密度／留白／对齐等；没有就写"无"}

【输出两个文件】
1. {目录}/pages_{批次}.html —— 一个顶层 <section class="slide"> 片段（可以只含这一页；类名与属性按下方骨架）
2. {目录}/page_{批次}.css —— 本页样式，不得含 @import

【页面骨架：照抄容器名，不要改】
<section class="slide reading" data-form="{本页形式}" data-frame-boundary="line|integrated|space">
  <div class="slide__frame" aria-hidden="true"></div>
  <div class="slide__tracker">章节名称</div>
  <header class="slide__header">
    <h1 class="slide__title">本页主判断</h1>
    <p class="slide__lead">必要范围或解释</p>
  </header>
  <div class="slide__body">正文与展品</div>
  <div class="source">来源与边界</div>
  <div class="slide__page">{页码}</div>
</section>

【必填：data-form】照抄简报的实现入口；通用 SVG 用 svg.custom，能承载现成组件外的图型。简报给了 visual 时同时写 data-visual；缺失或与 pages.json 不一致会失败。

【类名随 mode 走，不要写死】骨架里的 reading 类只在报告为 reading 时保留；报告是 presentation 时必须去掉，写成 `<section class="slide" …>`。两者不一致装配直接失败。

【必填：data-frame-boundary】三选一，没有默认值。
- line：标题之后需要清楚的分区，在标题组与正文留白中放 1px 淡线
- integrated：正文首排模块已有承担分区的顶线（如全宽表格上边），省去标题线
- space：全幅图、密集页或留白已足够
封面与全出血页另加 data-frame="off"，但 data-frame-boundary="space" 仍必须写。

【可用类：装配器已内联，直接用；需要新结构就写自己的类，不要改这些类的语义】
布局：.evidence-grid .layout-split .layout-three .layout-paired .layout-stack
      .proof-layout（.proof-main／.proof-aside，用 --proof-ratio 调比例）.plot-stack
展品：.exhibit > h2 + .unit + .graphic（svg 放 .graphic 内）
表格：.data-table（th/td 与 .num .selected .group）  .analytical-table（caption .column-unit .table-bar .total .group）
比较行：.precision-table .precision-row（.head） .precision-cell .precision-number .precision-bar-track／.precision-bar／.precision-bar-zero
文字：.annotation .evidence-note .decision-strip .matrix-note
状态：.status-label .status-good .status-risk .status-caution .microbar .row-label

【硬约束】
- 静态装配只接受内联 SVG 与 data: 资源。禁止 script、canvas、iframe、.chart、data-opt／
  data-recipe、外部 URL、@import、事件属性（on*）、srcset。要图表就在构建期 SSR 成内联
  SVG 再放进来；只调用配方 build 或 prepare、没有渲染成 SVG 的写法一律不能进静态稿。
- 禁止装饰性色条模块：注释／判断块的侧边条、数字卡片的顶部色条，以及换类名、伪元素、
  阴影、渐变或 SVG 画的同类外观，全部禁止。数据条、坐标轴、关系线、必要分隔与 quiet
  母版不在禁令内。去掉边条后要重排内容，不能留下同样大的空框。
- 颜色只从 assets/deck-themes.js 已注册的角色取；该文件是唯一来源，这里不列全表（清单会
  随主题扩展过期）。按语义选：结构与品牌 brand／brand-mid，强调 accent／accent-vivid，
  表格强调列 selected，正文、底纹与交替行 ink／gray-1..4／surface，状态 good／risk／
  caution 及其 -soft，类别 cat-1..6，连续量 seq-1..5，偏差 delta-*。
  字体只从 assets/deck-typography.js 取。不要写死十六进制色值或字体名，不要用系统字体。
- 字号角色：页主判断 32px/700，模块标题 18–20px/600，正文 16–17px，常规数据 15–16px，
  表头 15px/600，来源 12px。数字右对齐并用 lining-nums tabular-nums。

【交付前自检，逐条过】
- 每页都有 data-form，值照抄简报，没有自创（封面、参考资料、封底、分隔页除外）
- reading 类与该页所属报告的 mode 一致（presentation 时已去掉）
- 每页都有 data-frame-boundary
- 没有 script／canvas／外部 URL／@import
- 没有装饰色条模块
- 标题声称的"链条、差异、条件"，读者能在展品里找到，不是只在正文里读到
- 收短模块后重新组织过整页；没有短文字大空框，也没有把内容全部贴顶就结束
- 同层文字基线、共享比较轨道、实际绘图区对齐；来源有独立安全区
- 只改了这一页的文件，没有动别人的输出
```

## 模板二 · 独立复核契约

派发复核时把下面整段交给执行者。复核者必须没有参与该稿制作。

```text
你是本报告的独立复核者，未参与制作。请验收 {deck 绝对路径}，
把结果写到 {目录}/review.independent.json。

【输入必须齐备；缺任何一项就在结果里写明缺哪项，不要假装看过】
原始用户目标／用户明确偏好与认可、否定基线／task.json／原材料与分析定位／
作者规格／HTML／本次 audit.json／逐页截图／实际 PDF 栅格图

【输出：与主路径同结构的 JSON】
{
  "schemaVersion": 3,
  "status": "incomplete",
  "reviewer": "实际审查者标识",
  "independence": "independent",
  "htmlSha256": "取自 audit.htmlArtifact.sha256",
  "pdfSha256": "取自 audit.pdfArtifact.sha256",
  "auditSha256": "对 audit 解析对象执行 hash(stable(audit)) 的实际值",
  "checks": {
    "analysis": {"status": "not_reviewed", "basis": ""},
    "evidence": {"status": "not_reviewed", "basis": ""},
    "visual":   {"status": "not_reviewed", "basis": ""}
  },
  "coverage": [{
    "reviewer": "实际审查者标识",
    "independence": "independent",
    "layers": ["page", "exhibit", "annotation", "typography"],
    "htmlPages": [1],
    "pdfPages": [1],
    "evidence": [{"id": "html:实际pageId"}, {"id": "pdf:实际pageId"}]
  }],
  "issues": []
}

【格式规则】
- 实际检查完再改 status 为 complete；三项 checks 都要有非空 basis 和真实结论。
  analysis／evidence 可为 pass 或有实际理由的 not_applicable；**visual 只有在真的看过
  每页 HTML 截图和最终 PDF 之后才能写 pass，没看图就写 not_reviewed。**
- evidence 的 id 必须从本次 audit.evidenceManifest.entries 里选，媒介与页号逐一匹配；
  不能拿一张截图覆盖多页，也不能把 HTML 图当 PDF 证据。
- 哈希算法用 scripts/report_contract.cjs 的 hash／stable；auditSha256 是规范化对象摘要，
  不是 audit.json 原始文件字节摘要。
- issues 用 severity=minor／major／blocking、status=open／resolved、description；
  major 与 blocking 必须 resolved，否则不能称通过。

【允许与不允许】
允许用 helper 填路径、文件摘要和待检查槽位——这些是机械字段。
**不能预填 pass、complete、已看页码或独立身份**——这些是判断，必须来自实际检查。

【检查什么】
分析／证据：从最终标题回溯到发现与原文，复算关键派生数；核对重要反证、目标与预测、
时期／单位／范围、建议的成立条件是否保留。关键否定、分母、状态和条件要对照原文与
对象，**不能用总体文字覆盖率代替**。
视觉：先独立看总览、每页原尺寸图和实际 PDF，判断成品是否兑现原始目标，再查局部排印。
逐页核对模块内空置、全页剩余空间、同层文字基线、比较轨道、真实绘图区与来源安全区；
**外框相齐不代表内容对齐**。允许有效非对称与有目的留白，不接受短文字大空框或机械
等高填充。检查禁用色条模块，包括自定义类、伪元素和 SVG 变体；语义数据条、轴线、
必要分隔与 quiet 母版不误杀。
工程：实际浏览器、打印与离线检查；自动 PASS 与文字存在不等于视觉或 PDF 图形完整。
字体：实际字体／字重、字体就绪、PDF 嵌入、冷缓存断网、混排数字；**CSS 名字与
document.fonts.ready 本身不足以证明字体身份。** 记录缺字、伪粗与意外回退。

【如实记录】
没有代理工具、或无法看图时，写明缺哪项、完成到哪一步，不冒称独立复核已执行。
未看到的图片不能登记为看图通过；作者已修复的说法不能替代复验。局部修订只有在未变页
的身份与原证据关联核对后才继承，不能替换旧截图哈希冒认新检查。
```

复核者只需要读[交付契约](delivery.md)确认现行 schema 与聚合方式；本模板已包含它需要的字段。
