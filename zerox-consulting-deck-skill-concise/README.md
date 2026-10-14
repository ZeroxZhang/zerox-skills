> 语言：[简体中文](README.md) · [English](README_EN.md)

# Consulting Deck Skill · Concise

维护地址：[zerox-consulting-deck-skill-concise](https://github.com/ZeroxZhang/zerox-skills/tree/main/zerox-consulting-deck-skill-concise)。

**把一堆原始材料，变成一份能直接拿去见客户的咨询报告。**

给它财报、访谈、行业资料或一份初稿，它会先做分析，再把结论组织成有主线、有图表、有依据的整册报告，交付一份可翻页的 HTML 与一份同版 PDF。

[![整册总览](docs/showcase/report-overview.png)](docs/showcase/report-page-mechanism.png)

## 产出长什么样

| | |
|---|---|
| ![收入机制对比](docs/showcase/report-page-mechanism.png) | ![榜单信号与成立条件](docs/showcase/report-page-metric.png) |
| 两条业务线的机制、能力与风险逐项对照 | 大数字配点阵给出样本信号，右侧展开成立条件 |
| ![口径分离](docs/showcase/report-page-caveats.png) | |
| 两组数字来自不同分母就分开呈现，不拼成一条假的下降曲线 | |

成稿是**单个自包含 HTML**：双击即看，支持翻页、缩放、全屏、深链，内嵌一键下载的同版 PDF，离线与转发都不掉东西。

## 它和"让 AI 画几张图"的区别

- **先分析，再表达。** 材料按明细、分布和口径读懂，围绕问题做真正的计算、比较与机制推理，不把输入压成几条摘要再配图。
- **标题说了什么，图上就得看得见。** 标题声称的"链条、差异、条件"要在展品里找到对应结构；收短模块后必须回到整页重新分配空间。
- **亲眼看过才算完成。** 逐页查看 HTML 截图与最终 PDF 并给出具体判断；不能看图时如实写"未验收"，不用自动检查代替。
- **关键限制不会被悄悄丢掉。** 分母、期间、否定条件、事实与预测的身份绑定到页面真实对象，并核对是否真的进入最终 PDF。

支持三种材料状态：**原始材料**（完整分析）、**开放研究**（先探索再收敛）、**已确认文稿**（保留事实与结论，只重组表达）。

## 使用

在 `zerox-skills` 仓库根目录，把 `zerox-consulting-deck-skill-concise` 复制或软链到所用工具的技能目录，例如：

```bash
ln -s "$(pwd)/zerox-consulting-deck-skill-concise" ~/.codex/skills/zerox-consulting-deck-skill-concise
```

然后调用 `/zerox-consulting-deck-skill-concise`，说清**受众与要回答的问题、手上的材料、硬性要求**即可。不需要预先指定页数、图型数量或要套哪个框架。

开始之前需要知道：**一次完整制稿预计用时 1–2 小时**（随任务量浮动），**token 消耗明显大于普通问答**——调研、逐页制作、逐页看图验收和独立复核都是真跑；技能会先说明代价并等你确认再开工。建议使用**能读图的多模态模型**和**当前最强的 SOTA 模型**。用法举例与输入建议见[技能说明](docs/usage.md#怎么用)。

完整的产品说明、交付形态与安装构建见 [技能说明](docs/usage.md)。

## 仓库结构

| 内容 | 位置 |
|---|---|
| 技能入口（完成判据、六步主线、硬契约、命令） | [SKILL.md](SKILL.md) |
| 按需说明（图表选型、分析、精度、交付等） | [references/](references/) |
| 引擎、主题、字体、展品运行库 | [assets/](assets/) |
| 制稿与维护脚本 | [scripts/](scripts/) |
| 可选外部选型专家（默认不用，技能不分发其快照） | [echarts-viz-planner](https://github.com/ZeroxZhang/echarts-viz-planner) |

此目录只呈现技能本身。开发过程记录、历代迭代与审查留档在本地维护，不随仓库分发。

## 边界

交付形态是 **HTML + 同版 PDF**，不产出 PPTX。它做分析与表达，不替代外部事实核验——原材料的身份（事实／测算／受访者观点）会被如实保留。自动检查提供工程证据，不替代商业判断；文案里的"通过"只代表它检查过的范围。

三套主题（McKinsey／BCG／Accenture）为公开视觉资料的独立适配，**并非任何公司的官方内部模板**。本页展示的报告内容为演示材料，来源与身份在页面内标注。
