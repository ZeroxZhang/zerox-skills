# Architecture Diagram Generator / 架构图生成器

[English](#english) | [中文](#中文)

调用 / Invoke: `/zerox-architecture-diagram`

---

<a id="english"></a>

## Architecture Diagram Generator

A professional architecture diagram generation skill that creates beautiful system architecture diagrams as standalone HTML and SVG files. Based on [Cocoon-AI/architecture-diagram-generator](https://github.com/Cocoon-AI/architecture-diagram-generator).

Repository: [ZeroxZhang/zerox-skills · zerox-architecture-diagram](https://github.com/ZeroxZhang/zerox-skills/tree/main/zerox-architecture-diagram)

### Features

- **Light & Dark Themes** — Switch between white and dark backgrounds
- **Semantic Color Coding** — Consistent colors for frontend, backend, database, cloud, security, AI/ML, observability, and storage components
- **Icon Mode** — Inline SVG icons for common services (AWS, K8s, database, shield, cloud, server)
- **Swimlane / Layer Support** — First-class horizontal lanes for layered architectures (接入层/应用层/数据层)
- **Interactive Tooltips** — Hover tooltips on components via native SVG `<title>` elements
- **Chinese as Default Language** — All labels, titles, and legends use Chinese by default
- **Presentation Mode** — 16:9 aspect ratio optimized for slides and PPTs
- **Deterministic Layout Pipeline** — Text sizing, rank ordering, lane/group packing, port assignment, obstacle-aware orthogonal routing, label placement, and content-derived viewBox
- **Semantic SVG Contract** — Stable IDs and geometry metadata for nodes, routes, labels, lanes, groups, and legends
- **Executable Quality Gates** — Zero-dependency static validator plus optional Chrome-rendered glyph/collision checks
- **Multi-Region / Multi-AZ** — Support for cross-region and multi-availability-zone diagrams
- **Self-contained Output** — Both HTML and SVG files with embedded styles and inline graphics
- **Dual Format** — Generates HTML (full page with cards) and standalone SVG (for embedding)
- **Runtime-independent Output** — Generated files open offline in modern browsers with no JavaScript or remote font/image dependency
- **Professional Typography** — SimHei for Chinese, JetBrains Mono for technical labels
- **Smart Layering** — Arrows render cleanly behind component boxes
- **Bus-style Connections** — Multiple connections from one component share a single exit point
- **Review Mechanism** — Built-in checklist to prevent overlapping, misrouting, and other errors
- **Troubleshooting Guide** — Common mistakes and how to fix them

### Color Palette

| Component Type | Light Fill | Light Stroke | Dark Fill | Dark Stroke |
|---|---|---|---|---|
| Frontend | Light cyan | Cyan-600 | Dark cyan | Cyan-400 |
| Backend | Light emerald | Emerald-600 | Dark emerald | Emerald-400 |
| Database | Light violet | Violet-600 | Dark violet | Violet-400 |
| Cloud/AWS | Light amber | Amber-600 | Dark amber | Amber-400 |
| Security | Light rose | Rose-600 | Dark rose | Rose-400 |
| Cache/Redis | Light purple | Purple-600 | Dark purple | Purple-400 |
| Message Bus | Light orange | Orange-600 | Dark orange | Orange-400 |
| API Gateway | Light cyan | Cyan-600 | Dark cyan | Cyan-400 |
| Container/K8s | Light blue | Blue-600 | Dark blue | Blue-400 |
| AI/ML | Light pink | Pink-600 | Dark pink | Pink-400 |
| Observability | Light teal | Teal-600 | Dark teal | Teal-400 |
| Object Storage | Light indigo | Indigo-600 | Dark indigo | Indigo-400 |
| External | Light slate | Slate-500 | Dark slate | Slate-400 |

### Project Structure

```
zerox-architecture-diagram/
├── SKILL.md              # Skill instructions & design system
├── README.md             # Documentation
├── assets/
│   ├── template.html                 # Standard responsive template
│   └── template-presentation.html    # True 1280×720 template
├── references/
│   ├── layout.md                     # Deterministic layout/routing contract
│   ├── design-system.md              # Theme and component tokens
│   └── quality-gates.md              # Semantic SVG and acceptance rules
├── scripts/
│   ├── extract_svg.py                # Exact HTML → SVG extraction
│   ├── validate_diagram.py           # Static layout validator
│   └── render_check.py               # Optional Chrome rendered check
└── tests/                            # Passing and failing contract cases
```

### How It Works

1. **Requirements** — Resolve theme, language, mode, direction, lanes, and scope
2. **Graph Normalization** — Separate topology ranks, visual lanes, containing groups, nodes, ports, and edges
3. **Layout Planning** — Create a stable-ID ASCII plan before SVG geometry
4. **Layout Pipeline** — Size → rank/order → pack → place → route → label → bounds
5. **Semantic SVG Generation** — Preserve machine-readable IDs, bboxes, routes, and z-order
6. **Extraction & Static Validation** — Extract the exact SVG and run all geometry/parity gates
7. **Rendered Review** — Check actual browser glyph metrics, responsive overflow, and 16:9 clipping

### Validation

```bash
python3 scripts/extract_svg.py output.html output.svg
python3 scripts/validate_diagram.py output.html --strict
python3 scripts/validate_diagram.py output.svg --strict
python3 scripts/validate_diagram.py output.html --compare output.svg --strict
python3 scripts/render_check.py output.html --width 1440 --height 900
python3 -m unittest discover -s tests -v
```

Static validation requires only Python 3. The rendered check is optional and discovers a local Chrome/Chromium binary.

### Output

The skill generates **two** self-contained files:

**HTML file** (`.html`) — Full page with:
- Embedded CSS and inline SVG
- Theme-aware styling (light or dark mode)
- Interactive tooltips on hover
- Summary cards and footer metadata
- Can be opened directly in any browser

**SVG file** (`.svg`) — Standalone vector graphic:
- Extracted from the HTML, no HTML wrapper
- All styles and definitions inlined
- Hover tooltips preserved
- Can be embedded in documents, presentations, or websites
- Scalable to any resolution without quality loss

Both files can be:
- Opened directly in any browser
- Shared with teammates
- Included in documentation
- Printed or exported to PDF
- Hosted on any static site
- Used in presentations (presentation mode)

### Acknowledgements

This project is based on [Cocoon-AI/architecture-diagram-generator](https://github.com/Cocoon-AI/architecture-diagram-generator).

### License

MIT

---

<a id="中文"></a>

## 架构图生成器

一个专业的架构图生成技能，可以创建精美的系统架构图，同时输出 HTML 和 SVG 两种格式的独立文件。基于 [Cocoon-AI/architecture-diagram-generator](https://github.com/Cocoon-AI/architecture-diagram-generator) 优化开发。

项目仓库：[ZeroxZhang/zerox-skills · zerox-architecture-diagram](https://github.com/ZeroxZhang/zerox-skills/tree/main/zerox-architecture-diagram)

### 特性

- **浅色/深色双主题** — 支持白色和深色背景切换
- **语义化配色** — 前端、后端、数据库、云服务、安全、AI/ML、可观测性、存储组件使用一致的配色方案
- **图标模式** — 为常用服务提供内联 SVG 图标（AWS、K8s、数据库、安全盾、云、服务器）
- **泳道/分层支持** — 为分层架构提供原生水平泳道支持（接入层/应用层/数据层）
- **交互式提示** — 通过原生 SVG `<title>` 元素实现组件悬停提示
- **默认中文输出** — 所有标签、标题、图例默认使用中文
- **演示模式** — 16:9 宽高比，针对幻灯片和 PPT 优化
- **确定性布局流水线** — 依次完成文本测量、拓扑排序、泳道/容器打包、端口分配、正交避障路由、标签占位和动态 viewBox
- **语义化 SVG 契约** — 节点、路由、标签、泳道、边界和图例都有稳定 ID 与几何元数据
- **可执行质量门禁** — 零依赖静态校验器，并可选使用 Chrome 检查真实字形和碰撞
- **多区域/多可用区** — 支持跨区域和多可用区架构图
- **自包含输出** — 同时生成 HTML 和 SVG 文件，内嵌样式和图形
- **双格式输出** — HTML（含摘要卡片的完整页面）和 SVG（可嵌入的独立矢量图）
- **产物无运行时依赖** — 生成文件可离线打开，无 JavaScript、远程字体、图片或样式依赖
- **专业排版** — 中文使用黑体（SimHei），技术标签使用 JetBrains Mono 等宽字体
- **智能分层** — 箭头在组件框下方渲染，层次清晰
- **总线式连线** — 同一组件的多条连线共享单一出口点，避免分散
- **审查机制** — 内置检查清单，防止重叠、错连等问题
- **故障排查指南** — 常见错误及修复方法

### 配色方案

| 组件类型 | 浅色填充 | 浅色描边 | 深色填充 | 深色描边 |
|---|---|---|---|---|
| 前端 | 浅青色 | 青色-600 | 深青色 | 青色-400 |
| 后端 | 浅翠绿 | 翠绿-600 | 深翠绿 | 翠绿-400 |
| 数据库 | 浅紫罗兰 | 紫罗兰-600 | 深紫罗兰 | 紫罗兰-400 |
| 云服务 | 浅琥珀 | 琥珀-600 | 深琥珀 | 琥珀-400 |
| 安全 | 浅玫瑰 | 玫瑰-600 | 深玫瑰 | 玫瑰-400 |
| 缓存 | 浅紫色 | 紫色-600 | 深紫色 | 紫色-400 |
| 消息总线 | 浅橙色 | 橙色-600 | 深橙色 | 橙色-400 |
| API 网关 | 浅青色 | 青色-600 | 深青色 | 青色-400 |
| 容器/K8s | 浅蓝色 | 蓝色-600 | 深蓝色 | 蓝色-400 |
| AI/ML | 浅粉色 | 粉色-600 | 深粉色 | 粉色-400 |
| 可观测性 | 浅青色 | 青色-600 | 深青色 | 青色-400 |
| 对象存储 | 浅靛蓝 | 靛蓝-600 | 深靛蓝 | 靛蓝-400 |
| 外部 | 浅石板灰 | 石板灰-500 | 深石板灰 | 石板灰-400 |

### 项目结构

```
zerox-architecture-diagram/
├── SKILL.md              # 技能指令与设计系统
├── README.md             # 说明文档
├── assets/
│   ├── template.html                 # 标准响应式模板
│   └── template-presentation.html    # 真正的 1280×720 模板
├── references/
│   ├── layout.md                     # 确定性布局与路由契约
│   ├── design-system.md              # 主题和组件视觉规范
│   └── quality-gates.md              # 语义 SVG 与验收规则
├── scripts/
│   ├── extract_svg.py                # 精确提取 HTML 内联 SVG
│   ├── validate_diagram.py           # 静态布局校验器
│   └── render_check.py               # 可选 Chrome 实渲染检查
└── tests/                            # 通过与失败用例
```

### 工作原理

1. **需求确认** — 明确主题、语言、模式、方向、泳道和范围
2. **图模型规范化** — 拆分拓扑 rank、视觉 lane、容器 group、节点、端口和边
3. **布局规划** — 在 SVG 几何前创建稳定 ID 的 ASCII 计划
4. **布局流水线** — 测量 → 排序 → 打包 → 放置 → 路由 → 标签 → 边界
5. **语义 SVG 生成** — 保留可机器读取的 ID、bbox、路由和 z-order
6. **提取与静态校验** — 精确提取 SVG，并执行几何与一致性门禁
7. **浏览器实渲染检查** — 验证真实字形、响应式滚动和 16:9 裁切

### 验证命令

```bash
python3 scripts/extract_svg.py output.html output.svg
python3 scripts/validate_diagram.py output.html --strict
python3 scripts/validate_diagram.py output.svg --strict
python3 scripts/validate_diagram.py output.html --compare output.svg --strict
python3 scripts/render_check.py output.html --width 1440 --height 900
python3 -m unittest discover -s tests -v
```

静态校验只需要 Python 3；实渲染检查为可选项，会自动发现本机 Chrome/Chromium。

### 输出

技能生成**两个**自包含文件：

**HTML 文件**（`.html`）— 完整页面，包含：
- 内嵌 CSS 和 SVG
- 主题感知样式（浅色或深色模式）
- 悬停交互式提示
- 摘要卡片和页脚元数据
- 可直接在浏览器中打开

**SVG 文件**（`.svg`）— 独立矢量图：
- 从 HTML 中提取，无 HTML 外壳
- 所有样式和定义内联
- 保留悬停提示
- 可嵌入文档、演示文稿或网站
- 任意缩放不失真

两个文件都可以：
- 直接在任何浏览器中打开
- 与团队成员分享
- 嵌入到文档中
- 打印或导出为 PDF
- 部署到任何静态站点
- 用于演示文稿（演示模式）

### 致谢

本项目基于 [Cocoon-AI/architecture-diagram-generator](https://github.com/Cocoon-AI/architecture-diagram-generator) 开发。

### 许可证

MIT
