#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO PULSE HUB — Smart Supplier Bot v5.0
يجيب صور حقيقية + يرفعها على GitHub + ينزل المنتجات تلقائياً
"""

import os, json, base64, requests, time, re, logging, random, io
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
GOOGLE_API_KEY     = os.environ.get("GOOGLE_API_KEY", "AIzaSyBjH8OXjZ9r_tvB4z9miqlncdvVuRsfWiU")
GOOGLE_CX          = os.environ.get("GOOGLE_CX", "53f17b4ecf9924a25")

GITHUB_API         = "https://api.github.com"
GOOGLE_SEARCH_URL  = "https://www.googleapis.com/customsearch/v1"
RAW_BASE           = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main"

logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
log = logging.getLogger("smart_supplier")

# ═══════════════════════════════════════════════════════
# قاعدة بيانات المنتجات
# ═══════════════════════════════════════════════════════
PRODUCTS_DB = {
    "smartwatch": [
        {"name_en":"Apple Watch Series 9 45mm","name_ar":"ساعة أبل Watch Series 9","price":399,"orig":449,"rating":4.9,"reviews":12430,"badge":"الأكثر مبيعاً","features":["شاشة Retina","GPS+Cellular","مقاوم للماء 50م","تتبع صحي","18 ساعة"]},
        {"name_en":"Samsung Galaxy Watch 7 44mm","name_ar":"ساعة سامسونج Galaxy Watch 7","price":299,"orig":349,"rating":4.8,"reviews":8765,"badge":"مميز","features":["Exynos W1000","نوم AI","40 ساعة","MIL-STD-810","لياقة"]},
        {"name_en":"Garmin Fenix 7X Solar","name_ar":"ساعة غارمن Fenix 7X Solar","price":699,"orig":799,"rating":4.8,"reviews":5432,"badge":"","features":["شحن شمسي","GPS متعدد","37 يوم","خرائط توبو","مغامرات"]},
        {"name_en":"Apple Watch Ultra 2","name_ar":"ساعة أبل Watch Ultra 2","price":799,"orig":899,"rating":4.9,"reviews":4321,"badge":"حصري","features":["تيتانيوم","60 ساعة","86dB","100م","GPS دقيق"]},
        {"name_en":"Google Pixel Watch 3 45mm","name_ar":"ساعة غوغل Pixel Watch 3","price":349,"orig":399,"rating":4.7,"reviews":3210,"badge":"جديد","features":["Wear OS 4","AMOLED","Google Wallet","24 ساعة","ECG"]},
        {"name_en":"Xiaomi Watch S3","name_ar":"ساعة شاومي Watch S3","price":139,"orig":169,"rating":4.5,"reviews":6543,"badge":"قيمة مثالية","features":["AMOLED 1.43","12 أيام","GPS","150 رياضة","5ATM"]},
        {"name_en":"Amazfit Balance","name_ar":"ساعة أمازفيت Balance","price":229,"orig":269,"rating":4.6,"reviews":2876,"badge":"","features":["Zepp OS 3","14 أيام","AI صحي","AMOLED","GPS L1+L5"]},
        {"name_en":"Samsung Galaxy Watch Ultra","name_ar":"ساعة سامسونج Galaxy Watch Ultra","price":649,"orig":749,"rating":4.8,"reviews":1987,"badge":"جديد","features":["تيتانيوم","60 ساعة","MIL-STD","10ATM","GPS مزدوج"]},
        {"name_en":"Fitbit Versa 4","name_ar":"ساعة فيتبيت Versa 4","price":149,"orig":199,"rating":4.5,"reviews":9876,"badge":"","features":["Alexa","GPS","6 أيام","نوم","40 تمرين"]},
        {"name_en":"Garmin Venu 3S","name_ar":"ساعة غارمن Venu 3S","price":449,"orig":499,"rating":4.7,"reviews":3456,"badge":"","features":["AMOLED","AI جسم","Body Battery","سكر دم","GPS"]},
        {"name_en":"OnePlus Watch 3","name_ar":"ساعة ون بلس Watch 3","price":329,"orig":379,"rating":4.6,"reviews":2134,"badge":"","features":["Wear OS 4","100 ساعة","شحن سريع","GPS مزدوج","5ATM"]},
        {"name_en":"Huawei Watch GT 5 Pro","name_ar":"ساعة هواوي Watch GT 5 Pro","price":349,"orig":399,"rating":4.7,"reviews":4567,"badge":"","features":["تيتانيوم","14 يوم","صحي شامل","GPS مزدوج","خرائط"]},
        {"name_en":"Withings ScanWatch 2","name_ar":"ساعة ويذينغز ScanWatch 2","price":299,"orig":349,"rating":4.6,"reviews":1876,"badge":"","features":["ECG","SpO2","30 يوم","كلاسيكي","FDA"]},
        {"name_en":"TicWatch Pro 5 Enduro","name_ar":"ساعة تيكووتش Pro 5 Enduro","price":399,"orig":449,"rating":4.6,"reviews":1234,"badge":"","features":["Snapdragon W5+","مزدوج","80 ساعة","Wear OS","MIL-STD"]},
        {"name_en":"Coros Apex 2 Pro","name_ar":"ساعة كوروس Apex 2 Pro","price":499,"orig":599,"rating":4.8,"reviews":2345,"badge":"","features":["GPS متعدد","75 ساعة","توبو","شحن سريع","تيتانيوم"]},
    ],
    "smart-glasses": [
        {"name_en":"Apple Vision Pro","name_ar":"نظارة Apple Vision Pro","price":3499,"orig":3999,"rating":4.8,"reviews":4532,"badge":"حصري","features":["micro-OLED 4K","visionOS","R1 Chip","3D كاميرا","انغماس كامل"]},
        {"name_en":"Meta Quest 3 512GB","name_ar":"نظارة Meta Quest 3","price":649,"orig":749,"rating":4.8,"reviews":15432,"badge":"الأكثر مبيعاً","features":["Snapdragon XR2 Gen 2","Mixed Reality","Pancake","Meta Store","2.2h"]},
        {"name_en":"Ray-Ban Meta Wayfarer","name_ar":"نظارة Ray-Ban Meta الذكية","price":329,"orig":379,"rating":4.5,"reviews":8765,"badge":"مميز","features":["كاميرا 12MP","مفتوحة","BT 5.3","Meta AI","4 ساعات"]},
        {"name_en":"Meta Quest 3S 128GB","name_ar":"نظارة Meta Quest 3S","price":299,"orig":349,"rating":4.7,"reviews":6543,"badge":"جديد","features":["XR2 Gen 2","Mixed Reality","128GB","أخف","Meta Store"]},
        {"name_en":"XREAL Air 2 Pro","name_ar":"نظارة XREAL Air 2 Pro","price":449,"orig":499,"rating":4.6,"reviews":3210,"badge":"","features":["330 بوصة","120Hz","Electrochromic","USB-C","72g"]},
        {"name_en":"HTC Vive XR Elite","name_ar":"نظارة HTC Vive XR Elite","price":999,"orig":1199,"rating":4.6,"reviews":1876,"badge":"","features":["XR2 Gen 1","4K+","Viveport","قابل للخلع","2h"]},
        {"name_en":"Pico 4 Ultra VR","name_ar":"نظارة Pico 4 Ultra","price":599,"orig":699,"rating":4.5,"reviews":2345,"badge":"","features":["XR2 Gen 2","Spatial Video","Hand Tracking","3GB","3h"]},
        {"name_en":"Snap Spectacles 5th Gen","name_ar":"نظارة Snap Spectacles الجيل 5","price":399,"orig":449,"rating":4.3,"reviews":1234,"badge":"","features":["AR","كاميرا ثنائية","Snapchat","Lens Studio","30 دقيقة"]},
        {"name_en":"XREAL Beam Pro","name_ar":"نظارة XREAL Beam Pro","price":599,"orig":699,"rating":4.5,"reviews":1543,"badge":"","features":["Spatial Computing","كاميرتان","Android 13","3D","5000mAh"]},
        {"name_en":"Vuzix Z100 AR Glasses","name_ar":"نظارة Vuzix Z100 الذكية","price":699,"orig":799,"rating":4.3,"reviews":543,"badge":"","features":["Waveguide AR","AR1","8h","Android 11","Hands-free"]},
        {"name_en":"TCL NXTWEAR S2 Plus","name_ar":"نظارة TCL NXTWEAR S2 Plus","price":379,"orig":429,"rating":4.4,"reviews":876,"badge":"","features":["105 بوصة","1080p","USB-C","72g","120Hz"]},
        {"name_en":"Inmo Air 2 Smart Glasses","name_ar":"نظارة Inmo Air 2 الذكية","price":399,"orig":449,"rating":4.2,"reviews":654,"badge":"","features":["ChatGPT","ترجمة","27g","9h","Waveguide"]},
        {"name_en":"Rokid Max 2 AR","name_ar":"نظارة Rokid Max 2","price":549,"orig":629,"rating":4.5,"reviews":987,"badge":"","features":["Micro-OLED 1080p","120Hz","4700nit","Spatial Audio","USB-C"]},
        {"name_en":"Viture One XR Glasses","name_ar":"نظارة Viture One XR","price":439,"orig":499,"rating":4.4,"reviews":765,"badge":"","features":["135 بوصة","Electrochromic","Cinema","2K","77g"]},
        {"name_en":"Meta Ray-Ban Skyler Glasses","name_ar":"نظارة Meta Ray-Ban Skyler","price":349,"orig":399,"rating":4.5,"reviews":3210,"badge":"","features":["12MP Ultra Wide","AI","BT 5.3","6h","مفتوحة"]},
    ],
    "health": [
        {"name_en":"Oura Ring Gen 4","name_ar":"خاتم Oura Ring الجيل 4","price":349,"orig":399,"rating":4.8,"reviews":18765,"badge":"الأكثر مبيعاً","features":["نوم دقيق","Readiness","8 أيام","SpO2","Ring AI"]},
        {"name_en":"WHOOP 4.0 Fitness Band","name_ar":"حزام WHOOP 4.0","price":239,"orig":279,"rating":4.6,"reviews":8765,"badge":"","features":["Strain","Recovery","HRV","5 أيام","دقيق"]},
        {"name_en":"Ultrahuman Ring AIR","name_ar":"خاتم Ultrahuman Ring AIR","price":349,"orig":399,"rating":4.7,"reviews":5432,"badge":"مميز","features":["بدون اشتراك","AI نوم","Metabolic","7 أيام","IP68"]},
        {"name_en":"Fitbit Charge 6 Tracker","name_ar":"سوار Fitbit Charge 6","price":159,"orig":199,"rating":4.6,"reviews":12345,"badge":"","features":["ECG","Google Maps","YouTube","7 أيام","GPS"]},
        {"name_en":"Garmin Vivosmart 5","name_ar":"سوار Garmin Vivosmart 5","price":149,"orig":179,"rating":4.5,"reviews":6543,"badge":"","features":["OLED","7 أيام","Body Battery","HRV","5ATM"]},
        {"name_en":"Withings ScanWatch Nova","name_ar":"ساعة Withings ScanWatch Nova","price":499,"orig":599,"rating":4.7,"reviews":2345,"badge":"","features":["ECG","30 يوم","SpO2","كلاسيكي","FDA"]},
        {"name_en":"Amazfit Helio Ring","name_ar":"خاتم أمازفيت Helio Ring","price":299,"orig":349,"rating":4.5,"reviews":1876,"badge":"","features":["تيتانيوم","صحة","4 أيام","Zepp","IP68"]},
        {"name_en":"RingConn Gen 2 Air Ring","name_ar":"خاتم RingConn Gen 2 Air","price":199,"orig":249,"rating":4.5,"reviews":3210,"badge":"قيمة مثالية","features":["10 أيام","بدون اشتراك","نوم","SpO2","متعدد"]},
        {"name_en":"Xiaomi Smart Band 9 Pro","name_ar":"سوار شاومي Smart Band 9 Pro","price":79,"orig":99,"rating":4.6,"reviews":15432,"badge":"اقتصادي","features":["AMOLED","GPS","21 يوم","150 رياضة","SpO2"]},
        {"name_en":"Muse 2 Brain Sensing Headband","name_ar":"عصابة Muse 2 للتأمل","price":249,"orig":299,"rating":4.5,"reviews":2876,"badge":"","features":["EEG 7","تأمل","تنفس","قلب","تطبيق"]},
        {"name_en":"Samsung Galaxy Ring","name_ar":"خاتم سامسونج Galaxy Ring","price":399,"orig":449,"rating":4.6,"reviews":4321,"badge":"جديد","features":["تيتانيوم","7 أيام","Samsung Health","AI","IP68"]},
        {"name_en":"Polar Verity Sense Monitor","name_ar":"جهاز Polar Verity Sense","price":89,"orig":109,"rating":4.7,"reviews":5678,"badge":"","features":["HR دقيق","ذراع","30h","BT+ANT+","IP67"]},
        {"name_en":"Biostrap EVO Health Band","name_ar":"سوار Biostrap EVO الصحي","price":199,"orig":249,"rating":4.4,"reviews":1234,"badge":"","features":["HRV دقيق","SpO2","نوم","طبي","IP67"]},
        {"name_en":"Garmin Index BPM Monitor","name_ar":"جهاز Garmin Index لضغط الدم","price":149,"orig":179,"rating":4.5,"reviews":3456,"badge":"","features":["ضغط دم","BT 5.0","Garmin Connect","دقيق","40 قياس"]},
        {"name_en":"Withings Body Scan Scale","name_ar":"ميزان Withings Body Scan","price":299,"orig":349,"rating":4.7,"reviews":876,"badge":"","features":["تركيب جسم","ECG قدم","عصب","صحي","WiFi"]},
    ],
    "smart-home": [
        {"name_en":"Amazon Echo Show 10 3rd Gen","name_ar":"شاشة Amazon Echo Show 10","price":249,"orig":299,"rating":4.7,"reviews":23456,"badge":"الأكثر مبيعاً","features":["HD 10 بوصة","يتابعك","13MP","Alexa","مكبر 3 بوصة"]},
        {"name_en":"Apple HomePod 2nd Generation","name_ar":"مكبر Apple HomePod الجيل 2","price":299,"orig":349,"rating":4.7,"reviews":12345,"badge":"مميز","features":["Spatial Audio","S7","تحكم","Siri","صوت"]},
        {"name_en":"Google Nest Hub Max Display","name_ar":"شاشة Google Nest Hub Max","price":229,"orig":279,"rating":4.6,"reviews":15432,"badge":"","features":["10 بوصة","كاميرا Duo","Photos","Assistant","Full-range"]},
        {"name_en":"Philips Hue Color Starter Kit","name_ar":"طقم إضاءة Philips Hue","price":199,"orig":249,"rating":4.7,"reviews":34567,"badge":"","features":["16M لون","صوتي","Bridge","تطبيق","موسيقى"]},
        {"name_en":"Ring Video Doorbell Pro 2","name_ar":"جرس Ring Video Doorbell Pro 2","price":249,"orig":299,"rating":4.5,"reviews":43210,"badge":"","features":["1536p","Bird's Eye","ذكي","Alexa","3D"]},
        {"name_en":"Google Nest Learning Thermostat","name_ar":"منظم حرارة Nest الجيل 4","price":279,"orig":329,"rating":4.7,"reviews":28765,"badge":"","features":["يتعلم","15% توفير","يحسك","OLED","Google Home"]},
        {"name_en":"Amazon Echo Dot 5th Gen","name_ar":"مكبر Amazon Echo Dot الجيل 5","price":49,"orig":59,"rating":4.7,"reviews":98765,"badge":"قيمة مثالية","features":["Alexa","2x أوضح","Smart Home","LED","مزامنة"]},
        {"name_en":"Arlo Pro 5S Security Camera","name_ar":"كاميرا Arlo Pro 5S","price":249,"orig":299,"rating":4.6,"reviews":8765,"badge":"","features":["2K HDR","ألوان ليلية","160°","6 أشهر","Alexa"]},
        {"name_en":"Yale Assure Lock 2 Plus","name_ar":"قفل ذكي Yale Assure Lock 2","price":329,"orig":379,"rating":4.5,"reviews":4321,"badge":"","features":["Matter","بصمة+رمز","AES-128","Yale Access","تنبيهات"]},
        {"name_en":"iRobot Roomba j9 Plus","name_ar":"مكنسة iRobot Roomba j9+","price":799,"orig":999,"rating":4.7,"reviews":6543,"badge":"","features":["60 يوم","تجنب AI","خريطة","Alexa","شحن تلقائي"]},
        {"name_en":"Nanoleaf Shapes Hexagons Kit","name_ar":"إضاءة Nanoleaf سداسية","price":199,"orig":249,"rating":4.5,"reviews":12345,"badge":"","features":["16M لون","موسيقى","لمس","Thread","حر"]},
        {"name_en":"Sonos Era 300 Speaker","name_ar":"مكبر Sonos Era 300","price":449,"orig":499,"rating":4.7,"reviews":3456,"badge":"","features":["Spatial Audio","Dolby Atmos","6 مكبرات","S2","بدون اشتراك"]},
        {"name_en":"Ecobee Smart Thermostat Premium","name_ar":"منظم Ecobee Smart Premium","price":249,"orig":299,"rating":4.7,"reviews":21345,"badge":"","features":["Alexa مدمج","غرفة","23% توفير","SmartSensor","ENERGY STAR"]},
        {"name_en":"Samsung SmartThings Hub","name_ar":"مركز Samsung SmartThings","price":129,"orig":149,"rating":4.5,"reviews":5432,"badge":"","features":["Zigbee+Z-Wave+WiFi","مركزي","تلقائي","أمان","شامل"]},
        {"name_en":"Eufy Security HomeBase 3","name_ar":"نظام Eufy Security HomeBase 3","price":299,"orig":349,"rating":4.6,"reviews":4321,"badge":"","features":["16GB محلي","Triple Band","AI","8K","بدون اشتراك"]},
    ],
    "earbuds": [
        {"name_en":"Apple AirPods Pro 2 USB-C","name_ar":"سماعات AirPods Pro الجيل 2","price":249,"orig":279,"rating":4.9,"reviews":54321,"badge":"الأكثر مبيعاً","features":["ANC H2","Adaptive","Spatial","IP68","6h+30h"]},
        {"name_en":"Sony WF-1000XM5 Earbuds","name_ar":"سماعات Sony WF-1000XM5","price":279,"orig":329,"rating":4.8,"reviews":23456,"badge":"مميز","features":["أفضل ANC","V2","360","LDAC","8h+24h"]},
        {"name_en":"Bose QuietComfort Ultra Earbuds","name_ar":"سماعات Bose QuietComfort Ultra","price":299,"orig":349,"rating":4.8,"reviews":15432,"badge":"","features":["Immersive","CustomTune","6h+24h","USB-C","IP54"]},
        {"name_en":"Samsung Galaxy Buds 3 Pro","name_ar":"سماعات Samsung Galaxy Buds 3 Pro","price":249,"orig":299,"rating":4.7,"reviews":12345,"badge":"","features":["ANC AI","Blade","IP57","360°","6h+30h"]},
        {"name_en":"Apple AirPods 4 with ANC","name_ar":"سماعات Apple AirPods 4 ANC","price":179,"orig":199,"rating":4.8,"reviews":32145,"badge":"جديد","features":["H2 ANC","Open-ear","USB-C","5h+30h","IP54"]},
        {"name_en":"Sony WH-1000XM5 Headphones","name_ar":"سماعات Sony WH-1000XM5 فوق الأذن","price":349,"orig":399,"rating":4.8,"reviews":45678,"badge":"","features":["ANC AI","30h","Multi-point","LDAC","فولد"]},
        {"name_en":"Nothing Ear 3 Wireless","name_ar":"سماعات Nothing Ear 3","price":149,"orig":179,"rating":4.6,"reviews":8765,"badge":"","features":["شفاف","ANC 45dB","8.5h+40h","IP55","ChatGPT"]},
        {"name_en":"Jabra Evolve2 Buds Pro","name_ar":"سماعات Jabra Evolve2 Buds","price":249,"orig":299,"rating":4.5,"reviews":4321,"badge":"","features":["مهني","ANC AI","6h+33h","UC","Jabra AI"]},
        {"name_en":"Beats Studio Buds Plus","name_ar":"سماعات Beats Studio Buds+","price":169,"orig":199,"rating":4.6,"reviews":6543,"badge":"","features":["ANC 36dB","Transparency","IP54","9h+36h","Android+iOS"]},
        {"name_en":"Sennheiser Momentum True Wireless 4","name_ar":"سماعات Sennheiser MTW4","price":279,"orig":329,"rating":4.7,"reviews":3456,"badge":"","features":["Hi-Fi","ANC Adaptive","7h+28h","aptX","IP54"]},
        {"name_en":"Google Pixel Buds Pro 2","name_ar":"سماعات Google Pixel Buds Pro 2","price":229,"orig":259,"rating":4.7,"reviews":8765,"badge":"جديد","features":["Tensor A1","ANC","11h+33h","ترجمة","Gemini"]},
        {"name_en":"Anker Soundcore Liberty 4 Pro","name_ar":"سماعات Anker Soundcore Liberty 4","price":129,"orig":159,"rating":4.6,"reviews":12345,"badge":"قيمة مثالية","features":["ANC 50dB","LDAC","11h+53h","IPX4","شاشة"]},
        {"name_en":"JBL Tour Pro 3 Earbuds","name_ar":"سماعات JBL Tour Pro 3","price":249,"orig":299,"rating":4.6,"reviews":5432,"badge":"","features":["شاشة لمس","ANC Pro","10h+40h","Hi-Res","ChatGPT"]},
        {"name_en":"Shure Aonic Free 2","name_ar":"سماعات Shure Aonic Free 2","price":299,"orig":349,"rating":4.6,"reviews":2345,"badge":"","features":["استوديو","ANC","7h+28h","USB-C","لمس"]},
        {"name_en":"Technics EAH-AZ100 Earbuds","name_ar":"سماعات Technics EAH-AZ100","price":299,"orig":349,"rating":4.7,"reviews":1876,"badge":"","features":["ANC AI","Jitter-less","10h+25h","USB-C","IPX4"]},
    ],
    "productivity": [
        {"name_en":"Apple iPad Pro M4 13 inch","name_ar":"جهاز iPad Pro M4 13 بوصة","price":1299,"orig":1499,"rating":4.9,"reviews":23456,"badge":"الأكثر مبيعاً","features":["M4","OLED Tandem","Apple Intelligence","120Hz","USB4"]},
        {"name_en":"Samsung Galaxy Tab S10 Ultra","name_ar":"تابلت Samsung Galaxy Tab S10 Ultra","price":1299,"orig":1499,"rating":4.8,"reviews":12345,"badge":"مميز","features":["Snapdragon 8 Gen 3","AMOLED 14.6","S Pen","DeX","12000mAh"]},
        {"name_en":"Logitech MX Master 3S Mouse","name_ar":"ماوس Logitech MX Master 3S","price":99,"orig":119,"rating":4.9,"reviews":45678,"badge":"","features":["8000 DPI","MagSpeed","7 أزرار","70 يوم","Bolt"]},
        {"name_en":"Logitech MX Keys S Plus Keyboard","name_ar":"لوحة Logitech MX Keys S Plus","price":149,"orig":179,"rating":4.8,"reviews":23456,"badge":"","features":["Smart Backlight","Smart Actions","5 أجهزة","10 أيام","Flow"]},
        {"name_en":"Keychron Q6 Max Wireless Keyboard","name_ar":"لوحة Keychron Q6 Max","price":299,"orig":349,"rating":4.8,"reviews":8765,"badge":"","features":["ميكانيكي","QMK/VIA","Gasket","BT 5.1","5000mAh"]},
        {"name_en":"Elgato Stream Deck Neo Panel","name_ar":"جهاز Elgato Stream Deck Neo","price":99,"orig":119,"rating":4.7,"reviews":6543,"badge":"","features":["8 LCD","شاشتان","تكامل","USB-C","شامل"]},
        {"name_en":"Apple Pencil Pro Stylus","name_ar":"قلم Apple Pencil Pro","price":129,"orig":149,"rating":4.8,"reviews":21345,"badge":"","features":["Squeeze+Tap","دوران","Barrel Roll","مغناطيسي","9ms"]},
        {"name_en":"Anker 737 GaNPrime 120W Charger","name_ar":"شاحن Anker 737 GaNPrime 120W","price":89,"orig":109,"rating":4.8,"reviews":34567,"badge":"قيمة مثالية","features":["120W","3 منافذ","GaN III","43 دقيقة","USB-C+A"]},
        {"name_en":"Samsung Odyssey OLED G9 Monitor","name_ar":"شاشة Samsung Odyssey OLED G9","price":1299,"orig":1499,"rating":4.7,"reviews":3456,"badge":"","features":["OLED 49 QHD","240Hz","0.03ms","HDR","FreeSync"]},
        {"name_en":"Wacom Intuos Pro Large Tablet","name_ar":"لوح رسم Wacom Intuos Pro L","price":449,"orig":499,"rating":4.8,"reviews":8765,"badge":"","features":["8192 ضغط","Pro Pen 3","BT 5.0","Touch","ExpressKey"]},
        {"name_en":"Steam Deck OLED 1TB Gaming","name_ar":"جهاز Steam Deck OLED 1 تيرابايت","price":649,"orig":749,"rating":4.8,"reviews":12345,"badge":"","features":["OLED HDR 90Hz","AMD APU","50% أكثر","1TB NVMe","WiFi 6E"]},
        {"name_en":"Anker MagGo 3-in-1 Wireless Charger","name_ar":"محطة شحن Anker MagGo اللاسلكي","price":79,"orig":99,"rating":4.7,"reviews":23456,"badge":"","features":["MagSafe 15W","3-in-1","iPhone+Watch+AirPods","20W","قابل للطي"]},
        {"name_en":"LG UltraWide 34 5K2K Monitor","name_ar":"شاشة LG UltraWide 34 بوصة","price":999,"orig":1199,"rating":4.7,"reviews":4321,"badge":"","features":["5K2K","IPS","Thunderbolt 4","KVM","Ergo Stand"]},
        {"name_en":"Jabra Evolve2 85 ANC Headset","name_ar":"سماعات Jabra Evolve2 85","price":449,"orig":529,"rating":4.6,"reviews":3210,"badge":"","features":["ANC عمل","Busylight","37h","UC","8 ميكروفون"]},
        {"name_en":"Twelve South HiRise 3 Deluxe","name_ar":"حامل Twelve South HiRise 3","price":99,"orig":119,"rating":4.7,"reviews":5432,"badge":"","features":["MagSafe 15W","لاب توب","Ergo","iPhone+Mac","تعديل"]},
    ],
}

CAT_AR = {
    "smartwatch":"ساعات ذكية","smart-glasses":"نظارات ذكية",
    "health":"صحة ذكية","smart-home":"منزل ذكي",
    "earbuds":"سماعات ذكية","productivity":"إنتاجية",
}

# ═══════════════════════════════════════════════════════
# تحميل الصورة ورفعها على GitHub
# ═══════════════════════════════════════════════════════

def download_image(url: str) -> bytes | None:
    """يحمّل الصورة من الإنترنت"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "image/*,*/*"
        }
        r = requests.get(url, headers=headers, timeout=15, stream=True)
        if r.status_code == 200 and "image" in r.headers.get("content-type",""):
            data = r.content
            if len(data) > 5000:  # على الأقل 5KB
                return data
    except Exception as e:
        log.debug(f"download error: {e}")
    return None


def upload_image_to_github(image_data: bytes, filename: str) -> str:
    """يرفع الصورة على GitHub ويرجع الـ raw URL"""
    try:
        path = f"images/{filename}"
        content = base64.b64encode(image_data).decode()
        headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
        
        # تحقق إذا كان الملف موجود
        sha = ""
        r = requests.get(f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/{path}", headers=headers, timeout=10)
        if r.status_code == 200:
            sha = r.json().get("sha", "")
        
        payload = {"message": f"🖼️ Add product image: {filename}", "content": content, "branch": "main"}
        if sha:
            payload["sha"] = sha
        
        r = requests.put(f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/{path}", headers=headers, json=payload, timeout=30)
        if r.status_code in [200, 201]:
            raw_url = f"{RAW_BASE}/images/{filename}"
            log.info(f"✅ Uploaded: {filename} → {raw_url}")
            return raw_url
    except Exception as e:
        log.error(f"upload error: {e}")
    return ""


def get_real_image_url(product_name: str) -> str:
    """يبحث في Google عن صورة حقيقية"""
    try:
        params = {
            "key": GOOGLE_API_KEY,
            "cx":  GOOGLE_CX,
            "q":   f"{product_name} official product photo",
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
                if url and url.startswith("http"):
                    return url
    except Exception as e:
        log.warning(f"Google search error: {e}")
    return ""


def get_product_image(product_name: str, product_id: str, category: str = "") -> str:
    """يجيب صورة حقيقية ويرفعها على GitHub"""
    try:
        import image_fetcher
        return image_fetcher.get_image_for_product(product_name, product_id, category)
    except Exception as e:
        log.error(f"image_fetcher error: {e}")
        return get_svg_placeholder(category, product_name)


# ═══════════════════════════════════════════════════════
# SVG Fallback احترافي
# ═══════════════════════════════════════════════════════

def get_svg_placeholder(category: str, name: str = "") -> str:
    """يرجع رابط SVG من GitHub حسب الفئة"""
    svg_map = {
        "smartwatch":    f"{RAW_BASE}/images/smartwatch.svg",
        "smart-glasses": f"{RAW_BASE}/images/smart-glasses.svg",
        "health":        f"{RAW_BASE}/images/health.svg",
        "smart-home":    f"{RAW_BASE}/images/smart-home.svg",
        "earbuds":       f"{RAW_BASE}/images/earbuds.svg",
        "productivity":  f"{RAW_BASE}/images/productivity.svg",
    }
    return svg_map.get(category, svg_map["smartwatch"])

def _get_svg_placeholder_old(category: str, name: str) -> str:
    """OLD - data URI version"""
    svgs = {
        "smartwatch": f"""<svg viewBox="0 0 300 300" xmlns="http://www.w3.org/2000/svg"><rect width="300" height="300" fill="#0f1923"/><rect x="112" y="45" width="76" height="12" rx="6" fill="#1e3a5f"/><rect x="112" y="243" width="76" height="12" rx="6" fill="#1e3a5f"/><rect x="90" y="70" width="120" height="160" rx="30" fill="#1a2a3a" stroke="#3b82f6" stroke-width="2.5"/><rect x="102" y="82" width="96" height="136" rx="20" fill="#0a0f1a"/><text x="150" y="145" text-anchor="middle" fill="#60a5fa" font-size="32" font-family="Arial" font-weight="bold">10:08</text><text x="150" y="170" text-anchor="middle" fill="#94a3b8" font-size="14" font-family="Arial">SAT</text><text x="150" y="205" text-anchor="middle" fill="#3b82f6" font-size="11" font-family="Arial">{name[:18]}</text></svg>""",
        "smart-glasses": f"""<svg viewBox="0 0 300 300" xmlns="http://www.w3.org/2000/svg"><rect width="300" height="300" fill="#0f0a1a"/><rect x="15" y="143" width="270" height="4" rx="2" fill="#4a3a6a"/><ellipse cx="97" cy="150" rx="63" ry="48" fill="#1a0f2e" stroke="#7c3aed" stroke-width="2.5"/><ellipse cx="203" cy="150" rx="63" ry="48" fill="#1a0f2e" stroke="#7c3aed" stroke-width="2.5"/><rect x="160" y="138" width="40" height="24" rx="6" fill="#2d1b4e"/><ellipse cx="97" cy="150" rx="45" ry="33" fill="#120a22"/><ellipse cx="203" cy="150" rx="45" ry="33" fill="#120a22"/><circle cx="97" cy="150" r="18" fill="#1e0f3a"/><circle cx="203" cy="150" r="18" fill="#1e0f3a"/><circle cx="97" cy="150" r="8" fill="#7c3aed" opacity="0.9"/><circle cx="203" cy="150" r="8" fill="#7c3aed" opacity="0.9"/><text x="150" y="240" text-anchor="middle" fill="#7c3aed" font-size="11" font-family="Arial">{name[:18]}</text></svg>""",
        "health": f"""<svg viewBox="0 0 300 300" xmlns="http://www.w3.org/2000/svg"><rect width="300" height="300" fill="#0a1a0f"/><circle cx="150" cy="140" r="95" fill="#0f2a1a" stroke="#10b981" stroke-width="2.5"/><circle cx="150" cy="140" r="75" fill="#0a1f14"/><polyline points="75,140 100,140 118,110 137,170 155,120 172,140 225,140" fill="none" stroke="#10b981" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><text x="150" y="100" text-anchor="middle" fill="#34d399" font-size="36" font-family="Arial" font-weight="bold">72</text><text x="150" y="120" text-anchor="middle" fill="#6ee7b7" font-size="13" font-family="Arial">BPM</text><text x="150" y="250" text-anchor="middle" fill="#10b981" font-size="11" font-family="Arial">{name[:18]}</text></svg>""",
        "smart-home": f"""<svg viewBox="0 0 300 300" xmlns="http://www.w3.org/2000/svg"><rect width="300" height="300" fill="#0a0f1a"/><polygon points="150,40 260,130 40,130" fill="#1a2a4a" stroke="#3b82f6" stroke-width="2.5"/><rect x="60" y="130" width="180" height="130" fill="#1a2a4a" stroke="#3b82f6" stroke-width="2"/><rect x="115" y="190" width="70" height="70" rx="5" fill="#0a1525"/><rect x="75" y="145" width="55" height="50" rx="5" fill="#0a1525"/><rect x="170" y="145" width="55" height="50" rx="5" fill="#0a1525"/><circle cx="102" cy="170" r="10" fill="#3b82f6" opacity="0.9"/><circle cx="197" cy="170" r="10" fill="#fbbf24" opacity="0.9"/><text x="150" y="265" text-anchor="middle" fill="#3b82f6" font-size="11" font-family="Arial">{name[:18]}</text></svg>""",
        "earbuds": f"""<svg viewBox="0 0 300 300" xmlns="http://www.w3.org/2000/svg"><rect width="300" height="300" fill="#1a0a0a"/><rect x="80" y="80" width="140" height="130" rx="30" fill="#2a1010" stroke="#ef4444" stroke-width="2.5"/><ellipse cx="115" cy="145" rx="22" ry="30" fill="#1a0a0a" stroke="#ef4444" stroke-width="2"/><ellipse cx="185" cy="145" rx="22" ry="30" fill="#1a0a0a" stroke="#ef4444" stroke-width="2"/><circle cx="115" cy="145" r="10" fill="#ef4444" opacity="0.8"/><circle cx="185" cy="145" r="10" fill="#ef4444" opacity="0.8"/><path d="M115,115 Q150,100 185,115" fill="none" stroke="#555" stroke-width="2"/><circle cx="150" cy="240" r="25" fill="#2a1010" stroke="#ef4444" stroke-width="2"/><circle cx="150" cy="240" r="10" fill="#ef4444" opacity="0.6"/><text x="150" y="285" text-anchor="middle" fill="#ef4444" font-size="11" font-family="Arial">{name[:18]}</text></svg>""",
        "productivity": f"""<svg viewBox="0 0 300 300" xmlns="http://www.w3.org/2000/svg"><rect width="300" height="300" fill="#0f0f0a"/><rect x="30" y="50" width="240" height="160" rx="12" fill="#1a1a0f" stroke="#f59e0b" stroke-width="2.5"/><rect x="44" y="64" width="212" height="132" rx="6" fill="#0a0a05"/><rect x="55" y="82" width="90" height="8" rx="4" fill="#f59e0b" opacity="0.8"/><rect x="55" y="98" width="65" height="6" rx="3" fill="#78716c"/><rect x="55" y="112" width="80" height="6" rx="3" fill="#78716c"/><rect x="55" y="126" width="55" height="6" rx="3" fill="#78716c"/><rect x="160" y="78" width="82" height="82" rx="6" fill="#1f1a05" stroke="#f59e0b" stroke-width="1.5"/><polyline points="168,148 182,120 196,132 214,105 242,118" fill="none" stroke="#f59e0b" stroke-width="2.5" stroke-linecap="round"/><rect x="110" y="218" width="80" height="12" rx="6" fill="#2a2a15"/><rect x="30" y="230" width="240" height="10" rx="5" fill="#1a1a0f"/><text x="150" y="270" text-anchor="middle" fill="#f59e0b" font-size="11" font-family="Arial">{name[:18]}</text></svg>""",
    }
    svg = svgs.get(category, svgs["smartwatch"])
    encoded = base64.b64encode(svg.encode()).decode()
    return f"data:image/svg+xml;base64,{encoded}"


# ═══════════════════════════════════════════════════════
# GitHub
# ═══════════════════════════════════════════════════════

def _gh_headers():
    return {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

def pull_products():
    try:
        r = requests.get(f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/products.json", headers=_gh_headers(), timeout=10)
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
        r = requests.put(f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/products.json", headers=_gh_headers(), json=payload, timeout=30)
        return r.status_code in [200, 201]
    except Exception as e:
        log.error(f"push: {e}")
        return False

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
# الوظائف الرئيسية
# ═══════════════════════════════════════════════════════

def fill_store(chat_id=None):
    """يملأ المتجر بـ 90 منتج مع صور حقيقية مرفوعة على GitHub"""
    if chat_id:
        send(chat_id, "⏳ جاري ملء المتجر بـ 90 منتج...\n\n🔍 سأبحث عن صورة حقيقية لكل منتج وأرفعها على GitHub\n\n⏱ يأخذ 5-10 دقائق ☕")

    products = []
    counter = 1

    for cat_id, items in PRODUCTS_DB.items():
        cat_ar = CAT_AR[cat_id]
        if chat_id:
            send(chat_id, f"📦 جاري معالجة فئة: *{cat_ar}* ({len(items)} منتج)...")

        for p in items:
            pid = f"NPH-{counter:03d}"
            discount = round((1 - p["price"] / p["orig"]) * 100)

            # جيب صورة حقيقية من Google وارفعها على GitHub
            image_url = get_product_image(p["name_en"], pid, cat_id)

            # إذا فشل كل شيء، استخدم SVG مدمج
            if not image_url:
                image_url = get_svg_placeholder(cat_id, p["name_ar"])

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
                "description_ar": f"{p['name_ar']} — من أفضل منتجات {cat_ar}. جودة عالية وأداء استثنائي.",
                "features_ar": p["features"],
                "tags": [cat_ar, p["name_ar"].split()[0]],
                "badge": p.get("badge", ""),
                "active": True,
                "shipping_days": "7-14",
                "featured": p.get("badge") in ["الأكثر مبيعاً", "مميز", "حصري"],
                "added_by": "smart_bot_v5",
                "added_at": datetime.now().strftime("%Y-%m-%d"),
            }
            products.append(product)
            counter += 1
            time.sleep(1)

    _, sha = pull_products()
    ok = push_products(products, sha, f"🤖 Fill store: {len(products)} products with real images on GitHub")

    if chat_id:
        if ok:
            send(chat_id,
                f"✅ *تم ملء المتجر بنجاح!*\n\n"
                f"⌚ ساعات: 15\n🥽 نظارات: 15\n💪 صحة: 15\n"
                f"🏠 منزل: 15\n🎧 سماعات: 15\n💼 إنتاجية: 15\n\n"
                f"*إجمالي: {len(products)} منتج* بصور حقيقية مرفوعة على GitHub ✅\n\n"
                f"🌐 https://neo-pulse-hub.it.com/products.html"
            )
        else:
            send(chat_id, "❌ فشل رفع products.json على GitHub")
    return products


def auto_add_products(count=5, chat_id=None):
    """يضيف منتجات جديدة تلقائياً مع صور حقيقية"""
    products, sha = pull_products()
    existing = {p.get("name_en","").lower() for p in products}

    candidates = []
    for cat_id, items in PRODUCTS_DB.items():
        for p in items:
            if p["name_en"].lower() not in existing:
                candidates.append((cat_id, p))

    if not candidates:
        if chat_id: send(chat_id, "ℹ️ كل المنتجات موجودة أصلاً")
        return []

    random.shuffle(candidates)
    selected = candidates[:count]

    max_id = max([int(p["id"].replace("NPH-","")) for p in products if p.get("id","").startswith("NPH-")] or [0])
    counter = max_id + 1
    added = []

    for cat_id, p in selected:
        pid = f"NPH-{counter:03d}"
        discount = round((1 - p["price"] / p["orig"]) * 100)

        image_url = get_product_image(p["name_en"], pid, cat_id)
        if not image_url:
            image_url = get_svg_placeholder(cat_id, p["name_ar"])

        product = {
            "id": pid, "name_ar": p["name_ar"], "name_en": p["name_en"],
            "category": cat_id, "category_ar": CAT_AR[cat_id],
            "price": p["price"], "original_price": p["orig"], "discount": discount,
            "rating": p["rating"], "reviews": p["reviews"],
            "stock": random.randint(20,100), "image": image_url,
            "description_ar": f"{p['name_ar']} — من أفضل منتجات {CAT_AR[cat_id]}.",
            "features_ar": p["features"], "tags": [CAT_AR[cat_id]],
            "badge": p.get("badge",""), "active": True, "shipping_days": "7-14",
            "featured": p.get("badge") in ["الأكثر مبيعاً","مميز","حصري"],
            "added_by": "auto_bot_v5", "added_at": datetime.now().strftime("%Y-%m-%d"),
        }
        products.append(product)
        added.append(product)
        counter += 1
        time.sleep(1)

    if added:
        push_products(products, sha, f"🤖 Auto-add: {len(added)} products with real images")
        if chat_id:
            names = "\n".join([f"✅ `{p['id']}` {p['name_ar']}" for p in added])
            send(chat_id, f"🚀 *تمت إضافة {len(added)} منتجات:*\n\n{names}")
    return added


def fix_all_images(chat_id=None):
    """يصلح صور كل المنتجات — يحمّل ويرفع على GitHub"""
    products, sha = pull_products()
    if not products:
        if chat_id: send(chat_id, "❌ لا توجد منتجات")
        return

    if chat_id:
        send(chat_id, f"🖼️ جاري تصليح صور {len(products)} منتج...\n\n📥 سأحمّل كل صورة وأرفعها على GitHub\n\n⏱ يأخذ 10-15 دقيقة ☕")

    fixed = 0
    for p in products:
        pid = p.get("id", f"NPH-{fixed:03d}")
        new_img = get_product_image(p.get("name_en",""), pid)
        if new_img:
            p["image"] = new_img
            fixed += 1
        time.sleep(1)

    push_products(products, sha, f"🖼️ Fix images: {fixed} real images uploaded to GitHub")
    if chat_id:
        send(chat_id, f"✅ تم تصليح {fixed} صورة ورفعها على GitHub!\n\n🌐 https://neo-pulse-hub.it.com/products.html")


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
    if cmd == "fill": fill_store()
    elif cmd == "auto":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        auto_add_products(count)
    elif cmd == "fix": fix_all_images()
