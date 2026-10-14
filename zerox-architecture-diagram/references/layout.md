# Deterministic Layout and Routing

Use this reference for every generated diagram. It separates graph semantics from geometry so that changes to one node do not require hand-moving unrelated arrows.

## Contents

1. [Terminology](#terminology)
2. [Constants](#constants)
3. [Layout record](#layout-record)
4. [Sizing pass](#sizing-pass)
5. [Rank and ordering pass](#rank-and-ordering-pass)
6. [Lane and group pass](#lane-and-group-pass)
7. [Coordinate pass](#coordinate-pass)
8. [Port assignment](#port-assignment)
9. [Orthogonal routing](#orthogonal-routing)
10. [Bus routing](#bus-routing)
11. [Label placement](#label-placement)
12. [Legend and viewBox](#legend-and-viewbox)
13. [Cycles and compound diagrams](#cycles-and-compound-diagrams)

## Terminology

- **Rank**: graph depth along the primary flow direction.
- **Lane**: an ordered visual band such as a team, tier, trust zone, or deployment domain.
- **Group**: a containing boundary such as Region, AZ, VPC, cluster, or security group.
- **Port**: a named point on one side of a node used by an edge.
- **Route channel**: free horizontal or vertical space reserved for edges.
- **Bus**: one source port and one shared trunk feeding multiple branches.

Never use “layer” in the layout record; it is ambiguous between rank, lane, group, and SVG z-order.

## Constants

Use these defaults unless the diagram density or mode requires more space:

```text
baseGrid          = 10
majorGrid         = 20
nodePaddingX      = 16
nodePaddingY      = 12
nodeMinWidth      = 120
nodeMaxWidth      = 220
nodeMinHeight     = 60
nodeGap           = 40
rankGap           = 60
presentationGap   = 60
laneLabelGutter   = 100
laneTopGutter     = 40
lanePadding       = 20
groupTitleGutter  = 30
groupPadding      = 20
routeClearance    = 20
parallelEdgeGap   = 8
portGap           = 20
targetGap         = 2
labelGap          = 4
outerPadding      = 40
```

`snap10(v) = ceil(v / 10) * 10`; `snap20(v) = ceil(v / 20) * 20`.

- Node x/y/width/height use the 10px base grid. This permits 120px and 140px nodes to align by their centers.
- Rank origins, lane/group boundaries, and viewBox width/height use the 20px major grid.
- Ports and label anchors may be off-grid because they derive from measured geometry.

## Layout record

Before SVG generation, maintain one record per object. The record may live in working notes, but its IDs and geometry must be copied into SVG `data-*` attributes.

```text
Node   = {id, label, sublabel, type, icon, rank, order, lane, group, x, y, w, h}
Edge   = {id, source, target, kind, label, sourceSide, targetSide, busId, points}
Lane   = {id, label, order, x, y, w, h, contentRect}
Group  = {id, label, parent, x, y, w, h, padding}
Legend = {x, y, w, h, rows, columns}
```

IDs are ASCII kebab-case and unique within their object type. Edge IDs should read as `source-target-purpose` when multiple edges connect the same nodes.

## Sizing pass

Size nodes before assigning coordinates.

### Text estimate

For the configured font size:

```text
estimatedWidth =
  cjkCount   * fontSize
  + asciiCount * fontSize * 0.62
  + spaceCount * fontSize * 0.33
```

Use the larger of the label and sublabel estimates. Add 24px for a side icon or 0px for an icon above the label, then add horizontal padding on both sides.

```text
rawWidth = max(labelWidth + iconSpace, sublabelWidth) + 2 * nodePaddingX
nodeWidth = snap10(clamp(rawWidth, nodeMinWidth, nodeMaxWidth))
```

If text exceeds `nodeMaxWidth`:

1. Wrap at a semantic delimiter or word boundary.
2. Increase height by 20px per additional line.
3. Keep at most two visible label lines and preserve the full text in the component `<title>`.
4. Never shrink primary labels below 11px in standard mode or 10px in presentation mode.

Set `nodeHeight = snap10(max(nodeMinHeight, contentHeight + 2 * nodePaddingY))`.

## Rank and ordering pass

### Rank assignment

1. Build the directed graph from the normalized edge set.
2. Collapse each strongly connected component (SCC) into a temporary super-node.
3. Assign the condensed DAG by longest-path rank from external/user sources.
4. Expand SCC members within the same rank and mark their cycle/return edges for an outer channel.
5. Respect explicit rank overrides only when they do not create a backward primary-flow edge.

Message buses, brokers, and gateways occupy their own rank when they are first-class components.

### Crossing reduction

Initial order is the user’s semantic order. Then run four sweeps:

1. Left-to-right or top-to-bottom: sort each rank by the median position of predecessors.
2. Reverse direction: sort by the median position of successors.
3. Repeat both sweeps once.
4. Keep stable ordering for ties.

Prefer fewer crossings over shorter individual edges. Keep related replicas or shard nodes adjacent.

## Lane and group pass

### Lanes

For horizontal lanes, reserve a left label gutter:

```text
contentRect.x = lane.x + laneLabelGutter
contentRect.y = lane.y + laneTopGutter
contentRect.w = lane.w - laneLabelGutter - lanePadding
contentRect.h = lane.h - laneTopGutter - lanePadding
```

All nodes assigned to the lane must fit inside `contentRect`. Lane height is content height plus the gutters; minimum lane height is 120px.

When access/application/data are the primary flow tiers, use `TB`: the tier is both the semantic rank and the horizontal lane. Do not also apply an unrelated left-to-right “layer” formula.

### Nested groups

Layout groups inside-out:

1. Layout nodes inside the deepest group.
2. Union their node, label, and internal-route bounds.
3. Inflate by group padding and add the title gutter.
4. Snap the group boundary to the major grid.
5. Treat the completed group as a compound node when packing its parent.

Use transparent or very subtle group fills so nested boundaries do not repaint lane colors.

## Coordinate pass

Never use fixed `rank * 180` or `index * 80` formulas.

### LR flow

```text
rankWidth[r] = max(node.w for node in rank r)
rankX[0] = snap20(contentLeft)
rankX[r+1] = snap20(rankX[r] + rankWidth[r] + rankGap)
```

Within each rank:

```text
nextY = previousY + previousHeight + nodeGap
```

Center a shorter rank within the available lane content height only after calculating its true total height.

### TB flow

Use the symmetric calculation:

```text
rankHeight[r] = max(node.h for node in rank r)
rankY[0] = snap20(contentTop)
rankY[r+1] = snap20(rankY[r] + rankHeight[r] + rankGap)
nextX = previousX + previousWidth + nodeGap
```

When rank and lane boundaries coincide, compute lane height from that rank’s tallest node plus gutters. When a lane contains several ranks, allocate route channels between them.

### Gap check

For every pair of nodes:

- If their y projections overlap, horizontal gap must be at least `nodeGap`.
- If their x projections overlap, vertical gap must be at least `nodeGap`.
- Diagonal nodes whose projections do not overlap do not require both gaps.

## Port assignment

Choose sides from flow direction and relative geometry:

- LR primary edge: source right, target left.
- TB primary edge: source bottom, target top.
- Back edge: use the nearest side that feeds an outer return channel.
- Cross-lane edge: prefer the side facing the destination lane.

The default port is side center. Mixed node widths do not need artificial x/y shifts: use an off-center target port when a straight approach is clearer.

For several unrelated edges on one side, distribute ports symmetrically with at least `portGap`. For a semantic bus, use exactly one shared source port. For high fan-in, distribute target ports or introduce a merge bus; do not stack unrelated arrowheads.

## Orthogonal routing

Use one Manhattan routing process for straight, L, U, and return routes.

1. Inflate every unrelated node rectangle by `routeClearance`.
2. Create a source stub that leaves the source in its port normal direction.
3. Create a target stub that approaches the target in its port normal direction and ends `targetGap` before the boundary.
4. Build candidate channels from obstacle sides, lane corridors, group gateways, and midpoints between adjacent obstacles.
5. Find a collision-free orthogonal path between the stubs.
6. Remove zero-length and collinear intermediate points.

Score candidate paths with:

```text
cost = length
     + 40 * bendCount
     + 200 * edgeCrossingCount
     + 500 * obstacleIntersectionCount
     + 20 * routeProximityPenalty
```

An obstacle intersection makes the route invalid; the large cost is useful while exploring candidates. Prefer a longer clean route over a short route that crosses nodes or several edges.

Output absolute `M/L` commands only:

```svg
<path d="M 560 270 L 580 270 L 580 430 L 638 430" .../>
```

The final segment must point toward the target. Account for marker geometry when choosing the 2px endpoint gap; use `markerUnits="userSpaceOnUse"` and a marker whose tip coincides with `refX`.

## Bus routing

A bus has one source, one source port, one trunk, one junction, and two or more branches.

```text
source port -> source stub -> neutral trunk -> junction
                                           -> branch A -> target A
                                           -> branch B -> target B
```

SVG contract:

```svg
<path data-role="bus-trunk" data-bus-id="api-data"
      data-source="api" data-points="560,270 580,270"
      d="M 560 270 L 580 270"/>
<path data-role="edge-route" data-edge-id="api-db" data-bus-id="api-data"
      data-source="api" data-target="db"
      data-points="580,270 580,430 638,430"
      d="M 580 270 L 580 430 L 638 430"/>
```

Draw the trunk once without an arrowhead. Every branch starts at the same junction and ends at its own target. If branches use different colors or dash patterns, keep the trunk neutral.

## Label placement

Place labels after routing but reserve their geometry before finalizing the viewBox.

1. Prefer the midpoint of the longest non-trunk segment.
2. For horizontal segments, place the label 8px above; for vertical segments, 10px to the right.
3. Estimate the text bbox with the sizing formula and record it in `data-bbox`.
4. Reject a position that comes within `labelGap` of a node, group title, lane title, or another label.
5. Try the opposite side, then the next-longest segment, then a small callout with a leader.

Render edge labels after components so masks cannot clip them, but still treat any label-node intersection as a validation failure.

## Legend and viewBox

Build the legend from the set of component types actually used. Calculate item widths from their labels, wrap rows to the available width, and center the content within its container.

Standard mode:

```text
legend.x = (viewBoxWidth - legend.w) / 2
legend.y >= max(nodeBottom, groupBottom, laneBottom, routeBottom, labelBottom) + 20
```

Presentation mode places the legend at bottom-right with 20px margins.

Compute a single union over visible geometry:

```text
contentBBox = union(
  title, subtitle, lanes, groups, nodes,
  routes including marker extents, labels, legend
)
viewBox = snap20(inflate(contentBBox, outerPadding))
```

Shift geometry so the resulting viewBox origin is `0 0`. Standard mode is at least 1000×680. Presentation mode is exactly 1280×720; if content does not fit at readable sizes, re-layout, simplify secondary labels, or split the diagram instead of scaling text below the minimum.

## Cycles and compound diagrams

- Route cycle and return edges through dedicated outer channels beyond the affected SCC bounds.
- Route self-loops on the least occupied side with a three-segment external loop.
- Route cross-group edges through explicit boundary gateways; do not cross a group title.
- Pack multiple Regions/AZs using their computed compound bounds plus 40px between peer groups.
- Place cross-region labels and latency annotations in the inter-group corridor.
- Re-run crossing reduction and routing after any group resize.
