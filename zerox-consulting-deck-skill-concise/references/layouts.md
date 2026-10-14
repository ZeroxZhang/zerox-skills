# 单页布局选型：把阅读任务变成页面结构

> **什么时候读**：S3 逐页构思，定完 `proves`、选 `form` 之前。
> **读完要能做什么**：找到与本页读者任务相符的页级结构；知道它读起来是什么顺序、什么时候不该用；并直接写出 `pages.json` 的 `regions`。

与[图表选型](charts.md)对称：`charts.md` 管**关系 → 图型**，本文管**读者任务 → 页级结构**。先按 `charts.md` 定这页要让人看出什么关系，再回来选结构；两者都定了才写 `pages.json`。

## 这份清单是什么，不是什么

**它是构思词汇表，不是模板库。** 选中一条之后，仍要回到"这页要让读者看出什么关系"重新检查一遍；对不上就改构思或改结构，**不是把材料切碎塞进框里**。

- 这是**可选结构**。清单里的类名、比例、内联 grid 都可以不用；自己写布局同样合法。立场见[整页创作](page_design.md)「不做过度约束」。
- **不排名、不给配额、不规定填充率、不推荐常用优先级。** 相邻页面可以用完全不同的结构；一页只用一条成立，一页综合几条也成立。条目按族分组、族内按阅读任务的复杂度排，**排序不含推荐意味**。
- 条目里的比例是**起点**：先算主视觉需要多大才能充分表达，再反推比例。`8fr/4fr` 可以改成 `9fr/3fr` 或 `7fr/5fr`，只要主次和阅读顺序还成立。
- `regions` 是**示例值**。`span` 只表示相对宽度份额，**不是栏数、不必合计 12**；校验只要求它是正数。
- 可用高度是**预算，不是定律**。实际按标题与来源的真实行数算。
- 示例文案与数据为虚构，只用于说明结构，不作为证据。

**三条最容易被违反的**：

1. 不要从空白模板逐格填摘要——先有构思，再找结构。
2. 不要因为某条结构好看，就让它决定内容分工。
3. 不要用结构名代替判断。"这是一页矩阵"不是这页成立的理由。

## 与「可选骨架」的关系

[整页创作](page_design.md)的「可选骨架」表是**更粗一层的原型词**（12 个原型能承担什么阅读任务）；本文是这些原型在 1280×720 上的**具体落法**。两层并存，不互相替代：拿不准用哪个结构时，先在骨架表里找读者任务，再回本文找对应落法。

| 骨架表原型 | 本文条目 |
|---|---|
| 纯文本 | 辛-1 三栏研究论述 |
| 单图表 | 甲-2 全幅主图＋底部解读 |
| 图表＋解释 | 甲-1 主图＋侧栏解读 |
| 多展品 | 戊-2 主图＋四项辅助证据、丙-3 同尺度小多图 |
| 表格 | 辛-2 多对象×多指标总表、戊-3 完整表格＋决策栏、戊-4 双明细表＋共通判断 |
| 框架／概念 | 丁-4 分层结构＋逐层释义、己-3 顶层命题＋双支柱 |
| 流程 | 丁-1 横向阶段＋共同条件、丁-2 阶梯推进 |
| 时间线／路线图 | 庚-2 路线图＋风险门槛、结-1 目录与路线图 |
| 对比 | 乙-1 双栏对照、乙-2 三／四栏并列 |
| 执行摘要 | 甲-3 结论横带＋三项支撑、己-1 中轴结论＋四侧条件、己-2 决策摘要＋证据与异议 |
| 章节分隔 | 结-2 章节导读 |
| 附录 | 辛-2、结-1 |

## 先算可用高度，再选结构

`1280×720` reading：`.slide.reading{padding:32px 40px 26px}` → 内容盒 **1200 × 662**。角色基线见[母版与排印](type_frame.md)。

| 项 | 计算 | 值 |
|---|---|---|
| 页主判断 | `32px × 1.28` | 40.96 / 行，另加 margin 8 |
| 副题 | `15px × 1.45` | 21.75 / 行 |
| 标题区 header | `n × 40.96 + 8 + 21.75` | n=1 → **70.71**；n=2 → **111.67** |
| 正文区 body | `662 − header − 16` | n=1 → 575.29；n=2 → 534.33 |
| 来源 | `12px × 1.35` + margin 12 | 单行 **28.2**；两行 44.4 |

引擎的 `.slide__body` 只有 `flex:1;min-height:0;display:grid;gap:16px`，**没有自带行模板**；来源放哪里由作者决定，两种写法的主内容高度不一样：

| 来源位置 | body 写法 | 主内容可用高度（标题 1 行 / 2 行） |
|---|---|---|
| body 内 | 显式声明 `grid-template-rows:minmax(0,1fr) auto` | **527.1 / 486.1** |
| body 外（[最小页面结构](type_frame.md)） | 不用改，来源留在 body 之后 | **547.1 / 506.1** |

来源放 body 内却不写行模板时，两行会按内容平分剩余高度——读者会看到主体被压掉近一半，这是最容易踩的坑。

宽度同理，`1200` 内容盒、gap 24 下实测：

| 写法 | 实际列宽 |
|---|---|
| `.layout-split` 8fr/4fr | 784 / 392 |
| `repeat(3,minmax(0,1fr))` | 384 |
| `repeat(2,minmax(0,1fr))` | 588 |
| 784 的列内再分两栏 | 380 |

**380px 是带标签图表的实际下限**：图中再排「名称 ＋ 标注 ＋ 数值」三列，绘图区只剩一半，整张图的文字会被一起缩到读不出。要把两项证据并排，就让它们共用一套坐标系（一张图两条序列）或换到通栏，不要各占半宽。

侧栏、解读区这类**自然高度**的分区顶部对齐，其下方空白是预期的，不要拉高填充。但若这一栏只有两三行短句（实测这类分区常在 130px 上下，不到列高的四分之一），与其留一列空白，不如把判断并进证据组，或干脆改甲-3 的结论横带——那就不是独立的栏了。

**选结构前先用这张表估一下装不装得下**；装不下时改的是布局、分面或分工，不是把字号压小——图型选定后不因放不下而改表，见[图表选型](charts.md)。

## 族与条目

`regions` 三条硬规则见本文末「从选型接到 `pages.json`」。各条目的「常见 form」取自 `assets/deck-forms.js`。

**形式名后的 `†` 表示该形式已接入通用标注层，摆位自动完成，直接写 `annotations` 即可。** 没有 `†` 的形式（`kit.tree`、`kit.swimlane`、`kit.processFlow`、`kit.comparisonTable`、全部 `diagram.*`、全部 `html.*`、`svg.custom`）**不是不能写旁解读，而是标注要由作者摆位**：声明 `annotationMode:"manual"` 之后照常写 `annotations`，并承担逐页目视验收。不声明就写会被拒绝——那是静默默认，不是自由选择。

这条界线只管"谁负责摆位"，**不管你能画什么**。旁解读是每页都要争取的表达，如果把它变成"只有带 `†` 的形式才配标注"，作者就会被推回那几种形式，编码族反而更单一——这正是要避免的结果。遇到装着放下但标注摆不开的情况，先考虑换布局、分面或缩小标注范围，而不是换掉图型。

### 甲 单证据统领

#### 甲-1 主图＋侧栏解读

- **读者任务**：一个核心图表已能承担证明，另有两三个解释点要贴着它说。
- **阅读路径**：判断标题 → 主图 → 侧栏解释 → 来源。
- **落地**：`.layout-split`（`minmax(0,8fr) minmax(0,4fr)`，gap 24 → 实测 784 / 392）。主图更需要宽度时改内联 `minmax(0,9fr) minmax(0,3fr)`。
- **regions**：`[{"slot":"main","span":8,"form":"<本页 form>","role":"primary"},{"slot":"aside","span":4,"form":"html.text","role":"support"}]`
- **取舍**：侧栏**不要再开一个同等复杂的新议题**；窄于 4fr 时只放短判断，不放表。
- **不该用**：主图需要 >9fr 才读得清（长序列、宽散点）→ 改甲-2。
- **常见 form**：`recipe.timeSeries`†／`kit.waterfall`†／`recipe.rankedBar`† ＋ `html.text`

#### 甲-2 全幅主图＋底部解读

- **读者任务**：主图的**宽度本身**就是证明力（横向趋势、长序列、宽比较）。
- **阅读路径**：标题 → 通栏图 → 左下事实 → 右下含义。
- **落地**：body 内两个子节点——图独占首行通栏，下方接 `.layout-split`（8fr/4fr）。行距用 body 默认 gap 20。
- **regions**：`[{"slot":"top","span":12,"form":"<本页 form>","role":"primary"},{"slot":"bottom","span":8,"form":"html.text","role":"evidence"},{"slot":"bottom","span":4,"form":"html.text","role":"context"}]`
- **取舍**：底部只在图**说不完**时出现；图自己能说完就整页给图。
- **不该用**：短宽比图通栏后更空；需要精确读数的散点被压到一窄条后读不出 → 改甲-1。
- **常见 form**：`recipe.timeSeries`†／`kit.stacked`†／`recipe.histogram`† ＋ `html.text`

#### 甲-3 结论横带＋三项支撑

- **读者任务**：一个综合判断由三个同级维度共同支持（执行摘要、阶段复盘）。
- **阅读路径**：横带结论 → 三项从左到右 → 回到结论。
- **落地**：内联 `grid-template-rows:auto minmax(0,1fr)`；横带占首行，下行用 `.layout-three`。
- **regions**：`[{"slot":"top","span":12,"form":"html.text","role":"primary"},{"slot":"bottom","span":4,"form":"html.kpi","role":"support"},{"slot":"bottom","span":4,"form":"kit.bullet","role":"evidence"},{"slot":"bottom","span":4,"form":"kit.bullet","role":"evidence"}]`
- **取舍**：三项**必须真的同级**；横带里不要塞第二层论证，否则会被读成标题。
- **不该用**：三项之间没有共同结论、只是三个并列事实 → 改乙-2。
- **常见 form**：`html.kpi`／`precision.columns`† ＋ `html.text`

### 乙 并列与对照

#### 乙-1 双栏对照

- **读者任务**：两个方案／群体／时期在**同一组维度**上的取舍。
- **阅读路径**：标题 → 左右同序比较 → 每栏结论。
- **落地**：`.layout-paired`（`repeat(2,minmax(0,1fr))`，gap 24）。一侧明显更重时改内联 `minmax(0,7fr) minmax(0,5fr)`。
- **regions**：`[{"slot":"left","span":6,"form":"<本页 form>","role":"primary"},{"slot":"right","span":6,"form":"kit.comparisonTable","role":"support"}]`
- **取舍**：两栏**维度和口径必须一致**，不能各写各的问题；对称不等于相等面积。
- **不该用**：两侧不是同一维度的对照（如"现状"对"建议"）→ 改己-2 或己-3。
- **常见 form**：`kit.comparisonTable`／`html.table`／`kit.dumbbell`†／`kit.slope`†

#### 乙-2 三栏／四栏并列

- **读者任务**：三到四个同级主题或短信息单元（分群、能力、选项、原则）。
- **阅读路径**：标题 → 逐栏 → 横向比较各栏的相同字段。
- **落地**：三栏 `.layout-three`；四栏内联 `repeat(4,minmax(0,1fr))`，或用 `.evidence-grid` 每条 `span 3`。
- **regions**：三栏 `[{"slot":"left","span":4,"form":"html.text","role":"primary"},{"slot":"main","span":4,"form":"html.text","role":"support"},{"slot":"right","span":4,"form":"html.text","role":"evidence"}]`
- **取舍**：每栏 4fr ≈ 372px 正文宽，**只适合短段落**；四栏只放短句。
- **不该用**：每项超过四个字段或需要长论述 → 改辛-2 或拆页。**"相邻页重复三栏段落"是本技能点名的过度摘要信号**，出现时回原材料找还没表达的关联，而不是换外观。
- **常见 form**：`html.text`／`kit.bullet`†／`kit.processFlow`／`html.kpi`

### 丙 矩阵与分面

#### 丙-1 四格矩阵

- **读者任务**：两个维度交叉出四种处理策略（优先级、机会分层、组合判断）。
- **阅读路径**：先读行列语义 → 左上优先项 → 其余三种策略 → 右侧收束。
- **落地**：内联 `minmax(0,7fr) minmax(0,5fr)`；左栏内部 `grid-template-columns:repeat(2,minmax(0,1fr));grid-template-rows:repeat(2,minmax(0,1fr))`，gap 24。
- **regions**：`[{"slot":"left","span":7,"form":"html.matrix","role":"primary"},{"slot":"right","span":5,"form":"html.text","role":"support"}]`
- **取舍**：**两轴必须有名称和方向**；只把四段话放进四个框不算矩阵。
- **不该用**：两个维度在材料里高度共线（如"重要性"与"紧急度"）→ 拆成一维排序。
- **常见 form**：`html.matrix`／`kit.heatmap`†（连续量时）／`html.text`

#### 丙-2 三对象×三维度九格

- **读者任务**：三个对象在三个维度上的定性比较（供应商、技术方案、进入路径）。
- **阅读路径**：第一行识别对象 → 同行比较 → 沿列汇总取舍。
- **落地**：`.evidence-grid`，九格各 `grid-column:span 4`；下方通栏一行写口径与图例（`span 12`）。
- **regions**：`[{"slot":"full","span":12,"form":"html.matrix","role":"primary"},{"slot":"bottom","span":12,"form":"html.text","role":"context"}]`（按 R3，九格只写一条，不为每格各写一条）
- **取舍**：单格只放短判断；需要长论证时减少维度，不是缩小字号。
- **不该用**：三个对象在不同维度上不可比 → 改辛-2 明细表。
- **常见 form**：`html.matrix`／`html.table` ＋ `html.text`

#### 丙-3 同尺度小多图

- **读者任务**：多个同口径序列并行比较（区域、产品线、客户分群）。
- **阅读路径**：逐行扫描变化 → 定位差异单元 → 读对应解释。
- **落地**：内联 `repeat(3,minmax(0,1fr))` × 2 行，gap 24（实测每格 384×261，图区 384×217）；统一量尺写进图内。
- **regions**：`[{"slot":"main","span":12,"form":"svg.custom","visual":"small-multiples","role":"primary"}]`
- **取舍**：**必须共用同一量尺**，否则图形会夸大差异；带面积填充时**基准线要画在填充之上**，否则基期那条线被填充吃掉，六张图就没有共同参照了。刻度只在首列出现，每张只标自己的变化量，绝对值交给公共刻度——六张各标一套绝对值等于六套坐标。用 `svg.custom` 时 `visual` 必填，并要在 pages.json 用 `encodingFamily` 声明实际编码族（本条目是 `trend`）——未登记入口不报族，族的分布就看不见它；成稿要带同名 `data-visual`。每格只有 384 宽，图内标签实际落在 12–13px，这是这一条的固有代价。
- **不该用**：序列超过 6 个，或读者要看的是时间趋势而非横向差异 → 减少小图或改分面。
- **常见 form**：`svg.custom`（`visual: small-multiples`）／`recipe.timeSeries`†／`kit.bullet`†

### 丁 递进与拆解

#### 丁-1 横向阶段＋共同条件

- **读者任务**：三到五个顺序明确的阶段，且跨阶段有共同门槛。
- **阅读路径**：左 → 右读阶段 → 底部读共同约束。
- **落地**：内联 `grid-template-rows:minmax(0,2fr) minmax(0,1fr)`；上行 `repeat(4,minmax(0,1fr))`。
- **regions**：`[{"slot":"top","span":3,"form":"kit.processFlow","role":"primary"},{"slot":"top","span":3,"form":"html.text","role":"support"},{"slot":"top","span":3,"form":"html.text","role":"support"},{"slot":"top","span":3,"form":"html.text","role":"support"},{"slot":"bottom","span":12,"form":"html.text","role":"context"}]`
- **取舍**：**等宽不表示等时长**，**顺序不冒充因果**；真实时长差异明显时改用有刻度的形式。
- **不该用**：阶段超过 5 个，或阶段之间有交叉依赖 → 改泳道或拆页。
- **常见 form**：`kit.processFlow`／`diagram.process`／`diagram.swimlane`

#### 丁-2 阶梯推进

- **读者任务**：阶段之间有先决条件或成熟度递进，且必须**看见依赖**。
- **阅读路径**：左上 → 中 → 右下；空白本身表示推进方向。
- **落地**：内联 `grid-template-columns:repeat(4,minmax(0,1fr));grid-template-rows:repeat(4,minmax(0,1fr))`；第 i 个模块落在第 i 行第 i 列，逐级下移。
- **regions**：`[{"slot":"left","span":3,"form":"html.text","role":"primary"},{"slot":"main","span":3,"form":"html.text","role":"support"},{"slot":"right","span":3,"form":"html.text","role":"support"},{"slot":"right","span":3,"form":"html.text","role":"evidence"}]`
- **取舍**：底部空白必须是**方向**而不是"没做完"——两者在截图里长得一样，只有在有明显台阶时才成立。
- **不该用**：阶段之间其实没有先决关系（那只是并列）→ 改丁-1 或乙-2。
- **常见 form**：`diagram.hierarchy`／`kit.processFlow`／`html.text`

#### 丁-3 逻辑拆解树

- **读者任务**：从整体拆到驱动因素或根因（指标拆解、问题诊断）。
- **阅读路径**：左侧总指标 → 中间一级驱动 → 右侧计算口径。
- **落地**：内联 `grid-template-columns:3fr 4fr 5fr`；三栏同起一行，拆解方向由左向右读，不靠缩进表示层级。
- **regions**：`[{"slot":"left","span":3,"form":"kit.tree","role":"primary"},{"slot":"main","span":4,"form":"html.text","role":"support"},{"slot":"right","span":5,"form":"html.text","role":"evidence"}]`
- **取舍**：**每层必须同一拆分逻辑**（都加法或都乘法），混用会让读者算不通。
- **不该用**：叶子超过 5 个 → 改两层或拆页。
- **常见 form**：`kit.tree`／`diagram.hierarchy`／`kit.waterfall`†

#### 丁-4 分层结构＋逐层释义

- **读者任务**：抽象目标逐级落到动作（战略解码、能力层次、治理结构）。
- **阅读路径**：左侧自上而下理解层级 → 右侧读层间如何传递与验证。
- **落地**：`.layout-paired`；左栏内部 `grid-template-rows:repeat(3,minmax(0,1fr))`。
- **regions**：`[{"slot":"left","span":6,"form":"diagram.hierarchy","role":"primary"},{"slot":"right","span":6,"form":"html.text","role":"context"}]`
- **取舍**：**空间分层优先于装饰性金字塔**；只画金字塔不作层间释义，属于用形状代替论证。
- **不该用**：层级之间没有传递关系（只是三个并列项）→ 改乙-2。
- **常见 form**：`diagram.hierarchy`／`html.text`／`kit.bullet`†

### 戊 主辅互补

#### 戊-1 指标概览＋证据组合

- **读者任务**：同一主题同时需要 KPI、局部证据和管理解读。
- **阅读路径**：左上指标 → 左下两组证据 → 右侧综合判断。
- **落地**：内联 `minmax(0,8fr) minmax(0,4fr)`；左列内部 `grid-template-rows:auto minmax(0,1fr)`（上为 KPI 横排，下为证据组），右列为解读。**这条行模板不能省**：不写时 KPI 行会跟着内容一起被撑到实测 238px，证据组只剩 285px。
- **regions**：`[{"slot":"top","span":8,"form":"html.kpi","role":"primary"},{"slot":"main","span":8,"form":"kit.bullet","role":"evidence"},{"slot":"aside","span":4,"form":"html.text","role":"context"}]`（证据组按 R3 只写一条。784 再一分为二每张只剩 380，低于带标签图表的可读下限——这一块通常只放一张图，或把两项证据做成同一坐标系里的两条序列）
- **取舍**：指标不先被看见就失去概览作用；解读区不要变成第二组证据。`html.kpi` 上限 5 张卡，且**每张要有比较基准**。
- **不该用**：指标之间没有可比基准（只是几个孤立的数）→ 改甲-3。
- **常见 form**：`html.kpi`／`kit.bullet`†／`kit.dumbbell`† ＋ `html.text`

#### 戊-2 主图＋四项辅助证据

- **读者任务**：一个主问题需要四个局部切片解释。
- **阅读路径**：主图 → 四格证据 → 检查解释是否与主图一致。
- **落地**：内联 `minmax(0,6fr) minmax(0,6fr)`；右栏内部 `grid-template-columns:repeat(2,minmax(0,1fr));grid-template-rows:repeat(2,minmax(0,1fr))`，gap 24。
- **regions**：`[{"slot":"main","span":6,"form":"<本页 form>","role":"primary"},{"slot":"aside","span":6,"form":"kit.bullet","role":"evidence"}]`（四格按 R3 写一条）
- **取舍**：主图**必须保住坐标空间**；小格只承载短证据。
- **不该用**：把主图塞不下的东西挪进小格——那是改分工，不是改布局。
- **常见 form**：`recipe.timeSeries`† ＋ `kit.bullet`†／`precision.columns`†

#### 戊-3 完整表格＋决策栏

- **读者任务**：比较维度多、要保留可复核细节，同时要给出判断。
- **阅读路径**：判断 → 表格逐项核对 → 侧栏确认成立条件。
- **落地**：`.layout-split`（8fr/4fr）；表格更宽时改内联 `minmax(0,9fr) minmax(0,3fr)`，并把 `regions` 的 span 同步改成 9/3。
- **regions**：`[{"slot":"main","span":8,"form":"html.table","role":"primary"},{"slot":"aside","span":4,"form":"html.text","role":"support"}]`
- **取舍**：3fr ≈ 285px，**侧栏只放短判断，不放第二张表**。
- **不该用**：侧栏内容本身需要横向比较 → 改戊-4 或拆页。
- **常见 form**：`html.table`／`kit.comparisonTable`／`html.matrix` ＋ `html.text`

#### 戊-4 双明细表＋共通判断

- **读者任务**：两组明细要并读，但塞不进同一张宽表（成本/收益、供需、前后期）。
- **阅读路径**：左表 → 右表 → 底部共同判断。
- **落地**：`.layout-stack`（`minmax(0,1fr) auto`，gap 18）包住上层 `.layout-paired`。
- **regions**：`[{"slot":"top","span":6,"form":"html.table","role":"primary"},{"slot":"top","span":6,"form":"html.table","role":"evidence"},{"slot":"bottom","span":12,"form":"html.text","role":"context"}]`
- **取舍**：左右并排**只表示阅读节奏，不表示一一因果对应**——必须在图注写明，否则读者会误读成配对。
- **不该用**：两组明细本来就有共同主键 → 合成一张表（改辛-2）。
- **常见 form**：`html.table`／`kit.comparisonTable` ＋ `html.text`

### 己 综合与研判

#### 己-1 中轴结论＋四侧条件

- **读者任务**：一个综合结论受四项条件共同约束（可行性研判、决策门槛）。
- **阅读路径**：先看中轴判断 → 四侧条件 → 回中轴做决策。
- **落地**：内联 `repeat(3,minmax(0,1fr))`；中轴居中一栏，四项条件按二二分列左右两栏。
- **regions**：`[{"slot":"main","span":4,"form":"html.text","role":"primary"},{"slot":"left","span":4,"form":"kit.bullet","role":"evidence"},{"slot":"right","span":4,"form":"kit.bullet","role":"evidence"}]`
- **取舍**：**只适用于汇聚关系，不适用于时间顺序**。条件必须真的会改变结论；凑数的"条件"应删。
- **不该用**：条件之间有权重差异（那就不是"共同满足"）→ 改丙-1 或戊-3。
- **常见 form**：`html.text`／`kit.bullet`†／`diagram.condition`

#### 己-2 决策摘要＋证据与异议

- **读者任务**：决策者要快速读结论，同时能核对主要依据与**反对意见**。
- **阅读路径**：顶部状态 → 左侧证据 → 右侧异议与成立条件。
- **落地**：内联 `grid-template-rows:auto minmax(0,1fr)`；下行 `.layout-split`（8fr/4fr）。
- **regions**：`[{"slot":"top","span":12,"form":"html.text","role":"primary"},{"slot":"bottom","span":8,"form":"html.table","role":"evidence"},{"slot":"bottom","span":4,"form":"html.text","role":"context"}]`
- **取舍**：状态条只是入口，正文必须保留判断依据；**保留意见不能写成一行免责**。
- **不该用**：没有真实异议（那应改甲-3）；两侧其实不是同一维度的对照（→ 乙-1）。
- **常见 form**：`html.text`／`html.table`

#### 己-3 顶层命题＋双支柱

- **读者任务**：一个目标依赖两项**互补**机制（获客与留存、供给与需求）。
- **阅读路径**：顶层目标 → 左右两条路径 → 各自的验证方法。
- **落地**：内联 `grid-template-rows:auto minmax(0,1fr)` ＋ `.layout-paired`。
- **regions**：`[{"slot":"top","span":12,"form":"html.text","role":"primary"},{"slot":"left","span":6,"form":"kit.bullet","role":"support"},{"slot":"right","span":6,"form":"kit.bullet","role":"support"}]`
- **取舍**：**左右是互补关系，要区别于二选一**；两条支柱必须能被同一套指标检验。
- **不该用**：两条其实是备选方案 → 改乙-1。
- **常见 form**：`html.text`／`kit.bullet`†／`html.table`

### 庚 执行与治理

#### 庚-1 工作包×责任矩阵

- **读者任务**：多角色参与多工作包，需要明确最终责任。
- **阅读路径**：工作包 → 最终批准者 → 执行者 → 协作与知会。
- **落地**：全幅 `html.table`／`.analytical-table` 直接占满 body。
- **regions**：`[{"slot":"main","span":12,"form":"html.matrix","role":"primary"}]`
- **取舍**：**矩阵表达职责，不表达先后**；角色超过 5 个时按阶段拆分。`html.matrix` 要求权重与评分锚点透明。
- **不该用**：要表达的是时间顺序 → 改丁-1 或庚-2。
- **常见 form**：`html.matrix`／`html.table`

#### 庚-2 路线图＋风险门槛

- **读者任务**：计划、风险与"进入下一阶段的门槛"要同页管理。
- **阅读路径**：左上目标 → 左下阶段 → 右上风险 → 右下门槛。
- **落地**：内联 `minmax(0,8fr) minmax(0,4fr)`；**两列各自** `grid-template-rows:auto minmax(0,1fr)`，四格才读得出上下的分工。
- **regions**：`[{"slot":"main","span":8,"form":"html.table","role":"primary"},{"slot":"aside","span":4,"form":"kit.bullet","role":"evidence"}]`
- **取舍**：**风险不是额外的流程节点**，保持独立归属；门槛必须是可判断的条件，不是"加强沟通"。
- **不该用**：没有真实门槛，只是时间表 → 改丁-1（或结-1）。
- **常见 form**：`html.table`／`kit.processFlow` ＋ `html.text`

#### 庚-3 行动台账＋双侧约束

- **读者任务**：多项短行动要责任与时限，同时保留共同约束。
- **阅读路径**：左侧排序依据 → 中部逐项 → 右侧升级规则。
- **落地**：内联 `grid-template-columns:3fr 6fr 3fr`。
- **regions**：`[{"slot":"main","span":6,"form":"html.table","role":"primary"},{"slot":"left","span":3,"form":"html.text","role":"context"},{"slot":"right","span":3,"form":"html.text","role":"evidence"}]`
- **取舍**：明细长句改用全幅表格，**不靠压缩字号承载**。
- **不该用**：行动少于 5 项（三栏会显空）→ 改乙-2 或戊-3。
- **常见 form**：`html.table`／`html.text`

### 辛 论述与查证

#### 辛-1 三栏研究论述

- **读者任务**：文字论述多于数值比较（研究发现、访谈归纳、政策解读、方法说明）。
- **阅读路径**：左现象 → 中解释 → 右边界与待验证。
- **落地**：`.layout-three`。
- **regions**：`[{"slot":"left","span":4,"form":"html.text","role":"primary"},{"slot":"main","span":4,"form":"html.text","role":"support"},{"slot":"right","span":4,"form":"html.text","role":"context"}]`
- **取舍**：**不逐条切成卡片**，段落内部要连续；4fr 栏约 20 余中文字/行，接近可读下限。
- **不该用**：材料其实有数值比较 → 那是选错结构，不是选错栏数。
- **常见 form**：`html.text`

#### 辛-2 多对象×多指标总表

- **读者任务**：对象与指标都多，读者要**交叉查阅并逐格查数**。
- **阅读路径**：指标表头 → 重点对象 → 同列差异 → 口径说明。
- **落地**：全幅 `html.table`／`.analytical-table`；列比例用 `<colgroup>` 自定义。
- **regions**：`[{"slot":"main","span":12,"form":"html.table","role":"primary"}]`
- **取舍**：这是**主动选表格**的合法场景（读者任务本来就是逐格查数）；新增字段导致长句换行时分组或拆表，**不缩字号**。
- **不该用**：读者要的是趋势或对比结论，不是查数 → 回图表选型。
- **常见 form**：`html.table`／`kit.comparisonTable`／`html.matrix`

## 结构页：目录与路线图 · 章节导读 · 结论与行动

[首尾规则](bookends.md)负责封面、参考资料、封底三类**首尾页**的收录、格式与验收，它的规则不适用于本节。本节的三类是**正文侧结构页**，位置、页序、页面角色声明以本节为准。

**页序区别必须分清**，否则装完才发现正文页数对不上（装配会直接报页数不符）：

| 结构页 | `data-page-role` | 占 `pages.json` 正文位 | 需 `data-form` |
|---|---|---|---|
| 结-1 目录与路线图 | `content` | **是** | 是 |
| 结-2 章节导读 | `divider` | **否** | 否 |
| 结-3 结论与行动 | `content` | **是** | 是 |

`divider` 页虽不占正文位，仍是 `.slide`，**`data-frame-boundary` 仍须显式声明**。

#### 结-1 目录与路线图

- **读者任务**：进入正文前看到章节顺序、每章解决什么问题、各自的页范围。
- **阅读路径**：章节序号 → 章名 → 本章问题 → 页范围。
- **落地**：`.layout-three` 或全幅 `html.table`；章节多时用横向结构带。
- **regions**：`[{"slot":"main","span":12,"form":"html.text","role":"primary"}]`
- **取舍**：**结构面不整页铺底**；章名与页范围要能一眼扫到。条目内容要来自已冻结的正文，不预告还没写的结论。
- **不该用**：全篇不足五页时目录没有导航价值 → 省略，直接进正文。
- **常见 form**：`html.text`／`html.table`／`kit.processFlow`

#### 结-2 章节导读

- **读者任务**：感知转场，知道本章解决什么问题、结论是什么。
- **阅读路径**：章号 → 章名 → 本章问题 → 本章结论（自上而下单轴）。
- **落地**：单轴布局，右侧留白；页范围钉右上。
- **regions**：`[{"slot":"main","span":8,"form":"html.text","role":"primary"}]`
- **取舍**：**允许有意的低密度**，不套正文的密度要求；**禁止再开第二栏**。结论必须来自已冻结内容。
- **不该用**：章节很短或只有一章 → 省略导读，避免为转场而转场。
- **常见 form**：`html.text`

#### 结-3 结论与行动

- **读者任务**：知道结论、成立条件与下一步。
- **阅读路径**：结论 → 成立条件 → 行动分条（或：假设 → 验证 → 反证）。
- **落地**：结论面与条件分区；`.layout-split`（8fr/4fr）或结论横带＋分条。
- **regions**：`[{"slot":"main","span":8,"form":"html.text","role":"primary"},{"slot":"aside","span":4,"form":"html.text","role":"context"}]`
- **取舍**：**不使用整页底色**；结论必须已在正文出现过，这里只做收束，不引入新判断。
- **不该用**：结论依赖的假设还没被检验 → 先补验证页（或改用"假设—验证—反证"三轨）。
- **常见 form**：`html.text`／`html.table`

## 从选型接到 pages.json

选定结构后，把分区写进 `pages.json` 的 `regions`。字段定义只有一份来源：[交付契约](delivery.md)的 pages 一节。三条硬规则：

- **R1**：`role:"primary"` 的 `form` **必须等于** `page.form`，且**恰好一个** `primary`。校验会直接拒绝，不静默通过。
- **R2**：对称结构（双栏、九格、小多图）也要指定一个主区。**"主区"表示读者的第一落点，不表示面积更大**——对照页选左栏为主区，不代表右栏是次要证据。
- **R3**：`regions` 是**分区**声明，不是 DOM 清单。九格、六个小图、四个条件**只写一条**；每写一条，都要能在页面上指出一块独立区域。

**`regions` 不会生成布局。** 它只是给装配、QA 和交付门禁看的声明；页面实际怎么排仍由 HTML 与 CSS 决定，两者必须对得上——写 `layout-split` 就得真有两栏，写了 `aside` 就得真有一块可指认的侧栏。

`slot` 取值 `main / left / right / top / bottom / aside / full`；`role` 取值 `primary / support / context / evidence`。**`span` 只表示相对宽度份额**，写成与 fr 比例一致的数字即可（8fr:4fr → 8 和 4），不必合计为 12。

```json
{
  "page": 3,
  "proves": "商超是净下滑的主要来源，电商只抵消约三分之一",
  "form": "kit.waterfall",
  "regions": [
    {"slot": "main", "span": 8, "form": "kit.waterfall", "role": "primary"},
    {"slot": "aside", "span": 4, "form": "html.text", "role": "support"}
  ]
}
```

## 什么时候该换结构、什么时候该拆页

- **换结构**：内容与结构对不上时（如"其实是并列而非对照"），先回去改 `proves` 和分工，再重选。不要靠调整比例硬撑一个不成立的构思。
- **拆页**：一条结构装不下、且压缩会伤害可读性时拆。拆完两页都要各自成立——**拆页不是把一个判断切成两半**，而是让后半页承担新的阅读任务。
- **合并**：一页只复述上一页，或只能给出几条通用建议时合并。"一页一个判断"不要求每条摘要独占一页。
- **回原材料**：相邻页反复出现同一种弱结构（三栏段落、短条图＋长说明）时，通常是材料在选型之前就被过度摘要了。这时回原材料找还没表达的关联，**不是换一种外观皮肤**。
