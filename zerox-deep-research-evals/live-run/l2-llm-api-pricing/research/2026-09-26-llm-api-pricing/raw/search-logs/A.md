# 检索日志 · A

## 2026-09-26T18:48:00+08:00 · direct-URL(已知权威源)

- 查询原文: 无检索（能力盘点：本会话 WebSearch 工具返回空结果，改用直接 HTTP 抓取已知权威官方文档）
- 过滤: —
- 打开并存档: `A001` `A002` `A003` `A005`
- 弃用:
  - https://openai.com/api/pricing/ — HTTP 403，登记 `A004`（metadata-only）
  - https://ai.google.dev/gemini-api/docs/pricing — curl 探测得 302，改用 urllib 成功（`A005`）

## 2026-09-26T18:52:00+08:00 · brave-search(HTTP)

- 查询原文: `LLM API pricing prompt caching batch discount 2026`
- 过滤: 语言=`en`
- 看过的结果: 各家官方文档、第三方成本分析
- 备注: 本题为「官方计价口径」，二手成本分析不作证据，仅用于发现遗漏口径（缓存 TTL、批处理窗口）。
