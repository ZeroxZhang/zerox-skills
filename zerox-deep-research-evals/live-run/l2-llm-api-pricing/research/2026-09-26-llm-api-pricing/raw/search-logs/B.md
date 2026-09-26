# 检索日志 · B

## 2026-09-26T19:05:00+08:00 · curl(已知权威源探测)

- 查询原文: 无检索式（能力盘点：本会话 WebSearch 工具返回空结果，改用直接抓取任务书与 A 线已知的官方文档 URL；先用 curl -I 探测可达性再采档）
- 过滤: —
- 探测的 URL 与状态:
  1. docs.anthropic.com/en/docs/build-with-claude/prompt-caching — 200，302 到 platform.claude.com/docs/en/build-with-claude/prompt-caching
  2. platform.claude.com/docs/en/build-with-claude/prompt-caching — 200
  3. docs.anthropic.com/en/docs/build-with-claude/batch-processing — 200，302 到 platform.claude.com 同路径
  4. platform.openai.com/docs/guides/prompt-caching — 200，302 到 developers.openai.com/api/docs/guides/prompt-caching
  5. platform.openai.com/docs/guides/batch — 200，302 到 developers.openai.com/api/docs/guides/batch
  6. ai.google.dev/gemini-api/docs/caching — 200
  7. ai.google.dev/gemini-api/docs/batch — 404 → 改用 ai.google.dev/gemini-api/docs/batch-api — 200（A005 快照侧栏链接确认路径）
- 打开并存档: （下一条续记）
- 弃用:
  - ai.google.dev/gemini-api/docs/batch — 404，改用 batch-api

## 2026-09-26T19:10:00+08:00 · capture_source.py(采档)

- 查询原文: 无检索式，按任务书建议信源 + 探测结果直接采档
- 打开并存档: `B001`(Anthropic prompt caching) `B002`(Anthropic batch) `B003`(OpenAI prompt caching) `B004`(OpenAI batch) `B005`(Gemini caching) `B006`(Gemini batch)
- 备注: 长上下文阈值优先从本线缓存/批处理文档与 A 线计价页快照（`A001` `A002` `A005`）取原文，不另占存档预算；6 源上限已用满，不再增档

## 2026-09-26T19:40:00+08:00 · brave/ddg/bing(引擎检索，补长上下文阈值)

- 查询原文: `OpenAI API pricing "long context" threshold tokens` / `OpenAI API pricing long context threshold tokens`
- 过滤: 语言=`en` 站点=`—`
- 看过的结果: 无有效结果 —— brave 返回无外链的挑战页；html.duckduckgo.com 与 lite.duckduckgo.com 均返回 anomaly 拦截页；bing 返回 10 条结果但全部是 openai.com/chatgpt.com 泛页（locale 串为 ko-KR），无任何文档定义长上下文分界
- 弃用:
  - search.brave.com/search — 页面为反爬挑战，无结果外链
  - duckduckgo html/lite — HTTP 200 但正文为 anomaly 拦截
  - bing.com/search — 结果为品牌泛页，与「阈值定义」无关

## 2026-09-26T19:45:00+08:00 · 本地存档全文检索(rg/grep)

- 查询原文: 在包内 `raw/sources/*.md` 与 `raw/files/*.html` 检索 `272K`、`TTL`、`48 hours`、`long context threshold`
- 目的: 在 6 源预算内尽量补齐「长上下文阈值」与「Google 显式缓存 TTL」
- 看过的结果:
  1. `A002` 原始 HTML：Long context 列头 tooltip = `>272K input tokens`，模型数据含 `gpt-5.5 (<272K context length)` → OpenAI 阈值 272K，但**快照正文未收录**该字符串（抽取丢 tooltip），不能作快照内逐字摘录 → 记入 `E-020` 解读，置信度中
  2. `B005` 正文与 HTML 均无显式缓存 TTL；页面自身指向 `/gemini-api/docs/generate-content/caching`（快照行 1200-1203）→ 缺口，受 6 源上限不补档
  3. `B006` 快照行 2173-2176：Gemini 批任务 48 小时过期 → 记入 `E-025`
- 打开并存档: 无新增（仅读既有存档）
- 弃用: 无
