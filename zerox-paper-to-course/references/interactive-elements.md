# Interactive Elements Reference

Implementation patterns for every interactive element type used in zerox-paper-to-course tutorials.

> **Architecture note:** All CSS and JavaScript live in `references/styles.css` and `references/main.js`, copied verbatim into every course directory. Write only the HTML patterns below — no inline `<style>` or `<script>`.

## Table of Contents
0. [Cover Page / Hero Section](#cover-page--hero-section)
1. [Math Derivation Walkthrough](#math-derivation-walkthrough)
2. [Pseudocode Walkthrough](#pseudocode-walkthrough)
3. [Result Comparison Interactive](#result-comparison-interactive)
4. [Research Lineage Tree](#research-lineage-tree)
5. [Research Dialogue (Group Chat)](#research-dialogue-group-chat)
6. [SVG Diagrams](#svg-diagrams)
7. [Multiple-Choice Quizzes](#multiple-choice-quizzes)
8. [Drag-and-Drop Matching](#drag-and-drop-matching)
9. [Spot the Assumption](#spot-the-assumption)
10. [Ablation Toggle](#ablation-toggle)
11. [Callout Boxes](#callout-boxes)
12. [Contribution / Concept Cards](#contribution--concept-cards)
13. [Paper Citation Cards](#paper-citation-cards)
14. [Flow Diagrams](#flow-diagrams)
15. [Glossary Tooltips](#glossary-tooltips)
16. [Numbered Step Cards](#numbered-step-cards)
17. [Icon-Label Rows](#icon-label-rows)

---

## Cover Page / Hero Section

The course cover is a full-viewport landing page that appears before all modules. It is NOT a `.module` — it has no nav-dot and does not participate in scroll-snap.

**Wiring:** The "Start Learning" button scrolls to Module 0. Handled by `main.js` cover CTA listener.

**HTML:**
```html
<section class="course-cover">
  <div class="course-cover-inner">
    <span class="course-cover-badge">Interactive Tutorial</span>
    <h1 class="course-cover-title">Nonsense Helps：提示空间扰动如何拓宽推理探索</h1>
    <p class="course-cover-subtitle">How adding random noise to prompts can expand reasoning exploration in LLM training</p>
    <p class="course-cover-authors">Yuntao Bai et al. · arXiv 2026</p>
    <div class="course-cover-meta">
      <span class="course-cover-meta-item">&#128218; 7 Modules</span>
      <span class="course-cover-meta-item">&#9201; ~45 min</span>
      <span class="course-cover-meta-item">&#127891; Intermediate</span>
    </div>
    <div class="course-cover-abstract">
      <span class="course-cover-abstract-label">Abstract</span>
      <p>本文提出 LoPE 方法，通过在提示空间中添加 Lorem Ipsum 随机噪声来促进 GRPO 训练的探索，解决了零优势问题...</p>
    </div>
    <a href="#module-0" class="course-cover-cta">开始学习 →</a>
  </div>
</section>
```

**Rules:**
- The cover is NOT a `.module` section — no `scroll-snap-align`, no module number
- The "Start Learning" button scrolls to Module 0 (the prerequisites module)
- Paper title should be in the course's output language, with the English original in parentheses if translated
- Abstract is abbreviated to 2-3 sentences, not the full paper abstract
- Metadata badges: module count, estimated time (rough: 5-7 min per module), difficulty level
- Difficulty levels: Beginner (no prerequisites), Intermediate (some domain knowledge), Advanced (significant math/domain background)

---

## Math Derivation Walkthrough

The most important teaching element. Shows a mathematical equation and lets the learner click through each derivation step.

**Wiring:** `main.js` auto-initializes every `.math-derivation`. Steps are `.math-step` elements. Controls: `.math-next-btn`, `.math-prev-btn`, `.math-reset-btn`. Progress: `.math-progress`.

**HTML:**
```html
<div class="math-derivation animate-in" id="math-deriv-1">
  <div class="math-step" data-step="0">
    <div class="math-equation">
      $$L_{GRPO} = -\mathbb{E}_{q \sim P(Q)} \left[ \frac{1}{G} \sum_{i=1}^{G} \min\left( \frac{\pi_\theta(o_i|q)}{\pi_{ref}(o_i|q)} A_i, \text{clip}(\cdot) A_i \right) \right]$$
    </div>
    <div class="math-explanation">
      <p>GRPO 的损失函数衡量模型的回答与参考策略之间的差异。优势函数 $A_i$ 告诉我们每个回答相对于平均水平有多好。</p>
    </div>
  </div>

  <div class="math-step" data-step="1" style="display:none">
    <div class="math-equation">
      $$A_i = \frac{r_i - \text{mean}(\{r_1, ..., r_G\})}{\text{std}(\{r_1, ..., r_G\})}$$
    </div>
    <div class="math-explanation">
      <p>优势函数通过组内归一化计算：将每个回答的奖励减去均值，再除以标准差。这告诉我们每个回答相对于同组其他回答的优劣程度。</p>
    </div>
  </div>

  <!-- more steps -->

  <div class="math-controls">
    <button class="btn math-prev-btn">上一步</button>
    <button class="btn math-next-btn">下一步</button>
    <button class="btn math-reset-btn">重新开始</button>
    <span class="math-progress"></span>
  </div>
</div>
```

**Rules:**
- Each step should explain ONE transformation or insight
- The explanation should be in plain language, not just "taking the derivative"
- KaTeX auto-renders `$$...$$` blocks; `main.js` re-renders when a new step becomes visible
- Use `$...$` for inline math within explanations

---

## Pseudocode Walkthrough

Like a code translation block, but for algorithm pseudocode. Left panel: the algorithm. Right panel: line-by-line explanation.

**Wiring:** `main.js` auto-initializes every `.pseudocode-translation`. Controls: `.pseudocode-next-btn`, `.pseudocode-prev-btn`, `.pseudocode-reset-btn`. Progress: `.pseudocode-progress`.

**HTML:**
```html
<div class="pseudocode-translation animate-in" id="pseudo-lope">
  <div class="pseudocode-block">
    <span class="translation-label">ALGORITHM</span>
    <span class="pseudocode-line">INPUT: prompt q, model π, perturbation text P</span>
    <span class="pseudocode-line">FOR i = 1 TO G DO</span>
    <span class="pseudocode-line">  q' = CONCAT(random_prefix(P), q)</span>
    <span class="pseudocode-line">  o_i = SAMPLE(π, q')</span>
    <span class="pseudocode-line">  r_i = REWARD(o_i, q)</span>
    <span class="pseudocode-line">END FOR</span>
    <span class="pseudocode-line">A = NORMALIZE({r_1, ..., r_G})</span>
    <span class="pseudocode-line">UPDATE π USING A</span>
  </div>
  <div class="pseudocode-explanation">
    <span class="translation-label">EXPLANATION</span>
    <div class="pseudocode-explanation-lines">
      <p class="pe">输入：原始问题、当前模型、用于扰动的文本（如 Lorem Ipsum）</p>
      <p class="pe">对每个采样组重复 G 次</p>
      <p class="pe">随机截取扰动文本的一段，拼接到问题前面</p>
      <p class="pe">用模型对加了噪声的问题生成回答</p>
      <p class="pe">用奖励函数评估回答质量（基于原始问题，不是扰动后的问题）</p>
      <p class="pe">结束循环</p>
      <p class="pe">对所有奖励做归一化，得到优势值</p>
      <p class="pe">用优势值更新模型参数</p>
    </div>
  </div>
</div>

<div class="pseudocode-controls">
  <button class="btn pseudocode-prev-btn">上一行</button>
  <button class="btn pseudocode-next-btn">下一行</button>
  <button class="btn pseudocode-reset-btn">重新开始</button>
  <span class="pseudocode-progress"></span>
</div>
```

**Rules:**
- Pseudocode should be language-agnostic (INPUT, FOR, IF...THEN, not Python/C++)
- Each line maps 1:1 to an explanation line
- The explanation should explain WHY, not just WHAT

---

## Result Comparison Interactive

Interactive bar charts for comparing experimental results across methods or configurations.

**Wiring:** `main.js` auto-initializes every `.result-comparison`. Metric toggle buttons: `.result-metric` with `data-metric` attribute. Bars: `.result-bar` with `data-*` attributes per metric.

**HTML:**
```html
<div class="result-comparison animate-in">
  <div class="result-header">
    <h4>数学推理基准测试结果</h4>
    <div class="result-metric-toggle">
      <button class="result-metric active" data-metric="accuracy">准确率</button>
      <button class="result-metric" data-metric="pass1">Pass@1</button>
    </div>
  </div>
  <div class="result-bars">
    <div class="result-bar" data-accuracy="78.3" data-pass1="65.2">
      <span class="result-label">LoPE (本文)</span>
      <div class="result-bar-track"><div class="result-fill ours" style="width:0%"></div></div>
      <span class="result-value"></span>
    </div>
    <div class="result-bar" data-accuracy="72.1" data-pass1="58.7">
      <span class="result-label">GRPO 基线</span>
      <div class="result-bar-track"><div class="result-fill baseline" style="width:0%"></div></div>
      <span class="result-value"></span>
    </div>
    <div class="result-bar" data-accuracy="68.5" data-pass1="54.3">
      <span class="result-label">PPO 基线</span>
      <div class="result-bar-track"><div class="result-fill baseline" style="width:0%"></div></div>
      <span class="result-value"></span>
    </div>
  </div>
</div>
```

**Rules:**
- The "ours" bar uses `.result-fill.ours` (accent color); baselines use `.result-fill.baseline` (gray)
- Data values are percentages (shown as width%)
- `main.js` animates bar widths and updates values on metric toggle

---

## Research Lineage Tree

Visual tree showing how this paper relates to prior work.

**HTML (CSS-based tree):**
```html
<div class="lineage-tree animate-in">
  <div class="lineage-node lineage-root" data-detail="LoPE：通过在提示中添加随机噪声来扩展推理探索空间">
    <span class="lineage-label">LoPE</span>
    <span class="lineage-detail">本文 (2026)</span>
  </div>
  <div class="lineage-branch">
    <div class="lineage-edge-label">改进</div>
    <div class="lineage-node" data-detail="Group Relative Policy Optimization：组内相对优势估计">
      <span class="lineage-label">GRPO</span>
      <span class="lineage-detail">Shao et al., 2024</span>
    </div>
    <div class="lineage-branch">
      <div class="lineage-edge-label">基于</div>
      <div class="lineage-node" data-detail="Proximal Policy Optimization：近端策略优化">
        <span class="lineage-label">PPO</span>
        <span class="lineage-detail">Schulman et al., 2017</span>
      </div>
    </div>
  </div>
  <div class="lineage-branch">
    <div class="lineage-edge-label">相关</div>
    <div class="lineage-node" data-detail="Reinforcement Learning from Human Feedback">
      <span class="lineage-label">RLHF</span>
      <span class="lineage-detail">Ouyang et al., 2022</span>
    </div>
  </div>
</div>
```

**SVG-based tree (for complex lineages):**
```html
<div class="svg-diagram">
  <svg viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg">
    <rect class="node-rect accent" x="300" y="20" width="200" height="60" rx="12"/>
    <text x="400" y="50" text-anchor="middle" font-weight="700" font-size="14">LoPE</text>
    <text x="400" y="68" text-anchor="middle" font-size="11" fill="#9E9790">本文, 2026</text>

    <line class="edge-line accent" x1="400" y1="80" x2="200" y2="150"/>
    <text x="280" y="115" font-size="10" fill="#9E9790" font-style="italic">改进</text>
    <rect class="node-rect" x="100" y="150" width="200" height="60" rx="12"/>
    <text x="200" y="180" text-anchor="middle" font-weight="700" font-size="14">GRPO</text>

    <line class="edge-line" x1="200" y1="210" x2="200" y2="280"/>
    <rect class="node-rect" x="100" y="280" width="200" height="60" rx="12"/>
    <text x="200" y="310" text-anchor="middle" font-weight="700" font-size="14">PPO</text>
  </svg>
</div>
```

---

## Research Dialogue (Group Chat)

iMessage-style chat showing researchers or methods "discussing" a concept. Same engine as codebase-to-course's group chat.

**Wiring:** `main.js` auto-initializes every `.chat-window`. Controls: `.chat-next-btn`, `.chat-all-btn`, `.chat-reset-btn`. Progress: `.chat-progress`.

**HTML:**
```html
<div class="chat-window animate-in" id="chat-module2">
  <div class="chat-messages">
    <div class="chat-message" data-msg="0" data-sender="researcher-a" style="display:none">
      <div class="chat-avatar" style="background: var(--color-actor-1)">A</div>
      <div class="chat-bubble">
        <span class="chat-sender" style="color: var(--color-actor-1)">研究者 A</span>
        <p>这不就是数据增强吗？在输入前面加随机文本，跟 back-translation 有什么本质区别？</p>
      </div>
    </div>
    <div class="chat-message" data-msg="1" data-sender="researcher-b" style="display:none">
      <div class="chat-avatar" style="background: var(--color-actor-2)">B</div>
      <div class="chat-bubble">
        <span class="chat-sender" style="color: var(--color-actor-2)">研究者 B</span>
        <p>不完全一样。数据增强改变的是训练数据的分布，而 LoPE 改变的是推理时的提示空间。模型本身没有变，变的是它探索的方式。</p>
      </div>
    </div>
  </div>
  <div class="chat-typing" style="display:none">
    <div class="chat-avatar">?</div>
    <div class="chat-typing-dots">
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
    </div>
  </div>
  <div class="chat-controls">
    <button class="btn chat-next-btn">下一条</button>
    <button class="btn chat-all-btn">全部播放</button>
    <button class="btn chat-reset-btn">重播</button>
    <span class="chat-progress"></span>
  </div>
</div>
```

---

## SVG Diagrams

For concept maps, experimental frameworks, algorithm flows, and comparison matrices.

**HTML:**
```html
<div class="svg-diagram animate-in">
  <svg viewBox="0 0 800 300" xmlns="http://www.w3.org/2000/svg">
    <!-- Example: experimental framework -->
    <rect class="node-rect accent" x="50" y="120" width="160" height="60" rx="12"/>
    <text x="130" y="150" text-anchor="middle" font-weight="700" font-size="13">原始提示 q</text>

    <line class="edge-line" x1="210" y1="150" x2="290" y2="150"/>
    <polygon class="edge-arrow" points="285,145 295,150 285,155"/>

    <rect class="node-rect" x="290" y="120" width="160" height="60" rx="12"/>
    <text x="370" y="145" text-anchor="middle" font-weight="600" font-size="13">添加噪声</text>
    <text x="370" y="163" text-anchor="middle" font-size="11" fill="#9E9790">Lorem Ipsum</text>

    <line class="edge-line" x1="450" y1="150" x2="530" y2="150"/>
    <polygon class="edge-arrow" points="525,145 535,150 525,155"/>

    <rect class="node-rect accent" x="530" y="120" width="160" height="60" rx="12"/>
    <text x="610" y="145" text-anchor="middle" font-weight="700" font-size="13">模型采样</text>
    <text x="610" y="163" text-anchor="middle" font-size="11" fill="#9E9790">π(o|q')</text>
  </svg>
</div>
```

**Rules:**
- Use `viewBox` for responsiveness, `width="100%"` on the SVG
- Use CSS variable references in inline `style` attributes for colors
- Keep node text short (1-2 lines)
- Use `<foreignObject>` for longer text blocks if needed

---

## Multiple-Choice Quizzes

Same pattern as codebase-to-course, adapted for paper content.

**Wiring:** `main.js` exposes `window.selectOption(btn)`, `window.checkQuiz(containerId)`, `window.resetQuiz(containerId)`.

**HTML:**
```html
<div class="quiz-container animate-in" id="quiz-module3">
  <div class="quiz-question-block"
       data-correct="option-b"
       data-explanation-right="正确！当所有采样都失败时，优势函数为零，模型无法学习。"
       data-explanation-wrong="不太对。想想当组内所有回答的奖励都相同时会发生什么...">
    <h3 class="quiz-question">如果一组采样中所有回答都得到了相同的奖励，GRPO 会发生什么？</h3>
    <div class="quiz-options">
      <button class="quiz-option" data-value="option-a" onclick="selectOption(this)">
        <div class="quiz-option-radio"></div>
        <span>模型会随机选择一个回答作为正例</span>
      </button>
      <button class="quiz-option" data-value="option-b" onclick="selectOption(this)">
        <div class="quiz-option-radio"></div>
        <span>优势函数为零，模型无法从这组采样中学习</span>
      </button>
      <button class="quiz-option" data-value="option-c" onclick="selectOption(this)">
        <div class="quiz-option-radio"></div>
        <span>模型会降低所有回答的概率</span>
      </button>
    </div>
    <div class="quiz-feedback"></div>
  </div>

  <button class="quiz-check-btn" onclick="checkQuiz('quiz-module3')">检查答案</button>
  <button class="quiz-reset-btn" onclick="resetQuiz('quiz-module3')">重试</button>
</div>
```

---

## Drag-and-Drop Matching

Same pattern as codebase-to-course, adapted for matching concepts to definitions, methods to papers, etc.

**HTML:**
```html
<div class="dnd-container animate-in" id="dnd-module2">
  <div class="dnd-chips">
    <div class="dnd-chip" draggable="true" data-answer="grpo">GRPO</div>
    <div class="dnd-chip" draggable="true" data-answer="ppo">PPO</div>
    <div class="dnd-chip" draggable="true" data-answer="reinforce">REINFORCE</div>
  </div>
  <div class="dnd-zones">
    <div class="dnd-zone" data-correct="grpo">
      <p class="dnd-zone-label">使用组内相对优势估计，不需要价值网络</p>
      <div class="dnd-zone-target">拖放到这里</div>
    </div>
    <div class="dnd-zone" data-correct="ppo">
      <p class="dnd-zone-label">使用裁剪目标函数限制策略更新幅度</p>
      <div class="dnd-zone-target">拖放到这里</div>
    </div>
    <div class="dnd-zone" data-correct="reinforce">
      <p class="dnd-zone-label">最基础的策略梯度方法，使用蒙特卡洛采样</p>
      <div class="dnd-zone-target">拖放到这里</div>
    </div>
  </div>
  <div style="margin-top:var(--space-4)">
    <button class="btn" onclick="checkDnD('dnd-module2')">检查匹配</button>
    <button class="btn" onclick="resetDnD('dnd-module2')">重置</button>
  </div>
</div>
```

---

## Spot the Assumption

Shows a claim or experimental setup and asks the learner to identify the hidden assumption.

**Wiring:** Uses quiz-style selection via `window.selectAssumption(btn)` and `window.checkAssumption(containerId)`.

**HTML:**
```html
<div class="assumption-challenge animate-in" id="assumption-1"
     data-correct="option-b"
     data-explanation-right="正确！论文只在数学推理任务上测试，假设了这个方法在其他推理类型（如代码、常识推理）上也有效，但这并未被验证。"
     data-explanation-wrong="不太对。想想实验的范围和结论的泛化性...">
  <h3>找出以下结论中隐藏的假设：</h3>
  <div class="assumption-claim">
    "LoPE 通过在提示空间中添加扰动，有效地提升了大语言模型的推理探索能力。"
  </div>
  <div class="assumption-options">
    <button class="assumption-option" data-value="option-a" onclick="selectAssumption(this)">
      <div class="quiz-option-radio"></div>
      <span>假设了 Lorem Ipsum 是最优的扰动文本</span>
    </button>
    <button class="assumption-option" data-value="option-b" onclick="selectAssumption(this)">
      <div class="quiz-option-radio"></div>
      <span>假设了在数学推理上的提升可以泛化到其他推理任务</span>
    </button>
    <button class="assumption-option" data-value="option-c" onclick="selectAssumption(this)">
      <div class="quiz-option-radio"></div>
      <span>假设了更大的模型总是能获得更大的提升</span>
    </button>
  </div>
  <div class="assumption-feedback"></div>
  <button class="quiz-check-btn" onclick="checkAssumption('assumption-1')">检查答案</button>
</div>
```

---

## Ablation Toggle

Shows experimental results with different components removed. Each tab shows what happens when you remove one part.

**Wiring:** `window.showLayer(layerId, btn)` — same engine as layer toggle.

**HTML:**
```html
<div class="ablation-demo animate-in">
  <div class="ablation-tabs">
    <button class="ablation-tab active" onclick="showLayer('full', this)">完整 LoPE</button>
    <button class="ablation-tab" onclick="showLayer('no-prefix', this)">去掉随机前缀</button>
    <button class="ablation-tab" onclick="showLayer('no-norm', this)">去掉归一化</button>
  </div>
  <div class="ablation-viewport">
    <div class="ablation-layer" id="full" style="display:block">
      <div class="ablation-metric">78.3%</div>
      <div class="ablation-delta positive">+6.2% vs 基线</div>
      <p class="ablation-description">完整方法：随机前缀 + 组内归一化优势</p>
    </div>
    <div class="ablation-layer" id="no-prefix" style="display:none">
      <div class="ablation-metric">72.1%</div>
      <div class="ablation-delta neutral">与基线持平</div>
      <p class="ablation-description">去掉随机前缀后，方法退化为标准 GRPO</p>
    </div>
    <div class="ablation-layer" id="no-norm" style="display:none">
      <div class="ablation-metric">74.8%</div>
      <div class="ablation-delta positive">+2.7% vs 基线</div>
      <p class="ablation-description">去掉归一化后仍有提升，但效果减弱</p>
    </div>
  </div>
</div>
```

---

## Callout Boxes

Max 2 per module.

```html
<div class="callout callout-accent animate-in">
  <div class="callout-icon">&#128161;</div>
  <div class="callout-content">
    <strong class="callout-title">关键洞察</strong>
    <p>你不需要改变模型或奖励函数 — 只需要改变输入。这是 LoPE 最反直觉的地方。</p>
  </div>
</div>
```

**Variants:**
- `callout-accent`: key insights
- `callout-info`: good to know
- `callout-warning`: common misconceptions

---

## Contribution / Concept Cards

```html
<div class="contribution-cards stagger-children animate-in">
  <div class="contribution-card">
    <div class="contribution-num">1</div>
    <div class="contribution-text">
      <strong>提示空间扰动</strong>
      <p>在原始问题前拼接随机文本，改变模型的输入分布</p>
    </div>
  </div>
  <div class="contribution-card">
    <div class="contribution-num">2</div>
    <div class="contribution-text">
      <strong>零优势问题的解决</strong>
      <p>通过扰动使采样结果多样化，避免所有回答得到相同奖励</p>
    </div>
  </div>
</div>
```

---

## Paper Citation Cards

```html
<div class="paper-citation animate-in">
  <div class="paper-citation-title">DeepSeekMath: Pushing the Limits of Mathematical Reasoning</div>
  <div class="paper-citation-authors">Shao et al., 2024</div>
  <div class="paper-citation-summary">提出了 GRPO 方法，通过组内相对优势估计替代价值网络，简化了 RL 训练流程。本文在此基础上进一步探索提示空间扰动。</div>
</div>
```

---

## Flow Diagrams

```html
<div class="flow-steps animate-in">
  <div class="flow-step">
    <div class="flow-step-num">1</div>
    <p>原始提示</p>
  </div>
  <div class="flow-arrow">&rarr;</div>
  <div class="flow-step">
    <div class="flow-step-num">2</div>
    <p>添加噪声前缀</p>
  </div>
  <div class="flow-arrow">&rarr;</div>
  <div class="flow-step">
    <div class="flow-step-num">3</div>
    <p>模型采样 G 个回答</p>
  </div>
  <div class="flow-arrow">&rarr;</div>
  <div class="flow-step">
    <div class="flow-step-num">4</div>
    <p>奖励评估 + GRPO 更新</p>
  </div>
</div>
```

---

## Glossary Tooltips

Mark up EVERY technical term on first use per module.

```html
<p>LoPE 使用
  <span class="term" data-definition="GRPO（Group Relative Policy Optimization）：一种强化学习方法，通过比较同一组内多个回答的相对优劣来更新模型，不需要单独训练价值网络。">GRPO</span>
  作为基础训练框架，并在
  <span class="term" data-definition="提示空间（Prompt Space）：模型接收的输入文本构成的空间。改变提示就是改变模型看到的输入。">提示空间</span>
  中引入扰动。
</p>
```

**Rules:**
- Every technical term on first use per module
- Keep definitions to 1-2 sentences in everyday language
- Use bilingual format: `中文解释（English Term）`
- Don't mark the same term twice within the same screen
- Use `cursor: pointer` (not `cursor: help`)

---

## Numbered Step Cards

```html
<div class="step-cards stagger-children animate-in">
  <div class="step-card">
    <div class="step-num">1</div>
    <div class="step-body">
      <strong>采样阶段</strong>
      <p>对每个问题生成 G 个回答，使用标准 GRPO 采样</p>
    </div>
  </div>
  <div class="step-card">
    <div class="step-num">2</div>
    <div class="step-body">
      <strong>扰动阶段</strong>
      <p>在部分采样的问题前添加随机 Lorem Ipsum 前缀</p>
    </div>
  </div>
</div>
```

---

## Icon-Label Rows

```html
<div class="icon-rows stagger-children animate-in">
  <div class="icon-row">
    <div class="icon-circle" style="background: var(--color-actor-1)">&#129513;</div>
    <div>
      <strong>数学推理基准</strong>
      <p>GSM8K, MATH, Minerva 等数据集</p>
    </div>
  </div>
  <div class="icon-row">
    <div class="icon-circle" style="background: var(--color-actor-2)">&#129504;</div>
    <div>
      <strong>模型规模</strong>
      <p>1.7B, 4B, 7B 参数量的模型</p>
    </div>
  </div>
</div>
```
