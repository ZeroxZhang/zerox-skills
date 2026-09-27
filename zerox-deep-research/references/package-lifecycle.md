# 研究包布局与生命周期

## 版本与目录

新 L2/L3 包使用 `package.json` 的 `schema_version: 2`；这是包格式版本，不是技能版本。模板见 `../assets/package-template.json`。按实际用途创建目录，不预建空壳。

```text
research/<日期>-<主题>/
├── package.json             # 格式版本、数据/检索适用性
├── README.md                # 阅读、数据复用、核验入口
├── report.md                # 主报告
├── sources.md               # 来源索引
├── manifest-sha256.txt      # 封包时最后生成
├── raw/                     # 原始证据，采集后不改
│   ├── sources/             # 快照
│   ├── files/               # 原始附件，只存一份
│   └── user-provided/       # 用户原件副本
├── data/                    # 数据集目录、字典、extracted/、curated/
├── notes/                   # 证据摘录、冲突与判断
├── analysis/                # 数据转换、计算、采用规则与复跑说明
├── work/                    # 可更新的过程文件
│   ├── brief.md             # 唯一任务契约
│   ├── plan.md              # 研究进度
│   ├── tasks/               # 有子代理时
│   └── search-logs/         # 实时追加的检索日志
└── qa/                      # 人工复核与机器检查结果
```

`raw/` 只读指采集后不改正文；新增来源用新 ID，原件不复制到 data。work 持续更新、data/notes/analysis 可修订；封包后变更须走新版本。原始采集 ID 不复用，capture_source.py 会拒绝覆盖。

所有机器路径字段以包根为基准；Markdown 链接相对所在文档。不可含绝对路径、`..` 或符号链接的规则只针对机器路径字段；data/README.md 的人工导航可使用 `../sources.md` 等正常相对链接。

## 开题与执行

1. 选输出位置、创建 package.json 和 work/brief.md；brief 同时是套件任务契约，不另维护第二份。
2. 声明数据适用性。`available` 表示本次承诺交付数据，执行中尚未有数据时自动检查失败是预期；只有证明确实无法获得才改为 unavailable 并更新契约。
3. 搜索执行时标 `search_status=performed`；无联网/仅用户给定材料且未进行检索时用 not_applicable，必须说明原因且不创建空日志。非检索活动可写 work/activity.md。
4. 迭代更新来源、数据、笔记和缺口；每轮可运行自动检查，不必等全文完成后才发现格式偏离。
5. 脚本路径以下均相对技能目录，不是研究包目录。

## 验收与封包

**自动检查不等于内容可信，也不等于可以交付。**

1. 完成 report、数据、notes、work 状态与 README 叙述。README 保留且只保留一组 `<!-- package-stats:start -->` / `<!-- package-stats:end -->`，标记外不另手填来源数或“检查通过”。
2. `python scripts/check_package.py <包> --json`：只读检查，错误须修复。PASS_AUTOMATED 仅表示实际覆盖的机器检查通过。
3. 按 quality-checklist 做人工核验（可由执行 Agent 或独立审稿 Agent 完成），保存 `qa/review.json`。四项：问题回答、证据支撑、数据口径与计算、假设局限；每项都要有实际核验位置与理由。无数据时 data_semantics 应复核不适用/不可得理由，不能跳过。
4. 人工核验完成后运行 `python scripts/check_package.py <包> --review-digest`，把指纹写入 review 的 reviewed_digest。指纹本身不是复核证据，不能拿到指纹就自动填通过。
5. `python scripts/check_package.py <包> --write-manifest`：先验收；失败不写文件。通过后依次更新 README 机器统计、生成 qa/checks.json、最后生成 manifest。旧格式禁止封包。工作计划中“打包交付”的最终状态以 qa/checks.json 和清单验证为准，不封包后再改计划。
6. `python scripts/check_package.py <包> --final`：只读验证当前包、人工复核绑定、检查记录和完整清单。通过后在包目录之外生成 ZIP，ZIP 不放回包内。

内容指纹覆盖 raw、data、report、sources、notes、analysis、work、package.json 等；排除 README、qa/review.json、qa/checks.json 和清单以避免生成循环。最终清单覆盖除自身外全部文件，README、复核与检查记录也在其中。哈希用于检测变化，不证明来源真实性或防伪签名。

没有代码执行能力时按相同契约人工核验，明确标为“未完成自动检查/未封包”，不能编造 PASS 或校验清单。没有文件写入能力时说明无法交付数据文件与材料包。

## 旧包、断点恢复与后续版本

- 无 package.json：识别为 legacy v1，按旧路径只读诊断，显式报告未解析文件、元数据错误和覆盖缺口；不创建文件、不移动路径、不自动升级。
- 自动检查 v1 的通过只描述旧版已执行检查，不能宣称符合 v2；`--write-manifest` 和 `--final` 均拒绝将其认证为 v2。
- 需要迁移旧包时作为单独任务：保留旧目录，用副本转换布局与链接，保留原始证据字节，再补数据和验收；不得伪补历史原文。
- 未封包的同一任务允许续跑；先读版本、work/plan、sources、数据目录和检索日志，再从现有最大 ID 继续。
- 已封包的后续修订：保留交付版，新建带 `-r2` 等后缀的工作副本，package.json 填新 package_id 和 supersedes（旧包 ID），重新执行自动与人工核验。在新工作副本中移除旧 manifest 与 qa/checks，重置人工复核，旧交付版保持不变。封包命令拒绝覆盖已有清单。
