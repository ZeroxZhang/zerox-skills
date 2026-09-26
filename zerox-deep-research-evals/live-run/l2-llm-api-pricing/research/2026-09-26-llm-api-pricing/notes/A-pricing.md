# A-计价结构

## E-001 Anthropic 把缓存拆成写入与命中两个价

- 论断: Anthropic 的计价表把缓存拆成「5 分钟写入」「1 小时写入」「命中与刷新」三个独立价，与 input/output 并列
- 来源: `A001` · 定位: 计价表表头
- 逐字摘录:

  > | Name | Input | Output | 5m writes | 1h writes | Hits and refreshes |

- 解读: 表头明示六列结构。这意味着「缓存价」在 Anthropic 是**三个数**，不是一个数——任何只比「缓存价格」一个数的对比都丢信息。
- 置信度: 高
- 用于: [1]
- 交叉来源: `A002`

## E-002 Anthropic 缓存价相对 input 的倍率

- 论断: Claude Fable 5.1 的缓存 5m 写入价为 input 的 1.25 倍、1h 写入为 2 倍、命中约为 input 的 0.025 倍
- 来源: `A001` · 定位: 计价表 Claude Fable 5.1 行
- 逐字摘录:

  > | Claude Fable 5.1For demanding reasoning and long-horizon agentic work | $10/MTok | $50/ MTok | $12.50/ MTok | $20/ MTok | $0.25/ MTok |

- 解读: 推断倍率 = 12.5/10 = **1.25**、20/10 = **2**、0.25/10 = **0.025**。这是**推断**，表内未写倍率。对 Opus 5.5（$4 → $5 / $8 / $0.20）则为 1.25 / 2 / **0.05**——写入倍率一致，**命中倍率不一致**（0.025 vs 0.05）。故预算测算必须按具体型号取数，不能套用单一比例。
- 置信度: 高
- 用于: [2]
- 交叉来源: none

## E-003 OpenAI 把长短上下文拆成两套价

- 论断: OpenAI 计价表为每个模型同时给出「Short context」与「Long context」两套价格，每套含 Input / Cached input / Cache writes / Output 四项
- 来源: `A002` · 定位: Flagship models 计价表表头
- 逐字摘录:

  > | Model | Input | Cached input | Cache writes | Output | Input | Cached input | Cache writes | Output |

- 解读: 与 Anthropic 的六列结构不同源。Anthropic 表内**没有**长上下文分档列，OpenAI 有。因此「input 单价」必须先确认是短上下文还是长上下文口径才能比。
- 置信度: 高
- 用于: [3]
- 交叉来源: `A001`

## E-004 OpenAI 长上下文加价的具体倍率

- 论断: gpt-6-astra 短上下文 input $10.00，长上下文 input $20.00，即 2 倍；缓存写入同为 2 倍
- 来源: `A002` · 定位: Flagship models 表 gpt-6-astra 行
- 逐字摘录:

  > | gpt-6-astra | $10.00 | $1.00 | $12.50 | $50.00 | $20.00 | $2.00 | $25.00 | $75.00 |

- 解读: 左半四列为短上下文（10 / 1 / 12.5 / 50），右半四列为长上下文（20 / 2 / 25 / 75）。output 从 50 → 75 为 1.5 倍，与 input 的 2 倍不同。**推断**：加价倍率按 token 类型分别设定，不能用一个统一系数换算。
- 置信度: 高
- 用于: [3]
- 交叉来源: none

## E-005 Gemini 的缓存是「按小时存储」计价

- 论断: Gemini 的 context caching 另有按小时收取的存储费（$4.50 / 1,000,000 tokens per hour），与按 token 的缓存价并列
- 来源: `A005` · 定位: 某模型的 Context caching price 行
- 逐字摘录:

  > | Context caching price | Not available | $0.20, prompts<= 200k tokens$0.40, prompts > 200k$4.50 / 1,000,000 tokens per hour (storage price) |

- 解读: 这是与 Anthropic / OpenAI **根本不同**的计价维度：Gemini 把缓存当成占用存储的资源按小时收费。把三家的「缓存价」并排放进一张表而不标注计价维度，属于口径错误。
- 置信度: 高
- 用于: [4]
- 交叉来源: `A001` `A002`

## E-006 Gemini 的 output 价含 thinking tokens

- 论断: Gemini 的 output 价格明确包含 thinking tokens
- 来源: `A005` · 定位: 某模型的 Output price 行
- 逐字摘录:

  > | Output price (including thinking tokens) | Not available | $12.00, prompts<= 200k tokens$18.00, prompts > 200k |

- 解读: 这是一个隐蔽的口径差异。若另两家的 thinking / reasoning tokens 单独计费或不计费，则同样「output 单价」的数字背后是不同的计费 token 集合。**推断**：预算测算必须先统一「output 是否含思考 token」的口径。
- 置信度: 高
- 用于: [5]
- 交叉来源: `A001` `A002`
