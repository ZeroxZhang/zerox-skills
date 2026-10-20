# CLI 使用说明

在 Skill 根目录执行，Python 3.10+，标准库；Windows 可按环境改用 `py -3`。中文 UTF-8 输入输出。默认不联网、不外发文件，不依赖私有插件或密钥。命令中的 `/tmp` 是示例，可替换为有权限的工作目录。

## 工作区与配置

```bash
python3 scripts/init_project.py --output /tmp/dd-example --target "待核验法定名称" --purpose investment --depth Standard
```

`--as-of YYYY-MM-DD` 可设置历史截止日；默认按 `--timezone Asia/Shanghai` 的执行当日。平台没有 IANA 时区数据时可显式选 `--timezone UTC` 并注明时区差异。`--listing-status listed --exchange 交易所 --security-code 代码` 只是输入信息，会预建研报需求，身份仍待核实。

目的编码：investment 投资、acquisition 并购、partnership 合作、credit 授信、supplier 供应商、competitor 竞品。未给目的则 null/pending。配置改目的后，按契约重建对应 `scorecard.csv` 全部八维度记录；不得保留旧目的评分。

配置 `module_scope` 对01–18分别给 pending/applicable/not_applicable，后者必须写理由。Quick未展开不等于不适用。`events` 每项包含 date/entity_id/description；`industry_keywords`、`languages` 控制计划；`peer_required` 表示关键问题需要可比/上下游补证。

`identity_status=resolved` 要与实体台账一致；`control_chain_checked=true` 和 `control_evidence_ids` 需实证。关系表记录多条边；有效区间为左闭右开，proposed 不等于已交割。`category_exemptions` 仅可用于制度不适用或尚无相应期的官方中期材料，必须说明依据；不能豁免难取得的研报。

`report_status` 为 draft/limited/complete；`declared_complete` 为是否宣称全部执行完成。`last_refresh_at` 为实际最后复查的带时区时间。`published_score` 仅在真正发布综合分时填写，由检查器重算核对。

## 检索计划

```bash
python3 scripts/search_plan.py --project /tmp/dd-example --output /tmp/dd-plan.json
```

计划覆盖别名、代码、控制链主体、模块、来源、语言及滚动时间窗。所有任务是 not_executed，不会写搜索日志。Agent 实际访问后另填 `search-log.csv`。

## 台账维护

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

所有场景维度均留行。缺失分数为空并写 reason；不适用须写依据。非空评分必须有充分证据、锚点及高/中置信度。原始权重来自契约，必要变更用 `scoring_override` 给完整 weights、critical_dimensions 和 reason。

输出 coverage、partial_score、overall_score 与独立 research_gate。低于门槛、关键维度未覆盖或有重大未解冲突时 overall_score=null；局部分数不包装为总分。

## 报告组装与检查

模块内容放在工作区 `modules/01-名称.md` 至 `18-名称.md`；同一编号只保留一个本次版本。章节补充用 JSON 的 summary、highlights、recommendation、research_comparison、data_bridge、judgment、next_steps 字段，每个值是已有分析的 Markdown。

```bash
python3 scripts/build_report.py --project /tmp/dd-example --sections /tmp/sections.json --output /tmp/dd-report.md
python3 scripts/check_report.py --project /tmp/dd-example --report /tmp/dd-report.md --mode draft --output /tmp/dd-check.json
python3 scripts/check_report.py --project /tmp/dd-example --report /tmp/dd-report.md --mode completed
python3 scripts/check_report.py --mode template --report templates/report-full.md
```

组装默认拒绝覆盖，只有 `--overwrite` 才替换指定输出。组装不自动升级配置完成状态；未填写内容转为明确缺口，不能视为完整研究。Quick 仍输出研报面板与限制。完成态不得有未填字段、主体歧义、模块适用性待定或未满足的研报任务。

检查输出区分 errors、warnings、manual_review。必须执行人工复核：引用是否支持原句、实体是否匹配、同源、最新性、假设、重要反证、决策权限及已执行工作的真实证明。

## 退出码与安全写入

- `0`：命令成功，或结构校验通过。与研究真实性、充分性无等价关系。
- `1`：validate/check_report 检测到硬错误。
- `2`：参数、输入、格式或文件/权限错误，输出可定位的错误消息。

初始化不允许已存在路径；新增导出默认不覆盖；台账更新在写入前验证并保留快照。不要将包含秘密或商业资料的项目工作区提交至公开仓库。
