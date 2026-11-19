#!/usr/bin/env python3
"""
NEO PULSE HUB — Affiliate Injection Script
Automatically injects into every public HTML page (root + blog/ar + blog/en)
at deploy time:
  1. Affiliate disclosure notice (required by Amazon Associates ToS / FTC)
  2. Self-hosted affiliate click tracker (scripts/affiliate-tracker.js)
Safe: idempotent (skips already-injected pages), no external calls, no secrets.

Usage:
  python3 scripts/inject_affiliate_assets.py          # inject
  python3 scripts/inject_affiliate_assets.py --check  # verify only, exit 1 if missing
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Tracker path must be relative to each page's own location:
# root pages use scripts/..., blog pages use ../../scripts/...
def tracker_snippet_for(depth: int) -> str:
    prefix = "../" * depth
    return f'<script src="{prefix}scripts/affiliate-tracker.js" defer></script>'


def disclosure_snippet(lang: str) -> str:
    base = (
        '<div id="nph-affiliate-disclosure" style="position:fixed;bottom:0;left:0;right:0;'
        'z-index:999;background:rgba(2,5,16,.95);backdrop-filter:blur(10px);'
        'border-top:1px solid rgba(99,179,237,.25);padding:.55rem 1rem;text-align:center;'
        'font-size:.72rem;line-height:1.5;">'
        '<a href="/affiliate-disclosure.html" style="color:#60a5fa;text-decoration:underline;">'
        "{text}</a>"
        "</div>"
    )
    if lang == "en":
        return base.format(text="This site contains affiliate links — click for full disclosure")
    return base.format(text="يحتوي هذا الموقع على روابط تسويق بالعمولة (أفيليت) — انقر هنا للإفصاح الكامل")


SKIP_FILES = {
    "affiliate-disclosure.html",  # already a disclosure page
    "404.html",                   # not a public revenue page
}

# Directories to process, with their depth relative to repo root.
PAGE_DIRS = [
    (ROOT, 0),
    (ROOT / "blog" / "ar", 1),
    (ROOT / "blog" / "en", 1),
]


def page_language(html: str) -> str:
    match = re.search(r'<html[^>]*\blang\s*=\s*["\']?([a-zA-Z]{2})', html[:200])
    return match.group(1).lower() if match else "ar"


def process_html(path: Path, depth: int) -> bool:
    """Inject tracker + disclosure banner. Returns True if file changed."""
    try:
        html = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False

    original = html
    changed = False
    tracker = tracker_snippet_for(depth)

    if "affiliate-tracker.js" not in html:
        # strip any broken-depth tracker reference first (e.g. plain
        # scripts/... inside blog pages) to avoid duplicates
        html = re.sub(
            r'<script src="(?:\.\./)*scripts/affiliate-tracker\.js"[^>]*></script>\s*',
            "",
            html,
        )
        html = html.replace("</body>", tracker + "\n</body>", 1)
        changed = True

    if "nph-affiliate-disclosure" not in html:
        snippet = disclosure_snippet(page_language(html))
        html = html.replace("</body>", snippet + "\n</body>", 1)
        changed = True

    if changed:
        path.write_text(html, encoding="utf-8")
    return html != original


def main() -> int:
    check_mode = "--check" in sys.argv
    changed_files = []
    missing = []
    total = 0

    for directory, depth in PAGE_DIRS:
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.html")):
            if path.name in SKIP_FILES:
                continue
            total += 1
            try:
                html = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            has_assets = ("affiliate-tracker.js" in html and "nph-affiliate-disclosure" in html)
            if check_mode and not has_assets:
                missing.append(str(path.relative_to(ROOT)))
            if not check_mode and process_html(path, depth):
                changed_files.append(str(path.relative_to(ROOT)))

    if check_mode:
        if missing:
            print(f"X {len(missing)} page(s) missing affiliate assets:")
            for name in missing:
                print(f"  ! {name}")
            return 1
        print(f"OK: all {total} public pages carry disclosure + tracker.")
        return 0

    print(f"Processed {total} HTML files (root + blog).")
    if changed_files:
        print(f"Injected affiliate assets into {len(changed_files)} file(s):")
        for name in changed_files:
            print(f"  + {name}")
    else:
        print("No changes needed — all pages already carry disclosure + tracker.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
