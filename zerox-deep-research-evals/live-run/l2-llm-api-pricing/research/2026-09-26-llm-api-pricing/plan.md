# 研究计划 · 大模型 API 计价口径

## 进度清单

- [x] 0 定级
- [x] 1 开题与建包
- [x] 2 计划确认（按直接开工处理，假设入 brief.md）
- [x] 3 迭代研究与存档
- [ ] 4 综合
- [ ] 5 质检
- [ ] 6 打包交付

## 子问题状态

| # | 子问题 | 当前置信度 | 已有证据（来源 ID） | 缺口 | 下一步 |
|---|---|---|---|---|---|
| Q1 | 基础单价与计价单位 | 高 | A001 A002 A003 A005 | — | 已答 |
| Q2 | 缓存口径 | 中 | A001 A002 A005 | TTL 与最低缓存长度的官方表述 | B 线 |
| Q3 | 长上下文加价 | 高 | A002 A005 | Anthropic 是否另有分档 | 已答（H2 待终局） |
| Q4 | 批处理折扣与生效条件 | 低 | — | 三家 batch 文档 | B 线 |
| Q5 | 隐藏加价项 | 中 | A002 A005 | Anthropic 的 thinking token 计费口径 | 待查 |

## 研究线

| 代号 | 主题 | 负责 | 范围边界 | 来源 ID 区间 | 状态 |
|---|---|---|---|---|---|
| M | 能力盘点、合并、对抗性检索、综合 | 主线程 | 不做专题深挖 | M001– | 进行中 |
| A | 三家官方计价表与分档 | 主线程 | 不碰缓存 TTL / batch 细则 | A001– | 完成 |
| B | 缓存与批处理口径细节 | 子代理 | 不碰基础单价 | B001– | 进行中 |

## 迭代日志

### 第 1 轮 · 2026-09-26

- **能力盘点**（见 `raw/search-logs/M.md`）：本会话 WebSearch 工具返回空结果；WebFetch 返回模型处理过的摘要（不能作逐字摘录依据）；`curl`/`urllib` 可拿原始字节。降级决定：发现渠道用 Brave 搜索页 + 已知权威 URL，采集一律走 `capture_source.py`。
- **学到什么**：三家的「缓存」计价维度不同——Anthropic 按 token 写读（5m/1h 写入 + 命中），OpenAI 分短/长上下文各给 Input / Cached input / Cache writes / Output 四列，Gemini 另收按小时的存储费。**口径不可直接比**。
- **假设**：H1（缓存价格不可直接比）被强加强；H2（长上下文加价仅 OpenAI/Gemini 显式分档）被 A002、A005 印证，Anthropic 侧待终局确认。
- **矛盾**：同一厂商页面内并列多套价格（OpenAI 的 Standard / Batch / Flex / Fast mode 四个 tab；Gemini 的 Free Tier / Paid Tier），单看一个 tab 会得出错误结论。
- **二阶线索**：OpenAI 文档提到「FedRAMP endpoints are charged a 10% uplift」——合规部署的隐藏加价项，预算测算易漏。
- **还缺什么**：三家 batch 折扣率；缓存 TTL 与最低缓存长度；Anthropic thinking token 计费口径。
- **下一轮决定**：B 线并行查缓存与批处理细则；主线程做对抗性检索（查「API pricing comparison misleading」类批评）。

### 第 2 轮 · 2026-09-26

- 合并 B 线成果；去重；更新 sources.md。
- 对抗性检验完成；矛盾点（thinking token 计费、Free Tier 可用性）写进「分歧与不确定性」。
