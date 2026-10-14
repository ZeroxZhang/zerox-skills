# Quality Gates and Semantic SVG Contract

The templates and generated artifacts must satisfy both static geometry checks and a rendered browser review. The semantic contract makes layout defects detectable without guessing which `<rect>` is a node or which `<path>` is an icon.

## Contents

1. [Root contract](#root-contract)
2. [Object contract](#object-contract)
3. [Validation commands](#validation-commands)
4. [Static checks](#static-checks)
5. [Rendered checks](#rendered-checks)
6. [Exceptions](#exceptions)
7. [Pre-output checklist](#pre-output-checklist)

## Root contract

The SVG root must declare:

```svg
<svg xmlns="http://www.w3.org/2000/svg"
     width="WIDTH" height="HEIGHT"
     viewBox="0 0 WIDTH HEIGHT"
     role="img"
     aria-labelledby="diagram-title diagram-desc"
     data-diagram-version="1"
     data-mode="standard|presentation"
     data-theme="light|dark"
     data-direction="LR|TB"
     data-base-grid="10"
     data-major-grid="20">
```

The first semantic children are an accessible `<title>`, `<desc>`, and a machine-readable model:

```svg
<metadata id="diagram-model">{
  "nodes": [
    {"id":"api","type":"backend","lane":"application","group":"aws-west"}
  ],
  "edges": [
    {"id":"api-db","source":"api","target":"db","kind":"sync","bus":"api-data"}
  ]
}</metadata>
```

The metadata node/edge sets must exactly match semantic component and edge elements. Keep the ASCII layout plan immediately before the SVG for human review.

## Object contract

### Component

```svg
<g data-role="component" data-id="api" data-type="backend"
   data-lane="application" data-group="aws-west"
   data-bbox="420,240,140,60">
  <title>...</title>
  <rect data-role="mask" .../>
  <rect data-role="box" .../>
  ...
</g>
```

`data-bbox` is `x,y,width,height` and must match both mask and box geometry.

### Edge route

```svg
<path data-role="edge-route" data-edge-id="api-db"
      data-source="api" data-target="db" data-kind="sync"
      data-source-side="right" data-target-side="left"
      data-points="560,270 580,270 580,430 638,430"
      d="M 560 270 L 580 270 L 580 430 L 638 430"/>
```

Use absolute `M/L` commands. `data-points` must describe the same visible route.

For a bus, use a separate trunk and branches:

```svg
<path data-role="bus-trunk" data-bus-id="api-data"
      data-source="api" data-source-side="right"
      data-points="560,270 580,270" d="M 560 270 L 580 270"/>
<path data-role="edge-route" data-edge-id="api-db" data-bus-id="api-data"
      data-source="api" data-target="db"
      data-points="580,270 580,430 638,430"
      d="M 580 270 L 580 430 L 638 430"/>
```

The validator treats the trunk start as the bus source endpoint and each branch start as the shared junction.

### Edge label

```svg
<text data-role="edge-label" data-edge-id="api-db"
      data-bbox="586,408,22,12" x="597" y="418"
      text-anchor="middle">SQL</text>
```

The bbox is the conservative planned text extent, including 2px safety padding. Browser review verifies actual glyph bounds.

### Lane, boundary, title, and legend

```svg
<g data-role="lane" data-id="application" data-bbox="20,200,960,160">...</g>
<g data-role="boundary" data-id="aws-west" data-bbox="200,80,600,540">...</g>
<text data-role="diagram-title" data-bbox="380,18,240,24">系统架构图</text>
<g data-role="legend" data-bbox="250,660,500,80">...</g>
<g data-role="legend-item" data-type="backend">...</g>
```

Every declared bbox must contain the visible geometry owned by that semantic object.

## Validation commands

Extract first, then validate HTML, SVG, and parity:

```bash
python3 scripts/extract_svg.py diagram.html diagram.svg
python3 scripts/validate_diagram.py diagram.html --strict
python3 scripts/validate_diagram.py diagram.svg --strict
python3 scripts/validate_diagram.py diagram.html --compare diagram.svg --strict
python3 scripts/render_check.py diagram.html --width 1440 --height 900
python3 scripts/render_check.py diagram.svg --width 1000 --height 760
```

Exit codes:

- `0`: all required checks pass.
- `1`: one or more validation failures.
- `2`: input, parsing, or validator execution failure.

Use `--json` for a machine-readable report. `--strict` upgrades warnings such as undeclared edge crossings to failures.

## Static checks

The bundled validator checks:

### Structure and parity

- SVG namespace, viewBox, mode/theme/direction, title, description, and local `<style>`.
- Unique semantic IDs and valid source/target references.
- Metadata node/edge sets equal rendered node/edge sets.
- HTML inline SVG and standalone SVG normalize to the same XML tree.
- Marker references resolve to existing IDs.

### Geometry

- Component bbox matches its box and mask.
- Node coordinates/sizes align to the base grid.
- Lane, group, and viewBox geometry aligns to the major grid.
- Nodes do not overlap and maintain the minimum projected-axis gap.
- Nodes stay inside their declared lane/group content area.
- Routes use orthogonal segments and remain inside the viewBox.
- Non-bus routes start on their source boundary and end 2px before the target boundary.
- Bus trunks start on the source boundary; branches start at the common junction.
- Routes do not intersect unrelated components.
- Collinear overlap longer than 10px requires the same bus ID.
- Undeclared perpendicular crossings are reported.
- Planned label bboxes do not intersect nodes, other labels, or the viewBox edge.

### Composition

- Standard viewBox is at least 1000×680 and uses a centered legend.
- Presentation viewBox is exactly 1280×720 and uses a bottom-right legend.
- Legend sits at least 20px away from nodes and boundaries.
- Every used component type appears in the legend.
- DOM z-order is `route < component < edge-label < legend`.

## Rendered checks

Static geometry cannot know the exact glyph metrics of every platform font. Open both artifacts in a browser and verify:

- `getBBox()` for every edge label stays outside component and label bboxes.
- Long Chinese and English labels do not overflow or clip.
- Marker tips retain the intended target gap.
- HTML and standalone SVG use the same computed font family, font size, and visible title.
- Dark SVG colors remain dark after extraction.
- No HTTP request is needed to render fonts, icons, CSS, or images.
- Keyboard focus reaches the diagram scroll region and each component tooltip remains available.

`scripts/render_check.py` automates the actual `getBBox()` collision checks and page-level horizontal-overflow check with a local Chrome/Chromium binary. It exits with code `2` when no compatible browser is available; report that as `validator_unavailable` rather than claiming a rendered pass.

Viewport matrix:

```text
Standard: 1440×900, 1024×768, 375×812, and 200% zoom
Presentation: exact 1280×720
```

Only `.diagram-scroll` may overflow horizontally in standard mode. The overall page must remain scrollable vertically and must not clip content with `overflow:hidden`.

## Exceptions

An unavoidable crossing must be explicit:

```svg
<path data-role="edge-route" ...
      data-allow-crossing="true"
      data-exception-reason="跨区域复制链路共用边界网关"/>
```

Use exceptions only after trying rank reordering, alternate ports, and an outer channel. Report every exception to the user. Never use an exception for node overlap, label overlap, clipping, missing metadata, or HTML/SVG drift.

## Pre-output checklist

- [ ] Requirements, direction, rank/lane/group meaning are explicit.
- [ ] ASCII plan includes every stable node and edge ID.
- [ ] Text sizing ran before coordinate placement.
- [ ] No fixed-step layout formula ignores actual node size.
- [ ] Routes use assigned ports and inflated obstacles.
- [ ] Shared bus trunk is drawn exactly once.
- [ ] Labels have reserved bboxes and a clear corridor.
- [ ] Title, routes, markers, labels, groups, and legend all contribute to viewBox bounds.
- [ ] Theme tokens and font stack live inside the SVG.
- [ ] Static validation passes for HTML, SVG, and parity.
- [ ] Browser review passes at the required viewports.
- [ ] Both self-contained output files are returned.
