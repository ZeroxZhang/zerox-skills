#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把一个来源采集进研究包：存原始文件、算哈希、抽正文、写快照、吐一行 JSON 摘要。

只用 Python 标准库即可运行；装了 trafilatura / pypdf / beautifulsoup4 时自动增强。
不做任何绕过：401/402/403/429、付费墙、验证码、超过体积阈值一律报错退出，由 agent 按降级规则改用其他方式。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

DEFAULT_MAX_BYTES = 50 * 1024 * 1024  # 50MB
USER_AGENT = "Mozilla/5.0 (compatible; zerox-deep-research/1.0; +research-archival)"
SNAPSHOT_FIELDS = [
    "id", "title", "url", "final_url", "author_org", "published", "accessed",
    "language", "source_type", "credibility", "conflict_of_interest",
    "capture_method", "completeness", "original_files", "sha256", "research_line",
    "subquestions", "supersedes", "archive_url", "access_note", "rights_note",
]
PAYWALL_MARKERS = (
    "subscribe to continue", "sign in to continue", "create an account to continue",
    "paywall", "subscription required", "members only", "已经订阅", "订阅后继续阅读",
    "付费阅读", "开通会员", "登录后继续", "请登录后阅读全文", "购买后查看",
)
CAPTCHA_MARKERS = (
    "captcha", "are you a robot", "verify you are human", "cloudflare ray id",
    "人机验证", "安全验证", "拖动滑块", "请完成安全验证",
)


# ---------------------------------------------------------------- 命令行

def parse_args(argv=None):
    p = argparse.ArgumentParser(description="采集来源进研究包（原始文件 + 快照 + JSON 摘要）")
    p.add_argument("source", help="URL（http/https）或本地文件路径")
    p.add_argument("--package", required=True, help="研究包根目录")
    p.add_argument("--id", required=True, help="来源 ID，如 M001 / A012 / U001")
    p.add_argument("--slug", required=True, help="文件名短横线小写，≤40 字符")
    p.add_argument("--title", default=None)
    p.add_argument("--author", dest="author_org", default="unknown")
    p.add_argument("--published", default="unknown")
    p.add_argument("--lang", dest="language", default="unknown")
    p.add_argument("--source-type", default="secondary",
                   choices=["primary", "secondary", "tertiary"])
    p.add_argument("--credibility", default="B", choices=["A", "B", "C", "-", "—"])
    p.add_argument("--coi", dest="conflict_of_interest", default="none")
    p.add_argument("--line", dest="research_line", default="M")
    p.add_argument("--subquestions", default="", help="逗号分隔，如 Q1,Q2")
    p.add_argument("--supersedes", default=None)
    p.add_argument("--archive-url", dest="archive_url", default=None)
    p.add_argument("--rights-note", dest="rights_note", default="none")
    p.add_argument("--access-note", dest="access_note", default=None,
                   help="覆盖自动判定的访问说明")
    p.add_argument("--completeness", default=None,
                   choices=["full", "partial", "summary", "snippet-only", "metadata-only"])
    p.add_argument("--capture-method", default="script",
                   choices=["script", "browser", "fetch-tool", "snippet", "metadata-only"])
    p.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    p.add_argument("--max-extract-chars", type=int, default=400_000,
                   help="正文提取上限，超出截断并把完整度降为 partial")
    return p.parse_args(argv)


def fail(code, reason, **extra):
    """以一行 JSON 报错退出。code: 2=访问受限/超限，3=参数错误，4=提取失败。"""
    print(json.dumps({"ok": False, "reason": reason, **extra}, ensure_ascii=False))
    sys.exit(code)


def validate(args):
    if not re.fullmatch(r"[A-Z]\d{3}", args.id):
        fail(3, "bad_id", detail="来源 ID 必须形如 M001 / A012")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,39}", args.slug):
        fail(3, "bad_slug", detail="slug 需小写字母数字连字符，≤40 字符")
    if args.source.startswith(("http://", "https://")):
        return "url"
    path = Path(args.source).expanduser()
    if not path.exists():
        fail(3, "source_not_found", detail=str(path))
    return "path"


# ---------------------------------------------------------------- 取字节

def read_local(path: Path, max_bytes: int):
    size = path.stat().st_size
    if size > max_bytes:
        fail(2, "oversize", size=size, max_bytes=max_bytes)
    ctype, _ = mimetypes.guess_type(str(path))
    return path.read_bytes(), ctype or "application/octet-stream", None, 200, "file:{}".format(path)


def read_url(url: str, max_bytes: int):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            status = getattr(resp, "status", 200)
            ctype = resp.headers.get("Content-Type", "application/octet-stream")
            declared = resp.headers.get("Content-Length")
            if declared and int(declared) > max_bytes:
                fail(2, "oversize", size=int(declared), max_bytes=max_bytes, url=url)
            chunks, total = [], 0
            while True:
                chunk = resp.read(65536)
                if not chunk:
                    break
                total += len(chunk)
                if total > max_bytes:
                    fail(2, "oversize", size=total, max_bytes=max_bytes, url=url)
                chunks.append(chunk)
            return b"".join(chunks), ctype, resp.geturl(), status, None
    except urllib.error.HTTPError as e:
        if e.code in (401, 402, 403, 429):
            fail(2, "access_denied", status=e.code, url=url,
                 access_note="HTTP {}".format(e.code))
        fail(2, "http_error", status=e.code, url=url)
    except Exception as e:  # 网络、DNS、TLS 等
        fail(2, "fetch_error", error="{}: {}".format(type(e).__name__, e), url=url)


def sniff_blockers(text: str):
    low = text.lower()
    for m in PAYWALL_MARKERS:
        if m in low:
            return "paywall", m
    for m in CAPTCHA_MARKERS:
        if m in low:
            return "captcha", m
    return None, None


# ---------------------------------------------------------------- 正文提取

class _TextExtractor(HTMLParser):
    """标准库兜底：保留标题、段落、列表、表格、链接，丢掉脚本与样式。"""

    BLOCK_TAGS = {"p", "div", "section", "article", "br", "hr", "tr", "li", "h1", "h2",
                  "h3", "h4", "h5", "h6", "blockquote", "pre", "table", "ul", "ol"}
    SKIP_TAGS = {"script", "style", "noscript", "svg", "template", "head"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self._skip, self._href = [], 0, None
        self._list_depth, self._in_pre, self._row = 0, False, []

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP_TAGS:
            self._skip += 1
            return
        if self._skip:
            return
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.parts.append("\n" + "#" * int(tag[1]) + " ")
        elif tag == "li":
            self.parts.append("\n" + "  " * self._list_depth + "- ")
        elif tag in {"ul", "ol"}:
            self._list_depth += 1
        elif tag == "br":
            self.parts.append("\n")
        elif tag == "hr":
            self.parts.append("\n---\n")
        elif tag == "tr":
            self._row = []
        elif tag in {"td", "th"}:
            self._row.append("")
        elif tag == "a":
            self._href = dict(attrs).get("href")
        elif tag == "blockquote":
            self.parts.append("\n> ")
        elif tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP_TAGS:
            self._skip = max(0, self._skip - 1)
            return
        if self._skip:
            return
        if tag in {"ul", "ol"}:
            self._list_depth = max(0, self._list_depth - 1)
        elif tag == "tr" and self._row:
            self.parts.append("\n| " + " | ".join(self._row) + " |")
            self._row = []
        elif tag == "a" and self._href:
            self.parts.append(" ({})".format(self._href))
            self._href = None
        elif tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data):
        if self._skip:
            return
        if self._row:
            self._row[-1] = self._row[-1] + data.strip()
        else:
            self.parts.append(data if self._in_pre else re.sub(r"[ \t]+", " ", data))

    def text(self):
        raw = "".join(self.parts)
        raw = re.sub(r"\n{3,}", "\n\n", raw)
        return raw.strip()


def extract_html(data: bytes) -> tuple[str, str]:
    """返回 (正文, 提取器名)。优先第三方，退回标准库。"""
    try:
        import trafilatura  # type: ignore
        html = data.decode("utf-8", errors="replace")
        out = trafilatura.extract(html, include_comments=False, include_tables=True,
                                  output_format="markdown")
        if out and len(out.strip()) > 200:
            return out.strip(), "trafilatura"
    except Exception:
        pass
    try:
        from bs4 import BeautifulSoup  # type: ignore
        html = data.decode("utf-8", errors="replace")
        soup = BeautifulSoup(html, "html.parser")
        for t in soup(["script", "style", "noscript"]):
            t.decompose()
        out = soup.get_text("\n")
        out = re.sub(r"\n{3,}", "\n\n", out).strip()
        if out:
            return out, "beautifulsoup"
    except Exception:
        pass
    parser = _TextExtractor()
    parser.feed(data.decode("utf-8", errors="replace"))
    return parser.text(), "html.parser"


def extract_pdf(data: bytes, stem: Path) -> tuple[str, str]:
    """返回 (带页码标记的正文, 提取器名)。"""
    try:
        from pypdf import PdfReader  # type: ignore
        reader = PdfReader(str(stem))
        pages = []
        for i, page in enumerate(reader.pages, 1):
            pages.append("<!-- p.{} -->\n{}".format(i, (page.extract_text() or "").strip()))
        return "\n\n".join(pages).strip(), "pypdf"
    except Exception:
        pass
    pdftotext = shutil.which("pdftotext")
    if pdftotext:
        try:
            out = subprocess.run([pdftotext, "-layout", str(stem), "-"],
                                 capture_output=True, timeout=120)
            if out.returncode == 0:
                pages = out.stdout.decode("utf-8", errors="replace").split("\f")
                marked = ["<!-- p.{} -->\n{}".format(i, p.strip())
                          for i, p in enumerate(pages, 1) if p.strip()]
                return "\n\n".join(marked).strip(), "pdftotext"
        except Exception:
            pass
    return "", "none"


def extract_text(data: bytes, ctype: str, raw_path: Path):
    """按内容类型抽正文。返回 (正文, 提取器, 自动判定的 access_note 或 None)。"""
    mime = ctype.split(";")[0].strip().lower()
    if mime in ("text/html", "application/xhtml+xml") or data[:200].lstrip().lower().startswith(
            (b"<!doctype html", b"<html", b"<head", b"<body")):
        kind, note = sniff_blockers(data.decode("utf-8", errors="replace")[:20000])
        if kind:
            return "", "none", "{}: {}".format(kind, note)
        text, how = extract_html(data)
        return text, how, None
    if mime == "application/pdf" or raw_path.suffix.lower() == ".pdf":
        text, how = extract_pdf(data, raw_path)
        return text, how, None
    if mime.startswith("text/") or mime in ("application/json", "application/xml",
                                           "text/csv", "application/csv"):
        try:
            charset = "utf-8"
            if "charset=" in ctype.lower():
                charset = ctype.lower().split("charset=")[-1].split(";")[0].strip() or "utf-8"
            return data.decode(charset, errors="replace"), "decode:{}".format(charset), None
        except Exception:
            return data.decode("utf-8", errors="replace"), "decode:utf-8", None
    # 二进制：不硬转文字
    return "", "none", "binary:{}".format(mime)


# ---------------------------------------------------------------- 快照写入

def yaml_scalar(v):
    if v is None:
        return "null"
    if isinstance(v, (list, tuple)):
        return "[" + ", ".join(yaml_scalar(x) for x in v) + "]"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    # JSON 字符串也是合法 YAML 标量；统一转义以便检查器可靠解析。
    return json.dumps(str(v), ensure_ascii=False)


def write_snapshot(path: Path, meta: dict, body: str):
    lines = ["---"]
    for key in SNAPSHOT_FIELDS:
        lines.append("{}: {}".format(key, yaml_scalar(meta.get(key))))
    lines.append("---")
    lines.append("")
    lines.append("# {}".format(meta.get("title") or meta["id"]))
    lines.append("")
    lines.append(body if body else "（无法提取正文，见 raw/files/ 下的原始文件）")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv=None):
    args = parse_args(argv)
    kind = validate(args)

    pkg = Path(args.package).expanduser().resolve()
    if (pkg / "manifest-sha256.txt").exists():
        fail(3, "package_already_sealed", detail="已封包目录不可继续采集；请创建新版本工作目录")
    src_dir = pkg / "raw" / "sources"
    files_dir = pkg / "raw" / ("user-provided" if args.id.startswith("U") else "files")
    # 一个 ID 永远对应同一份采集。重新采集须新 ID + supersedes，不能覆盖旧字节。
    existing = [p for p in (pkg / "raw").rglob(args.id + "-*") if p.is_file()]
    if existing:
        fail(3, "id_already_exists", detail="来源 ID 已使用；请分配新 ID，旧版保留")
    src_dir.mkdir(parents=True, exist_ok=True)
    files_dir.mkdir(parents=True, exist_ok=True)

    if kind == "url":
        data, ctype, final_url, status, _ = read_url(args.source, args.max_bytes)
    else:
        p = Path(args.source).expanduser().resolve()
        data, ctype, final_url, status, _ = read_local(p, args.max_bytes)

    # 嗅探受限内容（只看前 20KB，避免大文件全量解码）
    if ctype.split(";")[0].strip().lower() not in ("application/pdf",):
        head = data[:20000]
        if b"<" in head[:200] or b"html" in head[:200].lower():
            block_kind, marker = sniff_blockers(head.decode("utf-8", errors="replace"))
            if block_kind:
                fail(2, "access_blocked", block_kind=block_kind, marker=marker,
                     access_note="{}: {}".format(block_kind, marker))

    ext = Path(urllib.parse.urlparse(final_url or args.source).path).suffix
    if not ext or len(ext) > 8:
        guessed = mimetypes.guess_extension(ctype.split(";")[0].strip().lower())
        ext = guessed or ".bin"
    raw_name = "{}-{}{}".format(args.id, args.slug, ext)
    raw_path = files_dir / raw_name
    with raw_path.open("xb") as out:
        out.write(data)
    digest = hashlib.sha256(data).hexdigest()

    body, extractor, auto_note = extract_text(data, ctype, raw_path)
    if args.completeness:
        completeness = args.completeness
    elif not body.strip():
        completeness = "metadata-only"
    elif len(body) > args.max_extract_chars:
        completeness = "partial"
        body = body[:args.max_extract_chars] + "\n\n[... 截断：正文超过 {} 字符 ...]".format(
            args.max_extract_chars)
    elif extractor == "none":
        completeness = "metadata-only"
    else:
        completeness = "full"

    accessed = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    meta = {
        "id": args.id,
        "title": args.title or args.slug,
        "url": args.source if kind == "url" else "file:{}".format(args.source),
        "final_url": final_url or (args.source if kind == "url" else "file:{}".format(args.source)),
        "author_org": args.author_org,
        "published": args.published,
        "accessed": accessed,
        "language": args.language,
        "source_type": args.source_type,
        "credibility": args.credibility,
        "conflict_of_interest": args.conflict_of_interest,
        "capture_method": args.capture_method,
        "completeness": completeness,
        "original_files": [raw_path.relative_to(pkg).as_posix()],
        "sha256": digest,
        "research_line": args.research_line,
        "subquestions": [s.strip() for s in args.subquestions.split(",") if s.strip()],
        "supersedes": args.supersedes,
        "archive_url": args.archive_url,
        "access_note": args.access_note or auto_note or "正常",
        "rights_note": args.rights_note,
    }
    snap_name = "{}-{}.md".format(args.id, args.slug)
    write_snapshot(src_dir / snap_name, meta, body)

    print(json.dumps({
        "ok": True,
        "id": args.id,
        "snapshot": "raw/sources/" + snap_name,
        "original": raw_path.relative_to(pkg).as_posix(),
        "sha256": digest,
        "bytes": len(data),
        "status": status,
        "content_type": ctype,
        "final_url": meta["final_url"],
        "extractor": extractor,
        "completeness": completeness,
        "body_chars": len(body),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
