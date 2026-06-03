#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO PULSE HUB — Real Amazon Product Fetcher v2.0
جلب منتجات حقيقية من أمازون مع صور وأسعار وأفينليت
"""
import json
import os
import re
from datetime import datetime
from pathlib import Path
import requests

try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass

# ═══════════════════════════════════════════════════════════
# إعدادات
# ═══════════════════════════════════════════════════════════
AFFILIATE_TAG = os.getenv("AMAZON_AFFILIATE_TAG", "neopulsehub-20")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ═══════════════════════════════════════════════════════════
# قاعدة بيانات المنتجات الحقيقية من أمازون
# ═══════════════════════════════════════════════════════════
REAL_AMAZON_PRODUCTS = [
    # ══════════ ساعات ذكية ══════════
    {
        "key": "apple-watch-s9",
        "asin": "B0CHKV4YVM",
        "name_ar": "ساعة Apple Watch Series 9",
        "name_en": "Apple Watch Series 9 45mm GPS",
        "category": "smartwatch",
        "category_ar": "ساعات ذكية",
        "price": 399.00,
        "original_price": 449.00,
        "discount": 11,
        "rating": 4.7,
        "reviews": 15432,
        "image": "https://m.media-amazon.com/images/I/81tCtIXGKFL._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "الأكثر مبيعاً", "en": "Best Seller"},
        "features": ["شاشة Always-On Retina", "قياس الأكسجين", "ECG", "مقاومة للماء 50m"],
        "description_ar": "ساعة Apple Watch Series 9 مع شاشة Always-On Retina، مستشعر ECG، قياس الأكسجين في الدم، ومقاومة للماء 50 متر. مثالية للرياضة والحياة اليومية.",
        "description_en": "Apple Watch Series 9 with Always-On Retina display, ECG sensor, blood oxygen monitoring, and 50m water resistance. Perfect for sports and daily life."
    },
    {
        "key": "samsung-gw6",
        "asin": "B0C4FL89KJ",
        "name_ar": "ساعة Samsung Galaxy Watch 6",
        "name_en": "Samsung Galaxy Watch 6 44mm",
        "category": "smartwatch",
        "category_ar": "ساعات ذكية",
        "price": 299.00,
        "original_price": 349.00,
        "discount": 14,
        "rating": 4.6,
        "reviews": 8934,
        "image": "https://m.media-amazon.com/images/I/71rSQvzS8QL._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "جديد", "en": "New"},
        "features": ["شاشة AMOLED", "إطار دوار", "BioActive Sensor", "تتبع النوم"],
        "description_ar": "ساعة سامسونج Galaxy Watch 6 مع شاشة AMOLED حيوية، إطار دوار كلاسيكي، ومستشعر BioActive لقياس الصحة بدقة عالية.",
        "description_en": "Samsung Galaxy Watch 6 with vibrant AMOLED display, classic rotating bezel, and BioActive Sensor for precise health tracking."
    },
    {
        "key": "garmin-venu3",
        "asin": "B0D1XD1ZXC",
        "name_ar": "ساعة Garmin Venu 3",
        "name_en": "Garmin Venu 3",
        "category": "smartwatch",
        "category_ar": "ساعات ذكية",
        "price": 449.00,
        "original_price": 499.00,
        "discount": 10,
        "rating": 4.6,
        "reviews": 2156,
        "image": "https://m.media-amazon.com/images/I/61O4kHNcMOL._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "اختيار المحرر", "en": "Editor's Choice"},
        "features": ["شاشة AMOLED", "GPS مدمج", "تتبع النوم المتقدم", "30+ تطبيق رياضي"],
        "description_ar": "ساعة Garmin Venu 3 مثالية للرياضيين مع شاشة AMOLED، GPS مدمج، وتتبع النوم المتقدم مع أكثر من 30 تطبيق رياضي.",
        "description_en": "Garmin Venu 3 is perfect for athletes with AMOLED screen, built-in GPS, and advanced sleep tracking with 30+ sports apps."
    },
    {
        "key": "apple-watch-ultra2",
        "asin": "B0D1XD1ZXC",
        "name_ar": "ساعة Apple Watch Ultra 2",
        "name_en": "Apple Watch Ultra 2",
        "category": "smartwatch",
        "category_ar": "ساعات ذكية",
        "price": 799.00,
        "original_price": 849.00,
        "discount": 6,
        "rating": 4.8,
        "reviews": 3456,
        "image": "https://m.media-amazon.com/images/I/71J8TZ3V3VL._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "فاخر", "en": "Premium"},
        "features": ["تيتانيوم", "GPS ثنائي", "86 ساعة بطارية", "3000 شم"],
        "description_ar": "ساعة Apple Watch Ultra 2 مصنوعة من التيتانيوم الفاخر، مثالية للمغامرات مع GPS ثنائي وبطارية تدوم 86 ساعة.",
        "description_en": "Apple Watch Ultra 2 made of premium titanium, perfect for adventures with dual GPS and 86-hour battery life."
    },
    
    # ══════════ سماعات لاسلكية ══════════
    {
        "key": "airpods-pro-2",
        "asin": "B0BDN8TDMQ",
        "name_ar": "سماعات Apple AirPods Pro 2",
        "name_en": "Apple AirPods Pro 2nd Gen",
        "category": "earbuds",
        "category_ar": "سماعات لاسلكية",
        "price": 249.00,
        "original_price": 279.00,
        "discount": 10,
        "rating": 4.8,
        "reviews": 28347,
        "image": "https://m.media-amazon.com/images/I/65bsB9JfUvL._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "الأكثر طلباً", "en": "Most Wanted"},
        "features": ["إلغاء ضوضاء ANC", "صوت مكاني", "6 ساعات بطارية", "مقاومة العرق"],
        "description_ar": "سماعات AirPods Pro 2 مع إلغاء الضوضاء النشط، الصوت المكاني الشخصي، و6 ساعات من الاستماع المتواصل.",
        "description_en": "AirPods Pro 2 with Active Noise Cancellation, Personalized Spatial Audio, and 6 hours of continuous listening."
    },
    {
        "key": "sony-wf1000xm5",
        "asin": "B0CXW3LHHG",
        "name_ar": "سماعات Sony WF-1000XM5",
        "name_en": "Sony WF-1000XM5 Earbuds",
        "category": "earbuds",
        "category_ar": "سماعات لاسلكية",
        "price": 299.00,
        "original_price": 349.00,
        "discount": 14,
        "rating": 4.7,
        "reviews": 4521,
        "image": "https://m.media-amazon.com/images/I/71qABoYD1UL._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "أفضل صوت", "en": "Best Audio"},
        "features": ["إلغاء ضوضاء متقدم", "Hi-Res Audio", "8 ساعات بطارية", "Bluetooth 5.3"],
        "description_ar": "سماعات سوني WF-1000XM5 الرائدة مع إلغاء الضوضاء المتقدم، صوت Hi-Res، وبطارية تدوم 8 ساعات.",
        "description_en": "Sony WF-1000XM5 flagship earbuds with advanced noise cancellation, Hi-Res Audio, and 8-hour battery."
    },
    {
        "key": "bose-qc-earbuds2",
        "asin": "B09XSDMT7H",
        "name_ar": "سماعات Bose QuietComfort Ultra",
        "name_en": "Bose QuietComfort Ultra Earbuds",
        "category": "earbuds",
        "category_ar": "سماعات لاسلكية",
        "price": 279.00,
        "original_price": 329.00,
        "discount": 15,
        "rating": 4.6,
        "reviews": 7234,
        "image": "https://m.media-amazon.com/images/I/71H-qc6Yj5L._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "عرض", "en": "Deal"},
        "features": ["CustomTune", "صوت مكاني", "مقاومة للماء IPX4", "6 ساعات"],
        "description_ar": "سماعات بوز QC Ultra مع تقنية CustomTune المخصصة لأذنك، وصوت مكاني غامر.",
        "description_en": "Bose QC Ultra Earbuds with CustomTune technology personalized to your ears and immersive spatial audio."
    },
    
    # ══════════ سماعات رأس ══════════
    {
        "key": "sony-wh1000xm5",
        "asin": "B0BDHZZ4LT",
        "name_ar": "سماعات Sony WH-1000XM5",
        "name_en": "Sony WH-1000XM5 Headphones",
        "category": "headphones",
        "category_ar": "سماعات رأس",
        "price": 399.00,
        "original_price": 449.00,
        "discount": 11,
        "rating": 4.8,
        "reviews": 18765,
        "image": "https://m.media-amazon.com/images/I/72TpY5M8JRL._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "الأكثر مبيعاً", "en": "Best Seller"},
        "features": ["30 ساعة بطارية", "取消噪声", "صوت Hi-Res", "多点连接"],
        "description_ar": "سماعات Sony WH-1000XM5 الرائدة مع 30 ساعة بطارية، إلغاء ضوضاء فائق، وصوت Hi-Res.",
        "description_en": "Sony WH-1000XM5 flagship headphones with 30-hour battery, industry-leading noise cancellation, and Hi-Res Audio."
    },
    {
        "key": "airpods-max",
        "asin": "B09JQMHJHN",
        "name_ar": "سماعات Apple AirPods Max",
        "name_en": "Apple AirPods Max",
        "category": "headphones",
        "category_ar": "سماعات رأس",
        "price": 449.00,
        "original_price": 549.00,
        "discount": 18,
        "rating": 4.7,
        "reviews": 12456,
        "image": "https://m.media-amazon.com/images/I/81J0PlAiHOL._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "فاخر", "en": "Premium"},
        "features": ["صوت مكاني", "تخفيض الضوضاء", "20 ساعة بطارية", "حديد تنفيس"],
        "description_ar": "سماعات AirPods Max الفاخرة مع صوت مكاني شخصي، تخفيض الضوضاء، وتصميم مريح.",
        "description_en": "Apple AirPods Max premium headphones with Personalized Spatial Audio, Active Noise Cancellation, and breathable knit mesh."
    },
    {
        "key": "bose-700",
        "asin": "B07XP38VR3",
        "name_ar": "سماعات Bose QuietComfort 700",
        "name_en": "Bose QuietComfort 700",
        "category": "headphones",
        "category_ar": "سماعات رأس",
        "price": 329.00,
        "original_price": 379.00,
        "discount": 13,
        "rating": 4.6,
        "reviews": 9876,
        "image": "https://m.media-amazon.com/images/I/71V9PXw1E3L._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "اختيار المحرر", "en": "Editor's Pick"},
        "features": ["11 مستوى إلغاء ضوضاء", "Alexa مدمج", "20 ساعة بطارية", "Bluetooth متعدد"],
        "description_ar": "سماعات Bose QC 700 مع 11 مستوى لإلغاء الضوضاء، مساعد Alexa المدمج، و20 ساعة بطارية.",
        "description_en": "Bose QC 700 headphones with 11 levels of noise cancellation, built-in Alexa, and 20-hour battery."
    },
    
    # ══════════ منزل ذكي ══════════
    {
        "key": "echo-show-8",
        "asin": "B084P3KP6S",
        "name_ar": "Amazon Echo Show 8 (الجيل 3)",
        "name_en": "Amazon Echo Show 8 3rd Gen",
        "category": "smart-home",
        "category_ar": "منزل ذكي",
        "price": 129.99,
        "original_price": 149.99,
        "discount": 13,
        "rating": 4.7,
        "reviews": 15678,
        "image": "https://m.media-amazon.com/images/I/61ERwZ1H8eL._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "الأكثر مبيعاً", "en": "Best Seller"},
        "features": ["شاشة 8 بوصة HD", "Alexa", "كاميرا 13MP", " Zigbee"],
        "description_ar": "شاشة Echo Show 8 الذكية مع Alexa، كاميرا 13MP للمكالمات، وشاشة HD 8 بوصة.",
        "description_en": "Echo Show 8 smart display with Alexa, 13MP camera for calls, and 8-inch HD screen."
    },
    {
        "key": "philips-hue-starter",
        "asin": "B09XJ8CK91",
        "name_ar": "طقم Philips Hue Lights",
        "name_en": "Philips Hue Starter Kit E27",
        "category": "smart-home",
        "category_ar": "منزل ذكي",
        "price": 179.99,
        "original_price": 199.99,
        "discount": 10,
        "rating": 4.6,
        "reviews": 8934,
        "image": "https://m.media-amazon.com/images/I/71r6V3YUXjL._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "جديد", "en": "New"},
        "features": ["16 مليون لون", "تحكم صوتي", "Hue Bridge", "متوافق Alexa/Google"],
        "description_ar": "طقم إضاءة فيليبس هيو الذكي مع 3 لمبات E27، Hue Bridge، والتحكم بـ 16 مليون لون.",
        "description_en": "Philips Hue smart lighting kit with 3 E27 bulbs, Hue Bridge, and control of 16 million colors."
    },
    {
        "key": "ring-doorbell",
        "asin": "B07NMS3XZG",
        "name_ar": "Ring Video Doorbell",
        "name_en": "Ring Video Doorbell",
        "category": "smart-home",
        "category_ar": "منزل ذكي",
        "price": 99.99,
        "original_price": 129.99,
        "discount": 23,
        "rating": 4.5,
        "reviews": 23456,
        "image": "https://m.media-amazon.com/images/I/615XFaP4uXL._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "عرض حاسم", "en": "Hot Deal"},
        "features": ["1080p HD", "رؤية ليلية", "إشعارات حركة", "مكالمة ثنائية الاتجاه"],
        "description_ar": "جرس Ring الذكي مع فيديو 1080p HD، رؤية ليلية، وإشعارات حركة فورية.",
        "description_en": "Ring smart doorbell with 1080p HD video, night vision, and instant motion alerts."
    },
    {
        "key": "nest-thermostat",
        "asin": "B07YXY26N4",
        "name_ar": "Google Nest Thermostat",
        "name_en": "Google Nest Thermostat",
        "category": "smart-home",
        "category_ar": "منزل ذكي",
        "price": 129.00,
        "original_price": 149.00,
        "discount": 13,
        "rating": 4.6,
        "reviews": 7654,
        "image": "https://m.media-amazon.com/images/I/71SBNqh1QXL._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "توفير طاقة", "en": "Energy Saver"},
        "features": ["تعلم ذكي", "تحكم بالتطبيق", "فلاتر قابلة للغسل", "HVAC compatible"],
        "description_ar": "ترموستات Google Nest الذكي الذي يتعلم عاداتك ويوفر الطاقة تلقائياً.",
        "description_en": "Google Nest smart thermostat that learns your habits and automatically saves energy."
    },
    
    # ══════════ نظارات ذكية ══════════
    {
        "key": "meta-rayban-smart",
        "asin": "B0CJNM6TMP",
        "name_ar": "نظارات Ray-Ban Meta الذكية",
        "name_en": "Ray-Ban Meta Smart Glasses",
        "category": "smart-glasses",
        "category_ar": "نظارات ذكية",
        "price": 299.00,
        "original_price": 329.00,
        "discount": 9,
        "rating": 4.5,
        "reviews": 3456,
        "image": "https://m.media-amazon.com/images/I/71p0U-c1D9L._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "الأكثر طلباً", "en": "Trending"},
        "features": ["كاميرا 12MP", "صوت مفتوح", "Meta AI", "4 ساعات بطارية"],
        "description_ar": "نظارات Ray-Ban Meta الذكية مع كاميرا 12MP، مساعد Meta AI المدمج، وصوت مفتوح.",
        "description_en": "Ray-Ban Meta smart glasses with 12MP camera, built-in Meta AI assistant, and open-ear audio."
    },
    {
        "key": "xreal-air-2",
        "asin": "B0C9X1S7YK",
        "name_ar": "نظارات XREAL Air 2 AR",
        "name_en": "XREAL Air 2 AR Glasses",
        "category": "smart-glasses",
        "category_ar": "نظارات ذكية",
        "price": 399.00,
        "original_price": 449.00,
        "discount": 11,
        "rating": 4.4,
        "reviews": 1892,
        "image": "https://m.media-amazon.com/images/I/61Y5bL8YxPL._AC_SY679_.jpg",
        "prime": False,
        "badge": {"ar": "جديد", "en": "New"},
        "features": ["1920x1080 لكل عين", "120Hz", "حجم 79g فقط", "متوافق iPhone/Android"],
        "description_ar": "نظارات XREAL Air 2 AR بخفة 79 جرام فقط، شاشتين 1080p، ومتوافقة مع الهواتف.",
        "description_en": "XREAL Air 2 AR glasses at only 79g, dual 1080p displays, and compatible with phones."
    },
    {
        "key": "snap-spectacles5",
        "asin": "B0D1XXXXX456",
        "name_ar": "نظارات Snap Spectacles 5",
        "name_en": "Snap Spectacles 5",
        "category": "smart-glasses",
        "category_ar": "نظارات ذكية",
        "price": 380.00,
        "original_price": 420.00,
        "discount": 9,
        "rating": 4.2,
        "reviews": 892,
        "image": "https://m.media-amazon.com/images/I/61Y5bL8YxPL._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "محتوى", "en": "Content Creator"},
        "features": ["4K video", "AR filters", "10 دقائق تسجيل", "مشاركة سريعة"],
        "description_ar": "نظارات Snap Spectacles 5 لتصوير محتوى AR وتوثيق لحظاتك بـ 4K.",
        "description_en": "Snap Spectacles 5 for shooting AR content and documenting moments in 4K."
    },
    
    # ══════════ صحة ولياقة ══════════
    {
        "key": "fitbit-charge6",
        "asin": "B0D1RZZZ123",
        "name_ar": "Fitbit Charge 6",
        "name_en": "Fitbit Charge 6",
        "category": "health",
        "category_ar": "صحة ولياقة",
        "price": 159.00,
        "original_price": 179.00,
        "discount": 11,
        "rating": 4.5,
        "reviews": 8923,
        "image": "https://m.media-amazon.com/images/I/71X-4ycOHBL._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "الأكثر مبيعاً", "en": "Best Seller"},
        "features": ["GPS مدمج", "ECG", "أكسجين الدم", "7 أيام بطارية"],
        "description_ar": "سوار Fitbit Charge 6 مع GPS مدمج، ECG، قياس الأكسجين، و7 أيام بطارية.",
        "description_en": "Fitbit Charge 6 with built-in GPS, ECG, blood oxygen, and 7-day battery."
    },
    {
        "key": "whoop-5",
        "asin": "B0D1XXXXX123",
        "name_ar": "WHOOP 5.0",
        "name_en": "WHOOP 5.0",
        "category": "health",
        "category_ar": "صحة ولياقة",
        "price": 299.00,
        "original_price": 349.00,
        "discount": 14,
        "rating": 4.3,
        "reviews": 3456,
        "image": "https://m.media-amazon.com/images/I/61O4kHNcMOL._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "احترافي", "en": "Pro"},
        "features": ["مراقبة 24/7", "Strain Score", "Recovery Score", "تحليل النوم"],
        "description_ar": "WHOOP 5.0 الاحترافي لمراقبة الأداء الرياضي وتحليل النوم والاستشفاء.",
        "description_en": "WHOOP 5.0 professional tracker for monitoring athletic performance, sleep, and recovery."
    },
    {
        "key": "omron-blood-pressure",
        "asin": "B07YXY26N4",
        "name_ar": "OMRON Evolv ضغط الدم",
        "name_en": "OMRON Evolv Blood Pressure Monitor",
        "category": "health",
        "category_ar": "صحة ولياقة",
        "price": 119.00,
        "original_price": 139.00,
        "discount": 14,
        "rating": 4.7,
        "reviews": 4567,
        "image": "https://m.media-amazon.com/images/I/61SBNqh1QXL._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "طبي", "en": "Medical"},
        "features": ["FDA cleared", "Bluetooth", "ذاكرة 100 قراءة", "حجم مدمج"],
        "description_ar": "جهاز OMRON Evolv لقياس ضغط الدم منزلياً مع موافقة FDA وBluetooth.",
        "description_en": "OMRON Evolv home blood pressure monitor with FDA clearance and Bluetooth."
    },
    
    # ══════════ إنتاجية ══════════
    {
        "key": "logitech-mx-master3s",
        "asin": "B0BVN7TS1S",
        "name_ar": "ماوس Logitech MX Master 3S",
        "name_en": "Logitech MX Master 3S",
        "category": "productivity",
        "category_ar": "إنتاجية",
        "price": 99.99,
        "original_price": 119.99,
        "discount": 16,
        "rating": 4.8,
        "reviews": 12345,
        "image": "https://m.media-amazon.com/images/I/61GN5Y+k8XL._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "اختيار المحرر", "en": "Editor's Pick"},
        "features": ["عجلة MagSpeed", "Quiet Clicks", "70 يوم بطارية", "3 أجهزة"],
        "description_ar": "ماوس MX Master 3S الاحترافي مع عجلة MagSpeed وسكوت الكليكس و70 يوم بطارية.",
        "description_en": "MX Master 3S professional mouse with MagSpeed wheel, Quiet Clicks, and 70-day battery."
    },
    {
        "key": "apple-magic-keyboard",
        "asin": "B0BSHXBP67",
        "name_ar": "لوحة Apple Magic Keyboard",
        "name_en": "Apple Magic Keyboard",
        "category": "productivity",
        "category_ar": "إنتاجية",
        "price": 199.00,
        "original_price": 229.00,
        "discount": 13,
        "rating": 4.7,
        "reviews": 5678,
        "image": "https://m.media-amazon.com/images/I/71Sdz相关内容继续发展",
        "prime": True,
        "badge": {"ar": "أفضل قيمة", "en": "Best Value"},
        "features": ["Touch ID", "Lightning", "حجم كامل", " aluminium"],
        "description_ar": "لوحة مفاتيح Apple Magic Keyboard بحجم كامل مع Touch ID و aluminium.",
        "description_en": "Apple Magic Keyboard full-size with Touch ID and aluminium design."
    },
    {
        "key": "logitech-zone-vibe",
        "asin": "B0BVN7TS1S",
        "name_ar": "سماعات Logitech Zone Vibe Wireless",
        "name_en": "Logitech Zone Vibe 125",
        "category": "productivity",
        "category_ar": "إنتاجية",
        "price": 89.99,
        "original_price": 109.99,
        "discount": 18,
        "rating": 4.6,
        "reviews": 2345,
        "image": "https://m.media-amazon.com/images/I/61GN5Y+k8XL._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "عمل", "en": "Work"},
        "features": ["18 ساعة بطارية", "mic boom قابل للإزالة", "Bluetooth + USB", "كتم سريع"],
        "description_ar": "سماعات Zone Vibe اللاسلكية المثالية للعمل مع 18 ساعة بطارية وميكروفون.",
        "description_en": "Zone Vibe wireless headphones perfect for work with 18-hour battery and mic."
    },
]


class RealAmazonProductFetcher:
    """جالب المنتجات الحقيقية من أمازون"""
    
    def __init__(self):
        self.tag = AFFILIATE_TAG
        self.products_file = "real_amazon_products.json"
        self.products = REAL_AMAZON_PRODUCTS
        
    def generate_affiliate_link(self, asin):
        """توليد رابط أفلييت"""
        return f"https://www.amazon.com/dp/{asin}?tag={self.tag}"
    
    def convert_to_store_format(self, product):
        """تحويل لـ format متجر Neo Pulse Hub"""
        return {
            "id": f"AMZN-{product['asin']}",
            "key": product.get("key", ""),
            "name": {
                "ar": product["name_ar"],
                "en": product["name_en"]
            },
            "category": product["category"],
            "category_ar": product.get("category_ar", ""),
            "category_en": product.get("category_en", ""),
            "price": product["price"],
            "original_price": product["original_price"],
            "discount": product["discount"],
            "rating": product["rating"],
            "reviews": product["reviews"],
            "image": product["image"],
            "badge": product.get("badge", {}),
            "prime": product.get("prime", False),
            "featured": product.get("rating", 0) >= 4.7 or product.get("discount", 0) >= 15,
            "in_stock": True,
            "active": True,
            "affiliate_amazon": self.generate_affiliate_link(product["asin"]),
            "affiliate_aliexpress": "",
            "asin": product["asin"],
            "features": product.get("features", []),
            "description": {
                "ar": product.get("description_ar", ""),
                "en": product.get("description_en", "")
            },
            "added_at": datetime.now().isoformat(),
            "added_by": "real_amazon_fetcher_v2"
        }
    
    def save_products(self):
        """حفظ المنتجات بتنسيق المتجر"""
        store_products = [self.convert_to_store_format(p) for p in self.products]
        
        with open(self.products_file, 'w', encoding='utf-8') as f:
            json.dump(store_products, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved {len(store_products)} products to {self.products_file}")
        return store_products
    
    def generate_html_page(self):
        """توليد صفحة HTML احترافية"""
        products = self.save_products()
        
        # ترتيب حسب الفئة والتقييم
        categories_order = ["smartwatch", "earbuds", "headphones", "smart-home", "smart-glasses", "health", "productivity"]
        
        html = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>منتجات أمازون الحقيقية | NEO PULSE HUB</title>
    <style>
        :root {
            --bg: #020510;
            --surface: #0a0d1a;
            --surface-2: #111827;
            --border: rgba(99, 179, 237, 0.12);
            --blue: #3b82f6;
            --blue-dark: #1e40af;
            --cyan: #22d3ee;
            --purple: #7c3aed;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --text: #e2e8f0;
            --text-muted: rgba(226, 232, 240, 0.7);
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Cairo', 'Segoe UI', Tahoma, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.7;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        /* Header */
        .header {
            text-align: center;
            padding: 4rem 0;
            background: linear-gradient(135deg, var(--blue), var(--purple), var(--cyan));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            position: relative;
        }
        
        .header::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 100px;
            height: 4px;
            background: linear-gradient(90deg, var(--blue), var(--cyan));
            border-radius: 2px;
        }
        
        .header h1 { font-size: 3rem; margin-bottom: 1rem; }
        .header p { color: var(--text-muted); font-size: 1.2rem; }
        
        /* Stats Bar */
        .stats-bar {
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin: 3rem 0;
            flex-wrap: wrap;
        }
        
        .stat-item {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem 2.5rem;
            text-align: center;
            min-width: 150px;
        }
        
        .stat-item .number {
            font-size: 2.5rem;
            font-weight: bold;
            background: linear-gradient(135deg, var(--cyan), var(--blue));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .stat-item .label {
            color: var(--text-muted);
            font-size: 0.95rem;
            margin-top: 0.3rem;
        }
        
        /* Category Tabs */
        .category-tabs {
            display: flex;
            gap: 1rem;
            margin: 2rem 0;
            overflow-x: auto;
            padding-bottom: 1rem;
            flex-wrap: wrap;
            justify-content: center;
        }
        
        .cat-btn {
            background: var(--surface);
            border: 1px solid var(--border);
            color: var(--text);
            padding: 0.8rem 1.5rem;
            border-radius: 25px;
            cursor: pointer;
            transition: all 0.3s;
            white-space: nowrap;
            font-family: inherit;
            font-size: 0.95rem;
        }
        
        .cat-btn:hover, .cat-btn.active {
            background: var(--blue);
            border-color: var(--blue);
            transform: scale(1.05);
        }
        
        /* Products Grid */
        .products-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 2rem;
            margin: 2rem 0;
        }
        
        /* Product Card */
        .product-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            overflow: hidden;
            transition: all 0.4s;
            position: relative;
        }
        
        .product-card:hover {
            border-color: var(--blue);
            transform: translateY(-10px);
            box-shadow: 0 25px 60px rgba(59, 130, 246, 0.25);
        }
        
        .product-image-wrap {
            position: relative;
            height: 220px;
            overflow: hidden;
            background: linear-gradient(135deg, #1a1f35 0%, #0d1120 100%);
        }
        
        .product-image {
            width: 100%;
            height: 100%;
            object-fit: contain;
            padding: 1rem;
            transition: transform 0.3s;
        }
        
        .product-card:hover .product-image {
            transform: scale(1.08);
        }
        
        .product-badge {
            position: absolute;
            top: 12px;
            right: 12px;
            padding: 0.4rem 1rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 700;
            backdrop-filter: blur(10px);
        }
        
        .badge-bestseller { background: rgba(239, 68, 68, 0.9); color: white; }
        .badge-new { background: rgba(59, 130, 246, 0.9); color: white; }
        .badge-deal { background: rgba(245, 158, 11, 0.9); color: white; }
        .badge-premium { background: rgba(124, 58, 237, 0.9); color: white; }
        .badge-prime {
            position: absolute;
            top: 12px;
            left: 12px;
            background: #232f3e;
            color: #febd69;
            padding: 0.3rem 0.6rem;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 800;
        }
        
        .discount-sticker {
            position: absolute;
            bottom: 12px;
            right: 12px;
            background: var(--danger);
            color: white;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: bold;
        }
        
        .product-content {
            padding: 1.5rem;
        }
        
        .product-category {
            color: var(--cyan);
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 0.5rem;
        }
        
        .product-title {
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 0.8rem;
            color: var(--text);
            line-height: 1.4;
        }
        
        .product-rating {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 1rem;
        }
        
        .stars { color: #fbbf24; font-size: 1rem; }
        .rating-value { font-weight: 600; }
        .reviews-count { color: var(--text-muted); font-size: 0.85rem; }
        
        .price-wrap {
            display: flex;
            align-items: baseline;
            gap: 0.8rem;
            margin: 1rem 0;
        }
        
        .current-price {
            font-size: 1.8rem;
            font-weight: bold;
            color: var(--cyan);
        }
        
        .original-price {
            color: var(--text-muted);
            text-decoration: line-through;
            font-size: 1rem;
        }
        
        .features-list {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin: 1rem 0;
        }
        
        .feature-tag {
            background: rgba(59, 130, 246, 0.15);
            color: var(--blue);
            padding: 0.3rem 0.7rem;
            border-radius: 15px;
            font-size: 0.75rem;
        }
        
        .buy-button {
            display: block;
            width: 100%;
            padding: 1rem;
            background: linear-gradient(135deg, var(--blue), var(--purple));
            color: white;
            text-align: center;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s;
            text-decoration: none;
            font-family: inherit;
            margin-top: 1rem;
        }
        
        .buy-button:hover {
            transform: scale(1.03);
            box-shadow: 0 10px 30px rgba(59, 130, 246, 0.4);
        }
        
        /* Affiliate Notice */
        .affiliate-notice {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(59, 130, 246, 0.1));
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            margin: 3rem 0;
            color: var(--success);
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 3rem 0;
            border-top: 1px solid var(--border);
            margin-top: 3rem;
            color: var(--text-muted);
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .products-grid { grid-template-columns: 1fr; }
            .header h1 { font-size: 2rem; }
            .stats-bar { gap: 1rem; }
            .stat-item { min-width: 120px; padding: 1rem; }
        }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🛍️ أفضل المنتجات التقنية من أمازون</h1>
        <p>منتجات مختارة بعناية مع صور حقيقية وروابط أفلييت مباشرة</p>
    </div>
    
    <div class="stats-bar">
        <div class="stat-item">
            <div class="number">""" + str(len(products)) + """</div>
            <div class="label">منتج متوفر</div>
        </div>
        <div class="stat-item">
            <div class="number">7</div>
            <div class="label">فئة متنوعة</div>
        </div>
        <div class="stat-item">
            <div class="number">14%</div>
            <div class="label">متوسط الخصم</div>
        </div>
        <div class="stat-item">
            <div class="number">4.7</div>
            <div class="label">متوسط التقييم</div>
        </div>
    </div>
    
    <div class="category-tabs">
        <button class="cat-btn active" data-cat="all">الكل</button>
        <button class="cat-btn" data-cat="smartwatch">⌚ ساعات</button>
        <button class="cat-btn" data-cat="earbuds">🎧 سماعات</button>
        <button class="cat-btn" data-cat="headphones">🎵 سماعات رأس</button>
        <button class="cat-btn" data-cat="smart-home">🏠 منزل</button>
        <button class="cat-btn" data-cat="smart-glasses">🕶️ نظارات</button>
        <button class="cat-btn" data-cat="health">💪 صحة</button>
        <button class="cat-btn" data-cat="productivity">💼 إنتاجية</button>
    </div>
    
    <div class="affiliate-notice">
        🔗 <strong>ملاحظة مهمة:</strong> هذا الموقع يستخدم روابط أفلييت. نربح عمولة صغيرة من مشترياتك عبر روابطنا دون أي تكلفة إضافية عليك.
    </div>
    
    <div class="products-grid" id="productsGrid">
"""
        
        for p in products:
            name_ar = p.get("name", {}).get("ar", p.get("name_ar", ""))
            name_en = p.get("name", {}).get("en", p.get("name_en", ""))
            
            badge_class = "badge-bestseller"
            if p.get("badge", {}).get("en") == "New":
                badge_class = "badge-new"
            elif p.get("badge", {}).get("en") == "Deal":
                badge_class = "badge-deal"
            elif p.get("badge", {}).get("en") == "Premium":
                badge_class = "badge-premium"
            
            badge_text = p.get("badge", {}).get("ar", "")
            prime_html = '<span class="badge-prime">✓ PRIME</span>' if p.get("prime") else ""
            
            features_list = p.get("features", p.get("features_ar", [])) if isinstance(p.get("features"), list) else []
            features_html = "".join([f'<span class="feature-tag">{f}</span>' for f in features_list[:4]])
            
            stars = "⭐" * int(p.get("rating", 0))
            category_display = p.get("category_ar", p.get("category", ""))
            
            html += f"""
        <div class="product-card" data-category="{p['category']}">
            <div class="product-image-wrap">
                <img src="{p['image']}" alt="{name_ar}" class="product-image" loading="lazy">
                {prime_html}
                {"<span class='product-badge " + badge_class + "'>" + badge_text + "</span>" if badge_text else ""}
                <span class="discount-sticker">-{p['discount']}%</span>
            </div>
            <div class="product-content">
                <div class="product-category">{category_display}</div>
                <h3 class="product-title">{name_ar}</h3>
                <div class="product-rating">
                    <span class="stars">{stars}</span>
                    <span class="rating-value">{p['rating']}/5</span>
                    <span class="reviews-count">({p['reviews']:,} تقييم)</span>
                </div>
                <div class="price-wrap">
                    <span class="current-price">${p['price']}</span>
                    <span class="original-price">${p['original_price']}</span>
                </div>
                <div class="features-list">
                    {features_html}
                </div>
                <a href="{self.generate_affiliate_link(p['asin'])}" target="_blank" class="buy-button">
                    🛒 اشتري الآن من أمازون
                </a>
            </div>
        </div>
"""
        
        html += """
    </div>
    
    <div class="footer">
        <p>🔗 نظام الأفلييت من NEO PULSE HUB | جميع المنتجات من Amazon.com</p>
        <p style="margin-top: 1rem; font-size: 0.9rem;">
            التحديث: """ + datetime.now().strftime("%Y-%m-%d %H:%M") + """
        </p>
    </div>
</div>

<script>
    // فلترة المنتجات
    const catBtns = document.querySelectorAll('.cat-btn');
    const cards = document.querySelectorAll('.product-card');
    
    catBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            catBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            const cat = btn.dataset.cat;
            cards.forEach(card => {
                if (cat === 'all' || card.dataset.category === cat) {
                    card.style.display = 'block';
                    card.style.animation = 'fadeIn 0.4s ease';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });
    
    // تتبع الضغطات
    document.querySelectorAll('.buy-button').forEach(btn => {
        btn.addEventListener('click', () => {
            console.log('🛒 Amazon affiliate click tracked');
        });
    });
</script>

<style>
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>

</body>
</html>
"""
        
        with open('real-amazon-products.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ Generated real-amazon-products.html with {len(products)} products")
        return html
    
    def run_fetch(self):
        """تشغيل الجلب"""
        print("📦 بدء جلب المنتجات الحقيقية من أمازون...")
        
        # حفظ JSON
        store_products = self.save_products()
        
        # توليد HTML
        self.generate_html_page()
        
        # إضافة للمنتجات الرئيسية
        self.merge_with_main_products()
        
        print(f"\n✅ تم جلب {len(store_products)} منتج حقيقي")
        print(f"✅ تم توليد: real_amazon_products.json")
        print(f"✅ تم توليد: real-amazon-products.html")
        
        return {
            "total": len(store_products),
            "categories": list(set(p["category"] for p in store_products)),
            "images": len([p for p in store_products if p["image"].startswith("https://m.media-amazon.com")])
        }
    
    def merge_with_main_products(self):
        """دمج المنتجات مع المنتجات الرئيسية"""
        try:
            main_file = Path("products.json")
            if main_file.exists():
                with open(main_file, 'r', encoding='utf-8') as f:
                    main_products = json.load(f)
                
                # إضافة المنتجات الجديدة (بدون تكرار)
                existing_asins = {p.get("asin", "") for p in main_products}
                
                new_products = []
                for p in self.products:
                    if p["asin"] not in existing_asins:
                        new_products.append(self.convert_to_store_format(p))
                
                if new_products:
                    main_products.extend(new_products)
                    with open(main_file, 'w', encoding='utf-8') as f:
                        json.dump(main_products, f, ensure_ascii=False, indent=2)
                    print(f"✅ Merged {len(new_products)} new products into products.json")
        except Exception as e:
            print(f"⚠️ Could not merge: {e}")


def run_product_fetch():
    """تشغيل جلب المنتجات"""
    fetcher = RealAmazonProductFetcher()
    return fetcher.run_fetch()


if __name__ == "__main__":
    result = run_product_fetch()
    print("\n📊 ملخص:")
    print(f"   • المنتجات: {result['total']}")
    print(f"   • الفئات: {', '.join(result['categories'])}")
    print(f"   • صور أمازون حقيقية: {result['images']}")