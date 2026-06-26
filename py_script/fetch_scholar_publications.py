#!/usr/bin/env python3
"""Google Scholar 抓取入口已暂停。

之前的 Google Scholar 爬取逻辑容易被反爬限制影响。按当前维护策略，本脚本只保留
一个明确的禁用提示，不访问网络，也不写入任何文件。
"""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "py_script" / "temp-pub-raw"


def main() -> None:
    parser = argparse.ArgumentParser(description="Google Scholar 抓取逻辑已暂停。")
    parser.add_argument("-y", "--year", type=int, help="保留参数兼容旧命令；当前不会执行抓取。")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="保留参数兼容旧命令；当前不会写入文件。")
    parser.add_argument("--max-pages", type=int, default=5, help="保留参数兼容旧命令；当前不会使用。")
    parser.add_argument("--delay", type=float, default=1.5, help="保留参数兼容旧命令；当前不会使用。")
    parser.add_argument("--profile-only", action="store_true", help="保留参数兼容旧命令；当前不会使用。")
    parser.add_argument("--dry-run", action="store_true", help="保留参数兼容旧命令；当前不会使用。")
    parser.parse_args()

    print("Google Scholar 抓取逻辑已暂停：本脚本不会访问网络，也不会生成 JSON。")
    print("当前请手工维护 py_script/temp-pub-raw/ 或 publications/ 下的 JSON，等待下一步方案。")


if __name__ == "__main__":
    main()
