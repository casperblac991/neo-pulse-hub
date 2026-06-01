#!/usr/bin/env python3
"""
تحديث صفحة products.html بجميع المنتجات من products.json
لضمان ظهور 682 منتج على الموقع
"""

import json

def update_products_html():
    # قراءة المنتجات
    with open('products.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    print(f"📦 قراءة {len(products)} منتج من products.json")
    
    # تحويل المنتجات لصيغة INLINE_PRODUCTS
    inline_products = []
    for p in products:
        # استخراج الاسم
        name_ar = p.get('name', {}).get('ar', '') or p.get('name_ar', '')
        name_en = p.get('name', {}).get('en', '') or p.get('name_en', '')
        
        # استخراج التصنيف
        cat_ar = p.get('category_ar', '')
        cat_en = p.get('category_en', '')
        category = p.get('category', '')
        
        # استخراج السعر
        price = p.get('price', 0)
        original_price = p.get('original_price', 0)
        discount = p.get('discount', 0)
        
        # استخراج التقييم
        rating = p.get('rating', 4.5)
        reviews = p.get('reviews', 1000)
        
        # استخراج الصورة
        image = p.get('image', 'https://placehold.co/400x400/1e3a5f/ffffff?text=Product')
        
        # استخراج البادج
        badge = p.get('badge', {})
        badge_ar = badge.get('ar', '') if isinstance(badge, dict) else (badge or p.get('badge_ar', ''))
        badge_en = badge.get('en', '') if isinstance(badge, dict) else p.get('badge_en', '')
        
        # حالة المخزون
        in_stock = p.get('in_stock', True)
        featured = p.get('featured', False)
        
        inline_prod = {
            "id": p.get('id', ''),
            "name_ar": name_ar,
            "name_en": name_en,
            "category": category,
            "category_ar": cat_ar,
            "category_en": cat_en,
            "price": price,
            "original_price": original_price,
            "discount": discount,
            "rating": rating,
            "reviews": reviews,
            "image": image,
            "badge_ar": badge_ar,
            "badge_en": badge_en,
            "in_stock": in_stock,
            "featured": featured
        }
        inline_products.append(inline_prod)
    
    # تحويل لأفضل صيغة
    inline_json = json.dumps(inline_products, ensure_ascii=False)
    
    print(f"✅ تم تحويل {len(inline_products)} منتج")
    
    # حفظ في ملف مؤقت
    with open('inline_products_temp.json', 'w', encoding='utf-8') as f:
        f.write(inline_json)
    
    print(f"💾 تم حفظ المنتجات المؤقتة في inline_products_temp.json")
    print(f"📊 الحجم: {len(inline_json)} حرف")
    
    return len(inline_products)

if __name__ == "__main__":
    count = update_products_html()
    print(f"\n🎯 جاهز لتحديث products.html بـ {count} منتج")