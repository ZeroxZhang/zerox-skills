# zerox-skills — 商业专业报告生产技能套件

把管理咨询、商业分析、市场调研、行业研究、投融资尽调、市场营销这些场景背后的同构价值链——**调研取证 → 建模分析 → 论证成线 → 表达成文 → 视觉呈现 → 交付质检**——沉淀为可独立调用、可组合、可路由的 skill。让下一份报告是积木重组，而不是从零重走。

## 双层结构

```
      /zerox  路由（意图识别 → 候选筛选 → 编排提示词）
              │
   ┌──────────┴──────────┐
   场景流水线层（5）        能力层（6）
   行业研究 · 市场调研      调研 · 分析 · 论证
   尽调 · deck · 营销方案   表达 · 视觉 · 质检
```

流水线 skill 端到端产出一类报告；能力 skill 专注价值链一段，可单独触发、单独迭代。编排只发生在 `zerox` 与流水线层，能力 skill 之间不互相指名。

## 目录导航

| 路径 | 作用 |
|---|---|
| `AGENTS.md` | 套件内硬规则（布局、契约、登记、边界） |
| `registry.md` | 成员注册表——槽位与状态的唯一真源 |
| `docs/architecture.md` | 架构决策：为何双层、路由契约、方法归属、增长原则 |
| `docs/skill-authoring.md` | skill 编写规范（命名 / frontmatter / 解剖 / 组合 / 验证） |
| `docs/roadmap.md` | 生长顺序与触发条件 |
| `templates/skill-template/` | 新 skill 脚手架 |
| `templates/task-contract.md` | 开工前任务契约模板 |

## 怎么用

当前仅骨架，尚无 skill 实体。成员就位后：

- 有明确交付物（「做一份行业研究报告」）→ 直接 `/zerox-<流水线>`
- 不确定该用哪套 → `/zerox`，它给出可直接发送的编排提示词
- 只要单点能力（只要图表选型、只要质检）→ `/zerox-<能力>`

套件外另有 4 个 `zerox-*` 个人 skill（`zerox-swarm`、`zerox-mp-writting`、`zerox-content-advisor`、`zerox-workflow-conventions`），共享品牌前缀但**不属套件**；成员资格以 `registry.md` 为准。

## 怎么新增 skill

1. 对照 `registry.md` 确认槽位与职责边界（没有槽位先补表再动手）
2. `cp -r templates/skill-template zerox-<name>`，把 `skill-skeleton.md` 改名为 `SKILL.md`，按 `docs/skill-authoring.md` 填实
3. `registry.md` 翻「已建」并填路径，`bridge-skill.sh link` 整套接入，按四级验证验收

**禁止先建壳后填肉**：目录出现时 SKILL.md 必须已有可执行行为。生长顺序见 `docs/roadmap.md`。

## 与既有技能的关系

`consulting_deck_skill`、`consulting-report-forge`、`consulting-report-skill` 三套既有报告管线**不迁移、不依赖、不调度**，只作设计参考（方法契约、交付契约、截图式视觉验收）。本套件全新构建全链路。
