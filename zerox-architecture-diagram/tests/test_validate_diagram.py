from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from scripts.extract_svg import extract_svg_text
from scripts.validate_diagram import DiagramValidator


ROOT = Path(__file__).resolve().parents[1]
STANDARD_TEMPLATE = ROOT / "assets" / "template.html"
PRESENTATION_TEMPLATE = ROOT / "assets" / "template-presentation.html"


class TemplateContractTests(unittest.TestCase):
    def issue_codes(self, path: Path) -> set[str]:
        return {issue.code for issue in DiagramValidator(path).validate()}

    def test_standard_template_passes(self) -> None:
        self.assertEqual([], DiagramValidator(STANDARD_TEMPLATE).validate())

    def test_presentation_template_passes(self) -> None:
        self.assertEqual([], DiagramValidator(PRESENTATION_TEMPLATE).validate())

    def test_extraction_preserves_svg_dom(self) -> None:
        html = STANDARD_TEMPLATE.read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as directory:
            svg_path = Path(directory) / "diagram.svg"
            svg_path.write_text(extract_svg_text(html), encoding="utf-8")
            validator = DiagramValidator(STANDARD_TEMPLATE)
            validator.validate()
            validator.compare(svg_path)
            self.assertNotIn("HTML_SVG_PARITY", {issue.code for issue in validator.issues})

    def test_off_grid_component_is_rejected(self) -> None:
        html = STANDARD_TEMPLATE.read_text(encoding="utf-8").replace(
            'data-bbox="700,520,140,60"',
            'data-bbox="705,520,140,60"',
            1,
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "off-grid.html"
            path.write_text(html, encoding="utf-8")
            self.assertIn("NODE_GRID", self.issue_codes(path))

    def test_component_overlap_is_rejected(self) -> None:
        html = STANDARD_TEMPLATE.read_text(encoding="utf-8").replace(
            'data-bbox="700,520,140,60"',
            'data-bbox="700,460,140,60"',
            1,
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "overlap.html"
            path.write_text(html, encoding="utf-8")
            self.assertIn("NODE_OVERLAP", self.issue_codes(path))

    def test_wrong_target_gap_is_rejected(self) -> None:
        html = STANDARD_TEMPLATE.read_text(encoding="utf-8").replace(
            'data-points="240,150 298,150" d="M 240 150 L 298 150"',
            'data-points="240,150 299,150" d="M 240 150 L 299 150"',
            1,
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad-gap.html"
            path.write_text(html, encoding="utf-8")
            self.assertIn("EDGE_TARGET_GAP", self.issue_codes(path))

    def test_legend_without_clearance_is_rejected(self) -> None:
        html = STANDARD_TEMPLATE.read_text(encoding="utf-8").replace(
            'data-bbox="250,660,500,80"',
            'data-bbox="250,620,500,80"',
            1,
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "legend-gap.html"
            path.write_text(html, encoding="utf-8")
            self.assertIn("LEGEND_GAP", self.issue_codes(path))

    def test_parity_drift_is_rejected(self) -> None:
        html = STANDARD_TEMPLATE.read_text(encoding="utf-8")
        svg = extract_svg_text(html).replace("TCP :443", "TCP :8443", 1)
        with tempfile.TemporaryDirectory() as directory:
            svg_path = Path(directory) / "drift.svg"
            svg_path.write_text(svg, encoding="utf-8")
            validator = DiagramValidator(STANDARD_TEMPLATE)
            validator.validate()
            validator.compare(svg_path)
            self.assertIn("HTML_SVG_PARITY", {issue.code for issue in validator.issues})

    def test_remote_font_dependency_is_rejected(self) -> None:
        html = STANDARD_TEMPLATE.read_text(encoding="utf-8").replace(
            "<style>",
            '<link rel="stylesheet" href="https://fonts.example.test/font.css">\n  <style>',
            1,
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "remote-font.html"
            path.write_text(html, encoding="utf-8")
            self.assertIn("EXTERNAL_RESOURCE", self.issue_codes(path))

    def test_any_declared_bbox_outside_viewbox_is_rejected(self) -> None:
        html = STANDARD_TEMPLATE.read_text(encoding="utf-8").replace(
            'data-role="diagram-title" data-bbox="360,16,280,26"',
            'data-role="diagram-title" data-bbox="360,-16,280,26"',
            1,
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "title-clipping.html"
            path.write_text(html, encoding="utf-8")
            self.assertIn("DECLARED_BBOX_VIEWBOX", self.issue_codes(path))

    def test_stroke_scaled_marker_is_rejected(self) -> None:
        html = STANDARD_TEMPLATE.read_text(encoding="utf-8").replace(
            'markerUnits="userSpaceOnUse"',
            'markerUnits="strokeWidth"',
            1,
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "scaled-marker.html"
            path.write_text(html, encoding="utf-8")
            self.assertIn("MARKER_UNITS", self.issue_codes(path))


if __name__ == "__main__":
    unittest.main()
