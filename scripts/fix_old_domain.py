#!/usr/bin/env python3
"""
NEO PULSE HUB — Legacy Domain Rewriter

Problem (diagnosed 2026-11-18): 22 files still reference the legacy domain
`neo-pulse-hub.com` (no `.it`) — including the daily article generator, which
stamps every NEW article with a canonical pointing at a domain we don't own.
Google treats such pages as duplicate/unverifiable and drops them from the
index — silently killing SEO for new content.

This script rewrites every occurrence of the legacy domain to the live one:
    https://neo-pulse-hub.com/...  ->  https://www.neo-pulse-hub.it.com/...
    http://neo-pulse-hub.com/...   ->  https://www.neo-pulse-hub.it.com/...
    //neo-pulse-hub.com/...        ->  //www.neo-pulse-hub.it.com/...

Safe:
  - idempotent (once fixed, no legacy domain remains to match)
  - --check mode reports remaining occurrences without writing (exit 1)
  - only rewrites text files (.html, .py, .js, .json, .xml, .txt, .md, .yml)

Usage:
  python3 scripts/fix_old_domain.py --write
  python3 scripts/fix_old_domain.py --check
"""
import re
import sys
from pathlib import Path

LEGACY = "neo-pulse-hub.com"
LIVE = "www.neo-pulse-hub.it.com"

# neo-pulse-hub.com must not match neo-pulse-hub.it.com (it wouldn't, since
# .it.com differs, but we anchor on the exact host boundary to be safe).
LEGACY_RE = re.compile(
    r"(?<![\w.\-])neo-pulse-hub\.com(?![\w.\-])"
)

TEXT_SUFFIXES = {".html", ".py", ".js", ".json", ".xml", ".txt", ".md", ".yml", ".yaml"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".github/workflows"}


def fix_text(content: str) -> tuple[str, int]:
    """Return (fixed_content, replacement_count)."""
    return LEGACY_RE.subn(LIVE, content)


def iter_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        yield path


def main() -> int:
    args = set(sys.argv[1:])
    check_mode = "--check" in args
    write_mode = "--write" in args
    if not (check_mode or write_mode):
        print("Usage: fix_old_domain.py --write | --check")
        return 2

    root = Path(__file__).resolve().parents[1]
    changed_files, remaining = [], 0

    for path in iter_files(root):
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        count = len(LEGACY_RE.findall(content))
        if not count:
            continue
        if check_mode:
            remaining += count
            print(f"  \u26a0\ufe0f {path.relative_to(root)}: {count} legacy reference(s)")
        else:
            fixed, _ = fix_text(content)
            path.write_text(fixed, encoding="utf-8")
            changed_files.append((path.relative_to(root), count))

    if check_mode:
        if remaining:
            print(f"\u274c {remaining} legacy domain reference(s) remain.")
            return 1
        print("\u2705 No legacy domain references — all URLs point at the live domain.")
        return 0

    print(f"Scanned text files under {root}")
    if changed_files:
        print(f"Fixed {sum(c for _, c in changed_files)} reference(s) in {len(changed_files)} file(s):")
        for rel, count in changed_files:
            print(f"  \u2705 {rel} ({count})")
    else:
        print("No legacy domain references found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
