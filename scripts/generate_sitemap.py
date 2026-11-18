#!/usr/bin/env python3
"""Self-generating sitemap for NEO PULSE HUB.

Scans the repository for every indexable page (root .html files + blog
articles ar/en) and regenerates sitemap.xml from scratch on every deploy:

  * host is the canonical non-www https://neo-pulse-hub.it.com
  * lastmod from the file's git last-commit date when available,
    falling back to the file's mtime
  * new pages (e.g. black-friday.html, how-we-test.html, new daily
    articles) enter the sitemap automatically — zero manual upkeep

Usage:
  python3 scripts/generate_sitemap.py --write
  python3 scripts/generate_sitemap.py --check
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
SITEMAP_PATH = ROOT / "sitemap.xml"
BASE_URL = "https://neo-pulse-hub.it.com"

EXCLUDE = {"404.html", "thank-you.html", "test.html"}
CHANGEFREQ = {"index.html": "daily", "deals-of-the-hour.html": "hourly", "black-friday.html": "daily"}
PRIORITY = {"index.html": "1.0", "products.html": "0.9", "black-friday.html": "0.9", "blog/ar/index.html": "0.8"}


def git_lastmod(path: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "--", str(path.relative_to(ROOT))],
            cwd=ROOT, capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()[:10]  # YYYY-MM-DD
    except (subprocess.SubprocessError, OSError):
        pass
    return None


def file_lastmod(path: Path) -> str:
    try:
        stamp = path.stat().st_mtime
        return datetime.fromtimestamp(stamp, tz=timezone.utc).strftime("%Y-%m-%d")
    except OSError:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def iter_pages() -> list[Path]:
    pages = []
    for path in sorted(ROOT.glob("*.html")):
        if path.name not in EXCLUDE:
            pages.append(path)
    for blog_dir in (ROOT / "blog" / "ar", ROOT / "blog" / "en"):
        if blog_dir.is_dir():
            for path in sorted(blog_dir.glob("*.html")):
                pages.append(path)
    return pages


def build_sitemap() -> str:
    urls: list[str] = []
    for path in iter_pages():
        rel = path.relative_to(ROOT).as_posix()
        loc = f"{BASE_URL}/{rel}"
        lastmod = git_lastmod(path) or file_lastmod(path)
        name = path.name
        changefreq = CHANGEFREQ.get(name, "weekly")
        priority = PRIORITY.get(rel, "0.7")
        urls.append(
            "  <url>\n"
            f"    <loc>{escape(loc)}</loc>\n"
            f"    <lastmod>{lastmod}</lastmod>\n"
            f"    <changefreq>{changefreq}</changefreq>\n"
            f"    <priority>{priority}</priority>\n"
            "  </url>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )


def main() -> int:
    args = set(sys.argv[1:])
    check_mode = "--check" in args
    write_mode = "--write" in args
    if not (check_mode or write_mode):
        print("Usage: generate_sitemap.py --write | --check")
        return 2

    content = build_sitemap()
    count = content.count("<loc>")

    if check_mode:
        current = SITEMAP_PATH.read_text(encoding="utf-8") if SITEMAP_PATH.exists() else ""
        if current != content:
            print(f"X sitemap.xml is stale ({current.count('<loc>')} urls, expected {count})")
            return 1
        print(f"OK: sitemap.xml current with {count} urls.")
        return 0

    SITEMAP_PATH.write_text(content, encoding="utf-8")
    print(json.dumps({"sitemap_urls": count, "output": str(SITEMAP_PATH)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
