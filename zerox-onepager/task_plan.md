# Onepager 产品级深度 Review 计划

## 目标

从产品设计与产品价值层面对 Onepager 做第二轮深度 Review，并结合 GitHub 优秀同类项目进行横向比较，输出可执行的产品路线建议与 PDF 报告。

## 研究范围

- 纵向：项目从模板生成器到内容智能、类型系统、风格系统、质量门禁的演进。
- 横向：GitHub 上的同类开源产品，重点覆盖 AI 海报/信息图、Markdown 到视觉内容、HTML/截图生成、Agent Skill 等相邻赛道。
- 产品层：目标用户、核心任务、价值主张、首次体验、交互成本、输出可信度、差异化、可扩展性、传播与增长。
- 不重复上一轮代码执行和质控细节，除非它们直接影响产品价值。

## 阶段

- [x] 建立研究范围和纵向假设
- [x] 收集 GitHub 同类项目与一手资料
- [x] 建立竞品分层与对比矩阵
- [x] 完成产品价值、体验和战略诊断
- [x] 输出 Markdown 与 PDF 深度报告
- [x] 校验来源、文件和最终结论

## 初始假设

1. Onepager 当前更像“高质量设计规范包 + Agent 工作流”，尚未形成清晰的产品入口。
2. 九风格、四类型、四尺寸、三密度的组合丰富，但配置复杂度可能吞噬“一句话生成”的核心价值。
3. 竞争壁垒不应是模板数量，而应是“内容理解 → 可控设计 → 可验证交付”的稳定闭环。
4. GitHub 同类项目可能分别赢在易用性、生态、交互式编辑、模板社区或结构化图表，Onepager 需要选择明确生态位。

## 错误记录

| 错误 | 处理 |
|---|---|
| GitHub Issues API 返回限流/错误对象，原解析脚本按数组处理失败 | 不重复调用；改用已获取的一手 README、搜索结果和公开 Issue/PR 定向页面 |
| Onepager GitHub API 元数据请求受限，字段为空 | 不将 Onepager Stars 用于关键结论；纵向数据以本地 Git 为准 |
| PDF 转换脚本缺少 `markdown` 与 `weasyprint` | 按 hv-analysis 环境要求安装后重试 |
| WeasyPrint 缺少 macOS 系统库 `libgobject-2.0-0` | 保留脚本生成的排版 HTML，改用已验证的 Playwright/Chromium 打印 PDF，避免修改系统包管理器 |

## P0 开发状态

- [x] 确认保留 `A/B/C/T/E/F` 核心交互协议
- [x] 内容蓝图 Schema 与示例
- [x] Onepager IR v1 Schema 与示例
- [x] Manifest v1 Schema
- [x] 项目初始化与源文件归档
- [x] 构建版本递增
- [x] 双质检 PASS 后记录构建
- [x] SHA-256 与工具版本校验
- [x] Skill、README、CHANGELOG 与报告同步
- [x] 单元测试和端到端 CLI 演练
