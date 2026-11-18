#!/usr/bin/env python3
"""Fix duplicated/placeholder product images in products.json.

Replaces repeated placehold.co placeholders in galleries with unique,
category-appropriate real photos (Unsplash CDN URLs, free to hotlink),
and deduplicates gallery entries.

Runs automatically as part of catalog normalization (deploy time).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "products.json"

# Unique, per-category product photos (Unsplash CDN, free license).
# Expanded pools so every product gets distinct images even with a
# large catalog; deterministic cycling guarantees full galleries.
CATEGORY_IMAGES: dict[str, list[str]] = {
    "smartwatch": [
        "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&q=80",
        "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=800&q=80",
        "https://images.unsplash.com/photo-1617043786394-f977fa12eddf?w=800&q=80",
        "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=800&q=80",
        "https://images.unsplash.com/photo-1546868871-7041f2fbcf45?w=800&q=80",
        "https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?w=800&q=80",
    ],
    "earbuds": [
        "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800&q=80",
        "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=800&q=80",
        "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=800&q=80",
        "https://images.unsplash.com/photo-1516280440614-379a5dc9db41?w=800&q=80",
        "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80",
        "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=800&q=80",
    ],
    "smart-home": [
        "https://images.unsplash.com/photo-1558002038-1055907df827?w=800&q=80",
        "https://images.unsplash.com/photo-1585060544812-6b45742d762a?w=800&q=80",
        "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800&q=80",
        "https://images.unsplash.com/photo-1558021212-9f277a9a6ef0?w=800&q=80",
        "https://images.unsplash.com/photo-1524678606370-a47ad25cb82a?w=800&q=80",
        "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&q=80",
    ],
    "accessories": [
        "https://images.unsplash.com/photo-1527814050087-3793815479db?w=800&q=80",
        "https://images.unsplash.com/photo-1572569517542-6c2ad68f7854?w=800&q=80",
        "https://images.unsplash.com/photo-1600294037681-c5b4a4d0b4ef?w=800&q=80",
        "https://images.unsplash.com/photo-1625139201317-0a4b0e1f4b41?w=800&q=80",
        "https://images.unsplash.com/photo-1598550476439-6847785fcea6?w=800&q=80",
        "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=800&q=80",
    ],
    "fallback": [
        "https://images.unsplash.com/photo-1498049794561-7780e7231661?w=800&q=80",
        "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=800&q=80",
        "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&q=80",
        "https://images.unsplash.com/photo-1588508065123-287b28e013da?w=800&q=80",
    ],
}

PLACEHOLDER_PATTERNS = re.compile(r"placehold\.co|via\.placeholder", re.IGNORECASE)


def is_placeholder(url: str) -> bool:
    return bool(url and PLACEHOLDER_PATTERNS.search(url))


def normalize_category(product: dict[str, Any]) -> str:
    category = str(product.get("category", "")).lower().strip()
    if "home" in category:
        return "smart-home"
    if "watch" in category:
        return "smartwatch"
    if "earbud" in category or "headphone" in category:
        return "earbuds"
    if "access" in category or not category:
        return "accessories"
    return CATEGORY_IMAGES.get(category, CATEGORY_IMAGES["fallback"]) and category


def fix_product_gallery(product: dict[str, Any], index: int) -> dict[str, Any]:
    raw_category = normalize_category(product)
    pool = CATEGORY_IMAGES.get(raw_category, CATEGORY_IMAGES["accessories"])

    main_image = str(product.get("image", "") or "")
    gallery = product.get("gallery") if isinstance(product.get("gallery"), list) else []
    gallery = [str(item) for item in gallery if str(item).strip()]

    # Keep real (non-placeholder) images first, in order.
    real = [u for u in gallery if not is_placeholder(u)]

    # Fill up to 4 gallery slots with pool photos not already in the gallery.
    # Deterministic per-product offset so images stay distinct across products
    # even when the pool cycles (no two adjacent products share the same set).
    replacements: list[str] = []
    offset = index % len(pool)
    for step in range(len(pool)):
        if len(replacements) + len(real) >= 4:
            break
        url = pool[(offset + step) % len(pool)]
        if url not in real and url not in replacements:
            replacements.append(url)

    new_gallery = real + replacements
    # Deduplicate while preserving order.
    seen: set[str] = set()
    unique: list[str] = []
    for url in new_gallery:
        if url not in seen:
            seen.add(url)
            unique.append(url)
    if not unique:
        unique = [pool[offset]]

    product["gallery"] = unique[:4]
    if main_image and not is_placeholder(main_image):
        # Keep the real main image first if it's not already there.
        if main_image not in product["gallery"]:
            product["gallery"] = [main_image] + product["gallery"][:3]
    else:
        product["image"] = unique[0]

    # Ensure image is the first gallery entry for consistency.
    if product["gallery"] and product["gallery"][0] != product.get("image"):
        product["image"] = product["gallery"][0]
    return product


def main() -> int:
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        print("products.json must contain a JSON array", file=sys.stderr)
        return 1

    fixed = 0
    for index, product in enumerate(data):
        if not isinstance(product, dict):
            continue
        before = json.dumps(product.get("gallery"), ensure_ascii=False)
        fix_product_gallery(product, index)
        after = json.dumps(product.get("gallery"), ensure_ascii=False)
        if before != after:
            fixed += 1

    CATALOG_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"products_total": len(data), "galleries_fixed": fixed}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
