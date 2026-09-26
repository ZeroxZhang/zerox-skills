# 生长路线

## 总原则

- **真实任务驱动**：skill 由反复出现的真实问题催生。`registry.md` 里的槽位是占座，不是待办清单。
- **禁止空壳**：一个 skill 目录出现时，其 SKILL.md 必须已有可执行行为。一次只养一个。
- **失败驱动修改**：每次真实任务后回填对应能力层 `references/`，改动能解释一类稳定失败。

## 阶段 0（已落地）：骨架与规则

AGENTS / README / registry / docs / templates 就位，13 个槽位全部「规划中」，零技能实体。

## 阶段 1：能力层（按触发条件择机，不按清单顺序）

| 顺序 | skill | 触发条件 | 可参考的既有资产（只读） |
|---|---|---|---|
| 1 | `zerox-deep-research` | ✅ **已建**（2026-09-26） | forge 的 `evidence-ledger.md` |
| 2 | `zerox-storyline` | 出现第一个需要成篇论证的任务 | deck 的 `storyline_method.md` |
| 3 | `zerox-visual` | 出现第一个要交付 HTML+PDF 的任务 | deck 的 `chart_matching.md` / `typography_system.md` / `page_frame.md` |
| 4 | `zerox-writing` | 成篇后措辞与摘要成为瓶颈 | — |
| 5 | `zerox-analysis` | 出现第一个需要框架建模与反证的任务 | — |
| 6 | `zerox-qa` | 交付前检查成为瓶颈（截图验收可提前并入 visual） | deck 的视觉 QA 纪律 |

调研、论证、视觉先行的理由：它们是所有报告的共用地基，方法文档也最可复用。

## 阶段 2：路由 `zerox`

**触发条件：已建成员 ≥2**（否则路由无候选可筛，是空壳）。建路由时写 manifest 解析脚本，并烘焙回退快照 `zerox/references/skill-names.txt`。

## 阶段 3：场景流水线

**触发条件：能力层已建 ≥3 且出现真实端到端报告任务。** 首个建议 `zerox-industry-report`（最通用，能压测全链）；其余四个按真实任务频次排序插入：

| skill | 场景 | 主要串用 |
|---|---|---|
| `zerox-industry-report` | 行业研究 | 全链六段 |
| `zerox-market-research` | 市场调研 | 全链，强调规模测算 |
| `zerox-dd-report` | 投融资尽调 | 强调证据台账与反证 |
| `zerox-consulting-deck` | 咨询汇报 deck | 强调论证→视觉 |
| `zerox-marketing-plan` | 营销方案 | 强调调研→论证→表达 |

商业分析（经营复盘 / 方案对比 / 问题诊断）暂不设独立槽位；出现高频真实任务时再补。

## 维护节奏

- 每次真实任务后回填 `references/`；`registry.md` 状态同步。
- 定期用四级验证回归；发现结构性问题按全局原则 6 一次性解决整类。
