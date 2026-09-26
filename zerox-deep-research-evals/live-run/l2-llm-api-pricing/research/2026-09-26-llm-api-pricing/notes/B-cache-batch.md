# B-缓存与批处理计价口径

## E-001 Anthropic 默认缓存 TTL 5 分钟

- 论断: Anthropic prompt caching 默认 TTL 为 5 分钟，缓存内容每次被使用都会免费刷新，不重收写入费。
- 来源: `B001` · 定位: Prompt caching 文档 · Lifetime 段（快照行 175）
- 逐字摘录:

  > By default, the cache has a 5-minute lifetime. The cache is refreshed for no additional cost each time the cached content is used.

- 解读: 「刷新免费」意味着活跃对话只要间隔小于 5 分钟，就只在首次写入时付 1.25× 写入费，后续命中按 0.1× 读价计费，不再产生写入费——这是 agent 高频轮次场景下缓存成本远低于直觉的原因。
- 置信度: 高
- 用于: none
- 交叉来源: none

## E-002 Anthropic TTL 计时从请求开始

- 论断: Anthropic 缓存寿命从发起写入或读取的请求开始计时（而非响应结束），生成耗时占用 TTL。
- 来源: `B001` · 定位: Prompt caching 文档 · Lifetime 段（快照行 177）
- 逐字摘录:

  > The lifetime is measured from the start of the request that writes or reads the cache entry, not from the end of its response. Time spent generating a response counts against the lifetime: if a response takes 4 minutes to stream, a follow-up request that reuses the same cached prefix must start within about 1 minute of that response completing.

- 解读: 对预算建模的含义：5 分钟 TTL 不是「响应后再有 5 分钟」，长生成会吃掉 TTL；agent 轮次要命中缓存，需按「写入请求开始 + 5 分钟 − 本次生成时长」估算剩余窗口。
- 置信度: 高
- 用于: none
- 交叉来源: none

## E-003 Anthropic 1 小时 TTL 与 2× 写入价

- 论断: Anthropic 提供 1 小时 TTL 选项，写入价为 2× 基础输入价；默认自动缓存是 5 分钟 TTL。
- 来源: `B001` · 定位: Prompt caching 文档 · TTL support 小节（快照行 324）
- 逐字摘录:

  > By default, automatic caching uses a 5-minute TTL. You can specify a 1-hour TTL at 2x the base input token price:

- 解读: 1h 写入比 5m 写入贵 60%（2× vs 1.25×）。是否值得取决于复用间隔分布；对间隔常超过 5 分钟、低于 1 小时的 side-agent 场景，1h TTL 换命中率通常划算（推断）。
- 置信度: 高
- 用于: none
- 交叉来源: none

## E-004 Anthropic 缓存读写乘数

- 论断: Anthropic 缓存计价乘数为：5 分钟写入 1.25×、1 小时写入 2×、命中读取 0.1×（部分模型有例外）。
- 来源: `B001` · 定位: Prompt caching 文档 · Pricing 节乘数列表（快照行 266-270）
- 逐字摘录:

  > - 5-minute cache write tokens are 1.25 times the base input tokens price
  > - 1-hour cache write tokens are 2 times the base input tokens price
  > - Cache read tokens are 0.1 times the base input tokens price (see the table footnote for per-model exceptions)

- 解读: 写入价 × 命中价构成「写一次、命中 N 次」的摊薄曲线；命中价 0.1× 是三家中最低的一档（对比 OpenAI 同为 0.1×、Google 显式缓存另按存储小时计费）。表格脚注还说明 Fable 5.1 / Mythos 5.1 命中价为 0.025×、Opus 5.5 为 0.05×，旗舰模型命中更便宜。
- 置信度: 高
- 用于: none
- 交叉来源: none

## E-005 Anthropic 最低可缓存长度

- 论断: Anthropic 按模型分档设置最低可缓存 prompt 长度：512 / 1,024 / 2,048 / 4,096 tokens 不等，Sonnet 5 等主力模型为 1,024。
- 来源: `B001` · 定位: Prompt caching 文档 · Cache limitations 小节（快照行 454-466）
- 逐字摘录:

  > On the Claude API, Claude Platform on AWS (/docs/en/build-with-claude/claude-platform-on-aws), Google Cloud (/docs/en/build-with-claude/claude-on-vertex-ai), and Microsoft Foundry (/docs/en/build-with-claude/claude-in-microsoft-foundry), the minimum cacheable prompt length is:
  > - 512 tokens for Claude Fable 5.1, Claude Mythos 5.1, Claude Opus 5.5, Claude Opus 5, Claude Fable 5, and Claude Mythos 5 (https://anthropic.com/glasswing)
  > - 2,048 tokens for Claude Mythos Preview (https://anthropic.com/glasswing) and Claude Opus 4.7
  > - 4,096 tokens for Claude Opus 4.6 and Claude Opus 4.5
  > - 1,024 tokens for Claude Opus 4.8, Claude Sonnet 5, Claude Sonnet 4.6, Claude Sonnet 4.5, Claude Opus 4.1 (retired, except on Bedrock and Google Cloud (/docs/en/about-claude/model-deprecations)), Claude Opus 4 (retired, except on Google Cloud (/docs/en/about-claude/model-deprecations)), and Claude Sonnet 4 (retired, except on Bedrock and Google Cloud (/docs/en/about-claude/model-deprecations))
  > - 4,096 tokens for Claude Haiku 4.5
  > - 2,048 tokens for Claude Haiku 3.5 (retired, except on Bedrock and Google Cloud (/docs/en/about-claude/model-deprecations))

- 解读: 最低长度随模型档位变化（新旗舰 512、Sonnet 5/4.x 1,024、Haiku 4.5 4,096），做矩阵时不能只写一个数，须绑定模型。系统提示+工具定义不足阈值的 agent 会静默不缓存（见 E-006）。
- 置信度: 高
- 用于: none
- 交叉来源: none

## E-006 Anthropic 低于最低长度的静默行为

- 论断: 低于最低可缓存长度的请求不缓存也不报错，需靠 usage 字段核验。
- 来源: `B001` · 定位: Prompt caching 文档 · Cache limitations 小节（快照行 470）
- 逐字摘录:

  > Shorter prompts cannot be cached, even if marked with cache_control. Any requests to cache fewer than this number of tokens will be processed without caching, and no error is returned.

- 解读: 计费口径上的陷阱：预算表假设「已打 cache_control 即按缓存价」会低估成本；实际短前缀按全价 input 计费。核验手段是响应 usage 中 cache_creation_input_tokens 与 cache_read_input_tokens 是否为 0（同段后文）。
- 置信度: 高
- 用于: none
- 交叉来源: none

## E-007 Anthropic Sonnet 5 缓存价目

- 论断: Sonnet 5 每百万 tokens：输入 $2、输出 $10、5m 写入 $2.50、1h 写入 $4、命中 $0.20。
- 来源: `B001` · 定位: Prompt caching 文档 · Pricing 表（表头快照行 197-198：Name/Input/Output/5m writes/1h writes/Hits and refreshes；本行快照行 210）
- 逐字摘录:

  > | Claude Sonnet 5The best combination of speed and intelligence | $2/ MTok | $10/ MTok | $2.50/ MTok | $4/ MTok | $0.20/ MTok |

- 解读: 与乘数表自洽：$2 × 1.25 = $2.50（5m 写）、$2 × 2 = $4（1h 写）、$2 × 0.1 = $0.20（命中）。写入 $2.50 与输入 $2 相比仅高 25%，一次写入 + 一次命中的合计 $2.70，低于两次未缓存输入 $4——缓存的盈亏平衡点是「同一前缀至少复用一次」（推断）。
- 置信度: 高
- 用于: none
- 交叉来源: none

## E-008 Anthropic Batch 五折

- 论断: Anthropic Message Batches API 全部用量按标准价 50% 计费。
- 来源: `B002` · 定位: Message Batches 文档 · Pricing 节（快照行 210）
- 逐字摘录:

  > The Batches API offers significant cost savings. All usage is charged at 50% of the standard API prices.

- 解读: 「All usage」在 FAQ 中进一步明确覆盖 input、output 与 special tokens。批处理是无条件按完成请求计费的折扣（非营销价），对延迟不敏感的离线 agent 任务直接砍半。
- 置信度: 高
- 用于: none
- 交叉来源: `A001`

## E-009 Anthropic Batch 24 小时窗口

- 论断: Anthropic Batch 多数 1 小时内完成，最迟 24 小时；超时未完成的批次过期。
- 来源: `B002` · 定位: Message Batches 文档 · Batch limitations（快照行 163）
- 逐字摘录:

  > - The system processes each batch as fast as possible, with most batches completing within 1 hour. You can access batch results when all messages have completed or after 24 hours, whichever comes first. Batches expire if processing does not complete within 24 hours.

- 解读: 生效条件即「24 小时完成窗口」：折扣只有在请求于窗口内执行才产生；过期请求不计费（同文档 expired 状态行）。另有上限 100,000 条请求或 256 MB（同小节），超限须拆批。
- 置信度: 高
- 用于: none
- 交叉来源: none

## E-010 Anthropic 缓存与批处理叠加

- 论断: Anthropic 的缓存折扣与 Batch 折扣可叠加，但批内缓存命中为 best-effort，命中率约 30%-98%。
- 来源: `B002` · 定位: Message Batches 文档 · Using prompt caching with Message Batches（快照行 497）
- 逐字摘录:

  > The Message Batches API supports prompt caching, allowing you to potentially reduce costs and processing time for batch requests. The pricing discounts from prompt caching and Message Batches can stack, providing even greater cost savings when both features are used together. However, because batch requests are processed asynchronously and concurrently, cache hits are provided on a best-effort basis. Users typically experience cache hit rates ranging from 30% to 98%, depending on their traffic patterns.

- 解读: 叠加的量化口径：写入 1.25×、命中 0.1× 的乘数再乘 50%，即批处理下 5m 写入实付 0.625× 普通输入价、命中实付 0.05×。但命中率区间 30%-98% 方差极大，预算建模不能默认全命中（推断）。计价乘数可叠加这一点同时见 `A001`「Batch API and prompt caching discounts can be combined」。
- 置信度: 高
- 用于: none
- 交叉来源: `A001`

## E-011 Anthropic 长上下文不加价

- 论断: Claude 4.6 及之后模型的 1M 上下文按标准价计费，长上下文不加价，缓存与批处理折扣按标准比率贯穿全窗口。
- 来源: `A001` · 定位: Anthropic API Pricing · Long context pricing 节（快照行 371）
- 逐字摘录:

  > Claude 4.6 and later models and Claude Mythos Preview (https://anthropic.com/glasswing) include the full 1M token context window (/docs/en/build-with-claude/context-windows) at standard pricing. (A 900k-token request is billed at the same per-token rate as a 9k-token request.) Prompt caching and batch processing discounts apply at standard rates across the full context window.

- 解读: 对比矩阵要点：Anthropic 主力新模型没有「>200K 加价档」，与 Google（>200k 翻倍，见 E-027）、OpenAI（>272K 双列价，见 E-020）不同口径。旧模型是否另有分档，本行未取到原文（缺口）。
- 置信度: 高
- 用于: none
- 交叉来源: none

## E-012 OpenAI 缓存命中最高降 90%

- 论断: OpenAI 缓存命中按模型的 cached-input 优惠价计费，折扣最高可达 90%。
- 来源: `B003` · 定位: Prompt caching 指南 · Benefits 列表（快照行 1867）
- 逐字摘录:

  > - Cheaper input tokens: Pay the model’s reduced cached-input rate for reused tokens, discounted up to 90%.

- 解读: 「up to 90%」与价目表一致：GPT-6 系列 cached input = 输入价的 10%（$0.20 vs $2.00，见 E-020）。写「最高 90%」而非固定 90%，是因为早期模型 cached-input 率由模型决定（见 B003 摘要表「Model-dependent cached-input rate」）。
- 置信度: 高
- 用于: none
- 交叉来源: `A002`

## E-013 OpenAI 缓存写 1.25× 读 0.1×

- 论断: GPT-5.6 及之后模型缓存写入为标准输入价 1.25×，读取为 0.1×。
- 来源: `B003` · 定位: Prompt caching 指南 · Pricing 段（快照行 2022）
- 逐字摘录:

  > For GPT-5.6 and later, cache writes cost 1.25× the standard, uncached input-token rate. It is worth incurring this charge when you know a prefix will be reused, because subsequent reads cost only 0.1× that rate.

- 解读: 与 Anthropic 完全同构（1.25× 写 / 0.1× 读），两家矩阵可并列；文中给出的成本例：写一次+复用一次合计 1.35×，十次请求 2.15× vs 不缓存 10×。早期模型（GPT-5.6 前）无额外写入费、读取率为模型自定（B003 摘要表）。
- 置信度: 高
- 用于: none
- 交叉来源: none

## E-014 OpenAI 最低缓存长度 1024

- 论断: OpenAI 最低可缓存前缀长度：GPT-5.6 及之后为 1,024 tokens，更早模型随请求配置变化。
- 来源: `B003` · 定位: Prompt caching 指南 · Minimum cacheable length 段（快照行 2016）
- 逐字摘录:

  > The minimum cacheable prompt length is 1,024 tokens for GPT-5.6 and later and varies by request settings for earlier models.

- 解读: 同段还说明 OpenAI 隐藏系统内容的 token 不计入该最低长度。与 Anthropic 的按模型 512-4,096 分档相比，OpenAI 只对新模型给单一阈值；「随请求设置变化」意味着早期模型的阈值无法在价目表静态化（推断：预算里只能按新模型 1,024 取值并标注）。
- 置信度: 高
- 用于: none
- 交叉来源: none

## E-015 OpenAI 缓存 TTL 30 分钟

- 论断: OpenAI 缓存最小存活期由 prompt_cache_options.ttl 控制，唯一且默认取值 30m；命中会续期。
- 来源: `B003` · 定位: Prompt caching 指南 · Cache lifetime 节（快照行 2261）
- 逐字摘录:

  > Use prompt_cache_options.ttl to control the minimum cache lifetime. The only supported value, 30m, is also the default. A cached prefix remains eligible for reuse for 30 minutes after its most recent write or reuse, though OpenAI may retain it longer.

- 解读: TTL 口径为「最近一次写入或复用后 30 分钟」——比 Anthropic 5 分钟长，且复用即续期，轮次密集的 agent 只要间隔 <30 分钟即可持续命中；不可配置更长，需要更长窗口得靠扩展保留（E-016）。
- 置信度: 高
- 用于: none
- 交叉来源: none

## E-016 OpenAI 扩展保留 24h

- 论断: 部分早期模型可用 prompt_cache_retention 设为 24h 扩展保留（通常约 30 分钟可用，最长 24 小时）。
- 来源: `B003` · 定位: Prompt caching 指南 · Cache lifetime 节 retention 列表（快照行 2269）
- 逐字摘录:

  > - 24h: Extended retention typically keeps entries available for around 30 minutes and can retain them for up to 24 hours.

- 解读: 「通常约 30 分钟」是关键限定：24h 是保留上限而非命中保证，不能按 24 小时必命中建模（推断）。扩展保留仅适用于 gpt-5.5/5.x/5/4.1 等列出的模型，不适用于 GPT-6 系列（同节表注）。
- 置信度: 高
- 用于: none
- 交叉来源: none

## E-017 OpenAI Batch 五折与 24h 周期

- 论断: OpenAI Batch API 为同步 API 五折、独立高限额池、24 小时完成周期。
- 来源: `B004` · 定位: Batch 指南 · 开篇（快照行 1873）
- 逐字摘录:

  > Learn how to use OpenAI’s Batch API to send asynchronous groups of requests with 50% lower costs, a separate pool of significantly higher rate limits, and a clear 24-hour turnaround time.

- 解读: 折扣生效条件：完成窗口目前只能设 24h（同文档 completion window 段）；价目表 Batch 列与 Standard 列同模型为半价（如 gpt-6-sol 输入 $2.00 → Batch $1.00，见 E-020 同表），cached input 与 cache writes 在 Batch 列同样给出，即缓存价随批处理同比例减半。
- 置信度: 高
- 用于: none
- 交叉来源: `A002`

## E-018 OpenAI Batch 模型支持条件

- 论断: Batch API 并非所有模型都可用，需查模型文档确认支持。
- 来源: `B004` · 定位: Batch 指南 · Batch expiration 前的模型支持段（快照行 2775）
- 逐字摘录:

  > The Batch API is widely available across most of our models, but not all. Please refer to the model reference docs (/api/docs/models) to ensure the model you’re using supports the Batch API.

- 解读: 批处理折扣的生效条件之一：模型不支持则无法走 Batch 价；另有数据驻留限制（同段：GPT-6 Sol/Luna 的 EU data residency 仅 Standard 处理可用）。预算矩阵的 Batch 行需标注「模型适用性」列。
- 置信度: 高
- 用于: none
- 交叉来源: none

## E-019 OpenAI Batch 过期计费规则

- 论断: OpenAI Batch 超 24 小时未完成则过期：未完成请求取消不计费，已完成请求按消耗 token 计费。
- 来源: `B004` · 定位: Batch 指南 · Batch expiration 节（快照行 2791）
- 逐字摘录:

  > Batches that do not complete in time eventually move to an expired state; unfinished requests within that batch are cancelled, and any responses to completed requests are made available via the batch’s output file. You will be charged for tokens consumed from any completed requests.

- 解读: 与 Anthropic 一致的「按完成计费、过期不罚」口径；预算里 Batch 折扣的边界条件是 24h 窗口内被调度执行，而非提交即锁定。
- 置信度: 高
- 用于: none
- 交叉来源: none

## E-020 OpenAI 短长上下文双列价

- 论断: OpenAI 主力模型价目按 Short context / Long context 双列，长上下文各列约为短上下文 2 倍。
- 来源: `A002` · 定位: OpenAI API Pricing · Flagship models · Standard 表（快照行 1833-1837）
- 逐字摘录:

  > |  | Short context | Long context |
  > | Model | Input | Cached input | Cache writes | Output | Input | Cached input | Cache writes | Output |
  > | gpt-6-astra | $10.00 | $1.00 | $12.50 | $50.00 | $20.00 | $2.00 | $25.00 | $75.00 |
  > | gpt-6-sol | $2.00 | $0.20 | $2.50 | $10.00 | $4.00 | $0.40 | $5.00 | $15.00 |
  > | gpt-6-luna | $0.10 | $0.01 | $0.125 | $0.50 | $0.20 | $0.02 | $0.25 | $0.75 |

- 解读: 双列价严格 2×（input/output/cached/cache-writes 全列同比），缓存乘数在长上下文档同样成立。**分界阈值**：快照（抽取正文）未收录阈值定义，但在同一来源的原始 HTML（`raw/files/A002-openai-pricing.html`）中，Long context 列头的 tooltip 文本为「>272K input tokens」，且模型数据里出现「gpt-5.5 (<272K context length)」——即分界为 272K 输入 tokens；该字符串只存在于原始 HTML、不在快照正文，无法作快照内逐字摘录，故阈值按旁证处理（置信度：中）。Batch/Flex 列同样双列（快照行 1849-1864）。
- 置信度: 高（双列 2×）；阈值 272K：中
- 用于: none
- 交叉来源: none

## E-021 Google 隐式缓存默认开启

- 论断: Gemini API 对 2.5 及更新模型默认开启隐式缓存，命中自动降价，无需配置。
- 来源: `B005` · 定位: Context Caching 文档 · Implicit caching 节（快照行 1207-1212）
- 逐字摘录:

  > Implicit caching is enabled by default for all Gemini 2.5 and newer models. It is supported for both stateful (/gemini-api/docs/text-generation#multi-turn-conversations) (using previous_interaction_id) and stateless (/gemini-api/docs/text-generation#stateless-conversations) conversation modes. We automatically pass on cost savings if your request hits caches. There is nothing you need to do in order to enable this. The minimum input token count for context caching is listed in the following table for each model:

- 解读: Google 的隐式缓存没有用户可见的写入价/TTL 口径——「自动传递折扣」但未给折扣幅度（本页与 A005 价目页均未给隐式命中的具体倍率，属缺口）。用户显式管理 TTL 的缓存对象在另一页面（快照行 1200-1203 指向 generateContent API 的 caching 页），本轮 6 源预算内未采档（缺口）。
- 置信度: 高（默认开启与自动折扣）；隐式命中折扣幅度：未取到
- 用于: none
- 交叉来源: none

## E-022 Google 隐式缓存最低 token

- 论断: Gemini 各模型隐式缓存最低输入长度：3.x/3.1 系列 4,096 tokens，2.5 系列 2,048 tokens。
- 来源: `B005` · 定位: Context Caching 文档 · Implicit caching 节最低 token 表（快照行 1214-1228）
- 逐字摘录:

  > | Model | Min token limit |
  > | Gemini 3.8 Flash | 4,096 |
  > | Gemini 3.7 Flash | 4,096 |
  > | Gemini 3.6 Flash | 4,096 |
  > | Gemini 3.5 Flash | 4,096 |
  > | Gemini 3.1 Pro Preview | 4,096 |
  > | Gemini 2.5 Flash | 2,048 |
  > | Gemini 2.5 Pro | 2,048 |

- 解读: Google 的最低缓存长度（2,048/4,096）明显高于 OpenAI/Anthropic 新模型（1,024/512），短 system prompt + 小工具集的 agent 在 Google 上更难触发命中（推断）。
- 置信度: 高
- 用于: none
- 交叉来源: none

## E-023 Google 上下文缓存价与存储价

- 论断: Gemini 3.8 Flash 的上下文缓存 token 价 $0.075/百万（2027-01-01 起 $0.15），另按 $0.50/百万 tokens/小时收存储费（2027 起 $1.00）。
- 来源: `A005` · 定位: Gemini API Pricing · Gemini 3.8 Flash · Standard 表 Context caching price 行（快照行 1313）
- 逐字摘录:

  > | Context caching price | Free of charge | $0.075 through December 31, 2026.$0.15 starting January 1, 2027.$0.50 / 1,000,000 tokens per hour (storage price) through December 31, 2026.$1.00 / 1,000,000 tokens per hour (storage price) starting January 1, 2027. |

- 解读: Google 显式缓存是「命中 token 价 + 按小时存储费」的双轨计费，与 Anthropic/OpenAI 纯乘数模型不同：即使未命中，缓存对象只要存着就按小时计费，缓存的盈亏平衡还取决于存活时长（推断）。价目页还标注 Batch 行缓存价同规则减半（快照行 1349）。免费档免费、促销价 2026-12-31 截止，做年度预算须用 2027 年价。
- 置信度: 高
- 用于: none
- 交叉来源: none

## E-024 Google Batch 五折与 24h 目标

- 论断: Gemini Batch API 按标准价 50% 异步处理，目标周转 24 小时。
- 来源: `B006` · 定位: Batch API 文档 · 开篇（快照行 1199-1202）
- 逐字摘录:

  > The Gemini Batch API is designed to process large volumes of requests
  > asynchronously at 50% of the standard cost (/gemini-api/docs/pricing).
  > The target turnaround time is 24 hours, but in majority of cases, it is much
  > quicker.

- 解读: 技术细节节再次确认「50% of the standard interactive API cost」（快照行 3308-3309）。与 A005 Batch 行互证：Gemini 3.8 Flash 标准输入 $0.75、Batch 输入 $0.375，恰为一半。
- 置信度: 高
- 用于: none
- 交叉来源: `A005`

## E-025 Google Batch 48 小时过期

- 论断: Gemini 批任务运行或等待超过 48 小时即过期（JOB_STATE_EXPIRED），无结果可取。
- 来源: `B006` · 定位: Batch API 文档 · 状态说明（快照行 2173-2176）
- 逐字摘录:

  > - JOB_STATE_EXPIRED: The job has expired because it was running or pending
  > for more than 48 hours. The job will not have any results to retrieve.
  > You can try submitting the job again or splitting up
  > the requests into smaller batches.

- 解读: 三家批处理窗口不同：Google 目标 24h、硬过期 48h；Anthropic 与 OpenAI 均为 24h 过期。做「批处理生效条件」对比时应分列「目标周转」与「过期上限」两栏（推断：Google 过期前的请求执行情况按状态机理解不产生结果，B006 未逐条写计费细则，属口径缺口）。
- 置信度: 高
- 用于: none
- 交叉来源: none

## E-026 Google Batch 中的缓存计费

- 论断: Gemini 批处理支持上下文缓存，批内命中按标准上下文缓存价计费。
- 来源: `B006` · 定位: Batch API 文档 · Technical details · Caching 项（快照行 3317-3321）
- 逐字摘录:

  > - Caching: Context caching (/gemini-api/docs/caching) is supported
  > for batch requests. Reuse cached content by specifying the cached_content
  > resource name in the configuration of individual requests within your batch.
  > If a request in your batch results in a cache hit, you pay the
  > standard context caching rates (/gemini-api/docs/pricing).

- 解读: 与 Anthropic「折扣可叠加」不同，Google 明确写出缓存命中在批内按缓存价（而非批折扣后的 token 价另算）——缓存价与批处理价的关系需按页内口径核对（A005 Batch 行显示缓存价也减半）。叠加规则各家不同，是矩阵中最易误比的一格。
- 置信度: 高
- 用于: none
- 交叉来源: `A005`

## E-027 Google 长上下文 200k 分界

- 论断: Gemini API 按 prompt ≤200k / >200k 分档计价，超 200k 输入翻倍（Gemini 3.1 Pro Preview：$2.00 → $4.00）。
- 来源: `A005` · 定位: Gemini API Pricing · Gemini 3.1 Pro Preview · Standard 表 Input price 行（快照行 2527）
- 逐字摘录:

  > | Input price | Not available | $2.00, prompts<= 200k tokens$4.00, prompts > 200k tokens |

- 解读: 分档影响的不只是输入：同模型 output 与 context caching 价同样按 ≤/>200k 双档（快照行 2531、2535）。注意不是所有模型都有双档——同页 Gemini 3.8 Flash Standard 只有单档价（快照行 1310），长上下文加价是模型特定的（推断）。
- 置信度: 高
- 用于: none
- 交叉来源: `A003`

## E-028 Vertex AI 200K 长上下文计价规则

- 论断: Vertex AI 口径：查询输入上下文长于 200K tokens 时，全部 token（输入与输出）按长上下文价计费。
- 来源: `A003` · 定位: Vertex AI Pricing · Gemini 模型价目表脚注（快照行 466）
- 逐字摘录:

  > * If a query input context is longer than 200K tokens, all tokens (input and output) are charged at long context rates.

- 解读: 关键口径：不是「只有超过 200K 的部分加价」，而是**整请求**全部 token 切到长上下文价——预算模型必须按整请求跳档计算。同页另一小节的措辞为「longer than or equal to 200K」（快照行 1718），200K 整点归属在文档内不一致，边界值按保守处理（推断）。
- 置信度: 高（阈值 200K 与整请求计费）；边界开闭：中
- 用于: none
- 交叉来源: `A005`

---

## 本轮缺口（供主线程合并时注意）

1. Google 显式缓存（cache 对象）的 TTL 取值范围（默认/最短/最长）未取到官方原文：`ai.google.dev/gemini-api/docs/caching` 现为隐式缓存页（`B005`），显式缓存正文在 `/gemini-api/docs/generate-content/caching`（`B005` 快照行 1200-1203 指明），受 6 源预算限制未采档。显式缓存的存储价已由 `A005` 覆盖。
2. OpenAI 长上下文分界 272K 只存在于 `A002` 原始 HTML 的 tooltip（`raw/files/A002-openai-pricing.html`），快照正文未收录，无法作快照内逐字摘录（见 E-020 解读）。
3. Google 隐式缓存命中的具体折扣幅度（相当于几折）三家官方文档均未在本轮来源中给出数值。
4. Anthropic 旧模型（Claude 4.5 及更早）的长上下文是否另有加价档，`A001` 只对 4.6+ 作出「标准价」声明，未取到旧模型表述。
