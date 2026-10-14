# 中文字体方案

本文件定义了不同设计风格对应的字体栈方案。
Google Fonts 是可选增强，不是运行前提。所有方案必须配置完整的系统字体 fallback，确保离线或受限网络环境仍可稳定渲染。

---

## 字体哲学

字体是设计的声音。选择字体不是"好看就行"，而是信息性格的外化。

### 核心原则

1. **每页最多 2 种字体家族**（一种标题，一种正文），超过 2 种即视觉噪音
2. **每页最多 3 种字重**（如 400/600/900），字重过多会消解层级对比的力量
3. **数据必须使用等宽字体**：数字在等宽字体下对齐精确，传达可信感
4. **衬线体 = 人文/历史/优雅；无衬线体 = 现代/理性/效率**
5. **拒绝装饰性字体用于正文**：展示字体（如 ZCOOL 系列）仅限标题或极短文本

### 字体性格对照

| 字体类型 | 传递情绪 | 适用风格 |
|---------|---------|---------|
| 无衬线体 (Sans-serif) | 现代、理性、效率 | B1, B2, B4, B5, B8, B9 |
| 衬线体 (Serif) | 人文、历史、优雅 | B3, B6, B7 |
| 等宽体 (Monospace) | 精确、技术、数据 | B1, B7, B8, B9 (数据展示) |
| 系统字体 | 原生、直接、无修饰 | B4 (粗野主义专用) |
| Inter + Noto Sans SC | 克制、专业、国际化 | B9 (Google 原生专用) |

---

## 通用加载方式

在 HTML 的 `<head>` 中，可根据风格加载对应网络字体；若运行环境不允许联网，直接使用同一方案中的系统 fallback：

### 标准加载（B1, B2, B4, B5, B8）
```html
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap');
</style>
```

### 衬线加载（B3, B6, B7）
```html
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap');
</style>
```

### B4 粗野主义专用
B4 风格**不使用 Google Fonts**，优先使用系统字体栈，传递原生、不加修饰的力量感。

---

## 字号阶梯与比例

字号比例采用 **1.333（Perfect Fourth）** 作为主要比例，在紧凑场景可使用 **1.25（Major Third）**。

### A1 纵向长图 (800px)

| 层级 | 字号 | 字重 | 用途 |
|------|------|------|------|
| BigNumber | 72-96px | 700-900 | 核心数据展示 |
| L1 主标题 | 38-48px | 700-900 | 核心论点/产品名 |
| L2 副标题 | 28-32px | 600-700 | 价值主张/方案名 |
| L3 小标题 | 22-24px | 600-700 | 模块标题 |
| L4 正文 | 15-16px | 400-500 | 段落文字 |
| L5 辅助说明 | 12-13px | 400 | 来源/日期/脚注 |

### A2 横向宽图 (1920px)

| 层级 | 字号 | 字重 | 用途 |
|------|------|------|------|
| BigNumber | 120-180px | 700-900 | 核心数据展示（页面上最大的文字） |
| L1 主标题 | 56-72px | 700-900 | 核心论点/产品名 |
| L2 副标题 | 32-40px | 600-700 | 价值主张/方案名 |
| L3 小标题 | 26-28px | 600-700 | 模块标题 |
| L4 正文 | 18-20px | 400-500 | 段落文字 |
| L5 辅助说明 | 14-16px | 400 | 来源/日期/脚注 |

### A3 正方形 (1080px)

| 层级 | 字号 | 字重 | 用途 |
|------|------|------|------|
| BigNumber | 96-144px | 700-900 | 核心数据展示 |
| L1 主标题 | 42-56px | 700-900 | 核心论点/产品名 |
| L2 副标题 | 26-30px | 600-700 | 价值主张/方案名 |
| L3 小标题 | 20-24px | 600-700 | 模块标题 |
| L4 正文 | 16-18px | 400-500 | 段落文字 |
| L5 辅助说明 | 12-14px | 400 | 来源/日期/脚注 |

### A4 竖版海报 (1080px)

| 层级 | 字号 | 字重 | 用途 |
|------|------|------|------|
| BigNumber | 96-140px | 700-900 | 核心数据展示 |
| L1 主标题 | 36-56px | 700-900 | 核心论点/产品名 |
| L2 副标题 | 22-30px | 600-700 | 价值主张/方案名 |
| L3 小标题 | 18-24px | 600-700 | 模块标题 |
| L4 正文 | 16-18px | 400-500 | 段落文字 |
| L5 辅助说明 | 12-14px | 400 | 来源/日期/脚注 |

**A4 说明**：
- 画布尺寸 1080×1440px（3:4），垂直空间比 A3 多 360px
- 正文字号约为画布宽度的 1.5%-1.7%
- BigNumber 与 A3 接近，但可适当放大至 140px（空间充裕时）
- 2 栏布局或单栏+图表混合布局

### BigNumber 字号规范（强制）

BigNumber 的字号必须是**页面上最大的文字元素**，必须超过主标题的字号。

| 尺寸 | 最小 BigNumber | 推荐 BigNumber | 单位字号 | 标签字号 |
|------|---------------|---------------|---------|---------|
| A1 | 72px | 84-96px | 28-32px | 14-16px |
| A2 | 120px | 140-160px | 40-48px | 16-18px |
| A3 | 96px | 120-132px | 32-40px | 14-16px |
| A4 | 96px | 112-140px | 32-40px | 14-16px |

**规则**：
- BigNumber 数字与主标题的字号比至少为 **1.5:1**
- BigNumber 数字与标签的字号比至少为 **4:1**
- 单位（如 `%`, `+`, `x`）使用比数字小 30-50% 的字号
- 小数点使用与单位相同的字号和颜色

> **T4 宣传海报例外**：T4 使用专属字号阶梯，BigNumber 与正文比 ≥ 8:1，不遵循上表。详见 [cross-reference.md](cross-reference.md) 第 4 节。

---

## 字号计算原则

- 正文字号约为画布宽度的 **1.8%-2.2%**
- 主标题约为正文字号的 **2.5-3.5 倍**
- BigNumber 约为正文字号的 **5-8 倍**
- 副标题约为正文字号的 **1.5-1.8 倍**
- 辅助说明约为正文字号的 **0.8-0.9 倍**

**高密度模式 (C3) 调整**：
- 正文字号可取范围下限，留出更多空间给内容
- 标题和 BigNumber 字号保持不变，维持视觉层级

**低密度模式 (C1) 调整**：
- 正文字号可取范围上限，增强阅读舒适度
- BigNumber 字号可适当放大，增强视觉冲击力
- 行高可适当增加

---

## 风格-字体映射

### B1 暗夜编辑

传达精确、深沉、技术可信感。

```css
:root {
  --font-heading: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', sans-serif;
  --font-body: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', 'SF Mono', monospace;
}
```

- 主标题：字重 800，无衬线
- 模块标题：字重 600
- BigNumber：等宽字体 JetBrains Mono，字重 700
- 正文：字重 400，行高 1.8
- 字重限制：400 / 600 / 800（最多3种）

### B2 瑞士精密

传达理性、权威、网格纪律。

```css
:root {
  --font-heading: 'Noto Sans SC', 'Inter', 'Helvetica Neue', 'PingFang SC', sans-serif;
  --font-body: 'Noto Sans SC', 'Inter', 'Helvetica Neue', 'PingFang SC', sans-serif;
  --font-mono: 'JetBrains Mono', 'SF Mono', monospace;
}
```

- 主标题：字重 900（极粗），可能是正文的 4 倍
- 模块标题：字重 700
- BigNumber：无衬线，字重 900，正红色
- 正文：字重 400
- 字重限制：400 / 700 / 900（最多3种）

### B3 有机自然

传达人文、温暖、自然气息。

```css
:root {
  --font-heading: 'Noto Serif SC', 'Songti SC', 'STSong', 'SimSun', serif;
  --font-body: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
}
```

- 主标题：衬线体 Noto Serif SC，字重 700
- 模块标题：无衬线体，字重 600，陶土色
- BigNumber：衬线体 Noto Serif SC，字重 700
- 正文：无衬线体，字重 400，行高 2.0
- 字重限制：400 / 600 / 700（最多3种）

### B4 建筑粗野

传达原始、力量、不加修饰。

```css
:root {
  /* B4 不使用 Google Fonts，使用系统字体栈 */
  --font-heading: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans SC', 'PingFang SC', sans-serif;
  --font-body: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans SC', 'PingFang SC', sans-serif;
  --font-mono: 'SF Mono', 'Cascadia Code', 'Noto Sans SC', monospace;
}
```

- 主标题：系统字体，字重 900，极大字号
- 模块标题：系统字体，字重 700
- BigNumber：系统字体，字重 900，电黄背景块
- 正文：系统字体，字重 400
- 字重限制：400 / 700 / 900（最多3种）

### B5 新波普编辑

传达活力、大胆、杂志感。

```css
:root {
  --font-heading: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  --font-body: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
}
```

- 主标题：字重 900，Extra Bold，极大字号
- 模块标题：字重 700
- BigNumber：字重 900，黑字+黄底块
- 正文：字重 400-500
- 字重限制：400 / 700 / 900（最多3种）

### B6 极简东方

传达宁静、克制、高级感。

```css
:root {
  --font-heading: 'Noto Serif SC', 'Songti SC', 'STSong', 'SimSun', serif;
  --font-body: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
}
```

- 主标题：衬线体 Noto Serif SC，字重 400（极轻，以体量取胜）
- 模块标题：无衬线体，字重 300
- BigNumber：衬线体 Noto Serif SC，字重 400，墨黑色
- 正文：无衬线体，字重 400，行高 2.2
- 字重限制：300 / 400 / 700（最多3种）

### B7 数据新闻

传达理性、精确、可信感。

```css
:root {
  --font-heading: 'Noto Serif SC', 'Georgia', 'Times New Roman', serif;
  --font-body: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
}
```

- 主标题：衬线体 Noto Serif SC，字重 700，深海军蓝
- 模块标题：无衬线体，字重 600
- BigNumber：等宽字体 JetBrains Mono，字重 700，深海军蓝
- 正文：无衬线体，字重 400
- 图表标签：等宽字体，字重 500，小字号，全大写
- 字重限制：400 / 600 / 700（最多3种）

### B8 赛博街道

传达未来、 gritty、酷感。

```css
:root {
  --font-heading: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  --font-body: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', 'SF Mono', monospace;
}
```

- 主标题：字重 800，可使用极简故障效果
- 模块标题：字重 600，霓虹色
- BigNumber：等宽字体 JetBrains Mono，字重 700，霓虹粉
- 正文：字重 400，轻微字母间距（`letter-spacing: 0.03em`）
- 字重限制：400 / 600 / 800（最多3种）

### B9 谷歌原生

传达系统化克制与局部胆大。Google 官方网站设计语言。

**Light 模式**（默认）：
```css
:root {
  --font-heading: 'Inter', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', system-ui, sans-serif;
  --font-body: 'Inter', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', 'IBM Plex Mono', 'SF Mono', monospace;
}
```

**Dark 模式**（I/O 风格）：
```css
:root {
  --font-heading: 'Inter', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', system-ui, sans-serif;
  --font-body: 'Inter', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', 'IBM Plex Mono', 'SF Mono', monospace;
}
```

- 主标题：Inter + Noto Sans SC，英文用字重 500，中文因笔画密度可用 700-900
- 模块标题：字重 500，`#202124`（Light）/ `#f1f3f4`（Dark）
- BigNumber：等宽字体 JetBrains Mono，字重 700，Google 蓝 `#1a73e8`（Light）/ 浅蓝 `#8ab4f8`（Dark）
- 正文：字重 400，行高 1.6-1.7
- 数据标签：等宽字体 JetBrains Mono，字重 500，小字号，全大写，`letter-spacing: 0.05em`
- 字重限制：400 / 500 / 700（英文最多 3 种；中文标题允许 900 但不与英文混用）

**中文排版特殊规则（B9 专属）**：
- 中文标题推荐用 700-900（Noto Sans SC 900），英文标题配 500-600（Inter 600），这样中英文视觉权重相等
- 中文正文行高 1.6-1.7，display 行高 1.15-1.3
- 标题 48px 以上 `letter-spacing: -0.5px`，32-48px `-0.25px`，24px 以下 `0`
- 中文按钮文字 `letter-spacing: 0`（不要照搬英文的 0.25px）
- 正文建议 17-18px 起步（中文比英文同字号下显小）

**Google Fonts 加载**：
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+SC:wght@300;400;500;700;900&family=JetBrains+Mono:wght@400;500;700&display=swap');
</style>
```

---

## 中文排版核心参数

无论何种风格，以下参数必须遵守：

```css
body {
  font-size: 15px;           /* 正文基础字号（A1基准，A2/A3按比例放大） */
  line-height: 1.8;          /* 中文需要更大行高 */
  letter-spacing: 0.02em;    /* 微调字间距 */
  text-align: justify;       /* 两端对齐 */
  word-break: break-all;     /* 中文断字 */
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

h1, h2, h3 {
  line-height: 1.4;          /* 标题行高可收紧 */
  letter-spacing: 0.04em;    /* 标题字间距稍大 */
  margin-bottom: 0.6em;
}

p {
  margin-bottom: 1em;        /* 段间距 > 行间距 */
}
```

### 风格差异化排版参数

| 风格 | 正文行高 | 标题行高 | 字间距 | 特殊处理 |
|------|---------|---------|--------|---------|
| B1 暗夜编辑 | 1.8 | 1.4 | 0.02em | 数据区域 letter-spacing: 0.05em |
| B2 瑞士精密 | 1.6 | 1.2 | 0 | 标题 letter-spacing: -0.02em（紧凑感） |
| B3 有机自然 | 2.0 | 1.5 | 0.02em | 正文 text-align: left（拒绝两端对齐） |
| B4 建筑粗野 | 1.6 | 1.1 | 0.01em | 标题 text-transform: uppercase |
| B5 新波普编辑 | 1.7 | 1.3 | 0.03em | 大标题 letter-spacing: -0.03em |
| B6 极简东方 | 2.2 | 1.6 | 0.05em | 标题 font-weight: 400 |
| B7 数据新闻 | 1.8 | 1.4 | 0.01em | 图表标签全大写 |
| B8 赛博街道 | 1.8 | 1.4 | 0.03em | 正文 letter-spacing: 0.03em |
| B9 谷歌原生 | 1.6-1.7 | 1.15-1.3 | 0 | 英文 500 字重为主，中文 700-900；标题 48px+ 负 letter-spacing |

---

## 字体加载失败的 fallback 策略

为保证在字体未能加载的情况下依然呈现良好效果：

1. 始终将系统中文字体放在 fallback 链中
2. macOS: `PingFang SC`, `Hiragino Sans GB`
3. Windows: `Microsoft YaHei`
4. Linux: `WenQuanYi Micro Hei`
5. 最终 fallback: `sans-serif`

### 完整 fallback 示例

**无衬线体**：
```css
font-family: 'Noto Sans SC', 'PingFang SC', 'Hiragino Sans GB',
             'Microsoft YaHei', 'WenQuanYi Micro Hei', sans-serif;
```

**衬线体**：
```css
font-family: 'Noto Serif SC', 'Songti SC', 'STSong',
             'SimSun', 'WenQuanYi Micro Hei', serif;
```

**等宽体**：
```css
font-family: 'JetBrains Mono', 'Fira Code', 'SF Mono',
             'Cascadia Code', 'Noto Sans SC', monospace;
```

---

## 字重使用禁忌

1. **禁止在正文中使用字重 100/200**：过细的字重在屏幕上可读性极差
2. **禁止在标题中使用字重 300 以下**：标题需要视觉存在感
3. **禁止同一层级使用两种字重**：如"正文"只能有一种字重，不可混用 400 和 500
4. **禁止字重跳跃**：如果使用了 400 和 700，中间没有 500/600 的过渡，跳跃感过强
5. **B6 极简东方例外**：允许标题使用 400（极轻），这是风格的一部分
