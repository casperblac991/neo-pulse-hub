#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إعادة بناء صفحة المنتجات بالبيانات الأصلية مع تحسينات
"""

import json
from pathlib import Path

def load_products():
    """تحميل المنتجات من ملف products_pool.json"""
    with open('products_pool.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_html():
    """توليد صفحة HTML احترافية"""
    products = load_products()
    
    # تجميع المنتجات حسب الفئة
    categories = {}
    for product in products:
        cat = product.get('category_ar', 'أخرى')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(product)
    
    html = '''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>المنتجات | NEO PULSE HUB</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Cairo', 'Segoe UI', sans-serif;
            background: #020510;
            color: #e2e8f0;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 3rem;
            flex-wrap: wrap;
            gap: 1rem;
        }
        
        .header h1 {
            font-size: 2.5rem;
            background: linear-gradient(135deg, #3b82f6, #7c3aed);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .language-toggle {
            display: flex;
            gap: 1rem;
        }
        
        .lang-btn {
            padding: 0.5rem 1rem;
            background: rgba(59, 130, 246, 0.2);
            border: 1px solid #3b82f6;
            color: #3b82f6;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .lang-btn.active {
            background: #3b82f6;
            color: white;
        }
        
        .sidebar {
            display: flex;
            gap: 2rem;
            margin-bottom: 2rem;
            flex-wrap: wrap;
        }
        
        .categories {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }
        
        .category-btn {
            padding: 0.7rem 1.5rem;
            background: rgba(99, 179, 237, 0.1);
            border: 1px solid rgba(99, 179, 237, 0.3);
            color: #22d3ee;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 0.9rem;
        }
        
        .category-btn:hover,
        .category-btn.active {
            background: #3b82f6;
            border-color: #3b82f6;
            color: white;
        }
        
        .products-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 2rem;
            margin-top: 2rem;
        }
        
        .product-card {
            background: rgba(10, 13, 26, 0.8);
            border: 1px solid rgba(99, 179, 237, 0.2);
            border-radius: 12px;
            overflow: hidden;
            transition: all 0.3s;
            position: relative;
        }
        
        .product-card:hover {
            border-color: #3b82f6;
            transform: translateY(-8px);
            box-shadow: 0 15px 40px rgba(59, 130, 246, 0.2);
        }
        
        .product-image {
            width: 100%;
            height: 200px;
            background: rgba(59, 130, 246, 0.1);
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            position: relative;
        }
        
        .product-image img {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }
        
        .badge {
            position: absolute;
            top: 10px;
            right: 10px;
            background: #ef4444;
            color: white;
            padding: 0.3rem 0.8rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: bold;
        }
        
        .badge.featured {
            background: #8b5cf6;
        }
        
        .product-info {
            padding: 1.5rem;
        }
        
        .product-category {
            font-size: 0.75rem;
            color: rgba(226, 232, 240, 0.6);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 0.5rem;
        }
        
        .product-name {
            font-size: 1.1rem;
            font-weight: 600;
            color: #22d3ee;
            margin-bottom: 0.5rem;
            line-height: 1.3;
        }
        
        .product-rating {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 1rem;
            font-size: 0.9rem;
        }
        
        .stars {
            color: #fbbf24;
        }
        
        .price-section {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 1rem;
        }
        
        .price {
            font-size: 1.5rem;
            font-weight: bold;
            color: #22d3ee;
        }
        
        .original-price {
            font-size: 0.9rem;
            color: rgba(226, 232, 240, 0.5);
            text-decoration: line-through;
        }
        
        .discount {
            background: #ef4444;
            color: white;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: bold;
        }
        
        .buy-button {
            width: 100%;
            padding: 0.8rem;
            background: linear-gradient(135deg, #3b82f6, #7c3aed);
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 0.95rem;
        }
        
        .buy-button:hover {
            transform: scale(1.02);
            box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3);
        }
        
        .stock-info {
            font-size: 0.8rem;
            color: rgba(226, 232, 240, 0.5);
            margin-top: 0.5rem;
            text-align: center;
        }
        
        @media (max-width: 768px) {
            .products-grid {
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 1rem;
            }
            
            .header {
                flex-direction: column;
                align-items: flex-start;
            }
        }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🛍️ المنتجات</h1>
        <div class="language-toggle">
            <button class="lang-btn active" onclick="switchLanguage('ar')">العربية</button>
            <button class="lang-btn" onclick="switchLanguage('en')">English</button>
        </div>
    </div>
    
    <div class="sidebar">
        <div class="categories">
            <button class="category-btn active" onclick="filterCategory('all')">جميع المنتجات (''' + str(len(products)) + ''')</button>
'''
    
    # إضافة أزرار الفئات
    for i, (cat, items) in enumerate(categories.items()):
        html += f'            <button class="category-btn" onclick="filterCategory(\'{i}\')">{cat} ({len(items)})</button>\n'
    
    html += '''        </div>
    </div>
    
    <div class="products-grid" id="productsGrid">
'''
    
    # إضافة المنتجات
    for product in products[:30]:  # أول 30 منتج
        discount_html = f'<span class="discount">-{product.get("discount", 0)}%</span>' if product.get("discount") else ''
        badge_html = f'<span class="badge {("featured" if product.get("featured") else "")}">{product.get("badge", "")}</span>' if product.get("badge") else ''
        
        html += f'''        <div class="product-card" data-category="{product.get('category_ar', '')}">
            <div class="product-image">
                <img src="{product.get('image', '')}" alt="{product.get('name_ar', '')}">
                {badge_html}
            </div>
            <div class="product-info">
                <div class="product-category">{product.get('category_ar', '')}</div>
                <h3 class="product-name">{product.get('name_ar', '')}</h3>
                <div class="product-rating">
                    <span class="stars">{'⭐' * int(product.get('rating', 0))}</span>
                    <span>{product.get('rating', 0)}/5</span>
                    <span>({product.get('reviews', 0):,})</span>
                </div>
                <div class="price-section">
                    <span class="price">${product.get('price', 0)}</span>
                    {discount_html}
                    <span class="original-price">${product.get('original_price', 0)}</span>
                </div>
                <a href="https://www.amazon.com/s?k={product.get('name_en', '')}&tag=neopulsehub-20" target="_blank" class="buy-button">اشتري من أمازون</a>
                <div class="stock-info">المخزون: {product.get('stock', 0)} وحدة</div>
            </div>
        </div>
'''
    
    html += '''    </div>
</div>

<script>
function filterCategory(category) {
    const cards = document.querySelectorAll('.product-card');
    const buttons = document.querySelectorAll('.category-btn');
    
    buttons.forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    cards.forEach(card => {
        if (category === 'all') {
            card.style.display = 'block';
        } else {
            card.style.display = 'block';
        }
    });
}

function switchLanguage(lang) {
    const buttons = document.querySelectorAll('.lang-btn');
    buttons.forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    alert('تم تبديل اللغة إلى: ' + (lang === 'ar' ? 'العربية' : 'الإنجليزية'));
}
</script>
</body>
</html>
'''
    
    return html

if __name__ == "__main__":
    print("🔄 جاري إعادة بناء صفحة المنتجات...")
    html = generate_html()
    
    with open('products_rebuilt.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("✅ تم إنشاء صفحة المنتجات الجديدة: products_rebuilt.html")
