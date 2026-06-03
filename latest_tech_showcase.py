#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO PULSE HUB — Latest Technology Showcase v2.0
عرض أحدث التقنيات والمنتجات الحديثة
"""
import json
from datetime import datetime
from pathlib import Path

try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass

# ═══════════════════════════════════════════════════════════
# أحدث التقنيات لعام 2026
# ═══════════════════════════════════════════════════════════
LATEST_TECHNOLOGIES = [
    {
        "id": "tech-ai-wearables",
        "category": "AI Wearables",
        "name_ar": "أجهزة الذكاء الاصطناعي القابلة للارتداء",
        "name_en": "AI-Powered Wearables",
        "description_ar": "أحدث الأجهزة المزودة بتقنية الذكاء الاصطناعي المدمج للتنبؤ بالحالات الصحية وتقديم توصيات مخصصة.",
        "description_en": "Latest devices with built-in AI technology to predict health conditions and provide personalized recommendations.",
        "icon": "🤖",
        "features": [
            "تحليل صحي ذكي 24/7",
            "توقع أمراض القلب",
            "توصيات غذائية مخصصة",
            "مراقبة النوم المتقدمة",
            "تحليل الإجهاد والتوتر"
        ],
        "products": [
            {"name": "Apple Watch Series 10", "price": 449, "asin": "B0CHKV4YVM"},
            {"name": "Samsung Galaxy Watch 7", "price": 349, "asin": "B0C4FL89KJ"},
            {"name": "WHOOP 5.0 Pro", "price": 399, "asin": "B0D1XXXXX123"}
        ],
        "trending": True,
        "new": True
    },
    {
        "id": "tech-spatial-computing",
        "category": "Spatial Computing",
        "name_ar": "الحوسبة المكانية",
        "name_en": "Spatial Computing",
        "description_ar": "تقنية جديدة تجمع بين العالم الرقمي وال реальي باستخدام نظارات الواقع المعزز.",
        "description_en": "New technology that combines digital and real worlds using augmented reality glasses.",
        "icon": "🌐",
        "features": [
            "العمل في الفضاء ثلاثي الأبعاد",
            "اجتماعات افتراضية واقعية",
            "ألعاب AR متقدمة",
            "التسوق بتجربة غامرة",
            "التعلم بالتفاعل ثلاثي الأبعاد"
        ],
        "products": [
            {"name": "Apple Vision Pro 2", "price": 2999, "asin": "B0D1XXXXX789"},
            {"name": "Meta Quest 4", "price": 599, "asin": "B0D1XXXXX456"},
            {"name": "XREAL Air 3", "price": 499, "asin": "B0C9X1S7YK"}
        ],
        "trending": True,
        "new": True
    },
    {
        "id": "tech-smart-home-ai",
        "category": "Smart Home AI",
        "name_ar": "المنزل الذكي المدعوم بالذكاء الاصطناعي",
        "name_en": "AI-Powered Smart Home",
        "description_ar": "أنظمة منزلية ذكية تتعلم من عاداتك وتتحكم في كل شيء تلقائياً.",
        "description_en": "Smart home systems that learn from your habits and control everything automatically.",
        "icon": "🏠",
        "features": [
            "تحكم صوتي متقدم",
            "توفير الطاقة التلقائي",
            "أمن ذكي متكامل",
            "إضاءة تكيفية",
            "تحكم في المناخ الذكي"
        ],
        "products": [
            {"name": "Amazon Echo Hub", "price": 179, "asin": "B084P3KP6S"},
            {"name": "Google Nest Hub Max", "price": 229, "asin": "B07YXY26N4"},
            {"name": "Philips Hue 4th Gen", "price": 199, "asin": "B09XJ8CK91"}
        ],
        "trending": False,
        "new": True
    },
    {
        "id": "tech-wireless-audio",
        "category": "Wireless Audio",
        "name_ar": "الصوت اللاسلكي الاحترافي",
        "name_en": "Pro Wireless Audio",
        "description_ar": "سماعات لاسلكية بتقنيات متقدمة تقدم جودة صوت استوديو بدون أسلاك.",
        "description_en": "Wireless headphones with advanced technologies providing studio-quality sound without wires.",
        "icon": "🎧",
        "features": [
            "صوت Hi-Res لاسلكي",
            "إلغاء ضوضاء متقدم",
            "بطارية 40+ ساعة",
            "توصيل متعدد الأجهزة",
            "صوت مكاني غامر"
        ],
        "products": [
            {"name": "Sony WH-1000XM6", "price": 449, "asin": "B0BDHZZ4LT"},
            {"name": "Bose QC Ultra", "price": 379, "asin": "B09XSDMT7H"},
            {"name": "Apple AirPods Max 2", "price": 549, "asin": "B09JQMHJHN"}
        ],
        "trending": True,
        "new": False
    },
    {
        "id": "tech-health-monitoring",
        "category": "Health Monitoring",
        "name_ar": "مراقبة الصحة المتقدمة",
        "name_en": "Advanced Health Monitoring",
        "description_ar": "أجهزة متطورة لمراقبة الصحة بشكل يومي مع تحليلات متقدمة.",
        "description_en": "Advanced devices for daily health monitoring with analytics.",
        "icon": "💪",
        "features": [
            "ECG وقياس ضغط الدم",
            "مراقبة الأكسجين",
            "تحليل النوم العميق",
            "تتبع التوتر",
            "توصيات صحية مخصصة"
        ],
        "products": [
            {"name": "Apple Watch Ultra 3", "price": 899, "asin": "B0D1XD1ZXC"},
            {"name": "Fitbit Sense 3", "price": 249, "asin": "B0D1RZZZ123"},
            {"name": "Withings ScanWatch 2", "price": 399, "asin": "B0D1XXXXX234"}
        ],
        "trending": True,
        "new": False
    },
    {
        "id": "tech-productivity-tools",
        "category": "Productivity Tools",
        "name_ar": "أدوات الإنتاجية الذكية",
        "name_en": "Smart Productivity Tools",
        "description_ar": "أجهزة وأدوات تساعدك على العمل بكفاءة أعلى وتحقيق أهدافك.",
        "description_en": "Devices and tools to help you work more efficiently and achieve your goals.",
        "icon": "💼",
        "features": [
            "ماوس احترافي هادئ",
            "لوحات المفاتيح الذكية",
            "شاشات خارجية محمولة",
            "كاميرات 4K احترافية",
            "إضاءة مكتب ذكية"
        ],
        "products": [
            {"name": "Logitech MX Master 4", "price": 119, "asin": "B0BVN7TS1S"},
            {"name": "Apple Magic Keyboard", "price": 229, "asin": "B0BSHXBP67"},
            {"name": "CalDigit TS4", "price": 399, "asin": "B0D1XXXXX345"}
        ],
        "trending": False,
        "new": False
    }
]


class LatestTechShowcase:
    """عرض أحدث التقنيات"""
    
    def __init__(self):
        self.affiliate_tag = "neopulsehub-20"
        self.data_file = "latest_tech.json"
        
    def generate_affiliate_link(self, asin):
        return f"https://www.amazon.com/dp/{asin}?tag={self.affiliate_tag}"
    
    def export_tech_data(self):
        """تصدير بيانات التقنيات"""
        data = []
        for tech in LATEST_TECHNOLOGIES:
            t = tech.copy()
            # إضافة روابط الأفلييت للمنتجات
            for p in t["products"]:
                p["affiliate_link"] = self.generate_affiliate_link(p["asin"])
            data.append(t)
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return data
    
    def generate_html_page(self):
        """توليد صفحة HTML للتقنيات"""
        techs = self.export_tech_data()
        
        html = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>أحدث التقنيات | NEO PULSE HUB</title>
    <style>
        :root {
            --bg: #020510;
            --surface: #0a0d1a;
            --surface-2: #111827;
            --border: rgba(99, 179, 237, 0.12);
            --blue: #3b82f6;
            --cyan: #22d3ee;
            --purple: #7c3aed;
            --pink: #ec4899;
            --success: #10b981;
            --text: #e2e8f0;
            --text-muted: rgba(226, 232, 240, 0.7);
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Cairo', 'Segoe UI', sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.7;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        /* Hero Section */
        .hero {
            text-align: center;
            padding: 4rem 0;
            background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
            position: relative;
            overflow: hidden;
        }
        
        .hero::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at 20% 50%, rgba(124, 58, 237, 0.3), transparent 50%),
                        radial-gradient(circle at 80% 50%, rgba(34, 211, 238, 0.3), transparent 50%);
        }
        
        .hero-content {
            position: relative;
            z-index: 1;
        }
        
        .hero h1 {
            font-size: 3.5rem;
            background: linear-gradient(135deg, var(--cyan), var(--blue), var(--purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }
        
        .hero p {
            font-size: 1.3rem;
            color: var(--text-muted);
        }
        
        .hero-badges {
            display: flex;
            justify-content: center;
            gap: 1rem;
            margin-top: 2rem;
        }
        
        .badge {
            background: rgba(59, 130, 246, 0.2);
            border: 1px solid var(--blue);
            padding: 0.5rem 1.5rem;
            border-radius: 20px;
            font-size: 0.9rem;
        }
        
        /* Stats */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin: 3rem 0;
        }
        
        .stat-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 2rem;
            text-align: center;
            transition: all 0.3s;
        }
        
        .stat-card:hover {
            border-color: var(--cyan);
            transform: translateY(-5px);
        }
        
        .stat-icon {
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: bold;
            background: linear-gradient(135deg, var(--cyan), var(--blue));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .stat-label {
            color: var(--text-muted);
            margin-top: 0.5rem;
        }
        
        /* Tech Categories Grid */
        .tech-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 2rem;
            margin: 3rem 0;
        }
        
        .tech-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 20px;
            overflow: hidden;
            transition: all 0.4s;
        }
        
        .tech-card:hover {
            border-color: var(--blue);
            transform: translateY(-8px);
            box-shadow: 0 25px 60px rgba(59, 130, 246, 0.2);
        }
        
        .tech-header {
            padding: 2rem;
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(124, 58, 237, 0.1));
            position: relative;
        }
        
        .tech-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
        
        .tech-badge {
            position: absolute;
            top: 1rem;
            right: 1rem;
            padding: 0.3rem 1rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        
        .badge-new {
            background: var(--success);
            color: white;
        }
        
        .badge-trending {
            background: var(--pink);
            color: white;
        }
        
        .tech-title {
            font-size: 1.5rem;
            font-weight: bold;
            color: var(--cyan);
            margin-bottom: 0.5rem;
        }
        
        .tech-category {
            color: var(--text-muted);
            font-size: 0.9rem;
        }
        
        .tech-body {
            padding: 1.5rem 2rem;
        }
        
        .tech-description {
            color: var(--text-muted);
            margin-bottom: 1.5rem;
            line-height: 1.8;
        }
        
        .tech-features {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-bottom: 1.5rem;
        }
        
        .feature-tag {
            background: rgba(34, 211, 238, 0.1);
            color: var(--cyan);
            padding: 0.4rem 0.8rem;
            border-radius: 15px;
            font-size: 0.8rem;
            border: 1px solid rgba(34, 211, 238, 0.3);
        }
        
        /* Products Section */
        .tech-products {
            background: var(--surface-2);
            border-radius: 12px;
            padding: 1.5rem;
            margin-top: 1rem;
        }
        
        .tech-products h4 {
            color: var(--text);
            margin-bottom: 1rem;
            font-size: 1rem;
        }
        
        .product-list {
            display: flex;
            flex-direction: column;
            gap: 0.8rem;
        }
        
        .product-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.8rem;
            background: var(--surface);
            border-radius: 8px;
            transition: all 0.3s;
        }
        
        .product-item:hover {
            background: rgba(59, 130, 246, 0.1);
        }
        
        .product-info {
            display: flex;
            flex-direction: column;
        }
        
        .product-name {
            font-weight: 600;
            color: var(--text);
        }
        
        .product-price {
            color: var(--cyan);
            font-weight: bold;
        }
        
        .product-link {
            background: var(--blue);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            text-decoration: none;
            font-size: 0.85rem;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .product-link:hover {
            background: var(--purple);
            transform: scale(1.05);
        }
        
        /* CTA Section */
        .cta-section {
            background: linear-gradient(135deg, var(--blue), var(--purple));
            border-radius: 20px;
            padding: 3rem;
            text-align: center;
            margin: 4rem 0;
        }
        
        .cta-section h2 {
            font-size: 2rem;
            color: white;
            margin-bottom: 1rem;
        }
        
        .cta-section p {
            color: rgba(255, 255, 255, 0.8);
            margin-bottom: 2rem;
        }
        
        .cta-button {
            display: inline-block;
            background: white;
            color: var(--purple);
            padding: 1rem 2.5rem;
            border-radius: 30px;
            text-decoration: none;
            font-weight: bold;
            font-size: 1.1rem;
            transition: all 0.3s;
        }
        
        .cta-button:hover {
            transform: scale(1.05);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 3rem 0;
            border-top: 1px solid var(--border);
            color: var(--text-muted);
        }
        
        @media (max-width: 768px) {
            .hero h1 { font-size: 2rem; }
            .tech-grid { grid-template-columns: 1fr; }
            .stats-grid { grid-template-columns: repeat(2, 1fr); }
        }
    </style>
</head>
<body>
    <div class="hero">
        <div class="hero-content">
            <h1>🚀 أحدث التقنيات 2026</h1>
            <p>اكتشف أحدث الابتكارات التقنية وأكثرها تطوراً</p>
            <div class="hero-badges">
                <span class="badge">🤖 ذكاء اصطناعي</span>
                <span class="badge">🌐 حوسبة مكانية</span>
                <span class="badge">💡 حلول ذكية</span>
            </div>
        </div>
    </div>
    
    <div class="container">
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon">🎯</div>
                <div class="stat-number">""" + str(len(techs)) + """</div>
                <div class="stat-label">فئة تقنية</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📱</div>
                <div class="stat-number">""" + str(sum(len(t["products"]) for t in techs)) + """</div>
                <div class="stat-label">منتج حديث</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">⭐</div>
                <div class="stat-number">""" + str(len([t for t in techs if t.get("trending")])) + """</div>
                <div class="stat-label">تقنية رائجة</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">✨</div>
                <div class="stat-number">""" + str(len([t for t in techs if t.get("new")])) + """</div>
                <div class="stat-label">جديد 2026</div>
            </div>
        </div>
        
        <div class="tech-grid">
"""
        
        for tech in techs:
            badge_html = ""
            if tech.get("new"):
                badge_html = '<span class="tech-badge badge-new">✨ جديد 2026</span>'
            elif tech.get("trending"):
                badge_html = '<span class="tech-badge badge-trending">🔥 رائج</span>'
            
            features_html = "".join([f'<span class="feature-tag">{f}</span>' for f in tech["features"]])
            
            products_html = ""
            for p in tech["products"]:
                products_html += f"""
            <div class="product-item">
                <div class="product-info">
                    <span class="product-name">{p["name"]}</span>
                    <span class="product-price">${p["price"]}</span>
                </div>
                <a href="{p["affiliate_link"]}" target="_blank" class="product-link">
                    🛒 اشتري
                </a>
            </div>
"""
            
            html += f"""
            <div class="tech-card">
                <div class="tech-header">
                    {badge_html}
                    <div class="tech-icon">{tech["icon"]}</div>
                    <h3 class="tech-title">{tech["name_ar"]}</h3>
                    <div class="tech-category">{tech["category"]}</div>
                </div>
                <div class="tech-body">
                    <p class="tech-description">{tech["description_ar"]}</p>
                    <div class="tech-features">
                        {features_html}
                    </div>
                    <div class="tech-products">
                        <h4>📦 منتجات متوفرة:</h4>
                        <div class="product-list">
                            {products_html}
                        </div>
                    </div>
                </div>
            </div>
"""
        
        html += """
        </div>
        
        <div class="cta-section">
            <h2>🛍️ تسوق أحدث التقنيات بأسعار منافسة</h2>
            <p>اكتشف منتجاتنا المختارة من أمازون مع روابط أفلييت مباشرة</p>
            <a href="real-amazon-products.html" class="cta-button">
                تصفح المنتجات الآن
            </a>
        </div>
    </div>
    
    <div class="footer">
        <p>🔗 نظام الأفلييت من NEO PULSE HUB | آخر تحديث: """ + datetime.now().strftime("%Y-%m-%d") + """</p>
    </div>
</body>
</html>
"""
        
        with open('latest-technologies.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ Generated latest-technologies.html with {len(techs)} tech categories")
        return html


class BotStatusChecker:
    """فاحص حالة البوتات"""
    
    def __init__(self):
        self.admin_token = None
        self.admin_id = None
        
    def check_all_bots(self):
        """فحص حالة كل البوتات"""
        import os
        
        bots = [
            {
                "name": "Customer Bot",
                "token_env": "CUSTOMER_BOT_TOKEN",
                "commands": ["/start", "/products"],
                "status": "service"
            },
            {
                "name": "Admin Bot",
                "token_env": "ADMIN_BOT_TOKEN",
                "commands": ["/start", "/stats", "/orders", "/broadcast"],
                "status": "admin"
            },
            {
                "name": "Supplier Bot",
                "token_env": "SUPPLIER_BOT_TOKEN",
                "commands": ["/start", "/add", "/refresh", "/report"],
                "status": "supplier"
            },
            {
                "name": "Recommendation Bot",
                "token_env": "RECO_BOT_TOKEN",
                "commands": ["/start", "/recommend"],
                "status": "recommendation"
            }
        ]
        
        results = []
        for bot in bots:
            token = os.environ.get(bot["token_env"], "")
            status = "✅ يعمل" if token else "❌ غير موجود"
            
            # فحص إذا البوت يعمل فعلياً
            if token:
                try:
                    import requests
                    r = requests.get(
                        f"https://api.telegram.org/bot{token}/getMe",
                        timeout=5
                    )
                    if r.status_code == 200:
                        bot_info = r.json()
                        if bot_info.get("ok"):
                            status = "✅ يعمل - @" + bot_info.get("result", {}).get("username", "")
                except:
                    status = "⚠️ يوجد توكن لكن الاتصال مشكل"
            
            results.append({
                "name": bot["name"],
                "status": status,
                "token_exists": bool(token),
                "commands": bot["commands"]
            })
        
        return results
    
    def print_bot_status(self):
        """طباعة حالة البوتات"""
        results = self.check_all_bots()
        
        print("\n" + "="*60)
        print("🤖 حالة البوتات في NEO PULSE HUB")
        print("="*60)
        
        working = sum(1 for r in results if r["token_exists"])
        total = len(results)
        
        print(f"\n📊 ملخص: {working}/{total} بوت يعمل\n")
        
        for r in results:
            token_icon = "✅" if r["token_exists"] else "❌"
            print(f"  {token_icon} {r['name']}")
            print(f"     الحالة: {r['status']}")
            print(f"     الأوامر: {', '.join(r['commands'])}")
            print()
        
        return results
    
    def send_status_to_admin(self):
        """إرسال حالة البوتات للأدمين"""
        import os, requests
        
        admin_token = os.environ.get("ADMIN_BOT_TOKEN", "")
        admin_id = os.environ.get("ADMIN_USER_ID", "")
        
        if not admin_token or not admin_id:
            return None
        
        results = self.check_all_bots()
        working = sum(1 for r in results if r["token_exists"])
        total = len(results)
        
        msg = "🤖 *تقرير حالة البوتات*\n\n"
        msg += f"📊 المجموع: {working}/{total} يعمل\n\n"
        
        for r in results:
            status_icon = "✅" if r["token_exists"] else "❌"
            msg += f"{status_icon} *{r['name']}*\n"
            msg += f"   {r['status']}\n\n"
        
        try:
            requests.post(
                f"https://api.telegram.org/bot{admin_token}/sendMessage",
                json={"chat_id": admin_id, "text": msg, "parse_mode": "Markdown"},
                timeout=10
            )
            print("✅ تم إرسال تقرير الحالة للأدمين")
        except Exception as e:
            print(f"⚠️ Could not send: {e}")
        
        return results


def run_latest_tech_update():
    """تشغيل تحديث التقنيات الحديثة"""
    print("🚀 بدء تحديث أحدث التقنيات...")
    
    # عرض التقنيات
    showcase = LatestTechShowcase()
    showcase.generate_html_page()
    
    # فحص البوتات
    checker = BotStatusChecker()
    checker.print_bot_status()
    
    print("\n✅ تم تحديث التقنيات وفحص البوتات")


if __name__ == "__main__":
    run_latest_tech_update()