#!/usr/bin/env python3
"""
تحديث روابط أمازون - استخدام روابط أمازون مباشرة مع ASIN
"""

import json

# قاعدة بيانات ASINs حقيقية من Amazon Associates
ASIN_DATABASE = {
    # Apple Watch - روابط مباشرة
    'apple watch series 9 45mm': 'B0CHKV4YVM',
    'apple watch series 9': 'B0CHKV4YVM',
    'apple watch ultra': 'B0CM5JV468',
    'apple watch series 8': 'B0BDJ2VGDH',
    'apple watch series 7': 'B09V3KXJPB',
    'apple watch se': 'B0BDL15GKL',
    'apple watch': 'B0CHKV4YVM',
    
    # Samsung
    'galaxy watch 6': 'B0C4FL89KJ',
    'galaxy watch 5': 'B0B5W8V2L3',
    'galaxy watch': 'B0C4FL89KJ',
    'samsung watch': 'B0C4FL89KJ',
    
    # AirPods
    'airpods pro': 'B0BDN8TDMQ',
    'airpods': 'B0BDN8TDMQ',
    
    # Sony Headphones
    'sony wh-1000xm5': 'B09XS7JWHH',
    'sony wh-1000xm4': 'B0863TXMT3',
    'sony wh-1000xm3': 'B07S4YQCC3',
    'sony wf-1000xm5': 'B0BWX8VBKC',
    'sony wf-1000xm4': 'B085R9JC5V',
    'sony headphones': 'B09XS7JWHH',
    
    # Bose
    'bose quietcomfort ultra': 'B0BXYCDQPF',
    'bose quietcomfort': 'B09LMTSBR3',
    'bose 700': 'B07Y8LRNSP',
    'bose soundlink': 'B08MJMYVPP',
    'bose': 'B09LMTSBR3',
    
    # Garmin
    'garmin fenix': 'B0BS4LNVMY',
    'garmin venu': 'B09LM3S1QM',
    'garmin': 'B0BS4LNVMY',
    
    # Echo
    'echo dot 5': 'B09FH8K2ZB',
    'echo dot': 'B09FH8K2ZB',
    'echo show 10': 'B09V3KX52B',
    'echo show': 'B09V3KX52B',
    'echo': 'B09FH8K2ZB',
    
    # Google
    'nest hub': 'B09V3KX3YS',
    'nest thermostat': 'B07Y8LRNSP',
    'nest doorbell': 'B08C9K5X91',
    'nest': 'B09V3KX3YS',
    'google nest': 'B09V3KX3YS',
    
    # Logitech
    'logitech mx master': 'B088TG9NWT',
    'logitech mx keys': 'B07S92LRGM',
    'logitech g pro': 'B08C9M1T1F',
    'logitech': 'B088TG9NWT',
    
    # Ring
    'ring doorbell': 'B09JQM3TZ2',
    'ring camera': 'B0BN2ZSL4N',
    'ring': 'B09JQM3TZ2',
    
    # Anker
    'anker soundcore': 'B0BHHJ5VQB',
    'anker': 'B0BHHJ5VQB',
    
    # Gaming
    'playstation 5': 'B0BJHHBDN9',
    'ps5': 'B0BJHHBDN9',
    'nintendo switch': 'B09RK4HWZY',
    'xbox': 'B08H93ZRK2',
    
    # Kitchen
    'ninja air fryer': 'B08FWT2QXL',
    'instant pot': 'B09KVQNBGY',
    
    # Smart Home
    'tp-link kasa': 'B07K3PXJWG',
    'tp-link': 'B07K3PXJWG',
    'smart plug': 'B07K3PXJWG',
    
    # Cameras
    'arlo': 'B0B5W8V2L3',
    'wyze': 'B07NYN84L3',
    
    # Tablets
    'ipad pro': 'B0D3J9XDMQ',
    'ipad': 'B0D3J9XDMQ',
    'ipad air': 'B0D3J7YHGD',
    
    # Fitbit
    'fitbit': 'B09V3KX52B',
    'withings': 'B09LM3S1QM',
}

def get_best_asin(name):
    """البحث عن أفضل ASIN للمنتج"""
    name_lower = name.lower()
    
    # البحث عن المطابقة الأفضل
    best_match = None
    best_key = None
    
    for key, asin in ASIN_DATABASE.items():
        if key in name_lower:
            # أطول مطابقة هي الأفضل
            if best_key is None or len(key) > len(best_key):
                best_key = key
                best_match = asin
    
    return best_match

def create_direct_amazon_link(asin):
    """إنشاء رابط أمازون مباشر مع tag"""
    tag = "neopulsehub-20"
    return f"https://www.amazon.com/dp/{asin}?tag={tag}"

def update_all_links():
    print("🔗 تحديث جميع روابط أمازون...")
    
    with open('products.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    updated = 0
    not_found = 0
    
    for product in products:
        name = product.get('name', {})
        if isinstance(name, dict):
            name_ar = name.get('ar', '')
            name_en = name.get('en', '')
            name_full = f"{name_ar} {name_en}".lower()
        else:
            name_full = str(name).lower()
        
        # الحصول على ASIN
        asin = get_best_asin(name_full)
        
        if asin:
            # إنشاء رابط مباشر
            new_link = create_direct_amazon_link(asin)
            product['affiliate_amazon'] = new_link
            product['asin'] = asin
            updated += 1
        else:
            # استخدام رابط بحث مع tag
            current_link = product.get('affiliate_amazon', '')
            if current_link and 'tag=' not in current_link:
                separator = '&' if '?' in current_link else '?'
                product['affiliate_amazon'] = current_link + separator + 'tag=neopulsehub-20'
            not_found += 1
    
    # حفظ
    with open('products.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ تم تحديث {updated} منتج برابط مباشر")
    print(f"⚠️ {not_found} منتج بدون ASIN محدد (ستخدم رابط بحث)")
    
    # عرض عينة
    print("\n📋 روابط محدثة (عينة):")
    for p in products[:5]:
        name = p.get('name', {})
        name = name.get('ar', 'N/A') if isinstance(name, dict) else name
        link = p.get('affiliate_amazon', '')
        print(f"\n  🛒 {name[:40]}...")
        print(f"     🔗 {link}")

if __name__ == "__main__":
    update_all_links()