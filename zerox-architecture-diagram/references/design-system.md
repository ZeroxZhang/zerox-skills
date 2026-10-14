# Diagram Design System

Use this reference after geometry is planned. Keep the semantic structure stable and change visual tokens rather than duplicating ad-hoc styles.

## Contents

1. [Self-contained SVG](#self-contained-svg)
2. [Theme tokens](#theme-tokens)
3. [Semantic component palette](#semantic-component-palette)
4. [Typography](#typography)
5. [Component pattern](#component-pattern)
6. [Edges and markers](#edges-and-markers)
7. [Lanes and groups](#lanes-and-groups)
8. [Icons and tooltips](#icons-and-tooltips)
9. [HTML shell](#html-shell)

## Self-contained SVG

Put the font stack, theme tokens, component classes, marker definitions, and grid pattern inside the SVG. Do not rely on `body` inheritance, Google Fonts, external images, or an HTML stylesheet.

```svg
<svg xmlns="http://www.w3.org/2000/svg"
     width="1000" height="760"
     viewBox="0 0 1000 760"
     preserveAspectRatio="xMidYMin meet"
     role="img"
     aria-labelledby="diagram-title diagram-desc"
     data-diagram-version="1"
     data-mode="standard"
     data-theme="light"
     data-base-grid="10"
     data-major-grid="20">
  <title id="diagram-title">系统架构图</title>
  <desc id="diagram-desc">从用户接入到应用与数据服务的系统架构。</desc>
  <defs>...</defs>
  <style>...</style>
  ...
</svg>
```

Use `fill-opacity` with hex colors instead of `rgba(...)` presentation attributes for broader Office, Keynote, and SVG viewer compatibility.

## Theme tokens

Use an internal style block:

```svg
<style>
  svg {
    font-family: 'SimHei', 'Microsoft YaHei', 'PingFang SC',
      'JetBrains Mono', ui-monospace, monospace;
    --canvas: #ffffff;
    --grid: #e2e8f0;
    --text: #1e293b;
    --muted: #64748b;
    --mask: #ffffff;
    --line: #64748b;
    --legend-fill: #f8fafc;
    --legend-stroke: #cbd5e1;
  }
  svg[data-theme='dark'] {
    --canvas: #0f172a;
    --grid: #1e293b;
    --text: #f1f5f9;
    --muted: #94a3b8;
    --mask: #0f172a;
    --line: #94a3b8;
    --legend-fill: #1e293b;
    --legend-stroke: #475569;
  }
  text { fill: var(--text); }
  .muted { fill: var(--muted); }
  .route { fill: none; stroke: var(--line); stroke-width: 1.5; }
</style>
```

Set `data-theme` on the SVG itself. A dark HTML body does not turn a light inline SVG into a dark standalone SVG.

## Semantic component palette

| `data-type` | Light fill / stroke / text | Dark fill / stroke / text |
|---|---|---|
| `frontend` | `#ecfeff` / `#0891b2` / `#155e75` | `#164e63` / `#22d3ee` / `#a5f3fc` |
| `backend` | `#ecfdf5` / `#059669` / `#065f46` | `#064e3b` / `#34d399` / `#6ee7b7` |
| `database` | `#f5f3ff` / `#7c3aed` / `#5b21b6` | `#4c1d95` / `#a78bfa` / `#c4b5fd` |
| `cache` | `#faf5ff` / `#9333ea` / `#6b21a8` | `#581c87` / `#c084fc` / `#d8b4fe` |
| `cloud` | `#fffbeb` / `#d97706` / `#92400e` | `#78350f` / `#fbbf24` / `#fde68a` |
| `security` | `#fff1f2` / `#e11d48` / `#9f1239` | `#881337` / `#fb7185` / `#fda4af` |
| `message-bus` | `#fff7ed` / `#ea580c` / `#9a3412` | `#7c2d12` / `#fb923c` / `#fdba74` |
| `gateway` | `#ecfeff` / `#0891b2` / `#155e75` | `#164e63` / `#22d3ee` / `#a5f3fc` |
| `container` | `#eff6ff` / `#2563eb` / `#1e40af` | `#1e3a8a` / `#60a5fa` / `#93c5fd` |
| `external` | `#f8fafc` / `#64748b` / `#334155` | `#334155` / `#94a3b8` / `#cbd5e1` |
| `ai-ml` | `#fdf2f8` / `#db2777` / `#be185d` | `#831843` / `#f472b6` / `#fbcfe8` |
| `observability` | `#f0fdfa` / `#0d9488` / `#0f766e` | `#134e4a` / `#2dd4bf` / `#5eead4` |
| `object-storage` | `#eef2ff` / `#4f46e5` / `#4338ca` | `#312e81` / `#818cf8` / `#a5b4fc` |

Use the fill at 90% opacity in light mode and 30% opacity in dark mode, always over the opaque mask. Keep the text/stroke pair from the same row and theme.

## Typography

- Visible SVG title: 20px, centered, weight 700. Presentation: 18px.
- Subtitle: 10px, centered, muted.
- Component label: 11–12px, weight 600.
- Component sublabel: 9px, muted.
- Edge label: 8–9px.
- Lane/group label: 10px, weight 600.
- Legend: 8–10px.

Chinese is primary by default. Technical names, protocols, versions, and ports may remain English. Avoid ultra-light gray text; body-sized text should meet WCAG AA contrast against its actual background.

Keep a visible title inside the SVG so extraction does not discard the diagram identity. The HTML page may use a smaller context heading rather than repeating the same large title.

## Component pattern

Every component uses one semantic group. `<title>` is the first child so tooltips and accessibility remain reliable.

```svg
<g data-role="component"
   data-id="api"
   data-type="backend"
   data-lane="application"
   data-group="aws-west"
   data-bbox="420,240,140,60">
  <title>API 服务器&#10;类型：后端服务&#10;FastAPI :8000</title>
  <rect data-role="mask" x="420" y="240" width="140" height="60"
        rx="6" fill="var(--mask)"/>
  <rect data-role="box" class="node-box" x="420" y="240"
        width="140" height="60" rx="6"/>
  <text class="node-label" x="490" y="265" text-anchor="middle">API 服务器</text>
  <text class="node-subtitle" x="490" y="281" text-anchor="middle">FastAPI :8000</text>
</g>
```

Use `rx="6"`, 1.5px strokes, and `vector-effect="non-scaling-stroke"` on borders and routes when practical.

## Edges and markers

Draw edge routes before components and edge labels after components.

```svg
<marker id="arrow-neutral" markerWidth="8" markerHeight="8"
        refX="8" refY="4" orient="auto" markerUnits="userSpaceOnUse">
  <path d="M 0 0 L 8 4 L 0 8 Z" fill="#64748b"/>
</marker>
```

The marker tip is exactly at `refX`, so a route ending 2px before a target retains the intended 2px gap. Create theme-appropriate fixed-color marker variants; do not pair a purple route with a violet marker.

| Edge kind | Stroke | Pattern |
|---|---|---|
| Sync/data | Neutral or source semantic color | Solid `1.5` |
| Auth/security | Rose | `stroke-dasharray="5 5"` |
| Async/event | Orange | `stroke-dasharray="2 4"` |
| Replication/cross-region | Purple | `stroke-dasharray="6 4"` |
| Return | Neutral | Solid, routed through outer channel |

For bidirectional traffic, use two separately identified edges with parallel 8px spacing. Do not use one ambiguous double-headed line when direction matters.

## Lanes and groups

Order large background structures as groups first, then lanes, then routes. Prefer `fill="none"` on region/AZ boundaries; if a fill is necessary, use low opacity and ensure it does not recolor nested lanes.

```svg
<g data-role="lane" data-id="application" data-bbox="20,200,960,160">
  <rect x="20" y="200" width="960" height="160" rx="4"
        fill="#ecfdf5" fill-opacity="0.35"/>
  <text x="40" y="226" class="lane-label">应用层</text>
</g>
```

Boundary strokes:

- Region: `stroke-dasharray="8 4"`, `rx="12"`.
- AZ: `stroke-dasharray="2 3"`, `rx="8"`.
- Security group: `stroke-dasharray="4 4"`, rose stroke.

## Icons and tooltips

Icons are decorative and stay inside the declared node bbox. Set `aria-hidden="true"` on their group. Keep icons 16×16 with 1.2px strokes. Use a generic server icon when a brand-specific icon is unavailable; never invent a vendor mark.

Supported generic icons:

- server
- database
- cloud
- shield
- container / Kubernetes
- user/device
- queue/event
- object storage
- observability

If an icon sits above the label, shift the text down and include the icon in the sizing pass. Full component details belong in the native component `<title>`, not in a custom JavaScript tooltip.

## HTML shell

The HTML wrapper is responsive; the SVG geometry itself remains stable.

```css
body {
  margin: 0;
  padding: clamp(12px, 3vw, 32px);
  background: #f8fafc;
  color: #1e293b;
}
.diagram-scroll {
  overflow: auto;
  overscroll-behavior-inline: contain;
}
.diagram-scroll svg {
  display: block;
  width: 100%;
  min-width: 900px;
  height: auto;
}
@media (max-width: 640px) {
  .diagram-card { padding: 8px; }
}
```

Make the scroll region keyboard-focusable with `tabindex="0"` and an `aria-label`. In presentation mode, omit page cards/footer and use the true 1280×720 template; CSS alone must not pretend that a standard viewBox is presentation-ready.
