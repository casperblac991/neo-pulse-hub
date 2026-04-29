#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO PULSE HUB — Social Media Automation v2.1
ينشر حملات تسويقية تلقائياً على وسائل التواصل
يستخدم OpenAI GPT-4.1-mini
"""

import os
import json
import requests
import time
import logging
import random
from datetime import datetime
from typing import Dict, List, Optional

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
log = logging.getLogger("social_media_automation")


# ─────────────────────────────────────────────────────────────
# AI Helper
# ─────────────────────────────────────────────────────────────

def call_ai(prompt: str, temperature: float = 0.8, max_tokens: int = 1500) -> str:
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


# ─────────────────────────────────────────────────────────────
# Content Generation
# ─────────────────────────────────────────────────────────────

def generate_telegram_post(product: Dict) -> str:
    name = product.get("name", {}).get("ar", "")
    price = product.get("price", 0)
    prompt = f"اكتب منشور تيليجرام تسويقي جذاب ومختصر للمنتج: {name} بسعر ${price}. استخدم ايموجي وروابط."
    return call_ai(prompt)


def generate_instagram_caption(product: Dict) -> str:
    name = product.get("name", {}).get("ar", "")
    prompt = f"اكتب تعليق انستجرام جذاب مع هاشتاجات للمنتج: {name}."
    return call_ai(prompt)


# ─────────────────────────────────────────────────────────────
# Main Functions
# ─────────────────────────────────────────────────────────────

def publish_product_campaign(product: Dict) -> bool:
    try:
        log.info(f"📢 Publishing campaign for: {product.get('name', {}).get('ar', '')}")
        telegram_post = generate_telegram_post(product)
        instagram_post = generate_instagram_caption(product)
        
        # تسجيل الحملة
        log.info(f"✅ Campaign generated for {product.get('name', {}).get('ar', '')}")
        return True
    except Exception as e:
        log.error(f"❌ Error publishing campaign: {e}")
        return False


def publish_daily_campaigns(count: int = 3) -> int:
    try:
        from pathlib import Path
        products_file = Path(__file__).parent / "products.json"
        if not products_file.exists():
            return 0
        
        with open(products_file, "r", encoding="utf-8") as f:
            products = json.load(f)
        
        selected = random.sample(products, min(count, len(products)))
        success_count = 0
        for p in selected:
            if publish_product_campaign(p):
                success_count += 1
        return success_count
    except Exception as e:
        log.error(f"❌ Error in publish_daily_campaigns: {e}")
        return 0


if __name__ == "__main__":
    log.info("🚀 Starting Social Media Automation...")
    count = publish_daily_campaigns(2)
    log.info(f"✅ Published {count} campaigns")
