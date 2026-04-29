#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO PULSE HUB — Amazon AI Fetcher v2.1
يجلب منتجات من أمازون بذكاء اصطناعي
يستخدم OpenAI GPT-4.1-mini
"""

import os
import json
import requests
import time
import logging
import random
from datetime import datetime
from typing import List, Dict, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ─────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
log = logging.getLogger("amazon_ai_fetcher")


# ─────────────────────────────────────────────────────────────
# AI Helper
# ─────────────────────────────────────────────────────────────

def call_ai(prompt: str, temperature: float = 0.6, max_tokens: int = 2000) -> str:
    """استدعاء OpenAI API (gpt-4.1-mini)"""
    try:
        from openai import OpenAI
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        log.error(f"❌ AI call error: {e}")
        return ""


def call_ai_json(prompt: str) -> Optional[Dict]:
    result = call_ai(prompt + "\nارجع JSON فقط.")
    try:
        import re
        clean = re.sub(r'```json|```', '', result).strip()
        return json.loads(clean)
    except:
        return None


# ─────────────────────────────────────────────────────────────
# Main Logic
# ─────────────────────────────────────────────────────────────

def fetch_all_categories(products_per_category: int = 2) -> List[Dict]:
    categories = ["smartwatch", "earbuds", "smart-home"]
    all_products = []
    
    for cat in categories:
        log.info(f"🔍 Fetching for category: {cat}")
        prompt = f"أعطني بيانات {products_per_category} منتجات شهيرة في أمازون لفئة {cat}. ارجع JSON array يحتوي على (name_ar, name_en, price, rating, reviews, description_ar, description_en)."
        
        results = call_ai_json(prompt)
        if results and isinstance(results, list):
            for item in results:
                product = {
                    "id": f"AI-{int(time.time())}-{random.randint(100,999)}",
                    "name": {"ar": item.get("name_ar", ""), "en": item.get("name_en", "")},
                    "price": item.get("price", 99),
                    "rating": item.get("rating", 4.5),
                    "category": cat,
                    "image": f"https://source.unsplash.com/600x400/?{cat}",
                    "affiliate_amazon": f"https://www.amazon.com/s?k={item.get('name_en', '').replace(' ', '+')}"
                }
                all_products.append(product)
                log.info(f"✅ Added: {product['name']['ar']}")
    
    return all_products


if __name__ == "__main__":
    log.info("🚀 Starting Amazon AI Fetcher...")
    products = fetch_all_categories(2)
    output_file = "/home/ubuntu/neo-pulse-hub/amazon_ai_products.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    log.info(f"✅ Saved {len(products)} products")
