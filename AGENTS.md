# zerox-skills 套件规则

## 规则来源

- 全局行为规则以 `../AGENTS.md` 的「Global AGENTS.md」段为唯一 canonical；先读该文件再读本文件。本文件只补充套件范围内规则，不复制全局正文。
- 套件的结构事实、成员状态与契约，以本目录的 `registry.md`、`docs/`、`templates/` 为准，不依赖记忆推断。

## 本套件是什么

商业专业报告生产的技能套件真源，隶属 `../`（my_own_skills 统一管理根）。把「调研取证 → 建模分析 → 论证成线 → 表达成文 → 视觉呈现 → 交付质检」这条价值链沉淀为可独立调用、可组合的 skill：双层切分（能力层 + 场景流水线层）+ 独立路由。

## 布局硬规则

- 技能真源必须是本目录的**直接一级子目录**（`bridge-skill.sh` 集合识别只匹配 `<套件>/<成员>/SKILL.md` 一层），不得加 `skills/` 中间层。
- 目录名 == frontmatter `name`；小写英文、数字、连字符，少于 64 字符。
- 命名空间：路由 `zerox`，成员一律 `zerox-*`。套件成员资格以 `registry.md` 为准，**不靠前缀判定**（套件外另有 4 个 `zerox-*` 个人 skill 共享此前缀）。
- `docs/`、`templates/`、`registry.md`、`README.md`、`AGENTS.md`、`CLAUDE.md` 不是技能；模板内不得出现名为 `SKILL.md` 的文件。

## 成员契约摘要

完整规范见 `docs/skill-authoring.md`，此处只列硬约束：

- 叶子 skill 禁止指名、调用或引导用户去跑兄弟 skill；跨 skill 只允许**只读** `../zerox-<能力>/references/` 下的方法文档，不复制正文。
- 叶子收尾只保留条件式路由提示（「若还需…，回到 `/zerox` 重新编排」）。编排只发生在路由 `zerox` 与场景流水线层。
- 组合上限：1 主 + ≤2 辅（前置筛选 / 证据补充 / 验收约束）；单一任务、单一交付物，禁止多份报告拼接。
- 动工前先写任务契约（`templates/task-contract.md`），验收以契约为准；需求变更先改契约再改产出。
- 与套件外同前缀 skill（`zerox-swarm`、`zerox-mp-writting`、`zerox-content-advisor`、`zerox-workflow-conventions`）易混时，description 必写边界句消歧。

## 登记与同步

- 新 skill 落地 = 目录就位 + `registry.md` 对应行翻「已建」并填路径 + 整套接入：

  ```bash
  ~/.claude/skills/dbs-bridge/scripts/bridge-skill.sh link /Volumes/Out/my_own_skills/zerox-skills
  ```

- 父级 `my_own_skills_manage.md` 只登记套件整体一条，成员不逐个登记。
- `registry.md` 与实际目录必须保持一致；增删成员同步改表。

## 维护

- 禁止建空壳：一个 skill 目录出现时，其 SKILL.md 必须已有可执行行为；空目录、占位 README、changelog 一律不建。
- 同类问题反复出现时，按全局「核心理性约束原则 6」先定位层级（结构 / 约定 / 抽象），一次性解决整类问题，不逐个打补丁。
- 修改必须能解释一类稳定失败；随真实任务回填 `references/`，不为装饰写文档。

## 边界

- 不迁移、不修改、不依赖既有三套报告管线（`consulting_deck_skill`、`consulting-report-forge`、`consulting-report-skill`）；它们只作设计参考（方法契约、交付契约、截图式视觉验收）。
- 路由只调度套件内成员（自研闭环），不跨调度套件外 skill（含同前缀的 4 个个人 skill）。

## 当前状态

首次落地仅骨架与规则，无技能实体。槽位版图见 `registry.md`，生长顺序见 `docs/roadmap.md`。
