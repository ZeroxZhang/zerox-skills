#!/usr/bin/env python3
"""验证 zerox-architecture-diagram 语义 SVG 的静态布局契约。"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import sys
from typing import Optional, Sequence
import xml.etree.ElementTree as ET


SVG_RE = re.compile(r"<svg\b[\s\S]*?</svg>", re.IGNORECASE)
NUMBER = r"-?(?:\d+(?:\.\d*)?|\.\d+)"
PATH_POINT_RE = re.compile(rf"([ML])\s*({NUMBER})[\s,]+({NUMBER})")
MARKER_RE = re.compile(r"url\(#([^\)]+)\)")
EPS = 0.01


class InputError(Exception):
    """输入或契约无法解析。"""


@dataclass(frozen=True)
class Box:
    x: float
    y: float
    w: float
    h: float

    @property
    def right(self) -> float:
        return self.x + self.w

    @property
    def bottom(self) -> float:
        return self.y + self.h

    def inflated(self, amount: float) -> "Box":
        return Box(self.x - amount, self.y - amount, self.w + amount * 2, self.h + amount * 2)


@dataclass
class Issue:
    level: str
    code: str
    message: str


@dataclass
class SemanticObject:
    element: ET.Element
    identifier: str
    box: Box


@dataclass
class Route:
    element: ET.Element
    identifier: str
    source: str
    target: Optional[str]
    bus_id: Optional[str]
    points: list[tuple[float, float]]
    role: str


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def almost_equal(a: float, b: float, tolerance: float = EPS) -> bool:
    return abs(a - b) <= tolerance


def on_grid(value: float, grid: float) -> bool:
    return almost_equal(value / grid, round(value / grid))


def parse_numbers(value: str, count: int, field: str) -> list[float]:
    parts = [part for part in re.split(r"[\s,]+", value.strip()) if part]
    if len(parts) != count:
        raise InputError(f"{field} 需要 {count} 个数字，实际为 {len(parts)} 个")
    try:
        return [float(part) for part in parts]
    except ValueError as exc:
        raise InputError(f"{field} 包含非数字内容: {value}") from exc


def parse_box(element: ET.Element, field: str = "data-bbox") -> Box:
    value = element.get(field)
    if not value:
        raise InputError(f"{local_name(element.tag)} 缺少 {field}")
    x, y, w, h = parse_numbers(value, 4, field)
    if w <= 0 or h <= 0:
        raise InputError(f"{field} 的宽高必须为正数: {value}")
    return Box(x, y, w, h)


def parse_data_points(element: ET.Element) -> list[tuple[float, float]]:
    value = element.get("data-points")
    if not value:
        raise InputError(f"{element.get('data-edge-id') or element.get('data-bus-id')} 缺少 data-points")
    points: list[tuple[float, float]] = []
    for pair in value.strip().split():
        nums = parse_numbers(pair, 2, "data-points")
        points.append((nums[0], nums[1]))
    if len(points) < 2:
        raise InputError("data-points 至少需要两个点")
    return points


def parse_visible_points(element: ET.Element) -> list[tuple[float, float]]:
    tag = local_name(element.tag)
    if tag == "line":
        return [
            (float(element.get("x1", "nan")), float(element.get("y1", "nan"))),
            (float(element.get("x2", "nan")), float(element.get("y2", "nan"))),
        ]
    if tag == "polyline":
        raw = element.get("points", "")
        return [(float(x), float(y)) for x, y in re.findall(rf"({NUMBER})[\s,]+({NUMBER})", raw)]
    if tag != "path":
        raise InputError(f"业务路由不支持 <{tag}>")

    d = element.get("d", "")
    commands = re.findall(r"[A-Za-z]", d)
    if not commands or any(command not in {"M", "L"} for command in commands):
        raise InputError("业务 path 只允许绝对 M/L 命令")
    points = [(float(x), float(y)) for _, x, y in PATH_POINT_RE.findall(d)]
    if len(points) != len(commands):
        raise InputError(f"无法完整解析 path: {d}")
    return points


def boxes_intersect(a: Box, b: Box) -> bool:
    return a.x < b.right - EPS and b.x < a.right - EPS and a.y < b.bottom - EPS and b.y < a.bottom - EPS


def box_contains(outer: Box, inner: Box, tolerance: float = EPS) -> bool:
    return (
        inner.x >= outer.x - tolerance
        and inner.y >= outer.y - tolerance
        and inner.right <= outer.right + tolerance
        and inner.bottom <= outer.bottom + tolerance
    )


def point_in_box(point: tuple[float, float], box: Box) -> bool:
    x, y = point
    return box.x - EPS <= x <= box.right + EPS and box.y - EPS <= y <= box.bottom + EPS


def point_on_boundary(point: tuple[float, float], box: Box, side: Optional[str]) -> bool:
    x, y = point
    checks = {
        "left": almost_equal(x, box.x) and box.y - EPS <= y <= box.bottom + EPS,
        "right": almost_equal(x, box.right) and box.y - EPS <= y <= box.bottom + EPS,
        "top": almost_equal(y, box.y) and box.x - EPS <= x <= box.right + EPS,
        "bottom": almost_equal(y, box.bottom) and box.x - EPS <= x <= box.right + EPS,
    }
    if side:
        return checks.get(side, False)
    return any(checks.values())


def leaves_source(start: tuple[float, float], next_point: tuple[float, float], side: Optional[str]) -> bool:
    if not side:
        return True
    sx, sy = start
    nx, ny = next_point
    return {
        "left": nx < sx - EPS and almost_equal(ny, sy),
        "right": nx > sx + EPS and almost_equal(ny, sy),
        "top": ny < sy - EPS and almost_equal(nx, sx),
        "bottom": ny > sy + EPS and almost_equal(nx, sx),
    }.get(side, False)


def target_gap_ok(
    previous: tuple[float, float],
    end: tuple[float, float],
    box: Box,
    side: Optional[str],
    gap: float = 2,
) -> bool:
    px, py = previous
    ex, ey = end
    checks = {
        "left": almost_equal(box.x - ex, gap) and box.y - EPS <= ey <= box.bottom + EPS and ex > px + EPS and almost_equal(ey, py),
        "right": almost_equal(ex - box.right, gap) and box.y - EPS <= ey <= box.bottom + EPS and ex < px - EPS and almost_equal(ey, py),
        "top": almost_equal(box.y - ey, gap) and box.x - EPS <= ex <= box.right + EPS and ey > py + EPS and almost_equal(ex, px),
        "bottom": almost_equal(ey - box.bottom, gap) and box.x - EPS <= ex <= box.right + EPS and ey < py - EPS and almost_equal(ex, px),
    }
    if side:
        return checks.get(side, False)
    return any(checks.values())


def segment_intersects_box_interior(
    start: tuple[float, float], end: tuple[float, float], box: Box
) -> bool:
    x1, y1 = start
    x2, y2 = end
    if almost_equal(y1, y2):
        low, high = sorted((x1, x2))
        return box.y + EPS < y1 < box.bottom - EPS and low < box.right - EPS and high > box.x + EPS
    if almost_equal(x1, x2):
        low, high = sorted((y1, y2))
        return box.x + EPS < x1 < box.right - EPS and low < box.bottom - EPS and high > box.y + EPS
    return True


def segment_relation(
    first: tuple[tuple[float, float], tuple[float, float]],
    second: tuple[tuple[float, float], tuple[float, float]],
) -> tuple[str, float, Optional[tuple[float, float]]]:
    (a1, a2), (b1, b2) = first, second
    ax1, ay1 = a1
    ax2, ay2 = a2
    bx1, by1 = b1
    bx2, by2 = b2
    a_horizontal = almost_equal(ay1, ay2)
    b_horizontal = almost_equal(by1, by2)

    if a_horizontal and b_horizontal and almost_equal(ay1, by1):
        overlap = min(max(ax1, ax2), max(bx1, bx2)) - max(min(ax1, ax2), min(bx1, bx2))
        return ("overlap", max(0.0, overlap), None)
    if not a_horizontal and not b_horizontal and almost_equal(ax1, bx1):
        overlap = min(max(ay1, ay2), max(by1, by2)) - max(min(ay1, ay2), min(by1, by2))
        return ("overlap", max(0.0, overlap), None)

    horizontal = first if a_horizontal else second
    vertical = second if a_horizontal else first
    (h1, h2), (v1, v2) = horizontal, vertical
    ix, iy = v1[0], h1[1]
    if (
        min(h1[0], h2[0]) - EPS <= ix <= max(h1[0], h2[0]) + EPS
        and min(v1[1], v2[1]) - EPS <= iy <= max(v1[1], v2[1]) + EPS
    ):
        return ("cross", 0.0, (ix, iy))
    return ("none", 0.0, None)


def canonical_xml(element: ET.Element) -> tuple:
    text = " ".join((element.text or "").split())
    attributes = tuple(sorted(element.attrib.items()))
    return (local_name(element.tag), attributes, text, tuple(canonical_xml(child) for child in list(element)))


class DiagramValidator:
    def __init__(self, path: Path):
        self.path = path
        try:
            self.original_text = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise InputError(f"无法读取 {path}: {exc}") from exc
        self.is_html = path.suffix.lower() in {".html", ".htm"} or "<html" in self.original_text[:500].lower()
        self.svg_text = self._extract_svg(self.original_text)
        try:
            self.root = ET.fromstring(self.svg_text)
        except ET.ParseError as exc:
            raise InputError(f"SVG XML 解析失败: {exc}") from exc
        self.elements = list(self.root.iter())
        self.order = {id(element): index for index, element in enumerate(self.elements)}
        self.issues: list[Issue] = []
        self.view_box = Box(0, 0, 0, 0)
        self.components: dict[str, SemanticObject] = {}
        self.lanes: dict[str, SemanticObject] = {}
        self.boundaries: dict[str, SemanticObject] = {}
        self.routes: list[Route] = []
        self.labels: list[SemanticObject] = []

    def _extract_svg(self, text: str) -> str:
        if self.is_html:
            match = SVG_RE.search(text)
            if not match:
                raise InputError("HTML 中没有找到内联 SVG")
            return match.group(0)
        return text.strip()

    def error(self, code: str, message: str) -> None:
        self.issues.append(Issue("error", code, message))

    def warning(self, code: str, message: str) -> None:
        self.issues.append(Issue("warning", code, message))

    def elements_with_role(self, role: str) -> list[ET.Element]:
        return [element for element in self.elements if element.get("data-role") == role]

    def validate(self) -> list[Issue]:
        self._validate_root()
        self._validate_self_containment()
        self._collect_objects()
        self._validate_metadata()
        self._validate_declared_bboxes()
        self._validate_components()
        self._validate_containment()
        self._validate_routes()
        self._validate_edge_relations()
        self._validate_labels()
        self._validate_legend()
        self._validate_z_order()
        self._validate_markers()
        return self.issues

    def _validate_declared_bboxes(self) -> None:
        """检查所有声明几何，而不只检查当前参与碰撞计算的语义角色。"""
        for element in self.elements:
            if not element.get("data-bbox"):
                continue
            role = element.get("data-role") or local_name(element.tag)
            identifier = element.get("data-id") or element.get("data-edge-id") or role
            try:
                box = parse_box(element)
            except InputError as exc:
                self.error("DECLARED_BBOX", f"{role} {identifier}: {exc}")
                continue
            if not box_contains(self.view_box, box):
                self.error("DECLARED_BBOX_VIEWBOX", f"{role} {identifier} 的 data-bbox 超出 viewBox")

    def _validate_root(self) -> None:
        if self.root.tag != "{http://www.w3.org/2000/svg}svg":
            self.error("SVG_NAMESPACE", "SVG 根元素缺少标准 xmlns")
        required = {
            "data-diagram-version",
            "data-mode",
            "data-theme",
            "data-direction",
            "data-base-grid",
            "data-major-grid",
            "role",
            "aria-labelledby",
            "width",
            "height",
        }
        for attribute in sorted(required):
            if not self.root.get(attribute):
                self.error("ROOT_ATTRIBUTE", f"SVG 根元素缺少 {attribute}")
        if self.root.get("role") != "img":
            self.error("ACCESSIBILITY", "SVG role 必须为 img")

        try:
            min_x, min_y, width, height = parse_numbers(self.root.get("viewBox", ""), 4, "viewBox")
            self.view_box = Box(min_x, min_y, width, height)
            if not almost_equal(min_x, 0) or not almost_equal(min_y, 0):
                self.error("VIEWBOX_ORIGIN", "viewBox 原点必须为 0 0")
            major = float(self.root.get("data-major-grid", "20"))
            if not on_grid(width, major) or not on_grid(height, major):
                self.error("VIEWBOX_GRID", f"viewBox 宽高必须对齐 {major:g}px 主网格")
            mode = self.root.get("data-mode")
            if mode == "presentation" and (not almost_equal(width, 1280) or not almost_equal(height, 720)):
                self.error("VIEWBOX_PRESENTATION", "演示模式 viewBox 必须为 1280×720")
            if mode == "standard" and (width < 1000 or height < 680):
                self.error("VIEWBOX_MINIMUM", "标准模式 viewBox 不得小于 1000×680")
            if mode not in {"standard", "presentation"}:
                self.error("MODE", "data-mode 必须为 standard 或 presentation")
            try:
                intrinsic_width = float(self.root.get("width", "nan"))
                intrinsic_height = float(self.root.get("height", "nan"))
                if not almost_equal(intrinsic_width, width) or not almost_equal(intrinsic_height, height):
                    self.error("SVG_INTRINSIC_SIZE", "SVG 固有 width/height 必须与 viewBox 宽高一致")
            except ValueError:
                self.error("SVG_INTRINSIC_SIZE", "SVG 固有 width/height 必须是数字")
        except (InputError, ValueError) as exc:
            self.error("VIEWBOX", str(exc))

        ids = [element.get("id") for element in self.elements if element.get("id")]
        duplicates = sorted(identifier for identifier, count in Counter(ids).items() if count > 1)
        for identifier in duplicates:
            self.error("DUPLICATE_XML_ID", f"XML id 重复: {identifier}")

        id_set = set(ids)
        labelled_by = self.root.get("aria-labelledby", "").split()
        if len(labelled_by) < 2 or any(identifier not in id_set for identifier in labelled_by):
            self.error("ACCESSIBILITY", "aria-labelledby 必须引用 SVG 内的 title 与 desc")
        if not any(local_name(element.tag) == "title" for element in list(self.root)):
            self.error("ACCESSIBILITY", "SVG 根缺少 title")
        if not any(local_name(element.tag) == "desc" for element in list(self.root)):
            self.error("ACCESSIBILITY", "SVG 根缺少 desc")
        if not any(local_name(element.tag) == "style" for element in self.elements):
            self.error("SELF_CONTAINED_STYLE", "SVG 内缺少本地 style")
        if self.root.get("data-theme") not in {"light", "dark"}:
            self.error("THEME", "data-theme 必须为 light 或 dark")
        if self.root.get("data-direction") not in {"LR", "TB"}:
            self.error("DIRECTION", "data-direction 必须为 LR 或 TB")

    def _validate_self_containment(self) -> None:
        if self.is_html and re.search(r"<script\b", self.original_text, re.IGNORECASE):
            self.error("HTML_RUNTIME_SCRIPT", "HTML 产物不得包含运行时 JavaScript")

        resource_pattern = re.compile(
            r"<(?:link|script|img|image|use)\b[^>]*(?:href|src)\s*=\s*['\"]([^'\"]+)['\"]",
            re.IGNORECASE,
        )
        for match in resource_pattern.finditer(self.original_text):
            value = match.group(1).strip()
            if value.startswith(("http://", "https://", "//")):
                self.error("EXTERNAL_RESOURCE", f"产物引用外部资源: {value}")
        if re.search(r"@import\s+(?:url\()?\s*['\"]?(?:https?:)?//", self.original_text, re.IGNORECASE):
            self.error("EXTERNAL_RESOURCE", "CSS 使用远程 @import")
        if re.search(r"url\(\s*['\"]?(?:https?:)?//", self.original_text, re.IGNORECASE):
            self.error("EXTERNAL_RESOURCE", "CSS 使用远程 url() 资源")

    def _collect_semantic_boxes(self, role: str, id_attribute: str = "data-id") -> dict[str, SemanticObject]:
        result: dict[str, SemanticObject] = {}
        for element in self.elements_with_role(role):
            identifier = element.get(id_attribute)
            if not identifier:
                self.error("SEMANTIC_ID", f"{role} 缺少 {id_attribute}")
                continue
            if identifier in result:
                self.error("SEMANTIC_ID", f"{role} data-id 重复: {identifier}")
                continue
            try:
                result[identifier] = SemanticObject(element, identifier, parse_box(element))
            except InputError as exc:
                self.error("BBOX", f"{role} {identifier}: {exc}")
        return result

    def _collect_objects(self) -> None:
        self.components = self._collect_semantic_boxes("component")
        self.lanes = self._collect_semantic_boxes("lane")
        self.boundaries = self._collect_semantic_boxes("boundary")
        self.labels = list(self._collect_semantic_boxes("edge-label", "data-edge-id").values())

        route_elements = self.elements_with_role("bus-trunk") + self.elements_with_role("edge-route")
        seen_edges: set[str] = set()
        seen_buses: set[str] = set()
        for element in route_elements:
            role = element.get("data-role", "")
            identifier = element.get("data-edge-id") if role == "edge-route" else element.get("data-bus-id")
            source = element.get("data-source", "")
            target = element.get("data-target")
            bus_id = element.get("data-bus-id")
            if not identifier or not source or (role == "edge-route" and not target):
                self.error("ROUTE_METADATA", f"{role} 缺少稳定 ID/source/target")
                continue
            registry = seen_edges if role == "edge-route" else seen_buses
            if identifier in registry:
                self.error("ROUTE_METADATA", f"{role} ID 重复: {identifier}")
                continue
            registry.add(identifier)
            try:
                points = parse_data_points(element)
                visible = parse_visible_points(element)
                if len(points) != len(visible) or any(
                    not almost_equal(px, vx) or not almost_equal(py, vy)
                    for (px, py), (vx, vy) in zip(points, visible)
                ):
                    self.error("ROUTE_POINTS", f"{identifier} 的 data-points 与可见路径不一致")
                self.routes.append(Route(element, identifier, source, target, bus_id, points, role))
            except (InputError, ValueError) as exc:
                self.error("ROUTE_PARSE", f"{identifier}: {exc}")

    def _validate_metadata(self) -> None:
        metadata = next((element for element in self.elements if local_name(element.tag) == "metadata" and element.get("id") == "diagram-model"), None)
        if metadata is None:
            self.error("MODEL_METADATA", "缺少 metadata#diagram-model")
            return
        try:
            model = json.loads("".join(metadata.itertext()))
        except (json.JSONDecodeError, TypeError) as exc:
            self.error("MODEL_METADATA", f"diagram-model 不是合法 JSON: {exc}")
            return

        model_nodes = {item.get("id") for item in model.get("nodes", []) if isinstance(item, dict)}
        model_edges = {item.get("id") for item in model.get("edges", []) if isinstance(item, dict)}
        if model_nodes != set(self.components):
            self.error("MODEL_NODE_PARITY", f"模型节点与 SVG 组件不一致: model={sorted(model_nodes)} svg={sorted(self.components)}")
        svg_edges = {route.identifier for route in self.routes if route.role == "edge-route"}
        if model_edges != svg_edges:
            self.error("MODEL_EDGE_PARITY", f"模型边与 SVG 路由不一致: model={sorted(model_edges)} svg={sorted(svg_edges)}")

        rendered_nodes = self.components
        for item in model.get("nodes", []):
            if not isinstance(item, dict) or item.get("id") not in rendered_nodes:
                continue
            component = rendered_nodes[item["id"]].element
            for model_field, svg_attribute in (
                ("type", "data-type"),
                ("lane", "data-lane"),
                ("group", "data-group"),
            ):
                if item.get(model_field) != component.get(svg_attribute):
                    self.error("MODEL_NODE_FIELDS", f"{item['id']} 的 {model_field} 与 SVG 不一致")

        rendered = {route.identifier: route for route in self.routes if route.role == "edge-route"}
        for item in model.get("edges", []):
            if not isinstance(item, dict) or item.get("id") not in rendered:
                continue
            route = rendered[item["id"]]
            if item.get("source") != route.source or item.get("target") != route.target:
                self.error("MODEL_EDGE_ENDPOINTS", f"{route.identifier} 的模型 source/target 与 SVG 不一致")
            if item.get("kind") != route.element.get("data-kind") or item.get("bus") != route.bus_id:
                self.error("MODEL_EDGE_FIELDS", f"{route.identifier} 的 kind/bus 与 SVG 不一致")

    def _validate_components(self) -> None:
        try:
            base_grid = float(self.root.get("data-base-grid", "10"))
        except ValueError:
            base_grid = 10
            self.error("GRID", "data-base-grid 不是数字")

        objects = list(self.components.values())
        for component in objects:
            box = component.box
            if any(not on_grid(value, base_grid) for value in (box.x, box.y, box.w, box.h)):
                self.error("NODE_GRID", f"组件 {component.identifier} 未对齐 {base_grid:g}px 基础网格")
            if not box_contains(self.view_box, box):
                self.error("NODE_VIEWBOX", f"组件 {component.identifier} 超出 viewBox")

            boxes = [child for child in component.element.iter() if child.get("data-role") == "box"]
            masks = [child for child in component.element.iter() if child.get("data-role") == "mask"]
            if len(boxes) != 1 or len(masks) != 1:
                self.error("COMPONENT_SHAPE", f"组件 {component.identifier} 必须各有一个 box 与 mask")
            for child in boxes + masks:
                try:
                    child_box = Box(
                        float(child.get("x", "nan")),
                        float(child.get("y", "nan")),
                        float(child.get("width", "nan")),
                        float(child.get("height", "nan")),
                    )
                    if child_box != box:
                        self.error("COMPONENT_BBOX", f"组件 {component.identifier} 的 data-bbox 与 rect 不一致")
                except ValueError:
                    self.error("COMPONENT_BBOX", f"组件 {component.identifier} 的 rect 几何无效")
            children = list(component.element)
            if not children or local_name(children[0].tag) != "title":
                self.error("COMPONENT_TOOLTIP", f"组件 {component.identifier} 的首个子元素必须是 title")

        for index, first in enumerate(objects):
            for second in objects[index + 1 :]:
                if boxes_intersect(first.box, second.box):
                    self.error("NODE_OVERLAP", f"组件 {first.identifier} 与 {second.identifier} 重叠")
                    continue
                y_overlap = min(first.box.bottom, second.box.bottom) - max(first.box.y, second.box.y)
                x_overlap = min(first.box.right, second.box.right) - max(first.box.x, second.box.x)
                if y_overlap > EPS:
                    gap = max(second.box.x - first.box.right, first.box.x - second.box.right)
                    if gap < 40 - EPS:
                        self.error("NODE_GAP", f"组件 {first.identifier} 与 {second.identifier} 的水平间距小于 40px")
                if x_overlap > EPS:
                    gap = max(second.box.y - first.box.bottom, first.box.y - second.box.bottom)
                    if gap < 40 - EPS:
                        self.error("NODE_GAP", f"组件 {first.identifier} 与 {second.identifier} 的垂直间距小于 40px")

    def _validate_containment(self) -> None:
        try:
            major_grid = float(self.root.get("data-major-grid", "20"))
        except ValueError:
            major_grid = 20
        for collection_name, collection in (("泳道", self.lanes), ("边界", self.boundaries)):
            for semantic in collection.values():
                if any(not on_grid(value, major_grid) for value in (semantic.box.x, semantic.box.y, semantic.box.w, semantic.box.h)):
                    self.error("MAJOR_GRID", f"{collection_name} {semantic.identifier} 未对齐 {major_grid:g}px 主网格")
                if not box_contains(self.view_box, semantic.box):
                    self.error("SEMANTIC_VIEWBOX", f"{collection_name} {semantic.identifier} 超出 viewBox")

        for component in self.components.values():
            lane_id = component.element.get("data-lane")
            if lane_id:
                lane = self.lanes.get(lane_id)
                if not lane:
                    self.error("LANE_REFERENCE", f"组件 {component.identifier} 引用了不存在的泳道 {lane_id}")
                else:
                    content_value = lane.element.get("data-content-bbox")
                    content_box = lane.box
                    if content_value:
                        try:
                            x, y, w, h = parse_numbers(content_value, 4, "data-content-bbox")
                            content_box = Box(x, y, w, h)
                            if not box_contains(lane.box, content_box):
                                self.error("LANE_CONTENT", f"泳道 {lane.identifier} 的内容区超出泳道边界")
                            if any(not on_grid(value, major_grid) for value in (x, y, w, h)):
                                self.error("LANE_CONTENT", f"泳道 {lane.identifier} 的内容区未对齐主网格")
                        except InputError as exc:
                            self.error("LANE_CONTENT", f"泳道 {lane.identifier}: {exc}")
                    if not box_contains(content_box, component.box):
                        self.error("LANE_CONTAINMENT", f"组件 {component.identifier} 超出泳道 {lane_id} 内容区")
            group_id = component.element.get("data-group")
            if group_id:
                group = self.boundaries.get(group_id)
                if not group:
                    self.error("GROUP_REFERENCE", f"组件 {component.identifier} 引用了不存在的边界 {group_id}")
                elif not box_contains(group.box, component.box):
                    self.error("GROUP_CONTAINMENT", f"组件 {component.identifier} 超出边界 {group_id}")

        for boundary in self.boundaries.values():
            parent_id = boundary.element.get("data-parent")
            if not parent_id:
                continue
            parent = self.boundaries.get(parent_id)
            if not parent:
                self.error("GROUP_REFERENCE", f"边界 {boundary.identifier} 引用了不存在的父边界 {parent_id}")
            elif not box_contains(parent.box, boundary.box):
                self.error("GROUP_CONTAINMENT", f"边界 {boundary.identifier} 超出父边界 {parent_id}")

    def _validate_routes(self) -> None:
        buses = {route.bus_id: route for route in self.routes if route.role == "bus-trunk"}
        for route in self.routes:
            if route.source not in self.components:
                self.error("EDGE_SOURCE", f"{route.identifier} 引用了不存在的源组件 {route.source}")
                continue
            if route.target and route.target not in self.components:
                self.error("EDGE_TARGET", f"{route.identifier} 引用了不存在的目标组件 {route.target}")
                continue

            for first, second in zip(route.points, route.points[1:]):
                if first == second:
                    self.error("EDGE_ZERO_SEGMENT", f"{route.identifier} 包含零长度线段")
                if not (almost_equal(first[0], second[0]) or almost_equal(first[1], second[1])):
                    self.error("EDGE_ORTHOGONAL", f"{route.identifier} 包含非正交线段")
            if any(not point_in_box(point, self.view_box) for point in route.points):
                self.error("EDGE_VIEWBOX", f"{route.identifier} 超出 viewBox")

            source = self.components[route.source].box
            if route.role == "bus-trunk":
                side = route.element.get("data-source-side")
                if not point_on_boundary(route.points[0], source, side) or not leaves_source(route.points[0], route.points[1], side):
                    self.error("BUS_SOURCE_PORT", f"总线 {route.identifier} 未从正确源端口向外离开")
            else:
                if route.bus_id:
                    trunk = buses.get(route.bus_id)
                    if not trunk:
                        self.error("BUS_TRUNK", f"边 {route.identifier} 缺少总线干线 {route.bus_id}")
                    elif route.points[0] != trunk.points[-1]:
                        self.error("BUS_JUNCTION", f"边 {route.identifier} 未从总线 {route.bus_id} 的末端分支")
                    elif trunk.source != route.source:
                        self.error("BUS_SOURCE", f"边 {route.identifier} 与总线 {route.bus_id} 的源组件不一致")
                else:
                    side = route.element.get("data-source-side")
                    if not point_on_boundary(route.points[0], source, side) or not leaves_source(route.points[0], route.points[1], side):
                        self.error("EDGE_SOURCE_PORT", f"边 {route.identifier} 未从正确源端口向外离开")

                target = self.components[route.target or ""].box
                if not target_gap_ok(route.points[-2], route.points[-1], target, route.element.get("data-target-side")):
                    self.error("EDGE_TARGET_GAP", f"边 {route.identifier} 未以 2px 间距从正确方向接近目标")

            for segment_index, (first, second) in enumerate(zip(route.points, route.points[1:])):
                for node_id, component in self.components.items():
                    if node_id == route.source and segment_index == 0 and (route.role == "bus-trunk" or not route.bus_id):
                        continue
                    if node_id == route.target and segment_index == len(route.points) - 2:
                        continue
                    if segment_intersects_box_interior(first, second, component.box.inflated(20)):
                        self.error("EDGE_CLEARANCE", f"边 {route.identifier} 与组件 {node_id} 的 20px 净空冲突")

    def _validate_edge_relations(self) -> None:
        segments: list[tuple[Route, tuple[tuple[float, float], tuple[float, float]]]] = []
        for route in self.routes:
            segments.extend((route, segment) for segment in zip(route.points, route.points[1:]))
        reported: set[tuple[str, str, str]] = set()
        for index, (first_route, first_segment) in enumerate(segments):
            for second_route, second_segment in segments[index + 1 :]:
                if first_route is second_route:
                    continue
                relation, length, point = segment_relation(first_segment, second_segment)
                pair = tuple(sorted((first_route.identifier, second_route.identifier)))
                if relation == "overlap" and length > 10 + EPS:
                    if first_route.bus_id and first_route.bus_id == second_route.bus_id:
                        self.warning("EDGE_BUS_OVERLAP", f"同一总线的 {pair[0]} 与 {pair[1]} 仍重复绘制 {length:g}px")
                    elif (pair[0], pair[1], relation) not in reported:
                        self.error("EDGE_OVERLAP", f"边 {pair[0]} 与 {pair[1]} 共线重叠 {length:g}px")
                        reported.add((pair[0], pair[1], relation))
                elif relation == "cross" and point is not None:
                    endpoints = {first_segment[0], first_segment[1]} & {second_segment[0], second_segment[1]}
                    same_bus = first_route.bus_id and first_route.bus_id == second_route.bus_id
                    if point in endpoints or same_bus:
                        continue
                    allowed = any(route.element.get("data-allow-crossing") == "true" for route in (first_route, second_route))
                    reason = any(route.element.get("data-exception-reason") for route in (first_route, second_route))
                    if allowed and reason:
                        self.warning("EDGE_CROSSING_ALLOWED", f"边 {pair[0]} 与 {pair[1]} 在 {point} 有声明交叉")
                    elif (pair[0], pair[1], relation) not in reported:
                        self.warning("EDGE_CROSSING", f"边 {pair[0]} 与 {pair[1]} 在 {point} 交叉")
                        reported.add((pair[0], pair[1], relation))

    def _validate_labels(self) -> None:
        edge_ids = {route.identifier for route in self.routes if route.role == "edge-route"}
        for label in self.labels:
            edge_id = label.element.get("data-edge-id")
            if edge_id not in edge_ids:
                self.error("LABEL_EDGE", f"标签 {label.identifier} 引用了不存在的边 {edge_id}")
            if not box_contains(self.view_box, label.box):
                self.error("LABEL_VIEWBOX", f"标签 {label.identifier} 超出 viewBox")
            padded = label.box.inflated(4)
            for component in self.components.values():
                if boxes_intersect(padded, component.box):
                    self.error("LABEL_NODE_OVERLAP", f"标签 {label.identifier} 与组件 {component.identifier} 冲突")
        for index, first in enumerate(self.labels):
            for second in self.labels[index + 1 :]:
                if boxes_intersect(first.box.inflated(4), second.box.inflated(4)):
                    self.error("LABEL_OVERLAP", f"标签 {first.identifier} 与 {second.identifier} 冲突")

    def _validate_legend(self) -> None:
        legends = self.elements_with_role("legend")
        if len(legends) != 1:
            self.error("LEGEND", f"必须且只能有一个 legend，实际为 {len(legends)}")
            return
        try:
            legend = parse_box(legends[0])
        except InputError as exc:
            self.error("LEGEND", str(exc))
            return
        if not box_contains(self.view_box, legend):
            self.error("LEGEND_VIEWBOX", "图例超出 viewBox")
        mode = self.root.get("data-mode")
        if mode == "standard" and not almost_equal(legend.x + legend.w / 2, self.view_box.w / 2, 1):
            self.error("LEGEND_CENTER", "标准模式图例没有水平居中")
        if mode == "presentation":
            if not almost_equal(self.view_box.w - legend.right, 20, 1) or not almost_equal(self.view_box.h - legend.bottom, 20, 1):
                self.error("LEGEND_PRESENTATION", "演示模式图例必须距右侧和底部各 20px")

        for semantic in list(self.components.values()) + list(self.boundaries.values()) + list(self.lanes.values()):
            if boxes_intersect(legend, semantic.box):
                self.error("LEGEND_OVERLAP", f"图例与 {semantic.identifier} 重叠")
        for label in self.labels:
            if boxes_intersect(legend, label.box.inflated(4)):
                self.error("LEGEND_LABEL_OVERLAP", f"图例与边标签 {label.identifier} 冲突")
        for route in self.routes:
            if any(
                segment_intersects_box_interior(first, second, legend)
                for first, second in zip(route.points, route.points[1:])
            ):
                self.error("LEGEND_ROUTE_OVERLAP", f"图例与路由 {route.identifier} 冲突")

        if mode == "standard":
            content = list(self.components.values()) + list(self.boundaries.values()) + list(self.lanes.values())
            bottoms = [item.box.bottom for item in content]
            bottoms.extend(label.box.bottom for label in self.labels)
            bottoms.extend(point[1] for route in self.routes for point in route.points)
            if bottoms:
                lowest = max(bottoms)
                if legend.y < lowest + 20 - EPS:
                    self.error("LEGEND_GAP", "标准模式图例与节点、边界、路由或标签的间距小于 20px")

        used_types = {component.element.get("data-type") for component in self.components.values()}
        legend_types = {element.get("data-type") for element in self.elements_with_role("legend-item")}
        missing = sorted(item for item in used_types - legend_types if item)
        if missing:
            self.error("LEGEND_TYPES", f"图例缺少组件类型: {', '.join(missing)}")

    def _validate_z_order(self) -> None:
        routes = self.elements_with_role("edge-route") + self.elements_with_role("bus-trunk")
        components = self.elements_with_role("component")
        labels = self.elements_with_role("edge-label")
        legends = self.elements_with_role("legend")
        if routes and components and max(self.order[id(item)] for item in routes) >= min(self.order[id(item)] for item in components):
            self.error("Z_ORDER", "所有 edge route / bus trunk 必须位于 component 之前")
        if components and labels and max(self.order[id(item)] for item in components) >= min(self.order[id(item)] for item in labels):
            self.error("Z_ORDER", "所有 edge label 必须位于 component 之后")
        if labels and legends and max(self.order[id(item)] for item in labels) >= min(self.order[id(item)] for item in legends):
            self.error("Z_ORDER", "legend 必须位于 edge label 之后")
        boundaries = self.elements_with_role("boundary")
        lanes = self.elements_with_role("lane")
        if boundaries and lanes and max(self.order[id(item)] for item in boundaries) >= min(self.order[id(item)] for item in lanes):
            self.error("Z_ORDER", "boundary 必须位于 lane 之前")

    def _validate_markers(self) -> None:
        ids = {element.get("id") for element in self.elements if element.get("id")}
        markers = {
            element.get("id"): element
            for element in self.elements
            if local_name(element.tag) == "marker" and element.get("id")
        }
        used_markers: set[str] = set()
        for element in self.elements:
            for attribute in ("marker-start", "marker-mid", "marker-end"):
                value = element.get(attribute)
                if not value:
                    continue
                match = MARKER_RE.fullmatch(value.strip())
                if not match or match.group(1) not in ids:
                    self.error("MARKER_REFERENCE", f"无效的 {attribute}: {value}")
                elif match.group(1) in markers:
                    used_markers.add(match.group(1))
        for marker_id in sorted(used_markers):
            marker = markers[marker_id]
            if marker.get("markerUnits") != "userSpaceOnUse":
                self.error("MARKER_UNITS", f"marker {marker_id} 必须使用 userSpaceOnUse，才能保持目标间距稳定")

    def compare(self, other_path: Path) -> None:
        other = DiagramValidator(other_path)
        if canonical_xml(self.root) != canonical_xml(other.root):
            self.error("HTML_SVG_PARITY", f"{self.path.name} 与 {other_path.name} 的 SVG DOM 不一致")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="验证架构图语义 SVG 与静态布局")
    parser.add_argument("input", type=Path, help="HTML 或 SVG 文件")
    parser.add_argument("--compare", type=Path, help="与另一个 HTML/SVG 的内联 SVG 做一致性比较")
    parser.add_argument("--strict", action="store_true", help="将 warning 视为失败")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出报告")
    return parser


def render_report(path: Path, issues: Sequence[Issue], as_json: bool) -> None:
    errors = sum(issue.level == "error" for issue in issues)
    warnings = sum(issue.level == "warning" for issue in issues)
    if as_json:
        print(json.dumps({"file": str(path), "errors": errors, "warnings": warnings, "issues": [asdict(issue) for issue in issues]}, ensure_ascii=False, indent=2))
        return
    if not issues:
        print(f"PASS {path} — 静态布局契约全部通过")
        return
    for issue in issues:
        print(f"{issue.level.upper()} [{issue.code}] {issue.message}")
    print(f"SUMMARY {path} — {errors} error(s), {warnings} warning(s)")


def main() -> int:
    args = build_parser().parse_args()
    try:
        validator = DiagramValidator(args.input)
        issues = validator.validate()
        if args.compare:
            validator.compare(args.compare)
            issues = validator.issues
    except InputError as exc:
        if args.json:
            print(json.dumps({"file": str(args.input), "execution_error": str(exc)}, ensure_ascii=False, indent=2))
        else:
            print(f"VALIDATOR ERROR: {exc}", file=sys.stderr)
        return 2

    render_report(args.input, issues, args.json)
    has_errors = any(issue.level == "error" for issue in issues)
    has_warnings = any(issue.level == "warning" for issue in issues)
    return 1 if has_errors or (args.strict and has_warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
