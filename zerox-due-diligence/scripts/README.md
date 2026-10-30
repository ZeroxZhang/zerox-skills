# CLI 使用说明

在 Skill 根目录执行，Python 3.10+，标准库；Windows 可按环境改用 `py -3`。中文 UTF-8 输入输出。默认不联网、不外发文件，不依赖私有插件或密钥。命令中的 `/tmp` 是示例，可替换为有权限的工作目录。

## 工作区与配置

```bash
python3 scripts/init_project.py --output /tmp/dd-example --target "待核验法定名称" --purpose company_research --depth Standard
# 用户给的是品牌名时：
python3 scripts/init_project.py --output /tmp/dd-brand --target "品牌名" --target-type brand --purpose company_research
```

初始化还会创建待编辑的 `report-content.json`（HTML 主报告内容模板，不代表已完成分析）和空的 `estimates/` 目录。`--target-type brand` 把目标登记为品牌：在以已核实的 `operator` 或 `brand_of` 关系查明经营主体之前，控制链与上市关系保持待核实，完成态检查也会拒绝；做法见[从品牌到公司](../references/brand-to-company.md)。

`--as-of YYYY-MM-DD` 可设置历史截止日；默认按 `--timezone Asia/Shanghai` 的执行当日。平台没有 IANA 时区数据时可显式选 `--timezone UTC` 并注明时区差异。`--listing-status listed --exchange 交易所 --security-code 代码` 只是输入信息，会预建研报需求，身份仍待核实。

目的编码：company_research 公司研究；investment 投资、acquisition 并购、partnership 合作、credit 授信、supplier 供应商、competitor 竞品为专项。明确了解公司是已确认目的；未给目的才保留 null/pending。所有项目评分默认关闭；六类专项确实需要评分时可用 `--enable-scoring` 初始化评分行，再确认项目评分条件。改变目的或权重后同步评分行，不能沿用旧目的分数。

`key_questions` 记录研究开始时约定的关键问题，每项为 `{kq_id, question, why_it_matters, sub_questions, claim_ids, status, answer}`；`kq_id` 形如 KQ-01，`status` 为 open/answered/answered_with_limits/unanswerable。已回答须写 `answer` 并关联声明，判定无法回答须写原因。仍有 open 或 unanswerable 时不能完成约定范围。写法见[工作流](../references/workflow.md)。

配置 `module_scope` 对01–18分别给 pending/applicable/deferred/not_applicable：deferred 表示适用但本次未展开，not_applicable 表示确实不适用，两者都必须写理由。模块01、02、03、05、09、12、15不能 deferred 或 not_applicable；上市关系触发后模块18同样不能。`events` 每项包含 date/entity_id/description；`industry_keywords`、`languages` 控制计划；`peer_required` 表示关键问题需要可比/上下游补证。

`identity_status=resolved` 要与实体台账一致；`control_chain_checked=true` 和 `control_evidence_ids` 需实证。关系表记录多条边；待核实边允许 effective_from 为空，verified 则须真实生效日期与证据。有效区间为左闭右开，proposed 不等于已交割。品牌角色关系 `trademark_holder/operator/brand_of/licensee/manufacturer/distributor` 的下层（child）须为品牌或业务单元；主体角色、自然人权利人和子品牌例外统一见[从品牌到公司](../references/brand-to-company.md)。前三种参与相关主体的控制链检索；商标归属与经营控制分开解释，授权、生产和经销不构成控制。`category_exemptions` 仅可用于制度不适用或尚无相应期的官方中期材料，必须说明依据；不能豁免难取得的研报。

旧配置缺少新增字段时只读补默认（评分关闭、范围审核为空、关键问题为空），不自动重写文件。数据契约 1.0.0 的工作区可以继续使用。旧项目要重新声明完成或发布评分，应按当前规则复核。

`report_status` 为 draft/limited/complete；complete 只表示约定研究范围完成，需 `completion_review` 复核。`research_gate` 独立记录研报资料覆盖，仍有未读或未取得资料时保持 partial/incomplete。`declared_complete` 更严格，表示全部工作完成，有开放缺口或计划动作时不得设为 true。`last_refresh_at` 是实际最后复查的带时区时间。`published_score` 仅记录经检查可发布的实际总分。

`completion_review` 默认 null；结束范围时填写 `scope`（与用户约定的范围）、`key_claim_ids`（实际采用的关键结论）、`gap_assessments` 和带时区的 `reviewed_at`。每个开放缺口对应一项 `{gap_id, impact, disposition}`；`disposition` 为 non_blocking（不妨碍范围）、limits_conclusion（限制非核心结论）或 blocks_completion（阻断核心问题）。关键结论须有已核验的依据；缺口、重大冲突、必要检索未执行不能靠状态改写消失。未知妨碍核心问题时保持 limited，不事后缩小范围绕过。语义充分性仍需分析者复核。

## 检索计划

```bash
python3 scripts/search_plan.py --project /tmp/dd-example --output /tmp/dd-plan.json
```

计划按优先级排列：未回答的关键问题、关键声明与开放缺口的核验、官网基础阅读（含网页存档）、品牌追溯（`brand_trace`，仅品牌目标）与品牌层信号（`brand_signal`）、管理层言行追踪（`guidance_tracking`，上市主体另含业绩说明会与互动平台），最后是按模块、别名和语言展开的候选关键词、研报滚动时间窗与事件后检索。`deferred` 与 `not_applicable` 模块不生成候选关键词。所有任务都是 not_executed，不会写搜索日志；Agent 实际访问后另填 `search-log.csv`，发现新问题再更新计划。

## 估算与三角验证

```bash
cp templates/estimate-input.json /tmp/dd-example/estimates/EST-01-营收.json
# 填写各方法的公式与输入区间后：
python3 scripts/triangulate.py --input /tmp/dd-example/estimates/EST-01-营收.json --project /tmp/dd-example
```

每种方法写公式（只允许输入名、数字、括号和 `+ - * /`）、可选的 `unit_factor`（结果单位换算），以及每个输入的 low/base/high、单位、`basis`（evidence 或 assumption）、证据 ID 与理由。脚本按区间运算得出各方法的上下限，判断方法是否独立（不共用证据，也不共用来源同源组），输出：

- `status`：triangulated（已核对来源，至少两种独立方法且所有有证据方法无区间冲突）、divergent（存在有证据方法的区间冲突，不能取平均）或 insufficient（独立的有证据方法不足两种，或未提供项目核对来源）；
- `overlap`、`envelope`、全部独立组合、冲突方法、各方法区间与完整输入依据；
- `presentation`：证据与独立性足够时提供可放入 `report-content.json` 的 `range` 区间图（`kind=estimate`）；insufficient 时为空。

退出码 0 表示得到可用的估算结果，1 表示 insufficient，2 表示输入错误。`--project` 用于核对证据存在、同源组和关联声明。声明须为【推断】、estimate、numeric，且主体/范围一致、输入证据均通过带 `bridge` 的声明关联保留；期间、单位与原文含义仍需人工核对。未提供项目只试算，不宣称交叉印证。`check_report.py` 会检查 `estimates/` 下的全部文件，`build_report.py` 把估算表写入底稿。方法与边界见[估算与三角验证](../references/estimation-triangulation.md)。

## 台账维护

无原始发布日期的来源可把 `published_date` 留空，在 `grade_reason` 说明未知及其时点限制；历史时点隔离与研报日期要求见[证据标准](../references/evidence-standard.md)。访问日不得替代发布日期。

十三张CSV表头与规则在 [data-contract.json](../schemas/data-contract.json)。多值为 JSON 数组，CSV 负责引号转义；推荐 JSON 批量写入，避免手工引号错误。

`--input` 文件格式为表名到完整记录数组的映射，例如：

```json
{
  "source-register": [
    {
      "source_id": "S-0001",
      "title": "实际访问材料的真实标题",
      "source_type": "official",
      "publisher": "实际发布机构",
      "published_date": "2026-10-01",
      "accessed_date": "2026-10-20",
      "locator": "真实URL或有权限的本地路径",
      "grade": "S",
      "origin_group": "该原始材料的同源标识",
      "access_status": "full_text",
      "authenticity": "pending",
      "authorization": "实际允许的使用范围",
      "time_scope": "as_of"
    }
  ]
}
```

以上是格式示意，不是真实资料，执行前必须换成实际内容。一个批次可同时包含实体、来源、证据、声明及其关联，以满足循环引用。非必填字段可省略；更新采用完整行替换，省略字段会变为空，不是局部补丁。

```bash
python3 scripts/evidence_ledger.py --project /tmp/dd-example add --input /tmp/records.json
python3 scripts/evidence_ledger.py --project /tmp/dd-example add --input /tmp/updated-records.json --replace
python3 scripts/evidence_ledger.py --project /tmp/dd-example query --table source-register --field source_id --value S-0001
python3 scripts/evidence_ledger.py --project /tmp/dd-example sync-coverage
python3 scripts/evidence_ledger.py --project /tmp/dd-example validate
python3 scripts/evidence_ledger.py --project /tmp/dd-example export --output /tmp/dd-ledgers.json
```

`add` 默认拒绝重复主键；`--replace` 显式更新已有主键。每次修改会保存 `.ledger-backup-*` 完整快照。多表写入并非数据库事务，若中断，可检查快照后恢复对应文件；不要同时启动多个写入进程。

`sync-coverage` 预建必读类别/开放缺口，推导最新发现/全文/已读指针和门槛。**不会搜索、阅读全文或自动关闭缺口**。取得材料后，真实填写报告状态、类别相关性、阅读笔记、检索ID和最新性时间；核实已补齐后关闭相应缺口并给理由，再同步。

若增加事件、新报告或控制关系，必须重新同步并校验。新报告造成原已关闭缺口重新失效时，需人工重开原缺口或登记新缺口；检查器会拒绝未完成类别没有开放缺口的状态。

如果台账中的最新年度/中期/事件官方披露晚于已知公司跟踪报告，同步会自动补建事件后类别；其他重大事件仍须由分析者识别并写入配置。`constraints.network` 为 offline 或 unknown 时，不能把上市研报整体门槛提升为完成；声明 online 本身也不证明真实执行，仍需检索和阅读记录。

## 财务计算

```bash
python3 scripts/financial_ratios.py --input /tmp/dd-example/financial-input.json --output /tmp/dd-financial.json
```

先填写主体、范围、日期/天数、币种/单位、会计政策、实际预测、审计属性、来源和 `values`。每个非空数值在 `input_evidence` 中给证据ID数组。

支持的 `values`：

| 类别 | 字段 |
| --- | --- |
| 收入利润现金 | revenue、cost、net_profit、operating_cashflow、capex |
| 流动与速动 | current_assets、current_liabilities、inventory、prepayments |
| 平均资产权益 | assets_begin/end、equity_begin/end |
| 周转 | receivables_begin/end、inventory_begin/end、payables_begin/end、credit_sales、purchases |
| 跑道 | available_cash、monthly_net_burn |
| 补充债务资产输入 | total_debt、total_assets（保留输入，当前不单列杠杆指标） |

`prior` 是同结构上期对象或 null；增速实现同季同长度的实际同比，主体/范围/币种/单位/会计政策必须一致。季度比较或口径桥接另列分析底稿。

默认需平均余额。`options.allow_end_balance=true`、`allow_revenue_proxy=true`、`allow_cost_proxy=true` 分别显式允许期末余额、营收代赊销、成本代采购近似；输出保留标记。`quick_deductions` 默认 inventory/prepayments，缺失不会补零。

`capex_sign` 明确 positive_outflow 或 negative_outflow；简化自由现金流不冒充 FCFF/FCFE。跑道须给 `cash_burn_basis`，明确可用现金已剔除受限资金、历史/前瞻消耗定义、是否包括必要资本开支/偿债/已承诺支出。零现金可以得到零月，非正消耗不计算永久期限。

`thresholds` 数组每项为 `{metric, operator: "lt"或"gt", value, scope, source}`，输出只是适用范围明确的核查线索。单独计算不验证证据ID真实存在；项目报告检查会核对引用。

## 评分

```bash
python3 scripts/scoring.py --project /tmp/dd-example --output /tmp/dd-score.json
```

`company_research` 不评分。专项仅在 `scoring_enabled=true` 时计算；启用后先用 `scoring_override` 给完整 weights、critical_dimensions 和 reason，解释它们与核心问题的对应，即使采用候选权重也需确认。未确认时不发布综合分。已启用的所有维度均留行；缺失分数为空并写 reason，不适用须有依据。非空分数必须有充分证据、项目具体锚点及高/中置信度；契约的共用 scale 和各目的 criteria 供选择量尺，不替代判断。

输出 coverage、partial_score、overall_score 与独立 research_gate。低于门槛、关键维度未覆盖或有重大未解冲突时 overall_score=null；局部分数不包装为总分。

## HTML 主报告与独立底稿

模块分析放在工作区 `modules/01-名称.md` 至 `18-名称.md`；同一编号只保留一个本次版本。主报告需要独立编辑：按[报告设计](../references/report-design.md)从模块和已核验台账中提炼读者问题、结论与图表，填入工作区 `report-content.json`（`version: "1.2"`）。

内容规则只在两处定义，本文件不再重复：

- 字段、图表类型和每种内容块的约束见[内容契约](../schemas/report-content.schema.json)，可改写的结构见[内容模板](../templates/report-content.json)与[视觉配方](../references/visual-examples.json)。
- 11 个理解主题、业务图、公司时间线、人物分章、图片、比较矩阵、品牌关系图与估算区间图的编排要求见[报告设计](../references/report-design.md)。

```bash
python3 scripts/build_report.py \
  --project /tmp/dd-example \
  --content /tmp/dd-example/report-content.json \
  --output /tmp/dd-example/reports/report.html

python3 scripts/check_report.py \
  --project /tmp/dd-example \
  --report /tmp/dd-example/reports/report.html \
  --mode draft \
  --output /tmp/dd-example/reports/report-check.json

# 只有研究实际满足完成门槛时，才使用完成态检查。
python3 scripts/check_report.py \
  --project /tmp/dd-example \
  --report /tmp/dd-example/reports/report.html \
  --mode completed
```

构建生成离线 HTML（内联样式与图表）和同目录 `report-audit.md`；后者保留完整模块、关键问题、研究状态、估算底稿、台账及后续请求。默认拒绝覆盖，`--overwrite` 才替换两份输出。生成不会自动升级配置完成状态；未编辑的模板不能生成主报告。单文件 HTML 中仍可能包含项目材料，分享范围由用户授权决定。

检查输出区分 `errors`、`warnings`、`manual_review`，并附 `visual_review`、`brand_resolution`（品牌目标）与 `key_questions` 状态。检查同时校验工作区 `estimates/` 下的全部估算文件。完成态的额外要求见[质量门槛](../references/quality-gates.md)。

### 旧 HTML 内容迁移

`check_report.py --mode draft` 可读取历史 1.0/1.1 HTML，并提示它未通过新版要求；`--mode completed` 拒绝旧版。`build_report.py` 只接受 1.2 内容。迁移时按新版模板补齐 11 个解释主题、业务图、公司时间线（或契约允许的真实未知说明），按证据补充人物、图片及比较矩阵，保留原有证据及适用分析，再把 `version` 改为 `"1.2"`；只改版本号不算迁移。

### 兼容旧 Markdown 底稿

原有 `--sections` + `.md` 用法保留，适合单独导出完整底稿。`--sections` 的 JSON 字段为 summary、highlights、recommendation、research_comparison、data_bridge、judgment、next_steps，各值为已有分析的 Markdown。此路径不会把 18 模块改写成阅读型主报告。

```bash
python3 scripts/build_report.py --project /tmp/dd-example --sections /tmp/sections.json --output /tmp/dd-audit.md
python3 scripts/check_report.py --project /tmp/dd-example --report /tmp/dd-audit.md --mode draft
python3 scripts/check_report.py --mode template --report templates/report-full.md
```

## 可视化编辑检查

HTML 构建输出和检查输出的 `visual_review` 按章节列出视觉类型、计数和编辑线索，摘要写入同名 `-audit.md`。警告不自动改变研究状态，也不证明文字中的数字足够可比；分析者逐项决定转图或说明保留原因。

## 退出码与安全写入

- `0`：命令成功，或结构校验通过。与研究真实性、充分性无等价关系。
- `1`：validate/check_report 检测到硬错误。
- `2`：参数、输入、格式或文件/权限错误，输出可定位的错误消息。

初始化不允许已存在路径；新增导出默认不覆盖；台账更新在写入前验证并保留快照。不要将包含秘密或商业资料的项目工作区提交至公开仓库。
