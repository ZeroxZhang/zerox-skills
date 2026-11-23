# 设计风格详细规范

本文件定义了 Onepager 支持的十二种设计风格的完整视觉规范。
生成 HTML 时必须严格遵循所选风格的全部参数。

---

## 设计哲学总纲

所有风格必须共同遵守以下设计原则，这些原则是区分"专业设计"与"AI堆砌"的底线：

### 1. 克制即力量 (Restraint is Power)
- 每个视觉元素必须有明确的信息传达目的
- 坚决摒弃：无意义的发光效果、多层半透明堆叠、无目的的渐变
- 装饰性元素的视觉重量不得超过内容元素的 20%

### 2. 层级即叙事 (Hierarchy is Story)
- 通过字号对比（至少 3:1）、字重对比、留白对比建立不可动摇的层级
- 读者在 3 秒内必须能理解信息的组织结构
- 参考：经济学人排版、Stripe 文档设计

### 3. 网格即信仰 (Grid is Gospel)
- 所有布局基于 8pt 网格系统
- 元素对齐必须像素级精确，拒绝"差不多"

### 4. 反 AI 味红线
以下元素被明确禁止（特定风格例外需注明）：
- 蓝紫渐变（如 `linear-gradient(135deg, #6366f1, #a855f7)`）
- 无意义的发光阴影（`box-shadow: 0 0 30px rgba(...)`）
- 多层半透明毛玻璃堆叠（超过一层 backdrop-filter）
- 无目的的圆角（所有圆角必须有风格一致性理由）
- Emoji 作为图标（必须使用 SVG）

---

## 色彩预算法则（跨风格通用）

所有风格都遵循 **60-30-10 法则**：
- **60% 主色**：中性背景色，奠定整体基调
- **30% 辅助色**：品牌/主题色，用于标题、卡片、区块
- **10% 强调色**：高饱和度色，仅用于 CTA、关键数据、重点标注

全页色彩不超过 **3 个主色 + 2 个中性色**。B5 新波普编辑、B8 赛博街道、B9 谷歌原生、B10 短视频潮流、B11 粗野平面可适当放宽色彩数量，但需保持大致的 60-30-10 比例原则；B9 品牌四色满铺色块不计入主色限制；B10 的红青是"主音 + 对位音"关系，合计占比不得超过 16%；B11 的红与荧光绿是"信号"，单色 ≤3%、合计 ≤5%。

---

## B1: 暗夜编辑 (Dark Editorial)

> 设计哲学：像顶级科技出版物（Stripe Docs、Linear Blog）的暗色模式。深沉但不阴郁，信息密度高但层次分明。绝对拒绝"霓虹夜店"风格的科技风。

### 配色体系
- 主背景：`#0a0a0f` 极深灰（去除任何蓝调）
- 次级背景：`#111118` 深灰（卡片/区块，完全不透明，拒绝毛玻璃）
- 三级背景：`#1a1a24` 用于hover或嵌套层级
- 主强调色：`#f59e0b` 琥珀色（唯一强调色，温暖而醒目）
- 正文色：`#e2e8f0` 浅灰白
- 次要文字：`#64748b` 中灰
- 边框色：`#1e293b` 极深灰蓝（仅用于微妙分隔，不抢视觉）
- 成功/正向：`#14b8a6` 青绿（仅用于趋势指示）
- 危险/负向：`#f87171` 柔和红（仅用于趋势指示）

### 点缀元素
- **水平分隔线**：1px `#1e293b` 细线，用于模块分隔，拒绝发光效果
- **代码/数据高亮**：等宽字体 + 琥珀色背景块（`background: rgba(245,158,11,0.1)`）
- **角标/标签**：琥珀色细边框 + 透明背景，圆角 4px，极度克制
- **无网格背景、无发光 blob、无径向渐变装饰**

### 卡片样式
```css
.card {
  background: #111118;
  border: 1px solid #1e293b;
  border-radius: 8px;
  padding: 24px;
  /* 零阴影 — 依靠层级差异创造深度 */
}
.card:hover {
  border-color: #334155;
}
```

### 标题样式
- 主标题：`#f8fafc`，字重 700-800，不使用渐变，可使用琥珀色底部短下划线（4px 高，宽度短于文字）
- 模块标题：`#e2e8f0`，字重 600
- 数据标签：等宽字体 JetBrains Mono，字重 500，字母间距 0.05em

### 色彩预算映射
- 60% 主色：`#0a0a0f` 背景 + `#111118` 卡片
- 30% 辅助色：`#e2e8f0` 正文 + `#64748b` 次要文字
- 10% 强调色：`#f59e0b` 琥珀色（仅用于关键数据、CTA、标签边框）

### 图标风格
- **线性图标**，线宽 1.5px，24×24 viewBox，颜色跟随文字色

### BigNumber 样式
```css
.bignum-value {
  font-family: 'JetBrains Mono', 'Noto Sans SC', monospace;
  font-size: 120px; /* A2尺寸，A1=72px, A3=96px */
  font-weight: 700;
  color: #f59e0b;
  letter-spacing: -0.02em;
  line-height: 1;
}
.bignum-value::after {
  content: '';
  display: block;
  width: 48px;
  height: 4px;
  background: #f59e0b;
  margin-top: 16px;
}
.bignum-label {
  font-family: 'Noto Sans SC', sans-serif;
  font-size: 18px;
  color: #64748b;
  margin-top: 12px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}
.bignum-unit {
  font-size: 48px;
  color: #64748b;
  vertical-align: super;
}
```

---

## B2: 瑞士精密 (Swiss Precision)

> 设计哲学：瑞士国际主义平面设计（Swiss Style / International Typographic Style）。严格的非对称网格、Helvetica 美学、信息即设计。Josef Müller-Brockmann 的精神继承者。

### 配色体系
- 主背景：`#ffffff` 纯白
- 辅助背景：`#fafafa` 极浅灰（仅用于区分区块，不用于卡片）
- 主强调色：`#dc2626` 正红（瑞士设计标志性色彩）
- 辅助强调：`#000000` 纯黑
- 正文色：`#18181b` 纯黑
- 次要文字：`#71717a` 中灰
- 边框色：`#000000` 纯黑

### 点缀元素
- **粗黑水平线**：4-8px 纯黑水平线作为视觉锚点和模块分隔
- **几何色块**：纯红色或纯黑色矩形色块（非渐变）作为背景强调
- **非对称布局**：标题靠左，正文靠右，打破居中对称的平庸感
- **无阴影、无发光、无渐变、无圆角装饰**

### 卡片样式
```css
.card {
  background: #ffffff;
  border: 1px solid #000000;
  border-radius: 0; /* 瑞士风格：零圆角 */
  padding: 32px;
  box-shadow: none;
}
.card-emphasis {
  background: #dc2626;
  color: #ffffff;
  border: none;
}
```

### 标题样式
- 主标题：`#000000`，字重 900（极粗），可能是正文的 4 倍大小，左对齐绝不居中
- 模块标题：`#000000`，字重 700，配合左侧红色短竖线（4px 宽）或红色下划线
- 拒绝任何渐变文字、发光文字、阴影文字

### 色彩预算映射
- 60% 主色：白色背景 `#ffffff`
- 30% 辅助色：纯黑文字 `#18181b` + 灰色 `#71717a`
- 10% 强调色：正红 `#dc2626`（仅用于极小面积的强调、标签、几何色块）

### 图标风格
- **线性图标**，线宽 2px，风格极度简洁，24×24 viewBox

### BigNumber 样式
```css
.bignum-value {
  font-family: 'Noto Sans SC', 'Inter', 'Helvetica Neue', sans-serif;
  font-size: 160px; /* A2尺寸 */
  font-weight: 900;
  color: #dc2626;
  line-height: 0.9;
  letter-spacing: -0.03em;
}
.bignum-label {
  font-size: 20px;
  color: #000000;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  border-top: 4px solid #000000;
  padding-top: 12px;
  margin-top: 16px;
}
```

---

## B3: 有机自然 (Organic Nature)

> 设计哲学：侘寂美学 (Wabi-Sabi)。自然材质、不完美中的完美、时间的痕迹。参考 MUJI、原研哉的设计语言，以及日本民艺运动。

### 配色体系
- 主背景：`#faf8f5` 米白/纸色
- 辅助背景：`#f5f0e8` 浅米色（卡片/区块）
- 三级背景：`#ede8e0` 暖灰（hover或嵌套）
- 主强调色：`#c2410c` 陶土色
- 辅助强调：`#4d7c0f` 苔藓绿
- 正文色：`#3f3f46` 暖灰
- 次要文字：`#a1a1aa` 浅灰
- 边框色：`#e7e5e4` 暖灰白（极细或无边框）

### 点缀元素
- **纸质纹理**：可叠加极淡的 SVG 噪点纹理（opacity 0.02-0.03）
- **手绘感 SVG 线条**：有机曲线、不规则圆形作为装饰
- **自然元素**：叶子轮廓、石头轮廓、水波纹（仅作为极淡的背景装饰）
- **大圆角**：20-24px，模拟自然形态（石头、水滴）
- **无阴影、无发光**

### 卡片样式
```css
.card {
  background: #f5f0e8;
  border: none; /* 依靠颜色差异区分层级 */
  border-radius: 20px;
  padding: 28px;
  box-shadow: none;
}
```

### 标题样式
- 主标题：Noto Serif SC，字重 700，`#292524` 深暖灰，带有手写感的自然气息
- 模块标题：Noto Sans SC，字重 600，陶土色 `#c2410c`
- 整体温暖、舒适、有人文气息

### 色彩预算映射
- 60% 主色：米白 `#faf8f5` + 浅米色 `#f5f0e8`
- 30% 辅助色：暖灰文字 `#3f3f46` + 苔藓绿 `#4d7c0f` 区块
- 10% 强调色：陶土 `#c2410c`（仅用于关键数据、按钮、手绘装饰线）

### 图标风格
- **面性图标**，圆角 12px，颜色柔和（陶土/苔藓绿/米色），24×24 viewBox

### BigNumber 样式
```css
.bignum-value {
  font-family: 'Noto Serif SC', 'Songti SC', serif;
  font-size: 120px;
  font-weight: 700;
  color: #c2410c;
  line-height: 1;
}
.bignum-value::after {
  content: '';
  display: block;
  width: 80px;
  height: 3px;
  background: #c2410c;
  margin-top: 16px;
  border-radius: 2px; /* 手绘感的圆角 */
}
.bignum-label {
  font-family: 'Noto Sans SC', sans-serif;
  font-size: 18px;
  color: #4d7c0f;
  margin-top: 12px;
  font-weight: 500;
}
```

---

## B4: 建筑粗野 (Constructivist Brutalism)

> 设计哲学：粗野主义建筑与网页设计。原始、直接、不加修饰、力量感。参考 brutalistwebsites.com 和苏联构成主义海报。

### 配色体系
- 主背景：`#d4d4d4` 混凝土灰
- 辅助背景：`#e5e5e5` 浅灰（卡片）
- 反色背景：`#000000` 纯黑（用于反色块）
- 主强调色：`#ea580c` 安全橙
- 辅助强调：`#facc15` 电黄
- 正文色：`#171717` 纯黑
- 反色文字：`#ffffff` 纯白
- 次要文字：`#525252` 中灰

### 点缀元素
- **粗黑边框**：3-4px 纯黑边框，无圆角
- **硬阴影**：无模糊的纯色偏移阴影 `box-shadow: 8px 8px 0px #000000`（仅此风格允许硬阴影）
- **反色块**：黑色背景 + 白色/黄色文字的强烈对比区域
- **错位布局**：元素故意偏离网格 8-16px，制造张力
- **无渐变、无发光、无圆角**

### 卡片样式
```css
.card {
  background: #e5e5e5;
  border: 3px solid #000000;
  border-radius: 0;
  padding: 24px;
  box-shadow: 8px 8px 0px #000000;
}
.card-inverse {
  background: #000000;
  color: #ffffff;
  border: 3px solid #000000;
  box-shadow: 8px 8px 0px #ea580c;
}
```

### 标题样式
- 主标题：系统字体栈，字重 900，极大字号，纯黑或纯白（在反色块上）
- 模块标题：系统字体，字重 700，安全橙色背景块 + 黑色文字
- 拒绝任何细腻装饰，力量感优先

### 色彩预算映射
- 60% 主色：混凝土灰 `#d4d4d4` + 浅灰 `#e5e5e5`
- 30% 辅助色：纯黑 `#000000` 边框/文字/反色块 + 中灰 `#525252`
- 10% 强调色：安全橙 `#ea580c` + 电黄 `#facc15`（用于边框阴影、反色块、关键数据）

### 图标风格
- **面性图标**，粗黑边框风格，与卡片一致，24×24 viewBox

### BigNumber 样式
```css
.bignum-value {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 140px;
  font-weight: 900;
  color: #000000;
  line-height: 0.85;
  background: #facc15;
  padding: 16px 24px;
  display: inline-block;
  border: 3px solid #000000;
  box-shadow: 8px 8px 0px #000000;
}
.bignum-label {
  font-size: 24px;
  font-weight: 700;
  color: #000000;
  margin-top: 16px;
  text-transform: uppercase;
}
```

---

## B5: 新波普编辑 (Neo-Pop Editorial)

> 设计哲学：现代杂志排版（如 Wired、It's Nice That）。大胆色块与留白的精密平衡，编辑感而非插画感。孟菲斯的纪律化版本。

### 配色体系
- 主背景：`#fefce8` 奶油白
- 卡片背景-粉：`#fce7f3` 浅粉
- 卡片背景-黄：`#fef9c3` 浅黄
- 卡片背景-蓝：`#dbeafe` 浅蓝（纯蓝，非蓝紫）
- 主强调色：`#e11d48` 亮粉
- 辅助强调：`#2563eb` 宝蓝（纯蓝）、`#fbbf24` 明黄
- 正文色：`#1e1b4b` 深靛黑
- 次要文字：`#64748b` 中灰

### 点缀元素
- **纯色色块卡片**：粉色/黄色/蓝色的纯色背景卡片，2px 黑边框
- **粗体引用**：极大字号的粗体引用文字，作为视觉焦点
- **分栏排版**：杂志式多栏布局，文字环绕
- **无渐变、无阴影、无发光**

### 卡片样式
```css
.card {
  background: #fce7f3; /* 或 #fef9c3 / #dbeafe */
  border: 2px solid #000000;
  border-radius: 0; /* 杂志感：零圆角 */
  padding: 28px;
  box-shadow: none;
}
```

### 标题样式
- 主标题：极大字号（可能是正文的 3-4 倍），Extra Bold，深靛黑，左对齐
- 模块标题：亮粉色或宝蓝色背景块上的黑色/白色文字
- 强烈的字号对比，杂志封面感

### 色彩预算映射
- 60% 主色：奶油白 `#fefce8`
- 30% 辅助色：彩色卡片（粉/黄/蓝）+ 深靛黑文字
- 10% 强调色：亮粉 `#e11d48`（用于最大字号数字、关键 CTA）

### 图标风格
- **面性图标**，高饱和度填充，与卡片色彩呼应，24×24 viewBox

### BigNumber 样式
```css
.bignum-value {
  font-family: 'Noto Sans SC', 'Inter', sans-serif;
  font-size: 160px;
  font-weight: 900;
  color: #000000;
  line-height: 0.9;
  background: #fbbf24;
  padding: 20px 32px;
  display: inline-block;
  border: 2px solid #000000;
}
.bignum-label {
  font-size: 22px;
  font-weight: 700;
  color: #e11d48;
  margin-top: 12px;
}
```

---

## B6: 极简东方 (Minimalist East)

> 设计哲学：东方极简主义（参考原研哉、MUJI、安藤忠雄）。一即一切，留白即内容。信息密度极低，但每个元素都有极强的存在感。

### 配色体系
- 主背景：`#f5f5f4` 极浅灰白
- 辅助背景：`#e7e5e4` 浅暖灰（卡片，与背景差异极小）
- 主强调色：`#1c1917` 墨黑
- 点缀色：`#b91c1c` 朱红（仅用于极少量的点睛，如句号、短横线）
- 正文色：`#44403c` 暖黑
- 次要文字：`#a8a29e` 浅灰

### 点缀元素
- **几乎无装饰**：依靠留白和字号对比创造呼吸感
- **朱红点睛**：一条 2px 朱红细线，或一个朱红色的句号，作为唯一的色彩点缀
- **极大的留白**：模块间距可达 64-96px
- **无阴影、无边框或 0.5px 极细边框、无圆角或极小圆角**

### 卡片样式
```css
.card {
  background: #e7e5e4;
  border: none; /* 或 0.5px solid #d6d3d1 */
  border-radius: 4px; /* 极小圆角，暗示手工艺的微妙处理 */
  padding: 40px; /* 极大的内边距 */
  box-shadow: none;
}
```

### 标题样式
- 主标题：Noto Serif SC，字重 400（极轻，以体量取胜而非重量），墨黑 `#1c1917`，极大字号
- 模块标题：Noto Sans SC，字重 300，暖黑 `#44403c`
- 行高极大：2.0-2.2，给文字充分的呼吸空间

### 色彩预算映射
- 60% 主色：极浅灰白 `#f5f5f4` + 浅暖灰 `#e7e5e4`
- 30% 辅助色：暖黑 `#44403c` 文字 + 墨黑 `#1c1917` 标题
- 10% 强调色：朱红 `#b91c1c`（仅用于极细线条、极少量的句号或标点）

### 图标风格
- **极简线条图标**，线宽 1px，颜色与次要文字一致，24×24 viewBox

### BigNumber 样式
```css
.bignum-value {
  font-family: 'Noto Serif SC', 'Songti SC', serif;
  font-size: 140px;
  font-weight: 400;
  color: #1c1917;
  line-height: 1;
  letter-spacing: 0.05em;
}
.bignum-value::after {
  content: '';
  display: block;
  width: 60px;
  height: 2px;
  background: #b91c1c;
  margin-top: 24px;
}
.bignum-label {
  font-family: 'Noto Sans SC', sans-serif;
  font-size: 16px;
  color: #a8a29e;
  margin-top: 16px;
  font-weight: 300;
  letter-spacing: 0.1em;
}
```

---

## B7: 数据新闻 (Data Journalism)

> 设计哲学：经济学人 / 纽约时报数据可视化风格。数据即主角，排版服务于数据。理性、精确、可信。

### 配色体系
- 主背景：`#f8f7f4` 报纸白
- 辅助背景：`#ffffff` 纯白（卡片）
- 图表网格：`#e5e5e5` 浅灰
- 主强调色：`#1e3a5f` 深海军蓝
- 辅助强调：`#9f1239` 锈红（用于负向/对比数据）
- 正文色：`#292524` 深暖灰
- 次要文字：`#78716c` 中灰
- 边框色：`#d6d3d1` 暖灰

### 点缀元素
- **精细网格线**：1px 浅灰网格线（仅用于图表区域）
- **数据标注**：等宽字体的小字号数据标签，精确对齐
- **来源注释**：极小字号的斜体来源说明（"Source: ..."）
- **分隔线**：细水平线分隔模块，1px `#d6d3d1`

### 卡片样式
```css
.card {
  background: #ffffff;
  border: 1px solid #d6d3d1;
  border-radius: 4px;
  padding: 24px;
  box-shadow: none;
}
```

### 标题样式
- 主标题：Noto Serif SC，字重 700，深海军蓝 `#1e3a5f`，庄重可信
- 模块标题：Noto Sans SC，字重 600，深暖灰
- 图表标题：等宽字体，字重 500，小字号，全大写，字母间距加宽

### 色彩预算映射
- 60% 主色：报纸白 `#f8f7f4` + 纯白卡片
- 30% 辅助色：深暖灰 `#292524` 文字 + 中灰 `#78716c` 标注
- 10% 强调色：深海军蓝 `#1e3a5f`（主数据色）+ 锈红 `#9f1239`（对比数据色）

### 图标风格
- **极简线性图标**，线宽 1.5px，颜色 `#78716c`，24×24 viewBox

### BigNumber 样式
```css
.bignum-value {
  font-family: 'JetBrains Mono', 'Noto Sans SC', monospace;
  font-size: 120px;
  font-weight: 700;
  color: #1e3a5f;
  line-height: 1;
  letter-spacing: -0.02em;
}
.bignum-value .decimal {
  font-size: 60px;
  color: #78716c;
}
.bignum-unit {
  font-size: 36px;
  color: #78716c;
  font-weight: 400;
}
.bignum-label {
  font-family: 'Noto Sans SC', sans-serif;
  font-size: 16px;
  color: #78716c;
  margin-top: 8px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  border-top: 1px solid #d6d3d1;
  padding-top: 8px;
}
```

---

## B8: 赛博街道 (Cyber Street)

> 设计哲学：赛博朋克但不媚俗。深夜城市的霓虹反光， gritty but elegant。拒绝廉价的"霓虹夜店"效果，追求 Blade Runner 式的优雅粗粝。

### 配色体系
- 主背景：`#050505` 深黑
- 辅助背景：`#111111` 深灰（卡片）
- 主强调色：`#ff006e` 霓虹粉
- 辅助强调：`#00f5d4` 电青（粉+青的经典赛博组合，绝非蓝紫）
- 正文色：`#f0f0f0` 冷白
- 次要文字：`#737373` 中灰
- 边框色：`#262626` 深灰

### 点缀元素
- **扫描线效果**：CSS `repeating-linear-gradient` 模拟 CRT 扫描线（opacity 0.03，极度克制）
- **霓虹边框**：1px 霓虹色边框（`border: 1px solid #ff006e`），仅此风格允许
- **故障艺术 (Glitch)**：仅限主标题，使用 CSS clip-path 和 text-shadow 的极简故障效果
- **无模糊发光、无多层半透明**

### 卡片样式
```css
.card {
  background: #111111;
  border: 1px solid #262626;
  border-radius: 0; /* 赛博风格：锐角 */
  padding: 24px;
}
.card-highlight {
  border-color: #ff006e;
}
.card-cyan {
  border-color: #00f5d4;
}
```

### 标题样式
- 主标题：无衬线体，字重 800，冷白，可使用极简故障效果
- 模块标题：霓虹粉色或电青色，字重 600
- 数据：等宽字体，霓虹色

### 色彩预算映射
- 60% 主色：深黑 `#050505` + 深灰 `#111111`
- 30% 辅助色：冷白 `#f0f0f0` 文字 + 中灰 `#737373`
- 10% 强调色：霓虹粉 `#ff006e` + 电青 `#00f5d4`（严格交替使用，不混合）

### 图标风格
- **线性图标**，线宽 1.5px，霓虹色描边，24×24 viewBox

### BigNumber 样式
```css
.bignum-value {
  font-family: 'JetBrains Mono', 'Noto Sans SC', monospace;
  font-size: 140px;
  font-weight: 700;
  color: #ff006e;
  line-height: 1;
  letter-spacing: -0.02em;
  text-shadow: 2px 2px 0px #00f5d4; /* 极简的错位阴影，非发光 */
}
.bignum-label {
  font-family: 'Noto Sans SC', sans-serif;
  font-size: 18px;
  color: #737373;
  margin-top: 12px;
  text-transform: uppercase;
  letter-spacing: 0.15em;
}
```

---

## B9: 谷歌原生 (Google Native)

> 设计哲学：复刻 Google 官方网站设计语言——"系统化克制 + 局部胆大"。底盘永远是白底、深灰字、单一蓝色 CTA、宽留白。个性通过品牌四色大色块释放。绝不靠阴影、渐变、纹理制造"视觉冲击"——冲击来自内容本身。参考 cloud.google.com、io.google、workspace.google.com。

### 双配色方案

B9 支持两套配色：**Light 经典四色**（默认）与 **Dark I/O 深色**。在 Phase 2 交互配置时，若用户选择 B9，追问选择 Light 或 Dark。

#### Light 经典四色（默认）

- 主背景：`#ffffff` 纯白
- 辅助背景：`#f8f9fa` 极浅灰（区块交替背景，几乎所有 Google 长页面都靠它做节奏）
- 深色背景：`#202124` 深炭（用于 Footer、深色 CTA banner）
- 主强调色：`#1a73e8` Google 蓝（唯一 CTA 色、链接色）
- 主强调色 Hover：`#1967d2`
- 正文色：`#202124` 深炭灰（不要纯黑 #000）
- 次要文字：`#5f6368` 中灰
- 辅助文字：`#80868b` 浅灰
- 边框色：`#dadce0` 极浅灰
- 品牌四色（仅用于区块满铺色块、装饰性元素，**绝不用于按钮/正文/图标**）：
  - 品牌蓝：`#4285f4`
  - 品牌红：`#ea4335`
  - 品牌黄：`#fbbc04`
  - 品牌绿：`#34a853`

#### Dark I/O 深色

- 主背景：`#0a0e1a` 深墨蓝
- 辅助背景：`#111827` 深灰蓝（卡片/区块）
- 深色背景：`#0d1117` 深黑（Hero 渐变底）
- 主强调色 1：`#8ab4f8` 浅蓝
- 主强调色 2：`#c58af9` 淡紫（仅此风格允许紫色，因为是 Google I/O 官方配色）
- 主强调色 3：`#81c995` 浅绿
- 正文色：`#f1f3f4` 冷白
- 次要文字：`#9aa0a6` 冷灰
- 边框色：`#3c4043` 深灰

### 点缀元素

- **品牌四色满铺色块**：整个区块使用四色之一作为背景（`background: #4285f4` 等），文字翻白。区块按红→黄→绿→蓝循环。**这是 B9 最核心的视觉手段**
- **粗分隔线**：4-8px 纯色水平线，颜色取自品牌四色
- **细边框节奏**：1.5-2px 实线（`border-bottom: 1.5px solid #202124` 或品牌色）贯穿 section 分隔。在 T4 海报模式下，边框节奏可作为满铺色块的替代手段——用白底+粗边框+巨字+留白同样达成海报级冲击力，且更接近 Google 编辑风的克制感
- **装饰性圆点**：8-14px 实心圆（`border-radius: 50%`），使用强调色或品牌四色。用途：(a) 品牌 Logo 旁的视觉标点，(b) 走马灯文字间的分隔符，(c) section marker
- **区块交替节奏**：白底 → 品牌色块 → 灰底 `#f8f9fa` → 品牌色块 → 深炭底。**绝不**所有区块同色
- **无渐变、无发光、无毛玻璃**

### 卡片样式

**Light 模式边框卡**（ToB 默认）：
```css
.card {
  background: #ffffff;
  border: 1px solid #dadce0;
  border-radius: 8px;
  padding: 24px 24px 32px;
  box-shadow: none;
  transition: box-shadow 0.2s ease;
}
.card:hover {
  box-shadow: 0 4px 8px rgba(60,64,67,.1), 0 8px 16px 4px rgba(60,64,67,.08);
}
```

**Dark 模式边框卡**：
```css
.card {
  background: #111827;
  border: 1px solid #3c4043;
  border-radius: 8px;
  padding: 24px;
  box-shadow: none;
}
```

**满铺色块"卡"**（品牌四色区块内的内容单元）：
```css
.color-block-blue  { background: #4285f4; color: #ffffff; }
.color-block-red   { background: #ea4335; color: #ffffff; }
.color-block-yellow { background: #fbbc04; color: #202124; }
.color-block-green { background: #34a853; color: #ffffff; }
```

### 标题样式

**Light 模式**：
- 主标题：Inter / Noto Sans SC，字重 500（Medium），`#202124`，左对齐。字号为正文的 3-4 倍
- 模块标题：字重 500，`#202124`，无装饰线
- 数据标签：JetBrains Mono，字重 500，小字号，全大写，字母间距 0.05em

**Dark 模式**：
- 主标题：字重 600，`#f1f3f4` 冷白
- 模块标题：浅蓝 `#8ab4f8` 或淡紫 `#c58af9`（三色循环）

> ⚠️ Google 风格极少使用 700+ 字重。500（Medium）撑起 99% 的层级，这是"高级又克制"的核心。中文因笔画密度问题可使用 700-900 做标题。

### 色彩预算映射

**Light 模式**：
- 60% 主色：白色背景 `#ffffff` + 灰底 `#f8f9fa`
- 30% 辅助色：深炭灰 `#202124` 文字 + 品牌四色满铺色块
- 10% 强调色：Google 蓝 `#1a73e8`（仅用于 CTA、链接）

**Dark 模式**：
- 60% 主色：深墨蓝 `#0a0e1a` + 深灰蓝 `#111827`
- 30% 辅助色：冷白 `#f1f3f4` 文字 + 浅蓝/淡紫/浅绿标题
- 10% 强调色：浅蓝 `#8ab4f8`（CTA）+ 淡紫 `#c58af9`（点缀）

> **B9 颜色预算例外**：品牌四色满铺色块不计入主色限制。满铺色块是 B9 的核心视觉手段，而非"多余装饰"。

### 图标风格

- **线性图标**，线宽 1.5px，24×24 viewBox
- Light 模式：颜色跟随 `#5f6368`
- Dark 模式：颜色跟随 `#9aa0a6`

### BigNumber 样式

**Light 模式**：
```css
.bignum-value {
  font-family: 'JetBrains Mono', 'Noto Sans SC', monospace;
  font-size: 140px; /* A2尺寸，A1=72-96px, A3=96-120px, A4=96-140px */
  font-weight: 700;
  color: #1a73e8;
  line-height: 1;
  letter-spacing: -0.02em;
}
.bignum-label {
  font-family: 'Inter', 'Noto Sans SC', sans-serif;
  font-size: 16px;
  color: #5f6368;
  margin-top: 12px;
  font-weight: 500;
  letter-spacing: 0.05em;
}
```

**Dark 模式**：
```css
.bignum-value {
  font-family: 'JetBrains Mono', 'Noto Sans SC', monospace;
  font-size: 140px;
  font-weight: 700;
  color: #8ab4f8;
  line-height: 1;
  letter-spacing: -0.02em;
}
.bignum-label {
  font-family: 'Inter', 'Noto Sans SC', sans-serif;
  font-size: 16px;
  color: #9aa0a6;
  margin-top: 12px;
  font-weight: 500;
  letter-spacing: 0.05em;
}
```

### 署名样式

**Light**：
```css
.signature {
  color: #80868b;
  font-size: 12px;
  letter-spacing: 0.02em;
}
```

**Dark**：
```css
.signature {
  color: #9aa0a6;
  font-size: 12px;
  letter-spacing: 0.02em;
}
```

---

## B10: 短视频潮流 (Short-Video Feed)

> 设计哲学：把短视频 Feed 的沉浸感搬到静态画布。黑是舞台不是装饰，红青是唯一两个高音，其余全部交给灰度层级。信息像"悬浮在视频之上"：正文压在深底、元信息用等宽小字、动作栏竖排在边缘。这一风格的力量来自**对比与纪律**，不是霓虹与特效——所以它禁止渐变（唯一例外是底部可读性渐隐）、禁止发光、禁止扫描线与故障效果（那是 B8 的领域）。参考 TikTok / 抖音的品牌系统与移动端 Feed 界面。

### 双配色方案

B10 支持两套配色：**Dark 沉浸黑**（默认）与 **Paper 编辑白**。用户在 Phase 2 选择 B10 时追问选 Dark 还是 Paper；选择 `T4` 宣传海报时自动使用 **Dark**，不再追问。

#### Dark 沉浸黑（默认）

- 页面底：`#0B0B10` 深空黑（**不是纯黑**——纯黑会让画面失去分层能力，也无法做渐隐过渡）
- 视频沉浸区：`#16161C`（大色块"银幕"的底色）
- 卡片底：`#161823`（TikTok 官方黑）
- 卡片悬起：`#1C1E2A`
- 分隔线：`#262838`
- 强调边框：`#3A3D52`
- 正文色：`#F5F5F7` 冷白
- 次要文字：`#AEB2C0`
- 三级文字：`#84868F`
- 强调红：`#FE2C55`（深压 `#E61E45`）
- 对位青：`#25F4EE`（深压 `#14D6D0`）
- 强调底上的字：`#161823`（红底或青底上永远用这个深色，不要用白字压在青上）
- 成功：`#10B981`　错误：`#E5484D`

**同色系深浅（需要层级变化时用这些，不要另造颜色）**：

| 色系 | 100 | 300 | 500 | 700 | 900 |
|:--|:--|:--|:--|:--|:--|
| 红 | `#FFE9EE` | `#FFA0B5` | `#FE2C55` | `#C01338` | `#6B061D` |
| 青 | `#E3FEFD` | `#7CF8F4` | `#25F4EE` | `#0C8F8B` | `#054745` |
| 灰 | `#EBEBED` | `#ABACB4` | `#5D5F6B` | `#313340` | `#1B1D29` |

#### Paper 编辑白

- 页面底：`#FAFAFA`
- 卡片底：`#F2F2F4`
- 分隔线：`#E8E8EC`；强调边框 `#161823`
- 墨色（正文与标题）：`#161823`
- 次要文字：`#5D5F6B`；三级文字：`#87878F`
- 强调红 / 青：仍然只用 `#FE2C55` / `#25F4EE`，**但只做 1px 细线、角标、下划线与小色块**

> ⚠️ **Paper 模式下的红青不能承载文字**。`#FE2C55` 在白底上的对比度约 3.5:1，低于正文所需的 4.5:1。Paper 模式的 BigNumber 用墨黑 `#161823`，红青只出现在装饰线、编号点与强调下划线上。

### 点缀元素

B10 的标志性手法共 6 个，**每页最多选用 2 个**——它们是"签名"，不是"素材库"：

1. **双色错位（Chromatic Offset）**：把一个元素拆成三层，青色层 `translate(-3px, -2px)`、红色层 `translate(3px, 2px)`、主体（白或墨）在最上层。全页**只允许出现 1 处**，且只能用于主标题中的一个词、品牌名或一个 BigNumber。这是 B10 最强的识别符号，用两次就变成噪音。
   ```css
   .chromatic { position: relative; display: inline-block; }
   .chromatic::before,
   .chromatic::after { content: attr(data-text); position: absolute; left: 0; top: 0; }
   .chromatic::before { color: #25F4EE; transform: translate(-3px, -2px); z-index: -1; }
   .chromatic::after  { color: #FE2C55; transform: translate(3px, 2px);  z-index: -2; }
   ```
2. **底部渐隐（Bottom Scrim）**：`linear-gradient(to top, rgba(11,11,16,.92), rgba(11,11,16,0))` 覆盖画布底部 25-30%，把页脚信息从"银幕"上安全地压出来。**这是全风格唯一允许的渐变**，因为它有明确的可读性目的。
3. **右栏动作堆叠（Action Rail）**：贴右边缘竖排的 icon + mono 计数（`128` / `2.4万`），像 Feed 的点赞栏。用于承载"关键指标"或"目录"，不要用来放导航。
4. **Mono 元信息条**：11px、`letter-spacing: .14em`、`text-transform: uppercase`、颜色用 `#84868F`。所有标签、眉题、署名、时间地点都走这一套。
5. **硬边框节奏**：`1.5px solid #3A3D52` 贯穿 section 分隔。在深底上这是最便宜也最有效的"结构可见性"。
6. **胶囊 CTA**：`border-radius: 999px`，红底白字（或红底 `#161823` 字），**全页唯一一个 pill**。其余所有元素圆角 ≤ 12px。

### 卡片样式

**Dark 主卡**：
```css
.card {
  background: #161823;
  border: 1px solid #262838;
  border-radius: 8px;
  padding: 24px;
  box-shadow: none;          /* B10 不用阴影，靠边框与底色分层 */
}
.card--elevated { background: #1C1E2A; }
```

**沉浸区（"银幕"）**：
```css
.immersive {
  position: relative;
  background: #16161C;
  border-radius: 12px;
  overflow: hidden;
}
.immersive::after {           /* 底部渐隐，压在内容之上 */
  content: "";
  position: absolute; inset: auto 0 0 0; height: 30%;
  background: linear-gradient(to top, rgba(11,11,16,.92), rgba(11,11,16,0));
  pointer-events: none;
}
```

**Paper 主卡**：
```css
.card { background: #FFFFFF; border: 1px solid #E8E8EC; border-radius: 8px; padding: 24px; }
.card--accent { border-left: 3px solid #FE2C55; }
```

### 标题样式

**Dark 模式**：
- 主标题：`Inter` / `Noto Sans SC`，字重 800（中文 900），`#F5F5F7`，`line-height: 0.95`，`letter-spacing: -0.02em`，左对齐
- 模块标题：字重 700，`#F5F5F7`，前置 8px 青色竖条（`border-left: 3px solid #25F4EE`）
- 眉题 / 标签：`JetBrains Mono` 11px，`#84868F`，全大写，`letter-spacing: .14em`

**Paper 模式**：
- 主标题：墨黑 `#161823`，字重 800；允许一个词用 `Georgia` / `Noto Serif SC` **斜体**做编辑性强调——全页仅 1 处
- 模块标题：字重 700，墨黑，无竖条，改用 1.5px 底部实线

> ⚠️ B10 不用"渐变文字"、不用"描边标题"、不用"投影文字"（唯一例外是 BigNumber 的双色错位，见下）。

### 色彩预算映射

**Dark 模式面积预算**：
- 60% 主色：`#0B0B10` 页面底 + `#16161C` 沉浸区
- 30% 辅助色：`#161823` / `#1C1E2A` 卡片 + `#F5F5F7` 文字
- 强调色：红 **5-8%** + 青 **4-8%**，**合计 12-16%**（比早期版本放宽——把青色压到 4% 以下，B10 就退化成"暗色模板 + 一个红按钮"）

**Paper 模式**：`#FAFAFA` 底 + `#F2F2F4` 卡片 + `#161823` 文字；红青合计 ≤ 10%，且只做线、角标、下划线与小色块。

### 颜色不是预算，是角色

B10 的红与青**各有分工**，这是它区别于"暗色主题"的关键。只给面积不给角色，结果一定是只用红：

| 角色 | 颜色 | 承担什么 | 至少出现 |
|:--|:--|:--|:--|
| **行动色** | 红 `#FE2C55` | CTA、首个关键数字、警示、进度条、当前项标记 | 1 处，但不能只有它 |
| **结构色** | 青 `#25F4EE` | section 分隔线、编号与眉题、右栏计数、引用条、图表基线、单位符号 | **≥2 处结构功能** |
| **信息色** | 灰阶 `#AEB2C0` / `#84868F` | 正文说明、元信息、辅助标签 | 贯穿 |
| **主色** | 白 `#F5F5F7` | 主标题、核心内容 | 贯穿 |

> ⚠️ **青色存在感底线**：如果一页里青色只出现在双色错位的 4px 描边里，等同于没用。落地时必须回答："青在这张图上干了哪两件结构性的活？"答不出来就把它加上去——换掉一条分隔线、一组编号，或右栏的计数。

**红青同时出现的规则**：红在"动作位"，青在"结构位"，二者不承担同一个功能，也不大面积相邻。红青相邻且各自 ≥3% 面积即为"廉价霓虹"，返工。

**T4 例外**：B10 海报允许**一条**满宽红色 CTA 条（高度 ≤ 画布 8%）或**一个**满铺红色 hero 区块（面积 ≤ 35%）。二者只能选一。此时青色仍必须占 ≥2 处结构位。

### 图标风格

- **线性图标，线宽 2px**（比 B9 的 1.5px 更硬，这是 B10 的手感来源），24×24 viewBox，`stroke-linecap: round`
- Dark 模式：颜色 `#F5F5F7`；次级图标 `#84868F`
- Paper 模式：颜色 `#161823`
- 动作栏图标尺寸 28-32px；正文内联图标 14-16px
- 禁止面性图标、禁止彩色图标、禁止图标内外加圆底

### BigNumber 样式

**Dark 模式**：
```css
.bignum-value {
  font-family: 'JetBrains Mono', 'Noto Sans SC', monospace;
  font-size: 132px;                  /* A2；A1=72-96, A3=112-128, A4=112-140 */
  font-weight: 700;
  color: #FE2C55;                    /* 首个数字红 */
  line-height: 1;
  letter-spacing: -0.03em;
}
.bignum-item:nth-child(2) .bignum-value { color: #25F4EE; }  /* 第二个用青 */
.bignum-item:nth-child(n+3) .bignum-value { color: #F5F5F7; } /* 第三个起回归白 */
.bignum-label {
  font-family: 'JetBrains Mono', 'Noto Sans SC', monospace;
  font-size: 12px;
  color: #84868F;
  margin-top: 12px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}
```

**T4 专属**：允许一次双色错位（`text-shadow: 3px 2px 0 #25F4EE, -3px -2px 0 #FE2C55`），**且只能作用于一个数字**。注意这是 0 模糊的硬偏移，不是发光。

**Paper 模式**：`color: #161823`，标签 `#5D5F6B`，不用错位。

### 署名样式

**Dark**：
```css
.signature {
  font-family: 'JetBrains Mono', monospace;
  color: #84868F;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
```

**Paper**：`color: #5D5F6B`，其余相同。

### 与 B8 赛博街道的分界

两者都是深底 + 高饱和强调，容易被混用。判断标准：

| 维度 | B8 赛博街道 | B10 短视频潮流 |
|:--|:--|:--|
| 情绪 | 反叛、gritty、地下 | 潮流、直接、平台感 |
| 强调色 | 霓虹粉 `#ff006e` + 电青 | 官方红 `#FE2C55` + 对位青 `#25F4EE` |
| 特效 | 扫描线、故障错位、噪点、霓虹光晕 | **无特效**；只有硬边框、渐隐、一次双色错位 |
| 圆角 | 零圆角 / 硬切 | 2 / 6 / 8 / 12，CTA 可 pill |
| 字体 | 全大写、故障感 | 压缩巨字 + mono 元信息 |
| 元信息 | 少 | 丰富（mono 标签是质感来源） |

> 一句话：**B8 靠"破坏"制造冲击，B10 靠"纪律"制造冲击**。如果一个 B10 页面里出现了扫描线、霓虹光晕或超过一处的错位，它已经滑向 B8 了。

---

## B11: 粗野平面 (Brutalist Graphic)

> 设计哲学：把地下出版物的印刷暴力和瑞士朋克的排版实验压进一张纸。**近黑底 + 黑白高反差**是全部基调，红与荧光绿只作为"数字信号"点状闪烁。文字不是用来读的装饰，它本身就是图形结构：字号可以到 200px，也可以到 9px，中间没有过渡；字距压到贴在一起，行距收紧到近乎重叠；断行不讲礼貌，单词可以被拆到两行。照片是灰度半调拼贴，带复印机跑偏的颗粒。它故意不对齐，但每一处错位都是算过的。

**这一风格只有 Dark 一种模式**，不提供浅色版本。T4 直接使用 Dark。

### 配色

| 角色 | 值 | 用途 |
|:--|:--|:--|
| 场（底色） | `#0A0A0A` | 整页主背景，也是"留白"——这里的空白是黑的 |
| 场（次层） | `#141414` / `#1F1F1F` | 硬边方块、影像遮罩底 |
| 纸（反白） | `#F4F4F0` | 反白色块、正文反相块 |
| 墨（文字） | `#F4F4F0` | 主文字，**不用纯白**（纯白在近黑上会发飘） |
| 灰阶 | `#D8D8D2` / `#A8A8A2` / `#6E6E6A` | 辅助文字、半调、影像中间调 |
| 线条 | `#2E2E2E` | 硬边分隔、遮罩边缘 |
| 信号红 | `#FF2D16` | 点状强调：一个编号、一处下划、一个 8px 方块 |
| 荧光绿 | `#B6FF00` | 点状强调：技术标记、迷你标签、状态点 |

> **红与绿是"信号"不是"配色"**：单色面积 ≤3%，两者合计 ≤5%。它们只以 6-14px 的方块、1-2 字的小标签、1.5px 的短线形式出现。一旦某个红块超过页面面积 3%，它就从"信号"变成了"配色方案"，风格立刻垮掉。

### 三层结构

B11 的页面永远是三层叠出来的，缺一层就只剩"黑底大字"：

1. **黑场**（背景层）：`#0A0A0A`，占 40-60% 面积。它是材料，不是空隙。
2. **影像层**（灰度拼贴）：黑白照片、半调网点、硬边方块遮罩。可以只占 15%，也可以切掉画面一角。
3. **文字层**（结构）：巨型字块、极小标注、编号、技术标记。文字块要能**独立构成图形**——把字当色块用。

### 排版规则

**尺度**：最大字号 ÷ 最小字号 = **14:1 ~ 22:1**（这是全风格唯一的例外，见下方"与质检的关系"）。全页字号可到 8 级，但必须形成"巨块—中块—微标记"三段式，不允许平均分布。

**字距与行距**：
```css
.display {
  letter-spacing: -0.045em;   /* 大字：压到贴住 */
  line-height: 0.86;          /* 行距小于 1，让字块变成实心块 */
  text-transform: uppercase;  /* 西文全大写，中文不适用 */
}
.micro {
  font-size: 9px;
  letter-spacing: 0.18em;     /* 小字：反而拉开，形成"技术标注感" */
  text-transform: uppercase;
}
```
大字靠**收紧**，小字靠**拉开**——这是 B11 的呼吸方式，两个方向都不能省。

**断行与拆字**：
- 大胆断行：单行 2-4 个字符就换行，允许中文成语被拆成 `先
破
后
立`
- 跨行拆字：把一个词拆到两行，甚至拆成单字竖排（`display: flex; flex-direction: column`）
- 允许文字**部分越出画布**被裁切，但必须保证语义可读（切掉的只能是字身外延）
```html
<h1 class="display">
  <span class="line">先</span>
  <span class="line">破</span>
  <span class="line">后</span>
  <span class="line">立</span>
</h1>
```

**贴边**：文字优先贴画面边缘（左 40px 以内），而不是居中或等边距。至少一处元素与画布边缘距离为 0。

### 图像处理

没有真实照片时用**灰度色块 + 半调 + 噪点**模拟，四件事依次叠加：

```css
/* 1. 照片本体：去色 + 提对比，保留立体明暗 */
.photo {
  filter: grayscale(1) contrast(1.55) brightness(1.04);
  background: #1F1F1F;          /* 无照片时：用灰度渐变块占位 */
}
/* 2. 半调网点：一层点阵，multiply 叠在影像上 */
.photo::after {
  content: ""; position: absolute; inset: 0;
  background-image: radial-gradient(#0A0A0A 1px, transparent 1.3px);
  background-size: 5px 5px;
  mix-blend-mode: multiply; opacity: 0.55;
  pointer-events: none;
}
/* 3. 硬边遮罩：直角方块切掉一角，不做圆角 */
.photo-mask {
  clip-path: polygon(0 0, 100% 0, 100% 72%, 78% 72%, 78% 100%, 0 100%);
  border-radius: 0;
}
/* 4. 阶梯像素轮廓：用阶梯 clip-path 模拟低分辨率边缘 */
.stair {
  clip-path: polygon(0 0, 100% 0, 100% 100%, 88% 100%, 88% 92%, 76% 92%,
                     76% 84%, 64% 84%, 64% 76%, 0 76%);
}
```

**噪点 / 复印颗粒**（全页最多一层，opacity ≤0.06）：
```html
<svg style="position:absolute;width:0;height:0">
  <filter id="grain">
    <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" result="n"/>
    <feColorMatrix type="saturate" values="0"/>
    <feComponentTransfer><feFuncA type="linear" slope="0.06"/></feComponentTransfer>
  </filter>
</svg>
<div class="grain-layer" style="position:absolute;inset:0;filter:url(#grain);pointer-events:none"></div>
```

> 半调网点与颗粒是**材质**，不是装饰渐变。它们必须叠在影像或色块之上，不允许单独铺满页面当纹理背景。

### 网格：有控制的失衡

B11 打破网格，但不是随机：

- **不对称配比**：用 7:3、8:2、5:1 的分栏，**禁止 1:1**
- **局部高密度 vs 大面积黑场**：一处塞满字，紧邻一处连续空 ≥25%
- **轴向断裂**：页面上至少有一组元素的左边缘与主轴线错开 24-64px，制造"印刷跑版"
- **配重偏移**：视觉重心允许偏离画布中线，但 ≤12%（超过就是失控，不是失衡）

> 判断标准：把页面缩到 200px 宽，如果看起来像"排版出错"，说明还差一步——需要立刻在失衡处补一个微型标记（红/绿小方块、编号）把它"钉住"。**失衡必须有锚点**，否则只是没排好。

### 微型标记系统

这是 B11 的辨识度来源，每页 3-8 个，统一规格：

| 标记 | 规格 | 用途 |
|:--|:--|:--|
| 信号方块 | 8×8 / 12×12px 实心，红或绿 | 段落起点、关键数字旁 |
| 编号标签 | mono 9-10px，`[03]` / `FIG.02` | 模块索引、图注 |
| 技术短线 | 1.5px × 24-48px，红或绿 | 标题下的"下划线"，只画一段 |
| 角标框 | 1px 描边直角框，套住一个词 | 强调关键词（不用背景色） |

所有标记**直角、无圆角、无阴影**。

### 标题样式

- 主标题：Archivo Black / Anton / Inter Tight 900，`#F4F4F0`，`letter-spacing: -0.045em`，`line-height: 0.86`
- 中文巨型标题：Noto Sans SC 900，允许单字竖排
- 次级标题：全大写 mono 或 700 无衬线，可反相（黑底白字 ↔ 白底黑字）
- 模块标题：`[01]` 编号 + 全大写，字号小但距离拉开
- **禁止**：居中标题、圆角标签、渐变文字、投影

### 卡片样式

B11 几乎没有"卡片"——用**硬边方块**代替：

```css
.block {
  background: #F4F4F0; color: #0A0A0A;   /* 反相块：最常用的结构手段 */
  padding: 24px; border-radius: 0;
}
.frame {                                  /* 描边框：1px 或 2px 直角 */
  border: 1.5px solid #F4F4F0; padding: 20px; border-radius: 0;
}
.photo-block { background: #141414; border-radius: 0; overflow: hidden; }
```
统一 `border-radius: 0`。出现任何圆角即越界。

### 色彩预算

- 60-70%：`#0A0A0A` 黑场 + 灰阶影像
- 20-30%：`#F4F4F0` 反相块与文字
- 5% 以内：红 `#FF2D16` + 绿 `#B6FF00` 点状信号

> 没有第三强调色。红绿同时出现时必须分处两个角落，不允许相邻成"圣诞树"。

### 图标

- 线性 1.5px 或 2px，直角端点（`stroke-linecap: butt`），24×24
- 颜色只取 `#F4F4F0` / `#A8A8A2`
- 允许用**文字符号**替代图标：`+` `×` `→` `/` `|`，字号放大到与图标同高
- 禁止面性、描边圆角、彩色图标

### BigNumber

```css
.bignum-value {
  font-family: 'Archivo Black', 'Noto Sans SC', sans-serif;
  font-size: 200px;              /* A4；A2 可到 260px */
  font-weight: 900;
  letter-spacing: -0.05em;
  line-height: 0.8;
  color: #F4F4F0;
}
.bignum-item:first-child .bignum-value { color: #FF2D16; }  /* 只许一个数字红 */
.bignum-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px; letter-spacing: 0.18em; text-transform: uppercase;
  color: #A8A8A2;
}
```
数字与标签的字号比可达 20:1，这是 B11 允许的。数字下方不加装饰线，改在左上角加一个 8px 信号方块。

### 署名

```css
.signature {
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px; letter-spacing: 0.18em; text-transform: uppercase;
  color: #6E6E6A;
}
```

### 与 B4 建筑粗野的分界

两者都叫"粗野"，但完全不是一回事——选错风格，页面会立刻读成另一种东西：

| 维度 | B4 建筑粗野 | B11 粗野平面 |
|:--|:--|:--|
| 底色 | 混凝土灰 `#D4D4D4` 浅底 | 近黑 `#0A0A0A` 黑场 |
| 色彩 | 黑边框 + 安全橙单强调 | 黑白双色 + 红/荧光绿点状信号 |
| 影像 | 从不使用照片 | 灰度半调拼贴是核心层 |
| 排版 | 横平竖直、粗黑边框、方框阵列 | 跨行拆字、错位、贴边、切边 |
| 质感 | 硬阴影、零纹理 | 半调网点、颗粒、复印低保真 |
| 网格 | 显式的粗网格 | 故意的网格断裂 |
| 情绪 | 力量、直接、建设感 | 先锋、地下、实验印刷 |

> 一句话：**B4 是"混凝土建筑"，B11 是"地下印刷厂"**。

### T4 用法

B11 是天然的海报风格，T4 下选它几乎不会错：

- 主视觉：巨型拆字（单字竖排）+ 一块黑白半调影像 + 一处反相色块
- 放大器：P1 巨型字号（强制）+ P5 非对称网格 + P9 切边出血；P3 描边文字可用，但描边必须是直角 1.5px 实线
- **禁用 P2 满铺彩色色块**：B11 的满铺只能是黑或纸白，不允许红绿铺满
- CTA：一个反相块（白底黑字）或一条 1.5px 红底下划线，不用按钮形状

### 与质检的关系（重要）

B11 是**唯一被允许突破通用阈值**的风格，因为它的美学建立在极端对比上：

| 指标 | 通用要求 | B11 |
|:--|:--|:--|
| 字号跨度 | 8:1 ~ 12:1 | **14:1 ~ 22:1** |
| 字号级数 | ≤ 6 | **≤ 8** |
| 空气占比 (C2) | 22-38% | **34-52%**（黑场是材料） |
| 左右配重偏移 | ≤ 5% | **≤ 12%**（有控制的失衡） |

这些例外写在 `config-schema.json` 的 `styles.B11.layout_override` 里，`layout_check.py --style B11` 会自动应用。**超出 B11 的放宽值依然报错**——"控制"就体现在这里。

---

## B12 光学版画（Optical Print）

适合需要看清材料、结构或变化过程的产品介绍、展览海报、设计方法图。配置选 `B12`，各内容类型都使用 `Print`。先决定读者该看清对象的哪个部位，再决定刻线的走向和标题的切口。

| 画面要素 | 做法 |
|---|---|
| 纸与墨 | 暖纸承托墨蓝文字和主体，橙红标示发生变化的面或笔画。可从纸色 `#F3EBDD`、墨蓝 `#172943`、橙红 `#D34E29` 起稿。正文、单位和小字用深墨。 |
| 主图 | 用 SVG 画出一件与论点相关的东西。先做前、中、后三个遮挡面，再沿折痕、截面或曲面插入一组方向一致的刻线。在高光与指向文字的一侧露出纸面。 |
| 字形 | 宽笔画给镂空留空间。让一段物体轮廓接续一个字母边缘，或沿主图折痕把一个词切成两段套印。汉字保留能区分近形字的部件，名称、量纲和操作指令另以清晰文字承载。 |
| 版心 | 先画主图和标题的接触点，再把原始材料、局部放大或一条证据对到同一条轴。图注放在所指部位的外沿。裁掉外缘后复核物体是否仍可识别。 |
| 密度 | C1 保留一个轮廓和一个落款；C2 把解释放到主图转折处；C3 放大有解释价值的局部并附直接标注，图表、单位与来源置于净纸面。 |

在 T2 中以连续轮廓说明哪一步发生改变；在 T3 中保持真实比例、刻度与单位。标题光影可用一层定向硬边作厚度，刻线疏密表现材质。全幅均匀纹理会吞掉笔画，先减少线数，再缩至阅读尺寸复核。可运行的切字与折面画法见[海报美术指导](poster-art-direction.md)。

---

## 风格选择速查表

| 风格 | 适合内容 | 可以从哪件素材起稿 | 如何把信息排进画面 |
|---|---|---|---|
| B1 暗夜编辑 | 技术、产品剖析 | 在深灰底画一件装置的剖面，用琥珀色标出发生变化的部位 | 沿截面线排解释，标题落在暗部 |
| B2 瑞士精密 | 策略、比较 | 选一个关键比例，画成红色面积图或实物剪影 | 让主数字与图共用一条轴，单位和口径就近排列 |
| B3 有机自然 | 生活、教育、材料 | 从叶脉、织物或真实物件的轮廓中取一处放大 | 让短段落沿外缘落位，米白纸面分开整体与局部 |
| B4 建筑粗野 | 建筑、创意项目 | 用剖切面或分解轴测画出各部件的关系 | 厚边界充当切面，标题和图注贴在不同方向的边上 |
| B5 新波普编辑 | 活动、推广 | 将一件主题物切出轮廓，配一个重复或错色的局部 | 先读标题与物件的重叠处，再顺着色面读到活动信息 |
| B6 极简东方 | 展览、工艺 | 用剪影、一笔轮廓或材质的局部表现主体 | 顺着笔势留出空场，将最短的一句压到收笔处 |
| B7 数据新闻 | 调研、业绩 | 用真实序列画带标尺的主图，在异常值旁注释 | 主图先讲结论，共用基线的小表承载明细与来源 |
| B8 赛博街道 | 游戏、电子文化 | 拿对象的线框、部件或路径作前景，一种信号色标出变化 | 交叠限于标题和主图，参数落在平整底色上 |
| B9 谷歌原生 | 产品、功能发布 | 取一个真实操作前后的状态或几何结构 | 放大有差异的局部，用品牌色引到解释和操作结果 |
| B10 短视频潮流 | 消费产品、招募 | 选一幕能讲清用途的场景，做成占主要画幅的静帧 | 红色给行动，青色引导阅读，短标题跟随画面节奏 |
| B11 粗野平面 | 文化、独立出版 | 从黑白图像切出粗轮廓，在反相块里保留最具辨识度的细节 | 一个词允许解构，正文借稳定的列线保持连读 |
| B12 光学版画 | 产品、展览、方法图解 | 以墨蓝刻线画出主题对象的曲率，用纸色表现高光 | 把字的切口接到物体折痕，让注释落在轮廓收束处 |

---

## BigNumber 模块通用规范

若用户选择 E1（包含 BigNumber），则每张 OnePage 必须包含至少一组 BigNumber 数据展示，位置通常在 Header 下方或第一个内容模块中。若用户选择 E2（不包含 BigNumber），则跳过 BigNumber 模块。

### 结构要求
```html
<div class="bignum-module">
  <div class="bignum-grid" style="grid-template-columns: repeat(3, 1fr);">
    <div class="bignum-item">
      <div class="bignum-value">128<span class="bignum-unit">%</span></div>
      <div class="bignum-label">同比增长</div>
      <div class="bignum-trend up">
        <svg class="icon"><use href="#icon-trend-up"/></svg>
        <span>+23%</span>
      </div>
    </div>
    <!-- 2-4 个数据项 -->
  </div>
</div>
```

### 数量建议
- A1 纵向长图：2 个 BigNumber 横向排列
- A2 横向宽图：3-4 个 BigNumber 横向排列
- A3 正方形：2 个 BigNumber 横向排列

### 趋势指示
- 上升趋势：使用向上箭头 SVG + 强调色
- 下降趋势：使用向下箭头 SVG + 灰色/锈红色
- 中性趋势：使用横线 SVG + 次要文字色

### 视觉冲击原则
- 核心结论由数字承载时放到全页最大；作为主图旁的证据时，给数字和单位留出清晰的位置。
- 数字与标签之间必须有明显的视觉层级差异（至少 3:1 的字号比）
- 保持数值、单位和标签的相邻关系，让读者看清比较口径。
