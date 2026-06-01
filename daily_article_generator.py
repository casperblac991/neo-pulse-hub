#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 نظام التنزيل اليومي التلقائي للمقالات
- ينشئ مقالة جديدة كل يوم تلقائياً
- يدمج مع المدونة وصفحة المنتجات
- يولد روابط أمازون للتسويق
"""

import json
import random
import os
from datetime import datetime, timedelta
from pathlib import Path

class DailyArticleGenerator:
    def __init__(self):
        self.blog_dir = Path("blog/ar")
        self.products_file = "products.json"
        self.articles_data_file = "articles_data.json"
        self.articles = []
        self.products = []
        self.load_data()
    
    def load_data(self):
        """تحميل البيانات"""
        if Path(self.products_file).exists():
            with open(self.products_file, 'r', encoding='utf-8') as f:
                self.products = json.load(f)
        
        if Path(self.articles_data_file).exists():
            with open(self.articles_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # التعامل مع هيكل JSON القديم
                if isinstance(data, dict) and 'ar' in data:
                    self.articles = data['ar']
                elif isinstance(data, list):
                    self.articles = data
                else:
                    self.articles = []
        else:
            self.articles = []
    
    def save_articles_data(self):
        """حفظ بيانات المقالات"""
        # الحفاظ على هيكل JSON القديم
        data = {"ar": self.articles, "en": []}
        with open(self.articles_data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def generate_article_title(self, product):
        """توليد عنوان المقالة"""
        templates_ar = [
            "مراجعة شاملة: {name} - هل يستحق الشراء؟",
            "دليل الشراء: {name} - كل ما تحتاج معرفته",
            "{name} - مراجعة تفصيلية وأراء المستخدمين",
            "أفضل {name} في 2026 - مراجعة شاملة",
            "{name}: مراجعة شاملة مع verdict النهائي",
            " اكتشف {name} - مراجعة صادقة ومفصلة",
            "{name} - هل هو أفضل خيار في فئته؟",
            "تقرير كامل عن {name}: الميزات والعيوب",
            "{name} - مراجعة الخبراء والاختبارات",
            "كل ما تريد معرفته عن {name}",
        ]
        return random.choice(templates_ar).format(name=product.get('name', {}).get('ar', product.get('name', 'منتج')))
    
    def generate_article_content(self, product):
        """توليد محتوى المقالة"""
        name_ar = product.get('name', {}).get('ar', 'منتج')
        name_en = product.get('name', {}).get('en', 'Product')
        category = product.get('category', 'general')
        price = product.get('price', 0)
        original_price = product.get('original_price', 0)
        rating = product.get('rating', 4.5)
        reviews = product.get('reviews', 1000)
        description = product.get('description', {}).get('ar', '')
        features = product.get('features', {}).get('ar', [])
        affiliate = product.get('affiliate_amazon', '')
        
        rating_stars = "⭐" * int(rating)
        
        content = f"""---
title: "{name_ar}"
date: "{datetime.now().strftime('%Y-%m-%d')}"
category: "{category}"
rating: {rating}
price: {price}
---

# {name_ar}

![{name_ar}]({product.get('image', '')})

## مراجعة شاملة

{name_ar} هو أحد أبرز المنتجات في فئته، وقد اكتسب شعبية واسعة بين المستخدمين حول العالم. في هذه المراجعة الشاملة، سنستعرض جميع جوانب هذا المنتج لمساعدتك في اتخاذ قرار الشراء.

---

## المميزات الرئيسية ⭐

"""

        # إضافة المميزات
        if features:
            content += "- ".join([f"✅ **{f}**\n" for f in features[:5]])
        else:
            content += f"""- ✅ تصميم عصري وأنيق
- ✅ أداء عالي وفعال
- ✅ سهل الاستخدام
- ✅ جودة تصنيع عالية
- ✅ ضمان شامل
"""
        
        content += f"""

---

## المواصفات التقنية 📋

| المواصفة | القيمة |
|---------|--------|
| **الاسم** | {name_en} |
| **السعر الحالي** | ${price} |
| **السعر الأصلي** | ${original_price} |
| **التقييم** | {rating_stars} ({rating}/5) |
| **عدد المراجعات** | {reviews:,} |
| **التصنيف** | {category} |

---

## verdict النهائي 🎯

### المميزات ✅
- تقييم عالي {rating_stars}
- سعر تنافسي مع خصم {int(((original_price - price) / original_price) * 100)}%
- عدد مراجعات كبير ({reviews:,}) يدل على شعبية المنتج
- جودة تصنيع معتمدة

### العيوب المحتملة ❌
- قد يحتاج وقت للتعود على جميع الميزات
- التوصيل يستغرق 3-7 أيام عمل

---

## الحكم النهائي 💡

**{name_ar}** هو خيار ممتاز لأي شخص يبحث عن منتج عالي الجودة بسعر مناسب. التقييم {rating}/5 والعدد الكبير من المراجعات الإيجابية يؤكدان جودة هذا المنتج.

---

## أين تشتري؟ 🛒

👈 [اشتري من أمازون الآن - ${price}]({affiliate}) - رابط تسويق مدعوم

---

*ملاحظة: هذا التقرير تم توليده تلقائياً بواسطة نظام NEO PULSE HUB. آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
        
        return content
    
    def generate_html_article(self, product):
        """توليد صفحة HTML للمقالة"""
        name_ar = product.get('name', {}).get('ar', 'منتج')
        name_en = product.get('name', {}).get('en', 'Product')
        category = product.get('category', 'general')
        category_ar = product.get('category_ar', 'متفرقات')
        price = product.get('price', 0)
        original_price = product.get('original_price', 0)
        rating = product.get('rating', 4.5)
        reviews = product.get('reviews', 1000)
        image = product.get('image', '')
        affiliate = product.get('affiliate_amazon', '')
        discount = product.get('discount', 0)
        
        rating_stars = "⭐" * int(rating)
        
        slug = name_ar.replace(' ', '-').replace('/', '-').replace(':', '').replace('"', '')[:50]
        filename = f"{slug}-review.html"
        
        html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name_ar} - مراجعة شاملة | NEO PULSE HUB</title>
    <meta name="description" content="مراجعة شاملة لـ {name_ar} - تقييم {rating}/5. اكتشف المميزات والعيوب والسعر الحالي على أمازون.">
    <meta name="keywords" content="{name_ar}, مراجعة, تقييم, أمازون, شراء">
    <link rel="canonical" href="https://neo-pulse-hub.com/blog/ar/{filename}">
    
    <!-- Open Graph -->
    <meta property="og:type" content="article">
    <meta property="og:title" content="{name_ar} - مراجعة شاملة">
    <meta property="og:description" content="مراجعة شاملة لـ {name_ar} - تقييم {rating}/5">
    <meta property="og:image" content="{image}">
    
    <style>
        :root {{
            --primary: #3b82f6;
            --secondary: #7c3aed;
            --accent: #22d3ee;
            --dark-bg: #020510;
            --card-bg: #0a0d1a;
            --text: #e2e8f0;
            --text-muted: #94a3b8;
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Cairo', sans-serif;
            background: linear-gradient(135deg, var(--dark-bg), #0f172a);
            color: var(--text);
            line-height: 1.8;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        .article-header {{
            text-align: center;
            margin-bottom: 2rem;
            padding-bottom: 2rem;
            border-bottom: 2px solid var(--primary);
        }}
        
        .category-badge {{
            display: inline-block;
            background: rgba(16, 185, 129, 0.2);
            color: #10b981;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }}
        
        .article-title {{
            font-size: 2.5rem;
            color: var(--accent);
            margin-bottom: 1rem;
        }}
        
        .article-meta {{
            display: flex;
            justify-content: center;
            gap: 2rem;
            color: var(--text-muted);
            font-size: 0.9rem;
        }}
        
        .article-image {{
            width: 100%;
            max-height: 400px;
            object-fit: cover;
            border-radius: 15px;
            margin-bottom: 2rem;
        }}
        
        .price-box {{
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            margin: 2rem 0;
        }}
        
        .price-label {{
            font-size: 1rem;
            opacity: 0.9;
        }}
        
        .current-price {{
            font-size: 2.5rem;
            font-weight: bold;
            color: #fff;
        }}
        
        .original-price {{
            text-decoration: line-through;
            opacity: 0.7;
            font-size: 1.2rem;
        }}
        
        .discount-badge {{
            background: #10b981;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            margin-top: 0.5rem;
            display: inline-block;
        }}
        
        .buy-button {{
            display: block;
            background: linear-gradient(135deg, #f59e0b, #d97706);
            color: white;
            padding: 1rem 2rem;
            border-radius: 10px;
            text-decoration: none;
            font-weight: bold;
            font-size: 1.2rem;
            text-align: center;
            margin: 2rem 0;
            transition: transform 0.3s;
        }}
        
        .buy-button:hover {{
            transform: scale(1.05);
        }}
        
        h2 {{
            color: var(--accent);
            margin: 2rem 0 1rem;
            font-size: 1.8rem;
        }}
        
        h3 {{
            color: var(--primary);
            margin: 1.5rem 0 1rem;
        }}
        
        p {{
            margin-bottom: 1rem;
            color: var(--text);
        }}
        
        ul, ol {{
            margin: 1rem 0;
            padding-right: 2rem;
        }}
        
        li {{
            margin-bottom: 0.5rem;
        }}
        
        .specs-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 2rem 0;
        }}
        
        .specs-table th, .specs-table td {{
            padding: 1rem;
            border: 1px solid rgba(59, 130, 246, 0.2);
            text-align: right;
        }}
        
        .specs-table th {{
            background: var(--card-bg);
            color: var(--accent);
        }}
        
        .pros-cons {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
            margin: 2rem 0;
        }}
        
        .pros, .cons {{
            background: var(--card-bg);
            padding: 1.5rem;
            border-radius: 10px;
        }}
        
        .pros {{ border-right: 4px solid #10b981; }}
        .cons {{ border-right: 4px solid #ef4444; }}
        
        .pros h4 {{ color: #10b981; margin-bottom: 1rem; }}
        .cons h4 {{ color: #ef4444; margin-bottom: 1rem; }}
        
        .verdict-box {{
            background: linear-gradient(135deg, var(--card-bg), rgba(59, 130, 246, 0.1));
            border: 2px solid var(--primary);
            padding: 2rem;
            border-radius: 15px;
            margin: 2rem 0;
            text-align: center;
        }}
        
        .rating {{
            font-size: 2rem;
            color: #f59e0b;
            margin: 1rem 0;
        }}
        
        footer {{
            background: var(--card-bg);
            padding: 2rem;
            text-align: center;
            margin-top: 3rem;
            border-top: 2px solid var(--primary);
        }}
        
        .back-link {{
            color: var(--accent);
            text-decoration: none;
            font-weight: bold;
        }}
        
        @media (max-width: 768px) {{
            .article-title {{ font-size: 1.8rem; }}
            .pros-cons {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <article>
            <header class="article-header">
                <span class="category-badge">{category_ar}</span>
                <h1 class="article-title">{name_ar}</h1>
                <div class="article-meta">
                    <span>📅 {datetime.now().strftime('%Y-%m-%d')}</span>
                    <span>⭐ {rating}/5</span>
                    <span>👁️ {reviews:,} مراجعة</span>
                </div>
            </header>
            
            <img src="{image}" alt="{name_ar}" class="article-image">
            
            <div class="price-box">
                <div class="price-label">السعر الحالي على أمازون</div>
                <div class="current-price">${price}</div>
                <div class="original-price">${original_price}</div>
                <span class="discount-badge">خصم {discount}%</span>
            </div>
            
            <a href="{affiliate}" target="_blank" class="buy-button">
                🛒 اشتري الآن من أمازون - ${price}
            </a>
            
            <section>
                <h2>📝 مراجعة شاملة</h2>
                <p>
                    {name_ar} هو أحد أبرز المنتجات في فئته. في هذه المراجعة الشاملة، 
                    سنستعرض جميع جوانب هذا المنتج لمساعدتك في اتخاذ قرار الشراء الذكي.
                </p>
                
                <h3>⭐ المميزات</h3>
                <ul>
                    <li>تقييم عالي {rating_stars}</li>
                    <li>سعر تنافسي مع خصم {discount}%</li>
                    <li>عدد مراجعات كبير ({reviews:,})</li>
                    <li>جودة تصنيع عالية</li>
                    <li>ضمان شامل</li>
                    <li>توصيل سريع</li>
                </ul>
            </section>
            
            <section>
                <h2>📋 المواصفات التقنية</h2>
                <table class="specs-table">
                    <tr>
                        <th>المواصفة</th>
                        <th>القيمة</th>
                    </tr>
                    <tr>
                        <td>الاسم</td>
                        <td>{name_en}</td>
                    </tr>
                    <tr>
                        <td>التصنيف</td>
                        <td>{category_ar}</td>
                    </tr>
                    <tr>
                        <td>السعر</td>
                        <td>${price}</td>
                    </tr>
                    <tr>
                        <td>التقييم</td>
                        <td>{rating_stars} ({rating}/5)</td>
                    </tr>
                    <tr>
                        <td>عدد المراجعات</td>
                        <td>{reviews:,}</td>
                    </tr>
                </table>
            </section>
            
            <section>
                <h2>✅ المميزات vs ❌ العيوب</h2>
                <div class="pros-cons">
                    <div class="pros">
                        <h4>✅ المميزات</h4>
                        <ul>
                            <li>تقييم {rating}/5 ممتاز</li>
                            <li>سعر معقول</li>
                            <li>جودة عالية</li>
                            <li>سهل الاستخدام</li>
                            <li>دعم فني ممتاز</li>
                        </ul>
                    </div>
                    <div class="cons">
                        <h4>❌ العيوب</h4>
                        <ul>
                            <li>قد يحتاج وقت للتعود</li>
                            <li>التوصيل 3-7 أيام</li>
                        </ul>
                    </div>
                </div>
            </section>
            
            <div class="verdict-box">
                <h2>🎯 الحكم النهائي</h2>
                <div class="rating">{rating_stars} ({rating}/5)</div>
                <p>
                    <strong>{name_ar}</strong> هو خيار ممتاز. التقييم العالي وعدد المراجعات 
                    الكبيرة يؤكدان جودة هذا المنتج. ننصح بالشراء!
                </p>
            </div>
            
            <a href="{affiliate}" target="_blank" class="buy-button">
                🛒 اطلب الآن من أمازون
            </a>
        </article>
        
        <footer>
            <p>🔄 هذا التقرير تم توليده تلقائياً يوم {datetime.now().strftime('%Y-%m-%d')}</p>
            <p><a href="../blog_index_ar.html" class="back-link">← العودة للمدونة</a></p>
        </footer>
    </div>
</body>
</html>"""
        
        return filename, html
    
    def create_daily_article(self):
        """إنشاء مقالة يومية جديدة"""
        print("=" * 70)
        print("🎯 بدء توليد المقالات اليومية")
        print("=" * 70)
        
        # التحقق من آخر مقالة
        today = datetime.now().strftime('%Y-%m-%d')
        existing_today = [a for a in self.articles if isinstance(a, dict) and a.get('date') == today]
        
        if existing_today:
            print(f"⚠️ تم إنشاء مقالة اليوم بالفعل: {existing_today[0]['title']}")
            return None
        
        # اختيار منتج عشوائي لم يتم مراجعته
        used_products = [a.get('product_id') for a in self.articles]
        available_products = [p for p in self.products if p.get('id') not in used_products]
        
        if not available_products:
            # إعادة استخدام المنتجات القديمة
            available_products = self.products
        
        product = random.choice(available_products)
        product_id = product.get('id')
        
        print(f"📝 اختيار منتج: {product.get('name', {}).get('ar', 'غير محدد')}")
        
        # توليد المقالة
        title = self.generate_article_title(product)
        filename, html_content = self.generate_html_article(product)
        
        # حفظ ملف HTML
        filepath = self.blog_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ تم حفظ: {filepath}")
        
        # حفظ بيانات المقالة (تنسيق مطابق لل существующий)
        article_data = {
            "title": title,
            "file": filename,
            "path": f"blog/ar/{filename}",
            "product_id": product_id,
            "product_name": product.get('name', {}).get('ar', ''),
            "category": product.get('category', ''),
            "date": today,
            "created_at": datetime.now().isoformat(),
            "affiliate_link": product.get('affiliate_amazon', ''),
            "rating": product.get('rating', 0)
        }
        
        self.articles.append(article_data)
        self.save_articles_data()
        
        print(f"\n✨ تم إنشاء مقالة جديدة: '{title}'")
        print(f"📅 التاريخ: {today}")
        print(f"🔗 الملف: {filename}")
        
        return article_data
    
    def run(self):
        """تشغيل النظام"""
        # التأكد من وجود مجلد المدونة
        self.blog_dir.mkdir(parents=True, exist_ok=True)
        
        # إنشاء المقالة اليومية
        result = self.create_daily_article()
        
        if result:
            print("\n" + "=" * 70)
            print("🎉 تم إنجاز التنزيل اليومي بنجاح!")
            print("=" * 70)
            
            # عرض إحصائيات
            print(f"\n📊 إحصائيات المدونة:")
            print(f"   • إجمالي المقالات: {len(self.articles)}")
            print(f"   • المقالات اليوم: 1")
            print(f"   • المنتجات المتاحة: {len(self.products)}")
        else:
            print("\n📝 تم إنشاء مقالة اليوم بالفعل. ستصدر المقالة التالية غداً.")
        
        return result

if __name__ == "__main__":
    generator = DailyArticleGenerator()
    generator.run()