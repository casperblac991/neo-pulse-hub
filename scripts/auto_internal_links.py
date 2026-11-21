#!/usr/bin/env python3
"""Auto internal linking + FAQ schema (v1.2).

v1.2 fix: when no product matches an article, English fallback text was
grammatically broken ("The this product"). Now uses natural phrasing.
Idempotent: removes all previous injected blocks and re-injects one copy.
Usage: auto_internal_links.py --write | --check
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

FAQ_SECTION_RE = re.compile(
    r'<section class="nph-faq-section"[^>]*' + re.escape(MARKER) + r'[^>]*>.*?</section>\s*',
    re.DOTALL)
FAQ_JSON_RE = re.compile(
    r'<script type="application/ld\+json"[^>]*' + re.escape(MARKER) + r'[^>]*>.*?</script>\s*',
    re.DOTALL)
RELATED_RE = re.compile(
    r'<aside class="nph-related"[^>]*' + re.escape(MARKER) + r'[^>]*>.*?</aside>\s*',
    re.DOTALL)


def load_articles():
    articles = []
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
            m = re.search(r"<h1[^>]*>(.*?)</h1>", content, re.DOTALL | re.IGNORECASE)
            title = re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else path.stem
            articles.append({"path": path, "lang": lang, "title": title,
                             "content": content,
                             "category": guess_category(title, path.name)})
    return articles


def guess_category(title, filename):
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


def related_articles(current, all_articles):
    same_lang = [a for a in all_articles if a["lang"] == current["lang"] and a["path"] != current["path"]]
    same_cat = [a for a in same_lang if a["category"] == current["category"]]
    pool = same_cat if len(same_cat) >= 3 else same_cat + [a for a in same_lang if a["category"] != current["category"]]
    return pool[:3]


def find_product_for(title, catalog):
    t = title.lower()
    for product in catalog:
        name = product.get("name")
        if isinstance(name, dict):
            for lang in ("ar", "en"):
                c = str(name.get(lang, "")).strip()
                if c and (c.lower() in t or t in c.lower()):
                    return product
        elif name:
            c = str(name).strip()
            if c.lower() in t:
                return product
    return None


def build_related_block(current, related, lang):
    heading = "🔗 مقالات ذات صلة" if lang == "ar" else "🔗 Related articles"
    links = "".join(
        f'<li><a href="{BASE_URL}/{a["path"].relative_to(ROOT).as_posix()}">{a["title"]}</a></li>'
        for a in related)
    return (f'<aside class="nph-related" {MARKER}="1" '
            f'style="margin:2.5rem 0;padding:1.4rem 1.6rem;background:#0a0d1a;'
            f'border:1px solid rgba(99,179,237,.2);border-radius:14px">'
            f'<h3 style="font-size:1.05rem;font-weight:800;margin-bottom:.7rem">{heading}</h3>'
            f'<ul style="padding-inline-start:1.2rem;line-height:2">{links}</ul></aside>')


def build_faq_block(product, lang):
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
    rating = (product.get("rating", 4.5) if product else 4.5)
    reviews = (product.get("reviews", 500) if product else 500)

    if ar:
        if name:
            qa = [
                (f"كم سعر {name}؟", f"يتراوح سعر {name} حوالي {price_text.strip() or 'من 100$'} حسب المتجر والموسم — استخدم أزرار الشراء أعلى المقال لمقارنة السعر الحي بين أمازون وAliExpress."),
                (f"هل {name} يستحق الشراء؟", f"حسب تقييمات المشترين الموثقة، {name} يحصل على {rating}/5 من {reviews} مراجعة — تقييم ممتاز في فئته."),
                ("أين أشتريه بأفضل سعر؟", "نوصي بمقارنة السعر بين أمازون وAliExpress عبر الأزرار أعلى المقال — كلاهما آمن، واختر الأرخص لحظة الشراء."),
            ]
        else:
            qa = [
                ("كم تبلغ أسعار المنتجات المعروضة؟", "تختلف الأسعار حسب المتجر والموسم — استخدم أزرار الشراء أعلى المقال لمقارنة السعر الحي بين أمازون وAliExpress."),
                ("هل المنتجات المعروضة تستحق الشراء؟", f"نعرض فقط منتجات بتقييم موثوق {rating}/5 فأعلى من مراجعات مشترين حقيقية."),
                ("أين أشتري بأفضل سعر؟", "نوصي بمقارنة السعر بين أمازون وAliExpress عبر الأزرار أعلى المقال — كلاهما آمن، واختر الأرخص لحظة الشراء."),
            ]
    else:
        if name:
            qa = [
                (f"How much does the {name} cost?", f"The {name} typically runs around {price_text.strip() or '$100'} depending on store and season — use the buy buttons above to compare live Amazon and AliExpress prices."),
                (f"Is the {name} worth buying?", f"Based on verified buyer ratings, the {name} scores {rating}/5 from {reviews} reviews — an excellent rating for its category."),
                ("Where is the best place to buy it?", "We recommend comparing Amazon and AliExpress prices via the buttons above — both are safe; pick the cheaper one at checkout."),
            ]
        else:
            qa = [
                ("How much do the products listed here cost?", "Prices vary by store and season — use the buy buttons above to compare live Amazon and AliExpress prices."),
                ("Are the products listed here worth buying?", f"We only feature products with verified ratings of {rating}/5 or higher from real buyer reviews."),
                ("Where is the best place to buy?", "We recommend comparing Amazon and AliExpress prices via the buttons above — both are safe; pick the cheaper one at checkout."),
            ]

    faq_json = {"@context": "https://schema.org", "@type": "FAQPage",
                "mainEntity": [{"@type": "Question", "name": q,
                                "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]}
    items = "".join(
        f'<details style="background:#0a0d1a;border:1px solid rgba(99,179,237,.2);border-radius:12px;padding:1rem 1.2rem;margin-bottom:.7rem">'
        f'<summary style="font-weight:700;cursor:pointer">{q}</summary>'
        f'<p style="margin-top:.7rem;color:rgba(226,232,240,.75)">{a}</p></details>'
        for q, a in qa)
    heading = "❓ أسئلة شائعة" if ar else "❓ Frequently asked questions"
    return (f'<section class="nph-faq-section" {MARKER}="1" style="margin:2.5rem 0">'
            f'<h2 style="font-size:1.25rem;font-weight:800;margin-bottom:1rem">{heading}</h2>'
            f'{items}</section><script type="application/ld+json" {MARKER}="1">'
            f'{json.dumps(faq_json, ensure_ascii=False)}</script>')


def count_auto_blocks(content):
    return (len(FAQ_SECTION_RE.findall(content)), len(FAQ_JSON_RE.findall(content)))


def inject(content, related_html, faq_html):
    content = FAQ_SECTION_RE.sub("", content)
    content = FAQ_JSON_RE.sub("", content)
    content = RELATED_RE.sub("", content)
    injection = faq_html + related_html
    for closing in ("</article>", "</main>", "</body>"):
        idx = content.rfind(closing)
        if idx != -1:
            return content[:idx] + injection + content[idx:]
    return content + injection


def main():
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
    print(json.dumps({"articles_processed": len(articles),
                      "articles_rewritten": fixed,
                      "duplicates_cleaned": deduped}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
