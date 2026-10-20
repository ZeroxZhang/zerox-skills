# CLI 使用说明

在 Skill 根目录执行，Python 3.10+，标准库；Windows 可按环境改用 `py -3`。中文 UTF-8 输入输出。默认不联网、不外发文件，不依赖私有插件或密钥。命令中的 `/tmp` 是示例，可替换为有权限的工作目录。

## 工作区与配置

```bash
python3 scripts/init_project.py --output /tmp/dd-example --target "待核验法定名称" --purpose investment --depth Standard
```

初始化还会创建待编辑的 `report-content.json`，用于HTML主报告；它是内容模板，不代表已完成分析。

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

## HTML 主报告与独立底稿

模块分析仍放在工作区 `modules/01-名称.md` 至 `18-名称.md`；同一编号只保留一个本次版本。模块是研究底稿，主报告需要独立编辑：读取[报告设计](../references/report-design.md)，从模块和已核验台账中提炼读者问题、结论与可追溯图表，填入工作区 `report-content.json`。

字段和支持的图表类型见[内容契约](../schemas/report-content.schema.json)，示例结构见[内容模板](../templates/report-content.json)。证据ID必须存在于当前项目台账。正文避免呈现搜索日志、模块适用性、覆盖计数和完整请求问卷，但必须保留影响决策的重要限制。

新建HTML必须使用 `version: "1.2"`。默认先写公司画像和业务机制，再扩展增长、竞争、财务、风险与决策。以下11个 `explanation` 主题在全文各出现一次，可按内容分入自定章节，不强制章节名称或数量：

| topic | 正文必须解释 |
| --- | --- |
| identity | 公司做什么、行业与阶段，品牌/集团/经营主体的范围 |
| history_team | 创立背景、重要沿革、创始人或核心团队 |
| offering | 产品或服务、解决的需求与使用场景 |
| customers_markets | 使用者/购买者/付款者、主要市场与渠道 |
| transaction_flow | 需求、下单或签约、交付、收款及售后怎样衔接 |
| operating_model | 自营与外包分工，供给、履约和运营如何组织 |
| revenue_costs | 谁付费、如何计费、主要成本与现金逻辑 |
| differentiation | 相对替代方案的客户价值、支撑条件与边界 |
| financial_performance | 营收规模、构成、毛利率及净利率分别说明主体、期间、来源和缺口 |
| marketing | 渠道、内容投放/品牌、获客转化复购与尚未取得的数据 |
| competition | 主要竞品选择依据、同口径比较和替代，不以行业规模代替竞争分析 |

每块填写 `type`、`topic`、`title`、`text`、`status`、`evidence_ids`、`limitations`。`supported/partial` 至少有一条真实引用；`partial/unknown` 必须在 `limitations` 说明具体未知及其影响，`unknown` 可以没有引用。`supported` 的限制可为空字符串。渲染为自然的小标题和正文，覆盖状态只在检查输出中呈现。已有基础材料未进入正文属于编辑遗漏，应补回；真实缺证属于研究缺口，应补查并如实说明，不能为了通过检查编造答案。

至少一块 `process` 应标为 `purpose: "business_model"`，包含两个以上业务环节，各项 `basis` 为 `evidence/company_claim/inference/unknown`，对应证据直接支持、公司自述、分析推断、未知。只有 `unknown` 可以使用空引用；其他环节须有依据。公司自述和推断在正文中说明属性与边界，未知环节说明缺口；推荐合作步骤不能充当业务运转图。仅 `transaction_flow` 整体为 `unknown` 且明确写出限制时，允许省略业务图。其他流程可用 `purpose: "recommendation"` 或 `"other"`，也可不填写此字段；`basis` 可选，但未标未知的环节仍须引用。

`process.ordering` 可选 `sequence` 或 `conceptual`，省略时默认 `sequence` 以兼容历史内容。只有先后顺序已有依据时使用 `sequence`；若只知道环节及参与方，而订单、生产、交付和回款的先后尚未核实，应使用 `conceptual` 关联图，不显示顺序编号与箭头。新模板显式使用 `conceptual`，编辑时按证据选择，不能靠画箭头把未知时序变成事实。该字段控制呈现，不会自动验证时序真实性。

`timeline.purpose` 可填 `company_history/other`。公司发展时间线至少两个有引用、日期和事件说明的节点，且与 `identity` 同章；保留原始日期精度，计划与已发生分开。无此时间线时，只有 `history_team` 为 `partial/unknown` 且限制非空才允许生成，并给警告要求人工确认确实没有两个可用事件；不能随意标未知绕过。

`people` 块包含 `title` 和至少一个 `profiles` 条目，每人填写 `name/role/period/background/contribution/limitations/evidence_ids`。除 `limitations` 可为空，其余文字非空、引用非空。该块必须在与 `identity` 不同的独立章节；没有足够人物资料可以不放，检查会警告。角色与贡献、既往履历与现任状态分别介绍，不编造合伙人身份。

`image` 块填写 `role`（`logo/website/product/store/people/other`）、项目相对 `path`、`title/alt/caption`、`source_url`、`captured_at`（YYYY-MM-DD）、`usage_note` 与非空 `evidence_ids`。有原页时 `source_url` 填安全HTTP/HTTPS地址；本地或用户提供材料可为空字符串，通过 `evidence_ids` 关联原文件与来源台账，并在 `usage_note` 说明提供者和使用范围。`captured_at` 是本次实际取得或读取素材的日期，不是原图拍摄日或页面发布日期；原始时点未知在图注说明。

图片仅接受真实 PNG/JPEG/WebP，每张≤5 MiB、合计≤15 MiB；构建内嵌离线，不接受运行时SVG、绝对或越界路径、越界符号链接及运行时远程图片。来源SVG可用可信渲染或浏览器截图另存位图，保留原始来源，不得重新生成冒充真实标识。图片来源和使用说明不等于对页面宣传或人物身份的核验。模板没有预置图片，未实际取得图片则删除相应块。

`matrix` 块填写 `title`、至少两列 `columns`、至少一行 `rows`、`note`；可选 `purpose` 为 `competition/marketing/financial/other`。每行有 `label` 和与列数相同的 `cells`；每格有 `text/basis/evidence_ids`，`basis` 为 `evidence/company_claim/inference/unknown`，仅 `unknown` 允许空引用。比较维度、地区、时点及统计范围应一致；口径不同就解释差别，不强排排名。定性矩阵不计为定量图，仍需对可靠数字选择适当图表。

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

默认HTML支持离线阅读，内联报告样式与图表；同目录自动生成 `report-audit.md`，保留完整模块、研究状态、台账及后续请求。主报告的引用可定位到折叠证据附录。单文件HTML适合直接打开和分享，但其中仍可能包含项目材料，分享范围由用户授权决定。

组装默认拒绝覆盖，只有 `--overwrite` 才替换输出；注意主报告及对应底稿均属于本次交付。生成不会自动升级配置完成状态；Quick也采用HTML，研究门槛不变。未编辑的模板不能作为完成报告，禁止用“生成成功”替代分析。

检查输出区分 errors、warnings、manual_review。完成态不得有未填字段、主体歧义、模块适用性待定或未满足的研报任务。HTML检查不要求把元信息表、研究完成范围、研报覆盖表或搜索日志放回正文。

必须执行人工复核：仅看主报告能否回答“它是谁、卖给谁、怎样经营、怎样赚钱、关键未知是什么”；引用是否支持原句、实体与期间是否匹配、同源与最新性、重要反证、建议权限及已执行工作的真实证明；逐图检查数值、单位、主体范围、实际/预测属性、来源与可比口径，确认流程实际解释目标公司的交易而非通用行业常识。实际预览桌面、移动和打印，确认导航、图例、数据表、引用与折叠附录可读。字段齐全不证明解释充分，真实未知可以有限交付，不能据此宣称完成全部研究。

### 旧 HTML 内容迁移

`check_report.py --mode draft` 可读取历史1.0/1.1 HTML，并提示它未通过新版理解与内容要求；`--mode completed` 拒绝旧版。`build_report.py` 只接受1.2内容新建HTML。迁移时按新版模板补齐11个解释主题、业务图、公司时间线（或契约允许的真实未知说明），按证据补充独立人物介绍、图片及比较矩阵，保留原有证据及适用分析，再把 `version` 改为 `"1.2"`；只改版本号不算迁移。不新增CLI参数。

### 兼容旧 Markdown 底稿

原有 `--sections` + `.md` 用法保留，适合单独导出完整底稿。`--sections` 的 JSON 字段为 summary、highlights、recommendation、research_comparison、data_bridge、judgment、next_steps，各值为已有分析的Markdown。此路径不会把18模块自动改写成面向阅读的主报告。

```bash
python3 scripts/build_report.py --project /tmp/dd-example --sections /tmp/sections.json --output /tmp/dd-audit.md
python3 scripts/check_report.py --project /tmp/dd-example --report /tmp/dd-audit.md --mode draft
python3 scripts/check_report.py --mode template --report templates/report-full.md
```

完整与Quick Markdown模板保留给底稿兼容。无 `--sections` 时也可生成底稿骨架；未填写内容会保留缺口，不得宣称研究已完成。

## 退出码与安全写入

- `0`：命令成功，或结构校验通过。与研究真实性、充分性无等价关系。
- `1`：validate/check_report 检测到硬错误。
- `2`：参数、输入、格式或文件/权限错误，输出可定位的错误消息。

初始化不允许已存在路径；新增导出默认不覆盖；台账更新在写入前验证并保留快照。不要将包含秘密或商业资料的项目工作区提交至公开仓库。
