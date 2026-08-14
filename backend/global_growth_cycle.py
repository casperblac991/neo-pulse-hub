# -*- coding: utf-8 -*-
"""
NEO PULSE HUB — Global Growth Cycle
دورة نمو آمنة تعمل كل 6 ساعات عبر GitHub Actions.

المبدأ:
- تنفذ عمليات تدقيق وتوليد محلية قابلة لإعادة التشغيل.
- تستخدم Manus API للتحليل والتوصيات المنظمة.
- لا تنشر إعلانات أو رسائل مدفوعة تلقائياً؛ تحفظ مسودات تحتاج مراجعة أو موصلات معتمدة.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
REPORTS_DIR = ROOT / "docs" / "reports" / "growth"
PRODUCTS_FILE = ROOT / "products.json"
STATE_FILE = DATA_DIR / "manus_growth_tasks.json"
CAMPAIGNS_FILE = DATA_DIR / "six_hour_campaigns.json"
AUDIT_FILE = REPORTS_DIR / "latest_catalog_audit.json"

MANUS_API_KEY = os.getenv("MANUS_API_KEY", "").strip()
MANUS_BASE_URL = "https://api.manus.ai"
MAX_PENDING_TASKS = 1
POLL_SECONDS = 10
POLL_ATTEMPTS = 6

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
log = logging.getLogger("global_growth_cycle")


def read_json(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        log.warning("Could not read %s: %s", path, exc)
    return default


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def product_name(product: dict[str, Any]) -> str:
    name = product.get("name", {})
    if isinstance(name, dict):
        return str(name.get("ar") or name.get("en") or product.get("id", "منتج"))
    return str(name or product.get("id", "منتج"))


def image_key(value: Any) -> str:
    return str(value or "").strip().split("?", 1)[0]


def catalog_snapshot(products: list[dict[str, Any]]) -> dict[str, Any]:
    image_values = [image_key(p.get("image")) for p in products if p.get("image")]
    duplicate_counts = Counter(image_values)
    duplicate_images = [url for url, count in duplicate_counts.items() if count > 1]
    duplicate_product_count = sum(count - 1 for count in duplicate_counts.values() if count > 1)
    missing_images = [str(p.get("id", "")) for p in products if not p.get("image")]
    categories = Counter(str(p.get("category", "other")) for p in products)
    top_products = sorted(
        products,
        key=lambda p: (float(p.get("rating", 0) or 0), float(p.get("reviews", 0) or 0)),
        reverse=True,
    )[:8]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "product_count": len(products),
        "unique_image_count": len(set(image_values)),
        "duplicate_image_url_count": len(duplicate_images),
        "duplicate_product_count": duplicate_product_count,
        "duplicate_images": duplicate_images[:20],
        "missing_image_product_ids": missing_images[:50],
        "categories": dict(categories),
        "top_products": [
            {
                "id": p.get("id", ""),
                "name": product_name(p),
                "price_usd": p.get("price", 0),
                "rating": p.get("rating", 0),
                "category": p.get("category", "other"),
            }
            for p in top_products
        ],
    }


def build_campaign_drafts(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """إنشاء مسودات بالعربية والإنجليزية دون نشر خارجي تلقائي."""
    selected = sorted(
        products,
        key=lambda p: (float(p.get("rating", 0) or 0), float(p.get("reviews", 0) or 0)),
        reverse=True,
    )[:3]
    generated_at = datetime.now(timezone.utc).isoformat()
    drafts: list[dict[str, Any]] = []
    for product in selected:
        name_ar = str(product.get("name", {}).get("ar", product_name(product)))
        name_en = str(product.get("name", {}).get("en", name_ar))
        price = product.get("price", 0)
        product_id = str(product.get("id", ""))
        url = f"https://neo-pulse-hub.it.com/product-detail.html?id={product_id}"
        drafts.append(
            {
                "generated_at": generated_at,
                "product_id": product_id,
                "product_name_ar": name_ar,
                "product_name_en": name_en,
                "channels": {
                    "instagram": f"اكتشف {name_ar} بتجربة تقنية أذكى. السعر يبدأ من ${price}. التفاصيل: {url} #تقنية #تسوق",
                    "tiktok": f"هل تبحث عن ترقية ذكية؟ {name_ar} بسعر ${price}. شاهد التفاصيل عبر الرابط في الملف الشخصي.",
                    "telegram": f"🛍️ {name_ar}\nالسعر: ${price}\nالتفاصيل: {url}",
                    "email_subject_ar": f"اختيارنا الذكي اليوم: {name_ar}",
                    "email_subject_en": f"Smart pick of the day: {name_en}",
                },
                "status": "draft",
                "requires_review": True,
            }
        )
    return drafts


def manus_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "market_summary": {"type": "string"},
            "priority_actions": {"type": "array", "items": {"type": "string"}},
            "campaign_angles": {"type": "array", "items": {"type": "string"}},
            "seo_actions": {"type": "array", "items": {"type": "string"}},
            "risk_notes": {"type": "array", "items": {"type": "string"}},
        },
        "required": [
            "market_summary",
            "priority_actions",
            "campaign_angles",
            "seo_actions",
            "risk_notes",
        ],
        "additionalProperties": False,
    }


def api_headers() -> dict[str, str]:
    return {"x-manus-api-key": MANUS_API_KEY, "Content-Type": "application/json"}


def create_manus_task(snapshot: dict[str, Any]) -> str | None:
    if not MANUS_API_KEY:
        log.info("MANUS_API_KEY is not set; local cycle will continue.")
        return None
    prompt = (
        "أنت مستشار نمو لمنصة تجارة إلكترونية تقنية عالمية. "
        "حلل ملخص الكتالوج التالي، ثم اقترح أولويات تسويق ومحتوى وتحسين SEO "
        "للدورة القادمة. لا تنفذ شراء إعلانات، ولا ترسل رسائل، ولا تعدل مستودعاً. "
        "أعد توصيات عملية آمنة فقط، وباللغة العربية.\n\n"
        + json.dumps(snapshot, ensure_ascii=False)
    )
    payload = {"message": {"content": prompt}, "structured_output_schema": manus_schema()}
    try:
        response = requests.post(
            f"{MANUS_BASE_URL}/v2/task.create",
            json=payload,
            headers=api_headers(),
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        task_id = data.get("task_id")
        if not task_id:
            log.warning("Manus returned no task_id: %s", data)
            return None
        log.info("Created Manus growth task %s", task_id)
        return str(task_id)
    except requests.RequestException as exc:
        log.warning("Manus task creation skipped: %s", exc)
        return None


def fetch_structured_result(task_id: str) -> dict[str, Any] | None:
    try:
        response = requests.get(
            f"{MANUS_BASE_URL}/v2/task.listMessages",
            params={"task_id": task_id, "order": "asc"},
            headers=api_headers(),
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        messages = payload.get("messages", payload.get("data", []))
        if isinstance(messages, dict):
            messages = messages.get("messages", [])
        if not isinstance(messages, list):
            return None
        for event in reversed(messages):
            if event.get("type") == "structured_output_result":
                result = event.get("structured_output_result", {})
                if result.get("success"):
                    return result.get("value")
        return None
    except requests.RequestException as exc:
        log.warning("Could not read Manus task %s: %s", task_id, exc)
        return None


def maintain_manus_tasks(snapshot: dict[str, Any]) -> dict[str, Any] | None:
    state = read_json(STATE_FILE, {"pending": [], "completed": []})
    pending = [str(x) for x in state.get("pending", []) if x]
    completed = state.get("completed", [])[-20:]

    for task_id in list(pending):
        result = fetch_structured_result(task_id)
        if result is not None:
            completed.append(
                {
                    "task_id": task_id,
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "result": result,
                }
            )
            pending.remove(task_id)
            log.info("Stored structured Manus result for %s", task_id)

    if not pending and MANUS_API_KEY:
        task_id = create_manus_task(snapshot)
        if task_id:
            pending.append(task_id)

    write_json(STATE_FILE, {"pending": pending, "completed": completed})
    if completed:
        return completed[-1]
    return None


def main() -> int:
    products = read_json(PRODUCTS_FILE, [])
    if not isinstance(products, list):
        log.error("products.json must contain a list")
        return 1

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    snapshot = catalog_snapshot(products)
    write_json(AUDIT_FILE, snapshot)

    drafts = build_campaign_drafts(products)
    campaign_state = read_json(CAMPAIGNS_FILE, [])
    if not isinstance(campaign_state, list):
        campaign_state = []
    campaign_state.append(
        {
            "cycle_at": datetime.now(timezone.utc).isoformat(),
            "drafts": drafts,
            "status": "draft_only",
        }
    )
    write_json(CAMPAIGNS_FILE, campaign_state[-30:])

    latest_manus_result = maintain_manus_tasks(snapshot)
    if latest_manus_result:
        write_json(REPORTS_DIR / "latest_manus_growth_report.json", latest_manus_result)

    log.info(
        "Cycle complete: products=%d, unique_images=%d, duplicate_products=%d, drafts=%d",
        snapshot["product_count"],
        snapshot["unique_image_count"],
        snapshot["duplicate_product_count"],
        len(drafts),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
