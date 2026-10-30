"""本地图片边界与媒体包回归测试；文件头夹具为合成数据，不是真实图片。"""
import base64
import copy
import hashlib
import sys
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(os.environ.get("ZEROX_DD_ROOT", Path(__file__).resolve().parents[3] / "zerox-due-diligence"))
sys.path.insert(0, str(ROOT / "scripts"))

from common import InputError  # noqa: E402
from report_media import load_media, validate_media  # noqa: E402


# 此处仅测试文件头识别与包完整性，不声称这些字节能够解码为像素。
SYNTHETIC_HEADERS = {
    "image/png": b"\x89PNG\r\n\x1a\n",
    "image/jpeg": b"\xff\xd8\xff\xe0",
    "image/webp": b"RIFF\x04\x00\x00\x00WEBP",
}


def content(*paths):
    return {"sections": [{"blocks": [{"type": "image", "path": path} for path in paths]}]}


def packed(data, mime="image/png"):
    return {
        "mime": mime,
        "data": base64.b64encode(data).decode("ascii"),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


class ReportMediaTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="zerox-media-test-")
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name)
        self.project = self.workspace / "synthetic-project"
        self.project.mkdir()

    def write(self, path="images/example.png", data=None):
        target = self.project / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(SYNTHETIC_HEADERS["image/png"] if data is None else data)
        return target

    def test_supported_magic_roundtrips_without_trusting_extension(self):
        paths = []
        for index, (mime, data) in enumerate(SYNTHETIC_HEADERS.items()):
            path = f"images/type-{index}.untrusted-extension"
            paths.append(path)
            self.write(path, data)
        report = content(*paths)
        media = load_media(report, self.project)
        for path, (mime, data) in zip(paths, SYNTHETIC_HEADERS.items()):
            self.assertEqual(media[path], packed(data, mime))
        self.assertEqual(validate_media(report, media), media)

    def test_extension_cannot_disguise_unsupported_content(self):
        self.write(data=b"<svg xmlns='http://www.w3.org/2000/svg'></svg>")
        with self.assertRaisesRegex(InputError, "不支持 SVG"):
            load_media(content("images/example.png"), self.project)

    def test_unsupported_and_incomplete_headers_are_rejected(self):
        for data in (b"", b"GIF89a", b"\x89PNG", b"\xff\xd8", b"RIFF\x04\x00\x00\x00WAVE",
                     b"RIFF\x04\x00\x00\x00WEB", b"<svg/>"):
            with self.subTest(data=data):
                self.write(data=data)
                with self.assertRaises(InputError):
                    load_media(content("images/example.png"), self.project)
                with self.assertRaises(InputError):
                    validate_media(content("images/example.png"), {"images/example.png": packed(data)})

    def test_absolute_traversal_and_invalid_paths_are_rejected(self):
        for path in ("/etc/hosts", "../outside.png", "images/../example.png",
                     "images/../../outside.png", r"C:\images\example.png",
                     "C:/images/example.png", r"\\server\share\image.png",
                     r"..\outside.png", r"images\..\example.png", "", " ", None, 12, "x\x00.png"):
            with self.subTest(path=path):
                with self.assertRaises(InputError):
                    load_media(content(path), self.project)
                with self.assertRaises(InputError):
                    validate_media(content(path), {})

    def test_dotdot_in_filename_is_not_a_parent_segment(self):
        self.write("images/example..png")
        self.assertIn("images/example..png", load_media(content("images/example..png"), self.project))

    def test_symlink_file_escape_is_rejected(self):
        outside = self.workspace / "outside.png"
        outside.write_bytes(SYNTHETIC_HEADERS["image/png"])
        (self.project / "escape.png").symlink_to(outside)
        with self.assertRaisesRegex(InputError, "逃逸"):
            load_media(content("escape.png"), self.project)

    def test_symlink_directory_escape_is_rejected(self):
        outside = self.workspace / "outside"
        outside.mkdir()
        (outside / "example.png").write_bytes(SYNTHETIC_HEADERS["image/png"])
        (self.project / "images").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(InputError, "逃逸"):
            load_media(content("images/example.png"), self.project)

    def test_symlink_inside_project_is_allowed(self):
        target = self.write()
        (self.project / "alias.png").symlink_to(target)
        self.assertEqual(load_media(content("alias.png"), self.project)["alias.png"],
                         packed(SYNTHETIC_HEADERS["image/png"]))

    def test_missing_file_broken_and_looping_symlinks_become_input_errors(self):
        (self.project / "broken.png").symlink_to(self.project / "missing.png")
        (self.project / "loop.png").symlink_to(self.project / "loop.png")
        for path in ("missing.png", "broken.png", "loop.png"):
            with self.subTest(path=path), self.assertRaises(InputError):
                load_media(content(path), self.project)

    def test_non_file_and_invalid_project_become_input_errors(self):
        (self.project / "directory.png").mkdir()
        with self.assertRaisesRegex(InputError, "普通文件"):
            load_media(content("directory.png"), self.project)
        target = self.write()
        for project in (self.workspace / "missing", target, None, "bad\x00root"):
            with self.subTest(project=project), self.assertRaises(InputError):
                load_media(content("images/example.png"), project)

    def test_read_error_becomes_input_error(self):
        self.write()
        with patch.object(Path, "open", side_effect=PermissionError("合成权限错误")):
            with self.assertRaisesRegex(InputError, "无法读取图片"):
                load_media(content("images/example.png"), self.project)

    def test_duplicate_paths_are_loaded_and_counted_once(self):
        self.write()
        report = content("images/example.png", "images/example.png", "images/example.png")
        with patch("report_media.MAX_TOTAL_BYTES", 8):
            media = load_media(report, self.project)
            self.assertEqual(len(media), 1)
            self.assertEqual(validate_media(report, media), media)

    def test_all_image_blocks_are_collected(self):
        self.write("images/first.png")
        self.write("images/second.png")
        report = content("images/first.png")
        report["sections"].append({"blocks": [{"type": "text", "text": "合成正文"},
                                              {"type": "image", "path": "images/second.png"}]})
        self.assertEqual(set(load_media(report, self.project)),
                         {"images/first.png", "images/second.png"})

    def test_no_images_requires_empty_media(self):
        report = {"sections": [{"blocks": [{"type": "text", "text": "合成正文"}]}]}
        self.assertEqual(load_media(report, self.workspace / "does-not-need-to-exist"), {})
        self.assertEqual(validate_media(report, {}), {})
        for media in (None, [], {"unexpected.png": packed(SYNTHETIC_HEADERS["image/png"])}):
            with self.subTest(media=media), self.assertRaises(InputError):
                validate_media(report, media)

    def test_invalid_content_becomes_input_error(self):
        for report in (None, [], "invalid"):
            with self.subTest(report=report):
                with self.assertRaises(InputError):
                    load_media(report, self.project)
                with self.assertRaises(InputError):
                    validate_media(report, {})

    def test_missing_or_extra_media_paths_are_rejected(self):
        report = content("images/example.png")
        item = packed(SYNTHETIC_HEADERS["image/png"])
        for media in ({}, {"other.png": item}, {"images/example.png": item, "extra.png": item}):
            with self.subTest(media=media), self.assertRaisesRegex(InputError, "完全匹配"):
                validate_media(report, media)

    def test_invalid_media_record_fields_are_rejected(self):
        item = packed(SYNTHETIC_HEADERS["image/png"])
        for record in (None, [], {}, {**item, "extra": "field"}, {"data": item["data"]}):
            with self.subTest(record=record), self.assertRaises(InputError):
                validate_media(content("image.png"), {"image.png": record})

    def test_base64_must_decode_strictly_and_canonically(self):
        item = packed(SYNTHETIC_HEADERS["image/png"])
        invalid = [None, 1, "%%%bad%%%", item["data"] + "\n", item["data"][:-1],
                   item["data"] + "=", "非ASCII", item["data"][:-2] + "p="]
        for data in invalid:
            with self.subTest(data=data), self.assertRaisesRegex(InputError, "Base64"):
                validate_media(content("image.png"), {"image.png": {**item, "data": data}})

    def test_mime_must_match_magic_and_hash_must_match_bytes(self):
        item = packed(SYNTHETIC_HEADERS["image/png"])
        for field, values, message in (
                ("mime", ("image/jpeg", "image/svg+xml", None, []), "MIME"),
                ("sha256", ("0" * 64, item["sha256"].upper(), None, []), "sha256")):
            for value in values:
                with self.subTest(field=field, value=value), self.assertRaisesRegex(InputError, message):
                    validate_media(content("image.png"), {"image.png": {**item, field: value}})

    def test_changed_bytes_with_original_hash_are_rejected(self):
        original = packed(SYNTHETIC_HEADERS["image/png"])
        changed = copy.deepcopy(original)
        changed["data"] = base64.b64encode(SYNTHETIC_HEADERS["image/png"] + b"changed").decode("ascii")
        with self.assertRaisesRegex(InputError, "sha256"):
            validate_media(content("image.png"), {"image.png": changed})

    def test_file_size_boundary_and_overflow(self):
        # 使用缩小的同一边界检验等于上限、超限及实际解码字节数。
        with patch("report_media.MAX_FILE_BYTES", 12):
            allowed = SYNTHETIC_HEADERS["image/png"] + b"1234"
            self.write(data=allowed)
            report = content("images/example.png")
            media = load_media(report, self.project)
            self.assertEqual(validate_media(report, media), media)
            oversized = allowed + b"x"
            self.write(data=oversized)
            with self.assertRaisesRegex(InputError, "单文件"):
                load_media(report, self.project)
            with self.assertRaisesRegex(InputError, "单文件"):
                validate_media(report, {"images/example.png": packed(oversized)})

    def test_decoded_size_is_checked_even_when_base64_length_fits(self):
        # 8字节与9字节的Base64长度相同，编码长度预检不能替代解码大小检查。
        data = SYNTHETIC_HEADERS["image/png"] + b"x"
        with patch("report_media.MAX_FILE_BYTES", 8):
            with self.assertRaisesRegex(InputError, "单文件"):
                validate_media(content("image.png"), {"image.png": packed(data)})

    def test_total_size_boundary_and_overflow(self):
        paths = ("images/one.png", "images/two.png", "images/three.png")
        for path in paths:
            self.write(path)
        with patch("report_media.MAX_TOTAL_BYTES", 16):
            allowed = content(*paths[:2])
            media = load_media(allowed, self.project)
            self.assertEqual(validate_media(allowed, media), media)
            with self.assertRaisesRegex(InputError, "总量"):
                load_media(content(*paths), self.project)
            media[paths[2]] = packed(SYNTHETIC_HEADERS["image/png"])
            with self.assertRaisesRegex(InputError, "总量"):
                validate_media(content(*paths), media)


if __name__ == "__main__":
    unittest.main()
