> Language: [简体中文](README.md) · [English](README_EN.md)

# Consulting Deck Skill · Concise

Maintained at: [zerox-consulting-deck-skill-concise](https://github.com/ZeroxZhang/zerox-skills/tree/main/zerox-consulting-deck-skill-concise).

**Turn a pile of raw material into a consulting report you can hand to a client.**

Give it financials, interviews, industry research or a rough draft. It analyses first, then organises the findings into a full report with a clear storyline, real exhibits and traceable evidence — delivered as a paginated HTML file plus a matching PDF.

[![Full deck overview](docs/showcase/report-overview.png)](docs/showcase/report-page-mechanism.png)

## What the output looks like

| | |
|---|---|
| ![Two revenue mechanisms compared](docs/showcase/report-page-mechanism.png) | ![Ranking signal and its conditions](docs/showcase/report-page-metric.png) |
| Two business lines compared on mechanism, capability and risk | A large figure with a dot matrix, next to the conditions under which it holds |
| ![Separated denominators](docs/showcase/report-page-caveats.png) | |
| Two figures from different denominators stay separate — no fabricated trend line | |

The result is a **single self-contained HTML file**: open it and it works, with navigation, zoom, full screen, deep links and an embedded one-click download of the matching PDF. Offline and forwardable.

## What makes it different

- **Analysis before expression.** Material is read at the level of detail, distribution and measurement basis; the work is real calculation, comparison and mechanism reasoning — not bullets distilled from a summary.
- **If the title claims it, the exhibit must show it.** Claims of a chain, a gap or a condition must be findable in the exhibit itself; when modules are shortened the whole page is re-planned.
- **Nothing counts as done until it has been looked at.** Every page is reviewed as an HTML screenshot and in the final PDF, with a concrete judgement. When the tool cannot see images it says so rather than substituting an automated pass.
- **Key caveats are not quietly dropped.** Denominators, periods, negations and the fact/forecast distinction are bound to real page objects and verified as present in the final PDF.

Three input states are supported: **raw material** (full analysis), **open research** (explore then converge), and **confirmed copy** (keep the facts and conclusions, reorganise only).

## Getting started

From the `zerox-skills` repository root, copy or symlink `zerox-consulting-deck-skill-concise` into your tool's skills directory:

```bash
ln -s "$(pwd)/zerox-consulting-deck-skill-concise" ~/.codex/skills/zerox-consulting-deck-skill-concise
```

Then invoke `/zerox-consulting-deck-skill-concise` and state **the audience and the question, the material you have, and any hard constraints**. No need to specify page count, chart types or frameworks up front.

Before you start: a full deck takes **roughly 1–2 hours** (it varies with task size) and **consumes noticeably more tokens than ordinary Q&A** — research, page-by-page authoring, screenshot review and independent review all really run. The skill states this cost up front and waits for your confirmation. A **multimodal model that can read images** and a **current SOTA model** are recommended. Prompt examples and input guidance: [skill README](docs/usage.md#怎么用).

Full product description, deliverable contract and build instructions: [skill README](docs/usage.md).

## Repository layout

| Content | Location |
|---|---|
| Skill entry (completion criteria, six-step spine, hard contract, commands) | [SKILL.md](SKILL.md) |
| On-demand references (chart selection, analysis, precision, delivery, …) | [references/](references/) |
| Engine, themes, fonts, exhibit runtime | [assets/](assets/) |
| Authoring and maintenance scripts | [scripts/](scripts/) |
| Optional external selection advisor (off by default; no snapshot bundled) | [echarts-viz-planner](https://github.com/ZeroxZhang/echarts-viz-planner) |

This directory presents the skill itself. Development records, past iterations and reviews are kept locally and are not distributed with the repository.

## Boundaries

Delivery is **HTML + matching PDF**; no PPTX. It performs analysis and expression but does not replace external fact-checking — the provenance of source material (fact / estimate / interviewee view) is preserved as given. Automated checks provide engineering evidence, not commercial judgement; a "pass" only covers what was actually checked.

The three themes (McKinsey / BCG / Accenture) are independent adaptations of publicly available visual material, **not any firm's official internal template**. Report content shown here is demonstration material; sources and provenance are marked on the pages themselves.
