# 研究线 B： 缓存与批处理的计价口径细节

## 目标

查清三家大模型 API（Anthropic / OpenAI / Google）在 **prompt caching（上下文缓存）与 batch（批处理）** 上的计价口径：缓存写入价、缓存命中价、TTL 与过期规则、批处理折扣比例与生效条件、长上下文加价的触发阈值。回答到「能直接写进对比矩阵」的程度。

## 背景

整体研究的问题：为一份年度 agent 运行预算建立**可比口径**。主线程已完成 A 线（三家官方计价页的 input/output 价格），来源 ID `A001`（Anthropic）、`A002`（OpenAI）、`A003`（Vertex AI）、`A005`（Gemini API）。缓存与批处理是隐藏成本的主要来源，也是最容易被不同口径误比的部分。

## 范围边界

- **包含**：prompt caching 的写入/命中价、TTL、最低缓存长度；batch API 的折扣率与生效条件；长上下文（>200K 等）加价阈值。
- **不包含**：input/output 基础单价（A 线已完成）；微调价格；企业协议价；第三方成本分析的结论（只可用来发现遗漏的口径项，不作证据）。

## 建议信源与工具

- https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching （及 pricing 页的缓存行）
- https://platform.openai.com/docs/guides/prompt-caching 与 batch API 文档
- https://ai.google.dev/gemini-api/docs/caching 与 batch 文档
- 工具：`scripts/capture_source.py`（保真）。**不要用 WebFetch 的返回当原文**——它返回模型处理过的摘要，完整度只能标 `summary`，不能作逐字摘录依据。

## 预算

工具调用约 15 次；最多存档 6 个来源。

## 停止条件

- 三家的缓存与批处理口径都拿到官方原文 → 停
- 或预算用尽 → 停，把缺口写清楚

## 输出格式

只回传主线程，**不把全文塞回**：

1. 结论摘要（≤300 字）
2. 已写文件的路径清单
3. 来源 ID 清单（每条一行：完整度 / 一手二手 / 是否支撑关键结论）
4. 未解问题与建议的下一轮方向

## 存档要求（强制）

- 来源 ID 前缀用 **`B`**：`B001`、`B002`…
- 快照写 `raw/sources/<ID>-<slug>.md`，原始文件写 `raw/files/`（用 `capture_source.py`，不要手写快照）
- 检索日志写 `raw/search-logs/B.md`，每次检索立即记录
- 笔记写 `notes/B-cache-batch.md`，摘录格式见 `assets/notes-template.md`：
  `- 来源: \`B001\` · 定位: …` + `- 逐字摘录:` 下的 `>` 引用块（**逐字**，能在快照里原样找到）
- **不改** `sources.md`、`report.md`、`plan.md`（主线程统一合并）
- 读过且判定相关的来源一律存档；只引用自己实际读过的内容
