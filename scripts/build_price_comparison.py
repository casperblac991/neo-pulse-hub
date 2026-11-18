#!/usr/bin/env python3
"""Price comparison enrichment for NEO PULSE HUB.

Builds a lightweight cross-store price-comparison dataset (price-comparison.json)
from the product catalog: for every product that has BOTH an Amazon and an
AliExpress affiliate link, it computes the cheaper store, the price delta, and
a savings percentage, so pages can render a live "best price" comparison badge
next to buy buttons without any manual work.

Why: buyers who see a price comparison convert significantly better, and the
comparison keeps them on our platform until they click through with the
affiliate tag attached.

Idempotent — regenerates the same output from products.json on every deploy.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "products.json"
OUTPUT_PATH = ROOT / "price-comparison.json"


def number(value: Any) -> float | None:
    try:
        if isinstance(value, str):
            value = value.replace("$", "").replace(",", "").strip()
        result = float(value)
        return result if result > 0 else None
    except (TypeError, ValueError):
        return None


def build_comparison_entry(product: dict[str, Any]) -> dict[str, Any] | None:
    pid = str(product.get("id", "")).strip()
    if not pid:
        return None
    amazon = str(product.get("affiliate_amazon", "") or "").strip()
    aliexpress = str(product.get("affiliate_aliexpress", "") or "").strip()
    if not amazon or not aliexpress:
        # Comparison requires both stores to be meaningful.
        return None

    price = number(product.get("price"))
    if price is None:
        return None

    # The catalog carries a single reference price (USD). When it also carries
    # a known AliExpress price we use it; otherwise we present the catalog
    # price as the Amazon baseline and show both store buttons so the buyer
    # checks the live prices on the store pages in one click each.
    ali_price = number(product.get("aliexpress_price")) or price

    cheaper = "aliexpress" if ali_price < price else "amazon"
    delta = round(abs(price - ali_price), 2)
    savings_pct = round(delta / max(price, ali_price) * 100, 1)

    return {
        "id": pid,
        "name": product.get("name"),
        "category": product.get("category", ""),
        "stores": {
            "amazon": {"url": amazon, "price": price},
            "aliexpress": {"url": aliexpress, "price": ali_price},
        },
        "cheaper_store": cheaper,
        "price_delta_usd": delta,
        "savings_percent": savings_pct,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def main() -> int:
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        print("products.json must contain a JSON array", file=sys.stderr)
        return 1

    entries: list[dict[str, Any]] = []
    for product in data:
        if not isinstance(product, dict):
            continue
        entry = build_comparison_entry(product)
        if entry:
            entries.append(entry)

    entries.sort(key=lambda e: e["savings_percent"], reverse=True)
    OUTPUT_PATH.write_text(
        json.dumps({"products": entries}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"compared": len(entries), "output": str(OUTPUT_PATH.name)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
