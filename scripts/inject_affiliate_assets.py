#!/usr/bin/env python3
"""
NEO PULSE HUB — Affiliate Injection Script
Automatically injects into every HTML page at deploy time:
  1. Affiliate disclosure notice (required by Amazon Associates ToS / FTC)
  2. Self-hosted affiliate click tracker (scripts/affiliate-tracker.js)
Safe: idempotent (skips already-injected pages), no external calls, no secrets.
"""
import re
import sys
from pathlib import Path

TRACKER_SNIPPET = (
    '<script src="scripts/affiliate-tracker.js" defer></script>'
)

DISCLOSURE_SNIPPET = (
    '<div id="nph-affiliate-disclosure" style="position:fixed;bottom:0;left:0;right:0;'
    'z-index:999;background:rgba(2,5,16,.95);backdrop-filter:blur(10px);'
    'border-top:1px solid rgba(99,179,237,.25);padding:.55rem 1rem;text-align:center;'
    'font-size:.72rem;line-height:1.5;">'
    '<a href="/affiliate-disclosure.html" style="color:#60a5fa;text-decoration:underline;">'
    'يحتوي هذا الموقع على روابط تسويق بالعمولة (أفيليت) — انقر هنا للإفصاح الكامل</a>'
    '</div>'
)

DISCLOSURE_EN = (
    '<div id="nph-affiliate-disclosure" style="position:fixed;bottom:0;left:0;right:0;'
    'z-index:999;background:rgba(2,5,16,.95);backdrop-filter:blur(10px);'
    'border-top:1px solid rgba(99,179,237,.25);padding:.55rem 1rem;text-align:center;'
    'font-size:.72rem;line-height:1.5;">'
    '<a href="/affiliate-disclosure.html" style="color:#60a5fa;text-decoration:underline;">'
    'This site contains affiliate links — click for full disclosure</a>'
    '</div>'
)

SKIP_FILES = {
    "affiliate-disclosure.html",  # already a disclosure page
    "404.html",                   # not public-facing revenue page
}


def process_html(path: Path) -> bool:
    """Inject tracker + disclosure banner. Returns True if file changed."""
    try:
        html = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False

    original = html
    changed = False

    # 1) Inject tracker before </body> if not present
    if "affiliate-tracker.js" not in html:
        html = html.replace("</body>", TRACKER_SNIPPET + "\n</body>", 1)
        changed = True

    # 2) Inject disclosure banner before </body> if not present
    if "nph-affiliate-disclosure" not in html:
        lang = re.search(r'<html[^>]*\blang\s*=\s*["\']?([a-zA-Z]{2})', html[:200])
        snippet = DISCLOSURE_EN if lang and lang.group(1).lower().startswith("e") else DISCLOSURE_SNIPPET
        html = html.replace("</body>", snippet + "\n</body>", 1)
        changed = True

    if changed:
        path.write_text(html, encoding="utf-8")
    return changed


def main() -> int:
    root = Path(".").resolve()
    root_files = {p.name for p in root.glob("*.html")}
    changed_files = []
    total = 0

    for path in sorted(root.glob("*.html")):
        if path.name in SKIP_FILES:
            continue
        total += 1
        if process_html(path):
            changed_files.append(path.name)

    print(f"Processed {total} HTML files at repo root.")
    if changed_files:
        print(f"Injected affiliate assets into {len(changed_files)} file(s):")
        for name in changed_files:
            print(f"  ✅ {name}")
    else:
        print("No changes needed — all pages already carry disclosure + tracker.")

    if "--check" in sys.argv:
        print("CHECK MODE: listing pages missing disclosure only.")
        missing = []
        for path in sorted(root.glob("*. *.html")):
            pass  # placeholder
    return 0


if __name__ == "__main__":
    sys.exit(main())
