# Content Philosophy — Teaching Academic Papers

> **When to read this:** During Phase 3.5 (writing module briefs) and Phase 4 (writing module HTML). These principles guide every content decision.

## Core Principles

### Intuition First, Then Formalism

Every equation must be preceded by a plain-language sentence explaining what it means. Every algorithm must be preceded by an intuitive description of what it does. The learner should think "oh, that makes sense" before they see the math — the math then formalizes what they already understand.

**Example:** "The loss function measures how surprised the model is by its own answers — if it expected a different answer, the loss is high" → then show $L = -\log P(y|x)$.

### The Paper's Story

Every paper tells a story. Make that story explicit and narrative. "This paper is about a team that noticed their RL training was getting stuck, tried something counterintuitive (adding nonsense to prompts), and discovered it worked." This narrative framing helps learners remember the technical content.

Structure each module as a chapter in that story, not as a section summary.

### Show, Don't Tell — Aggressively Visual

**Text limits:**
- Max 2-3 sentences per text block
- Every screen must be at least 50% visual (diagrams, equations, cards, animations, SVG figures)
- Convert lists of 3+ items into cards, sequences into step cards or flow diagrams

**Convert text to visuals:**
- A list of methods → concept cards or pattern cards
- A pipeline of steps → SVG flow diagram or animated data flow
- An experimental framework → SVG architecture diagram
- Comparing results → interactive result comparison bars
- Research relationships → lineage tree (SVG or HTML)

### One Concept Per Screen

No walls of text. Each screen teaches exactly one idea. If you need more space, add another screen.

### Original Text, Not Paraphrase

The paper's actual text should be quoted sparingly — only for key definitions or claims. The course EXPLAINS the paper, not reproduces it. Direct quotes should be clearly marked with quotation marks and citation references.

### Question Everything — Critical Reading

Teach learners to read papers critically:
- Every experimental result should prompt: "Is this significant?"
- Every method choice should prompt: "Why this and not something else?"
- Every limitation should be surfaced, not hidden
- If the paper only tested on one dataset, say so
- If the improvement is within noise margins, say so

### Knowledge Expansion — Beyond the Paper

A paper exists within a research lineage. Actively expand beyond the paper:
- **Prerequisite concepts**: things you need to know before reading (math, algorithms, domain concepts)
- **Related work**: what else has been tried, how this paper differs
- **Research context**: where this paper fits in the field's evolution
- Pick the 3-5 most important related papers and give each a styled citation card

### Guided Entry — Background Before Content

Never start a course by throwing the learner into the paper's problem statement. A "curious practitioner" needs context first. Module 0 (Background & Prerequisites) should:

- Identify the 3-5 most important prerequisite concepts
- Explain each with intuition first, then formalism only if needed
- Use a "knowledge map" SVG to show how concepts connect
- Clearly mark this content as "background you need" vs. "what the paper says"
- Include at least one quiz to verify understanding before proceeding

The goal is that by the time the learner reaches Module 1, they have the vocabulary and mental models to understand the paper's contribution without getting lost in jargon.

### Make It Memorable

Use "aha!" callout boxes for key insights. Use humor where natural. Give methods and concepts personality.

### Glossary Tooltips — No Term Left Behind

Every technical term gets a tooltip on first use per module. Be extremely aggressive:
- Mathematical symbols ($\mathbb{E}$, $\arg\max$, softmax, KL divergence)
- Domain jargon (rollout, advantage function, policy gradient, perplexity)
- Acronyms (GRPO, PPO, RLHF, LoRA) — ALWAYS tooltip on first use
- Software/model names the learner might not know

**Tooltip format (bilingual):** `中文解释（English Term）` — e.g., "策略梯度（Policy Gradient）：一种通过计算策略的梯度来更新模型参数的优化方法"

Do NOT tooltip terms the learner likely knows from general education (e.g., "hypothesis," "experiment," "control group").

### SVG Diagrams for Visual Explanation

Use inline SVG for:
- Concept relationship diagrams
- Research lineage trees
- Experimental framework overviews
- Algorithm flowcharts
- Comparison matrices

SVGs should use the design system's CSS variables for colors, fonts, radii, and shadows. Keep them responsive with `viewBox` + `width="100%"`.

---

## Quiz Philosophy

Quizzes should test whether the learner can APPLY their knowledge, not regurgitate definitions.

**What to quiz (in order of value):**
1. **"What would you expect?" scenarios** — Given a modified experimental setup, what result would you predict?
2. **"What went wrong?" scenarios** — Given a surprising result, what explanation fits?
3. **Design decisions** — Why did the authors choose X over Y?
4. **Critical reading** — "Which of these conclusions is NOT supported by the data shown?"
5. **Tracing exercises** — "Trace the path from input to output in this algorithm."

**What NOT to quiz:**
- Definitions — that's what glossary tooltips are for
- Factual recall — nobody memorizes author names or years
- Anything answerable by scrolling up and copying

**Quiz tone:**
- Wrong answers get encouraging explanations ("不太对，原因是...")
- Correct answers get brief reinforcement ("正确！这是因为...")
- Never punitive, never score-focused
