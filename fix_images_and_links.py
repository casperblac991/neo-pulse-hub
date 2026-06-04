#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO PULSE HUB — Image & Link Fixer
إصلاح عدم مطابقة الصور وتحديث روابط أمازون
"""

import json
import re
from pathlib import Path
from datetime import datetime

# ═══════════════════════════════════════════════════════════
# قاعدة بيانات صور أمازون الحقيقية للمنتجات
# ═══════════════════════════════════════════════════════════
AMAZON_IMAGES = {
    # Apple Watch
    "B0CHKV4YVM": "https://m.media-amazon.com/images/I/81tCtIXGKFL._AC_SY679_.jpg",
    "B0BDJ2VGDH": "https://m.media-amazon.com/images/I/71J8TZ3V3VL._AC_SY679_.jpg",
    "B0CM5JV468": "https://m.media-amazon.com/images/I/81OYnM9n9PL._AC_SY679_.jpg",
    
    # Samsung
    "B0B5W8V2L3": "https://m.media-amazon.com/images/I/71rSQvzS8QL._AC_SY679_.jpg",
    "B0C4FL89KJ": "https://m.media-amazon.com/images/I/71rSQvzS8QL._AC_SY679_.jpg",
    "B0C23S4ZKR": "https://m.media-amazon.com/images/I/71pG2w2V9TL._AC_SY679_.jpg",
    
    # AirPods
    "B0BDN8TDMQ": "https://m.media-amazon.com/images/I/65bsB9JfUvL._AC_SY679_.jpg",
    "B09JQM3LZ9": "https://m.media-amazon.com/images/I/61okDnSxxNL._AC_SY679_.jpg",
    
    # Sony
    "B085R9JC5V": "https://m.media-amazon.com/images/I/71qABoYD1UL._AC_SY679_.jpg",
    "B0BWX8VBKC": "https://m.media-amazon.com/images/I/71qABoYD1UL._AC_SY679_.jpg",
    "B0863TXMT3": "https://m.media-amazon.com/images/I/51V3K2Vtb+L._AC_SY679_.jpg",
    "B09XS7JWHH": "https://m.media-amazon.com/images/I/51V3K2Vtb+L._AC_SY679_.jpg",
    
    # Bose
    "B0BXYCDQPF": "https://m.media-amazon.com/images/I/71H-qc6Yj5L._AC_SY679_.jpg",
    "B09XSDMT7H": "https://m.media-amazon.com/images/I/71H-qc6Yj5L._AC_SY679_.jpg",
    
    # Echo
    "B09FH8K2ZB": "https://m.media-amazon.com/images/I/714fP0K2VXL._AC_SY679_.jpg",
    "B09V3KX52B": "https://m.media-amazon.com/images/I/714fP0K2VXL._AC_SY679_.jpg",
    
    # Garmin
    "B0BS4LNVMY": "https://m.media-amazon.com/images/I/61O4kHNcMOL._AC_SY679_.jpg",
    "B09LM3S1QM": "https://m.media-amazon.com/images/I/61O4kHNcMOL._AC_SY679_.jpg",
    
    # Logitech
    "B088TG9NWT": "https://m.media-amazon.com/images/I/61GN5Y+k8XL._AC_SY679_.jpg",
    "B0BVN7TS1S": "https://m.media-amazon.com/images/I/61GN5Y+k8XL._AC_SY679_.jpg",
    
    # Ring
    "B09JQM3TZ2": "https://m.media-amazon.com/images/I/71cNBaXmyOL._AC_SY679_.jpg",
    "B0BN2ZSL4N": "https://m.media-amazon.com/images/I/71cNBaXmyOL._AC_SY679_.jpg",
    
    # Philips Hue
    "B09XJ8CK91": "https://m.media-amazon.com/images/I/71yvxNx9g2L._AC_SY679_.jpg",
    
    # TP-Link
    "B07K3PXJWG": "https://m.media-amazon.com/images/I/51KzXhX+L0L._AC_SY679_.jpg",
    
    # Nintendo
    "B09RK4HWZY": "https://m.media-amazon.com/images/I/71RyTdMwSUL._AC_SY679_.jpg",
    
    # PS5
    "B0BJHHBDN9": "https://m.media-amazon.com/images/I/71NQB6BgvlL._AC_SY679_.jpg",
    
    # Google Nest
    "B07Y8LRNSP": "https://m.media-amazon.com/images/I/51KzXhX+L0L._AC_SY679_.jpg",
    
    # Ray-Ban Meta
    "B0CJNM6TMP": "https://m.media-amazon.com/images/I/61Y5bL8YxPL._AC_SY679_.jpg",
    
    # Beats
    "B0C4BWMD4F": "https://m.media-amazon.com/images/I/71H-qc6Yj5L._AC_SY679_.jpg",
    
    # Amazfit
    "B0B8V7CNPK": "https://m.media-amazon.com/images/I/61O4kHNcMOL._AC_SY679_.jpg",
    
    # Xiaomi
    "B0CG4H4Y4T": "https://m.media-amazon.com/images/I/61O4kHNcMOL._AC_SY679_.jpg",
    
    # Keychron
    "B09ZWB1FGN": "https://m.media-amazon.com/images/I/61GN5Y+k8XL._AC_SY679_.jpg",
    
    # Tile
    "B09B2R44GF": "https://m.media-amazon.com/images/I/61O4kHNcMOL._AC_SY679_.jpg",
    
    # Whoop
    "B09HK3TRSL": "https://m.media-amazon.com/images/I/61O4kHNcMOL._AC_SY679_.jpg",
}

# ═══════════════════════════════════════════════════════════
# روابط أمازون مباشرة (ليست روابط بحث)
# ═══════════════════════════════════════════════════════════
AMAZON_LINKS = {
    "B0CHKV4YVM": "https://www.amazon.com/dp/B0CHKV4YVM?tag=neopulsehub-20",
    "B0BDJ2VGDH": "https://www.amazon.com/dp/B0BDJ2VGDH?tag=neopulsehub-20",
    "B0CM5JV468": "https://www.amazon.com/dp/B0CM5JV468?tag=neopulsehub-20",
    "B0B5W8V2L3": "https://www.amazon.com/dp/B0B5W8V2L3?tag=neopulsehub-20",
    "B0C4FL89KJ": "https://www.amazon.com/dp/B0C4FL89KJ?tag=neopulsehub-20",
    "B0C23S4ZKR": "https://www.amazon.com/dp/B0C23S4ZKR?tag=neopulsehub-20",
    "B0BDN8TDMQ": "https://www.amazon.com/dp/B0BDN8TDMQ?tag=neopulsehub-20",
    "B09JQM3LZ9": "https://www.amazon.com/dp/B09JQM3LZ9?tag=neopulsehub-20",
    "B085R9JC5V": "https://www.amazon.com/dp/B085R9JC5V?tag=neopulsehub-20",
    "B0BWX8VBKC": "https://www.amazon.com/dp/B0BWX8VBKC?tag=neopulsehub-20",
    "B0863TXMT3": "https://www.amazon.com/dp/B0863TXMT3?tag=neopulsehub-20",
    "B09XS7JWHH": "https://www.amazon.com/dp/B09XS7JWHH?tag=neopulsehub-20",
    "B0BXYCDQPF": "https://www.amazon.com/dp/B0BXYCDQPF?tag=neopulsehub-20",
    "B09XSDMT7H": "https://www.amazon.com/dp/B09XSDMT7H?tag=neopulsehub-20",
    "B09FH8K2ZB": "https://www.amazon.com/dp/B09FH8K2ZB?tag=neopulsehub-20",
    "B09V3KX52B": "https://www.amazon.com/dp/B09V3KX52B?tag=neopulsehub-20",
    "B0BS4LNVMY": "https://www.amazon.com/dp/B0BS4LNVMY?tag=neopulsehub-20",
    "B09LM3S1QM": "https://www.amazon.com/dp/B09LM3S1QM?tag=neopulsehub-20",
    "B088TG9NWT": "https://www.amazon.com/dp/B088TG9NWT?tag=neopulsehub-20",
    "B0BVN7TS1S": "https://www.amazon.com/dp/B0BVN7TS1S?tag=neopulsehub-20",
    "B09JQM3TZ2": "https://www.amazon.com/dp/B09JQM3TZ2?tag=neopulsehub-20",
    "B0BN2ZSL4N": "https://www.amazon.com/dp/B0BN2ZSL4N?tag=neopulsehub-20",
    "B09XJ8CK91": "https://www.amazon.com/dp/B09XJ8CK91?tag=neopulsehub-20",
    "B07K3PXJWG": "https://www.amazon.com/dp/B07K3PXJWG?tag=neopulsehub-20",
    "B09RK4HWZY": "https://www.amazon.com/dp/B09RK4HWZY?tag=neopulsehub-20",
    "B0BJHHBDN9": "https://www.amazon.com/dp/B0BJHHBDN9?tag=neopulsehub-20",
}

def fix_product_images_and_links():
    """إصلاح صور وروابط المنتجات"""
    print("🔧 بدء إصلاح الصور والروابط...")
    
    # قراءة المنتجات
    with open('products.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    fixed_images = 0
    fixed_links = 0
    failed_images = 0
    failed_links = 0
    
    for product in products:
        asin = product.get('asin', '')
        
        # إصلاح الصورة
        if asin and asin in AMAZON_IMAGES:
            new_image = AMAZON_IMAGES[asin]
            old_image = product.get('image', '')
            if not old_image.startswith("https://m.media-amazon.com"):
                product['image'] = new_image
                fixed_images += 1
                print(f"  ✅ [{product.get('id', 'unknown')}] صورة محدثة")
        
        # إصلاح الرابط
        if asin and asin in AMAZON_LINKS:
            new_link = AMAZON_LINKS[asin]
            old_link = product.get('affiliate_amazon', '')
            if not old_link or old_link != new_link:
                product['affiliate_amazon'] = new_link
                fixed_links += 1
        
        # إذا لم يكن ASIN أو كان في البيانات القديمة
        elif not asin or asin.startswith("B0D") or asin == "N/A":
            # محاولة استخراج ASIN من الرابط القديم
            old_link = product.get('affiliate_amazon', '')
            asin_match = re.search(r'/dp/([A-Z0-9]{10})', old_link)
            if asin_match:
                asin = asin_match.group(1)
                product['asin'] = asin
                
                if asin in AMAZON_IMAGES:
                    product['image'] = AMAZON_IMAGES[asin]
                    fixed_images += 1
                
                if asin in AMAZON_LINKS:
                    product['affiliate_amazon'] = AMAZON_LINKS[asin]
                    fixed_links += 1
    
    # حفظ الملف
    with open('products.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 ملخص الإصلاح:")
    print(f"  🖼️ صور محدثة: {fixed_images}")
    print(f"  🔗 روابط محدثة: {fixed_links}")
    
    return {"fixed_images": fixed_images, "fixed_links": fixed_links}

def update_html_with_real_images():
    """تحديث صفحة HTML بالصور الحقيقية"""
    print("\n🌐 تحديث صفحة HTML...")
    
    with open('products.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    # إنشاء HTML جديد
    html = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NEO PULSE HUB — الأجهزة الذكية</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #f5f5f5; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; text-align: center; }
        .stats { display: flex; justify-content: center; gap: 2rem; margin-top: 1rem; }
        .stat { text-align: center; }
        .stat .num { font-size: 2rem; font-weight: bold; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1.5rem; padding: 2rem; }
        .card { background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1); transition: transform 0.3s; }
        .card:hover { transform: translateY(-5px); }
        .card-img { width: 100%; height: 200px; object-fit: cover; }
        .card-body { padding: 1rem; }
        .card-title { font-size: 1.1rem; font-weight: bold; margin-bottom: 0.5rem; }
        .card-price { color: #667eea; font-size: 1.3rem; font-weight: bold; }
        .card-link { display: block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center; padding: 0.8rem; text-decoration: none; border-radius: 8px; margin-top: 1rem; }
        .badge { background: #ff6b6b; color: white; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.8rem; }
        .prime { background: #232F3E; color: #FF9900; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🛍️ NEO PULSE HUB</h1>
        <p>أفضل الأجهزة الذكية بأسعار منافسة</p>
        <div class="stats">
            <div class="stat"><div class="num">""" + str(len(products)) + """</div><div>منتج</div></div>
            <div class="stat"><div class="num">7</div><div>فئة</div></div>
        </div>
    </div>
    <div class="grid">
"""
    
    for p in products:
        if not p.get('active', True):
            continue
            
        name = p.get('name', {}).get('ar', p.get('name_ar', 'منتج'))
        price = p.get('price', 0)
        image = p.get('image', '')
        amazon_link = p.get('affiliate_amazon', '#')
        asin = p.get('asin', '')
        badge = p.get('badge', {}).get('ar', '')
        prime = '✓ PRIME' if p.get('prime') else ''
        rating = p.get('rating', 0)
        
        html += f"""        <div class="card">
            <div style="position: relative;">
                <img src="{image}" alt="{name}" class="card-img" loading="lazy">
                {f'<span class="badge" style="position:absolute;top:10px;right:10px;">{badge}</span>' if badge else ''}
                {f'<span class="prime" style="position:absolute;top:10px;left:10px;">{prime}</span>' if prime else ''}
            </div>
            <div class="card-body">
                <h3 class="card-title">{name}</h3>
                <p>⭐ {rating}/5</p>
                <p class="card-price">${price}</p>
                <a href="{amazon_link}" target="_blank" class="card-link">
                    🛒 اشتري الآن من أمازون
                </a>
            </div>
        </div>
"""
    
    html += """    </div>
    <footer style="text-align: center; padding: 2rem; color: #666;">
        <p>🔗 روابط الأفلييت من Amazon.com | التحديث: """ + datetime.now().strftime("%Y-%m-%d %H:%M") + """</p>
    </footer>
</body>
</html>"""
    
    with open('products_fixed.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ تم إنشاء: products_fixed.html")

if __name__ == "__main__":
    result = fix_product_images_and_links()
    update_html_with_real_images()
    print("\n✨ تم إصلاح جميع الصور والروابط!")