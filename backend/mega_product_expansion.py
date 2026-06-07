#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إضافة منتجات ضخمة - هدف 500+ منتج
للحصول على أكبر عدد من الزوبناء والنقرات
"""

import json
import random
from datetime import datetime

def generate_extensive_products():
    """توليد منتجات موسعة بكميات كبيرة"""
    
    all_products = []
    product_id = 1000
    
    categories_data = {
        # ========================================
        # ساعات ذكية - 50 منتج
        # ========================================
        "smartwatch": {
            "products": [
                "Apple Watch Series 9", "Samsung Galaxy Watch 6", "Garmin Venu 3", 
                "Fitbit Charge 6", "Amazfit Balance", "Huawei Watch GT 4", 
                "TicWatch Pro 5", "Fossil Gen 6", "Michael Kors Access",
                "Skagen Falster 3", "Xiaomi Watch S3", "Oppo Watch 4",
                "OnePlus Watch 2", "Mobvoi TicWatch 5", "Suunto Race",
                "Casio G-Shock Smart", "Tag Heuer Connected", "Montblanc Summit",
                "Louis Vuitton Tambour", "Hublot Big Bang e",
                "Citizen CZ Smart", "Seiko Prospex Smart", "Omega Smart",
                "Longines Conquest", "Tissot T-Connect", "Bulova Caliber",
                "Seiko Astron GPS", "Casio Edifice Bluetooth", "Xiaomi Watch 2 Pro",
                "Realme Watch 3 Pro", "Vivo Watch 3", "ZTE Watch Live",
                "Nubia Watch", "Kospet Prime 2", "Lemfo Lem T",
                "Blackview X1", "Oinom HM8", "Makibes F5",
                "Yunmai Pop", "Wonlex Q2", "K50 Smart Watch",
                "Ferrari Smart", "Lamborghini Watch", "Puma Smart",
                "Adidas Smart", "Nike Smart", "Under Armour Smart",
                "Asics Smart", "Polar Pacer", "Wahoo Elemnt",
            ],
            "price_range": (49, 899),
            "category_ar": "ساعات ذكية"
        },
        
        # ========================================
        # سماعات لاسلكية - 50 منتج
        # ========================================
        "earbuds": {
            "products": [
                "Apple AirPods Pro 2", "Samsung Galaxy Buds2 Pro", "Sony WF-1000XM5",
                "Bose QuietComfort Earbuds II", "Jabra Elite 85t", "Sennheiser Momentum 3",
                "Beats Fit Pro", "Google Pixel Buds Pro", "OnePlus Buds Pro 2",
                "Xiaomi Buds 4 Pro", "Oppo Enco X2", "Vivo TWS 3",
                "Realme Buds Air 5 Pro", "Nothing Ear 2", "Nothing Ear Stick",
                "Soundcore Liberty 4", "Anker Soundcore Space A40", "JBL Live Pro 2",
                "JBL Tour Pro 2", "Audio-Technica ATH-CK1TW", "AKG N30",
                "Beyerdynamic Free Byrd", "Shure Aonic Free", "Earsonics Spark",
                "Campfire Orbit", "Nura Loop", "Nuheara IQbuds2",
                "Sony LinkBuds S", "Sony WF-LS900N", "Bose Sport Earbuds",
                "Bose SoundSport Free", "Jabra Elite 75t", "Jabra Elite 7 Pro",
                "Jabra Elite 4 Active", "Samsung Galaxy Buds Live", "Samsung Galaxy Buds FE",
                "Amazon Echo Buds 2", "Anker Liberty 3 Pro", "EarFun Air Pro 3",
                "EarFun Free Pro 3", "TaoTronics SoundLiberty 80", "SoundPEATS Air3",
                "Tronspeaker Apollo", "Baseus Bowie M2", "QCY T18",
                "Fossil Sport Earbuds", "Michael Kors Earbuds", "Kate Spade Earbuds",
                "Ray-Ban Stories", "Bose Open Earbuds", "Sony Float Run",
            ],
            "price_range": (29, 349),
            "category_ar": "سماعات لاسلكية"
        },
        
        # ========================================
        # سماعات رأس - 40 منتج
        # ========================================
        "headphones": {
            "products": [
                "Sony WH-1000XM5", "Bose QuietComfort Ultra", "Apple AirPods Max",
                "Sennheiser Momentum 4", "Audio-Technica ATH-M50x", "Audio-Technica ATH-R70x",
                "Beyerdynamic DT 990 Pro", "Beyerdynamic DT 770 Pro", "AKG K371",
                "JBL Tour One M2", "JBL Everest 710", "Jabra Evolve2 85",
                "Jabra Evolve2 65", "Poly Voyager Focus 2", "Poly Blackwire 8225",
                "SteelSeries Arctis Nova Pro", "SteelSeries Arctis 7+", "HyperX Cloud III",
                "HyperX Cloud Alpha", "Razer BlackShark V2 Pro", "Razer Barracuda Pro",
                "Logitech Zone Vibe", "Logitech G Pro X", "Logitech H540",
                "Microsoft Surface Headphones 2", "Surface Headphones 2+", "Beats Studio Pro",
                "Beats Studio 3", "Beats Solo 3", "Beats Flex",
                "Marshall Monitor III", "Marshall Major IV", "Marshall Mid A.N.C.",
                "Bang & Olufsen Beoplay H95", "Bang & Olufsen Beoplay HX", "Master & Dynamic MW75",
                "Devialet Gemini", "Focal Bathys", "Grado GT500",
                "HiFiMan Sundara", "Sاشات Philips",
            ],
            "price_range": (49, 549),
            "category_ar": "سماعات رأس"
        },
        
        # ========================================
        # منزل ذكي - 40 منتج
        # ========================================
        "smart-home": {
            "products": [
                "Amazon Echo Dot 5", "Amazon Echo Show 10", "Amazon Echo Show 8",
                "Google Nest Hub 2", "Google Nest Hub Max", "Google Nest Mini",
                "Apple HomePod 2", "Apple HomePod Mini", "Sonos One",
                "Sonos Era 300", "Sonos Arc", "Sonos Beam",
                "Ring Video Doorbell 4", "Ring Doorbell Pro 2", "Ring Floodlight Cam",
                "Arlo Pro 4K", "Arlo Essential", "Eufy Security Cam 2K",
                "Wyze Cam v3", "Blink Mini", "Google Nest Cam",
                "TP-Link Kasa Plug", "TP-Link Kasa Switch", "TP-Link Tapo Cam",
                "Philips Hue Starter", "Philips Hue Bulb", "Philips Hue Strip",
                "LIFX Bulb", "Nanoleaf Shapes", "Govee Light Strip",
                "Wyze Plug", "Aqara Hub", "SmartThings Hub",
                "Ecobee Thermostat", "Nest Thermostat", "Honeywell Thermostat",
                "August Smart Lock", "Yale Lock", "Schlage Lock",
                "iRobot Roomba j7", "iRobot Roomba i7", "Ecovacs Deebot",
            ],
            "price_range": (19, 499),
            "category_ar": "المنزل الذكي"
        },
        
        # ========================================
        # الصحة واللياقة - 40 منتج
        # ========================================
        "health": {
            "products": [
                "Withings ScanWatch 2", "Withings Body Smart", "Withings BPM Connect",
                "Omron Evolv", "Omron Platinum", "QardioArm",
                "Fitbit Aria Air", "Fitbit Flex 2", "Garmin Index 2",
                "Polar H10", "Polar Verity Sense", "Whoop 4.0",
                "Oura Ring Gen 3", "Motiv Ring", "Ultrahuman Ring",
                "Apple Health Kit", "Samsung Health Band", "Xiaomi Mi Band 8",
                "Amazfit Band 7", "Huawei Band 8", "Realme Band 2",
                "Theragun Mini", "Theragun Prime", "Theragun Elite",
                "Hypervolt 2 Pro", "Hyperice Hypervolt GO", "Therabody Pro",
                "Oral-B iO 9", "Oral-B iO 7", "Oral-B Genius X",
                "Waterpik Complete", "Philips Sonicare 9900", "Forbright Toothbrush",
                "Withings Sleep", "Sleep Number Bed", "Eight Sleep Pod",
                "ResMed AirMini", "Z2 Auto CPAP", "Lofta BackSleep",
                "Contour Next", "One Drop", "Livongo",
            ],
            "price_range": (29, 399),
            "category_ar": "الصحة الذكية"
        },
        
        # ========================================
        # إنتاجية وأجهزة كمبيوتر - 50 منتج
        # ========================================
        "productivity": {
            "products": [
                "MacBook Air M3", "MacBook Pro 14", "MacBook Pro 16",
                "MacBook Air M2", "iPad Pro M4", "iPad Air M2",
                "iPad Mini 6", "iPad 10", "Samsung Tab S9",
                "Samsung Tab A9", "Microsoft Surface Pro 9", "Microsoft Surface Go 3",
                "Dell XPS 13", "Dell XPS 15", "Dell XPS 17",
                "HP Spectre x360", "HP Envy", "HP Pavilion",
                "Lenovo ThinkPad X1", "Lenovo Yoga 9i", "Lenovo IdeaPad",
                "ASUS ZenBook 14", "ASUS ROG Zephyrus", "ASUS ProArt",
                "Acer Swift 5", "Acer Spin 5", "MSI Prestige",
                "Razer Blade 14", "Razer Book 13", "LG Gram",
                "Samsung Galaxy Book", "Huawei MateBook", "Microsoft Surface Laptop",
                "Apple Pencil 2", "Apple Pencil Pro", "Logitech Crayon",
                "Logitech MX Keys", "Logitech MX Master 3S", "Apple Magic Keyboard",
                "Apple Magic Mouse", "Logitech MX Anywhere 3", "Microsoft Arc Mouse",
                "CalDigit TS4", "Belkin Thunderbolt", "Anker Hub",
                "LG UltraFine", "Samsung Monitor", "Dell Monitor",
                "Keychron Keyboard", "Drop Keyboard", "HHKB",
            ],
            "price_range": (29, 3499),
            "category_ar": "إنتاجية وأجهزة كمبيوتر"
        },
        
        # ========================================
        # ألعاب وترفيه - 40 منتج
        # ========================================
        "gaming": {
            "products": [
                "PlayStation 5", "Xbox Series X", "Xbox Series S",
                "Nintendo Switch OLED", "Nintendo Switch Lite", "Steam Deck OLED",
                "PlayStation VR2", "Meta Quest 3", "Meta Quest 2",
                "Valve Index", "HTC Vive Pro 2", "Pico 4",
                "Razer Blade 15 Gaming", "ASUS ROG Gaming Laptop", "Alienware Gaming",
                "Razer DeathAdder", "Razer Viper", "Logitech G Pro",
                "Logitech G502", "Corsair Dark Core", "SteelSeries Aerox",
                "Razer Huntsman", "Corsair K70", "Logitech G915",
                "HyperX Alloy Origins", "SteelSeries Apex Pro", "ROCCAT Vulcan",
                "Astro A50", "SteelSeries Arctis Nova", "Logitech G Pro X Headset",
                "Razer Kraken", "Corsair Virtuoso", "HyperX Cloud II",
                "PlayStation DualSense", "Xbox Elite Controller", "Scuf Controller",
                "Nacon Controller", "Razer Wolverine", "8BitDo Controller",
                "Secretlab Chair", "Razer Iskur", "Corsair T3 Rush",
            ],
            "price_range": (39, 699),
            "category_ar": "ألعاب وترفيه"
        },
        
        # ========================================
        # كاميرات وتصوير - 30 منتج
        # ========================================
        "cameras": {
            "products": [
                "Sony A7 IV", "Sony A7R V", "Sony A7S III",
                "Canon R6 II", "Canon R5 II", "Canon R8",
                "Nikon Z8", "Nikon Z6 III", "Nikon Zf",
                "Fujifilm X-T5", "Fujifilm X-H2", "Fujifilm X-S20",
                "Panasonic S5 II", "Olympus OM-1", "Leica Q3",
                "GoPro Hero 12", "DJI Action 4", "Insta360 X4",
                "DJI Osmo Pocket 3", "DJI Mini 4 Pro", "DJI Mavic 3 Pro",
                "Logitech Brio 4K", "Razer Kiyo Pro", "Elgato Cam Link",
                "Sony ZV-1", "Canon G7X III", "DJI Osmo Mobile",
                "Ultron Smart Cam", "Ring Indoor Cam", "Wyze Cam v3",
            ],
            "price_range": (49, 4499),
            "category_ar": "كاميرات وتصوير"
        },
        
        # ========================================
        # ملابس تقنية وإكسسوارات - 40 منتج
        # ========================================
        "accessories": {
            "products": [
                "Apple Watch Band", "Samsung Band", "Garmin Band",
                "AirPods Case", "AirPods Max Case", "Phone Case",
                "MacBook Case", "iPad Case", "Galaxy Tab Case",
                "MagSafe Charger", "Wireless Charger", "Car Charger",
                "Power Bank 10000", "Power Bank 20000", "Power Bank 26800",
                "USB-C Cable", "Lightning Cable", "HDMI Cable",
                "MacBook Stand", "Monitor Arm", "Phone Stand",
                "Screen Protector", "Tempered Glass", "Privacy Screen",
                "Webcam Cover", "Cable Organizer", "Desk Mat",
                "Mouse Pad RGB", "Headphone Stand", "Laptop Sleeve",
                "Cable Clips", "Wall Mount", "Float Dock",
                "Cleaning Kit", "Screen Cleaner", "Travel Adapter",
                "Extension Cord", "Surge Protector", "USB Hub",
                "SD Card Reader", "External SSD",
            ],
            "price_range": (9, 129),
            "category_ar": "إكسسوارات تقنية"
        },
        
        # ========================================
        # مطبخ ذكي - 30 منتج
        # ========================================
        "kitchen": {
            "products": [
                "Ninja Foodi", "Instant Pot Pro", "Breville Barista Express",
                "Vitamix 5200", "Nespresso Vertuo", "Keurig Coffee Maker",
                "Cuisinart Griddler", "George Foreman Grill", "Cosori Air Fryer",
                "Bella Air Fryer", "Philips Air Fryer XXL", "Ninja Air Fryer",
                "Dash Compact", "Parla Air Fryer", "Crux Air Fryer",
                "Hamilton Beach Kettle", "Fellow EKG Kettle", "Apex Electric Kettle",
                "Cuisinart DBM-8", "OXO Brew Grinder", "Baratza Encore",
                "Vitamix FoodCycler", "Tineco Floor One", "Bissell CrossWave",
                "iRobot Braava", "Shark Steam Mop", "Dyson V15 Detect",
                "Thermomix TM6", "Instant Pot Duo", "Ninja Creami",
            ],
            "price_range": (29, 699),
            "category_ar": "مطبخ ذكي"
        },
        
        # ========================================
        # رياضة ولياقة - 30 منتج
        # ========================================
        "sports": {
            "products": [
                "Garmin Forerunner 965", "Garmin Fenix 7", "Garmin Epix Pro",
                "Apple Watch Ultra 2", "Whoop 4.0", "Polar Vantage V3",
                "Wahoo Elemnt Rival", "Suunto Race", "Coros Pace 3",
                "Bowflex SelectTech 552", "Bowflex home gym", "Resistance Band Set",
                "Pull Up Bar", "Yoga Mat Premium", "Foam Roller",
                "Theragun Mini", "Hypervolt Go 2", "ClippBall",
                "Jump Rope Smart", "Smart Fitness Mirror", "Tempo Studio",
                "Echelon Reflect", "Tonal Home Gym", "EvoHome",
                "Ninebot Max G2", "Segway Ninebot", "Electric Scooter",
                "Electric Skateboard", "Hoverboard", "Kids Bike",
            ],
            "price_range": (29, 2499),
            "category_ar": "رياضة ولياقة"
        },
        
        # ========================================
        # إلكترونيات سيارات - 20 منتج
        # ========================================
        "car": {
            "products": [
                "MagSafe Car Mount", "Magnetic Mount", "Vent Mount",
                "Garmin Drive 52", "Garmin DriveSmart", "TomTom Go",
                "Rexing V1 Dash Cam", "Viofo A129", "Blackvue Dash Cam",
                "Anker Roav Charger", "Belkin Car Charger", "AUKEY Charger",
                "OBD2 Scanner", "Bluetooth Adapter", "FM Transmitter",
                "Car Phone Holder", "Wireless Car Play", "Android Auto",
                "Car Air Purifier", "Car Vacuum Cleaner",
            ],
            "price_range": (15, 299),
            "category_ar": "إلكترونيات سيارات"
        },
        
        # ========================================
        # أدوات مكتبية ذكية - 20 منتج
        # ========================================
        "office": {
            "products": [
                "Smart Desk Lamp", "Standing Desk", "Ergonomic Chair",
                "Monitor Light Bar", "Blue Light Glasses", "Wrist Rest",
                "Document Scanner", "Label Maker", "Shredder",
                "Desk Organizer", "Cable Management", "Whiteboard Smart",
                "Printer Ink Smart", "Roomba for Office", "Air Purifier Office",
                "Humidifier Smart", "Digital Frame", "Smart Notebook",
                "Scanner Pen", "Translation Device",
            ],
            "price_range": (19, 899),
            "category_ar": "أدوات مكتبية ذكية"
        },
        
        # ========================================
        # أجهزة أطفال - 20 منتج
        # ========================================
        "kids": {
            "products": [
                "Fire Kids Tablet", "LeapFrog Learning", "VTech Tablet",
                "Kids Smart Watch", "Kids GPS Tracker", "Kids Camera",
                "Coding Robot", "LEGO Mindstorms", "Snap Circuits",
                "Science Kit", "Math Game", "Reading Pen",
                "Kids Headphones", "Kids Ear Protection", "Study Lamp",
                "Drawing Tablet", "Musical Keyboard", "Drone Kids",
                "RC Car Smart", "Bike Helmet Smart",
            ],
            "price_range": (19, 399),
            "category_ar": "تقنية أطفال"
        },
    }
    
    # توليد المنتجات
    for category, data in categories_data.items():
        for product_name in data["products"]:
            min_price, max_price = data["price_range"]
            price = round(random.uniform(min_price, max_price), 2)
            original_price = round(price * random.uniform(1.1, 1.3), 2)
            
            all_products.append({
                "name_ar": f"{product_name} - {data['category_ar']}",
                "name_en": product_name,
                "category": category,
                "price": price,
                "original_price": original_price,
                "rating": round(random.uniform(4.0, 4.9), 1),
            })
    
    return all_products

def create_product_entry(product, index):
    """إنشاء كائن منتج كامل"""
    product_id = f"NPH-{index:04d}"
    
    category_images = {
        "smartwatch": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&q=80",
        "earbuds": "https://images.unsplash.com/photo-1590658268037-6bf12165a8ae?w=600&q=80",
        "headphones": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&q=80",
        "smart-home": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&q=80",
        "health": "https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?w=600&q=80",
        "productivity": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=600&q=80",
        "gaming": "https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w=600&q=80",
        "cameras": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600&q=80",
        "accessories": "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=600&q=80",
        "kitchen": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=600&q=80",
        "sports": "https://images.unsplash.com/photo-1517836357463-d25dfeac3408?w=600&q=80",
        "car": "https://images.unsplash.com/photo-1489824904134-891ab64532f1?w=600&q=80",
        "office": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=600&q=80",
        "kids": "https://images.unsplash.com/photo-1558060370-d64edd50ad47?w=600&q=80",
    }
    
    category_names = {
        "smartwatch": {"ar": "ساعات ذكية", "en": "Smart Watches"},
        "earbuds": {"ar": "سماعات لاسلكية", "en": "Wireless Earbuds"},
        "headphones": {"ar": "سماعات رأس", "en": "Headphones"},
        "smart-home": {"ar": "المنزل الذكي", "en": "Smart Home"},
        "health": {"ar": "الصحة الذكية", "en": "Smart Health"},
        "productivity": {"ar": "إنتاجية وأجهزة كمبيوتر", "en": "Productivity"},
        "gaming": {"ar": "ألعاب وترفيه", "en": "Gaming"},
        "cameras": {"ar": "كاميرات وتصوير", "en": "Cameras"},
        "accessories": {"ar": "إكسسوارات تقنية", "en": "Tech Accessories"},
        "kitchen": {"ar": "مطبخ ذكي", "en": "Smart Kitchen"},
        "sports": {"ar": "رياضة ولياقة", "en": "Sports"},
        "car": {"ar": "إلكترونيات سيارات", "en": "Car Electronics"},
        "office": {"ar": "أدوات مكتبية ذكية", "en": "Smart Office"},
        "kids": {"ar": "تقنية أطفال", "en": "Kids Tech"},
    }
    
    badges_ar = ["الأكثر مبيعاً", "جديد", "خصم", "مميز", "عرض محدود", "حصري", "تسريع", "اختيار المحرر", "عرض اليوم", "أفضل قيمة"]
    badges_en = ["Best Seller", "New", "Sale", "Featured", "Limited", "Exclusive", "Hot", "Editor's Choice", "Deal of Day", "Best Value"]
    
    discount = int(((product["original_price"] - product["price"]) / product["original_price"]) * 100)
    name_for_url = product["name_en"].replace(" ", "+").replace("&", "and").replace("(", "").replace(")", "")
    
    return {
        "id": product_id,
        "name": {"ar": product["name_ar"], "en": product["name_en"]},
        "category": product["category"],
        "category_ar": category_names.get(product["category"], {"ar": "متفرقات", "en": "Miscellaneous"})["ar"],
        "category_en": category_names.get(product["category"], {"ar": "متفرقات", "en": "Miscellaneous"})["en"],
        "price": product["price"],
        "original_price": product["original_price"],
        "discount": discount,
        "rating": product["rating"],
        "reviews": random.randint(100, 50000),
        "stock": random.randint(10, 150),
        "image": category_images.get(product["category"], "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&q=80"),
        "badge": {"ar": random.choice(badges_ar), "en": random.choice(badges_en)},
        "featured": random.random() > 0.85,
        "in_stock": True,
        "affiliate_amazon": f"https://www.amazon.com/s?k={name_for_url}&tag=neopulsehub-20",
        "affiliate_aliexpress": "",
        "description": {
            "ar": f"{product['name_en']} - منتج عالي الجودة مع ضمان سنتين وخدمة عملاء 24/7. التوصيل خلال 3-7 أيام عمل. مصمم لتجربة مستخدم ممتازة.",
            "en": f"{product['name_en']} - High quality product with 2-year warranty and 24/7 customer service. Delivery in 3-7 business days. Designed for an excellent user experience."
        },
        "features": {
            "ar": ["ضمان سنتين", "توصيل مجاني", "دعم فني", "جودة عالية", "سهل الاستخدام", "تصميم عصري"],
            "en": ["2 Year Warranty", "Free Shipping", "Technical Support", "High Quality", "Easy to Use", "Modern Design"]
        },
        "added_at": datetime.now().isoformat(),
        "added_by": "mega_expansion_v2"
    }

def main():
    print("=" * 80)
    print("🚀 بدء التوسع الضخم للمنتجات - الهدف: 500+ منتج")
    print("=" * 80)
    
    # توليد المنتجات
    new_products = generate_extensive_products()
    print(f"\n📦 تم توليد {len(new_products)} منتج جديد")
    
    # قراءة المنتجات الحالية
    with open('products.json', 'r', encoding='utf-8') as f:
        current = json.load(f)
    
    current_count = len(current)
    print(f"📊 المنتجات الحالية: {current_count}")
    
    # إضافة المنتجات الجديدة
    for i, p in enumerate(new_products, start=current_count + 1):
        current.append(create_product_entry(p, i))
    
    # حفظ
    with open('products.json', 'w', encoding='utf-8') as f:
        json.dump(current, f, ensure_ascii=False, indent=2)
    
    total = len(current)
    print(f"\n✅ تم تحديث products.json")
    print(f"📊 إجمالي المنتجات الآن: {total}")
    
    print("\n" + "=" * 80)
    print("✨ تم إنجاز التوسع بنجاح!")
    print("=" * 80)
    
    # إحصائيات
    categories = {}
    for p in current:
        cat = p.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\n📊 توزيع المنتجات حسب التصنيف:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        cat_name = cat.replace("-", " ").title()
        print(f"   • {cat_name}: {count} منتج")
    
    print(f"\n🎯 الهدف: زيادة النقرات والإيرادات")
    print(f"💰 رابط التسويق: ?tag=neopulsehub-20")

if __name__ == "__main__":
    main()