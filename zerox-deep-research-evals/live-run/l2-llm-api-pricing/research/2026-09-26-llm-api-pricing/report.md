# 大模型 API 计价口径对比：为预算测算建立可比口径

2026-09-26 · 截至 2026-09-26 · 研究包 `2026-09-26-llm-api-pricing`

## 执行摘要

**直接回答**：三家大模型 API 的价格**不能直接并排比较**。基础单价可以比（同一单位、同一 token 类型），但「缓存价格」在三家是三种不同商品，「output 单价」的计费 token 集合也不同。要做预算，必须先统一三个口径维度——缓存计价机制、长上下文分档、thinking token 归属——再比数字。

**关键结论**

1. **缓存不可直接比**：Anthropic 按 token 收写入费（5 分钟 / 1 小时两档）+ 命中费；OpenAI 收 cache write + cached input；Gemini 另收**按小时的存储费**。三者是三种商品。（置信度：高）[1][2][4][5][7][9]
2. **批处理是少数可直接比的一项**：三家都按标准价的 50% 计费。（置信度：高）[6][8][10]
3. **长上下文加价的分档方式不同**：OpenAI 与 Gemini 显式分「短/长上下文」两套价（input 约 2 倍），Anthropic 的标准计价表内无此分档列。（置信度：高）[2][4]
4. **output 的计费集合可能不同**：Gemini 明示 output 价**包含 thinking tokens**，另两家的计价表内未见此声明。（置信度：中）[4]
5. **隐藏加价项真实存在**：OpenAI 文档明示 FedRAMP 端点加价 10%。（置信度：高）[2]

## 关键发现

### 1. 「缓存」是三种商品，不是一个价目

**结论** 三家的缓存计价维度不同，把「缓存价」并排进一张表而不标注维度属于口径错误。[1][2][4]

**证据** 三家的计价结构分别是：

| | Anthropic [1] | OpenAI [2] | Gemini [4] |
|---|---|---|---|
| 写入 | 按 token，5m / 1h 两档价 | 按 token，cache writes 一档 | 按 token，cache token 价 |
| 命中 | 按 token（hits and refreshes） | 按 token（cached input） | 按 token |
| 存储 | 无 | 无 | **按小时收存储费** |
| 分档 | 表内不按上下文长度分 | 短/长上下文两套价 | ≤200k / >200k 两套价 |

换算成「相对各自短上下文 input 牌价的倍数」后（见 `analysis/normalize_cache_cost.py`，可复现）：

| 方案 | hit=0 | hit=0.5 | hit=1.0 | hit=2.0 |
|---|---|---|---|---|
| Anthropic | 1.250 | 1.262 | 1.275 | 1.300 |
| OpenAI | 1.250 | 1.300 | 1.350 | 1.450 |
| Gemini | 2.350 | 2.350 | 2.350 | 2.350 |

Gemini 一行与命中次数无关，因为它按存储小时计费；另两家随命中次数线性上升。**命中率越高，机制差异越致命。**

**对决策意味着什么** 缓存复用率高的 agent 负载（长系统提示、多轮工具调用）必须按命中次数建模，不能按「缓存打了几折」估算。Gemini 的存储费使短时高频复用与长时低频复用的成本曲线完全不同。

### 2. 批处理是可直接比的一项

**结论** 三家批处理折扣一致，都是标准价的 50%。[6][8][10]

**证据** Anthropic：「cutting costs by 50%」[6]；Gemini：「asynchronously at 50% of the standard cost」[10]；OpenAI 的批处理与 Flex 分列独立价格表[8]。Gemini 另注明目标周转 24 小时[10]。

**对决策意味着什么** 折扣率不是选型差异点；差异在周转时间与可用性条件。预算测算可以统一按 50% 计，但要另记周转假设。

### 3. 长上下文加价：分档方式不同，倍率却相近

**结论** OpenAI 与 Gemini 的长上下文 input 约为短上下文的 2 倍、output 约 1.5 倍；Anthropic 的标准表内无此分档。[2][4]

**证据** OpenAI gpt-6-astra：短上下文 `$10.00 / $1.00 / $12.50 / $50.00`，长上下文 `$20.00 / $2.00 / $25.00 / $75.00`[2]。Gemini 示例型号：input `$2.00 / $4.00`，output `$12.00 / $18.00`[4]。

**对决策意味着什么** 若负载经常超过 200K token，长上下文价才是真实成本；用短上下文牌价做预算会低估约一倍。

### 4. thinking tokens 的归属可能不同

**结论** Gemini 明示 output 价含 thinking tokens；另两家的计价表内未见同等声明。[4]

**证据** Gemini 的计价行写作「Output price (including thinking tokens)」[4]。Anthropic 与 OpenAI 的计价表列名分别为 Output 与 Output，未见包含声明[1][2]。

**对决策意味着什么** 若某家的 reasoning token 另计费，则「output 单价」数字背后的计费 token 集合不同。这是本次**未能完全查清**的一项，见「未解问题」。

## 分歧与不确定性

- **「哪家更便宜」没有单一答案**。同一份负载在三家的成本排序取决于：上下文长度、缓存命中率、output 占比、thinking token 占比、批处理可用性。任一变量换档都可能翻转排序。
- **同厂页面内并列多套价格**：OpenAI 的 Standard / Batch / Flex / Fast mode 是四套价[2]；Gemini 分 Free Tier 与 Paid Tier[4]。只看一个 tab 会得出错误结论。这不是来源冲突，是来源本身给的是条件价格。
- **反方观点的最有力表述**：「三家 API 价格可以直接并排比较，选最便宜的即可。」该观点被上述一手事实系统性削弱——尤其被 Gemini 的按小时存储费[9]与「including thinking tokens」[4]这两处**厂商自己的口径声明**削弱。
- **外部反面证据本轮未取得**：对「API pricing comparison misleading」的外部检索遭遇 HTTP 429 + 验证码，按规范不绕过，已记入检索日志。反证改用一手文档内部的口径冲突，这类反证更硬。

## 启示与建议 / 下一步

1. **先建口径表，再比价格**。预算测算的第一张表应该是「计价维度对照」（缓存怎么计、长上下文怎么分、thinking token 算谁的），第二张才是价格。`analysis/normalize_cache_cost.py` 给出可复现的换算框架。
2. **按命中次数而不是「缓存折扣」建模**。对多轮 agent 负载，把缓存命中次数设为独立变量做敏感性分析；本研究包的换算表已给出 hit=0/0.5/1/2 四档。
3. **长上下文价单独建模**。若负载经常 >200K token，用长上下文牌价；否则预算会低估约一倍。
4. **下一步值得做**：查清三家 thinking / reasoning token 的计费口径（本次未决）；用真实负载的 token 构成跑一次三方案成本模拟；核对 FedRAMP 类合规加价是否适用于目标部署。

## 未解问题与信息缺口

- **thinking tokens 的计费归属**：Gemini 明示含在 output 价内[4]；Anthropic 与 OpenAI 的计价表内未见声明。试过：通读 A001/A002 计价表全表。未找到明确表述。**什么样的新证据会改变结论**：任一家文档明确写出 reasoning/thinking token 是否计费、按什么费率。
- **Anthropic 是否另有长上下文分档**：A001 计价表内无分档列，但未穷尽其全部文档页面。若存在 >200K 分档表，结论 3 需修订。
- **外部第三方的成本对比批评**：检索受限（HTTP 429 + 验证码，未绕过），未取得。试过 3 条查询，均被限流。
- **Vertex AI 与 Gemini API 的价格是否一致**：本次以 Gemini API 价[4]为主，Vertex AI 定价[3]仅作对照取数，未逐项核对。两者是不同入口，做企业级预算时必须分清走哪一个。

## 方法与局限

- 检索范围与时间：2026-09-26 当日；检索次数 3 段日志 / 5 条查询；研究线 M / A / B
- **能力盘点与降级**（本环境）：内置网页搜索工具返回空结果，不可用；`WebFetch` 返回的是模型处理过的摘要（不能作逐字摘录依据）；`curl`/`urllib` 可拿原始字节。降级决定：发现渠道用 Brave 搜索页（HTTP）+ 已知权威 URL，**采集一律走 `capture_source.py`（script 路径）**，保证读到的就是存下的。
- 主要来源类型：**全部为一手官方文档**（10 个来源中 9 个为厂商官方文档），无二手转述作为关键结论依据。
- 无法访问的内容：`https://openai.com/api/pricing/` 返回 HTTP 403，脚本报错退出、**未做任何绕过**，仅登记元数据（A004）。同主题内容已由 `platform.openai.com/docs/pricing` 完整取得。
- 检索受限：Brave 搜索在对抗性检索阶段返回 HTTP 429 + 验证码，未绕过、未重试刷量。外部反面证据因此缺席。
- **采纳的假设**（见 `brief.md`）：预算测算假设月度负载按 input 60% / output 40% 的 token 构成；全部按 USD 原价、不做汇率换算；按 2026-09-26 现行计价、不预测调价。
- **局限**：价格随厂商调价而变，全部数字标注获取日期；本研究比的是**计价口径**，不是模型能力或性价比；未覆盖微调价、企业协议价、第三方转售商定价。
- 计算可复现：`analysis/normalize_cache_cost.py`。

## 参考来源

- [1] Anthropic. Anthropic API Pricing. unknown. https://docs.anthropic.com/en/docs/about-claude/pricing. 访问 2026-09-26. 来源 ID `A001` 存档 [raw/sources/A001-anthropic-pricing.md](raw/sources/A001-anthropic-pricing.md)
- [2] OpenAI. OpenAI API Pricing. unknown. https://platform.openai.com/docs/pricing. 访问 2026-09-26. 来源 ID `A002` 存档 [raw/sources/A002-openai-pricing.md](raw/sources/A002-openai-pricing.md)
- [3] Google Cloud. Vertex AI Generative AI pricing. unknown. https://cloud.google.com/vertex-ai/generative-ai/pricing. 访问 2026-09-26. 来源 ID `A003` 存档 [raw/sources/A003-vertex-ai-pricing.md](raw/sources/A003-vertex-ai-pricing.md)
- [4] Google. Gemini API pricing. unknown. https://ai.google.dev/gemini-api/docs/pricing. 访问 2026-09-26. 来源 ID `A005` 存档 [raw/sources/A005-gemini-api-pricing.md](raw/sources/A005-gemini-api-pricing.md)
- [5] Anthropic. Prompt caching. unknown. https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching. 访问 2026-09-26. 来源 ID `B001` 存档 [raw/sources/B001-anthropic-prompt-caching.md](raw/sources/B001-anthropic-prompt-caching.md)
- [6] Anthropic. Batch Processing. unknown. https://docs.anthropic.com/en/docs/build-with-claude/batch-processing. 访问 2026-09-26. 来源 ID `B002` 存档 [raw/sources/B002-anthropic-batch-processing.md](raw/sources/B002-anthropic-batch-processing.md)
- [7] OpenAI. Prompt caching. unknown. https://platform.openai.com/docs/guides/prompt-caching. 访问 2026-09-26. 来源 ID `B003` 存档 [raw/sources/B003-openai-prompt-caching.md](raw/sources/B003-openai-prompt-caching.md)
- [8] OpenAI. Batch API. unknown. https://platform.openai.com/docs/guides/batch. 访问 2026-09-26. 来源 ID `B004` 存档 [raw/sources/B004-openai-batch-guide.md](raw/sources/B004-openai-batch-guide.md)
- [9] Google. Context caching. unknown. https://ai.google.dev/gemini-api/docs/caching. 访问 2026-09-26. 来源 ID `B005` 存档 [raw/sources/B005-gemini-caching.md](raw/sources/B005-gemini-caching.md)
- [10] Google. Gemini Batch API. unknown. https://ai.google.dev/gemini-api/docs/batch-api. 访问 2026-09-26. 来源 ID `B006` 存档 [raw/sources/B006-gemini-batch-api.md](raw/sources/B006-gemini-batch-api.md)
