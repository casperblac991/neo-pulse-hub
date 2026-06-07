#!/usr/bin/env python3
"""
إعادة بناء صفحة products.html بالكامل
لتحميل جميع المنتجات من products.json
"""

import json
import re

def rebuild_products_page():
    # قراءة المنتجات
    with open('products.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    print(f"📦 قراءة {len(products)} منتج")
    
    # إنشاء JavaScript للمنتجات
    products_js = []
    for p in products:
        name_ar = p.get('name', {}).get('ar', '') or ''
        name_en = p.get('name', {}).get('en', '') or ''
        cat = p.get('category', '')
        cat_ar = p.get('category_ar', '') or get_cat_ar(cat)
        cat_en = p.get('category_en', '') or get_cat_en(cat)
        price = p.get('price', 0)
        if isinstance(price, str):
            price = float(price.replace('$', '').replace(',', ''))
        orig_price = p.get('original_price', 0)
        discount = p.get('discount', 0)
        rating = p.get('rating', 4.5)
        reviews = p.get('reviews', 1000)
        image = p.get('image', 'https://placehold.co/400x400/1e3a5f/ffffff?text=Product')
        badge = p.get('badge', {})
        badge_ar = badge.get('ar', '') if isinstance(badge, dict) else (badge or '')
        badge_en = badge.get('en', '') if isinstance(badge, dict) else ''
        in_stock = p.get('in_stock', True)
        
        prod_str = f'''{{
  id: "{p.get('id', '')}",
  name_ar: "{name_ar}",
  name_en: "{name_en}",
  category: "{cat}",
  category_ar: "{cat_ar}",
  category_en: "{cat_en}",
  price: {price},
  original_price: {orig_price},
  discount: {discount},
  rating: {rating},
  reviews: {reviews},
  image: "{image}",
  badge_ar: "{badge_ar}",
  badge_en: "{badge_en}",
  in_stock: {str(in_stock).lower()}
}}'''
        products_js.append(prod_str)
    
    # قراءة ملف products.html القديم
    with open('products.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    # البحث عن INLINE_PRODUCTS واستبداله
    pattern = r'const INLINE_PRODUCTS = \[.*?\];'
    
    # إنشاء المحتوى الجديد
    new_inline = 'const INLINE_PRODUCTS = [\n  ' + ',\n  '.join(products_js) + '\n];'
    
    # استبدال
    new_html = re.sub(pattern, new_inline, html, flags=re.DOTALL)
    
    # حفظ
    with open('products.html', 'w', encoding='utf-8') as f:
        f.write(new_html)
    
    print(f"✅ تم تحديث products.html بـ {len(products)} منتج")
    print(f"📊 حجم الملف: {len(new_html)} حرف")

def get_cat_en(cat):
    names = {
        'smartwatch': 'Smart Watch',
        'earbuds': 'Wireless Earbuds',
        'headphones': 'Headphones',
        'smart-home': 'Smart Home',
        'health': 'Smart Health',
        'productivity': 'Productivity',
        'gaming': 'Gaming',
        'cameras': 'Cameras',
        'smart-glasses': 'Smart Glasses',
        'accessories': 'Accessories',
        'kitchen': 'Smart Kitchen',
        'sports': 'Sports',
        'car': 'Car Electronics',
        'kids': 'Kids Tech',
        'office': 'Office'
    }
    return names.get(cat, cat)

def get_cat_ar(cat):
    names = {
        'smartwatch': 'ساعات ذكية',
        'earbuds': 'سماعات لاسلكية',
        'headphones': 'سماعات رأس',
        'smart-home': 'المنزل الذكي',
        'health': 'الصحة الذكية',
        'productivity': 'الإنتاجية',
        'gaming': 'ألعاب وترفيه',
        'cameras': 'كاميرات',
        'smart-glasses': 'نظارات ذكية',
        'accessories': 'إكسسوارات',
        'kitchen': 'مطبخ ذكي',
        'sports': 'رياضة',
        'car': 'إلكترونيات سيارات',
        'kids': 'تقنية أطفال',
        'office': 'أدوات مكتبية'
    }
    return names.get(cat, cat)

if __name__ == "__main__":
    rebuild_products_page()