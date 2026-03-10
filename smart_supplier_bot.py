#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO PULSE HUB — Smart Supplier Bot v4.0
يبحث عن صور حقيقية من Google Images ويضيف المنتجات تلقائياً
"""

import os, json, base64, requests, time, re, logging, random
from datetime import datetime

try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass

SUPPLIER_BOT_TOKEN = os.environ.get("SUPPLIER_BOT_TOKEN", "")
ADMIN_USER_ID      = int(os.environ.get("ADMIN_USER_ID", "0"))
GEMINI_API_KEY     = os.environ.get("GEMINI_API_KEY", "")
GITHUB_TOKEN       = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO        = os.environ.get("GITHUB_REPO", "casperblac991/neo-pulse-hub")
GITHUB_FILE        = "products.json"
GITHUB_API         = "https://api.github.com"

# Google Custom Search API
GOOGLE_API_KEY     = os.environ.get("GOOGLE_API_KEY", "AIzaSyBjH8OXjZ9r_tvB4z9miqlncdvVuRsfWiU")
GOOGLE_CX          = os.environ.get("GOOGLE_CX", "53f17b4ecf9924a25")
GOOGLE_SEARCH_URL  = "https://www.googleapis.com/customsearch/v1"

logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
log = logging.getLogger("smart_supplier")

# ═══════════════════════════════════════════════════════
# قاعدة بيانات المنتجات
# ═══════════════════════════════════════════════════════
PRODUCTS_DB = {
    "smartwatch": [
        {"name_en": "Apple Watch Series 9 45mm",   "name_ar": "ساعة أبل Watch Series 9",        "price": 399, "orig": 449, "rating": 4.9, "reviews": 12430, "badge": "الأكثر مبيعاً", "features": ["شاشة Retina دائمة التشغيل", "GPS + Cellular", "مقاوم للماء 50م", "تتبع صحي شامل", "بطارية 18 ساعة"]},
        {"name_en": "Samsung Galaxy Watch 7 44mm",  "name_ar": "ساعة سامسونج Galaxy Watch 7",    "price": 299, "orig": 349, "rating": 4.8, "reviews": 8765,  "badge": "مميز",           "features": ["معالج Exynos W1000", "تتبع نوم AI", "بطارية 40 ساعة", "مقاومة MIL-STD-810", "تتبع اللياقة"]},
        {"name_en": "Garmin Fenix 7X Solar",        "name_ar": "ساعة غارمن Fenix 7X Solar",      "price": 699, "orig": 799, "rating": 4.8, "reviews": 5432,  "badge": "",               "features": ["شحن شمسي", "GPS متعدد التردد", "بطارية 37 يوم", "خرائط توبو مدمجة", "مناسب للمغامرات"]},
        {"name_en": "Apple Watch Ultra 2",          "name_ar": "ساعة أبل Watch Ultra 2",          "price": 799, "orig": 899, "rating": 4.9, "reviews": 4321,  "badge": "حصري",           "features": ["هيكل تيتانيوم", "بطارية 60 ساعة", "صوت إنذار 86dB", "مقاومة 100م", "GPS دقة عالية"]},
        {"name_en": "Google Pixel Watch 3 45mm",    "name_ar": "ساعة غوغل Pixel Watch 3",        "price": 349, "orig": 399, "rating": 4.7, "reviews": 3210,  "badge": "جديد",           "features": ["Wear OS 4", "تتبع قلب متقدم", "شاشة AMOLED", "Google Wallet", "بطارية 24 ساعة"]},
        {"name_en": "Xiaomi Watch S3",              "name_ar": "ساعة شاومي Watch S3",             "price": 139, "orig": 169, "rating": 4.5, "reviews": 6543,  "badge": "قيمة مثالية",   "features": ["شاشة AMOLED 1.43\"", "12 أيام بطارية", "GPS مدمج", "150 وضع رياضي", "5ATM"]},
        {"name_en": "Amazfit Balance",              "name_ar": "ساعة أمازفيت Balance",            "price": 229, "orig": 269, "rating": 4.6, "reviews": 2876,  "badge": "",               "features": ["Zepp OS 3.0", "14 أيام بطارية", "تتبع صحي AI", "شاشة AMOLED", "GPS L1+L5"]},
        {"name_en": "Samsung Galaxy Watch Ultra",   "name_ar": "ساعة سامسونج Galaxy Watch Ultra", "price": 649, "orig": 749, "rating": 4.8, "reviews": 1987,  "badge": "جديد",           "features": ["هيكل تيتانيوم", "بطارية 60 ساعة", "MIL-STD-810X", "10ATM", "GPS Dual"]},
        {"name_en": "Fitbit Versa 4",               "name_ar": "ساعة فيتبيت Versa 4",            "price": 149, "orig": 199, "rating": 4.5, "reviews": 9876,  "badge": "",               "features": ["Alexa مدمج", "GPS", "6 أيام بطارية", "تتبع النوم", "40+ وضع تمرين"]},
        {"name_en": "Garmin Venu 3S",               "name_ar": "ساعة غارمن Venu 3S",             "price": 449, "orig": 499, "rating": 4.7, "reviews": 3456,  "badge": "",               "features": ["شاشة AMOLED", "استجابة جسم AI", "Body Battery", "تتبع سكر الدم", "GPS"]},
        {"name_en": "OnePlus Watch 3",              "name_ar": "ساعة ون بلس Watch 3",            "price": 329, "orig": 379, "rating": 4.6, "reviews": 2134,  "badge": "",               "features": ["Wear OS 4", "100 ساعة بطارية", "شحن 80% بـ 30 دقيقة", "GPS Dual", "5ATM"]},
        {"name_en": "Huawei Watch GT 5 Pro",        "name_ar": "ساعة هواوي Watch GT 5 Pro",      "price": 349, "orig": 399, "rating": 4.7, "reviews": 4567,  "badge": "",               "features": ["هيكل تيتانيوم", "بطارية 14 يوم", "تتبع صحي شامل", "GPS مزدوج", "خرائط"]},
        {"name_en": "Withings ScanWatch 2",         "name_ar": "ساعة ويذينغز ScanWatch 2",       "price": 299, "orig": 349, "rating": 4.6, "reviews": 1876,  "badge": "",               "features": ["تخطيط قلب ECG", "SpO2", "30 يوم بطارية", "تصميم كلاسيكي", "FDA"]},
        {"name_en": "TicWatch Pro 5 Enduro",        "name_ar": "ساعة تيكووتش Pro 5 Enduro",      "price": 399, "orig": 449, "rating": 4.6, "reviews": 1234,  "badge": "",               "features": ["Snapdragon W5+", "شاشة مزدوجة", "80 ساعة بطارية", "Wear OS", "MIL-STD"]},
        {"name_en": "Coros Apex 2 Pro",             "name_ar": "ساعة كوروس Apex 2 Pro",          "price": 499, "orig": 599, "rating": 4.8, "reviews": 2345,  "badge": "",               "features": ["GPS متعدد", "75 ساعة GPS", "خرائط توبو", "شحن سريع", "تيتانيوم"]},
    ],
    "smart-glasses": [
        {"name_en": "Apple Vision Pro",             "name_ar": "نظارة Apple Vision Pro",          "price": 3499,"orig": 3999,"rating": 4.8, "reviews": 4532,  "badge": "حصري",           "features": ["شاشة micro-OLED 4K", "visionOS", "R1 Chip", "كاميرات 3D", "انغماس كامل"]},
        {"name_en": "Meta Quest 3 512GB",           "name_ar": "نظارة Meta Quest 3",              "price": 649, "orig": 749, "rating": 4.8, "reviews": 15432, "badge": "الأكثر مبيعاً", "features": ["Snapdragon XR2 Gen 2", "Mixed Reality", "عدسات Pancake", "بطارية 2.2h", "Meta Store"]},
        {"name_en": "Ray-Ban Meta Wayfarer",        "name_ar": "نظارة Ray-Ban Meta الذكية",       "price": 329, "orig": 379, "rating": 4.5, "reviews": 8765,  "badge": "مميز",           "features": ["كاميرا 12MP", "مكبرات مفتوحة", "Bluetooth 5.3", "Meta AI", "4 ساعات"]},
        {"name_en": "Meta Quest 3S 128GB",          "name_ar": "نظارة Meta Quest 3S",             "price": 299, "orig": 349, "rating": 4.7, "reviews": 6543,  "badge": "جديد",           "features": ["Snapdragon XR2 Gen 2", "Mixed Reality", "128GB", "أخف بـ 50%", "Meta Store"]},
        {"name_en": "XREAL Air 2 Pro",              "name_ar": "نظارة XREAL Air 2 Pro",           "price": 449, "orig": 499, "rating": 4.6, "reviews": 3210,  "badge": "",               "features": ["شاشة 330\" افتراضية", "120Hz", "Electrochromic", "USB-C", "72g"]},
        {"name_en": "HTC Vive XR Elite",            "name_ar": "نظارة HTC Vive XR Elite",         "price": 999, "orig": 1199,"rating": 4.6, "reviews": 1876,  "badge": "",               "features": ["Snapdragon XR2 Gen 1", "4K+ عرض", "Viveport Infinity", "قابل للخلع", "2h"]},
        {"name_en": "Pico 4 Ultra VR",              "name_ar": "نظارة Pico 4 Ultra",              "price": 599, "orig": 699, "rating": 4.5, "reviews": 2345,  "badge": "",               "features": ["Snapdragon XR2 Gen 2", "Spatial Video", "Hand Tracking", "3GB RAM", "3h"]},
        {"name_en": "Snap Spectacles 5th Gen",      "name_ar": "نظارة Snap Spectacles الجيل 5",  "price": 399, "orig": 449, "rating": 4.3, "reviews": 1234,  "badge": "",               "features": ["AR مدمج", "كاميرا ثنائية", "Snapchat مدمج", "Lens Studio", "30 دقيقة"]},
        {"name_en": "XREAL Beam Pro",               "name_ar": "نظارة XREAL Beam Pro",            "price": 599, "orig": 699, "rating": 4.5, "reviews": 1543,  "badge": "",               "features": ["Spatial Computing", "كاميرتين", "Android 13", "3D Capture", "5000mAh"]},
        {"name_en": "Vuzix Z100 AR Glasses",        "name_ar": "نظارة Vuzix Z100 الذكية",        "price": 699, "orig": 799, "rating": 4.3, "reviews": 543,   "badge": "",               "features": ["Waveguide AR", "Qualcomm AR1", "8h بطارية", "Android 11", "Hands-free"]},
        {"name_en": "TCL NXTWEAR S2 Plus",          "name_ar": "نظارة TCL NXTWEAR S2 Plus",       "price": 379, "orig": 429, "rating": 4.4, "reviews": 876,   "badge": "",               "features": ["105\" افتراضية", "1080p Full HD", "USB-C", "72g", "120Hz"]},
        {"name_en": "Inmo Air 2 Smart Glasses",     "name_ar": "نظارة Inmo Air 2 الذكية",        "price": 399, "orig": 449, "rating": 4.2, "reviews": 654,   "badge": "",               "features": ["ChatGPT مدمج", "ترجمة فورية", "27g", "9h بطارية", "Waveguide"]},
        {"name_en": "Rokid Max 2 AR",               "name_ar": "نظارة Rokid Max 2",               "price": 549, "orig": 629, "rating": 4.5, "reviews": 987,   "badge": "",               "features": ["Micro-OLED 1080p", "120Hz", "4700nit", "Spatial Audio", "USB-C"]},
        {"name_en": "Viture One XR Glasses",        "name_ar": "نظارة Viture One XR",             "price": 439, "orig": 499, "rating": 4.4, "reviews": 765,   "badge": "",               "features": ["135\" افتراضية", "Electrochromic", "Cinema Mode", "2K", "77g"]},
        {"name_en": "Meta Ray-Ban Skyler Glasses",  "name_ar": "نظارة Meta Ray-Ban Skyler",       "price": 349, "orig": 399, "rating": 4.5, "reviews": 3210,  "badge": "",               "features": ["كاميرا 12MP Ultra Wide", "AI مساعد", "Bluetooth 5.3", "6h", "مفتوحة"]},
    ],
    "health": [
        {"name_en": "Oura Ring Gen 4",              "name_ar": "خاتم Oura Ring الجيل 4",          "price": 349, "orig": 399, "rating": 4.8, "reviews": 18765, "badge": "الأكثر مبيعاً", "features": ["تتبع نوم دقيق", "Readiness Score", "8 أيام بطارية", "Blood Oxygen", "Ring AI"]},
        {"name_en": "WHOOP 4.0 Fitness Band",       "name_ar": "حزام WHOOP 4.0",                  "price": 239, "orig": 279, "rating": 4.6, "reviews": 8765,  "badge": "",               "features": ["Strain Tracking", "Recovery Score", "HRV متقدم", "5 أيام بطارية", "دقة عالية"]},
        {"name_en": "Ultrahuman Ring AIR",          "name_ar": "خاتم Ultrahuman Ring AIR",        "price": 349, "orig": 399, "rating": 4.7, "reviews": 5432,  "badge": "مميز",           "features": ["بدون اشتراك", "AI نوم", "Metabolic Score", "7 أيام", "IP68"]},
        {"name_en": "Fitbit Charge 6 Tracker",      "name_ar": "سوار Fitbit Charge 6",            "price": 159, "orig": 199, "rating": 4.6, "reviews": 12345, "badge": "",               "features": ["ECG", "Google Maps", "YouTube Music", "7 أيام", "GPS"]},
        {"name_en": "Garmin Vivosmart 5",           "name_ar": "سوار Garmin Vivosmart 5",         "price": 149, "orig": 179, "rating": 4.5, "reviews": 6543,  "badge": "",               "features": ["OLED", "7 أيام", "Body Battery", "HRV Status", "5ATM"]},
        {"name_en": "Withings ScanWatch Nova",      "name_ar": "ساعة Withings ScanWatch Nova",    "price": 499, "orig": 599, "rating": 4.7, "reviews": 2345,  "badge": "",               "features": ["ECG", "30 يوم بطارية", "SpO2", "تصميم كلاسيكي", "FDA"]},
        {"name_en": "Amazfit Helio Ring",           "name_ar": "خاتم أمازفيت Helio Ring",        "price": 299, "orig": 349, "rating": 4.5, "reviews": 1876,  "badge": "",               "features": ["تيتانيوم", "صحة شاملة", "4 أيام", "Zepp Health", "IP68"]},
        {"name_en": "RingConn Gen 2 Air Ring",      "name_ar": "خاتم RingConn Gen 2 Air",        "price": 199, "orig": 249, "rating": 4.5, "reviews": 3210,  "badge": "قيمة مثالية",   "features": ["10 أيام", "بدون اشتراك", "نوم", "SpO2", "متعدد"]},
        {"name_en": "Xiaomi Smart Band 9 Pro",      "name_ar": "سوار شاومي Smart Band 9 Pro",    "price": 79,  "orig": 99,  "rating": 4.6, "reviews": 15432, "badge": "اقتصادي",       "features": ["AMOLED 1.74\"", "GPS", "21 يوم", "150 رياضة", "SpO2"]},
        {"name_en": "Muse 2 Brain Sensing Headband","name_ar": "عصابة Muse 2 للتأمل",            "price": 249, "orig": 299, "rating": 4.5, "reviews": 2876,  "badge": "",               "features": ["EEG 7 مستشعرات", "تأمل موجَّه", "تتبع تنفس", "نبضات القلب", "تطبيق"]},
        {"name_en": "Samsung Galaxy Ring",          "name_ar": "خاتم سامسونج Galaxy Ring",       "price": 399, "orig": 449, "rating": 4.6, "reviews": 4321,  "badge": "جديد",           "features": ["تيتانيوم خفيف", "7 أيام", "Samsung Health", "AI نوم", "IP68"]},
        {"name_en": "Polar Verity Sense Monitor",   "name_ar": "جهاز Polar Verity Sense",        "price": 89,  "orig": 109, "rating": 4.7, "reviews": 5678,  "badge": "",               "features": ["HR دقيق", "ذراع", "30h بطارية", "Bluetooth + ANT+", "IP67"]},
        {"name_en": "Biostrap EVO Health Band",     "name_ar": "سوار Biostrap EVO الصحي",        "price": 199, "orig": 249, "rating": 4.4, "reviews": 1234,  "badge": "",               "features": ["HRV دقيق", "SpO2 مستمر", "نوم", "طبي", "IP67"]},
        {"name_en": "Garmin Index BPM Monitor",     "name_ar": "جهاز Garmin Index لضغط الدم",    "price": 149, "orig": 179, "rating": 4.5, "reviews": 3456,  "badge": "",               "features": ["ضغط الدم", "Bluetooth 5.0", "Garmin Connect", "دقيق", "40 قياس"]},
        {"name_en": "Withings Body Scan Scale",     "name_ar": "ميزان Withings Body Scan",       "price": 299, "orig": 349, "rating": 4.7, "reviews": 876,   "badge": "",               "features": ["تركيب جسم", "ECG قدم", "عصب وعائي", "تطبيق صحي", "WiFi"]},
    ],
    "smart-home": [
        {"name_en": "Amazon Echo Show 10 3rd Gen",  "name_ar": "مكبر Amazon Echo Show 10",        "price": 249, "orig": 299, "rating": 4.7, "reviews": 23456, "badge": "الأكثر مبيعاً", "features": ["شاشة HD 10\"", "يتابعك تلقائياً", "كاميرا 13MP", "Alexa", "مكبر 3\""]},
        {"name_en": "Apple HomePod 2nd Generation", "name_ar": "مكبر Apple HomePod الجيل 2",     "price": 299, "orig": 349, "rating": 4.7, "reviews": 12345, "badge": "مميز",           "features": ["Spatial Audio", "S7 Chip", "تحكم منزل", "Siri", "صوت استثنائي"]},
        {"name_en": "Google Nest Hub Max Display",  "name_ar": "شاشة Google Nest Hub Max",       "price": 229, "orig": 279, "rating": 4.6, "reviews": 15432, "badge": "",               "features": ["شاشة 10\"", "كاميرا Duo", "Google Photos", "Assistant", "Full-range"]},
        {"name_en": "Philips Hue Color Starter Kit","name_ar": "طقم إضاءة Philips Hue الذكية",  "price": 199, "orig": 249, "rating": 4.7, "reviews": 34567, "badge": "",               "features": ["16M لون", "تحكم صوتي", "Hue Bridge", "تطبيق", "موسيقى"]},
        {"name_en": "Ring Video Doorbell Pro 2",    "name_ar": "جرس Ring Video Doorbell Pro 2",  "price": 249, "orig": 299, "rating": 4.5, "reviews": 43210, "badge": "",               "features": ["1536p HD+", "Bird's Eye View", "تنبيه ذكي", "Alexa", "3D"]},
        {"name_en": "Google Nest Learning Thermostat","name_ar": "منظم حرارة Nest الجيل 4",     "price": 279, "orig": 329, "rating": 4.7, "reviews": 28765, "badge": "",               "features": ["تعلم جدولك", "توفير 15%", "يحس بتواجدك", "OLED", "Google Home"]},
        {"name_en": "Amazon Echo Dot 5th Gen",      "name_ar": "مكبر Amazon Echo Dot الجيل 5",  "price": 49,  "orig": 59,  "rating": 4.7, "reviews": 98765, "badge": "قيمة مثالية",   "features": ["Alexa", "صوت أوضح 2x", "Smart Home", "ساعة LED", "مزامنة"]},
        {"name_en": "Arlo Pro 5S Security Camera",  "name_ar": "كاميرا Arlo Pro 5S أمان",       "price": 249, "orig": 299, "rating": 4.6, "reviews": 8765,  "badge": "",               "features": ["2K + HDR", "ألوان ليلية", "160°", "6 أشهر بطارية", "Alexa"]},
        {"name_en": "Yale Assure Lock 2 Plus",      "name_ar": "قفل ذكي Yale Assure Lock 2",    "price": 329, "orig": 379, "rating": 4.5, "reviews": 4321,  "badge": "",               "features": ["Matter + Z-Wave", "بصمة + رمز", "AES-128", "Yale Access", "تنبيهات"]},
        {"name_en": "iRobot Roomba j9 Plus",        "name_ar": "مكنسة iRobot Roomba j9+",       "price": 799, "orig": 999, "rating": 4.7, "reviews": 6543,  "badge": "",               "features": ["تفريغ 60 يوم", "تجنب عوائق AI", "خريطة ذكية", "Alexa", "شحن تلقائي"]},
        {"name_en": "Nanoleaf Shapes Hexagons Kit", "name_ar": "إضاءة Nanoleaf Shapes سداسية",  "price": 199, "orig": 249, "rating": 4.5, "reviews": 12345, "badge": "",               "features": ["16M لون", "موسيقى تفاعلية", "لمس", "Thread", "تصميم حر"]},
        {"name_en": "Sonos Era 300 Speaker",        "name_ar": "مكبر Sonos Era 300",             "price": 449, "orig": 499, "rating": 4.7, "reviews": 3456,  "badge": "",               "features": ["Spatial Audio", "Dolby Atmos", "6 مكبرات", "S2 App", "بدون اشتراك"]},
        {"name_en": "Ecobee Smart Thermostat Premium","name_ar": "منظم Ecobee Smart Premium",    "price": 249, "orig": 299, "rating": 4.7, "reviews": 21345, "badge": "",               "features": ["Alexa مدمج", "درجة حرارة غرفة", "توفير 23%", "SmartSensor", "ENERGY STAR"]},
        {"name_en": "Samsung SmartThings Hub",      "name_ar": "مركز Samsung SmartThings",       "price": 129, "orig": 149, "rating": 4.5, "reviews": 5432,  "badge": "",               "features": ["Zigbee + Z-Wave + WiFi", "تحكم مركزي", "روتين تلقائي", "أمان محلي", "شامل"]},
        {"name_en": "Eufy Security HomeBase 3",     "name_ar": "نظام Eufy Security HomeBase 3",  "price": 299, "orig": 349, "rating": 4.6, "reviews": 4321,  "badge": "",               "features": ["16GB محلي", "Triple Band WiFi", "BionicMind AI", "8K", "بدون اشتراك"]},
    ],
    "earbuds": [
        {"name_en": "Apple AirPods Pro 2 USB-C",    "name_ar": "سماعات AirPods Pro الجيل 2",     "price": 249, "orig": 279, "rating": 4.9, "reviews": 54321, "badge": "الأكثر مبيعاً", "features": ["ANC H2 Chip", "Adaptive Audio", "صوت مكاني", "IP68", "6h+30h"]},
        {"name_en": "Sony WF-1000XM5 Earbuds",      "name_ar": "سماعات Sony WF-1000XM5",        "price": 279, "orig": 329, "rating": 4.8, "reviews": 23456, "badge": "مميز",           "features": ["أفضل ANC", "V2 Processor", "360 صوت", "LDAC", "8h+24h"]},
        {"name_en": "Bose QuietComfort Ultra Earbuds","name_ar": "سماعات Bose QuietComfort Ultra","price": 299, "orig": 349, "rating": 4.8, "reviews": 15432, "badge": "",               "features": ["Immersive Audio", "CustomTune ANC", "6h+24h", "USB-C", "IP54"]},
        {"name_en": "Samsung Galaxy Buds 3 Pro",    "name_ar": "سماعات Samsung Galaxy Buds 3 Pro","price": 249, "orig": 299, "rating": 4.7, "reviews": 12345, "badge": "",               "features": ["ANC AI", "Blade Design", "IP57", "360° Audio", "6h+30h"]},
        {"name_en": "Apple AirPods 4 with ANC",     "name_ar": "سماعات Apple AirPods 4 ANC",     "price": 179, "orig": 199, "rating": 4.8, "reviews": 32145, "badge": "جديد",           "features": ["H2 ANC", "Open-ear", "USB-C", "5h+30h", "IP54"]},
        {"name_en": "Sony WH-1000XM5 Headphones",   "name_ar": "سماعات Sony WH-1000XM5 فوق الأذن","price": 349,"orig": 399, "rating": 4.8, "reviews": 45678, "badge": "",               "features": ["ANC AI", "30h بطارية", "Multi-point", "LDAC HiRes", "فولد"]},
        {"name_en": "Nothing Ear 3 Wireless",       "name_ar": "سماعات Nothing Ear 3",           "price": 149, "orig": 179, "rating": 4.6, "reviews": 8765,  "badge": "",               "features": ["تصميم شفاف", "ANC 45dB", "8.5h+40h", "IP55", "ChatGPT"]},
        {"name_en": "Jabra Evolve2 Buds Pro",       "name_ar": "سماعات Jabra Evolve2 Buds",      "price": 249, "orig": 299, "rating": 4.5, "reviews": 4321,  "badge": "",               "features": ["للمهنيين", "ANC AI", "Jabra AI", "6h+33h", "UC certified"]},
        {"name_en": "Beats Studio Buds Plus",       "name_ar": "سماعات Beats Studio Buds+",      "price": 169, "orig": 199, "rating": 4.6, "reviews": 6543,  "badge": "",               "features": ["ANC 36dB", "Transparency", "IP54", "9h+36h", "Android+iOS"]},
        {"name_en": "Sennheiser Momentum True Wireless 4","name_ar": "سماعات Sennheiser MTW4",   "price": 279, "orig": 329, "rating": 4.7, "reviews": 3456,  "badge": "",               "features": ["Hi-Fi صوت", "ANC Adaptive", "7h+28h", "aptX Lossless", "IP54"]},
        {"name_en": "Google Pixel Buds Pro 2",      "name_ar": "سماعات Google Pixel Buds Pro 2", "price": 229, "orig": 259, "rating": 4.7, "reviews": 8765,  "badge": "جديد",           "features": ["Tensor A1", "ANC محسَّن", "11h+33h", "ترجمة فورية", "Gemini"]},
        {"name_en": "Anker Soundcore Liberty 4 Pro","name_ar": "سماعات Anker Soundcore Liberty 4","price": 129,"orig": 159, "rating": 4.6, "reviews": 12345, "badge": "قيمة مثالية",   "features": ["ANC 50dB", "LDAC", "11h+53h", "IPX4", "شاشة"]},
        {"name_en": "JBL Tour Pro 3 Earbuds",       "name_ar": "سماعات JBL Tour Pro 3",          "price": 249, "orig": 299, "rating": 4.6, "reviews": 5432,  "badge": "",               "features": ["شاشة لمس", "ANC Pro", "10h+40h", "Hi-Res", "ChatGPT"]},
        {"name_en": "Shure Aonic Free 2",           "name_ar": "سماعات Shure Aonic Free 2",      "price": 299, "orig": 349, "rating": 4.6, "reviews": 2345,  "badge": "",               "features": ["جودة استوديو", "ANC", "7h+28h", "USB-C", "لمس"]},
        {"name_en": "Technics EAH-AZ100 Earbuds",   "name_ar": "سماعات Technics EAH-AZ100",      "price": 299, "orig": 349, "rating": 4.7, "reviews": 1876,  "badge": "",               "features": ["ANC AI", "Jitter-less", "10h+25h", "USB-C", "IPX4"]},
    ],
    "productivity": [
        {"name_en": "Apple iPad Pro M4 13 inch",    "name_ar": "جهاز iPad Pro M4 13 بوصة",       "price": 1299,"orig": 1499,"rating": 4.9, "reviews": 23456, "badge": "الأكثر مبيعاً", "features": ["M4 Chip", "OLED Tandem", "Apple Intelligence", "120Hz", "USB4"]},
        {"name_en": "Samsung Galaxy Tab S10 Ultra", "name_ar": "تابلت Samsung Galaxy Tab S10 Ultra","price": 1299,"orig": 1499,"rating": 4.8,"reviews": 12345,"badge": "مميز",           "features": ["Snapdragon 8 Gen 3", "AMOLED 14.6\"", "S Pen", "DeX", "12000mAh"]},
        {"name_en": "Logitech MX Master 3S Mouse",  "name_ar": "ماوس Logitech MX Master 3S",     "price": 99,  "orig": 119, "rating": 4.9, "reviews": 45678, "badge": "",               "features": ["8000 DPI", "MagSpeed عجلة", "7 أزرار", "70 يوم", "Bolt"]},
        {"name_en": "Logitech MX Keys S Plus Keyboard","name_ar": "لوحة Logitech MX Keys S Plus","price": 149, "orig": 179, "rating": 4.8, "reviews": 23456, "badge": "",               "features": ["Smart Backlight", "Smart Actions", "5 أجهزة", "10 أيام", "Flow"]},
        {"name_en": "Keychron Q6 Max Wireless Keyboard","name_ar": "لوحة Keychron Q6 Max",       "price": 299, "orig": 349, "rating": 4.8, "reviews": 8765,  "badge": "",               "features": ["مفاتيح ميكانيكية", "QMK/VIA", "Gasket Mount", "BT 5.1", "5000mAh"]},
        {"name_en": "Elgato Stream Deck Neo Panel",  "name_ar": "جهاز Elgato Stream Deck Neo",   "price": 99,  "orig": 119, "rating": 4.7, "reviews": 6543,  "badge": "",               "features": ["8 مفاتيح LCD", "شاشتا Info", "تكامل واسع", "USB-C", "كل شيء"]},
        {"name_en": "Apple Pencil Pro Stylus",       "name_ar": "قلم Apple Pencil Pro",           "price": 129, "orig": 149, "rating": 4.8, "reviews": 21345, "badge": "",               "features": ["Squeeze + Double Tap", "دوران", "Barrel Roll", "شحن مغناطيسي", "9ms"]},
        {"name_en": "Anker 737 GaNPrime 120W Charger","name_ar": "شاحن Anker 737 GaNPrime 120W", "price": 89,  "orig": 109, "rating": 4.8, "reviews": 34567, "badge": "قيمة مثالية",   "features": ["120W", "3 منافذ", "GaN III", "43 دقيقة 80%", "USB-C+A"]},
        {"name_en": "Samsung Odyssey OLED G9 Monitor","name_ar": "شاشة Samsung Odyssey OLED G9", "price": 1299,"orig": 1499,"rating": 4.7, "reviews": 3456,  "badge": "",               "features": ["OLED 49\" QHD", "240Hz", "0.03ms", "HDR True Black", "FreeSync"]},
        {"name_en": "Wacom Intuos Pro Large Tablet", "name_ar": "لوح رسم Wacom Intuos Pro L",    "price": 449, "orig": 499, "rating": 4.8, "reviews": 8765,  "badge": "",               "features": ["8192 ضغط", "Pro Pen 3", "BT 5.0", "Touch Multi", "ExpressKey"]},
        {"name_en": "Steam Deck OLED 1TB Gaming",   "name_ar": "جهاز Steam Deck OLED 1 تيرابايت","price": 649, "orig": 749, "rating": 4.8, "reviews": 12345, "badge": "",               "features": ["OLED HDR 90Hz", "AMD APU", "بطارية +50%", "1TB NVMe", "WiFi 6E"]},
        {"name_en": "Anker MagGo 3-in-1 Wireless Charger","name_ar": "محطة شحن Anker MagGo اللاسلكي","price": 79,"orig": 99,"rating": 4.7,"reviews": 23456, "badge": "",               "features": ["MagSafe 15W", "3-in-1", "iPhone+Watch+AirPods", "20W", "قابل للطي"]},
        {"name_en": "LG UltraWide 34 5K2K Monitor", "name_ar": "شاشة LG UltraWide 34 بوصة",    "price": 999, "orig": 1199,"rating": 4.7, "reviews": 4321,  "badge": "",               "features": ["5K2K 5120x2160", "IPS", "Thunderbolt 4", "KVM", "Ergo Stand"]},
        {"name_en": "Jabra Evolve2 85 ANC Headset", "name_ar": "سماعات Jabra Evolve2 85",        "price": 449, "orig": 529, "rating": 4.6, "reviews": 3210,  "badge": "",               "features": ["ANC للعمل", "Busylight", "37h", "UC Certified", "8 ميكروفون"]},
        {"name_en": "Twelve South HiRise 3 Deluxe", "name_ar": "حامل Twelve South HiRise 3",    "price": 99,  "orig": 119, "rating": 4.7, "reviews": 5432,  "badge": "",               "features": ["MagSafe 15W", "حامل لاب توب", "Ergo", "iPhone+Mac", "قابل تعديل"]},
    ],
}

CAT_AR = {
    "smartwatch": "ساعات ذكية",
    "smart-glasses": "نظارات ذكية",
    "health": "صحة ذكية",
    "smart-home": "منزل ذكي",
    "earbuds": "سماعات ذكية",
    "productivity": "إنتاجية",
}

# ═══════════════════════════════════════════════════════
# Google Image Search — يجيب صورة حقيقية
# ═══════════════════════════════════════════════════════

def get_real_image(product_name: str, category: str) -> str:
    """يبحث في Google عن صورة حقيقية للمنتج"""
    try:
        params = {
            "key": GOOGLE_API_KEY,
            "cx":  GOOGLE_CX,
            "q":   f"{product_name} product official photo",
            "searchType": "image",
            "num": 5,
            "imgSize": "large",
            "imgType": "photo",
            "safe": "active",
        }
        r = requests.get(GOOGLE_SEARCH_URL, params=params, timeout=15)
        if r.status_code == 200:
            items = r.json().get("items", [])
            for item in items:
                url = item.get("link", "")
                # تجنب الروابط التي تمنع التحميل الخارجي
                blocked = ["amazon.com/images", "apple.com/", "samsung.com/", "bestbuy.com"]
                if url and not any(b in url for b in blocked):
                    if url.lower().endswith((".jpg", ".jpeg", ".png", ".webp")) or "images" in url:
                        log.info(f"✅ Image found: {product_name[:30]} → {url[:60]}")
                        return url
            # إذا ما لقينا، خذ أول نتيجة
            if items:
                return items[0].get("link", "")
    except Exception as e:
        log.warning(f"Google search error for {product_name}: {e}")
    return ""


# ═══════════════════════════════════════════════════════
# GitHub
# ═══════════════════════════════════════════════════════

def _gh_headers():
    return {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

def pull_products():
    try:
        r = requests.get(f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/{GITHUB_FILE}", headers=_gh_headers(), timeout=10)
        if r.status_code == 200:
            return json.loads(base64.b64decode(r.json()["content"]).decode()), r.json().get("sha","")
    except Exception as e:
        log.error(f"pull: {e}")
    return [], ""

def push_products(products, sha, message="🤖 Update products"):
    try:
        content = base64.b64encode(json.dumps(products, ensure_ascii=False, indent=2).encode()).decode()
        payload = {"message": message, "content": content, "branch": "main"}
        if sha: payload["sha"] = sha
        r = requests.put(f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/{GITHUB_FILE}", headers=_gh_headers(), json=payload, timeout=30)
        return r.status_code in [200, 201]
    except Exception as e:
        log.error(f"push: {e}")
        return False


# ═══════════════════════════════════════════════════════
# Telegram
# ═══════════════════════════════════════════════════════

def send(chat_id, text, token=None):
    tok = token or SUPPLIER_BOT_TOKEN
    if not tok: return
    try:
        requests.post(
            f"https://api.telegram.org/bot{tok}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
            timeout=8
        )
    except: pass


# ═══════════════════════════════════════════════════════
# Core — بناء المنتجات مع صور حقيقية
# ═══════════════════════════════════════════════════════

def fill_store(chat_id=None):
    """يملأ المتجر بـ 90 منتج مع صور حقيقية من Google"""
    if chat_id:
        send(chat_id, "⏳ جاري ملء المتجر بـ 90 منتج مع صور حقيقية من Google...\n\nهذا يأخذ 2-3 دقائق ☕")

    products = []
    counter = 1
    total_cats = len(PRODUCTS_DB)
    cat_num = 0

    for cat_id, items in PRODUCTS_DB.items():
        cat_num += 1
        cat_ar = CAT_AR[cat_id]
        if chat_id:
            send(chat_id, f"🔍 [{cat_num}/{total_cats}] جاري البحث عن صور {cat_ar}...")

        for p in items:
            pid = f"NPH-{counter:03d}"
            discount = round((1 - p["price"] / p["orig"]) * 100)

            # جيب صورة حقيقية من Google
            image_url = get_real_image(p["name_en"], cat_id)
            time.sleep(0.5)  # تجنب rate limit

            # fallback إذا ما لقينا صورة
            if not image_url:
                bg = {"smartwatch":"1e3a5f","smart-glasses":"2d1b4e","health":"0f3d2e",
                      "smart-home":"1a2f4e","earbuds":"3d1a1a","productivity":"2d2a1a"}.get(cat_id,"333333")
                short = p["name_en"][:20].replace(" ","+").replace('"','')
                image_url = f"https://placehold.co/400x400/{bg}/ffffff?text={short}"

            product = {
                "id": pid,
                "name_ar": p["name_ar"],
                "name_en": p["name_en"],
                "category": cat_id,
                "category_ar": cat_ar,
                "price": p["price"],
                "original_price": p["orig"],
                "discount": discount,
                "rating": p["rating"],
                "reviews": p["reviews"],
                "stock": random.randint(20, 100),
                "image": image_url,
                "description_ar": f"{p['name_ar']} — من أفضل منتجات {cat_ar} في السوق. جودة عالية وأداء استثنائي.",
                "features_ar": p["features"],
                "tags": [cat_ar, p["name_ar"].split()[0]],
                "badge": p.get("badge", ""),
                "active": True,
                "shipping_days": "7-14",
                "featured": p.get("badge") in ["الأكثر مبيعاً", "مميز", "حصري"],
                "added_by": "smart_bot_v4",
                "added_at": datetime.now().strftime("%Y-%m-%d"),
            }
            products.append(product)
            counter += 1
            log.info(f"✅ {pid} {p['name_en'][:40]} → {image_url[:50]}")

    # رفع لـ GitHub
    _, sha = pull_products()
    ok = push_products(products, sha, f"🤖 Fill store: {len(products)} products with real Google images")

    if chat_id:
        if ok:
            send(chat_id,
                f"✅ *تم ملء المتجر بنجاح!*\n\n"
                f"⌚ ساعات: 15\n🥽 نظارات: 15\n💪 صحة: 15\n"
                f"🏠 منزل: 15\n🎧 سماعات: 15\n💼 إنتاجية: 15\n\n"
                f"*إجمالي: {len(products)} منتج* بصور حقيقية من Google 🎯\n"
                f"🌐 https://neo-pulse-hub.it.com/products.html"
            )
        else:
            send(chat_id, "❌ فشل الرفع على GitHub")
    return products


def auto_add_products(count=5, chat_id=None):
    """يضيف منتجات جديدة بصور حقيقية"""
    products, sha = pull_products()
    existing_names = {p.get("name_en","").lower() for p in products}

    all_new = []
    for cat_id, items in PRODUCTS_DB.items():
        for p in items:
            if p["name_en"].lower() not in existing_names:
                all_new.append((cat_id, p))

    if not all_new:
        if chat_id: send(chat_id, "ℹ️ كل المنتجات موجودة أصلاً")
        return []

    random.shuffle(all_new)
    selected = all_new[:count]

    counter = max([int(p["id"].replace("NPH-","")) for p in products if p.get("id","").startswith("NPH-")] or [0]) + 1
    added = []

    for cat_id, p in selected:
        pid = f"NPH-{counter:03d}"
        discount = round((1 - p["price"] / p["orig"]) * 100)

        image_url = get_real_image(p["name_en"], cat_id)
        time.sleep(0.5)

        if not image_url:
            bg = {"smartwatch":"1e3a5f","smart-glasses":"2d1b4e","health":"0f3d2e",
                  "smart-home":"1a2f4e","earbuds":"3d1a1a","productivity":"2d2a1a"}.get(cat_id,"333333")
            short = p["name_en"][:20].replace(" ","+").replace('"','')
            image_url = f"https://placehold.co/400x400/{bg}/ffffff?text={short}"

        product = {
            "id": pid, "name_ar": p["name_ar"], "name_en": p["name_en"],
            "category": cat_id, "category_ar": CAT_AR[cat_id],
            "price": p["price"], "original_price": p["orig"], "discount": discount,
            "rating": p["rating"], "reviews": p["reviews"],
            "stock": random.randint(20,100), "image": image_url,
            "description_ar": f"{p['name_ar']} — من أفضل منتجات {CAT_AR[cat_id]}.",
            "features_ar": p["features"], "tags": [CAT_AR[cat_id], p["name_ar"].split()[0]],
            "badge": p.get("badge",""), "active": True, "shipping_days": "7-14",
            "featured": p.get("badge") in ["الأكثر مبيعاً","مميز","حصري"],
            "added_by": "auto_bot", "added_at": datetime.now().strftime("%Y-%m-%d"),
        }
        products.append(product)
        added.append(product)
        counter += 1

    if added:
        push_products(products, sha, f"🤖 Auto-add: {len(added)} products with real images")
        if chat_id:
            names = "\n".join([f"✅ `{p['id']}` {p['name_ar']}" for p in added])
            send(chat_id, f"🚀 *تمت إضافة {len(added)} منتجات بصور حقيقية:*\n\n{names}")
    return added


def fix_all_images(chat_id=None):
    """يصلح صور كل المنتجات الحالية بصور حقيقية من Google"""
    products, sha = pull_products()
    if not products:
        if chat_id: send(chat_id, "❌ لا توجد منتجات")
        return

    if chat_id: send(chat_id, f"🖼️ جاري تصليح صور {len(products)} منتج من Google...\n\nيأخذ بضع دقائق ☕")

    fixed = 0
    for p in products:
        new_img = get_real_image(p.get("name_en",""), p.get("category",""))
        time.sleep(0.5)
        if new_img:
            p["image"] = new_img
            fixed += 1
            log.info(f"✅ Fixed: {p.get('name_en','')[:40]}")

    push_products(products, sha, f"🖼️ Fix images: {fixed} real Google images")
    if chat_id: send(chat_id, f"✅ تم تصليح {fixed} صورة بصور حقيقية من Google!")


# ═══════════════════════════════════════════════════════
# Daily Scheduler Job
# ═══════════════════════════════════════════════════════

def daily_job():
    log.info("⏰ Daily auto-populate...")
    added = auto_add_products(count=5)
    log.info(f"✅ Added {len(added)} products")
    if ADMIN_USER_ID and added:
        names = "\n".join([f"• {p['name_ar']}" for p in added])
        send(ADMIN_USER_ID,
            f"🤖 *تقرير يومي*\n\nتمت إضافة {len(added)} منتجات بصور حقيقية:\n{names}\n\n"
            f"🌐 https://neo-pulse-hub.it.com/products.html"
        )


if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "fill"
    if cmd == "fill":
        fill_store()
    elif cmd == "auto":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        auto_add_products(count)
    elif cmd == "fix":
        fix_all_images()
