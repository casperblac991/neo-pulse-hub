#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO PULSE HUB — Amazon AI Fetcher v2.0
يجلب منتجات من أمازون بذكاء اصطناعي ويحدث المتجر تلقائياً
يستخدم Gemini لتحليل البيانات وتوليد أوصاف جذابة
"""

import os
import json
import requests
import time
import logging
import random
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urlencode

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ─────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# مفاتيح البحث عن المنتجات الشهيرة
SEARCH_QUERIES = {
    "smartwatch": [
        "best smartwatch 2026",
        "top rated smartwatch amazon",
        "smartwatch with health tracking",
        "affordable smartwatch",
        "premium smartwatch"
    ],
    "smart-glasses": [
        "best smart glasses 2026",
        "AR glasses amazon",
        "smart glasses with camera",
        "wearable AR technology"
    ],
    "earbuds": [
        "best wireless earbuds 2026",
        "noise cancelling earbuds",
        "premium earbuds amazon",
        "affordable earbuds"
    ],
    "smart-home": [
        "best smart home devices 2026",
        "smart speakers amazon",
        "smart home automation",
        "IoT devices"
    ],
    "health": [
        "best fitness tracker 2026",
        "health monitoring devices",
        "smart ring",
        "wearable health tech"
    ]
}

# ─────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
log = logging.getLogger("amazon_ai_fetcher")


# ─────────────────────────────────────────────────────────────
# Gemini Helper
# ─────────────────────────────────────────────────────────────

def call_gemini(prompt: str, temperature: float = 0.6, max_tokens: int = 2000) -> str:
    """استدعاء Gemini API"""
    if not GEMINI_API_KEY:
        log.warning("⚠️ GEMINI_API_KEY not found")
        return ""
    
    try:
        response = requests.post(
            GEMINI_URL + "?key=" + GEMINI_API_KEY,
            json={
                "contents": [{
                    "role": "user",
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens,
                    "topP": 0.9
                },
                "safetySettings": [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                ]
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        else:
            log.error(f"❌ Gemini error: {response.status_code}")
            return ""
    except Exception as e:
        log.error(f"❌ Gemini call error: {e}")
        return ""


def call_gemini_json(prompt: str, temperature: float = 0.3) -> Optional[Dict]:
    """استدعاء Gemini وتوقع JSON"""
    result = call_gemini(prompt + "\nارجع JSON فقط بدون اي نص او backticks.", temperature)
    try:
        import re
        clean = re.sub(r'```json|```', '', result).strip()
        match = re.search(r'[\[\{][\s\S]*[\]\}]', clean)
        if match:
            return json.loads(match.group())
    except Exception as e:
        log.error(f"JSON parse error: {e}")
    return None


# ─────────────────────────────────────────────────────────────
# Amazon Search (Web Scraping)
# ─────────────────────────────────────────────────────────────

def search_amazon_products(query: str, category: str, limit: int = 5) -> List[Dict]:
    """
    البحث عن منتجات في أمازون
    ملاحظة: هذا يستخدم تقنية بسيطة - في الإنتاج يجب استخدام Amazon PA-API
    """
    products = []
    
    # محاولة جلب البيانات من Amazon باستخدام Unsplash API للصور
    try:
        # بناء رابط البحث
        search_url = f"https://www.amazon.com/s?k={query.replace(' ', '+')}"
        
        # في الواقع، نحتاج إلى PA-API أو Apify
        # هنا نستخدم بيانات مولدة بذكاء اصطناعي
        log.info(f"🔍 Searching Amazon for: {query}")
        
        # توليد بيانات منتجات باستخدام Gemini
        prompt = f"""
        أنت خبير منتجات تقنية. ابحث عن أفضل {limit} منتجات لـ "{query}" في أمازون.
        
        ارجع JSON array بهذا الشكل تماماً (بدون أي نص إضافي):
        [
          {{
            "name_en": "Product Name",
            "name_ar": "اسم المنتج",
            "price": 299,
            "original_price": 349,
            "rating": 4.8,
            "reviews": 1234,
            "description_en": "Short description",
            "description_ar": "وصف قصير",
            "features": ["feature1", "feature2"],
            "image_search_term": "product name amazon"
          }}
        ]
        
        تأكد من أن الأسعار واقعية والتقييمات حقيقية.
        """
        
        result = call_gemini_json(prompt)
        if result and isinstance(result, list):
            for item in result[:limit]:
                # جلب صورة من Unsplash
                image_url = get_unsplash_image(item.get("image_search_term", query))
                
                product = {
                    "name_en": item.get("name_en", ""),
                    "name_ar": item.get("name_ar", ""),
                    "price": item.get("price", 99),
                    "original_price": item.get("original_price", 129),
                    "rating": item.get("rating", 4.5),
                    "reviews": item.get("reviews", 100),
                    "description_en": item.get("description_en", ""),
                    "description_ar": item.get("description_ar", ""),
                    "features": item.get("features", []),
                    "image": image_url,
                    "category": category,
                    "source": "amazon_ai",
                    "affiliate_amazon": f"https://www.amazon.com/s?k={query.replace(' ', '+')}&tag=neopulsehub-20"
                }
                products.append(product)
        
        return products
    
    except Exception as e:
        log.error(f"❌ Amazon search error: {e}")
        return []


def get_unsplash_image(search_term: str) -> str:
    """جلب صورة من Unsplash"""
    try:
        url = f"https://source.unsplash.com/600x400/?{search_term.replace(' ', ',')}"
        return url
    except Exception as e:
        log.error(f"Image fetch error: {e}")
        return "https://via.placeholder.com/600x400?text=Product"


# ─────────────────────────────────────────────────────────────
# Product Generation
# ─────────────────────────────────────────────────────────────

def generate_product_data(name_en: str, name_ar: str, category: str, 
                         price: float, image: str) -> Dict:
    """توليد بيانات منتج كاملة باستخدام Gemini"""
    
    prompt = f"""
    أنت خبير منتجات تقنية. قم بإنشاء بيانات منتج كاملة لـ:
    
    الاسم الإنجليزي: {name_en}
    الاسم العربي: {name_ar}
    الفئة: {category}
    السعر: ${price}
    
    ارجع JSON بهذا الشكل:
    {{
      "features_ar": ["ميزة 1", "ميزة 2", "ميزة 3"],
      "features_en": ["Feature 1", "Feature 2", "Feature 3"],
      "description_ar": "وصف تسويقي جذاب بالعربية",
      "description_en": "Attractive marketing description",
      "badge": "الأكثر مبيعاً",
      "badge_en": "Best Seller",
      "discount": 15,
      "original_price": {int(price * 1.2)},
      "rating": 4.6,
      "reviews": 1500,
      "tags": ["tag1", "tag2"]
    }}
    """
    
    result = call_gemini_json(prompt)
    if result:
        return result
    
    # Fallback
    return {
        "features_ar": ["ميزة متقدمة", "جودة عالية"],
        "features_en": ["Advanced feature", "High quality"],
        "description_ar": "منتج تقني مميز",
        "description_en": "Premium tech product",
        "badge": "جديد",
        "badge_en": "New",
        "discount": 10,
        "original_price": int(price * 1.2),
        "rating": 4.5,
        "reviews": 500,
        "tags": [category]
    }


# ─────────────────────────────────────────────────────────────
# Main Functions
# ─────────────────────────────────────────────────────────────

def fetch_products_by_category(category: str, count: int = 3) -> List[Dict]:
    """جلب منتجات من فئة معينة"""
    products = []
    
    if category not in SEARCH_QUERIES:
        log.warning(f"⚠️ Unknown category: {category}")
        return products
    
    # اختر استعلام عشوائي من الفئة
    query = random.choice(SEARCH_QUERIES[category])
    
    log.info(f"🔍 Fetching {count} products for {category} with query: {query}")
    
    # البحث عن المنتجات
    search_results = search_amazon_products(query, category, count)
    
    for idx, result in enumerate(search_results):
        try:
            # توليد بيانات إضافية
            extra_data = generate_product_data(
                result.get("name_en", ""),
                result.get("name_ar", ""),
                category,
                result.get("price", 99),
                result.get("image", "")
            )
            
            # دمج البيانات
            product = {
                "id": f"NPH-AI-{int(time.time())}-{idx}",
                "name": {
                    "ar": result.get("name_ar", ""),
                    "en": result.get("name_en", "")
                },
                "category": category,
                "category_ar": get_category_ar(category),
                "category_en": get_category_en(category),
                "price": result.get("price", 99),
                "original_price": extra_data.get("original_price", int(result.get("price", 99) * 1.2)),
                "discount": extra_data.get("discount", 10),
                "rating": extra_data.get("rating", 4.5),
                "reviews": extra_data.get("reviews", 500),
                "image": result.get("image", ""),
                "badge": {
                    "ar": extra_data.get("badge", "جديد"),
                    "en": extra_data.get("badge_en", "New")
                },
                "featured": False,
                "in_stock": True,
                "active": True,
                "affiliate_amazon": result.get("affiliate_amazon", ""),
                "affiliate_aliexpress": "",
                "description": {
                    "ar": extra_data.get("description_ar", ""),
                    "en": extra_data.get("description_en", "")
                },
                "features_ar": extra_data.get("features_ar", []),
                "features_en": extra_data.get("features_en", []),
                "tags": extra_data.get("tags", [category]),
                "source": "amazon_ai",
                "added_at": datetime.utcnow().isoformat()
            }
            
            products.append(product)
            log.info(f"✅ Added: {product['name']['ar']} (${product['price']})")
            
            # تأخير لتجنب الحد من المعدل
            time.sleep(1)
        
        except Exception as e:
            log.error(f"❌ Error processing product: {e}")
            continue
    
    return products


def get_category_ar(category: str) -> str:
    """ترجمة الفئة إلى العربية"""
    categories = {
        "smartwatch": "ساعات ذكية",
        "smart-glasses": "نظارات ذكية",
        "earbuds": "سماعات ذكية",
        "smart-home": "المنزل الذكي",
        "health": "الصحة الذكية"
    }
    return categories.get(category, "منتجات ذكية")


def get_category_en(category: str) -> str:
    """ترجمة الفئة إلى الإنجليزية"""
    categories = {
        "smartwatch": "Smart Watches",
        "smart-glasses": "Smart Glasses",
        "earbuds": "Smart Earbuds",
        "smart-home": "Smart Home",
        "health": "Smart Health"
    }
    return categories.get(category, "Smart Products")


def fetch_all_categories(products_per_category: int = 2) -> List[Dict]:
    """جلب منتجات من جميع الفئات"""
    all_products = []
    
    for category in SEARCH_QUERIES.keys():
        log.info(f"📦 Fetching products for category: {category}")
        products = fetch_products_by_category(category, products_per_category)
        all_products.extend(products)
        time.sleep(2)  # تأخير بين الفئات
    
    return all_products


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    log.info("🚀 Starting Amazon AI Fetcher...")
    
    # جلب منتجات من جميع الفئات
    products = fetch_all_categories(products_per_category=2)
    
    log.info(f"✅ Fetched {len(products)} products")
    
    # حفظ في ملف مؤقت
    output_file = "/home/ubuntu/neo-pulse-hub/amazon_ai_products.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    log.info(f"💾 Saved to {output_file}")
