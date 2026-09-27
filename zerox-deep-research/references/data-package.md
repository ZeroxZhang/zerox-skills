# 数据资产契约

## 何时读取

开题定义数据需求、从材料提取记录、合并研究线、计算或验收数据时读取。数据包是同一研究交付中的可复用资产，不是第二份报告。

## 开题先定一行代表什么

在 `work/brief.md` 列出数据集主题、行粒度、字段、对象/时间/地域覆盖、来源要求、缺口处理和验收标准。数据需求先于大规模检索；每轮研究同时更新证据与数据，不能报告写完再反向凑表。

- 数值研究：公司年度收入、市场份额、用户规模等，必须区分主体、口径、期间、币种与单位。
- 定性研究：文献编码、政策事件、竞品功能、访谈主题，同样是一组可复用记录，不强制数字化。
- 有部分缺口：`data_status=available`，保留已获得数据，并把缺口列为记录或写入覆盖说明。
- 完全不可获得：`data_status=unavailable`，在 `package.json` 和 brief 写明尝试与限制；不能用空表冒充数据交付。
- 不适用：`data_status=not_applicable`，写明为什么结构化记录无助于本任务，不创建空壳目录。

## 文件分工与唯一真源

- 原始下载、API 响应、原始工作簿：`raw/files/`，用户材料副本：`raw/user-provided/`。原件只存一份，来源快照记录其路径与来源 ID。
- `data/extracted/`：按来源提取，保留原始表达和精确定位。不同来源的不同数值分别保留，不能平均或覆盖。
- `data/curated/`：统一单位、选择口径、计算、编码后的可用表。只通过输入记录 ID 追溯，不维护第二份来源映射。
- `analysis/`：转换脚本、算式、选择/排除理由、复跑步骤与依赖。结果表统一进入 `data/curated/`，不再散放 `analysis/`。
- `data/datasets.json`：数据集目录的机器真源；`data/README.md` 是它的阅读说明，不另维护手填行数。
- `data/dictionary.csv`：每个数据集的每一列必须定义。CSV 使用 UTF-8，标准引号转义，空字符串表示缺失，不能用 0 代替缺失。

表头起步可用 `../assets/data-records-template.csv` 和 `../assets/data-dictionary-template.csv`；按主题增减业务字段，公共字段不能删除。数据说明使用 `../assets/data-readme-template.md`。模板不等于已完成数据集，不能把只有表头的文件作为交付。

CSV 是默认可验收格式。可附 Excel 阅读版或 Parquet 大数据文件，须在数据 README 说明由哪些规范 CSV/原件生成，不能把这些附件当作自动检查已覆盖的数据。规模不适合 CSV 时先改任务契约和验收方法，报告未覆盖项。

## 数据集目录

`data/datasets.json` 为数组，每项必填：

| 字段 | 含义 |
|---|---|
| `id` | 包内唯一数据集 ID，如 `revenue-extracted` |
| `path` | 相对包根路径，如 `data/extracted/A-revenue.csv` |
| `stage` | `extracted` / `curated`，必须与路径相符 |
| `grain` | 每一行精确定义，如“某来源对某主体某年度收入的一项估计” |
| `coverage` | 实际覆盖对象、期间、地区；与开题要求的缺口 |
| `limitations` | 方法、来源、可比较性限制；没有已知限制写 none |

目录只登记实际非空 CSV，禁止占位行。模板见 `../assets/datasets-template.json`。

## 记录公共字段

每张表必须有以下字段。业务字段按主题增加，不把所有研究塞成收入表。

| 字段 | 规则 |
|---|---|
| `record_id` | 包内全局唯一、稳定，不因排序重编号；建议 `A-R0001`，主线程 `M-R0001` |
| `value` | 可供复用的值；数值不混写单位；区间用分别定义的上下界记录/列，不伪造点估计 |
| `value_type` | `number` / `string` / `boolean`；布尔值只用 true/false |
| `value_origin` | `reported` 原始披露/原话、`estimate` 外部估计、`derived` 本次计算或推断；不等于置信度 |
| `status` | `present` / `missing` / `unavailable` / `not_applicable` |
| `source_id` | 提取层有值记录必填，关联来源快照；整理层留空 |
| `source_locator` | 提取层有值记录必填：页码/表号/单元格/API 字段路径/原文段落；整理层留空 |
| `original_value` | 提取层有值记录必填，保留来源原始表述，例如“约 12 亿元”；不能拿模型摘要冒充原文 |
| `input_ids` | 整理层必填，以分号分隔的输入记录 ID；提取层留空 |
| `method` | 整理层必填，指向 `analysis/` 中脚本或算式说明的包内相对路径；提取层留空 |

补充规则：

- 数值记录必填 `entity,metric,unit,period,geography,scope`，不能识别的写 unknown 并说明限制；不能靠 unknown 绕过关键口径核验。
- 非 present 记录：`value` 为空，增加 `missing_reason`；标明未披露、找不到、受限或不适用，不填假数字。数据字典说明哪些字段可空。
- 定性记录：增加对象、编码维度、事件日期等领域字段。人工归类属于本次推断，整理层标 derived，方法中保留编码标准与歧义。
- 同源转载不算独立验证；来源关系和独立性判断写入 notes，不因有多条记录就提高置信度。
- 有冲突/筛选时：在方法中逐条说明输入记录的采用/排除理由，未采用数据仍留在 extracted。需要表内筛选时增加 `selection`、`selection_reason` 并写入字典。
- 统一币种、单位、期间或做计算属于 derived；纯筛选、原样选用可保留 reported/estimate，但同样须有 input_ids 和 method。
- 整理记录不得自引用或循环依赖。不可用输入不能推出 present 结果；情景假设应另写成明确标注的假设记录与依据，不能把缺失数据偷偷补成事实。

## 数据字典

`data/dictionary.csv` 列为：`dataset_id,field,type,description,unit,missing_rule`。

每个字段一行；type 为 string/number/boolean。`value` 列可定义为 string，由每条记录的 value_type 检查实际类型。无单位写 `n/a`；缺失规则用自然语言说明。脚本检查字典覆盖、类型和基础缺失规则，业务语义由人工复核。

## 报告与复核

报告中的关键数据追加 `[数据:A-R0001](data/extracted/A-revenue.csv)`，派生数字引用整理记录；同时保留原有来源引用 `[1]`。不要将每一个日期都机械视作指标；人工复核应覆盖影响结论的数字、比较、分类和矩阵。

机器能检查记录存在、路径、字段、输入关系、循环与基础类型，不能证明数字抄对、来源独立、口径可比或算式正确。人工从报告逐条回查关键数据；计算需要实际复跑或独立代入算式，对照结果并记录位置。只允许运行本次编写并审查过的分析脚本，不执行下载原件中的代码。

## 交接、续跑与独立导出

- 子代理只写本线 `data/extracted/<代号>-*.csv`，把数据集元信息与字段定义放入本线 `work/tasks/<代号>-data.json` 回传；主线程合并 datasets.json、dictionary.csv 与 curated，检查重复与分歧。
- 一条提取记录对应一次来源观察；更正提取可修正 data 并留下更正理由，原始快照不动。更正后重新计算下游并重新验收。
- 续跑先读 package.json、work/plan.md、datasets.json 与 qa 结果；检查已有记录 ID 后再分配，不覆盖已封包版本。
- 数据包可以独立使用，但从整包中单独导出时须携带 README、字典、全部传递依赖输入、方法、来源索引和对应原件/快照，重写相对路径并重新校验。不能只复制 curated 后留下断链。
