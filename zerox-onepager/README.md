> 当前维护位置 / Maintained at: [zerox-onepager](https://github.com/ZeroxZhang/zerox-skills/tree/main/zerox-onepager).
> 调用 `/zerox-onepager`。本页头图由技能生成，采用 B12 光学版画、3:4 竖版、中密度产品介绍海报。 / Invoke `/zerox-onepager`. The skill generated the cover as a 3:4, medium-density product poster in B12 Optical Print.

<div align="center">
  <a href="#english">English</a> | <a href="#简体中文">简体中文</a>
</div>

---

<h1 id="english">zerox-onepager</h1>

> A Claude Agent Skill for converting text content into high-quality OnePage infographics.

![Optical Print poster for zerox-onepager with a sliced ONEPAGE title and a line engraving of folded sheets](./onepager-readme-A4-B12-20261123.png)

[Editable poster HTML](./onepager-readme-A4-B12-20261123.html) · [Art direction and SVG techniques](./references/poster-art-direction.md)

## Overview

zerox-onepager is a Claude Agent Skill that transforms your provided text, Markdown, or PDF content into beautiful OnePage infographics (single-page visual posters) through a progressive interactive workflow.

### Use Cases

- Product feature introductions
- Strategy / methodology presentations
- Infographic creation
- Data visualization overviews
- One-page team/project reports

### Core Features

- **Multiple Sizes**: Vertical scroll (Mobile), Horizontal widescreen (16:9), Square (1:1), Portrait poster (3:4 for Xiaohongshu/WeChat) — 4 sizes total
- **Usage Scenes First**: Six scenes (product intro, work report, client pitch, event promo, data insight, how-to) that each carry a validated default configuration, so users pick "what it is for" instead of decoding six abstract dimensions
- **Twelve Design Styles**: Dark Editorial, Swiss Precision, Organic Nature, Constructivist Brutalism, Neo-Pop Editorial, Minimalist East, Data Journalism, Cyber Street, Google Native, Short-Video Feed (B10), Brutalist Graphic (B11), and Optical Print (B12)
- **Font Matching Step**: A dedicated font-matching pass with a curated open-source/Google Fonts library, CDN loading, CJK-aware fallback chains, and a seven-option `G1-G7` scheme
- **Three Information Densities**: Low/Medium/High density, automatically rewriting content to match the layout
- **Content Intelligence**: Applies consulting-grade content principles (MECE, Pyramid, SCQA, So What, Quantification) to restructure content for maximum impact
- **Type Differentiation**: Automatically detects and adapts to 4 content types (Commercial Persuasion with product/solution focus, Usage Guide with steps/spec focus, Infographic, Promotional Poster) with type-specific restructuring, focus sub-parameters, and T4 visual impact amplifiers
- **Smart Diagram Matching**: Automatically selects flowcharts, structure diagrams, architecture diagrams, etc., based on content logic
- **Optional BigNumber**: Toggle data highlight modules on/off (E1/E2), replace with quotes, diagrams, or whitespace when disabled
- **Signature/署名**: Use the Git user name or a custom brand signature and position it within the composition
- **Content-Based Naming**: Output files named as `{topic}-{size}-{style}-{date}` instead of generic names, avoiding overwrites
- **One-Click Config**: Accept recommended settings in one step during the interactive configuration phase
- **User-Controlled S/A/B/C/T/E/G/F Protocol**: Keep the full scene, size, style, density, type, BigNumber, font, and signature menu visible; the scene presets the rest, recommendations explain why, and users retain final control
- **Content Blueprint**: Review the audience, core claim, modules, evidence, and missing facts before rendering
- **Reproducible Projects**: Persist Blueprint, Onepager IR, confirmed configuration, build artifacts, quality reports, and SHA-256 hashes
- **Visual Standards**: 8pt Grid system, 60-30-10 color rule, WCAG AA contrast, consistent icon styles, plus a design-impact layer (single hero moment, full-bleed, cropped type, rhythm, negative space, optical alignment)
- **Poster composition**. Choose a subject from the material. Draw an original SVG, annotate a real object or chart, or shape a short title with a printable cut, knockout, overprint or relief. Recompose the page when its density or aspect ratio changes.
- **Chinese Typography Optimization**: Matches the best Chinese font scheme based on the design style
- **Quality checks**. Static and browser checks cover source structure, composition, canvas size, clipping and overflow. Review the exported image at full and thumbnail sizes.
- **Reliable HTML → PNG Conversion**: Fail-closed Playwright capture with atomic writes and output-dimension verification
- **Iteration & Rework**: Built-in guidance for fine-tuning, config changes, and content revisions post-delivery

## Installation

### Method 1: Upload on Claude.ai

1. Compress the `zerox-onepager/` folder into a ZIP file.
2. Open Claude.ai → Settings → Customization → Skills.
3. Click "+" → Upload the ZIP file.

### Method 2: Project Integration (Claude Code / Trae)

Copy the folder to your project's `.claude/skills/` or `.trae/skills/` directory:

```bash
cp -r zerox-onepager/ .trae/skills/zerox-onepager/
```

### Method 3: Global Installation

```bash
cp -r zerox-onepager/ ~/.trae/skills/zerox-onepager/
```

## Usage

Simply describe your request to the AI to trigger it automatically, for example:

- "Help me make an infographic out of this product description"
- "Generate a OnePage from this Markdown"
- "Turn this text into a long image suitable for mobile reading"

Or use the slash command to call it explicitly: `/zerox-onepager`

The interaction starts with a usage scene and always keeps the complete
`S/A/B/C/T/E/G/F` menu. You may accept the scene defaults, name just the scene,
or override any dimension:

```text
S3                             # client pitch, accept its defaults
S1 A4 B12 C2 T4 E2 G2 FZerox   # Optical Print product poster, system fonts
```

Reproducible project assets can be managed independently of the AI runtime:

```bash
python3 scripts/project.py init .onepager/projects/demo \
  --slug demo --title "Demo"
python3 scripts/project.py next-version .onepager/projects/demo
python3 scripts/project.py validate .onepager/projects/demo
```

## File Structure

```text
zerox-onepager/
├── SKILL.md                  # Core instructions (Entry point for the Agent)
├── scripts/
│   ├── capture.py            # Playwright HTML→PNG screenshot script
│   ├── install_deps.sh       # Dependency installation helper script
│   ├── project.py            # Reproducible project and build manifest CLI
│   ├── quality_check.py      # Static contract and design validation
│   ├── layout_check.py       # Composition: holes, voids, air ratio, type scale
│   └── render_check.py       # Browser-rendered geometry validation
├── references/
│   ├── config-schema.json    # Machine-readable configuration source of truth
│   ├── blueprint-schema.json # Content Blueprint contract
│   ├── onepager-ir-schema.json # Semantic intermediate representation
│   ├── manifest-schema.json  # Reproducible build manifest contract
│   ├── scenes.md             # Usage scene catalog: defaults, must-haves, acceptance tests
│   ├── layout-archetypes.md  # Layout archetypes and canvas budgets
│   ├── font-library.md       # Open-source / Google Fonts catalog, matching flow, loading rules
│   ├── design-styles.md      # Full visual specifications for the 12 design styles
│   ├── poster-art-direction.md # Static lettering, SVG illustration and composition
│   ├── typography.md         # Chinese font schemes and typography parameters
│   ├── layout-specs.md       # Layout specifications for the 4 sizes
│   ├── diagram-guide.md      # Diagram type matching and drawing guide
│   ├── density-guide.md      # Information density and content rewriting rules
│   ├── type-differentiation.md # Differentiated guidelines for 4 content types with focus sub-parameters
│   ├── cross-reference.md     # Dimension cross-reference rules (T×B, T×A, B×T)
│   └── visual-standards.md   # Cross-style universal visual standards
├── assets/
│   └── templates/
│       ├── lettering.svg      # SVG lettering / 可编辑字形母版
│       └── base-skeleton.html# HTML base skeleton template
├── tests/                    # Unit and Playwright integration tests
├── requirements.txt         # Python runtime dependencies
├── LICENSE.txt
└── README.md
```

## Dependencies

The screenshot and rendered-quality features require Python 3.8+, Playwright, and Chromium. The idempotent installer verifies both the Python package and browser executable:

```bash
bash scripts/install_deps.sh
```

If the runtime environment does not support screenshot tools, the Skill will directly deliver the HTML file.

## License

Apache License 2.0

---

<h1 id="简体中文">zerox-onepager</h1>

> 将文字内容转化为高品质 OnePage 介绍图的 Agent Skill。

![zerox-onepager 光学版画海报，切片字标下方是一叠弯曲的纸张，以刻线表现厚度](./onepager-readme-A4-B12-20261123.png)

[海报 HTML 源文件](./onepager-readme-A4-B12-20261123.html) · [构图与 SVG 字形做法](./references/poster-art-direction.md)

## 功能概述

zerox-onepager 是一个 Agent Skill，能够将用户提供的文字、Markdown 或 PDF 内容，通过渐进式交互流程，转化为精美的 OnePage 信息图（单页可视化海报）。

### 适用场景

- 产品功能介绍
- 策略/方法论展示
- 信息图表制作
- 数据可视化概览
- 团队/项目一页纸汇报

### 核心特性

- **多尺寸支持**：纵向长图、横向宽图 (16:9)、正方形 (1:1)、竖版海报 (3:4，适合小红书/公众号封面)
- **先选使用场景**：产品介绍 / 工作汇报 / 客户沟通 / 活动宣传 / 数据洞察 / 知识方法，每个场景自带一套经过验证的默认配置，用户只需判断"这是什么用途"
- **十二种设计风格**：暗夜编辑、瑞士精密、有机自然、建筑粗野、新波普编辑、极简东方、数据新闻、赛博街道、谷歌原生、短视频潮流（B10）、粗野平面（B11）、光学版画（B12）
- **字体匹配环节**：独立的字体匹配步骤 + 精选开源字库（以 Google Fonts 为主）+ CDN 加载规范 + 中文 fallback 链 + `G1-G7` 七档字体方案
- **三级信息密度**：低/中/高密度，自动改写内容匹配版式
- **内容智能**：运用咨询级内容原则（MECE、金字塔原理、SCQA、So What、量化优先）重构内容，最大化传达效果
- **类型差异化**：自动识别并适配 4 种内容类型（商业说服含 product/solution 导向、使用指南含 steps/spec 导向、信息图、宣传海报），按类型和 focus 子参数定制重构策略，T4 宣传海报强制启用视觉冲击放大器
- **智能图表匹配**：根据内容逻辑自动选择流程图、结构图、架构图等
- **BigNumber 可选**：数据展示模块可开关（E1/E2），关闭时可用引言块、图表或留白替代
- **署名支持**：自动从 git 用户名读取，或自定义品牌名/公众号名，署名随构图排版
- **内容命名**：输出文件按 `{主题}-{尺寸}-{风格}-{日期}` 命名，避免覆盖已有文件
- **一键采纳推荐**：配置阶段可直接回车采纳推荐配置，快速开始
- **用户可控 S/A/B/C/T/E/G/F 协议**：完整保留场景、尺寸、风格、密度、类型、BigNumber、字体与署名菜单；场景带出默认值，系统解释推荐理由，最终选择权属于用户
- **内容蓝图确认**：渲染前确认受众、核心论点、模块、证据和缺失事实
- **可复现项目**：保存蓝图、Onepager IR、用户确认配置、构建产物、质检报告与 SHA-256
- **视觉规范**：8pt Grid 对齐系统、60-30-10 色彩法则、WCAG AA 对比度、统一图标风格，以及设计感层（单一视觉事件、满血出血、切边巨字、节奏、负空间、光学对齐）
- **图文构图**。从素材中选主体，可以原创 SVG、标注实物或数据图，也可以用切片、镂空、套印或浮雕处理标题。密度和画幅改变时，重新安排图幅、注释位置和留白。
- **中文字体优化**：根据设计风格匹配最佳中文字体方案
- **质量检查**。静态、构图和浏览器渲染三项检查覆盖结构、画布、裁切和溢出，导出后再按原尺寸和缩略图复核。
- **可靠 HTML → PNG 转换**：截图失败即终止，采用原子写入并校验最终 PNG 尺寸
- **调整迭代**：交付后支持微调、配置变更、内容修改等迭代流程

## 安装方式

### 方式一：Claude.ai 上传

1. 将 `zerox-onepager/` 文件夹压缩为 ZIP 文件
2. 打开 Claude.ai → 设置 → 自定义 → Skills
3. 点击 "+" → 上传 ZIP 文件

### 方式二：项目集成 (Claude Code / Trae)

将文件夹复制到项目的 `.claude/skills/` 或 `.trae/skills/` 目录下：

```bash
cp -r zerox-onepager/ .trae/skills/zerox-onepager/
```

### 方式三：个人全局安装

```bash
cp -r zerox-onepager/ ~/.trae/skills/zerox-onepager/
```

## 使用方式

直接向 AI 描述你的需求即可自动触发，例如：

- "帮我把这段产品介绍做成一张信息图"
- "用这份 Markdown 生成一个 OnePage"
- "把这段文字做成一张适合手机阅读的长图"

或使用特定的唤醒词/斜杠命令显式调用：`/zerox-onepager`

交互时可以选择 `S/A/B/C/T/E/G/F`。用户可以采纳推荐组合，也可以覆盖任意维度，例如：

```text
S3                             # 客户沟通，采用场景默认配置
S1 A4 B12 C2 T4 E2 G2 FZerox   # 光学版画产品海报，使用系统字体
```

可复现项目资产可脱离 AI 运行时独立管理：

```bash
python3 scripts/project.py init .onepager/projects/demo \
  --slug demo --title "演示项目"
python3 scripts/project.py next-version .onepager/projects/demo
python3 scripts/project.py validate .onepager/projects/demo
```

## 文件结构说明

```text
zerox-onepager/
├── SKILL.md                  # 核心指令（Agent 读取的入口）
├── scripts/
│   ├── capture.py            # Playwright HTML→PNG 截图脚本
│   ├── install_deps.sh       # 依赖安装辅助脚本
│   ├── project.py            # 可复现项目与构建 Manifest CLI
│   ├── quality_check.py      # 静态契约与设计规范校验
│   ├── layout_check.py       # 构图与 SVG 的可见范围测量
│   └── render_check.py       # 浏览器真实渲染与几何校验
├── references/
│   ├── config-schema.json    # 机器可读配置单一事实源
│   ├── blueprint-schema.json # 内容蓝图契约
│   ├── onepager-ir-schema.json # 语义中间表示
│   ├── manifest-schema.json  # 可复现构建记录契约
│   ├── scenes.md             # 使用场景目录：默认配置、必备模块、验收判据
│   ├── layout-archetypes.md  # 按内容关系选版式、分配画布空间
│   ├── font-library.md       # 开源字库与字体匹配流程、加载规范
│   ├── design-styles.md      # 十二种设计风格的完整视觉规范
│   ├── poster-art-direction.md # 静帧字形、SVG 插画和图文构图
│   ├── typography.md         # 中文字体方案与排版参数
│   ├── layout-specs.md       # 四种尺寸的版式规范
│   ├── diagram-guide.md      # 图表类型匹配与绘制指南
│   ├── density-guide.md      # 信息密度与内容改写规则
│   ├── type-differentiation.md # 四种内容类型的差异化指南（含 focus 子参数）
│   ├── cross-reference.md     # 维度交叉规则（T×B、T×A、B×T 适配）
│   └── visual-standards.md   # 跨风格通用视觉规范
├── assets/
│   └── templates/
│       ├── lettering.svg      # SVG lettering / 可编辑字形母版
│       └── base-skeleton.html  # HTML 基础骨架模板
├── tests/                    # 单元测试与 Playwright 集成测试
├── requirements.txt         # Python 运行时依赖
├── LICENSE.txt
└── README.md
```

## 依赖

截图和渲染质检需要 Python 3.8+、Playwright 与 Chromium。幂等安装脚本会分别验证 Python 包和浏览器可执行文件：

```bash
bash scripts/install_deps.sh
```

如果运行环境不支持截图工具，Skill 会直接交付 HTML 文件。

## 许可证

Apache License 2.0
