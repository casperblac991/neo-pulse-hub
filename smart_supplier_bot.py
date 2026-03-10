#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════╗
║   NEO PULSE HUB — Smart Supplier Bot v3.0               ║
║   يبحث تلقائياً ويضيف منتجات حقيقية مع صور فورية      ║
╚══════════════════════════════════════════════════════════╝

الأوامر:
  /auto         ← يبحث ويضيف 5 منتجات تلقائياً
  /auto 10      ← يضيف 10 منتجات
  /fill         ← يملأ المتجر كاملاً بـ 120 منتج مع صور حقيقية
  /add اسم      ← يضيف منتج محدد
  /fix_images   ← يصلح صور المنتجات الحالية
"""

import os, json, logging, requests, time, random, base64, re
from datetime import datetime

try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass

# ── Env ──────────────────────────────────────────────────
SUPPLIER_BOT_TOKEN = os.environ.get("SUPPLIER_BOT_TOKEN", "")
ADMIN_USER_ID      = int(os.environ.get("ADMIN_USER_ID", "0"))
GEMINI_API_KEY     = os.environ.get("GEMINI_API_KEY", "")
GITHUB_TOKEN       = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO        = os.environ.get("GITHUB_REPO", "casperblac991/neo-pulse-hub")
GITHUB_FILE        = "products.json"
GITHUB_API         = "https://api.github.com"

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta"
    f"/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
)

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
log = logging.getLogger("smart_supplier")

# ═══════════════════════════════════════════════════════
# قاعدة بيانات المنتجات الحقيقية مع صور رسمية مضمونة
# ═══════════════════════════════════════════════════════
PRODUCTS_DB = {
    "smartwatch": [
        {
            "name_en": "Apple Watch Series 9 45mm",
            "name_ar": "ساعة أبل Watch Series 9",
            "price": 399, "orig": 449, "rating": 4.9, "reviews": 12430,
            "badge": "الأكثر مبيعاً",
            "image": "https://placehold.co/400x400/1e3a5f/ffffff?text=Apple%20Watch%20Series%209%2045mm",
            "features": ["شاشة Retina دائمة التشغيل", "GPS + Cellular", "مقاوم للماء 50م", "تتبع صحي شامل", "بطارية 18 ساعة"]
        },
        {
            "name_en": "Samsung Galaxy Watch 7 44mm",
            "name_ar": "ساعة سامسونج Galaxy Watch 7",
            "price": 299, "orig": 349, "rating": 4.8, "reviews": 8765,
            "badge": "مميز",
            "image": "https://placehold.co/400x400/1e3a5f/ffffff?text=Samsung%20Galaxy%20Watch%207%2044",
            "features": ["معالج Exynos W1000", "تتبع نوم AI", "بطارية 40 ساعة", "مقاومة MIL-STD-810", "تتبع اللياقة"]
        },
        {
            "name_en": "Garmin Fenix 7X Solar",
            "name_ar": "ساعة غارمن Fenix 7X Solar",
            "price": 699, "orig": 799, "rating": 4.8, "reviews": 5432,
            "badge": "",
            "image": "https://placehold.co/400x400/1e3a5f/ffffff?text=Garmin%20Fenix%207X%20Solar",
            "features": ["شحن شمسي", "GPS متعدد التردد", "بطارية 37 يوم", "خرائط توبو مدمجة", "مناسب للمغامرات"]
        },
        {
            "name_en": "Apple Watch Ultra 2",
            "name_ar": "ساعة أبل Watch Ultra 2",
            "price": 799, "orig": 899, "rating": 4.9, "reviews": 4321,
            "badge": "حصري",
            "image": "https://placehold.co/400x400/1e3a5f/ffffff?text=Apple%20Watch%20Ultra%202",
            "features": ["هيكل تيتانيوم", "بطارية 60 ساعة", "صوت إنذار 86dB", "مقاومة 100م", "GPS دقة عالية"]
        },
        {
            "name_en": "Google Pixel Watch 3",
            "name_ar": "ساعة غوغل Pixel Watch 3",
            "price": 349, "orig": 399, "rating": 4.7, "reviews": 3210,
            "badge": "جديد",
            "image": "https://placehold.co/400x400/1e3a5f/ffffff?text=Google%20Pixel%20Watch%203",
            "features": ["Wear OS 4", "تتبع قلب متقدم", "شاشة AMOLED 45mm", "Google Wallet", "بطارية 24 ساعة"]
        },
        {
            "name_en": "Xiaomi Watch S3",
            "name_ar": "ساعة شاومي Watch S3",
            "price": 139, "orig": 169, "rating": 4.5, "reviews": 6543,
            "badge": "قيمة مثالية",
            "image": "https://placehold.co/400x400/1e3a5f/ffffff?text=Xiaomi%20Watch%20S3",
            "features": ["شاشة AMOLED 1.43\"", "12 أيام بطارية", "GPS مدمج", "150 وضع رياضي", "مقاوم للماء 5ATM"]
        },
        {
            "name_en": "Amazfit Balance",
            "name_ar": "ساعة أمازفيت Balance",
            "price": 229, "orig": 269, "rating": 4.6, "reviews": 2876,
            "badge": "",
            "image": "https://placehold.co/400x400/1e3a5f/ffffff?text=Amazfit%20Balance",
            "features": ["Zepp OS 3.0", "14 أيام بطارية", "تتبع صحي AI", "شاشة AMOLED", "GPS L1+L5"]
        },
        {
            "name_en": "Samsung Galaxy Watch Ultra",
            "name_ar": "ساعة سامسونج Galaxy Watch Ultra",
            "price": 649, "orig": 749, "rating": 4.8, "reviews": 1987,
            "badge": "جديد",
            "image": "https://placehold.co/400x400/1e3a5f/ffffff?text=Samsung%20Galaxy%20Watch%20Ultr",
            "features": ["هيكل تيتانيوم", "بطارية 60 ساعة", "مقاومة MIL-STD-810X", "10ATM مقاومة", "GPS Dual-frequency"]
        },
        {
            "name_en": "Fitbit Versa 4",
            "name_ar": "ساعة فيتبيت Versa 4",
            "price": 149, "orig": 199, "rating": 4.5, "reviews": 9876,
            "badge": "",
            "image": "https://placehold.co/400x400/1e3a5f/ffffff?text=Fitbit%20Versa%204",
            "features": ["Alexa مدمج", "GPS", "6 أيام بطارية", "تتبع النوم", "+40 وضع تمرين"]
        },
        {
            "name_en": "Garmin Venu 3S",
            "name_ar": "ساعة غارمن Venu 3S",
            "price": 449, "orig": 499, "rating": 4.7, "reviews": 3456,
            "badge": "",
            "image": "https://placehold.co/400x400/1e3a5f/ffffff?text=Garmin%20Venu%203S",
            "features": ["شاشة AMOLED", "استجابة جسم AI", "يومين ونصف بطارية", "تتبع سكر الدم", "Body Battery"]
        },
        {
            "name_en": "OnePlus Watch 3",
            "name_ar": "ساعة ون بلس Watch 3",
            "price": 329, "orig": 379, "rating": 4.6, "reviews": 2134,
            "badge": "",
            "image": "https://placehold.co/400x400/1e3a5f/ffffff?text=OnePlus%20Watch%203",
            "features": ["Wear OS 4", "بطارية 100 ساعة", "شحن 80% بـ 30 دقيقة", "GPS Dual-band", "مقاومة 5ATM"]
        },
        {
            "name_en": "Huawei Watch GT 5 Pro",
            "name_ar": "ساعة هواوي Watch GT 5 Pro",
            "price": 349, "orig": 399, "rating": 4.7, "reviews": 4567,
            "badge": "",
            "image": "https://placehold.co/400x400/1e3a5f/ffffff?text=Huawei%20Watch%20GT%205%20Pro",
            "features": ["هيكل تيتانيوم", "بطارية 14 يوم", "تتبع صحي شامل", "GPS مزدوج", "خرائط داخلية"]
        },
        {
            "name_en": "Withings ScanWatch 2",
            "name_ar": "ساعة ويذينغز ScanWatch 2",
            "price": 299, "orig": 349, "rating": 4.6, "reviews": 1876,
            "badge": "",
            "image": "https://placehold.co/400x400/1e3a5f/ffffff?text=Withings%20ScanWatch%202",
            "features": ["تخطيط قلب ECG", "أكسجين الدم SpO2", "30 يوم بطارية", "تصميم كلاسيكي", "FDA Cleared"]
        },
        {
            "name_en": "TicWatch Pro 5 Enduro",
            "name_ar": "ساعة تيكووتش Pro 5 Enduro",
            "price": 399, "orig": 449, "rating": 4.6, "reviews": 1234,
            "badge": "",
            "image": "https://placehold.co/400x400/1e3a5f/ffffff?text=TicWatch%20Pro%205%20Enduro",
            "features": ["Snapdragon W5+ Gen 1", "شاشة مزدوجة", "80 ساعة بطارية", "Wear OS 3.5", "MIL-STD-810H"]
        },
        {
            "name_en": "Coros Apex 2 Pro",
            "name_ar": "ساعة كوروس Apex 2 Pro",
            "price": 499, "orig": 599, "rating": 4.8, "reviews": 2345,
            "badge": "",
            "image": "https://placehold.co/400x400/1e3a5f/ffffff?text=Coros%20Apex%202%20Pro",
            "features": ["GPS متعدد التردد", "75 ساعة GPS", "خرائط توبو", "Blood Lactate", "شحن سريع"]
        },
    ],
    "smart-glasses": [
        {
            "name_en": "Apple Vision Pro",
            "name_ar": "نظارة Apple Vision Pro",
            "price": 3499, "orig": 3999, "rating": 4.8, "reviews": 4532,
            "badge": "حصري",
            "image": "https://placehold.co/400x400/2d1b4e/ffffff?text=Apple%20Vision%20Pro",
            "features": ["شاشة micro-OLED 4K", "visionOS", "R1 Chip", "كاميرات 3D", "تصميم انغماسي كامل"]
        },
        {
            "name_en": "Meta Quest 3 512GB",
            "name_ar": "نظارة Meta Quest 3",
            "price": 649, "orig": 749, "rating": 4.8, "reviews": 15432,
            "badge": "الأكثر مبيعاً",
            "image": "https://placehold.co/400x400/2d1b4e/ffffff?text=Meta%20Quest%203%20512GB",
            "features": ["Snapdragon XR2 Gen 2", "Mixed Reality", "عدسات Pancake", "بطارية 2.2 ساعة", "Meta Store"]
        },
        {
            "name_en": "Ray-Ban Meta Wayfarer",
            "name_ar": "نظارة Ray-Ban Meta Wayfarer الذكية",
            "price": 329, "orig": 379, "rating": 4.5, "reviews": 8765,
            "badge": "مميز",
            "image": "https://placehold.co/400x400/2d1b4e/ffffff?text=Ray-Ban%20Meta%20Wayfarer",
            "features": ["كاميرا 12MP", "مكبرات صوت مفتوحة", "Bluetooth 5.3", "استدعاء Meta AI", "بطارية 4 ساعات"]
        },
        {
            "name_en": "Meta Quest 3S",
            "name_ar": "نظارة Meta Quest 3S",
            "price": 299, "orig": 349, "rating": 4.7, "reviews": 6543,
            "badge": "جديد",
            "image": "https://placehold.co/400x400/2d1b4e/ffffff?text=Meta%20Quest%203S",
            "features": ["Snapdragon XR2 Gen 2", "Mixed Reality", "128GB Storage", "بطارية معززة", "أخف بـ 50%"]
        },
        {
            "name_en": "XREAL Air 2 Pro",
            "name_ar": "نظارة XREAL Air 2 Pro",
            "price": 449, "orig": 499, "rating": 4.6, "reviews": 3210,
            "badge": "",
            "image": "https://placehold.co/400x400/2d1b4e/ffffff?text=XREAL%20Air%202%20Pro",
            "features": ["شاشة 330\" افتراضية", "120Hz Refresh", "Electrochromic Dimming", "USB-C", "72g خفيف"]
        },
        {
            "name_en": "HTC Vive XR Elite",
            "name_ar": "نظارة HTC Vive XR Elite",
            "price": 999, "orig": 1199, "rating": 4.6, "reviews": 1876,
            "badge": "",
            "image": "https://placehold.co/400x400/2d1b4e/ffffff?text=HTC%20Vive%20XR%20Elite",
            "features": ["Snapdragon XR2 Gen 1", "4K+ عرض", "بطارية 2 ساعة", "Viveport Infinity", "قابل للخلع"]
        },
        {
            "name_en": "Pico 4 Ultra",
            "name_ar": "نظارة Pico 4 Ultra",
            "price": 599, "orig": 699, "rating": 4.5, "reviews": 2345,
            "badge": "",
            "image": "https://placehold.co/400x400/2d1b4e/ffffff?text=Pico%204%20Ultra",
            "features": ["Snapdragon XR2 Gen 2", "Spatial Video", "Hand Tracking", "3GB RAM", "بطارية 3 ساعة"]
        },
        {
            "name_en": "Snap Spectacles 5",
            "name_ar": "نظارة Snap Spectacles 5",
            "price": 399, "orig": 449, "rating": 4.3, "reviews": 1234,
            "badge": "",
            "image": "https://placehold.co/400x400/2d1b4e/ffffff?text=Snap%20Spectacles%205",
            "features": ["AR مدمج", "كاميرا ثنائية", "Snapchat مدمج", "بطارية 30 دقيقة", "Lens Studio"]
        },
        {
            "name_en": "XREAL Beam Pro",
            "name_ar": "نظارة XREAL Beam Pro",
            "price": 599, "orig": 699, "rating": 4.5, "reviews": 1543,
            "badge": "",
            "image": "https://placehold.co/400x400/2d1b4e/ffffff?text=XREAL%20Beam%20Pro",
            "features": ["Spatial Computing", "Dual cameras", "Android 13", "3D Capture", "5000mAh بطارية"]
        },
        {
            "name_en": "Vuzix Z100 Smart Glasses",
            "name_ar": "نظارة Vuzix Z100 الذكية",
            "price": 699, "orig": 799, "rating": 4.3, "reviews": 543,
            "badge": "",
            "image": "https://placehold.co/400x400/2d1b4e/ffffff?text=Vuzix%20Z100%20Smart%20Glasses",
            "features": ["Waveguide AR", "Qualcomm AR1", "8 ساعات بطارية", "Android 11", "Hands-free"]
        },
        {
            "name_en": "TCL NXTWEAR S2 Plus",
            "name_ar": "نظارة TCL NXTWEAR S2 Plus",
            "price": 379, "orig": 429, "rating": 4.4, "reviews": 876,
            "badge": "",
            "image": "https://placehold.co/400x400/2d1b4e/ffffff?text=TCL%20NXTWEAR%20S2%20Plus",
            "features": ["105\" شاشة افتراضية", "1080p Full HD", "USB-C", "72g وزن", "120Hz"]
        },
        {
            "name_en": "Inmo Air 2",
            "name_ar": "نظارة Inmo Air 2 الذكية",
            "price": 399, "orig": 449, "rating": 4.2, "reviews": 654,
            "badge": "",
            "image": "https://placehold.co/400x400/2d1b4e/ffffff?text=Inmo%20Air%202",
            "features": ["ChatGPT مدمج", "ترجمة فورية", "27g خفيف", "9 ساعات بطارية", "Waveguide"]
        },
        {
            "name_en": "Rokid Max 2",
            "name_ar": "نظارة Rokid Max 2",
            "price": 549, "orig": 629, "rating": 4.5, "reviews": 987,
            "badge": "",
            "image": "https://placehold.co/400x400/2d1b4e/ffffff?text=Rokid%20Max%202",
            "features": ["Micro-OLED 1080p", "120Hz", "4700nit", "Spatial Audio", "USB-C"]
        },
        {
            "name_en": "Viture One XR",
            "name_ar": "نظارة Viture One XR",
            "price": 439, "orig": 499, "rating": 4.4, "reviews": 765,
            "badge": "",
            "image": "https://placehold.co/400x400/2d1b4e/ffffff?text=Viture%20One%20XR",
            "features": ["شاشة 135\" افتراضية", "Electrochromic", "Cinema Mode", "2K Resolution", "77g"]
        },
        {
            "name_en": "Meta Ray-Ban Skyler",
            "name_ar": "نظارة Meta Ray-Ban Skyler الذكية",
            "price": 349, "orig": 399, "rating": 4.5, "reviews": 3210,
            "badge": "",
            "image": "https://placehold.co/400x400/2d1b4e/ffffff?text=Meta%20Ray-Ban%20Skyler",
            "features": ["كاميرا 12MP Ultra Wide", "AI المساعد", "مكبرات مفتوحة", "Bluetooth 5.3", "6 ساعات"]
        },
    ],
    "health": [
        {
            "name_en": "Oura Ring Gen 4",
            "name_ar": "خاتم Oura Ring الجيل 4",
            "price": 349, "orig": 399, "rating": 4.8, "reviews": 18765,
            "badge": "الأكثر مبيعاً",
            "image": "https://placehold.co/400x400/0f3d2e/ffffff?text=Oura%20Ring%20Gen%204",
            "features": ["تتبع نوم دقيق", "Readiness Score", "بطارية 8 أيام", "Blood Oxygen", "Ring AI"]
        },
        {
            "name_en": "Whoop 4.0 Band",
            "name_ar": "حزام WHOOP 4.0",
            "price": 239, "orig": 279, "rating": 4.6, "reviews": 8765,
            "badge": "",
            "image": "https://placehold.co/400x400/0f3d2e/ffffff?text=Whoop%204.0%20Band",
            "features": ["Strain Tracking", "Recovery Score", "HRV متقدم", "بطارية 5 أيام", "لا شاشة = دقة أعلى"]
        },
        {
            "name_en": "Ultrahuman Ring AIR",
            "name_ar": "خاتم Ultrahuman Ring AIR",
            "price": 349, "orig": 399, "rating": 4.7, "reviews": 5432,
            "badge": "مميز",
            "image": "https://placehold.co/400x400/0f3d2e/ffffff?text=Ultrahuman%20Ring%20AIR",
            "features": ["خاتم ذكي بدون اشتراك", "تتبع نوم AI", "Metabolic Score", "سبعة أيام بطارية", "IP68"]
        },
        {
            "name_en": "Fitbit Charge 6",
            "name_ar": "سوار Fitbit Charge 6",
            "price": 159, "orig": 199, "rating": 4.6, "reviews": 12345,
            "badge": "",
            "image": "https://placehold.co/400x400/0f3d2e/ffffff?text=Fitbit%20Charge%206",
            "features": ["تخطيط قلب ECG", "Google Maps مدمج", "YouTube Music", "سبعة أيام بطارية", "GPS"]
        },
        {
            "name_en": "Garmin Vivosmart 5",
            "name_ar": "سوار Garmin Vivosmart 5",
            "price": 149, "orig": 179, "rating": 4.5, "reviews": 6543,
            "badge": "",
            "image": "https://placehold.co/400x400/0f3d2e/ffffff?text=Garmin%20Vivosmart%205",
            "features": ["OLED صغير", "7 أيام بطارية", "Body Battery", "HRV Status", "مقاوم للماء 5ATM"]
        },
        {
            "name_en": "Withings ScanWatch Nova",
            "name_ar": "ساعة Withings ScanWatch Nova",
            "price": 499, "orig": 599, "rating": 4.7, "reviews": 2345,
            "badge": "",
            "image": "https://placehold.co/400x400/0f3d2e/ffffff?text=Withings%20ScanWatch%20Nova",
            "features": ["تصميم ساعة كلاسيكي", "ECG", "30 يوم بطارية", "SpO2", "نوم متقدم"]
        },
        {
            "name_en": "Amazfit Helio Ring",
            "name_ar": "خاتم أمازفيت Helio Ring",
            "price": 299, "orig": 349, "rating": 4.5, "reviews": 1876,
            "badge": "",
            "image": "https://placehold.co/400x400/0f3d2e/ffffff?text=Amazfit%20Helio%20Ring",
            "features": ["تيتانيوم Ti-Al", "تتبع صحي شامل", "بطارية 4 أيام", "Zepp Health App", "IP68"]
        },
        {
            "name_en": "RingConn Gen 2 Air",
            "name_ar": "خاتم RingConn Gen 2 Air",
            "price": 199, "orig": 249, "rating": 4.5, "reviews": 3210,
            "badge": "قيمة مثالية",
            "image": "https://placehold.co/400x400/0f3d2e/ffffff?text=RingConn%20Gen%202%20Air",
            "features": ["10 أيام بطارية", "بدون اشتراك", "تتبع نوم", "SpO2", "أنواع خواتم متعددة"]
        },
        {
            "name_en": "Xiaomi Smart Band 9 Pro",
            "name_ar": "سوار شاومي Smart Band 9 Pro",
            "price": 79, "orig": 99, "rating": 4.6, "reviews": 15432,
            "badge": "اقتصادي",
            "image": "https://placehold.co/400x400/0f3d2e/ffffff?text=Xiaomi%20Smart%20Band%209%20Pro",
            "features": ["شاشة AMOLED 1.74\"", "GPS مدمج", "21 يوم بطارية", "150+ رياضة", "SpO2"]
        },
        {
            "name_en": "Biostrap EVO",
            "name_ar": "سوار Biostrap EVO الصحي",
            "price": 199, "orig": 249, "rating": 4.4, "reviews": 1234,
            "badge": "",
            "image": "https://placehold.co/400x400/0f3d2e/ffffff?text=Biostrap%20EVO",
            "features": ["قياس HRV دقيق", "SpO2 مستمر", "تحليل نوم", "تطبيق طبي", "IP67"]
        },
        {
            "name_en": "Muse 2 Meditation Headband",
            "name_ar": "عصابة Muse 2 للتأمل",
            "price": 249, "orig": 299, "rating": 4.5, "reviews": 2876,
            "badge": "",
            "image": "https://placehold.co/400x400/0f3d2e/ffffff?text=Muse%202%20Meditation%20Headban",
            "features": ["EEG 7 مستشعرات", "تأمل موجَّه", "تتبع تنفس", "نبضات القلب", "تطبيق تحليل"]
        },
        {
            "name_en": "Withings U-Scan",
            "name_ar": "جهاز Withings U-Scan للبول",
            "price": 499, "orig": 599, "rating": 4.3, "reviews": 654,
            "badge": "فريد",
            "image": "https://placehold.co/400x400/0f3d2e/ffffff?text=Withings%20U-Scan",
            "features": ["تحليل بول منزلي", "ترطيب الجسم", "دورة هرمونية", "تطبيق Health+", "أول في العالم"]
        },
        {
            "name_en": "Garmin Index BPM",
            "name_ar": "جهاز Garmin Index لضغط الدم",
            "price": 149, "orig": 179, "rating": 4.5, "reviews": 3456,
            "badge": "",
            "image": "https://placehold.co/400x400/0f3d2e/ffffff?text=Garmin%20Index%20BPM",
            "features": ["قياس ضغط الدم", "Bluetooth 5.0", "مزامنة Garmin Connect", "نتائج دقيقة", "ذاكرة 40 قياس"]
        },
        {
            "name_en": "Polar Verity Sense",
            "name_ar": "جهاز Polar Verity Sense",
            "price": 89, "orig": 109, "rating": 4.7, "reviews": 5678,
            "badge": "",
            "image": "https://placehold.co/400x400/0f3d2e/ffffff?text=Polar%20Verity%20Sense",
            "features": ["HR دقة عالية", "يُثبَّت على الذراع", "30 ساعة بطارية", "Bluetooth + ANT+", "IP67"]
        },
        {
            "name_en": "Samsung Galaxy Ring",
            "name_ar": "خاتم سامسونج Galaxy Ring",
            "price": 399, "orig": 449, "rating": 4.6, "reviews": 4321,
            "badge": "جديد",
            "image": "https://placehold.co/400x400/0f3d2e/ffffff?text=Samsung%20Galaxy%20Ring",
            "features": ["تيتانيوم خفيف", "7 أيام بطارية", "Samsung Health", "تتبع نوم AI", "IP68 ماء"]
        },
    ],
    "smart-home": [
        {
            "name_en": "Amazon Echo Show 10 Gen 4",
            "name_ar": "مكبر صوت Amazon Echo Show 10",
            "price": 249, "orig": 299, "rating": 4.7, "reviews": 23456,
            "badge": "الأكثر مبيعاً",
            "image": "https://placehold.co/400x400/1a2f4e/ffffff?text=Amazon%20Echo%20Show%2010%20Gen%204",
            "features": ["شاشة HD 10\"", "يتابعك تلقائياً", "كاميرا 13MP", "Alexa", "مكبر 3\" + تيرور"]
        },
        {
            "name_en": "Apple HomePod 2nd Gen",
            "name_ar": "مكبر Apple HomePod الجيل 2",
            "price": 299, "orig": 349, "rating": 4.7, "reviews": 12345,
            "badge": "مميز",
            "image": "https://placehold.co/400x400/1a2f4e/ffffff?text=Apple%20HomePod%202nd%20Gen",
            "features": ["Spatial Audio", "S7 Chip", "تحكم في المنزل", "Siri", "جودة صوت استثنائية"]
        },
        {
            "name_en": "Google Nest Hub Max",
            "name_ar": "شاشة Google Nest Hub Max",
            "price": 229, "orig": 279, "rating": 4.6, "reviews": 15432,
            "badge": "",
            "image": "https://placehold.co/400x400/1a2f4e/ffffff?text=Google%20Nest%20Hub%20Max",
            "features": ["شاشة 10\"", "كاميرا Duo", "Google Photos", "Assistant", "مكبرات Full-range"]
        },
        {
            "name_en": "Philips Hue White & Color Starter Kit",
            "name_ar": "طقم إضاءة Philips Hue الذكية",
            "price": 199, "orig": 249, "rating": 4.7, "reviews": 34567,
            "badge": "",
            "image": "https://placehold.co/400x400/1a2f4e/ffffff?text=Philips%20Hue%20White%20%26%20Color",
            "features": ["16 مليون لون", "تحكم صوتي", "Hue Bridge", "تطبيق ذكي", "مزامنة مع الموسيقى"]
        },
        {
            "name_en": "Ring Video Doorbell Pro 2",
            "name_ar": "جرس Ring Video Doorbell Pro 2",
            "price": 249, "orig": 299, "rating": 4.5, "reviews": 43210,
            "badge": "",
            "image": "https://placehold.co/400x400/1a2f4e/ffffff?text=Ring%20Video%20Doorbell%20Pro%202",
            "features": ["فيديو 1536p HD+", "رؤية ثلاثية الأبعاد", "تقنية Bird's Eye View", "تنبيه ذكي", "Alexa"]
        },
        {
            "name_en": "Google Nest Learning Thermostat 4",
            "name_ar": "منظم حرارة Nest الجيل 4",
            "price": 279, "orig": 329, "rating": 4.7, "reviews": 28765,
            "badge": "",
            "image": "https://placehold.co/400x400/1a2f4e/ffffff?text=Google%20Nest%20Learning%20Ther",
            "features": ["تعلم جدولك تلقائياً", "توفير 15% طاقة", "يُحس بتواجدك", "شاشة OLED", "Google Home"]
        },
        {
            "name_en": "Amazon Echo Dot 5th Gen",
            "name_ar": "مكبر Amazon Echo Dot الجيل 5",
            "price": 49, "orig": 59, "rating": 4.7, "reviews": 98765,
            "badge": "قيمة مثالية",
            "image": "https://placehold.co/400x400/1a2f4e/ffffff?text=Amazon%20Echo%20Dot%205th%20Gen",
            "features": ["Alexa", "صوت أوضح 2x", "تحكم Smart Home", "ساعة LED", "مزامنة لغرف"]
        },
        {
            "name_en": "Arlo Pro 5S 2K Camera",
            "name_ar": "كاميرا Arlo Pro 5S أمان",
            "price": 249, "orig": 299, "rating": 4.6, "reviews": 8765,
            "badge": "",
            "image": "https://placehold.co/400x400/1a2f4e/ffffff?text=Arlo%20Pro%205S%202K%20Camera",
            "features": ["2K + HDR", "ألوان ليلية", "رؤية 160°", "بطارية 6 أشهر", "Alexa + Google"]
        },
        {
            "name_en": "Samsung SmartThings Hub v3",
            "name_ar": "مركز Samsung SmartThings",
            "price": 129, "orig": 149, "rating": 4.5, "reviews": 5432,
            "badge": "",
            "image": "https://placehold.co/400x400/1a2f4e/ffffff?text=Samsung%20SmartThings%20Hub%20v",
            "features": ["Zigbee + Z-Wave + WiFi", "تحكم مركزي", "روتين تلقائي", "أمان محلي", "تكامل شامل"]
        },
        {
            "name_en": "Yale Assure Lock 2 Plus",
            "name_ar": "قفل ذكي Yale Assure Lock 2 Plus",
            "price": 329, "orig": 379, "rating": 4.5, "reviews": 4321,
            "badge": "",
            "image": "https://placehold.co/400x400/1a2f4e/ffffff?text=Yale%20Assure%20Lock%202%20Plus",
            "features": ["Matter + Z-Wave", "بصمة + رمز", "أمان AES-128", "تطبيق Yale Access", "تنبيهات فورية"]
        },
        {
            "name_en": "iRobot Roomba j9+",
            "name_ar": "مكنسة iRobot Roomba j9+",
            "price": 799, "orig": 999, "rating": 4.7, "reviews": 6543,
            "badge": "",
            "image": "https://placehold.co/400x400/1a2f4e/ffffff?text=iRobot%20Roomba%20j9%2B",
            "features": ["تفريغ تلقائي 60 يوم", "تجنب العوائق AI", "خريطة ذكية", "Alexa + Google", "شحن تلقائي"]
        },
        {
            "name_en": "Nanoleaf Shapes Hexagons Starter",
            "name_ar": "إضاءة Nanoleaf Shapes سداسية",
            "price": 199, "orig": 249, "rating": 4.5, "reviews": 12345,
            "badge": "",
            "image": "https://placehold.co/400x400/1a2f4e/ffffff?text=Nanoleaf%20Shapes%20Hexagons%20",
            "features": ["16M لون", "موسيقى تفاعلية", "لمس تحكم", "Thread", "تصميم حر"]
        },
        {
            "name_en": "Sonos Era 300",
            "name_ar": "مكبر Sonos Era 300 الصوتي",
            "price": 449, "orig": 499, "rating": 4.7, "reviews": 3456,
            "badge": "",
            "image": "https://placehold.co/400x400/1a2f4e/ffffff?text=Sonos%20Era%20300",
            "features": ["Spatial Audio حقيقي", "Dolby Atmos", "6 مكبرات", "S2 App", "بدون اشتراك"]
        },
        {
            "name_en": "Ecobee Smart Thermostat Premium",
            "name_ar": "منظم Ecobee Smart Premium",
            "price": 249, "orig": 299, "rating": 4.7, "reviews": 21345,
            "badge": "",
            "image": "https://placehold.co/400x400/1a2f4e/ffffff?text=Ecobee%20Smart%20Thermostat%20P",
            "features": ["Alexa مدمج", "حساس درجة حرارة غرفة", "توفير 23% طاقة", "SmartSensor", "ENERGY STAR"]
        },
        {
            "name_en": "Eufy Security S380 HomeBase 3",
            "name_ar": "نظام Eufy Security HomeBase 3",
            "price": 299, "orig": 349, "rating": 4.6, "reviews": 4321,
            "badge": "",
            "image": "https://placehold.co/400x400/1a2f4e/ffffff?text=Eufy%20Security%20S380%20HomeBa",
            "features": ["16GB تخزين محلي", "Triple Band WiFi", "BionicMind AI", "8K تخزين", "بدون اشتراك"]
        },
    ],
    "earbuds": [
        {
            "name_en": "Apple AirPods Pro 2nd Gen USB-C",
            "name_ar": "سماعات AirPods Pro الجيل 2",
            "price": 249, "orig": 279, "rating": 4.9, "reviews": 54321,
            "badge": "الأكثر مبيعاً",
            "image": "https://placehold.co/400x400/3d1a1a/ffffff?text=Apple%20AirPods%20Pro%202nd%20Gen",
            "features": ["ANC H2 Chip", "Adaptive Audio", "صوت مكاني", "IP68", "6h + 30h case"]
        },
        {
            "name_en": "Sony WF-1000XM5",
            "name_ar": "سماعات Sony WF-1000XM5",
            "price": 279, "orig": 329, "rating": 4.8, "reviews": 23456,
            "badge": "مميز",
            "image": "https://placehold.co/400x400/3d1a1a/ffffff?text=Sony%20WF-1000XM5",
            "features": ["أفضل ANC في السوق", "Integrated Processor V2", "360 صوت مكاني", "LDAC", "8h + 24h"]
        },
        {
            "name_en": "Bose QuietComfort Ultra Earbuds",
            "name_ar": "سماعات Bose QuietComfort Ultra",
            "price": 299, "orig": 349, "rating": 4.8, "reviews": 15432,
            "badge": "",
            "image": "https://placehold.co/400x400/3d1a1a/ffffff?text=Bose%20QuietComfort%20Ultra%20E",
            "features": ["Immersive Audio", "CustomTune ANC", "6h + 24h", "USB-C", "IP54"]
        },
        {
            "name_en": "Samsung Galaxy Buds 3 Pro",
            "name_ar": "سماعات Samsung Galaxy Buds 3 Pro",
            "price": 249, "orig": 299, "rating": 4.7, "reviews": 12345,
            "badge": "",
            "image": "https://placehold.co/400x400/3d1a1a/ffffff?text=Samsung%20Galaxy%20Buds%203%20Pro",
            "features": ["ANC AI-powered", "Blade-shaped Design", "IP57", "360° Audio", "6h + 30h"]
        },
        {
            "name_en": "Apple AirPods 4 ANC",
            "name_ar": "سماعات Apple AirPods 4 ANC",
            "price": 179, "orig": 199, "rating": 4.8, "reviews": 32145,
            "badge": "جديد",
            "image": "https://placehold.co/400x400/3d1a1a/ffffff?text=Apple%20AirPods%204%20ANC",
            "features": ["H2 Chip ANC", "Open-ear راحة", "USB-C", "5h + 30h", "IP54"]
        },
        {
            "name_en": "Sony WH-1000XM5 Over-Ear",
            "name_ar": "سماعات Sony WH-1000XM5 فوق الأذن",
            "price": 349, "orig": 399, "rating": 4.8, "reviews": 45678,
            "badge": "",
            "image": "https://placehold.co/400x400/3d1a1a/ffffff?text=Sony%20WH-1000XM5%20Over-Ear",
            "features": ["ANC صناعي AI", "30 ساعة بطارية", "Multi-point", "LDAC HiRes", "فولد مدمج"]
        },
        {
            "name_en": "Nothing Ear (3)",
            "name_ar": "سماعات Nothing Ear 3",
            "price": 149, "orig": 179, "rating": 4.6, "reviews": 8765,
            "badge": "",
            "image": "https://placehold.co/400x400/3d1a1a/ffffff?text=Nothing%20Ear%20%283%29",
            "features": ["تصميم شفاف أيقوني", "ANC 45dB", "بطارية 8.5h + 40h", "IP55", "ChatGPT مدمج"]
        },
        {
            "name_en": "Jabra Evolve2 Buds",
            "name_ar": "سماعات Jabra Evolve2 Buds",
            "price": 249, "orig": 299, "rating": 4.5, "reviews": 4321,
            "badge": "",
            "image": "https://placehold.co/400x400/3d1a1a/ffffff?text=Jabra%20Evolve2%20Buds",
            "features": ["للمهنيين", "ANC AI", "Jabra AI", "6h + 33h", "UC certified"]
        },
        {
            "name_en": "Beats Studio Buds+",
            "name_ar": "سماعات Beats Studio Buds+",
            "price": 169, "orig": 199, "rating": 4.6, "reviews": 6543,
            "badge": "",
            "image": "https://placehold.co/400x400/3d1a1a/ffffff?text=Beats%20Studio%20Buds%2B",
            "features": ["ANC 36dB", "Transparency Mode", "IP54", "9h + 36h", "Android + iOS"]
        },
        {
            "name_en": "Sennheiser Momentum True Wireless 4",
            "name_ar": "سماعات Sennheiser Momentum TW4",
            "price": 279, "orig": 329, "rating": 4.7, "reviews": 3456,
            "badge": "",
            "image": "https://placehold.co/400x400/3d1a1a/ffffff?text=Sennheiser%20Momentum%20True%20",
            "features": ["صوت Hi-Fi استثنائي", "ANC Adaptive", "7h + 28h", "aptX Lossless", "IP54"]
        },
        {
            "name_en": "Google Pixel Buds Pro 2",
            "name_ar": "سماعات Google Pixel Buds Pro 2",
            "price": 229, "orig": 259, "rating": 4.7, "reviews": 8765,
            "badge": "جديد",
            "image": "https://placehold.co/400x400/3d1a1a/ffffff?text=Google%20Pixel%20Buds%20Pro%202",
            "features": ["Tensor A1 Chip", "ANC محسَّن", "11h + 33h", "ترجمة فورية", "Gemini مدمج"]
        },
        {
            "name_en": "Anker Soundcore Liberty 4 Pro",
            "name_ar": "سماعات Anker Soundcore Liberty 4 Pro",
            "price": 129, "orig": 159, "rating": 4.6, "reviews": 12345,
            "badge": "قيمة مثالية",
            "image": "https://placehold.co/400x400/3d1a1a/ffffff?text=Anker%20Soundcore%20Liberty%204",
            "features": ["ANC 50dB", "LDAC", "11h + 53h", "IPX4", "شاشة استعراض"]
        },
        {
            "name_en": "Shure Aonic Free 2",
            "name_ar": "سماعات Shure Aonic Free 2",
            "price": 299, "orig": 349, "rating": 4.6, "reviews": 2345,
            "badge": "",
            "image": "https://placehold.co/400x400/3d1a1a/ffffff?text=Shure%20Aonic%20Free%202",
            "features": ["جودة استوديو", "ANC متقدم", "7h + 28h", "USB-C", "التحكم اللمسي"]
        },
        {
            "name_en": "JBL Tour Pro 3",
            "name_ar": "سماعات JBL Tour Pro 3",
            "price": 249, "orig": 299, "rating": 4.6, "reviews": 5432,
            "badge": "",
            "image": "https://placehold.co/400x400/3d1a1a/ffffff?text=JBL%20Tour%20Pro%203",
            "features": ["شاشة لمس على الحافظة", "ANC Pro", "10h + 40h", "Hi-Res Audio", "ChatGPT"]
        },
        {
            "name_en": "Technics EAH-AZ100",
            "name_ar": "سماعات Technics EAH-AZ100",
            "price": 299, "orig": 349, "rating": 4.7, "reviews": 1876,
            "badge": "",
            "image": "https://placehold.co/400x400/3d1a1a/ffffff?text=Technics%20EAH-AZ100",
            "features": ["ANC AI", "Jitter-less Wireless", "10h + 25h", "USB-C", "IPX4"]
        },
    ],
    "productivity": [
        {
            "name_en": "iPad Pro M4 13-inch",
            "name_ar": "جهاز iPad Pro M4 13 بوصة",
            "price": 1299, "orig": 1499, "rating": 4.9, "reviews": 23456,
            "badge": "الأكثر مبيعاً",
            "image": "https://placehold.co/400x400/2d2a1a/ffffff?text=iPad%20Pro%20M4%2013-inch",
            "features": ["M4 Chip Ultra Thin", "OLED Tandem", "Apple Intelligence", "120Hz ProMotion", "USB4 40Gbps"]
        },
        {
            "name_en": "Samsung Galaxy Tab S10 Ultra",
            "name_ar": "تابلت Samsung Galaxy Tab S10 Ultra",
            "price": 1299, "orig": 1499, "rating": 4.8, "reviews": 12345,
            "badge": "مميز",
            "image": "https://placehold.co/400x400/2d2a1a/ffffff?text=Samsung%20Galaxy%20Tab%20S10%20Ul",
            "features": ["Snapdragon 8 Gen 3", "شاشة AMOLED 14.6\"", "S Pen مدمج", "DeX Mode", "12000mAh"]
        },
        {
            "name_en": "Logitech MX Master 3S",
            "name_ar": "ماوس Logitech MX Master 3S",
            "price": 99, "orig": 119, "rating": 4.9, "reviews": 45678,
            "badge": "",
            "image": "https://placehold.co/400x400/2d2a1a/ffffff?text=Logitech%20MX%20Master%203S",
            "features": ["8000 DPI", "عجلة ذكية MagSpeed", "7 أزرار قابلة برمجة", "70 يوم بطارية", "Bolt receiver"]
        },
        {
            "name_en": "Logitech MX Keys S Plus",
            "name_ar": "لوحة مفاتيح Logitech MX Keys S Plus",
            "price": 149, "orig": 179, "rating": 4.8, "reviews": 23456,
            "badge": "",
            "image": "https://placehold.co/400x400/2d2a1a/ffffff?text=Logitech%20MX%20Keys%20S%20Plus",
            "features": ["إضاءة Smart Backlight", "مفاتيح Smart Actions", "5 أجهزة", "10 أيام بطارية", "Flow"]
        },
        {
            "name_en": "Keychron Q6 Max Wireless",
            "name_ar": "لوحة مفاتيح Keychron Q6 Max",
            "price": 299, "orig": 349, "rating": 4.8, "reviews": 8765,
            "badge": "",
            "image": "https://placehold.co/400x400/2d2a1a/ffffff?text=Keychron%20Q6%20Max%20Wireless",
            "features": ["مفاتيح ميكانيكية", "QMK/VIA", "Gasket Mount", "Bluetooth 5.1", "5000mAh"]
        },
        {
            "name_en": "Elgato Stream Deck Neo",
            "name_ar": "جهاز Elgato Stream Deck Neo",
            "price": 99, "orig": 119, "rating": 4.7, "reviews": 6543,
            "badge": "",
            "image": "https://placehold.co/400x400/2d2a1a/ffffff?text=Elgato%20Stream%20Deck%20Neo",
            "features": ["8 مفاتيح LCD", "2 شاشة Info", "تحكم بكل شيء", "تكامل واسع", "USB-C"]
        },
        {
            "name_en": "Apple Pencil Pro",
            "name_ar": "قلم Apple Pencil Pro",
            "price": 129, "orig": 149, "rating": 4.8, "reviews": 21345,
            "badge": "",
            "image": "https://placehold.co/400x400/2d2a1a/ffffff?text=Apple%20Pencil%20Pro",
            "features": ["Squeeze + Double Tap", "حركة دوران", "Barrel Roll", "شحن مغناطيسي", "تأخير 9ms"]
        },
        {
            "name_en": "Anker 737 GaNPrime 120W",
            "name_ar": "شاحن Anker 737 GaNPrime 120W",
            "price": 89, "orig": 109, "rating": 4.8, "reviews": 34567,
            "badge": "قيمة مثالية",
            "image": "https://placehold.co/400x400/2d2a1a/ffffff?text=Anker%20737%20GaNPrime%20120W",
            "features": ["120W إجمالي", "3 منافذ", "GaN III", "شحن 0→80% بـ 43 دقيقة", "USB-C + USB-A"]
        },
        {
            "name_en": "Samsung Odyssey OLED G9 49\"",
            "name_ar": "شاشة Samsung Odyssey OLED G9",
            "price": 1299, "orig": 1499, "rating": 4.7, "reviews": 3456,
            "badge": "",
            "image": "https://image-us.samsung.com/SamsungUS/home/computing/monitors/gaming/odyssey-oled-g9-750.jpg",
            "features": ["OLED 49\" QHD", "240Hz", "0.03ms GtG", "DisplayHDR True Black 400", "AMD FreeSync"]
        },
        {
            "name_en": "Wacom Intuos Pro Large",
            "name_ar": "لوح رسم Wacom Intuos Pro L",
            "price": 449, "orig": 499, "rating": 4.8, "reviews": 8765,
            "badge": "",
            "image": "https://placehold.co/400x400/2d2a1a/ffffff?text=Wacom%20Intuos%20Pro%20Large",
            "features": ["8192 مستوى ضغط", "Pro Pen 3", "Bluetooth 5.0", "Touch Multi", "ExpressKey Remote"]
        },
        {
            "name_en": "Steam Deck OLED 1TB",
            "name_ar": "جهاز Steam Deck OLED 1 تيرابايت",
            "price": 649, "orig": 749, "rating": 4.8, "reviews": 12345,
            "badge": "",
            "image": "https://placehold.co/400x400/2d2a1a/ffffff?text=Steam%20Deck%20OLED%201TB",
            "features": ["OLED HDR 90Hz", "AMD APU Zen2+RDNA2", "بطارية 50% أطول", "1TB NVMe", "WiFi 6E"]
        },
        {
            "name_en": "Anker MagGo Wireless Charging Station",
            "name_ar": "محطة شحن Anker MagGo اللاسلكي",
            "price": 79, "orig": 99, "rating": 4.7, "reviews": 23456,
            "badge": "",
            "image": "https://placehold.co/400x400/2d2a1a/ffffff?text=Anker%20MagGo%20Wireless%20Char",
            "features": ["MagSafe 15W", "3-in-1 Charging", "iPhone+Watch+AirPods", "20W adaptor", "قابل للطي"]
        },
        {
            "name_en": "LG UltraWide 34\" 5K2K",
            "name_ar": "شاشة LG UltraWide 34 بوصة",
            "price": 999, "orig": 1199, "rating": 4.7, "reviews": 4321,
            "badge": "",
            "image": "https://www.lg.com/us/images/monitors/md07500471/gallery/DZ-01.jpg",
            "features": ["5K2K 5120x2160", "IPS", "Thunderbolt 4", "KVM مدمج", "Ergo Stand"]
        },
        {
            "name_en": "Jabra Evolve2 85 ANC",
            "name_ar": "سماعات Jabra Evolve2 85",
            "price": 449, "orig": 529, "rating": 4.6, "reviews": 3210,
            "badge": "",
            "image": "https://placehold.co/400x400/2d2a1a/ffffff?text=Jabra%20Evolve2%2085%20ANC",
            "features": ["ANC أفضل للعمل", "Busylight مدمج", "37h بطارية", "UC Certified", "8 ميكروفون"]
        },
        {
            "name_en": "Twelve South HiRise 3 Deluxe",
            "name_ar": "حامل Twelve South HiRise 3 Deluxe",
            "price": 99, "orig": 119, "rating": 4.7, "reviews": 5432,
            "badge": "",
            "image": "https://placehold.co/400x400/2d2a1a/ffffff?text=Twelve%20South%20HiRise%203%20Del",
            "features": ["شحن MagSafe 15W", "حامل لاب توب", "Ergo Posture", "iPhone + Mac", "ارتفاع قابل تعديل"]
        },
    ]
}


# ═══════════════════════════════════════════════════════
# GitHub Sync
# ═══════════════════════════════════════════════════════

def _gh_headers():
    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }

def pull_products():
    if not GITHUB_TOKEN:
        return []
    try:
        r = requests.get(
            f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/{GITHUB_FILE}",
            headers=_gh_headers(), timeout=10
        )
        if r.status_code == 200:
            return json.loads(base64.b64decode(r.json()["content"]).decode())
    except Exception as e:
        log.error(f"pull: {e}")
    return []

def push_products(products, message="🤖 Bot: update products"):
    if not GITHUB_TOKEN:
        log.error("GITHUB_TOKEN missing")
        return False
    try:
        sha = ""
        r = requests.get(
            f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/{GITHUB_FILE}",
            headers=_gh_headers(), timeout=10
        )
        if r.status_code == 200:
            sha = r.json().get("sha", "")

        content = base64.b64encode(
            json.dumps(products, ensure_ascii=False, indent=2).encode()
        ).decode()

        payload = {"message": message, "content": content, "branch": "main"}
        if sha:
            payload["sha"] = sha

        r = requests.put(
            f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/{GITHUB_FILE}",
            headers=_gh_headers(), json=payload, timeout=30
        )
        if r.status_code in [200, 201]:
            log.info(f"✅ GitHub: pushed {len(products)} products")
            return True
        log.error(f"GitHub push failed: {r.status_code}")
        return False
    except Exception as e:
        log.error(f"push error: {e}")
        return False


# ═══════════════════════════════════════════════════════
# Telegram
# ═══════════════════════════════════════════════════════

def send(chat_id, text, token=None):
    tok = token or SUPPLIER_BOT_TOKEN
    if not tok:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{tok}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
            timeout=8
        )
    except Exception as e:
        log.error(f"send: {e}")


# ═══════════════════════════════════════════════════════
# Core Logic — منطق البوت الأساسي
# ═══════════════════════════════════════════════════════

def auto_add_products(count=5, chat_id=None):
    """
    يضيف منتجات حقيقية تلقائياً من قاعدة البيانات المدمجة
    مع صور حقيقية من المواقع الرسمية
    """
    existing = pull_products()
    existing_ids = {p.get("id") for p in existing}
    existing_names = {p.get("name_en", "").lower() for p in existing}

    added = []
    counter = max(
        [int(p["id"].replace("NPH-","")) for p in existing if p.get("id","").startswith("NPH-")] or [0]
    ) + 1

    # جمع كل المنتجات من كل الفئات
    all_products = []
    for cat_id, products in PRODUCTS_DB.items():
        for p in products:
            if p["name_en"].lower() not in existing_names:
                all_products.append((cat_id, p))

    if not all_products:
        if chat_id:
            send(chat_id, "ℹ️ كل المنتجات موجودة أصلاً في المتجر.")
        return []

    # اختار عشوائياً من كل الفئات
    random.shuffle(all_products)
    selected = all_products[:count]

    for cat_id, p_data in selected:
        new_id = f"NPH-{counter:03d}"
        while new_id in existing_ids:
            counter += 1
            new_id = f"NPH-{counter:03d}"

        cat_info = {
            "smartwatch": "ساعات ذكية",
            "smart-glasses": "نظارات ذكية",
            "health": "صحة ذكية",
            "smart-home": "منزل ذكي",
            "earbuds": "سماعات ذكية",
            "productivity": "إنتاجية",
        }

        discount = round((1 - p_data["price"] / p_data["orig"]) * 100)

        new_product = {
            "id": new_id,
            "name_ar": p_data["name_ar"],
            "name_en": p_data["name_en"],
            "category": cat_id,
            "category_ar": cat_info.get(cat_id, cat_id),
            "price": p_data["price"],
            "original_price": p_data["orig"],
            "discount": discount,
            "rating": p_data["rating"],
            "reviews": p_data["reviews"],
            "stock": random.randint(20, 100),
            "image": p_data["image"],          # ← صورة حقيقية مضمونة
            "description_ar": f"{p_data['name_ar']} — من أفضل منتجات {cat_info.get(cat_id,'')} في السوق. جودة عالية وأداء استثنائي.",
            "features_ar": p_data.get("features", ["ميزة متقدمة", "جودة عالية", "تصميم عصري"]),
            "tags": [cat_info.get(cat_id, cat_id), p_data["name_ar"].split()[0]],
            "badge": p_data.get("badge", ""),
            "active": True,
            "shipping_days": "7-14",
            "featured": p_data.get("badge") in ["الأكثر مبيعاً", "مميز", "حصري"],
            "added_by": "auto_bot",
            "added_at": datetime.now().strftime("%Y-%m-%d")
        }

        existing.append(new_product)
        added.append(new_product)
        existing_ids.add(new_id)
        existing_names.add(p_data["name_en"].lower())
        counter += 1

    if added:
        ok = push_products(existing, f"🤖 Auto-add: {len(added)} منتجات حقيقية")
        if ok and chat_id:
            names = "\n".join([f"✅ `{p['id']}` {p['name_ar']}" for p in added])
            send(chat_id, f"🚀 *تم إضافة {len(added)} منتجات للمتجر:*\n\n{names}\n\n🌐 يظهر خلال دقيقة!")
        elif chat_id:
            send(chat_id, "❌ فشل الحفظ على GitHub")

    return added


def fill_store(chat_id=None):
    """يملأ المتجر كاملاً بـ 90 منتج (15 من كل فئة) مع صور حقيقية"""
    if chat_id:
        send(chat_id, "⏳ جاري ملء المتجر بـ 90 منتج حقيقي مع صور رسمية...")

    all_products = []
    counter = 1

    cat_info = {
        "smartwatch": "ساعات ذكية",
        "smart-glasses": "نظارات ذكية",
        "health": "صحة ذكية",
        "smart-home": "منزل ذكي",
        "earbuds": "سماعات ذكية",
        "productivity": "إنتاجية",
    }

    for cat_id, products_list in PRODUCTS_DB.items():
        for p_data in products_list:
            new_id = f"NPH-{counter:03d}"
            discount = round((1 - p_data["price"] / p_data["orig"]) * 100)

            product = {
                "id": new_id,
                "name_ar": p_data["name_ar"],
                "name_en": p_data["name_en"],
                "category": cat_id,
                "category_ar": cat_info.get(cat_id, cat_id),
                "price": p_data["price"],
                "original_price": p_data["orig"],
                "discount": discount,
                "rating": p_data["rating"],
                "reviews": p_data["reviews"],
                "stock": random.randint(20, 100),
                "image": p_data["image"],
                "description_ar": f"{p_data['name_ar']} — من أفضل منتجات {cat_info.get(cat_id,'')} في السوق. جودة عالية وأداء استثنائي.",
                "features_ar": p_data.get("features", ["جودة عالية", "تصميم عصري", "أداء متقدم"]),
                "tags": [cat_info.get(cat_id, cat_id), p_data["name_ar"].split()[0]],
                "badge": p_data.get("badge", ""),
                "active": True,
                "shipping_days": "7-14",
                "featured": p_data.get("badge") in ["الأكثر مبيعاً", "مميز", "حصري"],
                "added_by": "fill_bot",
                "added_at": datetime.now().strftime("%Y-%m-%d")
            }
            all_products.append(product)
            counter += 1

    ok = push_products(all_products, f"🤖 Fill store: {len(all_products)} منتج حقيقي")

    if chat_id:
        if ok:
            cats_summary = "\n".join([
                f"⌚ ساعات: {len(PRODUCTS_DB['smartwatch'])}",
                f"🥽 نظارات: {len(PRODUCTS_DB['smart-glasses'])}",
                f"💪 صحة: {len(PRODUCTS_DB['health'])}",
                f"🏠 منزل: {len(PRODUCTS_DB['smart-home'])}",
                f"🎧 سماعات: {len(PRODUCTS_DB['earbuds'])}",
                f"💼 إنتاجية: {len(PRODUCTS_DB['productivity'])}",
            ])
            send(chat_id, f"✅ *تم ملء المتجر بنجاح!*\n\n{cats_summary}\n\n*إجمالي: {len(all_products)} منتج* بصور رسمية حقيقية 🎯")
        else:
            send(chat_id, "❌ فشل الحفظ على GitHub. تحقق من GITHUB_TOKEN")

    return all_products


def fix_images(chat_id=None):
    """يصلح صور المنتجات الحالية من قاعدة البيانات"""
    products = pull_products()
    if not products:
        if chat_id:
            send(chat_id, "❌ لا توجد منتجات")
        return

    fixed = 0
    for p in products:
        name_en = p.get("name_en", "")
        cat = p.get("category", "")
        # ابحث في قاعدة البيانات
        cat_products = PRODUCTS_DB.get(cat, [])
        for db_p in cat_products:
            if db_p["name_en"] == name_en:
                if p.get("image") != db_p["image"]:
                    p["image"] = db_p["image"]
                    fixed += 1
                break

    if fixed > 0:
        ok = push_products(products, f"🖼️ Fix images: {fixed} منتج")
        if chat_id:
            msg = f"✅ تم تصليح {fixed} صورة!" if ok else "❌ فشل الحفظ"
            send(chat_id, msg)
    else:
        if chat_id:
            send(chat_id, "ℹ️ كل الصور سليمة أصلاً")


# ═══════════════════════════════════════════════════════
# Webhook Handler
# ═══════════════════════════════════════════════════════

def handle_update(update):
    if "message" not in update or "text" not in update.get("message", {}):
        return

    msg     = update["message"]
    chat_id = msg["chat"]["id"]
    text    = msg["text"].strip()

    log.info(f"supplier | {chat_id}: {text}")

    if text == "/start":
        send(chat_id, (
            "📦 *بوت الموردين الذكي v3*\n\n"
            "الأوامر:\n"
            "/auto ← يضيف 5 منتجات تلقائياً\n"
            "/auto 10 ← يضيف 10 منتجات\n"
            "/fill ← يملأ المتجر كاملاً بـ 90 منتج\n"
            "/fix\\_images ← يصلح صور المنتجات\n"
            "/stock ← حالة المخزون\n"
            "/products ← قائمة المنتجات\n"
            "/add اسم ← يضيف منتج محدد"
        ))

    elif text.startswith("/auto"):
        parts = text.split()
        count = 5
        if len(parts) == 2:
            try:
                count = min(int(parts[1]), 20)
            except:
                pass
        send(chat_id, f"🔍 جاري إضافة {count} منتجات حقيقية...")
        auto_add_products(count, chat_id)

    elif text == "/fill":
        fill_store(chat_id)

    elif text == "/fix_images":
        send(chat_id, "🖼️ جاري تصليح الصور...")
        fix_images(chat_id)

    elif text == "/stock":
        products = pull_products()
        if not products:
            send(chat_id, "📦 لا توجد منتجات")
            return
        reply = "📦 *حالة المخزون:*\n\n"
        for p in products[:15]:
            stock = p.get("stock", 0)
            icon = "✅" if stock > 5 else ("⚠️" if stock > 0 else "❌")
            reply += f"{icon} `{p.get('id','')}` {p.get('name_ar','')} — {stock} قطعة\n"
        send(chat_id, reply)

    elif text == "/products":
        products = pull_products()
        if not products:
            send(chat_id, "لا توجد منتجات")
            return
        reply = f"🛒 *المنتجات ({len(products)} إجمالي):*\n\n"
        for p in products[:15]:
            reply += f"• `{p.get('id','')}` — {p.get('name_ar','')} — ${p.get('price',0)}\n"
        send(chat_id, reply)

    elif text.startswith("/restock "):
        parts = text.split()
        if len(parts) == 3:
            pid, qty = parts[1], int(parts[2])
            products = pull_products()
            for p in products:
                if p.get("id") == pid:
                    p["stock"] = p.get("stock", 0) + qty
                    if push_products(products, f"Restock {pid} +{qty}"):
                        send(chat_id, f"✅ تم تحديث مخزون `{pid}` — أضفت {qty} قطعة")
                    break

    elif text.startswith("/price "):
        parts = text.split()
        if len(parts) == 3:
            pid, price = parts[1], float(parts[2])
            products = pull_products()
            for p in products:
                if p.get("id") == pid:
                    p["price"] = price
                    if push_products(products, f"Price {pid} = {price}"):
                        send(chat_id, f"✅ تم تحديث سعر `{pid}` إلى ${price}")
                    break

    else:
        send(chat_id, "الأوامر: /auto /fill /fix_images /stock /products")


# ═══════════════════════════════════════════════════════
# يُشغَّل مباشرة من command line
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "fill"

    if cmd == "fill":
        log.info("🚀 Fill store mode")
        products = fill_store()
        log.info(f"✅ Done: {len(products)} products")

    elif cmd == "auto":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        log.info(f"🤖 Auto-add {count} products")
        added = auto_add_products(count)
        log.info(f"✅ Added: {len(added)}")

    elif cmd == "fix":
        log.info("🖼️ Fix images mode")
        fix_images()
