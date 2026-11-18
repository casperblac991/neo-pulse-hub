#!/usr/bin/env python3
"""
NEO PULSE HUB — Schema Markup Fixer

Diagnosed from Google Search Console URL inspection (2026-11-18):
  * "Product snippets: 3 valid items detected" BUT
  * "Merchant data: non-critical issues — 3 invalid items"

Root cause: the ItemList JSON-LD on index.html lists 3 Products with only
name/description/brand/price — missing the merchant-critical fields Google
requires for rich results: image, url, availability, aggregateRating,
and an offer url.

What this script does:
  1. Loads the canonical catalog (products.json).
  2. Scans every .html file for <script type="application/ld+json"> blocks.
  3. For each Product node, merges catalog data by matching product name:
       - image, url (product page)
       - offers.url (affiliate link), availability, price, priceCurrency
       - aggregateRating (ratingValue, reviewCount)
  4. Rewrites the JSON blocks with ensure_ascii=False (Arabic-safe).
  5. Also unifies the host across all text files to the NON-WWW live host
     (Google's selected canonical, and the host used in sitemap.xml):
       legacy   neo-pulse-hub.it.com / neo-pulse-hub.it.com -> neo-pulse-hub.it.com
       current  neo-pulse-hub.it.com                  -> neo-pulse-hub.it.com

Idempotent: enriched products already carry the fields, so re-running is a
no-op. --check mode reports what would change (exit 1 if anything missing).

Usage:
  python3 scripts/fix_schema_markup.py --write
  python3 scripts/fix_schema_markup.py --check
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "products.json"

LEGACY_HOST = "neo-pulse-hub.it.com"
LIVE_HOST = "neo-pulse-hub.it.com"

# Matches:
#   https://neo-pulse-hub.com...      (legacy, no .it)
#   https://www.neo-pulse-hub.com...  (legacy with www)
#   https://neo-pulse-hub.it.com  (live host with www — unify to non-www)
# Scheme is captured so we can preserve/normalize it; paths stay untouched
# because they sit outside the match. Does NOT match the non-www live host
# itself (idempotent) nor neo-pulse-hub.it.com inside longer names.
HOST_RE = re.compile(
    r"(https?://)?(www\.neo-pulse-hub\.it\.com|www\.neo-pulse-hub\.com|neo-pulse-hub\.com)(?![\w.\-])"
)

TEXT_SUFFIXES = {".html", ".py", ".js", ".json", ".xml", ".txt", ".md", ".yml", ".yaml"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build"}

JSONLD_RE = re.compile(
    r'(<script type="application/ld\+json">\s*)(.*?)(\s*</script>)',
    re.DOTALL | re.IGNORECASE,
)


def load_catalog() -> dict:
    """Return {normalized name -> product dict} from products.json."""
    catalog: dict = {}
    try:
        data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return catalog
    if not isinstance(data, list):
        return catalog
    for item in data:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        if isinstance(name, dict):
            for lang in ("en", "ar"):
                key = str(name.get(lang, "")).strip().casefold()
                if key:
                    catalog[key] = item
        elif name:
            catalog[str(name).strip().casefold()] = item
    return catalog


def find_product(catalog: dict, node: dict):
    """Match a JSON-LD Product node against the catalog by name."""
    name = str(node.get("name", "")).strip().casefold()
    if not name:
        return None
    if name in catalog:
        return catalog[name]
    # fallback: substring match (longest key first to reduce false positives)
    for key in sorted(catalog, key=len, reverse=True):
        if name in key or key in name:
            return catalog[key]
    return None


def product_page_url(product: dict) -> str:
    pid = str(product.get("id", "")).strip()
    if pid:
        return f"https://{LIVE_HOST}/products.html?id={pid}"
    return f"https://{LIVE_HOST}/products.html"


def enrich_product(node: dict, product: dict | None, changed: list) -> dict:
    """Fill merchant-critical fields on a Product JSON-LD node."""
    if product:
        image = str(product.get("image", "")).strip()
        if image and not node.get("image"):
            node["image"] = image
            changed.append("image")
        if not node.get("url"):
            node["url"] = product_page_url(product)
            changed.append("url")
        rating = product.get("rating")
        reviews = product.get("reviews")
        if rating and reviews and not node.get("aggregateRating"):
            node["aggregateRating"] = {
                "@type": "AggregateRating",
                "ratingValue": str(rating),
                "reviewCount": str(reviews),
            }
            changed.append("aggregateRating")
        offers = node.get("offers")
        if isinstance(offers, dict):
            amazon = str(product.get("affiliate_amazon", "")).strip()
            if amazon and not offers.get("url"):
                offers["url"] = amazon
                changed.append("offers.url")
            price = product.get("price")
            if price and not offers.get("price"):
                offers["price"] = str(price)
                changed.append("offers.price")
    # fields independent of catalog
    offers = node.get("offers")
    if isinstance(offers, dict) and not offers.get("availability"):
        offers["availability"] = "https://schema.org/InStock"
        changed.append("availability")
    if not node.get("url"):
        node["url"] = f"https://{LIVE_HOST}/products.html"
        changed.append("url")
    return node


def walk_nodes(node, catalog: dict, changed: list):
    """Recursively enrich every Product node inside any JSON-LD structure."""
    if isinstance(node, dict):
        if node.get("@type") == "Product":
            product = find_product(catalog, node)
            enrich_product(node, product, changed)
        for value in node.values():
            walk_nodes(value, catalog, changed)
    elif isinstance(node, list):
        for item in node:
            walk_nodes(item, catalog, changed)


def fix_jsonld_blocks(content: str, catalog: dict) -> tuple[str, list]:
    changed: list = []

    def repl(match: re.Match) -> str:
        prefix, body, suffix = match.group(1), match.group(2), match.group(3)
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            return match.group(0)  # leave invalid blocks untouched
        block_changed: list = []
        walk_nodes(data, catalog, block_changed)
        if block_changed:
            changed.extend(block_changed)
            new_body = json.dumps(data, ensure_ascii=False, indent=2)
            return prefix + new_body + suffix
        return match.group(0)

    return JSONLD_RE.sub(repl, content), changed


def unify_host(content: str) -> tuple[str, int]:
    """Legacy domain and www-variant of the live host -> non-www live host."""
    count = 0

    def repl(match: re.Match) -> str:
        nonlocal count
        count += 1
        scheme = match.group(1)  # may be None
        host = "https://" + LIVE_HOST if scheme else LIVE_HOST
        return host

    return HOST_RE.sub(repl, content), count


def iter_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        yield path


def main() -> int:
    args = set(sys.argv[1:])
    check_mode = "--check" in args
    write_mode = "--write" in args
    if not (check_mode or write_mode):
        print("Usage: fix_schema_markup.py --write | --check")
        return 2

    catalog = load_catalog()
    problems, fixes = [], []

    for path in iter_files(ROOT):
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        rel = str(path.relative_to(ROOT))

        unified, host_count = unify_host(content)
        enriched, schema_changes = fix_jsonld_blocks(unified, catalog)

        if host_count or schema_changes:
            if check_mode:
                if host_count:
                    problems.append(f"{rel}: {host_count} host reference(s) to unify")
                if schema_changes:
                    problems.append(f"{rel}: schema fields missing: {sorted(set(schema_changes))}")
            else:
                path.write_text(enriched, encoding="utf-8")
                fixes.append((rel, host_count, sorted(set(schema_changes))))

    if check_mode:
        if problems:
            print(f"X {len(problems)} issue(s) found:")
            for p in problems:
                print(f"  ! {p}")
            return 1
        print("OK: all JSON-LD products fully enriched and hosts unified.")
        return 0

    if fixes:
        print(f"Fixed {len(fixes)} file(s):")
        for rel, host_count, fields in fixes:
            detail = []
            if host_count:
                detail.append(f"{host_count} host ref(s) unified to non-www")
            if fields:
                detail.append("schema: " + ", ".join(fields))
            print(f"  + {rel} ({'; '.join(detail)})")
    else:
        print("No changes needed — schema complete, hosts unified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
