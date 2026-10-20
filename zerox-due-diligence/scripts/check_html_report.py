"""验证主报告的阅读稿、可见正文、图表和底稿链接，避免仅检查隐藏数据。"""
import json
import re
from html.parser import HTMLParser
from pathlib import Path

from common import InputError
from report_html import render
from report_model import validate_content
from visual_review import review_visuals


class ReportParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hidden = None
        self.payloads = []
        self.payload = None
        self.visible = []
        self.ids = []
        self.figures = 0
        self.external_assets = []
        self.svg_signature = []
        self.image_signature = []
        self.in_svg = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.append(attrs["id"])
        if tag in ("script", "style"):
            self.hidden = tag
        if tag == "script" and attrs.get("id") == "report-data":
            self.payload = ""
        if (tag == "script" and attrs.get("src")) or (tag == "link" and attrs.get("rel") == "stylesheet"):
            self.external_assets.append(tag)
        if tag == "img":
            self.image_signature.append(sorted(attrs.items()))
            if not attrs.get("src", "").startswith("data:image/") or "srcset" in attrs:
                self.external_assets.append("img")
        if tag == "figure" and "chart" in attrs.get("class", "").split():
            self.figures += 1
        if tag == "svg":
            self.in_svg = True
        if self.in_svg:
            self.svg_signature.append((tag, sorted(attrs.items())))

    def handle_endtag(self, tag):
        if tag == "script" and self.payload is not None:
            self.payloads.append(self.payload)
            self.payload = None
        if tag == self.hidden:
            self.hidden = None
        if tag == "svg":
            self.in_svg = False
        if tag in ("p", "h1", "h2", "h3", "li", "td", "summary"):
            self.visible.append("\n")

    def handle_data(self, value):
        if self.payload is not None:
            self.payload += value
        if not self.hidden:
            self.visible.append(value)

    @property
    def text(self):
        return "".join(self.visible)


def inspect_html(path, cfg, data, require_current=False, visual_review=None):
    errors, warnings = [], []
    parser = ReportParser()
    document = Path(path).read_text(encoding="utf-8")
    parser.feed(document)
    try:
        if len(parser.payloads) != 1:
            raise InputError("HTML 需包含且只包含一个 report-data 阅读稿")
        payload = json.loads(parser.payloads[0])
        if not isinstance(payload, dict) or set(payload) not in ({"content", "project", "audit_file"}, {"content", "project", "audit_file", "media"}):
            raise InputError("HTML 阅读稿封装格式不符")
        expected_project = {k: cfg[k] for k in ("target_id", "as_of_date", "purpose", "report_status")}
        if payload["project"] != expected_project:
            errors.append("HTML 主体、基准日、目的或报告状态与项目不一致，请重新生成")
        result = validate_content(payload["content"], cfg, data)
        editorial_review = review_visuals(payload["content"])
        if visual_review is not None:
            visual_review.update(editorial_review)
        if payload["content"]["version"] == "1.2":
            warnings.extend(editorial_review["warnings"])
        if payload["content"]["version"] == "1.2" and "media" not in payload:
            raise InputError("1.2 HTML 缺少离线媒体快照")
        if require_current and payload["content"]["version"] != "1.2":
            errors.append("完成态报告必须使用 1.2 公司、财务、营销与竞争契约；旧稿需补齐内容后重新生成")
        warnings.extend(result["warnings"])
        for section in payload["content"]["sections"]:
            for block in section["blocks"]:
                if block["type"] in ("text", "callout"):
                    paragraph = block["text"]
                    if re.search(r"\d", paragraph) and not re.search(r"\[E-\d+\]", paragraph):
                        warnings.append(f"章节“{section['title']}”存在含数字但未引用的段落，需人工判断")
        if parser.figures != result["chart_count"]:
            errors.append("可见图表数量与阅读稿不一致")
        if len(parser.ids) != len(set(parser.ids)):
            errors.append("HTML 锚点 ID 重复")
        for section in payload["content"]["sections"]:
            if section["id"] not in parser.ids:
                errors.append(f"HTML 正文缺少章节：{section['id']}")
        audit = payload["audit_file"]
        if not isinstance(audit, str) or audit != Path(path).stem + "-audit.md":
            raise InputError("底稿需为同目录的 <主报告名>-audit.md")
        if not (Path(path).parent / audit).is_file():
            errors.append("独立核验底稿不存在，请随 HTML 一起交付")
        expected, _ = render(payload["content"], cfg, data, audit, media=payload.get("media", {}))
        reference = ReportParser()
        reference.feed(expected)
        if parser.text.split() != reference.text.split() or parser.svg_signature != reference.svg_signature or parser.image_signature != reference.image_signature:
            errors.append("HTML 可见正文或图形与阅读稿/项目不一致；修改阅读稿后重新生成")
        if parser.external_assets:
            errors.append("主报告依赖外部脚本、样式或图片，不满足离线阅读要求")
    except (InputError, ValueError, TypeError, KeyError) as exc:
        errors.append(f"HTML 阅读稿：{exc}")
    return parser.text, errors, warnings
