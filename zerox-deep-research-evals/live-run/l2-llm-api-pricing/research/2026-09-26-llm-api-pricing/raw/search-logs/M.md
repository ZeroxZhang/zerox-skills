# 检索日志 · M

## 2026-09-26T18:45:00+08:00 · 能力盘点

- 本环境能力：
  - 网页搜索工具（WebSearch）：**返回空结果，不可用**
  - 网页抓取：`curl`/`urllib` 可拿原始字节（script 路径，保真）
  - WebFetch 工具：可用，但返回**模型处理过的摘要**（完整度只能标 `summary`，不作逐字摘录依据）
  - 文件读写 / 代码执行：可用（可把文件直接下载到磁盘）
  - 子代理：可用
- 降级决定：发现渠道用 Brave 搜索页（HTTP）+ 已知权威 URL；采集一律走 `capture_source.py`（script）。

## 2026-09-26T19:05:00+08:00 · brave-search(HTTP) — 受限

- 查询原文: `LLM API pricing comparison misleading cached input different meaning`
- 查询原文: `大模型 API 价格对比 口径 缓存 陷阱`
- 查询原文: `prompt caching pricing comparison`
- 结果: **HTTP 429 + 验证码挑战页**。按规范不绕过（不伪造、不重试刷量、不换 IP）。
- 处理: 记为**检索受限**。外部反面证据本轮未取得，写进「未解问题与信息缺口」。
- 替代做法: 反面证据改从已存一手文档内部的自相矛盾处提取（厂商自己的多套价格表与「including thinking tokens」这类口径声明），这类反证比二手批评更硬。

## 对抗性检验结论（基于一手文档内部反证）

- 反方观点最有力表述：「三家 API 价格可以直接并排比较，选最便宜的即可。」
- 该观点被以下一手事实削弱：OpenAI 同一模型有 Standard/Batch/Flex/Fast mode 四套价且长短上下文分档（A002）；Gemini 的缓存另收按小时存储费（A005）；Gemini 的 output 明示含 thinking tokens（A005）；OpenAI 文档明示 FedRAMP 端点加价 10%（A002）。
- 未被排除的可能：若某家的 thinking tokens 计费口径与另两家相同，则 E-006 的口径差异影响会缩小——需另查 Anthropic 侧的 thinking token 计费文档（本轮未取得）。
