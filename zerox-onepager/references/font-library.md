# 开源字体库与字体匹配

本文件是 zerox-onepager **字体选择的唯一事实源**：回答"用哪一款字体、从哪个 CDN 加载、加载失败怎么办"。
[typography.md](typography.md) 负责字号阶梯、行高、字重与 B1-B10 十种风格的映射，不负责选家族。两文件冲突时：**家族选择以本文件为准，字号/行高/字重以 typography.md 为准**。

Google Fonts 是可选增强，不是运行前提。任何方案都必须能在断网环境下回退到系统字体栈，且不得阻断 HTML 渲染。

> 边界：T4 宣传海报的字体强制覆盖（Tier C）以 [cross-reference.md](cross-reference.md) §2.1 为准；本文件的字体池为该覆盖提供候选，不复述覆盖规则。
>
> 本文所有 Google Fonts URL 均为完整 CSS2 地址，可直接粘贴进 @import 或 <link>。URL 中的 ; 用于分隔字重，不要删除。本文 61 条 Google Fonts URL（含目录、示例与加载片段）已于 2026-11-23 用 curl -s -o /dev/null -w "%{http_code}" 逐条校验，全部返回 200 且 CSS 中含目标 family；2 条 jsDelivr 备选 URL 同样为 200。

---

## 字体匹配流程（5 步）

**执行时机**：SKILL.md Phase 3.7——场景（S）与风格（B）确定之后、Phase 4 写 CSS 之前。产出物是 IR 的 typography 字段 + CSS 变量 + HTML 注释（见 Step 5），不是一堆散落的 CSS。

### Step 1 读语气 → 提取 3 个气质词

不要先挑字体再解释，先给内容"定调"。从蓝图与改写后的正文里找信号，映射成气质词：

| 素材信号（必须能在内容里指到具体句子/数字） | 高概率气质词 | 字体倾向 | 典型风格 |
|------|------|------|------|
| 有同比/环比/排名/基准线 | 精密、可信、冷静 | 等宽 + 中性无衬线 | B7, B2 |
| 有"发布/首发/速度/下一代/未来" | 未来、锐利、激进 | 几何科技 / 压缩展示 | B8, B1, B10 |
| 有"手作/自然/季节/慢/材质" | 温柔、质朴、呼吸 | 编辑衬线 / 人文衬线 | B3, B6 |
| 有观点、长引语、专栏式论证 | 编辑、克制、权威 | 编辑衬线 + 无衬线正文 | B3, B5, B7 |
| 有"活动/促销/倒计时/潮流" | 潮流、高能、年轻 | 压缩展示 / 几何无衬线 | B5, B10, T4 |
| 有代码/API/参数/日志/终端 | 精密、工程、冷静 | 等宽 + 几何无衬线 | B1, B8 |
| 有儿童/手绘/书信/节日祝福 | 温度、手作、亲密 | 手写（仅标题） | G6 场景 |

**硬性规则**：

1. 恰好 3 个词，且必须占满三个槽位：**体积词**（重/轻）、**温度词**（冷/暖）、**时代词**（传统/当代/未来）。缺哪个就用该 B 风格的默认气质补（默认气质见 typography.md 每个 B 小节的第一句）。
2. 每个词必须能指向素材里的一句证据。指不到的词删掉——它只是"看起来高级"的自我感动，会污染后面的选型。
3. 3 个词写进 HTML head 注释 <!-- typography tone: 精密 / 冷 / 当代 -->，并同步写进交付摘要。
4. 若已确认场景 S（见 [scenes.md](scenes.md)），用场景语气兜底：S2 工作汇报偏冷静/权威，S3 客户沟通偏可信/克制，S4 活动宣传偏热情/高能，S5 数据洞察偏精密/冷静。

### Step 2 定 display 家族（决定"声音"）

```
主标题需要"喊"吗？（T4，或主标题宽度 ≥ 画布宽 60%）
├─ 是 → 要更"紧"还是更"重"？
│   ├─ 更紧（窄字面，横排挤满）→ G4：Anton / Bebas Neue / Oswald / Barlow Condensed
│   └─ 更重（块状，压住版面）→ G4：Archivo Black / League Spartan / Anton
└─ 否 → 需要"叙事感"吗？（T1-T3 文案 > 80 字、观点、引用、人物）
    ├─ 是 → G3：Playfair Display / Fraunces / Newsreader / Noto Serif SC
    └─ 否 → 需要"未来/工程"吗？（科技、硬件、API、赛博）
        ├─ 是 → G5：Space Grotesk / Chakra Petch / Orbitron / Saira
        └─ 否 → G1 中性：Inter / Archivo / Manrope / Noto Sans SC 900
```

**判断依据表**（补充决策树无法覆盖的边界）：

| 情形 | 结论 |
|------|------|
| 英文标题 ≤ 3 个词、需要占据 ≥ 40% 画布宽 | 压缩展示（G4），用字号换宽度 |
| 英文标题是长句（≥ 6 个词） | 禁用压缩展示，改 G3 或 G1 |
| 中文标题 ≥ 12 字 | 必须放弃压缩/手写，中文没有压缩字面，硬套会掉字重 |
| 标题里同时有中英文 | 西文用 display、中文用 Noto Sans SC 700-900；不要指望西文 display 覆盖汉字 |
| 主标题与 BigNumber 同屏 | 两者共用同一 display 家族，靠字号与颜色分层，不换家族 |

**可测量红线**：display 家族只允许出现在 --font-heading、.display、.bignum；一旦出现在 --font-body 即违规（可用 Step 5 的自检命令发现）。

### Step 3 定正文家族（决定"可读性"）

**核心规则：中文必须单独指定 CJK 家族。** 西文字体（Inter/Anton 等）对汉字无效，浏览器会按字符逐字回退到系统字体，导致中英字面大小、基线、行高各不相同——这是"看起来很业余"的第一来源。

| 内容气质 | 西文正文 | 中文正文 | 禁止 |
|------|------|------|------|
| 现代 / 科技 / 效率 | Inter 400 | Noto Sans SC 400 | 中文用 300 以下 |
| 人文 / 叙事 / 杂志 | Source Serif 4 400 | Noto Serif SC 400 | A4 以下用 900 排长段 |
| 数据 / 新闻 / 报告 | Inter 400 | Noto Sans SC 400 | 正文混用两种 CJK 家族 |
| 东方极简（B6） | Inter 300-400 | Noto Sans SC 300-400 | 300 用在 16px 以下 |
| 手写人文（G6） | Inter 400 | Noto Sans SC 400（正文必须换回无衬线） | 正文用手写体/仿宋 |
| 潮流 Feed（B10） | Inter 400 | Noto Sans SC 400 | 正文用 900（900 只留给标题） |

**硬性规则**：

- CJK 家族必须出现在 --font-body 的前 3 位。写在最后一位等于没写——前面的字体若含拉丁字符仍会先命中，但汉字回退时机不可控。
- 正文只允许 400/500；300 仅 B6 且字号 ≥ 16px；100/200 全风格禁止。
- 中文正文字号按 typography.md 的尺寸表执行；同视觉字号下中文比西文显小，必要时 +1~2px（B9 规则：17-18px 起步）。
- 正文行高由 typography.md 的风格表决定，本文件不重复。

### Step 4 定 mono 家族（元信息与数据）

| 用途 | 首选 | 备选 | 要求 |
|------|------|------|------|
| BigNumber | JetBrains Mono 700 | IBM Plex Mono 600 | 数字必须等宽对齐 |
| 元信息/眉题/标签 | JetBrains Mono 500 | Geist Mono 500 / Space Mono 700 | 11-14px + uppercase + 0.05-0.14em |
| 代码/参数/日志 | JetBrains Mono 400 | IBM Plex Mono 400 / Fira Code 400 | 字形区分 0/O、1/l |
| 报纸/数据新闻（B7） | IBM Plex Mono 500 | Roboto Mono 500 | 与衬线标题形成机械对比 |
| 潮流 Feed（B10） | JetBrains Mono 400/500/700 | Geist Mono 400/500/700 | 11px + .14em + uppercase |

**硬性规则**：

- mono **不计入**"每页最多 2 个非 mono 家族"的预算（B10 = Inter + Noto Sans SC + mono，仍算 2 个非 mono 家族）。
- mono 只承担数字与拉丁字母。中文不需要等宽（汉字本身定宽），mono 栈尾部接 'Noto Sans SC', monospace 仅作兜底，不得让中文整段走 mono。
- 同一页只用一个 mono 家族；混两个 mono 属于无意义噪音。

### Step 5 声明与降级

把前 4 步的结果固化为一个声明块，三处同步：**IR 的 typography 字段**（按 onepager-ir-schema.json）、**CSS 变量**、**HTML 注释**。

```json
"typography": {
  "display": "Inter",
  "body": "Noto Sans SC",
  "mono": "JetBrains Mono",
  "origin": "google-fonts",
  "weights": [400, 700, 900],
  "fallback_chain": "'Inter', 'Noto Sans SC', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif",
  "cdn_url": "https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&family=Noto+Sans+SC:wght@400;700;900&family=JetBrains+Mono:wght@400;500;700&display=swap"
}
```

字段规则（与 onepager-ir-schema.json 的 typography 定义对齐）：

- display / body / mono 只写**家族名**，不写整条栈；body 写 CJK 家族名（如 Noto Sans SC），西文交给 fallback_chain 承接。
- origin 只能取 system / google-fonts / custom-cdn / local 四值之一；选网络字体时 origin 必须是 google-fonts 或 custom-cdn，且 fallback_chain 必填；纯系统栈为 system。
- weights 最多 3 个整数（100-900），必须与 CSS 实际使用的字重完全一致。
- fallback_chain 是完整 CSS 栈字符串，最后必须以 sans-serif / serif / monospace 收尾。
- cdn_url 写实际请求的那条 CSS2 URL；origin=system 时省略。

⚠️ tone（3 个气质词）与 scheme（G1-G7）**不在 IR schema 内**（typography 为 additionalProperties: false），不要硬塞：写入 HTML head 注释 <!-- typography tone: 精密 / 冷 / 当代 · scheme: G1 --> 和交付摘要即可。

```css
:root {
  --font-heading: 'Inter', 'Archivo', 'Noto Sans SC', 'PingFang SC', sans-serif;
  --font-body: 'Inter', 'Noto Sans SC', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  --font-mono: 'JetBrains Mono', 'SF Mono', 'Cascadia Code', 'Noto Sans SC', monospace;
}
```

**自检（3 条命令，交付前跑）**：

```bash
grep -c "@import" page.html                # @import 写法期望 1；link 写法为 0，应另有 2 条 preconnect
grep -o "https://[^ ]*" page.html          # 只允许 fonts.googleapis.com / 已批准的 jsDelivr
grep -o -- "--font-[a-z]*:[^;]*" page.html # 每条 fallback 必须以 sans-serif/serif/monospace 收尾
```

---

## 字体方案 G1-G7

G 方案是"选字策略"的枚举，与风格 B、类型 T 正交。选定后必须按 Step 5 写入 IR 的 typography 字段与 CSS 变量。

| 方案 | 名称 | 适用场景 | display 家族 | 正文家族 | mono 家族 | 风险提示 |
|------|------|------|------|------|------|------|
| G1 | 自动匹配（默认） | 用户未提字体；按 B 风格 + T 类型推导 | 见下方映射表 | 见下方映射表（CJK 必填） | JetBrains Mono | 推导结果必须落盘到声明块；"心里想的"不算执行 |
| G2 | 系统原生 | B4、零网络、企业内网、离线交付 | -apple-system / BlinkMacSystemFont / Segoe UI / Roboto | 同左 + Noto Sans SC / PingFang SC | SF Mono / Cascadia Code | 跨平台字形差异大；Linux 容器可能缺 CJK 字体，截图出豆腐块 |
| G3 | 编辑衬线 | B3/B6/B7、长文案、观点型 T1-T3 | Playfair Display / Fraunces / Newsreader / Noto Serif SC | Inter 400 + Noto Serif SC 或 Noto Sans SC 400 | IBM Plex Mono | 中文衬线笔画细，A4 以下避免 300/400 排长段；衬线标题不要配花体正文 |
| G4 | 展示黑体 | T4、B5、B10、需要极端字号对比 | Anton / Archivo Black / Bebas Neue / Oswald | Inter 400 + Noto Sans SC 400（正文绝不压缩） | JetBrains Mono | 压缩字体行高必须收紧到 0.95-1.05；中文无压缩字面，靠 700-900 补视觉重量 |
| G5 | 几何科技 | B1/B8、硬件/AI/API 主题 | Space Grotesk / Chakra Petch / Orbitron / Saira | Inter 400 + Noto Sans SC 400 | JetBrains Mono | Orbitron/Michroma 无中文，中文必须落 Noto Sans SC；几何字体大字号字距偏松，需 -0.01~-0.02em |
| G6 | 手写人文 | 邀请函、节日、书信、儿童内容 | Ma Shan Zheng / Long Cang / ZCOOL XiaoWei / LXGW WenKai | Inter 400 + Noto Sans SC 400（正文强制换回无衬线） | JetBrains Mono | 手写体仅限 ≤ 12 字标题；正文用手写体直接违规；手写字体只有 400，不能靠 700 加粗 |
| G7 | 自定义 | 用户点名指定字体名 | 用户指定 | 用户指定，CJK 缺失时补 Noto Sans SC | JetBrains Mono | 必须确认字体可获取（Google Fonts / CDN / 系统）；找不到时降级 G1 并在交付说明中标注 |

**G1 与既有硬编码字体栈的关系**：typography.md 中 B1-B10 的 :root 字体栈是"未启用字体匹配时的默认基线"。启用 G1 后若推导结果与默认栈一致，直接用默认栈；不一致时以本文件候选替换，并同步更新声明块与 CSS 变量——不允许出现"CSS 是一套、声明块是另一套"。

---

## 字体目录

按气质分组。每行含 6 列：字体名 / 气质关键词 / 适合位置 / 字重建议 / 可粘贴 CSS2 URL / 中英配对建议。
**单字重字体不写 :wght**（如 Anton 写成 family=Anton）；给单字重字体写 :wght@700 会让整条请求返回 400。

### 现代无衬线

| 字体 | 气质关键词 | 适合 | 字重建议 | Google Fonts CSS2 URL | 中英配对建议 |
|------|------|------|------|------|------|
| Inter | 中性、克制、国际化 | display / 正文 | 400/500/700/800/900 | https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;800;900&display=swap | 中英同用；中文配 Noto Sans SC 400（正文）/ 700-900（标题） |
| Space Grotesk | 几何、锐利、当代 | display | 400/500/700 | https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&display=swap | 配 Noto Sans SC 400；适合 B1/B8 的技术标题 |
| Manrope | 友好、圆润、现代 | display / 正文 | 400/600/800 | https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;800&display=swap | 比 Inter 更圆，适合 B5/B9 的亲和型产品页 |
| Archivo | 中性、紧凑、工业 | display | 400/600/800 | https://fonts.googleapis.com/css2?family=Archivo:wght@400;600;800&display=swap | B2/B10 首选；中文配 Noto Sans SC 900 |
| DM Sans | 简洁、友好、几何 | display / 正文 | 400/500/700 | https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap | 适合 B5/B9；中文配 Noto Sans SC 400 |
| Figtree | 轻快、现代、亲和 | display / 正文 | 400/600/800 | https://fonts.googleapis.com/css2?family=Figtree:wght@400;600;800&display=swap | 适合 T1 产品介绍；中文配 Noto Sans SC 400 |
| Plus Jakarta Sans | 利落、商务、当代 | display / 正文 | 400/600/800 | https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap | 适合 B9 的商务叙事；中文配 Noto Sans SC 400/700 |
| Public Sans | 中性、机构、稳重 | 正文 | 400/600/800 | https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;600;800&display=swap | 机构/政策类报告；中文配 Noto Sans SC 400 |
| Outfit | 几何、干净、年轻 | display | 400/600/800 | https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&display=swap | 适合 B5/B10；中文配 Noto Sans SC 700 |
| Sora | 未来、技术、锐利 | display | 400/600/700 | https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700&display=swap | 适合 B1/B8；中文配 Noto Sans SC 900 |

### 压缩展示

| 字体 | 气质关键词 | 适合 | 字重建议 | Google Fonts CSS2 URL | 中英配对建议 |
|------|------|------|------|------|------|
| Anton | 极端压缩、播报、冲击 | display（仅标题） | 400（单字重，本身即超粗） | https://fonts.googleapis.com/css2?family=Anton&display=swap | T4 Tier C 首选；中文配 Noto Sans SC 900 |
| Archivo Black | 块状、厚重、海报 | display | 400（单字重） | https://fonts.googleapis.com/css2?family=Archivo+Black&display=swap | 配 Noto Sans SC 900；适合 B5/T4 |
| Bebas Neue | 窄、干净、标题感 | display | 400（单字重） | https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap | 大字号展示；中文配 Noto Sans SC 900 |
| Oswald | 窄体、报头、信息型 | display | 400/600/700 | https://fonts.googleapis.com/css2?family=Oswald:wght@400;600;700&display=swap | 适合 B7 报头；中文配 Noto Sans SC 700 |
| Barlow Condensed | 窄、工业、系统感 | display | 500/700/800 | https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;700;800&display=swap | 配 Noto Sans SC 700；适合参数/规格海报 |
| Archivo Narrow | 窄、克制、可下探正文 | display / 正文（小字号） | 400/600/700 | https://fonts.googleapis.com/css2?family=Archivo+Narrow:wght@400;600;700&display=swap | 唯一可下探正文的窄体；中文配 Noto Sans SC 400 |
| Big Shoulders Display | 城市、粗粝、海报 | display | 600/800 | https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@600;800&display=swap | 配 Noto Sans SC 900；适合 B4/T4 |
| Teko | 数字感、体育、紧凑 | display / BigNumber 替代 | 500/700 | https://fonts.googleapis.com/css2?family=Teko:wght@500;700&display=swap | 适合数据海报；中文配 Noto Sans SC 900 |
| League Spartan | 宽重、复古、有力 | display | 400/700/900 | https://fonts.googleapis.com/css2?family=League+Spartan:wght@400;700;900&display=swap | 配 Noto Sans SC 900；适合 B5 标语 |

### 几何科技

| 字体 | 气质关键词 | 适合 | 字重建议 | Google Fonts CSS2 URL | 中英配对建议 |
|------|------|------|------|------|------|
| Chakra Petch | 机械、游戏、赛博 | display | 400/600/700 | https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;600;700&display=swap | B8 首选；中文配 Noto Sans SC 400 |
| Orbitron | 未来、科幻、HUD | display（仅英文） | 400/700/900 | https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap | 无中文；中文必须落 Noto Sans SC；适合 B8 短标题 |
| Rajdhani | 技术、仪表、窄几何 | display / 数据区 | 400/600/700 | https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&display=swap | 适合 B8 数据标签；中文配 Noto Sans SC 500/700 |
| Exo 2 | 科技、可变、干净 | display / 正文 | 400/600/800 | https://fonts.googleapis.com/css2?family=Exo+2:wght@400;600;800&display=swap | 适合 B1；中文配 Noto Sans SC 400 |
| Saira | 工业、可变、中性科技 | display / 正文 | 400/600/800 | https://fonts.googleapis.com/css2?family=Saira:wght@400;600;800&display=swap | 适合 B1/B2；中文配 Noto Sans SC 400/700 |
| Michroma | 宽体、复古未来、单字重 | display（仅英文） | 400（单字重） | https://fonts.googleapis.com/css2?family=Michroma&display=swap | 全大写短词才用；中文配 Noto Sans SC 900 |
| Bricolage Grotesque | 怪诞、当代、编辑感 | display | 400/700/800 | https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@400;700;800&display=swap | 适合 B5/B9；中文配 Noto Sans SC 700 |

### 等宽

| 字体 | 气质关键词 | 适合 | 字重建议 | Google Fonts CSS2 URL | 中英配对建议 |
|------|------|------|------|------|------|
| JetBrains Mono | 精确、工程、默认 | mono | 400/500/700 | https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap | 全风格默认 mono；中文兜底 Noto Sans SC |
| IBM Plex Mono | 报纸、编辑、克制 | mono | 400/500/600 | https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&display=swap | B7 数据新闻首选；中文兜底 Noto Sans SC |
| Space Mono | 复古、打字机、个性 | mono（短文本） | 400/700 | https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap | 适合 B5 标签；大段数字不如 JetBrains 稳 |
| Fira Code | 技术、代码、连字 | mono | 400/500/700 | https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;700&display=swap | 代码块；中文兜底 Noto Sans SC |
| Roboto Mono | 中性、通用、系统感 | mono | 400/500/700 | https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;500;700&display=swap | 适合 B2/B9；中文兜底 Noto Sans SC |
| Source Code Pro | 工程、清晰、Adobe 系 | mono | 400/600 | https://fonts.googleapis.com/css2?family=Source+Code+Pro:wght@400;600&display=swap | 适合 B1 参数区；中文兜底 Noto Sans SC |
| Geist Mono | 极简、当代、开发者 | mono | 400/500/700 | https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;500;700&display=swap | 适合 B9/B10；中文兜底 Noto Sans SC |
| DM Mono | 轻量、编辑、亲和 | mono（小字号） | 400/500 | https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&display=swap | 适合 B5/B3 标签；小字号别低于 400 |
| Martian Mono | 宽等宽、独特、未来 | mono（小剂量） | 400/600 | https://fonts.googleapis.com/css2?family=Martian+Mono:wght@400;600&display=swap | 只用于标签；正文数字禁用 |

### 编辑衬线

| 字体 | 气质关键词 | 适合 | 字重建议 | Google Fonts CSS2 URL | 中英配对建议 |
|------|------|------|------|------|------|
| Playfair Display | 高对比、优雅、杂志 | display | 400/600/700/900 | https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700;900&display=swap | 适合 B3/B5；中文配 Noto Serif SC 700 |
| Fraunces | 复古、柔软、有性格 | display | 400/700/900 | https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,700;9..144,900&display=swap | 适合 B3；中文配 Noto Serif SC 400/700 |
| Instrument Serif | 高对比、编辑、轻 | display | 400 + italic | https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&display=swap | 大字号标题；中文配 Noto Serif SC 400，正文不要用 |
| Newsreader | 新闻、可读、克制 | display / 正文 | 400/600 | https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,600&display=swap | B7 首选；中文配 Noto Serif SC 600 |
| Lora | 温暖、可读、平衡 | display / 正文 | 400/500/700 | https://fonts.googleapis.com/css2?family=Lora:wght@400;500;700&display=swap | 长文正文（西文）；中文配 Noto Serif SC 400 |
| Source Serif 4 | 中性、现代、工程感衬线 | display / 正文 | 400/700 | https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,700&display=swap | 与 Source Code Pro 同气质；中文配 Noto Serif SC 400 |
| Libre Baskerville | 古典、书卷、正式 | 正文 / display | 400/700 | https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@400;700&display=swap | 适合 B6/B7；中文配 Noto Serif SC 400 |
| EB Garamond | 古典、文学、优雅 | 正文 | 400/600 | https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;600&display=swap | 适合 B3/B6；小字号避免，中文配 Noto Serif SC 400 |
| Spectral | 屏幕衬线、清晰、编辑 | 正文 | 400/600 | https://fonts.googleapis.com/css2?family=Spectral:wght@400;600&display=swap | 适合 B7 正文；中文正文仍用 Noto Sans SC 400 更稳 |
| DM Serif Display | 高对比、标题、复古 | display | 400（单字重） | https://fonts.googleapis.com/css2?family=DM+Serif+Display&display=swap | 仅标题；中文配 Noto Serif SC 700 |

### 中文

| 字体 | 气质关键词 | 适合 | 字重建议 | Google Fonts CSS2 URL | 中英配对建议 |
|------|------|------|------|------|------|
| Noto Sans SC | 中性、通用、安全 | display / 正文 | 400/500/700/900 | https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700;900&display=swap | 默认 CJK 正文；西文配 Inter；中文标题用 900 补笔画密度 |
| Noto Serif SC | 宋体、人文、正式 | display / 正文 | 400/600/700/900 | https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700;900&display=swap | 配 Playfair Display / Newsreader；A4 以下避免 300 长文 |
| ZCOOL XiaoWei | 宋体变体、文艺、轻 | display（短标题） | 400（单字重） | https://fonts.googleapis.com/css2?family=ZCOOL+XiaoWei&display=swap | 仅标题；西文配 Newsreader；正文禁用 |
| ZCOOL QingKe HuangYou | 黑体变体、活泼、口语 | display（短标题） | 400（单字重） | https://fonts.googleapis.com/css2?family=ZCOOL+QingKe+HuangYou&display=swap | 仅标题；正文禁用（笔画缺口大） |
| ZCOOL KuaiLe | 手写感、俏皮、儿童 | display（短标题） | 400（单字重） | https://fonts.googleapis.com/css2?family=ZCOOL+KuaiLe&display=swap | 仅标题；B10 禁用；正文禁用 |
| Ma Shan Zheng | 毛笔、强表达、节日 | display（≤ 12 字） | 400（单字重） | https://fonts.googleapis.com/css2?family=Ma+Shan+Zheng&display=swap | G6 首选；西文正文配 Inter 400 |
| Long Cang | 行书、轻盈、手写 | display（≤ 8 字） | 400（单字重） | https://fonts.googleapis.com/css2?family=Long+Cang&display=swap | G6 备选；正文配 Noto Sans SC 400 |
| Zhi Mang Xing | 草书、速度、个性 | display（≤ 6 字） | 400（单字重） | https://fonts.googleapis.com/css2?family=Zhi+Mang+Xing&display=swap | 辨识度低，仅氛围词；正文禁用 |
| LXGW WenKai 霞鹜文楷 | 楷体、人文、温和 | display / 正文（人文） | 300/400/700 | Google Fonts 无 → 见下方备选来源 | 唯一可下探正文的楷体向字体；西文配 Inter 400 |
| Smiley Sans 得意黑 | 斜切、潮流、标题 | display（仅标题） | 400（单字重，斜体） | Google Fonts 无 → 见下方备选来源 | T4 Tier C 的中文替代；配 Anton / Archivo Black |

**非 Google Fonts 的备选来源**（第三方 CDN，必须配 fallback；上线前用 @版本号 固定，避免 latest 漂移）：

```html
<!-- LXGW WenKai 霞鹜文楷：family 名 'LXGW WenKai' / 'LXGW WenKai Mono' -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/lxgw-wenkai-webfont@1.7.0/style.css">

<!-- Smiley Sans 得意黑 Oblique：family 名 'Smiley Sans Oblique' -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/cn-fontsource-smiley-sans-oblique-regular/font.css">
```

⚠️ 早期版本引用过 cn-fontsource-smiley-sans-oblique/font.css（无 -regular），该路径返回 404。cross-reference.md §2.1 与本仓库 B9/T4 示例已改用带 -regular 的包名；自行检索时请先 curl 验证再写入。

### 特殊表达（慎用，全页最多 1 款 / 1 处）

| 字体 | 气质关键词 | 适合 | 字重建议 | Google Fonts CSS2 URL | 中英配对建议 |
|------|------|------|------|------|------|
| Alfa Slab One | 粗衬线、海报、复古 | display | 400（单字重） | https://fonts.googleapis.com/css2?family=Alfa+Slab+One&display=swap | 仅 T4；中文配 Noto Sans SC 900 |
| Bungee | 街头、潮流、图形化 | display（仅英文） | 400（单字重） | https://fonts.googleapis.com/css2?family=Bungee&display=swap | 适合 B5/B10 短词；中文另排 |
| Press Start 2P | 像素、游戏、复古 | display（≤ 6 词） | 400（单字重） | https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap | 仅装饰标题；中文禁用，正文禁用 |
| Caveat | 手写、亲切、笔记 | display（西文） | 400/700 | https://fonts.googleapis.com/css2?family=Caveat:wght@400;700&display=swap | 适合 B3/G6 的西文手写批注；中文配 Ma Shan Zheng 需谨慎（两套笔压不一致） |

---

## 加载规范（可直接复制的代码）

### 标准写法：link + preconnect（SKILL.md §3.7 的 ① 首选）

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&family=Archivo:wght@700;800&family=Noto+Sans+SC:wght@400;700;900&family=JetBrains+Mono:wght@400;500;700&display=swap">
```

规则：

- 两条 preconnect 都要写；fonts.gstatic.com **必须**带 crossorigin，否则连接复用不成立。
- 一个 URL 最多合并 6 个 family；超过时拆成两条 link，便于排查（见下方"排查表"）。
- display=swap 必须写：字体未就绪时先用 fallback 渲染，不出现空白文字。
- 只写 fonts.googleapis.com，**不要手写 fonts.gstatic.com 的 woff2 地址**——其 URL 带版本哈希会失效（实测一个旧地址已 404）。

### 单文件内联：@import（SKILL.md §3.7 的 ②）

单文件自包含、只能用一个 style 块时用 @import，不额外增加 link 结构。加载写法优先级与 SKILL.md §3.7 一致：**link + preconnect ① > @import ② > 纯系统栈 ③**；本 skill 的截图流程会等待 document.fonts，① 与 ② 的实际差异只有 1-2 个 RTT：

```html
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&family=Archivo:wght@700;800&family=Noto+Sans+SC:wght@400;700;900&family=JetBrains+Mono:wght@400;500;700&display=swap');

/* 下面才是其他规则 */
:root {
  --font-heading: 'Inter', 'Archivo', 'Noto Sans SC', 'PingFang SC', sans-serif;
  --font-body: 'Inter', 'Noto Sans SC', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  --font-mono: 'JetBrains Mono', 'SF Mono', 'Cascadia Code', 'Noto Sans SC', monospace;
}
</style>
```

规则：

- @import 必须是 style 里的**第一条语句**（在任何选择器、任何普通规则之前）。写在规则之后会被浏览器静默丢弃——字体永远不生效，也不报错，最难排查。
- 代价是无法 preconnect，多 1-2 个 RTT。本 skill 的截图流程会等待 document.fonts，可以忽略这点延迟。
- link 与 @import 二选一。同一家族两处都写会产生重复请求。

### 断网降级：完整 fallback 链

**规则：每条 font-family 的最后一项必须是通用族**（sans-serif / serif / monospace），中间按平台从新到旧排列。

```css
/* 无衬线 */
--font-sans: 'Inter', 'Noto Sans SC', 'PingFang SC', 'Hiragino Sans GB',
             'Microsoft YaHei', 'WenQuanYi Micro Hei', sans-serif;

/* 衬线 */
--font-serif: 'Playfair Display', 'Noto Serif SC', 'Songti SC', 'STSong',
              'SimSun', 'WenQuanYi Micro Hei', serif;

/* 等宽（尾部接 CJK 兜底，中文不需要等宽） */
--font-mono: 'JetBrains Mono', 'SF Mono', 'Cascadia Code',
             'Noto Sans SC', monospace;

/* 手写（G6，仅标题；正文必须换回无衬线） */
--font-hand: 'Ma Shan Zheng', 'Kaiti SC', 'STKaiti', 'KaiTi', serif;
```

断网时的行为：Google Fonts 请求失败 → 浏览器静默使用后续 fallback → 页面仍完整可读。scripts/capture.py 会在有资源加载失败时打印 WARN: N resource request(s) failed; system font fallback may have been used.，交付摘要中应记录该 WARN。

**验证降级是否真的生效**（不改线上文件）：

1. 复制一份 HTML，把 fonts.googleapis.com 全局替换成 fonts.googleapis.invalid；
2. 重新截图，对比字面：中文应落到 PingFang SC / 微软雅黑，且不出现方块；
3. 若出现方块（豆腐块），说明系统缺 CJK 字体——见下方 Linux 容器说明。

**Linux/容器风险**：scripts/install_deps.sh 只安装 Playwright 与 Chromium，**不安装 CJK 系统字体**。在干净容器里用 G2（不加载网络字体）会出豆腐块；可用 fc-list :lang=zh | head 检查，必要时安装 fonts-noto-cjk。G1/G3-G7 因有网络 CJK 字体兜底，风险较低。

### CJK 体积与子集化

实测（Chrome UA，2026-11-23）：

| 请求 | CSS 体积 | gzip 后 | @font-face 数量 |
|------|------|------|------|
| Noto Sans SC 3 字重（400/700/900） | 338,784 B | 92,725 B | 303（全部带 unicode-range） |
| Noto Sans SC 4 字重（400/500/700/900） | 451,712 B | — | 404 |
| Inter 3 字重（400/700/900） | 7,521 B | 719 B | 21 |

结论：

- Google Fonts 的 CJK 字体按 unicode-range 分片，浏览器只下载命中字符所在的分片。CSS 文本本身较大（~90 KB gzip），但不会一次下载整套字形。
- **西文字体不是瓶颈**（Inter 3 字重仅 7.5 KB CSS）；预算焦虑应放在"要不要加第二个 CJK 家族"上，而不是西文。
- 同一页最多加载 **1 个 CJK 家族**；第二套中文（如标题宋体 + 正文黑体）叠加时，CSS 体积与请求数近似翻倍。

**text= 子集化**（只有少量固定文案时）：

https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@700&text=%E4%B8%80%E9%A1%B5%E6%8A%A5%E5%91%8A%E8%AE%BE%E8%AE%A1&display=swap

实测：CSS 348 B、1 个 @font-face、unicode-range 恰好列出这 6 个字。

规则：

- text= 的内容**必须 URL 编码**。直接写中文会返回 HTTP 400（实测）。
- 只用于固定短文案：海报标题、CTA、统计标签，建议 ≤ 100 字。
- 每个字重单独请求（text= 与多个 wght 可并存，但会增加请求数）。
- **不能用于正文**：任何缺字都会回退到系统字体，造成同段字面跳变；改一个字就要改 URL。

### 加载失败兜底

1. **font-display**：统一用 display=swap（Google 返回的 CSS 已包含 font-display: swap）。自托管 @font-face 也必须显式写 font-display: swap。
2. **系统字体栈**：见上节完整链，任何方案都必须配。
3. **不要用 JS 检测或注入字体**，原因有四：
   - 本 skill 要求单文件、无外部 JS；scripts/capture.py 把任何 pageerror 视为失败（if page_errors: raise RuntimeError）；
   - 截图脚本已 wait_for_function("document.fonts.status === 'loaded'") 并额外等待 250ms，再写 JS 检测是重复劳动且引入时序风险；
   - JS 失败时没有兜底；CSS 失败时至少还有 fallback 链；
   - 用 JS 判断"字体是否加载"并切换 class 会造成 FOUT 抖动，截图可能抓到中间态。
4. **自托管兜底**（需要完全离线时）：把 woff2 放到项目内，用本地 @font-face + font-display: swap，并在 src 里保留 local() 优先命中系统已装字体。

### 排查表（URL 返回 200 但字体没生效）

| 现象 | 原因 | 处理 |
|------|------|------|
| 200 但页面字体没变 | family 名拼错时，若同 URL 有其他合法家族，Google 会**静默丢弃**该项（实测 200） | 在返回 CSS 里 grep "font-family: '目标名'"，没有就是没加载 |
| 整条 URL 返回 400 | 单字重字体写了 :wght@700；或请求了字体不存在的字重（如 Inter:wght@1200） | 去掉 :wght，或用本文已校验的字重组合 |
| 中文仍是系统字体 | CJK 家族没写进 --font-body，或拼写为中文名 | 用 'Noto Sans SC' 等 CSS 内英文名 |
| @import 完全无效 | 写在了其他 CSS 规则之后 | 移到 style 第一行 |

---

## 字体匹配与风格的映射表（B1-B10）

| 风格 | G 推荐 | display | 正文/CJK | mono | 说明 |
|------|------|------|------|------|------|
| B1 暗夜编辑 | G1 / G5 | Inter 700-800 或 Space Grotesk 700 | Inter 400 + Noto Sans SC 400 | JetBrains Mono 400/700 | 深底上不要用 300 以下；对比度不足时细字发虚 |
| B2 瑞士精密 | G1 / G4 | Archivo 800-900 或 Inter 900 | Inter 400 + Noto Sans SC 400 | IBM Plex Mono 500 | 中性 grotesque 气质，不要用几何字体替代 |
| B3 有机自然 | G3 | Fraunces 600-700 或 Newsreader 600 + Noto Serif SC 700 | Inter 400 + Noto Sans SC 400 | IBM Plex Mono 400 | 衬线标题 + 无衬线正文；中文衬线不要 900 |
| B4 建筑粗野 | G2 | 系统 Helvetica/Segoe 900 | 系统栈 + Noto Sans SC 400 | SF Mono / Cascadia Code | 不加载网络字体；容器缺 CJK 需装字体 |
| B5 新波普编辑 | G1 / G4 | Archivo Black 或 Anton | Inter 400 + Noto Sans SC 400 | Space Mono 400/700 | 撞色卡片上用重 display，正文必须回到 400 |
| B6 极简东方 | G3 | Noto Serif SC 400 + Cormorant/Newsreader 400 | Inter 300-400 + Noto Sans SC 300-400 | IBM Plex Mono 400 | 全页只用 400，靠字号与留白建立层级 |
| B7 数据新闻 | G3 / G1 | Newsreader/Lora 700 + Noto Serif SC 700 | Inter 400 + Noto Sans SC 400 | IBM Plex Mono 500 | 图表标签 mono + uppercase；数字对齐优先 |
| B8 赛博街道 | G5 | Chakra Petch 700 / Orbitron 700 | Inter 400 + Noto Sans SC 400 | JetBrains Mono 400/700 | Orbitron 无中文；中文标题落 Noto Sans SC 700-900 |
| B9 谷歌原生 | G1 | Inter 500-600（英）+ Noto Sans SC 700-900（中） | Inter 400 + Noto Sans SC 400 | JetBrains Mono 500 / IBM Plex Mono 500 | 中英视觉权重对齐；标题 48px+ 才用负字距 |
| B10 短视频潮流 | G1 / G4 | Inter / Archivo 700-800（-0.02em，line-height .95）+ Noto Sans SC 900 | Inter 400 + Noto Sans SC 400（line-height 1.6） | JetBrains Mono 400/500/700 | 字重只有 400/700/900；Paper 模式强调词用 Georgia / Noto Serif SC 斜体，全页 1 处 |
| B11 粗野平面 | G4 | Archivo Black / Anton 900（-0.045em，line-height .86）+ Noto Sans SC 900 | Inter 400 + Noto Sans SC 400 | JetBrains Mono 400（9px / .18em 大写） | 大字极紧、小字极松；中文允许单字竖排；只用一个 display 家族，靠尺寸而非家族制造对比 |

---

## 禁止清单

1. 🚫 **超过 2 个非 mono 家族**。计数方法：--font-heading 与 --font-body 里不同家族名的并集去掉 mono 后 ≤ 2。
2. 🚫 **把展示/装饰字体用于正文**。Anton、Bebas Neue、ZCOOL 系列、Press Start 2P 只允许出现在 --font-heading。
3. 🚫 **正文使用 100/200 字重**。300 仅 B6 且 ≥ 16px；其余风格正文从 400 起。
4. 🚫 **CJK 只写西文字体**。--font-body: 'Inter', sans-serif 不带任何中文家族 = 汉字逐字回退，中英字面不匹配。
5. 🚫 **只写 Web 字体不写 fallback**。每条 font-family 必须以 sans-serif / serif / monospace 收尾。
6. 🚫 **用 JS 检测或注入字体**。理由见"加载失败兜底"第 3 条。
7. 🚫 **@import 不在 style 首位**。写在规则之后会被静默丢弃。
8. 🚫 **给单字重字体写 :wght**。Anton、Bebas Neue、Archivo Black、ZCOOL 系列、Ma Shan Zheng 等都是单字重，写 :wght@700 会让整条 URL 返回 400。
9. 🚫 **同一 URL 合并超过 6 个 family**。拆分 link 便于定位失败项。
10. 🚫 **手写 fonts.gstatic.com 的 woff2 地址**。带版本哈希，会失效；只引 fonts.googleapis.com/css2。
11. 🚫 **text= 用于正文或未 URL 编码**。未编码中文直接 400；用于正文则缺字跳变。
12. 🚫 **一页混用两种以上字重节奏**。字重集合（非 mono）≤ 3 种，且必须包含 400（正文）与一个 ≥ 700 的标题字重。
13. 🚫 **未经校验的第三方字体 CDN**。凡本文件未列出的 CDN，落地前必须用 curl -o /dev/null -w "%{http_code}" 验证返回 200。
14. 🚫 **用中文名写 CSS family**。必须写 CSS 内的英文名（如 'Noto Sans SC'，不是 '思源黑体'）。
