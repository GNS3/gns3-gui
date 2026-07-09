#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Read gns3server/version.py, extract __version__, and create an annotated git tag."
        )
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show the tag that would be created without creating it",
    )
    return parser.parse_args()


def run_git(args: list[str], repo_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )


def get_version(repo_root: Path) -> str:
    version_file = repo_root / "gns3" / "version.py"
    content = version_file.read_text(encoding="utf-8")
    match = re.search(r"^__version__\s*=\s*['\"]([^'\"]+)['\"]", content, re.MULTILINE)
    if not match:
        raise ValueError("Unable to find __version__ in gns3server/version.py")
    return match.group(1)


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent.parent

    inside_repo = run_git(["rev-parse", "--is-inside-work-tree"], repo_root)
    if inside_repo.returncode != 0:
        print(f"Error: {repo_root} is not a git repository.", file=sys.stderr)
        return 1

    try:
        tag = 'v' + get_version(repo_root)
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    existing_tag = run_git(["rev-parse", tag], repo_root)
    if existing_tag.returncode == 0:
        print(f"Error: tag '{tag}' already exists.", file=sys.stderr)
        return 1

    if args.dry_run:
        print(f"Dry run: would create tag '{tag}' from gns3server/version.py")
        return 0

    create_tag = run_git(["tag", "-a", tag, "-m", f"Release {tag}"], repo_root)
    if create_tag.returncode != 0:
        print(create_tag.stderr.strip() or "Error: failed to create tag", file=sys.stderr)
        return 1
    print(f"Created tag '{tag}'")

    push_tag = run_git(["push", "origin", tag], repo_root)
    if push_tag.returncode != 0:
        print(push_tag.stderr.strip() or "Error: failed to push tag", file=sys.stderr)
        return 1
    print(f"Tag '{tag}' has been pushed to the remote repository.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


