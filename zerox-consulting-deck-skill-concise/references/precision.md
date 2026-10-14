# 精度、共享几何与关键语义

**什么时候读**：S4 实现阶段，页面有同行比较、复杂数值标注、多个证据模块，或需要跨页统一尺度时；S5 验收时用来判断哪些结论有自动证据、哪些必须实际看图。
**读完要能做什么**：用共享轨道和真实锚点建立对齐；选对专业标注入口并知道它的容量边界；说清每条实现路线的自动能力与**明确边界**；知道自动 PASS 在哪里结束、目视从哪里开始。

## 整页构思先于精度工具

页面构思与四项决定统一见[整页创作](page_design.md)；本文件只负责把这些决定落实到真实对象，不另设一套构图流程。先让主证据和关系充分展开，再按需要建立轨道与测量。

**自然高度、边界对齐或无溢出都不能证明完成**；收束辅助说明后仍要重新统筹全页。`.proof-layout` 和 `.plot-stack` 是可选接口，不应把全篇引向固定主辅模板。分隔线与锚点服务真实关系；主辅不强齐底边，独立补充不强配行。

## 共享排版与真实测量

### 同行比较：`render_comparison_rows.cjs`

```js
const {render} = require('./scripts/render_comparison_rows.cjs');
render({id, rows, columns, domain, decimals});   // → HTML 字符串
```

- `id` 需匹配 `/^[a-zA-Z][\w-]*$/`，同页唯一；`rows` 每行必须有有限数值 `value`，**未知值不能填零**。
- `columns` 的 key 可以是 `label`、`value`、`bar` 或其他数据字段：`value` 走右对齐 + tabular-nums，`bar` 生成数据条轨道，其余按原字段输出。字段缺失直接报错。
- `domain` 必须含零与全部数据（`lo ≤ 0 ≤ hi`）；不传时按含零的实际范围推导。
- 行内文字共享**首行**基线，数值共享**实际文字右缘**，数据条在独立行中心按含零尺度计算，负数同样绑定零点。
- 换行使用原文 `\n`。

**禁止逐标签 translateY 修补基线。** 需要调列宽时用 `--comparison-columns` 调整轨道，行高由内容决定。

### 几何 CSS 与锚点声明

- CSS 来自自动装配的 `assets/deck-geometry.css`，可用类：`.precision-table`、`.precision-row`（`.head` 为表头）、`.precision-cell`、`.precision-number`、`.precision-bar-track`、`.precision-bar`、`.precision-bar-zero`。`apply_theme.cjs` 会自动内联；QA 核对 `.layout-split` 等实际计算样式，缺 CSS 应在首个代表页暴露。
- 自定义 HTML／SVG 在**实际文字上**声明锚点：`data-geo-baseline="组ID"`、`data-geo-left/right/top/bottom/center-y="组ID"`。文字默认指首行，末行加 `data-geo-line="last"`。**不能把基线锚点放在 flex/grid 外框上。**数值 `right` 测的是实际文字范围。
- SVG 支持 alphabetic 实际字符基线及 transform；其他 baseline 模式明确未支持。
- `.precision-bar-track` 通过 `data-geo-row-center` 对应 `data-geo-row`，图形中心与文字基线分别核对。
- **跨图对齐要声明真实的 plot 边缘、标题等锚点，不能只声明 SVG 容器。**
- 同层标题需要共享基线时，在实际标题文字上声明同组锚点，并统一必要的字体与 line-height。主区继承 normal、侧栏继承固定行高时，容器同顶仍可能文字错位；用共同样式修正，不能逐标题偏移。

### 容差与校准

QA 等待字体和图形稳定、核对实际字体身份后，把 screen 坐标除以页面实际 scale。当前 Chromium 容差为 **0.35 逻辑 px**；已知的 4px 偏移和注入 2px 反例必须失败。**更换渲染环境先跑 `test_reliability.cjs` 校准，不得调宽容差去迁就可见错误。**

## 六类专业标注

作者决定证据与构图，工具从原值派生格式、累计量、坐标和标签候选；**不逐标签手写偏移**。既有 `ExhibitKit` 继续可用，但不把本入口的验证结论外推到旧组件。

### 入口与数据

```js
const {render, build} = require('./scripts/render_precision_exhibit.cjs');
// render({type, width, height, fontSize, theme, typography_id, unit,
//         items, comparisons, connections, format}) → svg
// build(spec) → {svg, geometry, audit}
```

条目形状：`columns` 用 `{id,label,value}`，`waterfall` 用 `{id,label,type:'total'|'subtotal'|'delta',value}`，`stacked` 用 `{id,label,segments:[{id,label,value}]}`；`comparisons:[{from,to,label?,showRelative?,kind?,format?}]`。

命令行：`node scripts/render_precision_exhibit.cjs spec.json exhibit.svg`。把 SVG 原样内联到现有 deck，引擎、母版和首尾仍走现有入口；最终 `pack_fonts.cjs` 为 SVG 和正文统一嵌入交付字体，`qa_deck.cjs` 生成最终截图与 PDF。原始 SVG 引用 `Deck Inter` / `Deck Noto Sans SC` 字体名、本身不嵌入字体，**不能把裸 SVG 的系统回退效果当作已验收风格**。

- `columns`：负值从零基线向下；无序类别默认不连接。`type:'total'|'subtotal'` 必须提供 `sumOf:['前置 id',…]`，原值须等于被引用项之和且不重复引用；总／小计使用真实 600 字重、描边和额外组间空间，**不改变数量尺度**。
- `waterfall`：首个 total 是起点；delta 逐项累计；后续 total 必须闭合，subtotal 可省略 value 由累计值生成。支持跨零、负值和小数。比较累计量时引用 total／subtotal。
- `stacked`：当前支持**非负绝对组成**；各列显式列全系列，零值填 0，**未知不当作 0**；系列顺序和颜色跨列一致。可选 `total` 必须等于系列之和。总量自动显示，微小片优先取得外置候选。此入口尚不支持负值堆积或百分比归一化。
- **容量**：`width/height` 是逻辑坐标中的真实绘制容量。改数据、字体或尺寸后重新运行 `render`，全部数据锚点和文字候选随之重算；**CSS 等比缩放只改变显示比例，不代替重新布局**。画布至少 400×260、文字至少 14px；超出容量明确报错——先增加适当空间、减少同时比较、分面或换表达。
- `title` 默认用于可访问名称；需要 SVG 内部标题时用 `showTitle:true`。单位、图例、类别换行和比较说明纳入绘图区预算；最长类别超过 4 行则拒绝拥挤输出。主题从 `deck-themes.js` 读取，真实字体从 `deck-typography.js` 读取；字体测量复用 `font_metrics.cjs` 的 fontkit + tnum。标签保守占位采用随包正文的 ascent／descent，**最终仍要检查实际浏览器字形**。

### 能力与可执行合同

| 能力 | 可执行合同 | 已验证范围 |
|---|---|---|
| 阶梯连接 | `connections:{mode:'continuous'\|'cumulative',style:'solid'\|'dashed'}`。cumulative 只用于瀑布，连接上一步累计终点与下一 delta 起点；continuous 是作者对连续关系的显式声明。堆积 continuous 须指定 `target:'total'` 或 `series:'系列 id'` | 连续柱图、含负值及小计瀑布；改数据、改尺寸；断轴跨区间路径分片 |
| 语义格式 | 原值、差额、增长率、百分点、倍数分开；变化带正负号。非零小值不会被印成 0。零／负基数增长率返回不适用原因，绝对差继续可读 | 小数、负值、微小量、零／负基数、百分点及倍数计算 |
| 合计／小计 | 真实类型与闭合校验；600 字重、描边、间距强调；堆积总量从分量相加 | columns `sumOf`、waterfall 累计、stacked total；错误合计拒绝 |
| Δ 与增长率 | `comparisons:[{from,to,label?,showRelative?,kind?,format?}]`。两柱／总量用 item id；指定堆积层用 `{item:'id',series:'id'}`。两柱／总量从真实顶端引出比较路径；指定层在顶部共用零起点的原值轨道比较，A/B 编号与主图真实外置标签对应 | 两期柱图、总量及指定小片层、含负值瀑布；层原值下降时箭头方向与 Δ 一致 |
| 外置标签与引线 | 先测量后选择柱内、柱外、左右错位候选；避开已有文字、标注线和其他柱片。引线从真实柱片侧边出发；候选穷尽则报错，不丢标签 | 0.2／0.5 微小片与 2／5 小片四个引线；数据或画布变化后重算 |
| 显式断轴 | `axisBreaks:[{from,to,gap:20}]`。可见说明列出省略区间，轴与柱片有断层标记；柱片、连续线、比较路径共用同一变换；`data-value` 保留原值 | 0–1,000／10,000 以上柱图、瀑布组合；实际 SVG 几何及导出的 PDF |

**指定堆积层比较**使用**同一零起点的小比较轨道**，图形长度和箭头方向都对应层原值；主堆积保留原位与真实累计高度。总量可以同时增加，但使用另一条明确的总量比较路径。

`data-axis-from/to` 在小轨道中表示层原值；`data-from/to-key` 保留原图归属，`data-from/to-anchor-key` 指向原值轨道端点；metadata 中 `layerTracks` 给出共同零点、比例尺和 A/B 引用。**不能把累计边界方向当作原值变化方向**——这是最容易出错的一处。层与总量混合端点比较会被明确拒绝；密集标注仍需增加空间或分面。

**断轴必须保留零点**，区间严格位于域内且不重叠。任何数据端点落入被省略区间会直接报错；跨越断层的柱由真实可见数值段生成多块，跨区间的竖线同步断开并标记。适用性仍需与完整尺度、局部放大或分面对照判断。`domain` 显式给出时不得截断数据或隐去零点。断层 gap 至少 8px，累计不得占绘图区 35% 以上。

### 共享纯函数

`assets/exhibit-geometry.js` 可在 Node `require`，也可在浏览器获得 `ExhibitGeometry`；它不依赖 DOM、不读取系统字体。导出 `finite`、`close`、`formatNumber`、`semanticFormat`、`change`、`extent`、`createScale`、`waterfall`、`rowTracks`、`intersects`、`contains`、`lineHitsRect`。

```js
semanticFormat(value, {kind:'value'|'delta'|'rate'|'pp'|'multiple', decimals, basis});
change(start, end, {decimals, rateDecimals, kind, basis});
// {delta, deltaLabel, rate, rateStatus:'ok'|'zero-base'|'negative-base', rateLabel}
createScale(domain, range, {breaks:[{from,to,gap}]});
// {domain, range, breaks, unit, map, visible, segments}
rowTracks(rows, {top, fontSize, lineHeight, gap, right});
// 每行 {top, height, center, firstBaseline, lastBaseline, baselines, right}
```

`rate` 接受比率原值（0.15 → +15%）；`pp` 必须声明 `basis:'fraction'|'percent'`；`change` 中 `kind:'pp'` 用百分点显示差额。`rowTracks` 明确区分图形中心和文字基线——HTML 应使用真正的共同排版结构，自定义 SVG 按这些轨道设置文字位置。**轨道声明本身不是浏览器测量的替代品。**

图元提供 `data-item/series/value/from/to/mark-id`，比较和引线另有真实端点键、原值差额、轴值与锚点。`auditLayout` 可检查生成阶段的数值映射、端点归属、文字／图形／标注线碰撞，无法布局即报错；metadata 和 `data-baseline` 供定位，**不单独构成通过证据**。

## 关键语义不能被总覆盖率替代

整体文字覆盖率只能发现大面积漏字，**不承担语义完整性的证明**。一句否定词、一个分母、一个适用条件丢失，可能让正确的数字表达出错误的结论，而覆盖率仍然很高。

需要核对的关键要素是：**关键数字及其单位／分母、适用期间、否定或成立条件、事实／预测／假设的身份、会改变建议的反证**。把它们放进任务合同的 `critical`，例如 `{"id":"share-boundary","text":"不是市场收入份额","target":"visibility-chart"}`；正文对应 `<span data-critical-id="share-boundary" data-critical-for="visibility-chart">不是市场收入份额</span>`，关联对象在同页有 `id="visibility-chart"`。

`id` 唯一；声明的 `text` 必须与可见正文一致（允许空白差异）；`target` 可省略，存在时必须关联真实可见对象。这些要素要建立"来源或计算 → 判断 → 页面对象 → PDF"的可核对对应，复用已有的证据与页面笔记，不为普通句子建全量台账。

QA 核对声明、屏幕与打印 DOM 完整性，以及**实际 PDF 对应位置内**的关键文字与关联对象文字。PDF 只用可提取文字对象，**不能把 Canvas 或图片里的字当作已自动验证**；文字提取不支持时明确转为实际 PDF 目视检查，不自动 pass。

此机制只覆盖显式声明，不会自动找齐所有业务限制。**作者仍须自己核对重要语义和视觉归属，不能因为整体覆盖率较高就忽略一句否定丢失。** 制作时让重要限定靠近对应的数字或箭头。

## 四层验收

| 层 | 自动定位 | 实际看图 |
|---|---|---|
| page | 模块锚点、内容范围、计算样式 | 主次、重心、留白功能、阅读顺序、母版 |
| exhibit | 同行列、数据完整性、尺度 | 对应自然、分组与线条表达正确关系 |
| annotation | 派生值、端点、候选碰撞与越界 | 小值辨认、箭头含义、引线归属、比较便利性 |
| typography | 实际字体、文字基线、数字格式 | 正常阅读与放大局部的字形、间隔、可读性 |

**一层的通过不能抵消另一层错误。** page 层先对照原始目标与用户明确要求判断（见[验收](qa.md)）；无碰撞、证据哈希齐全不等于整页成立。字体自然字形差异和合理中文换行可以接受；错误数据、明显错位、错误指认、不可读必须返工。完整报告要实际查看每页 HTML 截图及最终 PDF，关键标注与排印放大检查；**打印 DOM 不是最终 PDF**。

## 每条路线的自动能力与明确边界

| 路线 | 自动实现与验证 | 明确边界 |
|---|---|---|
| HTML 同行比较 | 首行／末行、数值右缘、条长和行中心；混排、换行、400/600 字重、负值小数、2 倍缩放 | 字形自然顶底不同不强行拉齐；小数点对齐需另提供 decimal 轨道，不以右缘冒充 |
| 静态 SVG | 实际字符基线、transform 后锚点；专业图共用数据映射及 fontkit 候选布局 | 原生 ECharts／custom SVG 须提供真实对象适配；**不因图型名称推断支持** |
| Canvas | 保留现有渲染、字体与打印检查 | 未提供可观测锚点适配器时记 `UNSUPPORTED_WITHOUT_ADAPTER`，**不声称同行／标注精度通过** |
| 最终 PDF | QA 检查嵌入字体、文字与页数；`audit_pdf_geometry.cjs` 读取实际 PDF 文字对象并按 HTML 测量锚点核对 | **只覆盖可提取文字的水平基线和右缘**；矢量归属、断层及整体构图仍要实际渲染看图 |

**估宽通过或自动几何 PASS 不代替实际看图。** 自动诊断可以提示异常剩余空间、成组对齐偏差、过度伸展背景或重复弱布局，但它只是定位线索：**不得以统一填充率、一律对称或数学质心作为审美 PASS 的门槛**。对作者已明确声明的共同基线与轨道可以做精确检查；未声明或未适配的关系要如实标出，不能默认通过。

### PDF 与跨媒介的容差

PDF 的文字关系与跨媒介位置**分别报告**：同组基线／右缘 spread 仍须 ≤0.35 逻辑 px，文字须完整对应。

Chrome 打印可能把整行基线取到最近的 CSS 像素，小数行高实测夹具已验证该签名。**仅在整组对齐、每段都符合最近整数（数值残差 ≤0.02px）、共同量化 ≤0.5px** 时才标 `CALIBRATED_BASELINE_ROUNDING`，并保留原始偏移；**右缘不套用该模型**。任意整组平移、单元素 2/4px 偏移、缺字与 18px 片段移位仍然失败。其他打印路径若不符合已验证模型，需要单独适配，**不能通过放宽组内容差解决**。

最终 PDF 审计在页面没有可测水平文字锚点时为 `NOT_DECLARED`，汇总为 `PARTIAL`，**不可称为完整精度通过**。

### 修改后重跑什么

改数据、字体、尺寸或画布后重新运行 `render` 并重看受影响成稿。`node scripts/test_precision_exhibit.cjs` 校验数值、闭合、格式与改数／换尺寸／长中文／混排／负值／小数等目标反例；`node scripts/test_precision_browser.cjs [样例目录]` **自带夹具**——目录里没有 gallery 时用 `scripts/build_precision_gallery.cjs` 从同一批 samples 现场生成（含字体子集内嵌），不需要任何历史目录；随后独立读取实际 SVG，按原 spec 重新累计并核对真实矩形、端点、引线端点和实际文字 bbox。故意移动柱、比较路径或引线 4px、制造文字碰撞、把层比较接回错误的累计边界、反转层 Δ 箭头，都必须失败。常规制稿只测受影响成稿与新计算，**不为复用这些入口重跑全库**。
