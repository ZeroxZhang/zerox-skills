---
name: zerox-architecture-diagram
description: Create and review professional system architecture, infrastructure, cloud, security, network-topology, deployment, and data-flow diagrams as self-contained HTML plus standalone SVG. Use this skill whenever a user wants to visualize technical components or service relationships, especially when layout, swimlanes, edge routing, multi-region grouping, presentation mode, or export quality matters.
license: MIT
metadata:
  version: "5.0"
  author: ZeroxZhang
---

# Architecture Diagram Skill

Create readable architecture diagrams whose layout remains correct after SVG extraction, browser resizing, and presentation export. Treat layout as a deterministic pipeline, not a collection of hand-tuned coordinates.

## Required resources

Read these files before generating a diagram:

1. `references/layout.md` — graph model, sizing, placement, ports, routing, labels, and viewBox calculation.
2. `references/design-system.md` — themes, typography, component styles, icons, and SVG patterns.
3. `references/quality-gates.md` — semantic SVG contract, validator usage, visual review, and output requirements.

Use `assets/template.html` for standard scrollable output. For presentation output, use `assets/template-presentation.html`; changing only CSS does not create a valid 16:9 layout.

## Workflow

Follow the seven stages in order. A later stage may send the work back to an earlier stage when validation exposes a layout defect.

### 1. Resolve requirements

Infer values from context when safe. Otherwise ask only for choices that materially change the diagram.

| Setting | Default | Options |
|---|---|---|
| Theme | Light | Light, Dark |
| Language | Chinese | Chinese, English |
| Mode | Standard | Standard, Presentation |
| Style | Icon when available | Icon, Text-only |
| Flow direction | Auto | LR, TB |
| Scope | Single region | Single region, Multi-region / Multi-AZ |

Direction rules:

- Use `TB` when horizontal bands represent primary tiers such as 接入层 / 应用层 / 数据层.
- Use `LR` for request or data pipelines without primary horizontal tiers.
- Do not use `layer` ambiguously. `rank` means graph depth, `lane` means a visual band, and `group` means a containing boundary such as Region, AZ, cluster, or trust domain.

### 2. Normalize the graph

Assign every object a stable ASCII ID before choosing coordinates.

- Node: `id`, label, sublabel, type, icon, rank, lane, group.
- Edge: `id`, source, target, kind, label, preferred ports, optional bus ID.
- Lane: `id`, label, order.
- Group: `id`, label, parent group, padding.

Treat message buses and gateways as real nodes when they have independent semantics. Preserve cycles; mark their return edges for an outer route channel.

### 3. Write the layout plan

Place this plan as an HTML comment immediately before the SVG. List every node and edge.

```text
MODE standard  THEME light  DIRECTION TB  GRID base=10 major=20
LANE access       order=0 label="接入层"
GROUP aws-west    parent=- label="AWS 区域: us-west-2"
NODE api          rank=1 lane=application group=aws-west x=420 y=240 w=140 h=60 type=backend icon=server
EDGE api-db       api:right -> db:left kind=sync label="SQL" bus=api-data
```

The plan is the source of truth for graph completeness; SVG metadata must use the same IDs.

### 4. Run the layout pipeline

Use the algorithms and constants in `references/layout.md`:

1. Measure text and determine node sizes.
2. Assign ranks and order nodes to reduce crossings.
3. Size lanes and nested groups from their content.
4. Assign coordinates using actual rank widths and node heights.
5. Assign source and target ports.
6. Route orthogonal edges around inflated obstacles.
7. Place labels, legend, and title; then derive the viewBox from the union of all geometry.

Do not write SVG routes until node, lane, and group geometry is stable.

### 5. Generate semantic SVG and HTML

Start from the mode-specific template and preserve its semantic hooks:

- `data-role="boundary|lane|edge-route|bus-trunk|component|edge-label|legend"`
- stable `data-id`, `data-edge-id`, `data-source`, and `data-target`
- explicit geometry in `data-bbox` and route points in `data-points`
- SVG-local styles, font stack, markers, title, and description

Render in this order:

```text
background -> boundaries -> lanes -> edge routes / bus trunks
-> component masks and boxes -> component text/icons
-> edge labels -> legend
```

Draw a shared bus trunk once. Draw each branch once from its junction to its target. Use a neutral trunk if branches have different semantics.

### 6. Extract and validate

Extract the exact inline SVG:

```bash
python3 scripts/extract_svg.py output.html output.svg
```

Run the deterministic quality gate on both artifacts:

```bash
python3 scripts/validate_diagram.py output.html --strict
python3 scripts/validate_diagram.py output.svg --strict
python3 scripts/validate_diagram.py output.html --compare output.svg --strict
```

Fix the layout model or algorithm that caused a failure. Do not silence a check or move a single label without re-running the complete gate.

### 7. Rendered review

Run the browser-backed geometry probe when Chrome/Chromium is available:

```bash
python3 scripts/render_check.py output.html --width 1440 --height 900
python3 scripts/render_check.py output.svg --width 1000 --height 760
# Presentation mode:
python3 scripts/render_check.py output.html --width 1280 --height 720
```

Then open both files and inspect the actual rendered result.

- Standard: desktop and narrow viewport; horizontal scrolling is allowed only inside the diagram region.
- Presentation: exact 1280×720 viewBox with no clipping.
- Verify long Chinese/English labels, marker tips, tooltips, dark theme, and standalone SVG fonts.
- Inspect at 100% and 200% zoom.

The static validator checks declared geometry. Browser review remains required because final glyph metrics vary by platform.

## Layout invariants

These are hard constraints; the detailed calculations live in `references/layout.md`.

- Base grid: 10px for node coordinates and sizes. Major grid: 20px for lanes, groups, rank origins, and viewBox dimensions.
- Node gap: at least 40px on the axis where their projections overlap.
- Route clearance: at least 20px from unrelated nodes and 8px between parallel routes.
- Source endpoint: on the declared source boundary. Target endpoint: 2px before the declared target boundary, with the final segment pointing toward it.
- Route shape: absolute orthogonal `M/L` segments only; no diagonal segment unless the user explicitly requests free-form routing.
- Labels: reserve a label corridor and keep a 4px gap from components, boundaries, and other labels.
- Lanes: reserve a label gutter; nodes must lie inside the lane content rectangle.
- Groups: derive size from contained geometry plus title gutter and padding. Layout inner groups before outer groups.
- Standard legend: centered horizontally and at least 20px below all content boundaries.
- Presentation legend: bottom-right with 20px right/bottom margins; it is not subject to the standard centering rule.
- Standard viewBox: content-derived, at least 1000×680, snapped up to the 20px major grid.
- Presentation viewBox: exactly `0 0 1280 720`.

## Language and accessibility

Chinese is the default for titles, node labels, lane labels, edge labels, legends, and summaries. Keep proper nouns, protocols, ports, and technologies in their conventional form.

Every SVG must include:

- `xmlns="http://www.w3.org/2000/svg"`
- numeric intrinsic `width` and `height` matching the viewBox
- `role="img"` and `aria-labelledby`
- one overall `<title>` and `<desc>`
- one native `<title>` as the first child of every component group
- an SVG-local font stack; do not rely on HTML inheritance or remote fonts

## Output

Always return two self-contained files:

1. `.html` — inline SVG, embedded CSS, optional summary cards, no runtime JavaScript, no external fonts/images/stylesheets.
2. `.svg` — the exact extracted SVG, with local styles/defs/tooltips and no HTML dependency.

Report the chosen mode, direction, validator result, and any intentionally allowed crossing or exception.
