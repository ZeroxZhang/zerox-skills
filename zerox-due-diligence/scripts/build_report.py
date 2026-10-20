"""主报告命令入口；默认生成 HTML，兼容旧版 Markdown 底稿。"""
from common import cli
from reader_report import build, main

if __name__ == "__main__":
    raise SystemExit(cli(main))
