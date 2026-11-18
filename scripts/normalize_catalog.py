#!/usr/bin/env python3
"""Normalize the public product catalog without inventing commercial data.

Usage:
  python3 scripts/normalize_catalog.py --check
  python3 scripts/normalize_catalog.py --write
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "products.json"
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
    product["affiliate_aliexpress"] = text(product.get("affiliate_aliexpress"))
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


def run_helper_script(name: str, required: bool = False) -> int:
    """Run a deploy-time helper script (affiliate fill, image fixes, disclosure injection)."""
    script = ROOT / "scripts" / name
    if not script.exists():
        print(f"{name} not found — skipping")
        return 0 if not required else 1

    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.stdout:
        print(result.stdout.strip())
    if result.returncode != 0:
        print(result.stderr.strip(), file=sys.stderr)
    return result.returncode


def run_flag_script(name: str) -> int:
    """Run a helper script that takes --write."""
    script = ROOT / "scripts" / name
    if not script.exists():
        print(f"{name} not found — skipping")
        return 0
    result = subprocess.run(
        [sys.executable, str(script), "--write"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.stdout:
        print(result.stdout.strip())
    if result.returncode != 0:
        print(result.stderr.strip(), file=sys.stderr)
    return result.returncode


def run_cta_fixer() -> int:
    """Rewrite legacy dead blog CTAs (products.html?id=NPH-*) into direct
    Amazon/AliExpress affiliate links. Idempotent — safe on every deploy."""
    return run_flag_script("fix_blog_ctas.py")


def run_domain_fixer() -> int:
    """Replace every legacy-domain reference (neo-pulse-hub.it.com without .it)
    with the live domain across all text files. Idempotent — safe on every
    deploy; keeps new generated articles and canonicals pointing at the
    domain we own."""
    return run_flag_script("fix_old_domain.py")


def run_schema_fixer() -> int:
    """Enrich Product JSON-LD (image, url, availability, aggregateRating,
    offer url) from the canonical catalog so Google's merchant checks pass,
    and unify hosts (legacy + www -> non-www live host). Idempotent."""
    return run_flag_script("fix_schema_markup.py")


def run_price_comparison() -> int:
    """Generate price-comparison.json (amazon vs aliexpress best-price data)
    so product pages and seasonal campaigns can render live comparisons."""
    script = ROOT / "scripts" / "build_price_comparison.py"
    if not script.exists():
        print("build_price_comparison.py not found — skipping")
        return 0
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.stdout:
        print(result.stdout.strip())
    if result.returncode != 0:
        print(result.stderr.strip(), file=sys.stderr)
    return result.returncode


def run_internal_links() -> int:
    """Inject related-articles blocks + FAQ schema into every blog article.
    Idempotent — re-running replaces previous blocks instead of stacking."""
    return run_flag_script("auto_internal_links.py")


def run_sitemap_generator() -> int:
    """Regenerate sitemap.xml from the repository's actual pages — runs LAST
    so it captures every change made earlier in the pipeline."""
    return run_flag_script("generate_sitemap.py")


def commit_generated_changes_in_ci() -> bool:
    """In GitHub Actions (--write mode), commit and push ALL generated changes
    (products.json + rewritten blog articles + injected assets + sitemap) so
    nothing is silently dropped by the workflow's narrower `git add products.json`.

    The workflow's own commit step then finds a clean tree and skips its push,
    avoiding duplicate commits or push races. Local runs (no GITHUB_ACTIONS)
    are never touched — this only acts inside CI.
    """
    if os.environ.get("GITHUB_ACTIONS") != "true":
        return False

    def git(*args: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)

    status = git("status", "--porcelain")
    if status.returncode != 0 or not status.stdout.strip():
        return False

    if git("config", "user.email").returncode != 0:
        git("config", "user.email", "action@github.com")
    if git("config", "user.name").returncode != 0:
        git("config", "user.name", "GitHub Action")

    git("add", "-A")
    staged = git("diff", "--staged", "--quiet")
    if staged.returncode == 0:
        return False

    commit = git(
        "commit",
        "-m",
        "chore: sync catalog + blog enrichment + sitemap [skip ci]",
    )
    if commit.returncode != 0:
        print(commit.stderr.strip(), file=sys.stderr)
        return False

    push = git("push", "origin", "HEAD:main")
    if push.returncode != 0:
        # Remote moved while we ran (another workflow pushed first):
        # rebase our commit on top and retry once.
        git("pull", "--rebase", "origin", "main")
        retry = git("push", "origin", "HEAD:main")
        if retry.returncode != 0:
            print(retry.stderr.strip(), file=sys.stderr)
            return False
    print("Committed and pushed generated changes (catalog + blog + sitemap).")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if not args.check and not args.write:
        parser.error("choose --check or --write")

    # Deploy-time affiliate compliance: fill AliExpress links FIRST so the
    # catalog is fully monetized before normalization and HTML injection.
    run_helper_script("fill_aliexpress_links.py")

    # Deploy-time compliance: inject affiliate disclosure + tracker into all pages.
    run_helper_script("inject_affiliate_assets.py")

    # Deploy-time image hygiene: unique real photos per product (no duplicates).
    run_helper_script("fix_product_images.py")

    # Deploy-time monetization: rewrite dead blog buy-buttons into direct
    # Amazon/AliExpress affiliate links (idempotent, guards revenue path).
    run_cta_fixer()

    # Deploy-time SEO: replace legacy domain references with the live domain
    # (canonicals, generator templates, JSON-LD) so Google indexes what we own.
    run_domain_fixer()

    # Deploy-time rich results: enrich Product JSON-LD with merchant-critical
    # fields (image, url, availability, aggregateRating) and unify hosts so
    # Google's "merchant data" checks pass and product snippets go live.
    run_schema_fixer()

    # Deploy-time conversion: cross-store price comparison dataset for
    # product pages and seasonal campaign pages (black-friday etc.).
    run_price_comparison()

    # Deploy-time SEO + engagement: related-articles blocks + FAQ schema
    # across the blog (idempotent, replaces previous blocks).
    run_internal_links()

    products, stats = load_normalized()
    output = json.dumps(products, ensure_ascii=False, indent=2) + "\n"
    current = CATALOG_PATH.read_text(encoding="utf-8")
    changed = current != output
    print(json.dumps({**stats, "output": len(products), "changed": changed}, ensure_ascii=False))
    if args.write and changed:
        CATALOG_PATH.write_text(output, encoding="utf-8")
        print(f"wrote {CATALOG_PATH}")
    if args.write:
        # Sitemap LAST: captures every change made above (new pages, injected
        # blocks, updated articles) so it never goes stale.
        run_sitemap_generator()
        commit_generated_changes_in_ci()
    return 1 if args.check and changed else 0


if __name__ == "__main__":
    sys.exit(main())
