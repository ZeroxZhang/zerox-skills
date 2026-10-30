"""检验公开安装命令的结果、失败清理和独立示例重建。"""
import contextlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(os.environ.get("zerox_dd_root", Path(__file__).resolve().parents[3] / "zerox-due-diligence"))


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="zerox-package-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.snippets = re.findall(r"python3 - <<'PY'\n(.*?)\nPY", (ROOT / "README.md").read_text(), re.S)
        self.assertEqual(len(self.snippets), 2)

    def install(self, source, test_home, snippet):
        previous = Path.cwd()
        try:
            os.chdir(source)
            with patch("pathlib.Path.home", return_value=test_home), contextlib.redirect_stdout(io.StringIO()):
                exec(compile(snippet, "README-install", "exec"), {})
        finally:
            os.chdir(previous)
        return test_home / ".codex/skills/zerox-due-diligence"

    def run_cli(self, root, script, *args):
        result = subprocess.run([sys.executable, str(root / "scripts" / script), *map(str, args)],
                                capture_output=True, text=True,
                                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout[-2000:])
        return json.loads(result.stdout)

    def test_both_language_install_commands_ship_only_runtime_and_examples(self):
        for index, snippet in enumerate(self.snippets):
            with self.subTest(language=index):
                installed = self.install(ROOT, self.base / str(index), snippet)
                self.assertTrue((installed / "examples/README.md").is_file())
                self.assertTrue((installed / "scripts/triangulate.py").is_file())
                for unwanted in ("tests", "development", "context.md", ".screenshots"):
                    self.assertFalse((installed / unwanted).exists())
                self.assertFalse(list(installed.rglob("*.pyc")))

    def test_incomplete_source_does_not_create_install_destination(self):
        source = self.base / "incomplete"
        shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns("examples", "__pycache__"))
        test_home = self.base / "recipient"
        with self.assertRaises(SystemExit):
            self.install(source, test_home, self.snippets[0])
        self.assertFalse((test_home / ".codex/skills/zerox-due-diligence").exists())

    def test_existing_install_is_preserved(self):
        test_home = self.base / "recipient"
        destination = test_home / ".codex/skills/zerox-due-diligence"
        destination.mkdir(parents=True)
        (destination / "keep.txt").write_text("existing skill")
        with self.assertRaises(FileExistsError):
            self.install(ROOT, test_home, self.snippets[0])
        self.assertEqual((destination / "keep.txt").read_text(), "existing skill")

    def test_copy_failure_removes_only_new_partial_install(self):
        test_home = self.base / "recipient"
        test_home.mkdir()
        (test_home / "keep.txt").write_text("unrelated")
        with patch("shutil.copytree", side_effect=OSError("simulated copy failure")):
            with self.assertRaises(OSError):
                self.install(ROOT, test_home, self.snippets[0])
        self.assertFalse((test_home / ".codex/skills/zerox-due-diligence").exists())
        self.assertEqual((test_home / "keep.txt").read_text(), "unrelated")

    def test_installed_example_rebuilds_without_source_checkout(self):
        installed = self.install(ROOT, self.base / "recipient", self.snippets[0])
        configs = list((installed / "examples").rglob("project-config.json"))
        self.assertEqual(len(configs), 1)
        project = configs[0].parent
        report = self.base / "rebuilt.html"
        self.run_cli(installed, "build_report.py", "--project", project,
                     "--content", project / "report-content.json", "--output", report)
        result = self.run_cli(installed, "check_report.py", "--project", project, "--report", report)
        self.assertEqual(result["errors"], [])
        self.assertTrue(report.with_name("rebuilt-audit.md").exists())
        self.assertNotIn(str(ROOT), report.read_text())


if __name__ == "__main__":
    unittest.main()
