# 可选专家接入

日常选型在 S3 按[图表选型](charts.md)完成，不需要独立 planner、plan JSON 或额外交接。用户指定 echarts-viz-planner，或作者比较候选后仍无法解决实质性取舍时，才使用本页；重复图型本身不是调用条件。

## 读取与使用

`node scripts/load_viz_planner.cjs --planner /实际/planner/目录` 校验本地资源并返回 `skill_file`、`skill_root` 与 `source_sha256`；省略路径时只找已有安装。加载器不联网、不解包、不写缓存、不同步其他技能。资源不可用时继续本技能内置选型，只有本次确实尝试且失败才写 `planner.mode: unavailable`。

实际读取返回的 `SKILL.md` 及其必要引用，以 `mode: api`、`contract_version: "1.1"`、`output_level: decision` 交接。给真实输入文件及摘要、读者任务、分析发现、来源定位、口径与未知、相邻论证、实际绘图区，以及 `static: true`、`offline: true` 和实际运行依赖。数据变换用 `transform_policy: propose`，由作者核对后落实到统一数据。

读取实际规格、理由、备选胜出条件和限制，不只读 summary。缺证据就补证或收窄；无现成组件时按语义用 SVG／HTML 实现。专家建议不接管整页设计，也不改变本技能的字体、主题与交付要求；选型参与者不算独立成稿复核者。

## 已采用的结果如何核对

实际采用后保留 plan，运行该 planner 的 `scripts/validate_plan.py plan.json --schema`；`task.json` 的 `planner` 写 `used` 并绑定 record，字段见[交付契约](delivery.md)。record 包含：

- `data: {path, sha256}`，`planner: {root, sourceSha256}`，`plans: [{path, sha256}]`；路径相对 record，根目录与摘要取真实加载结果。
- `pages` 中保留页码、`proves`、`roles`、`readingOrder`、`alignment`、所用 `plan` 下标及 `relationships: [{selector, minCount, meaning}]`。直接制作的页写 `directReason`。

plan 的 `data.ref` 与 `data.sha256` 必须指向同一冻结输入；数据、plan、record 或已采用的 planner 源码变化后，重核关系并更新绑定，再装配、QA、审查。既有记录缺失不能改填 `direct`。加载成功不等于执行了选型，schema 和可见图元检查也不证明选型或成稿质量。
