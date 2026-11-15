#!/usr/bin/env python3
"""Fill affiliate_aliexpress links in products.json using the approved
AliExpress Portals tracking ID.

Uses the official Portals deep-link format so every product click is
attributed to the platform's tracking ID. Idempotent: safe to re-run;
existing non-empty affiliate_aliexpress values are preserved unless
--force is passed.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "products.json"
TRACKING_ID = "ma1023802882fefae"

# Search-based storefront entry points per product (AliExpress search URL).
# The deep-link wrapper keeps the tracking ID attached to every hop.
def build_link(product: dict[str, Any]) -> str | None:
    name = product.get("name", {})
    if not isinstance(name, dict):
        return None
    query = (name.get("en") or name.get("ar") or "").strip()
    if not query:
        return None
    search_url = "https://www.aliexpress.com/wholesale?SearchText=" + quote(query)
    return f"https://s.click.aliexpress.com/e/_DDeGdzQ?aff_fcid={TRACKING_ID}&aff_platform=portals-tool&src=portals&url={quote(search_url, safe='')}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="overwrite existing aliexpress links")
    args = parser.parse_args()

    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        print("products.json must be a JSON array", file=sys.stderr)
        return 1

    filled = 0
    for product in data:
        if not isinstance(product, dict):
            continue
        existing = (product.get("affiliate_aliexpress") or "").strip()
        if existing and not args.force:
            continue
        link = build_link(product)
        if link:
            product["affiliate_aliexpress"] = link
            filled += 1

    CATALOG_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"filled": filled, "tracking_id": TRACKING_ID}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
