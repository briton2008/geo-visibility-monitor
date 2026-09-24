#!/usr/bin/env python3
"""Fail when a release package contains private data or misses required files."""

import json
import hashlib
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "README.md",
    "CHANGELOG.md",
    "LICENSE",
    ".github/SECURITY.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "PROVIDERS.md",
    "TRADEMARKS.md",
    "assets/logo.png",
    "config.example.json",
    "web/answer-data.example.js",
    ".github/workflows/ci.yml",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/feature_request.yml",
    ".github/pull_request_template.md",
]
BLOCKED_FINGERPRINTS = [
    (3, "2c3eff6a015cc7f14edee8056d7e9e7265b5fec3c9f801b12dbb0a62c0ce9397", "private brand name"),
    (10, "e836e60585ee7443dddc74327d00f092cb8a48b1541b6221a69793a9c8d6812a", "private brand alias"),
    (6, "87ff6b352ea35e1c6012aa0fd9774d3b1bd8bde9d61526be7def005a58b7b539", "private account name"),
    (10, "7e87aeda4c1af26bae79c21b11237ff266fac880ef63c1d7089288a85a954624", "unresolved placeholder"),
    (17, "866363805c55613a9e822dfb556cfaab2998f783cbb91e4a03ff031699ed42ea", "private dashboard host"),
]
TEXT_SUFFIXES = {".py", ".js", ".html", ".css", ".json", ".md", ".toml", ".yml", ".yaml"}
PUBLIC_BRAND_METADATA = {
    Path("README.md"),
    Path("TRADEMARKS.md"),
    Path(".codex-plugin/plugin.json"),
    Path(".claude-plugin/plugin.json"),
    Path(".claude-plugin/marketplace.json"),
    Path("web/index.html"),
    Path("web/language.js"),
}
PUBLIC_REPOSITORY_METADATA = {
    Path("README.md"),
    Path("CHANGELOG.md"),
    Path(".agents/plugins/marketplace.json"),
    Path(".github/ISSUE_TEMPLATE/config.yml"),
    Path("web/index.html"),
}


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(2)


def main() -> int:
    missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
    if missing:
        fail(f"missing required files: {', '.join(missing)}")

    config = json.loads((ROOT / "config.example.json").read_text(encoding="utf-8"))
    if config.get("brand", {}).get("official_domains") != ["example.com"]:
        fail("example config must use only example.com brand identity")

    findings = []
    tracked = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout.decode("utf-8").split("\0")
    for relative_text in tracked:
        if not relative_text:
            continue
        relative = Path(relative_text)
        path = ROOT / relative
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        if relative == Path("scripts/release_check.py") or any(part in {".git", ".venv", "__pycache__"} for part in relative.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        folded = text.casefold()
        if "github_owner" in folded:
            findings.append(f"{relative}: GitHub owner placeholder")
        for length, fingerprint, label in BLOCKED_FINGERPRINTS:
            if label in {"private brand name", "private brand alias"} and relative in PUBLIC_BRAND_METADATA:
                continue
            if label == "private account name" and relative in PUBLIC_REPOSITORY_METADATA:
                continue
            if any(
                hashlib.sha256(folded[index:index + length].encode()).hexdigest() == fingerprint
                for index in range(max(0, len(folded) - length + 1))
            ):
                findings.append(f"{relative}: {label}")
    if findings:
        fail("; ".join(findings))

    ignored_paths = {
        "config.json": "config.json",
        "web/answer-data.js": "web/answer-data.js",
        "runs": "runs/example/report.json",
        "runs-by-provider": "runs-by-provider/example/report.json",
        "state": "state/monitoring-state.json",
    }
    for label, ignored in ignored_paths.items():
        result = subprocess.run(
            ["git", "check-ignore", "-q", ignored],
            cwd=ROOT,
            check=False,
        )
        if result.returncode != 0:
            fail(f"sensitive local path is not ignored: {label}")

    print("PASS: release package contains required files and no blocked private terms")
    return 0


if __name__ == "__main__":
    sys.exit(main())
