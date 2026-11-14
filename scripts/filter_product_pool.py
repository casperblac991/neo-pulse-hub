#!/usr/bin/env python3
"""Safely filter products_pool.json into a reviewable candidate catalog.

The source pool is never modified. By default this writes a report only;
use --write to create products_candidates.json. The script deliberately does
not merge candidates into products.json because prices, images, and affiliate
links still need human verification.

Examples:
  python3 scripts/filter_product_pool.py
  python3 scripts/filter_product_pool.py --write
  python3 scripts/filter_product_pool.py --write --output /tmp/candidates.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
POOL_PATH = ROOT / "products_pool.json"
CATALOG_PATH = ROOT / "products.json"
DEFAULT_OUTPUT = ROOT / "products_candidates.json"


def text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def number(value: Any) -> float | None:
    try:
        value = text(value).replace("$", "").replace(",", "")
        result = float(value)
        return result if result > 0 else None
    except (TypeError, ValueError):
        return None


def normalize(value: Any) -> str:
    value = text(value).casefold()
    value = re.sub(r"[^\w\u0600-\u06ff]+", " ", value, flags=re.UNICODE)
    return re.sub(r"\s+", " ", value).strip()


def image_is_usable(value: Any) -> bool:
    image = text(value)
    if not image:
        return False
    if image.startswith(("http://", "https://")):
        parsed = urlparse(image)
        return bool(parsed.netloc and parsed.path)
    return (ROOT / image).is_file()


def product_names(item: dict[str, Any]) -> set[str]:
    return {
        key for key in (
            normalize(item.get("name")),
            normalize(item.get("name_ar")),
            normalize(item.get("name_en")),
        ) if key
    }


def product_keys(item: dict[str, Any]) -> set[str]:
    keys: set[str] = set()
    for field in ("id", "sku", "asin", "affiliate_amazon"):
        value = normalize(item.get(field))
        if value:
            keys.add(f"{field}:{value}")
    return keys


def canonicalize(item: dict[str, Any]) -> dict[str, Any]:
    name = {
        "ar": text(item.get("name_ar")),
        "en": text(item.get("name_en")),
    }
    return {
        "id": text(item.get("id")),
        "name": name,
        "price": number(item.get("price")),
        "rating": number(item.get("rating")) or 0,
        "category": text(item.get("category")) or "other",
        "image": text(item.get("image")),
        "affiliate_amazon": text(item.get("affiliate_amazon")),
        "reviews": int(item.get("reviews") or 0),
        "description": {
            "ar": text(item.get("description_ar")),
            "en": text(item.get("description_en")),
        },
        "source_pool_id": text(item.get("id")),
    }


def load_array(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path.name} must contain a JSON array")
    return [item for item in data if isinstance(item, dict)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write candidates JSON")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    pool = load_array(POOL_PATH)
    existing = load_array(CATALOG_PATH)
    existing_keys = {key for item in existing for key in (*product_keys(item), *[f"name:{name}" for name in product_names(item)])}

    seen_ids: set[str] = set()
    seen_keys: set[str] = set()
    seen_names: set[str] = set()
    candidates: list[dict[str, Any]] = []
    reasons: Counter[str] = Counter()

    for item in pool:
        item_id = normalize(item.get("id"))
        names = product_names(item)
        keys = product_keys(item)
        price = number(item.get("price"))
        if not item_id or not names:
            reasons["missing_id_or_name"] += 1
            continue
        if price is None:
            reasons["invalid_price"] += 1
            continue
        if not image_is_usable(item.get("image")):
            reasons["invalid_image_url_or_path"] += 1
            continue
        if item_id in seen_ids or keys & seen_keys or names & seen_names:
            reasons["duplicate_inside_pool"] += 1
            continue
        if keys & existing_keys or {f"name:{name}" for name in names} & existing_keys:
            reasons["already_in_products_json"] += 1
            continue

        candidate = canonicalize(item)
        candidates.append(candidate)
        seen_ids.add(item_id)
        seen_keys.update(keys)
        seen_names.update(names)

    report = {
        "source": str(POOL_PATH.relative_to(ROOT)),
        "existing_catalog": str(CATALOG_PATH.relative_to(ROOT)),
        "input": len(pool),
        "candidates": len(candidates),
        "rejected": sum(reasons.values()),
        "reasons": dict(reasons),
        "output": str(args.output),
        "written": bool(args.write),
        "note": "Candidates require human verification before merging into products.json.",
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if args.write:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(candidates, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
