# 设计风格详细规范

本文件定义了 Onepager 支持的九种设计风格的完整视觉规范。
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

全页色彩不超过 **3 个主色 + 2 个中性色**。B5 新波普编辑、B8 赛博街道、B9 谷歌原生可适当放宽色彩数量，但需保持大致的 60-30-10 比例原则；B9 品牌四色满铺色块不计入主色限制。

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

## 风格选择速查表

| 风格 | 核心情绪 | 适合内容 | 关键识别特征 |
|------|---------|---------|------------|
| B1 暗夜编辑 | 专业、深沉、可信 | 技术文档、SaaS产品 | 深灰底+琥珀色+等宽数据 |
| B2 瑞士精密 | 理性、精确、权威 | 金融报告、策略方案 | 纯白+正红+零圆角+粗线 |
| B3 有机自然 | 温暖、人文、治愈 | 生活方式、教育、品牌 | 米白+陶土色+衬线体+大圆角 |
| B4 建筑粗野 | 力量、直接、叛逆 | 创意项目、青年品牌 | 混凝土灰+粗黑边框+硬阴影 |
| B5 新波普编辑 | 活力、大胆、时尚 | 营销海报、活动推广 | 奶油白+撞色卡片+杂志排版 |
| B6 极简东方 | 宁静、克制、高级 | 艺术展览、奢侈品牌 | 极浅灰+墨黑+朱红细线+巨量留白 |
| B7 数据新闻 | 理性、精确、可信 | 数据报告、行业分析 | 报纸白+海军蓝+等宽字体+网格线 |
| B8 赛博街道 | 未来、 gritty、酷 | 游戏、科技、潮流 | 深黑+霓虹粉/电青+扫描线 |
| B9 谷歌原生 | 克制、专业、胆大 | 商业说服、ToB、活动 | 白底+Google蓝+品牌四色大色块 |

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
- 数字字号必须是页面上最大的文字元素（超过主标题）
- 数字与标签之间必须有明显的视觉层级差异（至少 3:1 的字号比）
- 拒绝"小数字+大图标"的平庸做法，数字本身必须是视觉焦点
