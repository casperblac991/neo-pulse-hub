#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Central AI facade for NEO PULSE HUB.

كل أجزاء المنصة التي تحتاج AI يجب أن تمر عبر هذا الملف بدلاً من استدعاء
مزود أو سكربت منفصل مباشرة. هذا يقلل الازدواجية ويحافظ على مصدر كتالوج واحد.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from .ai_engine import (
        answer_customer,
        analyze_sentiment,
        categorize_query,
        continue_conversation,
        extract_budget,
        generate_marketing_post,
        generate_product_description,
        is_purchase_intent,
        recommend_products_with_reason,
    )
except ImportError:  # تشغيل الملف مباشرة من backend/
    from ai_engine import (
        answer_customer,
        analyze_sentiment,
        categorize_query,
        continue_conversation,
        extract_budget,
        generate_marketing_post,
        generate_product_description,
        is_purchase_intent,
        recommend_products_with_reason,
    )

log = logging.getLogger("ai_orchestrator")
ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "products.json"


def load_catalog() -> List[Dict[str, Any]]:
    """Load the canonical catalog and return an empty list on invalid data."""
    try:
        data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("catalog must be a list")
        return [item for item in data if isinstance(item, dict) and item.get("id")]
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        log.error("Unable to load canonical catalog: %s", exc)
        return []


def catalog_context(products: Optional[List[Dict[str, Any]]] = None, limit: int = 40) -> str:
    products = products if products is not None else load_catalog()
    lines = []
    for product in products[: max(1, min(limit, 100))]:
        name = product.get("name", {})
        if isinstance(name, dict):
            name = name.get("ar") or name.get("en") or "منتج"
        lines.append(
            f"ID:{product.get('id')} | {name} | ${product.get('price', 'غير محدد')} | "
            f"{product.get('category', 'غير محدد')} | تقييم:{product.get('rating', 'غير محدد')}"
        )
    return "\n".join(lines)


def customer_reply(
    question: str,
    *,
    history: str = "",
    faqs: str = "",
    products: Optional[List[Dict[str, Any]]] = None,
) -> str:
    return answer_customer(
        question,
        products_context=catalog_context(products),
        faqs_context=faqs,
        user_history=history,
    )


def recommend(
    query: str,
    *,
    budget: Optional[float] = None,
    preferences: Optional[List[str]] = None,
    products: Optional[List[Dict[str, Any]]] = None,
) -> Tuple[List[str], str, str]:
    catalog = products if products is not None else load_catalog()
    return recommend_products_with_reason(query, catalog, budget, preferences)


def classify_message(text: str) -> Dict[str, Any]:
    return {
        "sentiment": analyze_sentiment(text),
        "purchase_intent": is_purchase_intent(text),
        "category": categorize_query(text),
        "budget": extract_budget(text),
    }


__all__ = [
    "load_catalog",
    "catalog_context",
    "customer_reply",
    "recommend",
    "classify_message",
    "continue_conversation",
    "generate_marketing_post",
    "generate_product_description",
]
