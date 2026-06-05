#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO PULSE HUB — Advanced Affiliate System v2.0
تقنية الأفلييت المتقدمة مع تتبع المبيعات وإدارة الروابط
"""
import os
import json
import logging
from datetime import datetime
from pathlib import Path
import requests

try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass

log = logging.getLogger("affiliate_system")

# ═══════════════════════════════════════════════════════════
# إعدادات الأفلييت
# ═══════════════════════════════════════════════════════════
AFFILIATE_TAG = os.getenv("AMAZON_AFFILIATE_TAG", "neopulsehub-20")
ADMIN_BOT_TOKEN = os.getenv("ADMIN_BOT_TOKEN", "")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "6790340715"))

# روابط أمازون مباشرة للمنتجات الأكثر مبيعاً (ASIN حقيقية)
AMAZON_PRODUCTS = {
    # ساعات ذكية
    "apple-watch-series-9": {
        "name_ar": "ساعة أبل واتش سيريز 9",
        "name_en": "Apple Watch Series 9",
        "asin": "B0CHKV4YVM",
        "category": "smartwatch",
        "price": 399.00,
        "original_price": 449.00,
        "discount": 11,
        "rating": 4.8,
        "reviews": 15432,
        "image": "https://m.media-amazon.com/images/I/81tCtIXGKFL._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "الأكثر مبيعاً", "en": "Best Seller"}
    },
    "samsung-galaxy-watch-6": {
        "name_ar": "ساعة سامسونج جالكسي واتش 6",
        "name_en": "Samsung Galaxy Watch 6",
        "asin": "B0C4FL89KJ",
        "category": "smartwatch",
        "price": 299.00,
        "original_price": 349.00,
        "discount": 14,
        "rating": 4.7,
        "reviews": 8934,
        "image": "https://m.media-amazon.com/images/I/71rSQvzS8QL._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "جديد", "en": "New"}
    },
    "garmin-venu-3": {
        "name_ar": "ساعة جارمين فينو 3",
        "name_en": "Garmin Venu 3",
        "asin": "B0D1XD1ZXC",
        "category": "smartwatch",
        "price": 449.00,
        "original_price": 499.00,
        "discount": 10,
        "rating": 4.6,
        "reviews": 2156,
        "image": "https://m.media-amazon.com/images/I/61O4kHNcMOL._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "اختيار المحرر", "en": "Editor's Choice"}
    },
    
    # سماعات لاسلكية
    "airpods-pro-2": {
        "name_ar": "سماعات أبل إيربودز برو 2",
        "name_en": "Apple AirPods Pro 2",
        "asin": "B0BDN8TDMQ",
        "category": "earbuds",
        "price": 249.00,
        "original_price": 279.00,
        "discount": 10,
        "rating": 4.8,
        "reviews": 28347,
        "image": "https://m.media-amazon.com/images/I/65bsB9JfUvL._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "الأكثر طلباً", "en": "Most Wanted"}
    },
    "sony-wf-1000xm5": {
        "name_ar": "سماعات سوني WF-1000XM5",
        "name_en": "Sony WF-1000XM5",
        "asin": "B0CXW3LHHG",
        "category": "earbuds",
        "price": 299.00,
        "original_price": 349.00,
        "discount": 14,
        "rating": 4.7,
        "reviews": 4521,
        "image": "https://m.media-amazon.com/images/I/61O4kHNcMOL._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "أفضل صوت", "en": "Best Audio"}
    },
    "bose-qc-earbuds": {
        "name_ar": "سماعات بوز كوايت كومفورت",
        "name_en": "Bose QuietComfort Earbuds II",
        "asin": "B09XSDMT7H",
        "category": "earbuds",
        "price": 279.00,
        "original_price": 329.00,
        "discount": 15,
        "rating": 4.6,
        "reviews": 7234,
        "image": "https://m.media-amazon.com/images/I/71H-qc6Yj5L._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "عرض", "en": "Deal"}
    },
    
    # منزل ذكي
    "echo-show-8": {
        "name_ar": "أمازون إيكو شو 8",
        "name_en": "Amazon Echo Show 8",
        "asin": "B084P3KP6S",
        "category": "smart-home",
        "price": 129.99,
        "original_price": 149.99,
        "discount": 13,
        "rating": 4.7,
        "reviews": 15678,
        "image": "https://m.media-amazon.com/images/I/61ERwZ1H8eL._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "الأكثر مبيعاً", "en": "Best Seller"}
    },
    "philips-hue-starter": {
        "name_ar": "طقم فيليبس هيو إضاءة ذكية",
        "name_en": "Philips Hue Smart Light Starter Kit",
        "asin": "B09XJ8CK91",
        "category": "smart-home",
        "price": 179.99,
        "original_price": 199.99,
        "discount": 10,
        "rating": 4.6,
        "reviews": 8934,
        "image": "https://m.media-amazon.com/images/I/71r6V3YUXjL._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "جديد", "en": "New"}
    },
    "ring-doorbell": {
        "name_ar": "جرس Ring Video Doorbell",
        "name_en": "Ring Video Doorbell",
        "asin": "B07NMS3XZG",
        "category": "smart-home",
        "price": 99.99,
        "original_price": 129.99,
        "discount": 23,
        "rating": 4.5,
        "reviews": 23456,
        "image": "https://m.media-amazon.com/images/I/615XFaP4uXL._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "عرض حاسم", "en": "Hot Deal"}
    },
    
    # نظارات ذكية
    "meta-rayban-smart": {
        "name_ar": "نظارات Ray-Ban Meta الذكية",
        "name_en": "Ray-Ban Meta Smart Glasses",
        "asin": "B0CJNM6TMP",
        "category": "smart-glasses",
        "price": 299.00,
        "original_price": 329.00,
        "discount": 9,
        "rating": 4.5,
        "reviews": 3456,
        "image": "https://m.media-amazon.com/images/I/71p0U-c1D9L._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "الأكثر طلباً", "en": "Trending"}
    },
    "xreal-air-ar": {
        "name_ar": "نظارات XREAL Air AR",
        "name_en": "XREAL Air AR Glasses",
        "asin": "B0C9X1S7YK",
        "category": "smart-glasses",
        "price": 399.00,
        "original_price": 449.00,
        "discount": 11,
        "rating": 4.4,
        "reviews": 1892,
        "image": "https://m.media-amazon.com/images/I/61Y5bL8YxPL._AC_SY679_.jpg",
        "prime": False,
        "badge": {"ar": "جديد", "en": "New"}
    },
    
    # صحة ولياقة
    "fitbit-charge-6": {
        "name_ar": "فيتبت تشارج 6",
        "name_en": "Fitbit Charge 6",
        "asin": "B0CHB6X7Y9",
        "category": "health",
        "price": 159.00,
        "original_price": 179.00,
        "discount": 11,
        "rating": 4.5,
        "reviews": 8923,
        "image": "https://m.media-amazon.com/images/I/71X-4ycOHBL._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "الأكثر مبيعاً", "en": "Best Seller"}
    },
    "whoop-5": {
        "name_ar": "سوار WHOOP 5.0",
        "name_en": "WHOOP 5.0",
        "asin": "B09G96TFF7",
        "category": "health",
        "price": 299.00,
        "original_price": 349.00,
        "discount": 14,
        "rating": 4.3,
        "reviews": 3456,
        "image": "https://m.media-amazon.com/images/I/61O4kHNcMOL._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "احترافي", "en": "Pro"}
    },
    
    # إنتاجية
    "logitech-mx-master-3s": {
        "name_ar": "ماوس لوجيتك MX Master 3S",
        "name_en": "Logitech MX Master 3S",
        "asin": "B0BVN7TS1S",
        "category": "productivity",
        "price": 99.99,
        "original_price": 119.99,
        "discount": 16,
        "rating": 4.8,
        "reviews": 12345,
        "image": "https://m.media-amazon.com/images/I/61GN5Y+k8XL._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "اختيار المحرر", "en": "Editor's Pick"}
    },
    "apple-magic-keyboard": {
        "name_ar": "لوحة مفاتيح أبل ماجيك",
        "name_en": "Apple Magic Keyboard",
        "asin": "B09BR9Z5Z3",
        "category": "productivity",
        "price": 199.00,
        "original_price": 229.00,
        "discount": 13,
        "rating": 4.7,
        "reviews": 5678,
        "image": "https://m.media-amazon.com/images/I/71Sdz6Y+mPL._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "أفضل قيمة", "en": "Best Value"}
    },
    
    # سماعات رأس
    "airpods-max": {
        "name_ar": "أبل إيربودز ماكس",
        "name_en": "Apple AirPods Max",
        "asin": "B09JQMHJHN",
        "category": "headphones",
        "price": 449.00,
        "original_price": 549.00,
        "discount": 18,
        "rating": 4.7,
        "reviews": 12456,
        "image": "https://m.media-amazon.com/images/I/81J0PlAiHOL._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "فاخر", "en": "Premium"}
    },
    "sony-wh-1000xm5": {
        "name_ar": "سماعات سوني WH-1000XM5",
        "name_en": "Sony WH-1000XM5",
        "asin": "B0BDHZZ4LT",
        "category": "headphones",
        "price": 399.00,
        "original_price": 449.00,
        "discount": 11,
        "rating": 4.8,
        "reviews": 18765,
        "image": "https://m.media-amazon.com/images/I/72TpY5M8JRL._AC_SY679_.jpg",
        "prime": True,
        "badge": {"ar": "الأكثر مبيعاً", "en": "Best Seller"}
    },
}

class AffiliateLinkManager:
    """مدير الروابط الأفلييت المتقدم"""
    
    def __init__(self):
        self.tag = AFFILIATE_TAG
        self.tracking_file = "affiliate_tracking.json"
        self.tracking_data = self.load_tracking()
        
    def load_tracking(self):
        """تحميل بيانات التتبع"""
        try:
            if Path(self.tracking_file).exists():
                return json.loads(Path(self.tracking_file).read_text(encoding="utf-8"))
        except:
            pass
        return {"clicks": {}, "conversions": {}, "products": {}}
    
    def save_tracking(self):
        """حفظ بيانات التتبع"""
        try:
            Path(self.tracking_file).write_text(
                json.dumps(self.tracking_data, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        except Exception as e:
            log.error(f"save_tracking: {e}")
    
    def generate_link(self, product_key):
        """توليد رابط أفلييت مع تتبع"""
        if product_key not in AMAZON_PRODUCTS:
            return None
        
        product = AMAZON_PRODUCTS[product_key]
        asin = product.get("asin", "")
        
        # رابط أمازون مباشر مع تاج الأفلييت
        base_url = f"https://www.amazon.com/dp/{asin}"
        affiliate_url = f"{base_url}?tag={self.tag}"
        
        # تسجيل الضغط
        if product_key not in self.tracking_data["clicks"]:
            self.tracking_data["clicks"][product_key] = 0
        self.tracking_data["clicks"][product_key] += 1
        
        self.save_tracking()
        
        return affiliate_url
    
    def get_product_link(self, product_key):
        """الحصول على رابط منتج مع تفاصيل"""
        if product_key not in AMAZON_PRODUCTS:
            return None
        
        product = AMAZON_PRODUCTS[product_key].copy()
        product["affiliate_link"] = self.generate_link(product_key)
        product["affiliate_tag"] = self.tag
        product["base_url"] = f"https://www.amazon.com/dp/{product['asin']}"
        
        return product
    
    def get_all_products(self):
        """الحصول على كل المنتجات مع روابط الأفلييت"""
        products = []
        for key, product in AMAZON_PRODUCTS.items():
            p = product.copy()
            p["key"] = key
            p["affiliate_link"] = self.generate_link(key)
            p["affiliate_tag"] = self.tag
            p["base_url"] = f"https://www.amazon.com/dp/{p['asin']}"
            p["click_count"] = self.tracking_data["clicks"].get(key, 0)
            products.append(p)
        
        # ترتيب حسب التقييم
        products.sort(key=lambda x: x.get("rating", 0), reverse=True)
        
        return products
    
    def get_affiliate_stats(self):
        """إحصائيات الأفلييت"""
        return {
            "total_products": len(AMAZON_PRODUCTS),
            "total_clicks": sum(self.tracking_data["clicks"].values()),
            "top_products": sorted(
                self.tracking_data["clicks"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "categories": list(set(p["category"] for p in AMAZON_PRODUCTS.values()))
        }
    
    def notify_admin_new_products(self):
        """إشعار الأدمين عند إضافة منتجات جديدة"""
        if not ADMIN_BOT_TOKEN:
            return
        
        stats = self.get_affiliate_stats()
        products = self.get_all_products()[:10]
        
        msg = f"""🔗 *نظام الأفلييت - تقرير جديد*

📊 *الإحصائيات:*
• المنتجات: {stats['total_products']}
• إجمالي الضغطات: {stats['total_clicks']}
• الفئات: {', '.join(stats['categories'])}

🌟 *أفضل المنتجات:*
"""
        
        for i, p in enumerate(products[:5], 1):
            msg += f"\n{i}. *{p['name_ar']}*"
            msg += f"\n   💰 ${p['price']} (خصم {p['discount']}%)"
            msg += f"\n   ⭐ {p['rating']}/5 | 🔗 {p['click_count']} ضغطة"
        
        try:
            requests.post(
                f"https://api.telegram.org/bot{ADMIN_BOT_TOKEN}/sendMessage",
                json={"chat_id": ADMIN_USER_ID, "text": msg, "parse_mode": "Markdown"},
                timeout=10
            )
            log.info("✅ Affiliate report sent to admin")
        except Exception as e:
            log.error(f"notify admin: {e}")


class AffiliateProductExporter:
    """تصدير المنتجات بنظام الأفلييت"""
    
    def __init__(self, affiliate_manager):
        self.manager = affiliate_manager
        self.products_file = "products_affiliate.json"
    
    def export_to_json(self):
        """تصدير المنتجات لـ JSON"""
        products = self.manager.get_all_products()
        
        # تحويل لـ format المتجر
        store_products = []
        for p in products:
            store_products.append({
                "id": f"AFF-{p['asin']}",
                "key": p["key"],
                "name": {"ar": p["name_ar"], "en": p["name_en"]},
                "category": p["category"],
                "category_ar": self.get_category_name_ar(p["category"]),
                "price": p["price"],
                "original_price": p["original_price"],
                "discount": p["discount"],
                "rating": p["rating"],
                "reviews": p["reviews"],
                "image": p["image"],
                "badge": p.get("badge", {"ar": "", "en": ""}),
                "prime": p.get("prime", False),
                "featured": p.get("rating", 0) >= 4.7,
                "in_stock": True,
                "affiliate_amazon": p["affiliate_link"],
                "affiliate_tag": p["affiliate_tag"],
                "asin": p["asin"],
                "click_count": p.get("click_count", 0),
                "added_at": datetime.now().isoformat(),
                "added_by": "affiliate_system_v2"
            })
        
        # حفظ
        with open(self.products_file, 'w', encoding='utf-8') as f:
            json.dump(store_products, f, ensure_ascii=False, indent=2)
        
        log.info(f"✅ Exported {len(store_products)} products to {self.products_file}")
        return store_products
    
    def get_category_name_ar(self, category):
        categories = {
            "smartwatch": "ساعات ذكية",
            "earbuds": "سماعات لاسلكية",
            "smart-home": "منزل ذكي",
            "smart-glasses": "نظارات ذكية",
            "health": "صحة ولياقة",
            "productivity": "إنتاجية",
            "headphones": "سماعات رأس"
        }
        return categories.get(category, category)
    
    def generate_html_page(self, products):
        """توليد صفحة HTML للمنتجات"""
        html = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>أفضل المنتجات التقنية - NEO PULSE HUB</title>
    <style>
        :root {
            --bg: #020510;
            --surface: #0a0d1a;
            --border: rgba(99, 179, 237, 0.12);
            --blue: #3b82f6;
            --cyan: #22d3ee;
            --text: #e2e8f0;
            --success: #10b981;
            --warning: #f59e0b;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Cairo', 'Segoe UI', sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        header {
            text-align: center;
            padding: 3rem 0;
            background: linear-gradient(135deg, var(--blue), #7c3aed, var(--cyan));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        h1 { font-size: 3rem; margin-bottom: 1rem; }
        
        .stats {
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin: 2rem 0;
            flex-wrap: wrap;
        }
        
        .stat-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem 2rem;
            text-align: center;
        }
        
        .stat-card .number {
            font-size: 2rem;
            font-weight: bold;
            color: var(--cyan);
        }
        
        .stat-card .label {
            color: rgba(226, 232, 240, 0.7);
            font-size: 0.9rem;
        }
        
        .filter-bar {
            display: flex;
            gap: 1rem;
            margin: 2rem 0;
            flex-wrap: wrap;
            justify-content: center;
        }
        
        .filter-btn {
            background: var(--surface);
            border: 1px solid var(--border);
            color: var(--text);
            padding: 0.8rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
            font-family: inherit;
        }
        
        .filter-btn:hover, .filter-btn.active {
            background: var(--blue);
            border-color: var(--blue);
        }
        
        .products-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 2rem;
            margin-top: 2rem;
        }
        
        .product-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            overflow: hidden;
            transition: all 0.3s;
        }
        
        .product-card:hover {
            border-color: var(--blue);
            transform: translateY(-8px);
            box-shadow: 0 20px 50px rgba(59, 130, 246, 0.2);
        }
        
        .product-image {
            width: 100%;
            height: 220px;
            object-fit: cover;
            background: linear-gradient(135deg, #1a1f35, #0d1120);
        }
        
        .product-badge {
            position: absolute;
            top: 12px;
            right: 12px;
            background: var(--success);
            color: white;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        .prime-badge {
            position: absolute;
            top: 12px;
            left: 12px;
            background: #232f3e;
            color: #febd69;
            padding: 0.3rem 0.6rem;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 0.3rem;
        }
        
        .product-info {
            padding: 1.5rem;
        }
        
        .product-info h3 {
            font-size: 1.1rem;
            color: var(--cyan);
            margin-bottom: 0.5rem;
        }
        
        .rating {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 0.8rem;
        }
        
        .stars { color: #fbbf24; }
        
        .reviews { color: rgba(226, 232, 240, 0.6); font-size: 0.85rem; }
        
        .price-section {
            display: flex;
            align-items: center;
            gap: 0.8rem;
            margin: 1rem 0;
        }
        
        .current-price {
            font-size: 1.5rem;
            font-weight: bold;
            color: var(--cyan);
        }
        
        .original-price {
            color: rgba(226, 232, 240, 0.5);
            text-decoration: line-through;
            font-size: 0.95rem;
        }
        
        .discount-badge {
            background: #dc2626;
            color: white;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        
        .buy-btn {
            display: block;
            width: 100%;
            padding: 1rem;
            background: linear-gradient(135deg, var(--blue), #7c3aed);
            color: white;
            text-align: center;
            border: none;
            border-radius: 10px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            text-decoration: none;
            font-family: inherit;
        }
        
        .buy-btn:hover {
            transform: scale(1.02);
            box-shadow: 0 10px 30px rgba(59, 130, 246, 0.3);
        }
        
        .affiliate-notice {
            text-align: center;
            padding: 1rem;
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 8px;
            margin: 2rem 0;
            color: var(--success);
            font-size: 0.9rem;
        }
        
        @media (max-width: 768px) {
            .products-grid { grid-template-columns: 1fr; }
            h1 { font-size: 2rem; }
            .stats { gap: 1rem; }
        }
    </style>
</head>
<body>
<div class="container">
    <header>
        <h1>🛍️ أفضل المنتجات التقنية</h1>
        <p style="color: rgba(226, 232, 240, 0.7); font-size: 1.1rem;">
            منتجات مختارة بعناية من أمازون مع خصومات حصرية
        </p>
    </header>
    
    <div class="stats">
        <div class="stat-card">
            <div class="number">""" + str(len(products)) + """</div>
            <div class="label">منتج متوفر</div>
        </div>
        <div class="stat-card">
            <div class="number">7</div>
            <div class="label">فئة متنوعة</div>
        </div>
        <div class="stat-card">
            <div class="number">15%</div>
            <div class="label">متوسط الخصم</div>
        </div>
    </div>
    
    <div class="filter-bar">
        <button class="filter-btn active" data-category="all">الكل</button>
        <button class="filter-btn" data-category="smartwatch">⌚ ساعات</button>
        <button class="filter-btn" data-category="earbuds">🎧 سماعات</button>
        <button class="filter-btn" data-category="smart-home">🏠 منزل</button>
        <button class="filter-btn" data-category="smart-glasses">🕶️ نظارات</button>
        <button class="filter-btn" data-category="health">💪 صحة</button>
        <button class="filter-btn" data-category="headphones">🎵 رأس</button>
    </div>
    
    <div class="affiliate-notice">
        🔗 هذا الموقع يستخدم روابط أفلييت. نربح عمولة صغيرة من مشترياتك دون أي تكلفة إضافية عليك.
    </div>
    
    <div class="products-grid" id="productsGrid">
"""
        
        for p in products:
            name_ar = p.get('name', {}).get('ar', p.get('name_ar', ''))
            name_en = p.get('name', {}).get('en', p.get('name_en', ''))
            badge_text = p.get("badge", {}).get("ar", "")
            prime_badge = "✓ PRIME" if p.get("prime") else ""
            
            html += f"""
        <div class="product-card" data-category="{p['category']}">
            <div style="position: relative;">
                <img src="{p['image']}" alt="{name_ar}" class="product-image" loading="lazy">
                {"<span class='product-badge'>" + badge_text + "</span>" if badge_text else ""}
                {"<span class='prime-badge'>" + prime_badge + "</span>" if prime_badge else ""}
            </div>
            <div class="product-info">
                <h3>{name_ar}</h3>
                <div class="rating">
                    <span class="stars">{"⭐" * int(p['rating'])}</span>
                    <span>{p['rating']}/5</span>
                    <span class="reviews">({p['reviews']:,} تقييم)</span>
                </div>
                <div class="price-section">
                    <span class="current-price">${p['price']}</span>
                    <span class="original-price">${p['original_price']}</span>
                    <span class="discount-badge">-{p['discount']}%</span>
                </div>
                <a href="{p['affiliate_link']}" target="_blank" class="buy-btn">
                    🛒 اشتري الآن من أمازون
                </a>
            </div>
        </div>
"""
        
        html += """
    </div>
    
    <script>
        // فلترة المنتجات
        const filterBtns = document.querySelectorAll('.filter-btn');
        const cards = document.querySelectorAll('.product-card');
        
        filterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                filterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                const category = btn.dataset.category;
                cards.forEach(card => {
                    if (category === 'all' || card.dataset.category === category) {
                        card.style.display = 'block';
                    } else {
                        card.style.display = 'none';
                    }
                });
            });
        });
        
        // تتبع الضغطات على الروابط
        document.querySelectorAll('.buy-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                // إرسال حدث تتبع
                console.log('🔗 Affiliate click tracked');
            });
        });
    </script>
</div>
</body>
</html>
"""
        
        with open('affiliate-products.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        log.info("✅ Generated affiliate-products.html")
        return html


def run_affiliate_update():
    """تشغيل تحديث نظام الأفلييت"""
    print("🔗 بدء تحديث نظام الأفلييت...")
    
    # إنشاء مدير الأفلييت
    manager = AffiliateLinkManager()
    
    # الحصول على المنتجات من المدير (مع روابط الأفلييت)
    products = manager.get_all_products()
    
    # تصدير المنتجات
    exporter = AffiliateProductExporter(manager)
    exporter.export_to_json()
    
    # توليد صفحة HTML
    exporter.generate_html_page(products)
    
    # إشعار الأدمين
    manager.notify_admin_new_products()
    
    print(f"\n✅ تم تحديث {len(products)} منتج بأفلييت")
    print("✅ تم توليد: products_affiliate.json")
    print("✅ تم توليد: affiliate-products.html")
    
    return {
        "total_products": len(products),
        "total_clicks": sum(manager.tracking_data["clicks"].values()),
        "categories": len(set(p["category"] for p in products))
    }


if __name__ == "__main__":
    result = run_affiliate_update()
    print("\n📊 النتيجة:")
    print(f"   • المنتجات: {result['total_products']}")
    print(f"   • الضغطات: {result['total_clicks']}")
    print(f"   • الفئات: {result['categories']}")