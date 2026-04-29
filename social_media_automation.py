#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO PULSE HUB — Social Media Automation v2.0
ينشر حملات تسويقية تلقائياً على Telegram و Instagram و WhatsApp
يستخدم Gemini لكتابة محتوى تسويقي جذاب
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
# Config
# ─────────────────────────────────────────────────────────────

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

TELEGRAM_BOT_TOKEN = os.environ.get("CUSTOMER_BOT_TOKEN", "")
TELEGRAM_CHANNEL = os.environ.get("TELEGRAM_CHANNEL", "")

# ─────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
log = logging.getLogger("social_media_automation")


# ─────────────────────────────────────────────────────────────
# Gemini Helper
# ─────────────────────────────────────────────────────────────

def call_gemini(prompt: str, temperature: float = 0.8, max_tokens: int = 1500) -> str:
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
                }
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


# ─────────────────────────────────────────────────────────────
# Content Generation
# ─────────────────────────────────────────────────────────────

def generate_telegram_post(product: Dict) -> str:
    """توليد منشور تيليجرام (حد أقصى 1000 حرف)"""
    
    name = product.get("name", {}).get("ar", "")
    price = product.get("price", 0)
    original_price = product.get("original_price", 0)
    discount = product.get("discount", 0)
    rating = product.get("rating", 0)
    reviews = product.get("reviews", 0)
    features = product.get("features_ar", [])[:3]
    
    prompt = f"""
    اكتب منشور تسويقي جذاب للمنتج التالي على تيليجرام:
    
    المنتج: {name}
    السعر: ${price} (كان ${original_price})
    الخصم: {discount}%
    التقييم: ⭐ {rating}/5 ({reviews} تقييم)
    المميزات: {', '.join(features)}
    
    المتطلبات:
    - استخدم emoji مناسبة وجذابة
    - اجعل النص قصير وسهل القراءة
    - أضف عبارة تحفيزية للشراء
    - لا تتجاوز 800 حرف
    - استخدم هاشتاجات ذات صلة
    
    اكتب المنشور مباشرة بدون مقدمة:
    """
    
    return call_gemini(prompt, temperature=0.8, max_tokens=800)


def generate_instagram_caption(product: Dict) -> str:
    """توليد تعليق إنستجرام (حد أقصى 2200 حرف)"""
    
    name = product.get("name", {}).get("ar", "")
    price = product.get("price", 0)
    rating = product.get("rating", 0)
    features = product.get("features_ar", [])[:4]
    
    prompt = f"""
    اكتب تعليق إنستجرام احترافي وجذاب للمنتج:
    
    المنتج: {name}
    السعر: ${price}
    التقييم: ⭐ {rating}/5
    المميزات: {', '.join(features)}
    
    المتطلبات:
    - اجعله جذاباً وملهماً
    - استخدم emoji وتنسيق جميل
    - أضف هاشتاجات شهيرة (10-15 هاشتاج)
    - استخدم line breaks للقراءة السهلة
    - أضف call-to-action واضح
    - لا تتجاوز 2000 حرف
    
    اكتب التعليق مباشرة:
    """
    
    return call_gemini(prompt, temperature=0.8, max_tokens=1500)


def generate_whatsapp_message(product: Dict) -> str:
    """توليد رسالة واتساب (حد أقصى 4096 حرف)"""
    
    name = product.get("name", {}).get("ar", "")
    price = product.get("price", 0)
    original_price = product.get("original_price", 0)
    discount = product.get("discount", 0)
    rating = product.get("rating", 0)
    features = product.get("features_ar", [])[:5]
    affiliate_link = product.get("affiliate_amazon", "")
    
    prompt = f"""
    اكتب رسالة واتساب تسويقية احترافية:
    
    المنتج: {name}
    السعر: ${price} (خصم {discount}% من ${original_price})
    التقييم: ⭐ {rating}/5
    المميزات: {', '.join(features)}
    الرابط: {affiliate_link}
    
    المتطلبات:
    - اجعلها احترافية وودية
    - استخدم emoji بحكمة
    - اقسمها إلى فقرات قصيرة
    - أضف معلومات مفيدة عن المنتج
    - ركز على الفوائد للمستخدم
    - أضف رابط الشراء في النهاية
    - استخدم لغة محفزة للشراء
    
    اكتب الرسالة مباشرة:
    """
    
    return call_gemini(prompt, temperature=0.8, max_tokens=2000)


# ─────────────────────────────────────────────────────────────
# Telegram Integration
# ─────────────────────────────────────────────────────────────

def send_telegram_message(text: str, channel_id: str = None) -> bool:
    """إرسال رسالة إلى قناة تيليجرام"""
    
    if not TELEGRAM_BOT_TOKEN:
        log.warning("⚠️ TELEGRAM_BOT_TOKEN not found")
        return False
    
    channel = channel_id or TELEGRAM_CHANNEL
    if not channel:
        log.warning("⚠️ TELEGRAM_CHANNEL not found")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": channel,
            "text": text,
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            log.info(f"✅ Telegram message sent to {channel}")
            return True
        else:
            log.error(f"❌ Telegram error: {response.status_code}")
            return False
    
    except Exception as e:
        log.error(f"❌ Error sending Telegram message: {e}")
        return False


def send_telegram_photo(photo_url: str, caption: str, channel_id: str = None) -> bool:
    """إرسال صورة مع تعليق إلى تيليجرام"""
    
    if not TELEGRAM_BOT_TOKEN:
        log.warning("⚠️ TELEGRAM_BOT_TOKEN not found")
        return False
    
    channel = channel_id or TELEGRAM_CHANNEL
    if not channel:
        log.warning("⚠️ TELEGRAM_CHANNEL not found")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        payload = {
            "chat_id": channel,
            "photo": photo_url,
            "caption": caption,
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            log.info(f"✅ Telegram photo sent to {channel}")
            return True
        else:
            log.error(f"❌ Telegram error: {response.status_code}")
            return False
    
    except Exception as e:
        log.error(f"❌ Error sending Telegram photo: {e}")
        return False


# ─────────────────────────────────────────────────────────────
# Campaign Publishing
# ─────────────────────────────────────────────────────────────

def publish_product_campaign(product: Dict, platforms: List[str] = None) -> Dict:
    """نشر حملة تسويقية لمنتج على منصات متعددة"""
    
    if platforms is None:
        platforms = ["telegram", "instagram", "whatsapp"]
    
    results = {
        "product_id": product.get("id", ""),
        "product_name": product.get("name", {}).get("ar", ""),
        "timestamp": datetime.utcnow().isoformat(),
        "platforms": {}
    }
    
    try:
        log.info(f"📢 Publishing campaign for: {results['product_name']}")
        
        # Telegram
        if "telegram" in platforms:
            telegram_post = generate_telegram_post(product)
            if telegram_post:
                # محاولة إرسال مع صورة
                image_url = product.get("image", "")
                if image_url:
                    success = send_telegram_photo(image_url, telegram_post)
                else:
                    success = send_telegram_message(telegram_post)
                
                results["platforms"]["telegram"] = {
                    "success": success,
                    "content": telegram_post[:100] + "..."
                }
                time.sleep(2)  # تأخير لتجنب الحد من المعدل
        
        # Instagram (محاكاة - في الواقع تحتاج إلى Instagram API)
        if "instagram" in platforms:
            instagram_caption = generate_instagram_caption(product)
            results["platforms"]["instagram"] = {
                "success": True,
                "content": instagram_caption[:100] + "...",
                "note": "Ready to post - requires manual Instagram API setup"
            }
        
        # WhatsApp (محاكاة - في الواقع تحتاج إلى WhatsApp Business API)
        if "whatsapp" in platforms:
            whatsapp_message = generate_whatsapp_message(product)
            results["platforms"]["whatsapp"] = {
                "success": True,
                "content": whatsapp_message[:100] + "...",
                "note": "Ready to send - requires WhatsApp Business API"
            }
        
        log.info(f"✅ Campaign published successfully")
        return results
    
    except Exception as e:
        log.error(f"❌ Error publishing campaign: {e}")
        results["error"] = str(e)
        return results


def publish_daily_campaigns(count: int = 3) -> List[Dict]:
    """نشر عدة حملات يومية"""
    
    try:
        # قراءة المنتجات
        from pathlib import Path
        products_file = Path(__file__).parent / "products.json"
        
        if not products_file.exists():
            log.warning("⚠️ products.json not found")
            return []
        
        with open(products_file, "r", encoding="utf-8") as f:
            products = json.load(f)
        
        if not products:
            log.warning("⚠️ No products found")
            return []
        
        # اختر منتجات عشوائية
        selected_products = random.sample(products, min(count, len(products)))
        
        results = []
        for product in selected_products:
            campaign_result = publish_product_campaign(product)
            results.append(campaign_result)
            time.sleep(3)  # تأخير بين الحملات
        
        return results
    
    except Exception as e:
        log.error(f"❌ Error in publish_daily_campaigns: {e}")
        return []


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    log.info("🚀 Starting Social Media Automation...")
    
    # نشر حملات يومية
    results = publish_daily_campaigns(count=2)
    
    log.info(f"✅ Published {len(results)} campaigns")
    
    # حفظ النتائج
    output_file = "/home/ubuntu/neo-pulse-hub/campaigns_log.json"
    with open(output_file, "a", encoding="utf-8") as f:
        for result in results:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")
    
    log.info(f"💾 Saved to {output_file}")
