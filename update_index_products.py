#!/usr/bin/env python3
"""
تحديث index.html لعرض جميع المنتجات (682) بدلاً من 50
"""

import json
import re

def update_index_products():
    # قراءة المنتجات من products.json
    with open('products.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    print(f"📦 قراءة {len(products)} منتج من products.json")
    
    # قراءة index.html
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    # تحويل المنتجات لصيغة JavaScript
    products_js = []
    for p in products:
        # استخراج البيانات
        prod_id = p.get('id', '')
        name = p.get('name', {})
        name_ar = name.get('ar', '') if isinstance(name, dict) else (name or '')
        name_en = name.get('en', '') if isinstance(name, dict) else ''
        
        category = p.get('category', '')
        category_ar = p.get('category_ar', '') or get_cat_ar(category)
        category_en = p.get('category_en', '') or get_cat_en(category)
        
        price = p.get('price', 0)
        if isinstance(price, str):
            price = float(price.replace('$', '').replace(',', ''))
        
        orig_price = p.get('original_price', 0)
        discount = p.get('discount', 0)
        rating = p.get('rating', 4.5)
        reviews = p.get('reviews', 1000)
        image = p.get('image', 'https://placehold.co/400x220/0a0d1a/60a5fa?text=NPH')
        
        badge = p.get('badge', {})
        badge_ar = badge.get('ar', '') if isinstance(badge, dict) else ''
        badge_en = badge.get('en', '') if isinstance(badge, dict) else ''
        
        featured = p.get('featured', False)
        amazon = p.get('affiliate_amazon', '#')
        
        prod_str = f'''  {{ "id": "{prod_id}", "name": {{ "ar": "{name_ar}", "en": "{name_en}" }}, "category": "{category}", "category_ar": "{category_ar}", "category_en": "{category_en}", "price": {price}, "original_price": {orig_price}, "discount": {discount}, "rating": {rating}, "reviews": {reviews}, "image": "{image}", "badge": {{ "ar": "{badge_ar}", "en": "{badge_en}" }}, "featured": {str(featured).lower()}, "affiliate_amazon": "{amazon}" }}'''
        products_js.append(prod_str)
    
    # البحث عن PRODUCTS_LIST القديم واستبداله
    pattern = r'const PRODUCTS_LIST = \[.*?\];'
    new_products = 'const PRODUCTS_LIST = [\n' + ',\n'.join(products_js) + '\n];'
    
    # استبدال
    new_html = re.sub(pattern, new_products, html, flags=re.DOTALL)
    
    # حفظ
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_html)
    
    print(f"✅ تم تحديث index.html بـ {len(products)} منتج")

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

if __name__ == "__main__":
    update_index_products()