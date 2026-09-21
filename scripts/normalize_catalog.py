#!/usr/bin/env python3
"""Normalize the public product catalog without inventing commercial data.

Usage:
  python3 scripts/normalize_catalog.py --check
  python3 scripts/normalize_catalog.py --write
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "products.json"
IMAGE_ROOT = ROOT
PLACEHOLDER = "https://placehold.co/800x800/0a0d1a/60a5fa?text=NEO+PULSE+HUB"


def number(value: Any, default: float = 0.0) -> float:
    try:
        if isinstance(value, str):
            value = value.replace("$", "").replace(",", "").strip()
        return float(value)
    except (TypeError, ValueError):
        return default


def integer(value: Any, default: int = 0) -> int:
    try:
        return int(float(str(value).replace(",", "").strip()))
    except (TypeError, ValueError):
        return default


def text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def localized(value: Any) -> dict[str, str]:
    if isinstance(value, dict):
        return {"ar": text(value.get("ar")), "en": text(value.get("en"))}
    return {"ar": text(value), "en": text(value)}


def clean_product(raw: dict[str, Any]) -> dict[str, Any] | None:
    product = dict(raw)
    product_id = text(product.get("id"))
    name = localized(product.get("name"))
    if not product_id or not (name["ar"] or name["en"]):
        return None

    product["id"] = product_id
    product["name"] = name
    product["price"] = round(max(number(product.get("price")), 0), 2)
    product["rating"] = round(min(max(number(product.get("rating")), 0), 5), 1)
    product["reviews"] = max(integer(product.get("reviews")), 0)
    product["category"] = text(product.get("category")) or "other"

    gallery = product.get("gallery") if isinstance(product.get("gallery"), list) else []
    image = text(product.get("image"))
    if image and image not in gallery:
        gallery.insert(0, image)
    gallery = list(dict.fromkeys(text(item) for item in gallery if text(item)))
    if not gallery:
        gallery = [PLACEHOLDER]
    product["image"] = gallery[0]
    product["gallery"] = gallery[:8]

    if isinstance(product.get("specifications"), dict):
        product["specifications"] = product["specifications"]
    else:
        product["specifications"] = {"ar": {}, "en": {}}
    if not isinstance(product.get("global_prices"), dict):
        product["global_prices"] = product.get("global_prices") or product.get("globalPrices") or {}
    product["affiliate_amazon"] = text(product.get("affiliate_amazon"))
    product["updated_at"] = text(product.get("updated_at") or product.get("updatedAt"))
    return product


def key_for(product: dict[str, Any]) -> str:
    name = product.get("name", {})
    english = text(name.get("en") if isinstance(name, dict) else name).casefold()
    arabic = text(name.get("ar") if isinstance(name, dict) else name).casefold()
    return re.sub(r"\s+", " ", f"{english}|{arabic}|{product.get('category', '')}").strip()


def load_normalized() -> tuple[list[dict[str, Any]], dict[str, int]]:
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("products.json must contain a JSON array")
    stats = {"input": len(data), "invalid": 0, "duplicate_ids": 0, "duplicate_names": 0}
    by_id: dict[str, dict[str, Any]] = {}
    for raw in data:
        product = clean_product(raw) if isinstance(raw, dict) else None
        if product is None:
            stats["invalid"] += 1
            continue
        if product["id"] in by_id:
            stats["duplicate_ids"] += 1
            current = by_id[product["id"]]
            if len(json.dumps(product, ensure_ascii=False)) > len(json.dumps(current, ensure_ascii=False)):
                by_id[product["id"]] = product
        else:
            by_id[product["id"]] = product

    by_name: dict[str, dict[str, Any]] = {}
    for product in by_id.values():
        key = key_for(product)
        if key in by_name:
            stats["duplicate_names"] += 1
            current = by_name[key]
            current_score = (number(current.get("rating")), integer(current.get("reviews")))
            product_score = (number(product.get("rating")), integer(product.get("reviews")))
            if product_score > current_score:
                by_name[key] = product
        else:
            by_name[key] = product
    return sorted(by_name.values(), key=lambda item: item["id"]), stats


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if not args.check and not args.write:
        parser.error("choose --check or --write")

    products, stats = load_normalized()
    output = json.dumps(products, ensure_ascii=False, indent=2) + "\n"
    current = CATALOG_PATH.read_text(encoding="utf-8")
    changed = current != output
    print(json.dumps({**stats, "output": len(products), "changed": changed}, ensure_ascii=False))
    if args.write and changed:
        CATALOG_PATH.write_text(output, encoding="utf-8")
        print(f"wrote {CATALOG_PATH}")
    return 1 if args.check and changed else 0


if __name__ == "__main__":
    sys.exit(main())
