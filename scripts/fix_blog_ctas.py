#!/usr/bin/env python3
"""
NEO PULSE HUB — Blog CTA Affiliate Rewriter

Root problem (diagnosed 2026-11-18): legacy blog articles link their buy
buttons to `products.html?id=NPH-XXX` — an internal catalog page that
ignores the id parameter. Readers who click "buy" land on a generic
catalog page and NO affiliate commission is ever tracked.

This script rewrites every such link into a direct affiliate link:
  - 1st CTA per product id -> Amazon search link (tag=neopulsehub09-20)
  - 2nd CTA per product id -> AliExpress Portals link (ma1023802882fefae)
Unknown NPH ids are left untouched and reported.

Safe:
  - idempotent (rewritten links no longer match the pattern)
  - --check mode reports remaining dead links without writing
  - never touches anything outside blog/**/*.html

Usage:
  python3 scripts/fix_blog_ctas.py --write   # rewrite dead CTAs
  python3 scripts/fix_blog_ctas.py --check   # report only (exit 1 if any)
"""
import re
import sys
from pathlib import Path
from urllib.parse import quote

AMAZON_TAG = "neopulsehub09-20"
ALI_TEMPLATE = (
    "https://s.click.aliexpress.com/e/_DDeGdzQ?aff_fcid=ma1023802882fefae"
    "&aff_platform=portals-tool&src=portals&url="
    "https%3A%2F%2Fwww.aliexpress.com%2Fwholesale%3FSearchText%3D{kw}"
)

# Legacy NPH product ids -> search keyword (verified against live articles)
NPH_PRODUCT_MAP = {
    "NPH-001": "Apple Watch Series 9",
    "NPH-002": "Samsung Galaxy Watch 6 Classic",
    "NPH-003": "Meta Ray-Ban Smart Glasses",
    "NPH-004": "Sony WH-1000XM5 Headphones",
    "NPH-005": "Apple AirPods Pro 2",
    "NPH-006": "Amazon Echo Show 10",
    "NPH-007": "Garmin Venu 3",
    "NPH-008": "Sony WH-1000XM5",
    "NPH-009": "Apple Watch Ultra 2",
    "NPH-010": "Google Nest Thermostat",
    "NPH-011": "Logitech MX Master 3S",
    "NPH-012": "Oura Ring Gen 3",
    "NPH-013": "Samsung Galaxy Buds2 Pro",
    "NPH-014": "Apple iPad Air 10.9",
    "NPH-015": "Apple Pencil Pro",
    "NPH-016": "Xiaomi Mi Band 8 Pro",
    "NPH-017": "Withings Body Scan",
    "NPH-018": "Philips Hue Starter Kit",
    "NPH-019": "Anker Soundcore Liberty 4 NC",
    "NPH-020": "Amazon Fire TV Stick 4K Max",
}

DEAD_CTA_RE = re.compile(
    r'<a\b([^>]*?)href="https?://[^"]*?products\.html\?id=(NPH-\d+)"([^>]*)>(.*?)</a>',
    re.S,
)


def amazon_link(keyword: str) -> str:
    return f"https://www.amazon.com/s?k={quote(keyword)}&tag={AMAZON_TAG}&ref=nosim"


def aliexpress_link(keyword: str) -> str:
    return ALI_TEMPLATE.format(kw=quote(keyword).replace("%20", "%2520"))


def rewrite_file(path: Path, lang_is_en: bool):
    """Rewrite dead CTAs in one file. Returns (changed, dead_left, unknown_ids)."""
    try:
        html = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False, 0, set()

    seen = {}
    unknown = set()

    def repl(match):
        pre, nph, post = match.group(1), match.group(2), match.group(3)
        keyword = NPH_PRODUCT_MAP.get(nph)
        if not keyword:
            unknown.add(nph)
            return match.group(0)
        count = seen.get(nph, 0)
        seen[nph] = count + 1
        if count % 2 == 0:
            url = amazon_link(keyword)
            label = "\U0001F6D2 Buy now on Amazon" if lang_is_en else "\U0001F6D2 \u0627\u0634\u062A\u0631\u0650 \u0627\u0644\u0622\u0646 \u0645\u0646 \u0623\u0645\u0627\u0632\u0648\u0646"
        else:
            url = aliexpress_link(keyword)
            label = "\U0001F6D2 Buy on AliExpress" if lang_is_en else "\U0001F6D2 \u0627\u0634\u062A\u0631\u0650 \u0627\u0644\u0622\u0646 \u0645\u0646 AliExpress"
        attrs = re.sub(r'\s*rel="[^"]*"', "", (pre + post))
        return (
            f'<a{attrs} href="{url}" target="_blank" '
            f'rel="nofollow sponsored noopener">{label}</a>'
        )

    new_html = DEAD_CTA_RE.sub(repl, html)
    changed = new_html != html
    if changed:
        path.write_text(new_html, encoding="utf-8")
    dead_left = len(DEAD_CTA_RE.findall(new_html))
    return changed, dead_left, unknown


def main() -> int:
    args = set(sys.argv[1:])
    check_mode = "--check" in args
    write_mode = "--write" in args
    if not (check_mode or write_mode):
        print("Usage: fix_blog_ctas.py --write | --check")
        return 2

    root = Path(".").resolve()
    files = sorted(root.glob("blog/**/*.html"))
    changed_files, remaining, unknown_all = [], 0, set()

    for path in files:
        if check_mode:
            try:
                html = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            matches = DEAD_CTA_RE.findall(html)
            if matches:
                remaining += len(matches)
                print(f"  \u26a0\ufe0f {path}: {len(matches)} dead CTA link(s)")
                unknown_all |= {m[1] for m in matches if m[1] not in NPH_PRODUCT_MAP}
        else:
            lang_is_en = "/en/" in path.as_posix()
            changed, dead_left, unknown = rewrite_file(path, lang_is_en)
            if changed:
                changed_files.append(str(path))
            remaining += dead_left
            unknown_all |= unknown

    if check_mode:
        if remaining:
            print(f"\u274c {remaining} dead CTA link(s) remain across the blog.")
            return 1
        print(f"\u2705 All {len(files)} blog articles carry direct affiliate CTAs.")
        return 0

    print(f"Scanned {len(files)} blog articles.")
    if changed_files:
        print(f"Rewrote dead CTAs in {len(changed_files)} file(s):")
        for name in changed_files:
            print(f"  \u2705 {name}")
    else:
        print("No dead CTAs found \u2014 all blog buy buttons are direct affiliate links.")
    if unknown_all:
        print(f"\u2139\ufe0f Unknown product id(s) left untouched: {', '.join(sorted(unknown_all))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
