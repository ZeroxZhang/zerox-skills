# Design System Reference

Complete CSS design tokens for the zerox-paper-to-course system. Copy `styles.css` verbatim into the course directory; customize only the accent color via `_base.html`.

## Table of Contents
1. [Color Palette](#color-palette)
2. [Typography](#typography)
3. [Spacing & Layout](#spacing--layout)
4. [Shadows & Depth](#shadows--depth)
5. [Animations & Transitions](#animations--transitions)
6. [Navigation & Progress](#navigation--progress)
7. [Module Structure](#module-structure)
8. [Responsive Breakpoints](#responsive-breakpoints)
9. [Math & Research Colors](#math--research-colors)
10. [SVG Diagram System](#svg-diagram-system)

---

## Color Palette

```css
:root {
  /* BACKGROUNDS */
  --color-bg:             #FAF7F2;       /* warm off-white */
  --color-bg-warm:        #F5F0E8;       /* alternating modules */
  --color-bg-code:        #1E1E2E;       /* code blocks */
  --color-text:           #2C2A28;
  --color-text-secondary: #6B6560;
  --color-text-muted:     #9E9790;
  --color-border:         #E5DFD6;
  --color-border-light:   #EEEBE5;
  --color-surface:        #FFFFFF;
  --color-surface-warm:   #FDF9F3;

  /* ACCENT (pick ONE — vermillion default) */
  --color-accent:         #D94F30;
  --color-accent-hover:   #C4432A;
  --color-accent-light:   #FDEEE9;
  --color-accent-muted:   #E8836C;

  /* SEMANTIC */
  --color-success:        #2D8B55;
  --color-success-light:  #E8F5EE;
  --color-error:          #C93B3B;
  --color-error-light:    #FDE8E8;
  --color-info:           #2A7B9B;
  --color-info-light:     #E4F2F7;

  /* ACTORS (research participants, methods, concepts) */
  --color-actor-1:        #D94F30;
  --color-actor-2:        #2A7B9B;
  --color-actor-3:        #7B6DAA;
  --color-actor-4:        #D4A843;
  --color-actor-5:        #2D8B55;
}
```

---

## Math & Research Colors

```css
:root {
  /* MATH — for equation blocks and derivations */
  --color-math-bg:        #F8F6F1;       /* warm cream */
  --color-math-border:    #D4C5A9;       /* warm gold */
  --color-math-text:      #3D3428;       /* dark brown */

  /* RESEARCH — for lineage/context elements */
  --color-research-bg:    #F0F4F8;       /* cool blue-gray */
  --color-research-accent:#2A5F8F;       /* deep blue */

  /* RESULTS — for experimental result displays */
  --color-result-pos:     #2D8B55;       /* green for improvements */
  --color-result-neg:     #C93B3B;       /* red for underperformance */
  --color-result-neutral: #6B6560;       /* gray for baselines */
}
```

---

## Typography

```css
:root {
  --font-display: 'Bricolage Grotesque', Georgia, serif;
  --font-body:    'DM Sans', -apple-system, sans-serif;
  --font-mono:    'JetBrains Mono', 'Fira Code', 'Consolas', monospace;

  /* TYPE SCALE (1.25 ratio) */
  --text-xs:   0.75rem;    /* labels, badges */
  --text-sm:   0.875rem;   /* secondary text, code */
  --text-base: 1rem;       /* body text */
  --text-lg:   1.125rem;   /* lead paragraphs */
  --text-xl:   1.25rem;    /* screen headings */
  --text-2xl:  1.5rem;     /* sub-module titles */
  --text-3xl:  1.875rem;   /* module subtitles */
  --text-4xl:  2.25rem;    /* module titles */
  --text-5xl:  3rem;       /* hero text */
  --text-6xl:  3.75rem;    /* module numbers */

  --leading-tight:  1.15;
  --leading-snug:   1.3;
  --leading-normal: 1.6;
  --leading-loose:  1.8;
}
```

---

## Spacing & Layout

```css
:root {
  --space-1:  0.25rem;   --space-2:  0.5rem;    --space-3:  0.75rem;
  --space-4:  1rem;      --space-5:  1.25rem;   --space-6:  1.5rem;
  --space-8:  2rem;      --space-10: 2.5rem;    --space-12: 3rem;
  --space-16: 4rem;      --space-20: 5rem;      --space-24: 6rem;

  --content-width:      800px;
  --content-width-wide: 1000px;
  --nav-height:         50px;
  --radius-sm:   8px;
  --radius-md:   12px;
  --radius-lg:   16px;
  --radius-full: 9999px;
}
```

---

## Shadows & Depth

```css
:root {
  --shadow-sm: 0 1px 2px rgba(44,42,40,0.05);
  --shadow-md: 0 4px 12px rgba(44,42,40,0.08);
  --shadow-lg: 0 8px 24px rgba(44,42,40,0.10);
  --shadow-xl: 0 16px 48px rgba(44,42,40,0.12);
}
```

---

## SVG Diagram System

All diagrams (flowcharts, concept maps, lineage trees, experimental frameworks) should use inline SVG with these conventions:

- Container: `.svg-diagram` class — responsive, max-width 800px, centered
- Nodes: `.node-rect` (default) or `.node-rect.accent` (highlighted)
- Edges: `.edge-line` (default) or `.edge-line.accent`
- Text: inherit from `var(--font-body)`, use `.mono` class for `var(--font-mono)`
- Colors: use CSS variables (`var(--color-accent)`, `var(--color-border)`, etc.)
- ViewBox: use `viewBox="0 0 WIDTH HEIGHT"` with `width="100%"` for responsiveness
- Complex diagrams: use `<foreignObject>` to embed HTML text blocks

```html
<svg class="svg-diagram" viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg">
  <rect class="node-rect accent" x="300" y="20" width="200" height="60" />
  <text x="400" y="55" text-anchor="middle" font-weight="700">This Paper</text>
  <line class="edge-line accent" x1="400" y1="80" x2="400" y2="120" />
  <polygon class="edge-arrow accent" points="395,120 405,120 400,130" />
  <!-- more elements -->
</svg>
```
