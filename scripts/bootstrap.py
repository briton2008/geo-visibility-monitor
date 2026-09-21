#!/usr/bin/env python3
"""Create local editable config and synthetic dashboard data on first checkout."""

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def copy_if_missing(source: Path, target: Path) -> None:
    if target.exists():
        print(f"keep {target.relative_to(ROOT)}")
        return
    shutil.copyfile(source, target)
    print(f"create {target.relative_to(ROOT)}")


def main() -> None:
    copy_if_missing(ROOT / "config.example.json", ROOT / "config.json")
    copy_if_missing(ROOT / "web" / "answer-data.example.js", ROOT / "web" / "answer-data.js")


if __name__ == "__main__":
    main()
