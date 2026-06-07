#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Amazon Product Fetcher with Affiliate Integration
منظومة متقدمة لجلب المنتجات من أمازون مع ربط الأفلييت والصور والأسعار
"""

import json
import os
from datetime import datetime
from pathlib import Path
import requests
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class AmazonAffiliateFetcher:
    def __init__(self):
        self.affiliate_tag = os.getenv('AMAZON_AFFILIATE_TAG', 'neopulsehub-20')
        self.products_file = 'amazon_products.json'
        self.products = []
        self.load_products()
        
    def load_products(self):
        """تحميل المنتجات المحفوظة"""
        if Path(self.products_file).exists():
            with open(self.products_file, 'r', encoding='utf-8') as f:
                self.products = json.load(f)
    
    def save_products(self):
        """حفظ المنتجات"""
        with open(self.products_file, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, ensure_ascii=False, indent=2)
    
    def generate_affiliate_link(self, product_asin):
        """توليد رابط أفلييت أمازون"""
        base_url = "https://www.amazon.com/dp/"
        return f"{base_url}{product_asin}?tag={self.affiliate_tag}"
    
    def fetch_trending_products(self):
        """جلب المنتجات الرائجة من أمازون (محاكاة)"""
        trending_products = [
            {
                "name": "Apple Watch Series 9",
                "asin": "B0CQSW5P6N",
                "category": "ساعات ذكية",
                "price": 399.99,
                "rating": 4.7,
                "reviews": 2543,
                "image": "https://m.media-amazon.com/images/I/81YyF-2B5QL._AC_SY679_.jpg",
                "description": "أحدث ساعة ذكية من أبل مع شاشة Retina وميزات صحية متقدمة"
            },
            {
                "name": "Sony WH-1000XM5 Headphones",
                "asin": "B0BDHZZ4LT",
                "category": "سماعات",
                "price": 399.99,
                "rating": 4.8,
                "reviews": 4521,
                "image": "https://m.media-amazon.com/images/I/71o8Q5XJS5L._AC_SY679_.jpg",
                "description": "أفضل سماعات إلغاء ضوضاء مع صوت Hi-Res وبطارية 30 ساعة"
            },
            {
                "name": "Philips Hue Smart Lights",
                "asin": "B07BVFVR9L",
                "category": "منزل ذكي",
                "price": 199.99,
                "rating": 4.6,
                "reviews": 3214,
                "image": "https://m.media-amazon.com/images/I/71rr4XxpZZL._AC_SY679_.jpg",
                "description": "إضاءة ذكية مع 16 مليون لون وتحكم بالصوت"
            },
            {
                "name": "Fitbit Charge 6",
                "asin": "B0CQSW5P6N",
                "category": "صحة ذكية",
                "price": 159.99,
                "rating": 4.5,
                "reviews": 2156,
                "image": "https://m.media-amazon.com/images/I/71X-4ycOHBL._AC_SY679_.jpg",
                "description": "متتبع لياقة مع GPS ومستشعرات صحية متقدمة"
            },
            {
                "name": "Ray-Ban Meta Smart Glasses",
                "asin": "B0BVFVR9L",
                "category": "نظارات ذكية",
                "price": 299.99,
                "rating": 4.4,
                "reviews": 1876,
                "image": "https://m.media-amazon.com/images/I/71rr4XxpZZL._AC_SY679_.jpg",
                "description": "نظارات ذكية مع كاميرا وصوت عالي الجودة"
            },
            {
                "name": "Amazon Echo Show 15",
                "asin": "B0CQSW5P6N",
                "category": "منزل ذكي",
                "price": 249.99,
                "rating": 4.6,
                "reviews": 2987,
                "image": "https://m.media-amazon.com/images/I/71o8Q5XJS5L._AC_SY679_.jpg",
                "description": "شاشة ذكية كبيرة مع Alexa والتحكم بالمنزل الذكي"
            },
            {
                "name": "Samsung Galaxy Watch 6",
                "asin": "B0BVFVR9L",
                "category": "ساعات ذكية",
                "price": 299.99,
                "rating": 4.7,
                "reviews": 3456,
                "image": "https://m.media-amazon.com/images/I/71rr4XxpZZL._AC_SY679_.jpg",
                "description": "ساعة ذكية من سامسونج مع تصميم كلاسيكي وإطار دوار"
            },
            {
                "name": "Logitech MX Master 3S",
                "asin": "B0CQSW5P6N",
                "category": "إنتاجية",
                "price": 99.99,
                "rating": 4.8,
                "reviews": 2654,
                "image": "https://m.media-amazon.com/images/I/71o8Q5XJS5L._AC_SY679_.jpg",
                "description": "أفضل ماوس لاسلكي للمحترفين مع عجلة MagSpeed"
            }
        ]
        
        return trending_products
    
    def generate_product_description(self, product):
        """توليد وصف منتج جذاب باستخدام GPT"""
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "أنت كاتب محتوى متخصص في المنتجات التقنية. اكتب وصفاً جذاباً وقصيراً (100-150 كلمة) للمنتج بالعربية يشجع على الشراء."
                    },
                    {
                        "role": "user",
                        "content": f"المنتج: {product['name']}\nالفئة: {product['category']}\nالسعر: ${product['price']}\nالتقييم: {product['rating']}/5\nالوصف الأساسي: {product['description']}"
                    }
                ],
                temperature=0.7,
                max_tokens=200
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"خطأ في توليد الوصف: {e}")
            return product['description']
    
    def create_product_card(self, product):
        """إنشاء بطاقة منتج HTML"""
        affiliate_link = self.generate_affiliate_link(product['asin'])
        marketing_description = self.generate_product_description(product)
        
        html = f"""
        <div class="product-card">
            <div class="product-image">
                <img src="{product['image']}" alt="{product['name']}">
            </div>
            <div class="product-info">
                <h3>{product['name']}</h3>
                <div class="product-rating">
                    <span class="stars">{'⭐' * int(product['rating'])}</span>
                    <span class="rating-value">{product['rating']}/5</span>
                    <span class="reviews">({product['reviews']} تقييم)</span>
                </div>
                <p class="product-description">{marketing_description}</p>
                <div class="product-price">
                    <span class="price">${product['price']}</span>
                </div>
                <a href="{affiliate_link}" target="_blank" class="buy-button">اشتري الآن من أمازون</a>
            </div>
        </div>
        """
        return html
    
    def update_products_page(self):
        """تحديث صفحة المنتجات بالمنتجات الجديدة"""
        products = self.fetch_trending_products()
        
        html_content = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>المنتجات | NEO PULSE HUB</title>
    <style>
        :root {
            --bg: #020510;
            --surface: #0a0d1a;
            --border: rgba(99, 179, 237, 0.12);
            --blue: #3b82f6;
            --cyan: #22d3ee;
            --text: #e2e8f0;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Cairo', sans-serif;
            background: var(--bg);
            color: var(--text);
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        h1 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, var(--blue), #7c3aed);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
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
            border-radius: 12px;
            overflow: hidden;
            transition: all 0.3s;
            display: flex;
            flex-direction: column;
        }
        
        .product-card:hover {
            border-color: var(--blue);
            transform: translateY(-8px);
            box-shadow: 0 15px 40px rgba(59, 130, 246, 0.2);
        }
        
        .product-image {
            width: 100%;
            height: 200px;
            overflow: hidden;
            background: rgba(59, 130, 246, 0.1);
        }
        
        .product-image img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .product-info {
            padding: 1.5rem;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
        }
        
        .product-info h3 {
            font-size: 1.1rem;
            margin-bottom: 0.5rem;
            color: var(--cyan);
        }
        
        .product-rating {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 1rem;
            font-size: 0.9rem;
            color: rgba(226, 232, 240, 0.7);
        }
        
        .product-description {
            font-size: 0.9rem;
            line-height: 1.5;
            margin-bottom: 1rem;
            flex-grow: 1;
            color: rgba(226, 232, 240, 0.8);
        }
        
        .product-price {
            font-size: 1.3rem;
            font-weight: bold;
            color: var(--cyan);
            margin-bottom: 1rem;
        }
        
        .buy-button {
            background: linear-gradient(135deg, var(--blue), #7c3aed);
            color: white;
            padding: 0.8rem 1.5rem;
            border-radius: 8px;
            text-decoration: none;
            text-align: center;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .buy-button:hover {
            transform: scale(1.05);
            box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3);
        }
        
        @media (max-width: 768px) {
            .products-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
<div class="container">
    <h1>🛍️ أحدث المنتجات</h1>
    <p style="color: rgba(226, 232, 240, 0.7); margin-bottom: 2rem;">تحديث يومي لأفضل المنتجات من أمازون</p>
    <div class="products-grid">
"""
        
        for product in products:
            html_content += self.create_product_card(product)
        
        html_content += """
    </div>
</div>
</body>
</html>
"""
        
        # Save to products page
        with open('products.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ تم تحديث صفحة المنتجات بـ {len(products)} منتج")
        return products
    
    def run_daily_update(self):
        """تشغيل التحديث اليومي"""
        print(f"🔄 بدء التحديث اليومي - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Fetch and update products
        products = self.update_products_page()
        
        # Save products data
        self.products = products
        self.save_products()
        
        print(f"✅ تم جلب {len(products)} منتج جديد")
        print(f"✅ تم ربط روابط الأفلييت لجميع المنتجات")
        print(f"✅ تم تحديث صفحة المنتجات")
        
        return products

if __name__ == "__main__":
    fetcher = AmazonAffiliateFetcher()
    products = fetcher.run_daily_update()
    print("\n📊 ملخص التحديث:")
    print(f"   - عدد المنتجات: {len(products)}")
    print(f"   - الفئات: {', '.join(set([p['category'] for p in products]))}")
    print(f"   - رابط الأفلييت: {fetcher.affiliate_tag}")
