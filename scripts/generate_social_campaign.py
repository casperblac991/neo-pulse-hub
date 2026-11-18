#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 مولّد حملة التسويق الاجتماعي - Neo Pulse Hub
يولّد محتوى جاهزاً للنشر على: TikTok, Instagram, Telegram, WhatsApp, Twitter/X
"""
import json, os, random
from datetime import datetime
from pathlib import Path

TAG = "neopulsehub09-20"
SITE = "https://neo-pulse-hub.it.com"

# تحميل المنتجات
with open("products.json", "r", encoding="utf-8") as f:
    products = json.load(f)

# أفضل المنتجات (تقييم عالي + سعر جذاب)
top_products = sorted(
    [p for p in products if p.get("rating") and float(p["rating"]) >= 4.5],
    key=lambda x: float(x.get("rating", 0)),
    reverse=True
)[:20]

def get_name(p):
    n = p.get("name", {})
    if isinstance(n, dict):
        return n.get("ar") or n.get("en") or ""
    return str(n)

def get_amazon_url(p):
    asin = p.get("asin", "")
    if asin and len(asin) == 10:
        return f"https://www.amazon.com/dp/{asin}?tag={TAG}"
    name_en = p.get("name", {})
    if isinstance(name_en, dict):
        name_en = name_en.get("en", "")
    import urllib.parse
    return f"https://www.amazon.com/s?k={urllib.parse.quote_plus(str(name_en))}&tag={TAG}"

# ── محتوى المنصات ──────────────────────────────────────────────

def tiktok_script(p):
    name = get_name(p)
    price = p.get("price", "")
    rating = p.get("rating", "")
    url = get_amazon_url(p)
    return f"""🎬 سكريبت TikTok/Reels (15-30 ثانية)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[0-3 ثا] Hook — افتح بسؤال:
"هل تعرف هذا المنتج اللي غيّر حياتي؟ 🔥"

[3-10 ثا] المنتج:
"أنا اشتريت {name}
السعر: ${price} فقط! ⭐{rating}/5"

[10-20 ثا] المميزات:
"وجدته على Amazon بأفضل سعر
الرابط في البايو 👆"

[20-30 ثا] CTA:
"متابع + لايك = مزيد من العروض 🛍️"

📌 الكابشن:
{name} بـ ${price} على أمازون 🔥
⭐ {rating}/5 تقييم
🛒 رابط الشراء: {url}
#تقنية #منتجات_ذكية #أمازون #عروض
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

def instagram_post(p):
    name = get_name(p)
    price = p.get("price", "")
    rating = p.get("rating", "")
    url = get_amazon_url(p)
    return f"""📸 منشور Instagram
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ {name}

💰 السعر: ${price}
⭐ التقييم: {rating}/5
🛒 متاح على Amazon

إيش يميزه؟
✅ جودة عالية
✅ سعر منافس
✅ شحن سريع

رابط الشراء في البايو 👆
أو: {url}

—
📌 Hashtags:
#نيو_بالس_هاب #تقنية_ذكية #منتجات_أمازون
#ساعات_ذكية #تكنولوجيا #عروض_أمازون
#smart_tech #amazon_deals #gadgets
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

def telegram_post(p):
    name = get_name(p)
    price = p.get("price", "")
    rating = p.get("rating", "")
    url = get_amazon_url(p)
    site_url = f"{SITE}/products.html"
    return f"""✈️ منشور Telegram/WhatsApp
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔥 عرض اليوم من NEO PULSE HUB

🛍️ **{name}**
💰 السعر: **${price}**
⭐ التقييم: {rating}/5

🛒 اشترِ الآن على Amazon:
{url}

📦 أو تصفح كل المنتجات:
{site_url}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 نصيحة: أضف للعربة الآن قبل نفاد الكمية!"""

def twitter_thread(products_list):
    lines = ["🧵 Thread: أفضل 5 منتجات تقنية هذا الأسبوع 👇\n"]
    for i, p in enumerate(products_list[:5], 1):
        name = get_name(p)
        price = p.get("price", "")
        rating = p.get("rating", "")
        url = get_amazon_url(p)
        lines.append(f"{i}/5 — {name}\n💰 ${price} | ⭐{rating}/5\n🔗 {url}\n")
    lines.append(f"5/5 — شاهد كل المنتجات:\n{SITE}/products.html\n#تقنية #أمازون #عروض")
    return "\n".join(lines)

# ── توليد الملف الكامل ──────────────────────────────────────────

output = []
output.append("=" * 60)
output.append(f"🚀 حملة NEO PULSE HUB — {datetime.now().strftime('%Y-%m-%d')}")
output.append("=" * 60)
output.append("")

# اختيار 5 منتجات للحملة
campaign_products = random.sample(top_products, min(5, len(top_products)))

output.append("📋 منتجات الحملة:")
for p in campaign_products:
    output.append(f"  • {get_name(p)} — ${p.get('price','')} — ⭐{p.get('rating','')}")
output.append("")

# TikTok
output.append("\n" + "🎬 " * 20)
output.append("TikTok / Instagram Reels / YouTube Shorts")
output.append("🎬 " * 20)
for p in campaign_products[:3]:
    output.append(tiktok_script(p))
    output.append("")

# Instagram
output.append("\n" + "📸 " * 20)
output.append("Instagram / Facebook Posts")
output.append("📸 " * 20)
for p in campaign_products[:3]:
    output.append(instagram_post(p))
    output.append("")

# Telegram/WhatsApp
output.append("\n" + "✈️ " * 20)
output.append("Telegram / WhatsApp Broadcast")
output.append("✈️ " * 20)
for p in campaign_products:
    output.append(telegram_post(p))
    output.append("")

# Twitter Thread
output.append("\n" + "🐦 " * 20)
output.append("Twitter/X Thread")
output.append("🐦 " * 20)
output.append(twitter_thread(campaign_products))

# حفظ الملف
out_path = Path("campaigns")
out_path.mkdir(exist_ok=True)
fname = out_path / f"campaign_{datetime.now().strftime('%Y%m%d')}.txt"
with open(fname, "w", encoding="utf-8") as f:
    f.write("\n".join(output))

print(f"✅ Campaign generated: {fname}")
print(f"📊 {len(campaign_products)} products | {len(output)} lines")
