#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把三家的缓存计价换算成同一口径，供 report.md 引用。

可复现：输入全部硬编码自研究包内快照，来源 ID 与定位写在注释里。
口径声明见 report.md「方法与局限」。

用法：python3 normalize_cache_cost.py
"""

# ── 输入数据（均取自 raw/sources/ 下的快照，逐字数字）────────────────
# A001: Claude Fable 5.1 行 —— | $10/MTok | $50/ MTok | $12.50/ MTok | $20/ MTok | $0.25/ MTok |
#       列：Input | Output | 5m writes | 1h writes | Hits and refreshes
ANTHROPIC = {
    "unit": "$/MTok",
    "input": 10.00, "output": 50.00,
    "cache_write_5m": 12.50, "cache_write_1h": 20.00, "cache_hit": 0.25,
    "thinking_tokens": "未在计价表内单列（待查）",
}

# A002: gpt-6-astra 行 —— | $10.00 | $1.00 | $12.50 | $50.00 | $20.00 | $2.00 | $25.00 | $75.00 |
#       列（短上下文）：Input | Cached input | Cache writes | Output
#       列（长上下文）：Input | Cached input | Cache writes | Output
OPENAI = {
    "unit": "$/1M tokens",
    "short": {"input": 10.00, "cached_input": 1.00, "cache_write": 12.50, "output": 50.00},
    "long":  {"input": 20.00, "cached_input": 2.00, "cache_write": 25.00, "output": 75.00},
    "thinking_tokens": "未在该表内单列（待查）",
}

# A005: 某模型 Context caching price 行 ——
#       | Context caching price | Not available | $0.20, prompts<= 200k tokens$0.40, prompts > 200k$4.50 / 1,000,000 tokens per hour (storage price) |
#       同组 Input price 行 —— | Input price | Not available | $2.00, prompts<= 200k tokens$4.00, prompts > 200k tokens |
#       同组 Output price 行 —— | Output price (including thinking tokens) | Not available | $12.00, prompts<= 200k tokens$18.00, prompts > 200k |
GEMINI = {
    "unit": "$/1M tokens",
    "short": {"input": 2.00, "output_incl_thinking": 12.00,
              "cache_token": 0.20, "cache_storage_per_hour": 4.50},
    "long":  {"input": 4.00, "output_incl_thinking": 18.00,
              "cache_token": 0.40, "cache_storage_per_hour": 4.50},
    "thinking_tokens": "包含在 output 价内（明示）",
}


def effective_cost_per_1m(hit_rate, hours=1.0):
    """每 1M prompt token 的 input 侧缓存有效单价（USD）。

    假设（写进报告）：
    - 1M token 先写入一次缓存，随后被命中 hit_rate 次（hit_rate 可 >1，如多轮复用）；
    - Gemini 的存储费按缓存占用 hours 小时计，与命中次数无关；
    - 只比 input 侧缓存机制，不计 output。
    """
    return {
        # Anthropic：一次 5m 写入 + 每次命中按 token 计费
        "Anthropic": ANTHROPIC["cache_write_5m"] + hit_rate * ANTHROPIC["cache_hit"],
        # OpenAI（短上下文）：一次 cache write + 每次命中按 cached input 计费
        "OpenAI(short)": OPENAI["short"]["cache_write"] + hit_rate * OPENAI["short"]["cached_input"],
        # Gemini：一次 cache token + 按小时存储（与命中次数无关）
        "Gemini(short)": GEMINI["short"]["cache_token"] + GEMINI["short"]["cache_storage_per_hour"] * hours,
    }


def main():
    print("口径：每 1M prompt token 的 input 侧缓存有效单价（USD）")
    print("假设：写入一次 + 命中 hit_rate 次；Gemini 存储费按 hours 小时计\n")

    print("【A】绝对单价（注意：三家取的不是同档型号，绝对值不可直接比！）")
    print("    Anthropic Fable 5.1  input $10/MTok；OpenAI gpt-6-astra input $10/1M；")
    print("    Gemini 为 A005 中 input $2.00 的示例型号——档位不同，仅演示计价结构。\n")
    header = "{:<16} {:>12} {:>12} {:>12} {:>12}".format(
        "方案", "hit=0", "hit=0.5", "hit=1.0", "hit=2.0")
    print(header)
    print("-" * len(header))
    for name in ["Anthropic", "OpenAI(short)", "Gemini(short)"]:
        row = []
        for hit in (0.0, 0.5, 1.0, 2.0):
            vals = effective_cost_per_1m(hit, hours=1.0)
            row.append("{:>12.3f}".format(vals[name]))
        print("{:<16} {}".format(name, "".join(row)))

    print("\n【B】可比口径：有效单价 ÷ 各自短上下文 input 牌价（倍数）")
    print("    消除了档位差异，只反映**缓存计价结构**的差异。\n")
    bases = {"Anthropic": ANTHROPIC["input"],
             "OpenAI(short)": OPENAI["short"]["input"],
             "Gemini(short)": GEMINI["short"]["input"]}
    print("{:<16} {}".format("方案", "".join("{:>12}".format("hit=" + h) for h in ("0", "0.5", "1.0", "2.0"))))
    print("-" * 64)
    for name in bases:
        row = []
        for hit in (0.0, 0.5, 1.0, 2.0):
            vals = effective_cost_per_1m(hit, hours=1.0)
            row.append("{:>12.3f}".format(vals[name] / bases[name]))
        print("{:<16} {}".format(name, "".join(row)))

    print("\n注：本表只比 input 侧缓存机制，不比 output。")
    print("注：Gemini 的 $4.50/1M tokens/hour 是存储费，与另两家的「按 token 写读」不是同一种商品。")
    print("注：hit_rate=2.0 表示该 1M token 被命中两次（如多轮对话复用），此时 Anthropic/OpenAI")
    print("     按命中次数计费，Gemini 按存储小时数计费——机制差异在高命中侧最明显。")

    print("\n── 分档倍率（直接来自快照，未做换算）──")
    print("Anthropic  Fable 5.1 : cache_write_5m/input = {:.2f}, write_1h/input = {:.2f}, hit/input = {:.3f}".format(
        ANTHROPIC["cache_write_5m"] / ANTHROPIC["input"],
        ANTHROPIC["cache_write_1h"] / ANTHROPIC["input"],
        ANTHROPIC["cache_hit"] / ANTHROPIC["input"]))
    print("OpenAI     gpt-6-astra: 长上下文 input/短上下文 input = {:.2f}, output 比 = {:.2f}".format(
        OPENAI["long"]["input"] / OPENAI["short"]["input"],
        OPENAI["long"]["output"] / OPENAI["short"]["output"]))
    print("Gemini     （示例型号）: 长上下文 input/短上下文 input = {:.2f}, output 比 = {:.2f}".format(
        GEMINI["long"]["input"] / GEMINI["short"]["input"],
        GEMINI["long"]["output_incl_thinking"] / GEMINI["short"]["output_incl_thinking"]))

    print("\n── 计价维度对照（不可直接比的原因）──")
    print("Anthropic 缓存维度: 按 token 写入（5m / 1h 两档）+ 按 token 命中")
    print("OpenAI    缓存维度: 按 token 写入 + 按 token 命中（cached input），且长短上下文两套价")
    print("Gemini    缓存维度: 按 token 命中 + **按小时存储费**（$4.50/1M tokens/hour）")


if __name__ == "__main__":
    main()
