# Onepager 产品研究发现

## 当前产品纵向

- 2026-03-20 首次提交，定位为 OnePage Generator Skill。
- 早期阶段集中于目录结构、命名、风格和展示图。
- 2026-04 增加内容智能、类型差异化、视觉标准、质量检查、A4、署名和命名规则。
- 2026-05 增加 B9 Google Native、T4 海报和视觉放大器，随后围绕“规范驱动还是原则驱动”发生多次提交与回滚。
- 当前产品形态由 `SKILL.md + references + HTML 模板 + Python 截图/质检脚本` 组成，没有独立 GUI、在线编辑器、模板市场或结构化中间格式。

## 待验证判断

- `A/B/C/T/E/F` 已被确认是便于用户选择的核心交互协议；优化目标是推荐理由、组合回复和状态持久化，不是隐藏菜单。
- 产品是面向“不会设计的人”、内容创作者、开发者，还是 Agent 平台用户，目前是否混杂。
- HTML/PNG 双交付是否足够，还是缺少可编辑的结构化产物。
- 风格规范是否构成壁垒，还是易被其他 Prompt/模板复制。
- GitHub 同类项目分别在哪个产品环节占据优势。

## 来源

- 本地 Git 历史与当前仓库文件，访问时间：2026-08-08。

## 初步竞品分层

### A. AI 直接生成信息图

- `arunenoah/AI_Inforgraphic_gen`：浏览器产品，Claude 生成可编辑 HTML，Gemini 直接生成 PNG；提供历史记录、成本统计、参考图和多布局。
- `ryanbaumann/infographic-agent`：两 Agent 管线，将内容准备与视觉生成分开，并提供独立 Skill 包。
- 优势：首次结果快，视觉表现自由。
- 弱点：文字准确性、稳定复现和局部编辑依赖具体模型。

### B. Markdown / 结构化内容转视觉

- `xiaolinbaba/xiaolin-madopic`：浏览器静态应用，实时预览，支持 Markdown、Mermaid、ECharts、KaTeX、卡片语法和 PNG/PDF/HTML 导出。
- `uhhc/md2card`：Markdown/JSON 双输入，自动分页，面向简报、公众号与小红书批量卡片。
- `iotate/infomagic`：桌面应用，先生成可编辑大纲，再分页生成图片，支持模板参考、批量重生成和 PDF。
- 优势：编辑闭环清晰、输出稳定、用户知道如何修改。
- 弱点：设计自由度通常受模板约束。

### C. Agent Skill / 设计工作流

- `Astralune-ai/Astra-graphic`：AI 直接生成与 HTML 精确布局双引擎，并将品牌资产抽成中央 `brand.json`。
- `arnaugonzalez/infographic-post-skill`：多后端生成、离线 fallback、质量审计、测试和发布文档较完整。
- `tengj/article-poster-generator`：针对“长文章拆成 5-8 张社媒海报”这一单一任务，产品价值非常明确。
- Onepager：设计规范和内容重构深度突出，但入口、目标用户和可编辑工作流较模糊。

## 初步产品判断

1. Onepager 目前的真正卖点不是“九种风格”，而是“把复杂内容转成经过结构化思考的一页视觉表达”。
2. 当前配置菜单把内部设计模型暴露给用户，用户先做六项设计决策才能得到结果，削弱了 Agent 产品应有的低摩擦体验。
3. HTML 是可编辑的技术产物，但不是可编辑的产品体验。用户缺少局部改文案、锁定模块、换一个布局、保留品牌等可感知能力。
4. 竞品正在形成“双引擎”共识：需要精确文字时走 HTML/SVG，需要高视觉表现时走图像模型。Onepager 只有精确布局路线。
5. 品牌复用、项目历史、模板/配方保存和批量系列化，是从一次性生成工具走向持续使用产品的关键。

## GitHub 规模快照（2026-08-08）

| 项目 | Stars | Forks | 产品信号 |
|---|---:|---:|---|
| `slidevjs/slidev` | 48,005 | 2,142 | 文本驱动视觉工具可以通过组件、主题、插件和社区形成平台 |
| `marp-team/marp` | 12,317 | 291 | “Markdown 即源文件”带来版本控制、可移植和多端生态 |
| `antvis/Infographic` | 5,688 | 440 | AI 友好 DSL + 约 200 模板 + SVG + 编辑器，是当前最强直接对标 |
| `xiaolinbaba/xiaolin-madopic` | 206 | 47 | 实时预览和丰富内容语法对个人创作者有明确吸引力 |
| `tengj/article-poster-generator` | 22 | 3 | 单一场景定位比泛化能力更容易被理解 |
| `uhhc/md2card` | 3 | 1 | Markdown/JSON 中间结构、自动分页、批量导出是可复用产品能力 |
| `arunenoah/AI_Inforgraphic_gen` | 2 | 0 | 双生成路线、历史/成本/参考图是完整产品工作台的雏形 |
| `Astralune-ai/Astra-graphic` | 1 | 1 | 品牌库和双引擎体现持续内容生产需求 |

数据来自 GitHub REST API，访问时间 2026-08-08。Stars 是时间点快照，不作为产品质量的单一判断。

## 关键横向洞察

### AntV Infographic 是最重要的直接参照

- 把 AI 输出从最终图片提升为可解析 DSL，解决了“修改一句话却要整张重生成”的问题。
- DSL 同时面向人和模型：比 HTML/CSS 更短、更稳定、更适合流式生成。
- 约 200 个模板不是简单风格数量，而是按时间线、比较、层级、流程等信息结构组织。
- 默认 SVG 使缩放、局部编辑和嵌入业务系统成为自然能力。
- 内置编辑器把“AI 生成之后怎么办”纳入产品，而 Onepager 目前把这个问题交给用户直接编辑 HTML。

### 大型相邻产品共同证明了“源文件”的价值

- Marp/Slidev 的核心不是主题数量，而是 Markdown 作为稳定源文件，加上可扩展主题、组件和导出生态。
- Onepager 当前没有比 HTML 更高层的中间产物。HTML 同时承担语义、布局和渲染，导致复用、局部修改、模板迁移和多尺寸适配都要重新让模型改代码。
- 若没有 Onepager IR/DSL，未来每增加一种导出格式或编辑能力，复杂度都会继续堆进 Prompt 和 HTML。

### 竞品对“生成后工作流”的投入明显高于 Onepager

- InfoMagic：大纲可编辑、分页、单页重生成、批量生成、PDF。
- Madopic：实时预览、本地草稿、图表/公式/图示、PNG/PDF/HTML。
- AI Infographic Generator：历史记录、成本、失败记录、参考图、多模型。
- Onepager：首次生成前配置很重，生成后的局部迭代仍依赖自然语言和完整 HTML 重写。
