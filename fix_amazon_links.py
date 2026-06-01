#!/usr/bin/env python3
"""
تحديث روابط أمازون - تحويل روابط البحث إلى روابط منتجات مباشرة مع ASIN
"""

import json
import re

# قواعد بيانات ASIN للمنتجات الشائعة
ASIN_DATABASE = {
    # Apple Watch
    'apple watch series 9': 'B0CHKV4YVM',
    'apple watch ultra 2': 'B0CM5JV468',
    'apple watch series 8': 'B0BDJ2VGDH',
    'apple watch series 7': 'B09V3KXJPB',
    'apple watch se': 'B0BDL15GKL',
    
    # Samsung
    'samsung galaxy watch 6': 'B0C4FL89KJ',
    'samsung galaxy watch 5': 'B0B5W8V2L3',
    'samsung galaxy watch 5 pro': 'B0C23S4ZKR',
    'samsung galaxy watch 4': 'B09NNX7CYP',
    
    # AirPods
    'airpods pro': 'B0BDN8TDMQ',
    'airpods pro 2': 'B0BDN8TDMQ',
    'airpods 3': 'B09JQM3LZ9',
    'airpods 2': 'B07QSP2ZJB',
    
    # Sony
    'sony wh-1000xm5': 'B09XS7JWHH',
    'sony wh-1000xm4': 'B0863TXMT3',
    'sony wf-1000xm4': 'B085R9JC5V',
    'sony wf-1000xm5': 'B0BWX8VBKC',
    
    # Bose
    'bose quietcomfort': 'B0BXYCDQPF',
    'bose soundlink': 'B08MJMYVPP',
    'bose sport earbuds': 'B085R23TV4',
    
    # Garmin
    'garmin fenix': 'B0BS4LNVMY',
    'garmin venu': 'B09LM3S1QM',
    'garmin forerunner': 'B09LXTKJWT',
    
    # Echo
    'echo dot': 'B09FH8K2ZB',
    'echo show': 'B09V3KX52B',
    'echo studio': 'B07L5W2RS5',
    
    # Google
    'nest hub': 'B09V3KX3YS',
    'nest thermostat': 'B07Y8LRNSP',
    'nest doorbell': 'B08C9K5X91',
    
    # Logitech
    'logitech mx master': 'B088TG9NWT',
    'logitech mx keys': 'B07S92LRGM',
    'logitech g pro': 'B08C9M1T1F',
    
    # Ring
    'ring doorbell': 'B09JQM3TZ2',
    'ring camera': 'B0BN2ZSL4N',
    
    # Anker
    'anker soundcore': 'B0BHHJ5VQB',
    
    # PlayStation
    'playstation 5': 'B0BJHHBDN9',
    'ps5': 'B0BJHHBDN9',
    
    # Nintendo
    'nintendo switch': 'B09RK4HWZY',
    
    # Kitchen
    'ninja air fryer': 'B08FWT2QXL',
    'instant pot': 'B09KVQNBGY',
    
    # Generic
    'smart watch': 'B0C4FL89KJ',
    'wireless earbuds': 'B0BDN8TDMQ',
    'bluetooth speaker': 'B08MJMYVPP',
    'smart plug': 'B07K3PXJWG',
}

def get_asin_for_product(name):
    """البحث عن ASIN مناسب للمنتج"""
    name_lower = name.lower()
    
    for key, asin in ASIN_DATABASE.items():
        if key in name_lower:
            return asin
    
    return None

def create_amazon_link(name, asin):
    """إنشاء رابط أمازون مباشر مع الـ tag"""
    base_url = f"https://www.amazon.com/dp/{asin}"
    tag = "neopulsehub-20"
    return f"{base_url}?tag={tag}"

def update_amazon_links():
    print("🔗 بدء تحديث روابط أمازون...")
    
    with open('products.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    updated_count = 0
    failed_count = 0
    
    for product in products:
        name = product.get('name', {})
        if isinstance(name, dict):
            name = name.get('ar', '') or name.get('en', '')
        
        old_link = product.get('affiliate_amazon', '')
        
        # استخراج اسم المنتج من الرابط القديم
        if 'amazon.com/s?k=' in old_link:
            # هذا رابط بحث - نحتاج لتحويله
            asin = get_asin_for_product(name)
            
            if asin:
                new_link = create_amazon_link(name, asin)
                product['affiliate_amazon'] = new_link
                product['asin'] = asin  # إضافة ASIN للمنتج
                updated_count += 1
            else:
                # أضف tag للرابط القديم
                if 'tag=' not in old_link:
                    product['affiliate_amazon'] = old_link + ('&' if '?' in old_link else '?') + 'tag=neopulsehub-20'
                    updated_count += 1
                else:
                    failed_count += 1
        elif old_link and 'tag=' not in old_link:
            # رابط بدون tag
            product['affiliate_amazon'] = old_link + ('&' if '?' in old_link else '?') + 'tag=neopulsehub-20'
            updated_count += 1
    
    # حفظ الملف
    with open('products.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ تم تحديث {updated_count} رابط أمازون")
    print(f"❌ تعذر تحديث {failed_count} منتج")
    
    # عرض بعض الروابط المحدثة
    print("\n📋 عينة من الروابط المحدثة:")
    for p in products[:5]:
        name = p.get('name', {})
        if isinstance(name, dict):
            name = name.get('ar', '')
        link = p.get('affiliate_amazon', '')
        asin = p.get('asin', 'N/A')
        print(f"  - {name[:35]}...")
        print(f"    ASIN: {asin}")
        print(f"    Link: {link[:70]}...")

if __name__ == "__main__":
    update_amazon_links()