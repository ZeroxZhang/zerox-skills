"""装载项目内图片并校验离线媒体包；仅核对文件头与完整性，不解码像素。"""
from __future__ import annotations

import base64
import binascii
import hashlib
import stat
from pathlib import Path, PurePosixPath, PureWindowsPath

from common import fail


MAX_FILE_BYTES = 5 * 1024 * 1024
MAX_TOTAL_BYTES = 15 * 1024 * 1024
_MEDIA_FIELDS = {"mime", "data", "sha256"}


def _relative_path(value):
    """保留内容中的路径键，使用跨平台分隔符检查路径边界。"""
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        fail("图片 path 必须为非空且不含空字符的相对路径")
    normalized = value.replace("\\", "/")
    windows = PureWindowsPath(value)
    if PurePosixPath(normalized).is_absolute() or windows.drive or windows.root:
        fail(f"图片 path 不允许绝对路径：{value!r}")
    if ".." in normalized.split("/"):
        fail(f"图片 path 不允许包含 .. 路径段：{value!r}")
    return PurePosixPath(normalized)


def _image_paths(content):
    """收集所有图片块，重复路径保留第一次出现的位置。"""
    if not isinstance(content, dict):
        fail("图片内容模型必须为对象")
    paths = {}
    pending = [content]
    visited = set()
    while pending:
        node = pending.pop()
        if not isinstance(node, (dict, list)):
            continue
        if id(node) in visited:
            continue
        visited.add(id(node))
        if isinstance(node, dict):
            if node.get("type") == "image":
                path = node.get("path")
                _relative_path(path)
                paths.setdefault(path, None)
            pending.extend(reversed(list(node.values())))
        else:
            pending.extend(reversed(node))
    return list(paths)


def _mime(data, path):
    """识别受支持文件头，不以扩展名推断文件类型或宣称可解码。"""
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    fail(f"图片 {path!r} 的文件头不受支持；仅支持 PNG、JPEG 和 WebP，不支持 SVG")


def _size(size, total, path):
    if size > MAX_FILE_BYTES:
        fail(f"图片 {path!r} 超过单文件 5 MiB 限制")
    if total + size > MAX_TOTAL_BYTES:
        fail("图片总量超过 15 MiB 限制")
    return total + size


def load_media(content, project) -> dict:
    """读取项目内的图片，返回可供渲染器嵌入 data URL 的媒体包。"""
    paths = _image_paths(content)
    if not paths:
        return {}
    try:
        root = Path(project).resolve(strict=True)
        root_stat = root.stat()
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        fail(f"无法读取图片项目目录：{exc}")
    if not stat.S_ISDIR(root_stat.st_mode):
        fail("图片项目路径必须为目录")

    media = {}
    total = 0
    for path in paths:
        relative = _relative_path(path)
        try:
            resolved = root.joinpath(*relative.parts).resolve(strict=True)
        except (OSError, RuntimeError, ValueError) as exc:
            fail(f"无法解析图片 {path!r}：{exc}")
        try:
            resolved.relative_to(root)
        except ValueError:
            fail(f"图片 {path!r} 通过符号链接逃逸项目目录")
        try:
            info = resolved.stat()
        except (OSError, ValueError) as exc:
            fail(f"无法读取图片 {path!r} 的文件信息：{exc}")
        if not stat.S_ISREG(info.st_mode):
            fail(f"图片 {path!r} 必须为普通文件")
        _size(info.st_size, total, path)
        try:
            with resolved.open("rb") as handle:
                # 有界读取也限制检查文件信息后发生的文件增长。
                data = handle.read(MAX_FILE_BYTES + 1)
        except (OSError, ValueError) as exc:
            fail(f"无法读取图片 {path!r}：{exc}")
        total = _size(len(data), total, path)
        media[path] = {
            "mime": _mime(data, path),
            "data": base64.b64encode(data).decode("ascii"),
            "sha256": hashlib.sha256(data).hexdigest(),
        }
    return media


def validate_media(content, media) -> dict:
    """验证快照媒体包与正文路径完全对应，并核对编码、类型、大小与哈希。"""
    paths = _image_paths(content)
    if not isinstance(media, dict):
        fail("媒体包必须为对象；没有图片时应为空对象")
    if set(media) != set(paths):
        fail("媒体包路径必须与正文 image 块路径完全匹配，不得遗漏或多出")
    result = {}
    total = 0
    encoded_limit = 4 * ((MAX_FILE_BYTES + 2) // 3)
    for path in paths:
        item = media[path]
        if not isinstance(item, dict) or set(item) != _MEDIA_FIELDS:
            fail(f"图片 {path!r} 必须包含且仅包含 mime、data、sha256")
        encoded = item["data"]
        if not isinstance(encoded, str):
            fail(f"图片 {path!r} 的 data 必须为 Base64 字符串")
        if len(encoded) > encoded_limit:
            fail(f"图片 {path!r} 的 Base64 数据超过单文件 5 MiB 限制")
        try:
            data = base64.b64decode(encoded, validate=True)
        except (binascii.Error, ValueError) as exc:
            fail(f"图片 {path!r} 的 Base64 数据非法：{exc}")
        # 严格要求标准编码，拒绝额外填充或未清零的填充位。
        if base64.b64encode(data).decode("ascii") != encoded:
            fail(f"图片 {path!r} 的 Base64 数据不是规范编码")
        total = _size(len(data), total, path)
        mime = _mime(data, path)
        if item["mime"] != mime:
            fail(f"图片 {path!r} 的 MIME 与文件头不匹配")
        digest = hashlib.sha256(data).hexdigest()
        if item["sha256"] != digest:
            fail(f"图片 {path!r} 的 sha256 与图片内容不匹配")
        result[path] = {"mime": mime, "data": encoded, "sha256": digest}
    return result
