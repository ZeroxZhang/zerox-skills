# 完整虚构示例 / Complete fictional example

[中文](#中文) | [English](#english)

## 中文

这是一份可运行、可复算的品牌研究示例。**枝间茶铺、相关公司、人物、注册号、来源机构、日期事件和全部数字均为合成设定，不是实际尽调。** 不要把示例复制到真实项目后保留这些数据或引用。

先打开[HTML 主报告](branch-tea/reports/report.html)，再按需查看[独立底稿](branch-tea/reports/report-audit.md)与[报告内容 JSON](branch-tea/report-content.json)。HTML 离线可读，使用与正式报告相同的渲染器；没有用生成图片冒充真实门店、人物或商标。

示例演示四件事：

- **品牌入口、公司主体**：品牌、商标权利人、零售经营公司与控制方分别建档；财务估算只指向经营公司单体，不混入集团或品牌口径。
- **有约束的估算**：门店与线上渠道法得到 1,640–2,220 万元，人员规模法得到 1,800–2,200 万元，重叠为 1,800–2,200 万元。完整公式、区间、假设及其理由见[估算输入](branch-tea/estimates/EST-01-revenue.json)，底稿可逐项复算。经营参数是教学情景假设，不能因区间相交就当作财报实绩。
- **公司判断与品牌信号分开**：官网历史定位、管理层计划与后续观察相互对照；评论和收据样本说明便利抽样的边界，不计算没有依据的 NPS、市场份额或营销回报。
- **不掩盖关键未知**：四个关键问题中，利润与现金问题仍无法回答，因此保持 `limited`。`completion_review` 记录为什么不能完成，而不是给完成状态盖章。

### 文件与证据边界

`branch-tea/` 是完整示例工作区：十三张台账、项目配置、七份合成原材料、七个适用模块底稿、估算输入、报告内容、HTML 和独立底稿。其他模块按约定范围标为 `deferred`，上市研报在合成设定下不适用。未提供实际财务数据，所以没有运行财务比率或把估算收入填入财务输入。

各来源的 `origin_group` 用来演示不同形成路径；它们全部出自本示例作者，**不证明现实中的来源独立性**。`resolved`、`verified` 和 `actual` 等字段只表示合成场景内的角色与记录类型，不能当作真实外部核验。搜索日志只记录读取包内材料，没有声称真实联网、访谈、现场或审计。

### 重建与检查

在技能根目录执行以下命令；会重建示例目录内已有的 HTML 与底稿。若要自由修改，先将整个 `examples/branch-tea/` 复制到技能包外的新工作区，再把命令中的项目路径替换为副本。

```bash
python3 scripts/evidence_ledger.py --project examples/branch-tea validate
python3 scripts/triangulate.py --project examples/branch-tea --input examples/branch-tea/estimates/EST-01-revenue.json
python3 scripts/build_report.py --project examples/branch-tea --content examples/branch-tea/report-content.json --output examples/branch-tea/reports/report.html --overwrite
python3 scripts/check_report.py --project examples/branch-tea --report examples/branch-tea/reports/report.html --mode draft
```

预期：台账与 `draft` 检查通过，估算状态为 `triangulated`。图片警告是预期的：虚构公司没有真实企业照片；期间、单位与桥接仍须人工核对。三张定量图、两张关系图、一条时间线、两个矩阵和十一项理解主题均由内容模型生成。

```bash
python3 scripts/check_report.py --project examples/branch-tea --report examples/branch-tea/reports/report.html --mode completed
```

该命令应返回 **退出码 1**：`KQ-04` 无法回答、关键财务声明未核实、`G-0001` 阻断范围完成。这是正确保留限制的演示，不应通过改状态或删除核心问题让它变绿。新建真实研究仍应使用 `init_project.py`，不要沿用本例已经锁定的虚构主体。

## English

This is a runnable, reproducible brand research example. **Branch Tea and every related company, person, identifier, source organization, dated event and number are fictional fixtures, not actual due diligence.** Do not retain this data or its citations when starting real research.

Start with the [HTML report](branch-tea/reports/report.html), then inspect the [independent workpaper](branch-tea/reports/report-audit.md) and [report content JSON](branch-tea/report-content.json). The HTML works offline and uses the production renderer. No generated image impersonates a real store, person or trademark.

The example demonstrates four practices:

- **Enter through a brand, research the companies**: separate the brand, trademark holder, retail operator and controlling company. The revenue estimate belongs to the operating legal entity alone, not to the brand or consolidated group.
- **Bound the estimate**: stores plus online sales produce RMB 16.4–22.2 million; workforce productivity produces RMB 18–22 million; the overlap is RMB 18–22 million. The [estimate input](branch-tea/estimates/EST-01-revenue.json) and workpaper preserve formulas, ranges, assumptions and rationale. Operating parameters are teaching scenarios; overlapping ranges do not establish reported revenue.
- **Separate company conclusions from brand signals**: compare historical positioning and management plans against subsequent observations. Review and receipt samples illustrate convenience-sampling limits, without inventing NPS, market share or marketing returns.
- **Keep critical unknowns visible**: one of four key questions—profit and cash generation—remains unanswered, so the project stays `limited`. Its `completion_review` records why completion is blocked rather than approving it.

### Files and evidence limits

`branch-tea/` is a complete sample workspace: thirteen ledgers, configuration, seven synthetic source documents, seven applicable module workpapers, an estimate, report content, HTML and the audit workpaper. Other modules are explicitly `deferred`; listed-company research is inapplicable within the fictional setup. There are no actual financial statements, so no financial ratios are calculated and estimated revenue is not inserted as financial input.

The `origin_group` values demonstrate distinct hypothetical source paths. Every source was written by the example author, so **they do not establish real-world independence**. Statuses such as `resolved`, `verified` and `actual` apply only inside the fixture. Search logs record local file reading, not real web research, interviews, site visits or audits.

### Rebuild and check

Run the commands in the Chinese section from the skill root. They rebuild the existing HTML and workpaper. To experiment, first copy all of `examples/branch-tea/` outside the installed skill and substitute that project path in the commands.

Expected results: ledger validation and the `draft` check pass; the estimate is `triangulated`. The missing-real-image warning is intentional because this fictional business has no real corporate photography. Periods, units and bridges still require human review. The content model generates three quantitative charts, two relationship diagrams, one timeline, two matrices and all eleven explanation topics.

The `--mode completed` command must return **exit code 1**: `KQ-04` is unanswered, a critical financial claim is unverified, and `G-0001` blocks scope completion. Do not change statuses or remove the question to make this example pass. Start real research with `init_project.py` rather than reusing its resolved fictional identities.
