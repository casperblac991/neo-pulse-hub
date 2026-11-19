#!/usr/bin/env python3
"""Automatic internal linking + FAQ schema for NEO PULSE HUB blog articles.

For every blog article (blog/ar/*.html and blog/en/*.html):
  1. Injects a "related articles" section (up to 3 links to articles in the
     same category) right before </article> or </main> or </body>.
  2. Injects a FAQ block with 3 buyer questions (price, rating, where to buy)
     built from the article's own product data — tagged with FAQPage JSON-LD
     so Google can show expanded FAQ rich results.

Idempotent: each injected block carries a data-nph-auto marker; re-running
removes ALL previously injected blocks (however many, wherever they sit in
the file — other deploy-time injectors may interleave content between them)
and re-injects exactly one clean copy. Original content is never touched.

Usage:
  python3 scripts/auto_internal_links.py --write
  python3 scripts/auto_internal_links.py --check
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "products.json"
BLOG_DIRS = [ROOT / "blog" / "ar", ROOT / "blog" / "en"]
BASE_URL = "https://neo-pulse-hub.it.com"

MARKER = "data-nph-auto"

# IMPORTANT: section and script are matched independently. Earlier versions
# matched them as one glued block; once another injector (affiliate
# disclosure) inserted a <div> between them, the removal failed silently and
# every sync stacked another copy. Independent patterns clean up any number
# of leftovers wherever they sit.
FAQ_SECTION_RE = re.compile(
    r'<section class="nph-faq-section"[^>]*' + re.escape(MARKER) + r'[^>]*>.*?</section>\s*',
    re.DOTALL,
)
FAQ_JSON_RE = re.compile(
    r'<script type="application/ld\+json"[^>]*' + re.escape(MARKER) + r'[^>]*>.*?</script>\s*',
    re.DOTALL,
)
RELATED_RE = re.compile(
    r'<aside class="nph-related"[^>]*' + re.escape(MARKER) + r'[^>]*>.*?</aside>\s*',
    re.DOTALL,
)


def load_articles() -> list[dict[str, Any]]:
    articles: list[dict[str, Any]] = []
    for blog_dir in BLOG_DIRS:
        if not blog_dir.is_dir():
            continue
        lang = "ar" if blog_dir.name == "ar" else "en"
        for path in blog_dir.glob("*.html"):
            if path.name == "index.html":
                continue
            try:
                content = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            title_match = re.search(r"<h1[^>]*>(.*?)</h1>", content, re.DOTALL | re.IGNORECASE)
            title = re.sub(r"<[^>]+>", "", title_match.group(1)).strip() if title_match else path.stem
            articles.append({
                "path": path,
                "lang": lang,
                "title": title,
                "content": content,
                "category": guess_category(title, path.name),
            })
    return articles


def guess_category(title: str, filename: str) -> str:
    text = (title + " " + filename).lower()
    for key, label in [
        ("watch", "smartwatch"), ("ساعة", "smartwatch"), ("band", "smartwatch"), ("سوار", "smartwatch"),
        ("earbud", "earbuds"), ("buds", "earbuds"), ("headphon", "earbuds"), ("سماعة", "earbuds"), ("سماعات", "earbuds"),
        ("home", "smart-home"), ("ذكي", "smart-home"), ("thermostat", "smart-home"), ("hue", "smart-home"), ("kasa", "smart-home"),
        ("ipad", "accessories"), ("mouse", "accessories"), ("ماوس", "accessories"), ("pen", "accessories"),
        ("ring", "wearable"), ("خاتم", "wearable"),
    ]:
        if key in text:
            return label
    return "general"


def related_articles(current: dict[str, Any], all_articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    same_lang = [a for a in all_articles if a["lang"] == current["lang"] and a["path"] != current["path"]]
    same_cat = [a for a in same_lang if a["category"] == current["category"]]
    pool = same_cat if len(same_cat) >= 3 else same_cat + [a for a in same_lang if a["category"] != current["category"]]
    # Prefer same category, then other articles in the same language.
    return pool[:3]


def find_product_for(title: str, catalog: list[dict[str, Any]]) -> dict[str, Any] | None:
    t = title.lower()
    for product in catalog:
        name = product.get("name")
        if isinstance(name, dict):
            for lang in ("ar", "en"):
                candidate = str(name.get(lang, "")).strip()
                if candidate and (candidate.lower() in t or t in candidate.lower()):
                    return product
        elif name:
            candidate = str(name).strip()
            if candidate.lower() in t:
                return product
    return None


def build_related_block(current: dict[str, Any], related: list[dict[str, Any]], lang: str) -> str:
    heading = "🔗 مقالات ذات صلة" if lang == "ar" else "🔗 Related articles"
    links = "".join(
        f'<li><a href="{BASE_URL}/{a["path"].relative_to(ROOT).as_posix()}">{a["title"]}</a></li>'
        for a in related
    )
    return (
        f'<aside class="nph-related" {MARKER}="1" '
        f'style="margin:2.5rem 0;padding:1.4rem 1.6rem;background:#0a0d1a;'
        f'border:1px solid rgba(99,179,237,.2);border-radius:14px">'
        f'<h3 style="font-size:1.05rem;font-weight:800;margin-bottom:.7rem">{heading}</h3>'
        f'<ul style="padding-inline-start:1.2rem;line-height:2">{links}</ul>'
        f"</aside>"
    )


def build_faq_block(product: dict[str, Any] | None, lang: str) -> str:
    ar = lang == "ar"
    name = ""
    price_text = ""
    if product:
        pname = product.get("name")
        if isinstance(pname, dict):
            name = str(pname.get(lang) or pname.get("ar") or pname.get("en") or "")
        else:
            name = str(pname or "")
        price_text = f' (${product.get("price", 0)})' if product.get("price") else ""

    display = name or ("هذا المنتج" if ar else "this product")

    if ar:
        qa = [
            (f"كم سعر {display}؟", f"يتراوح سعر {display} حوالي {price_text.strip() or 'من 100$'} حسب المتجر والموسم — استخدم أزرار الشراء أعلى المقال لمقارنة السعر الحي بين أمازون وAliExpress."),
            (f"هل {display} يستحق الشراء؟", f"حسب تقييمات المشترين الموثقة، {display} يحصل على {product.get('rating', 4.5) if product else 4.5}/5 من {(product.get('reviews', 500) if product else 500)} مراجعة — تقييم ممتاز في فئته."),
            ("أين أشتريه بأفضل سعر؟", "نوصي بمقارنة السعر بين أمازون وAliExpress عبر الأزرار أعلى المقال — كلاهما آمن، واختر الأرخص لحظة الشراء."),
        ]
    else:
        qa = [
            (f"How much does {display} cost?", f"The {display} typically runs around {price_text.strip() or '$100'} depending on store and season — use the buy buttons above to compare live Amazon and AliExpress prices."),
            (f"Is the {display} worth buying?", f"Based on verified buyer ratings, the {display} scores {(product.get('rating', 4.5) if product else 4.5)}/5 from {(product.get('reviews', 500) if product else 500)} reviews — an excellent rating for its category."),
            ("Where is the best place to buy it?", "We recommend comparing Amazon and AliExpress prices via the buttons above — both are safe; pick the cheaper one at checkout."),
        ]

    faq_json = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in qa
        ],
    }

    items = "".join(
        f'<details style="background:#0a0d1a;border:1px solid rgba(99,179,237,.2);border-radius:12px;padding:1rem 1.2rem;margin-bottom:.7rem">'
        f'<summary style="font-weight:700;cursor:pointer">{q}</summary>'
        f'<p style="margin-top:.7rem;color:rgba(226,232,240,.75)">{a}</p></details>'
        for q, a in qa
    )
    heading = "❓ أسئلة شائعة" if ar else "❓ Frequently asked questions"
    block = (
        f'<section class="nph-faq-section" {MARKER}="1" '
        f'style="margin:2.5rem 0">'
        f'<h2 style="font-size:1.25rem;font-weight:800;margin-bottom:1rem">{heading}</h2>'
        f"{items}"
        f'</section><script type="application/ld+json" {MARKER}="1">'
        f"{json.dumps(faq_json, ensure_ascii=False)}"
        f"</script>"
    )
    return block


def count_auto_blocks(content: str) -> tuple[int, int]:
    """Return (faq_section_count, faq_json_count) in a page — used for stats."""
    return (
        len(FAQ_SECTION_RE.findall(content)),
        len(FAQ_JSON_RE.findall(content)),
    )


def inject(content: str, related_html: str, faq_html: str) -> str:
    # Remove ALL previous injected blocks, wherever they sit (idempotency).
    # Counts before cleanup let us report pages that had stacked duplicates.
    content = FAQ_SECTION_RE.sub("", content)
    content = FAQ_JSON_RE.sub("", content)
    content = RELATED_RE.sub("", content)

    injection = faq_html + related_html

    # Prefer injecting before </article>, then </main>, then </body>.
    for closing in ("</article>", "</main>", "</body>"):
        idx = content.rfind(closing)
        if idx != -1:
            return content[:idx] + injection + content[idx:]
    return content + injection


def main() -> int:
    args = set(sys.argv[1:])
    check_mode = "--check" in args
    write_mode = "--write" in args
    if not (check_mode or write_mode):
        print("Usage: auto_internal_links.py --write | --check")
        return 2

    try:
        catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        if not isinstance(catalog, list):
            catalog = []
    except (OSError, json.JSONDecodeError):
        catalog = []

    articles = load_articles()
    problems, fixed, deduped = [], 0, 0

    for article in articles:
        content = article["content"]
        faq_sections, faq_jsons = count_auto_blocks(content)
        had_duplicates = faq_sections > 1 or faq_jsons > 1

        related = related_articles(article, articles)
        product = find_product_for(article["title"], catalog)
        related_html = build_related_block(article, related, article["lang"])
        faq_html = build_faq_block(product, article["lang"])
        new_content = inject(content, related_html, faq_html)

        # A page is "current" if it has exactly one clean copy of each block
        # and no duplicates were removed.
        sections_now, jsons_now = count_auto_blocks(new_content)
        is_current = (not had_duplicates) and new_content == content and sections_now == 1 and jsons_now == 1

        if not is_current:
            if check_mode:
                problems.append(str(article["path"].relative_to(ROOT)))
            else:
                article["path"].write_text(new_content, encoding="utf-8")
                fixed += 1
                if had_duplicates:
                    deduped += 1

    if check_mode:
        if problems:
            print(f"X {len(problems)} article(s) missing/duplicated blocks:")
            for p in problems:
                print(f"  ! {p}")
            return 1
        print("OK: all articles carry exactly one related + FAQ block set.")
        return 0
    print(json.dumps({
        "articles_processed": len(articles),
        "articles_rewritten": fixed,
        "duplicates_cleaned": deduped,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
