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
        self.blog_dir_ar = Path("blog/ar")
        self.blog_dir_en = Path("blog/en")
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
                if isinstance(data, dict):
                    self.articles = data.get('ar', [])
                    self.articles_en = data.get('en', [])
                elif isinstance(data, list):
                    self.articles = data
                    self.articles_en = []
                else:
                    self.articles = []
                    self.articles_en = []
        else:
            self.articles = []
            self.articles_en = []
    
    def save_articles_data(self):
        """حفظ بيانات المقالات"""
        # الحفاظ على هيكل JSON القديم
        if isinstance(self.articles, list):
            data = {"ar": self.articles, "en": self.articles_en if hasattr(self, 'articles_en') else []}
        else:
            data = self.articles
            
        with open(self.articles_data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def generate_article_title(self, product, lang='ar'):
        """توليد عنوان المقالة"""
        if lang == 'ar':
            templates = [
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
            name = product.get('name', {}).get('ar', product.get('name', 'منتج'))
        else:
            templates = [
                "Comprehensive Review: {name} - Is it worth buying?",
                "Buying Guide: {name} - Everything you need to know",
                "{name} - Detailed review and user opinions",
                "Best {name} in 2026 - Comprehensive review",
                "{name}: Full review with final verdict",
                "Discover {name} - Honest and detailed review",
                "{name} - Is it the best choice in its category?",
                "Complete report on {name}: Pros and Cons",
                "{name} - Expert review and tests",
                "Everything you want to know about {name}",
            ]
            name = product.get('name', {}).get('en', product.get('name', 'Product'))
            
        return random.choice(templates).format(name=name)
    
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
    
    def generate_html_article(self, product, lang='ar'):
        """توليد صفحة HTML للمقالة"""
        name_ar = product.get('name', {}).get('ar', 'منتج')
        name_en = product.get('name', {}).get('en', 'Product')
        category = product.get('category', 'general')
        category_ar = product.get('category_ar', 'متفرقات')
        category_en = product.get('category_en', 'Miscellaneous')
        price = product.get('price', 0)
        original_price = product.get('original_price', 0)
        rating = product.get('rating', 4.5)
        reviews = product.get('reviews', 1000)
        image = product.get('image', '')
        affiliate = product.get('affiliate_amazon', '')
        discount = product.get('discount', 0)
        
        rating_stars = "⭐" * int(rating)
        
        if lang == 'ar':
            slug = name_ar.replace(' ', '-').replace('/', '-').replace(':', '').replace('"', '')[:50]
            title_tag = f"{name_ar} - مراجعة شاملة | NEO PULSE HUB"
            desc_tag = f"مراجعة شاملة لـ {name_ar} - تقييم {rating}/5. اكتشف المميزات والعيوب والسعر الحالي على أمازون."
            dir_attr = 'rtl'
            lang_attr = 'ar'
            back_text = "← العودة للمدونة"
            back_link = "../blog_index_ar.html"
            current_price_label = "السعر الحالي على أمازون"
            buy_now_text = f"🛒 اشتري الآن من أمازون - ${price}"
            review_title = "📝 مراجعة شاملة"
            review_desc = f"{name_ar} هو أحد أبرز المنتجات في فئته. في هذه المراجعة الشاملة، سنستعرض جميع جوانب هذا المنتج لمساعدتك في اتخاذ قرار الشراء الذكي."
            features_title = "⭐ المميزات"
            feature_1 = f"تقييم عالي {rating_stars}"
            feature_2 = f"سعر تنافسي مع خصم {discount}%"
            feature_3 = f"عدد مراجعات كبير ({reviews:,})"
            specs_title = "📋 المواصفات التقنية"
            spec_name = "الاسم"
            spec_cat = "التصنيف"
            spec_rating = "التقييم"
            spec_reviews = "عدد المراجعات"
            pros_title = "✅ المميزات"
            cons_title = "❌ العيوب"
            pro_1 = f"تقييم {rating}/5 ممتاز"
            pro_2 = "سعر معقول"
            pro_3 = "جودة عالية"
            con_1 = "قد يحتاج وقت للتعود"
            con_2 = "التوصيل 3-7 أيام"
            verdict_title = "🎯 الحكم النهائي"
            verdict_desc = f"<strong>{name_ar}</strong> هو خيار ممتاز. التقييم العالي وعدد المراجعات الكبيرة يؤكدان جودة هذا المنتج. ننصح بالشراء!"
            footer_text = f"🔄 هذا التقرير تم توليده تلقائياً يوم {datetime.now().strftime('%Y-%m-%d')}"
            cat_label = category_ar
            name_label = name_ar
        else:
            slug = name_en.replace(' ', '-').replace('/', '-').replace(':', '').replace('"', '')[:50]
            title_tag = f"{name_en} - Comprehensive Review | NEO PULSE HUB"
            desc_tag = f"Comprehensive review of {name_en} - Rated {rating}/5. Discover features, pros, cons, and current price on Amazon."
            dir_attr = 'ltr'
            lang_attr = 'en'
            back_text = "← Back to Blog"
            back_link = "../blog_index_en.html"
            current_price_label = "Current Price on Amazon"
            buy_now_text = f"🛒 Buy Now on Amazon - ${price}"
            review_title = "📝 Comprehensive Review"
            review_desc = f"{name_en} is one of the leading products in its category. In this comprehensive review, we will explore all aspects of this product to help you make a smart buying decision."
            features_title = "⭐ Key Features"
            feature_1 = f"High rating {rating_stars}"
            feature_2 = f"Competitive price with {discount}% discount"
            feature_3 = f"Large number of reviews ({reviews:,})"
            specs_title = "📋 Technical Specifications"
            spec_name = "Name"
            spec_cat = "Category"
            spec_rating = "Rating"
            spec_reviews = "Reviews Count"
            pros_title = "✅ Pros"
            cons_title = "❌ Cons"
            pro_1 = f"Excellent {rating}/5 rating"
            pro_2 = "Reasonable price"
            pro_3 = "High quality"
            con_1 = "May take time to get used to"
            con_2 = "Shipping takes 3-7 days"
            verdict_title = "🎯 Final Verdict"
            verdict_desc = f"<strong>{name_en}</strong> is an excellent choice. The high rating and large number of reviews confirm the quality of this product. Highly recommended!"
            footer_text = f"🔄 This report was auto-generated on {datetime.now().strftime('%Y-%m-%d')}"
            cat_label = category_en
            name_label = name_en

        filename = f"{slug}-review.html"
        
        html = f"""<!DOCTYPE html>
<html lang="{lang_attr}" dir="{dir_attr}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title_tag}</title>
    <meta name="description" content="{desc_tag}">
    <link rel="canonical" href="https://neo-pulse-hub.com/blog/{lang}/{filename}">
    
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
            font-family: {("'Cairo', sans-serif" if lang == 'ar' else "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif")};
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
        
        .specs-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 2rem 0;
        }}
        
        .specs-table th, .specs-table td {{
            padding: 1rem;
            border: 1px solid rgba(59, 130, 246, 0.2);
            text-align: {('right' if lang == 'ar' else 'left')};
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
        
        .pros {{ border-{('right' if lang == 'ar' else 'left')}: 4px solid #10b981; }}
        .cons {{ border-{('right' if lang == 'ar' else 'left')}: 4px solid #ef4444; }}
        
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
                <span class="category-badge">{cat_label}</span>
                <h1 class="article-title">{name_label}</h1>
                <div class="article-meta">
                    <span>📅 {datetime.now().strftime('%Y-%m-%d')}</span>
                    <span>⭐ {rating}/5</span>
                    <span>👁️ {reviews:,} {('مراجعة' if lang == 'ar' else 'Reviews')}</span>
                </div>
            </header>
            
            <img src="{image}" alt="{name_label}" class="article-image">
            
            <div class="price-box">
                <div class="price-label">{current_price_label}</div>
                <div class="current-price">${price}</div>
                <div class="original-price">${original_price}</div>
                <span class="discount-badge">{('خصم' if lang == 'ar' else 'Discount')} {discount}%</span>
            </div>
            
            <a href="{affiliate}" target="_blank" class="buy-button">
                {buy_now_text}
            </a>
            
            <section>
                <h2>{review_title}</h2>
                <p>{review_desc}</p>
                
                <h3>{features_title}</h3>
                <ul>
                    <li>✅ {feature_1}</li>
                    <li>✅ {feature_2}</li>
                    <li>✅ {feature_3}</li>
                    <li>✅ {('جودة تصنيع عالية' if lang == 'ar' else 'High build quality')}</li>
                    <li>✅ {('ضمان شامل' if lang == 'ar' else 'Full warranty')}</li>
                    <li>✅ {('توصيل سريع' if lang == 'ar' else 'Fast delivery')}</li>
                </ul>
            </section>
            
            <section>
                <h2>{specs_title}</h2>
                <table class="specs-table">
                    <tr><th>{spec_name}</th><td>{name_label}</td></tr>
                    <tr><th>{spec_cat}</th><td>{cat_label}</td></tr>
                    <tr><th>{spec_rating}</th><td>{rating}/5</td></tr>
                    <tr><th>{spec_reviews}</th><td>{reviews:,}</td></tr>
                </table>
            </section>
            
            <section class="pros-cons">
                <div class="pros">
                    <h4>{pros_title}</h4>
                    <ul>
                        <li>{pro_1}</li>
                        <li>{pro_2}</li>
                        <li>{pro_3}</li>
                    </ul>
                </div>
                <div class="cons">
                    <h4>{cons_title}</h4>
                    <ul>
                        <li>{con_1}</li>
                        <li>{con_2}</li>
                    </ul>
                </div>
            </section>
            
            <div class="verdict-box">
                <h2>{verdict_title}</h2>
                <div class="rating">{rating_stars} ({rating}/5)</div>
                <p>{verdict_desc}</p>
            </div>
            
            <a href="{affiliate}" target="_blank" class="buy-button">
                {buy_now_text}
            </a>
        </article>
        
        <footer>
            <p>{footer_text}</p>
            <p><a href="{back_link}" class="back-link">{back_text}</a></p>
        </footer>
    </div>
</body>
</html>"""
        
        return filename, html
    
    def create_daily_article(self):
        """إنشاء مقالة يومية جديدة باللغتين"""
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
        
        # 1. توليد المقالة العربية
        title_ar = self.generate_article_title(product, 'ar')
        filename_ar, html_ar = self.generate_html_article(product, 'ar')
        filepath_ar = self.blog_dir_ar / filename_ar
        with open(filepath_ar, 'w', encoding='utf-8') as f:
            f.write(html_ar)
        print(f"✅ تم حفظ (AR): {filepath_ar}")
        
        article_data_ar = {
            "title": title_ar,
            "file": filename_ar,
            "path": f"blog/ar/{filename_ar}",
            "product_id": product_id,
            "product_name": product.get('name', {}).get('ar', ''),
            "category": product.get('category', ''),
            "date": today,
            "created_at": datetime.now().isoformat(),
            "affiliate_link": product.get('affiliate_amazon', ''),
            "rating": product.get('rating', 0)
        }
        self.articles.append(article_data_ar)

        # 2. توليد المقالة الإنجليزية
        title_en = self.generate_article_title(product, 'en')
        filename_en, html_en = self.generate_html_article(product, 'en')
        filepath_en = self.blog_dir_en / filename_en
        with open(filepath_en, 'w', encoding='utf-8') as f:
            f.write(html_en)
        print(f"✅ تم حفظ (EN): {filepath_en}")
        
        article_data_en = {
            "title": title_en,
            "file": filename_en,
            "path": f"blog/en/{filename_en}",
            "product_id": product_id,
            "product_name": product.get('name', {}).get('en', ''),
            "category": product.get('category', ''),
            "date": today,
            "created_at": datetime.now().isoformat(),
            "affiliate_link": product.get('affiliate_amazon', ''),
            "rating": product.get('rating', 0)
        }
        self.articles_en.append(article_data_en)
        
        self.save_articles_data()
        
        print(f"\n✨ تم إنشاء مقالات جديدة بنجاح!")
        print(f"📅 التاريخ: {today}")
        
        return article_data_ar
    
    def run(self):
        """تشغيل النظام"""
        # التأكد من وجود مجلد المدونة
        self.blog_dir_ar.mkdir(parents=True, exist_ok=True)
        self.blog_dir_en.mkdir(parents=True, exist_ok=True)
        
        # إنشاء المقالة اليومية
        result = self.create_daily_article()
        
        if result:
            print("\n" + "=" * 70)
            print("🎉 تم إنجاز التنزيل اليومي بنجاح!")
            print("=" * 70)
            
            # مزامنة الفهارس
            print("\n🔄 مزامنة فهارس المدونة...")
            os.system("python3 backend/sync_blog_indices.py")
            
            # عرض إحصائيات
            print(f"\n📊 إحصائيات المدونة:")
            print(f"   • إجمالي المقالات (AR): {len(self.articles)}")
            print(f"   • إجمالي المقالات (EN): {len(self.articles_en)}")
            print(f"   • المقالات اليوم: 1")
            print(f"   • المنتجات المتاحة: {len(self.products)}")
        else:
            print("\n📝 تم إنشاء مقالة اليوم بالفعل. ستصدر المقالة التالية غداً.")
        
        return result

if __name__ == "__main__":
    generator = DailyArticleGenerator()
    generator.run()