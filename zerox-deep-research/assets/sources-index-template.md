# 来源索引

<!--
由主线程维护。内容以各快照的元数据头为准，两者不一致时改索引来对齐快照。
子代理不直接改本文件（并行写入会冲突），只把来源 ID 清单回传主线程。
-->

| ID | 标题 | 作者/机构 | 发布 | 访问 | 层级 | 可信度 | 完整度 | 采集方式 | 本地文件 | URL | 引用号 | 备注 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| M001 | 示例标题 | 某机构 | 2025-03-15 | 2026-09-26 | 一手 | A | full | script | `raw/sources/M001-example.md` | https://example.com/a | [1][3] | |
| U001 | 用户材料：访谈记录 | 内部 | 2026-09-01 | 2026-09-26 | 一手 | — | full | script | `raw/user-provided/interview.md` | file: …/interview.md | [2] | 内部资料 |

列说明：

- **层级**：一手 / 二手 / 三手（对应快照 `source_type` 的 primary / secondary / tertiary）
- **可信度**：A / B / C，见 `../references/source-evaluation.md`；用户材料写 `—`
- **完整度**：full > partial > summary > snippet-only > metadata-only
- **采集方式**：script / browser / fetch-tool / snippet / metadata-only
- **引用号**：该来源在 report.md 中被哪些编号引用；未被引用写 `—`
- **备注**：重复合并、supersedes、付费墙、内部资料等
