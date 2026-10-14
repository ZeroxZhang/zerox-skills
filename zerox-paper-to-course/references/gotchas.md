# Gotchas — Common Failure Points

> **When to read this:** During Phase 4 (writing module HTML) and Phase 5 (review). Check every one of these before considering a course complete.

---

### Tooltip Clipping

Translation blocks and math blocks use `overflow: hidden`. If tooltips use `position: absolute` inside the term element, they get clipped. **Fix:** Tooltips must use `position: fixed` and be appended to `document.body`. Already handled by `main.js`.

### Not Enough Tooltips

The #1 failure is under-tooltipping. Math symbols are the most commonly missed. If a term wouldn't appear in everyday conversation with a non-technical friend, tooltip it. Err heavily on the side of too many.

### Math Without Intuition

Showing an equation without first explaining what it means in plain language. **Every equation must have:**
1. A preceding intuition sentence (what does this mean?)
2. The equation itself
3. A following "what this means" sentence (why does this matter?)

### Results Without Context

Showing "78.3% accuracy" without explaining what that number means. Is that good? Compared to what? What is the ceiling? Every result number needs a comparison anchor.

### Walls of Text

Writing more than 2-3 sentences in a row without a visual break. Every screen must be at least 50% visual. Convert any list of 3+ items into cards, any sequence into step cards or flow diagrams.

### Skipping Prerequisites

Assuming the learner knows what "KL divergence" or "policy gradient" means. Module 0 (Background & Prerequisites) exists for this reason. If a concept appears in Module 1+, it must have been taught in Module 0 or tooltipped.

### Treating the Paper as Infallible

The course should surface limitations, not just celebrate results. If the paper only tested on one dataset, say so. If the improvement is within noise margins, say so. Critical reading is a skill.

### Citation Sprawl

Listing 15 related papers in a wall of text. Instead, pick the 3-5 most important related papers and give each a styled citation card (`.paper-citation`) with a one-sentence summary.

### KaTeX Rendering Failures

Math blocks that don't render because of LaTeX syntax errors. Common pitfalls:
- Using `\begin{align}` — not supported by KaTeX auto-render without config. Use `aligned` inside `$$...$$` instead.
- Using `\mathbb` without ensuring KaTeX supports it (it does by default).
- Single `$` delimiters conflicting with text — ensure spaces around inline math.

### Pseudocode That Is Actually Code

Writing pseudocode that looks like Python or C++. Pseudocode should be language-agnostic and readable by someone who does not program. Use `INPUT`, `OUTPUT`, `FOR EACH`, `IF...THEN` style.

### Scroll-Snap Mandatory

Using `scroll-snap-type: y mandatory` traps users inside long modules. Always use `proximity`.

### Module Quality Degradation

Trying to write all modules in one pass causes later modules to be thin. Build one module at a time. For complex papers, use the parallel path with module briefs.

### Missing Interactive Elements

A module with only text and equations, no interactivity. Every module needs at least one of: quiz, data flow animation, research dialogue, math derivation, pseudocode walkthrough, result comparison.

### SVG Diagrams Not Responsive

SVG without `viewBox` or with fixed `width`/`height` in pixels. Always use `viewBox="0 0 W H"` with `width="100%"` and no fixed height.

### Language Inconsistency

Mixing languages within a course. Once the output language is determined (default: 简体中文), ALL content should be in that language. Only technical terms keep their English originals in parentheses.

### Missing Cover Page

Starting the course directly with Module 1 — no paper title, authors, abstract, or metadata. Every course must have a `_cover.html` hero section before the modules.

### Missing Module 0 (Prerequisites)

Jumping straight into the paper's problem without teaching prerequisite concepts. Module 0 is mandatory — it should teach the foundational knowledge a "curious practitioner" needs before reading the paper.

### Sidebar Not Syncing

Sidebar active state not updating on scroll, or click navigation not working. The sidebar items must map 1:1 to modules (same order as nav-dots), and `updateSidebar()` must be called from `updateProgress()`.

### Cover Page Using `.module` Class

The cover page must NOT use the `.module` class — it should use `.course-cover`. Using `.module` would break nav-dot and sidebar mapping since they query `$$('.module')`.
