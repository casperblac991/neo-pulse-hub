#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO PULSE HUB — Content Automation Bot v2.0
ينشر مقالات مراجعة تلقائياً على المدونة مع روابط أفلييت
يستخدم Gemini لكتابة محتوى عالي الجودة
"""

import os
import json
import requests
import time
import logging
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ─────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "casperblac991/neo-pulse-hub")

BASE_DIR = Path(__file__).parent
BLOG_DIR_AR = BASE_DIR / "blog" / "ar"
BLOG_DIR_EN = BASE_DIR / "blog" / "en"

# ─────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
log = logging.getLogger("content_automation")


# ─────────────────────────────────────────────────────────────
# Gemini Helper
# ─────────────────────────────────────────────────────────────

def call_gemini(prompt: str, temperature: float = 0.7, max_tokens: int = 3000) -> str:
    """استدعاء Gemini API"""
    if not GEMINI_API_KEY:
        log.warning("⚠️ GEMINI_API_KEY not found")
        return ""
    
    try:
        response = requests.post(
            GEMINI_URL + "?key=" + GEMINI_API_KEY,
            json={
                "contents": [{
                    "role": "user",
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens,
                    "topP": 0.9
                }
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        else:
            log.error(f"❌ Gemini error: {response.status_code}")
            return ""
    except Exception as e:
        log.error(f"❌ Gemini call error: {e}")
        return ""


# ─────────────────────────────────────────────────────────────
# Content Generation
# ─────────────────────────────────────────────────────────────

def generate_product_review(product: Dict, language: str = "ar") -> str:
    """توليد مراجعة منتج باستخدام Gemini"""
    
    if language == "ar":
        name = product.get("name", {}).get("ar", "")
        category = product.get("category_ar", "")
        prompt = f"""
        أنت كاتب محتوى متخصص في المنتجات التقنية. اكتب مراجعة شاملة وجذابة للمنتج التالي:
        
        اسم المنتج: {name}
        الفئة: {category}
        السعر: ${product.get('price', 0)}
        السعر الأصلي: ${product.get('original_price', 0)}
        التقييم: {product.get('rating', 0)}/5 ({product.get('reviews', 0)} تقييم)
        المميزات: {', '.join(product.get('features_ar', [])[:5])}
        الوصف: {product.get('description', {}).get('ar', '')}
        
        اكتب مراجعة بالعربية تتضمن:
        1. مقدمة جذابة (2-3 جمل)
        2. المواصفات الرئيسية (3-4 نقاط)
        3. المميزات والعيوب (4-5 نقاط لكل)
        4. الأداء العملي (2-3 فقرات)
        5. القيمة مقابل السعر (فقرة واحدة)
        6. التوصيات النهائية (فقرة واحدة)
        
        استخدم لغة سهلة وجذابة وتجنب الكلمات المعقدة.
        """
    else:
        name = product.get("name", {}).get("en", "")
        category = product.get("category_en", "")
        prompt = f"""
        You are a tech product content writer. Write a comprehensive and engaging review for:
        
        Product: {name}
        Category: {category}
        Price: ${product.get('price', 0)}
        Original Price: ${product.get('original_price', 0)}
        Rating: {product.get('rating', 0)}/5 ({product.get('reviews', 0)} reviews)
        Features: {', '.join(product.get('features_en', [])[:5])}
        Description: {product.get('description', {}).get('en', '')}
        
        Write a review in English including:
        1. Engaging introduction (2-3 sentences)
        2. Key specifications (3-4 points)
        3. Pros and cons (4-5 each)
        4. Real-world performance (2-3 paragraphs)
        5. Value for money (1 paragraph)
        6. Final recommendations (1 paragraph)
        
        Use simple and engaging language.
        """
    
    return call_gemini(prompt, temperature=0.7, max_tokens=3000)


def generate_buying_guide(category: str, products: List[Dict], language: str = "ar") -> str:
    """توليد دليل شراء شامل"""
    
    if language == "ar":
        category_ar = products[0].get("category_ar", "") if products else ""
        products_list = "\n".join([
            f"- {p.get('name', {}).get('ar', '')}: ${p.get('price', 0)} (تقييم: {p.get('rating', 0)}/5)"
            for p in products[:5]
        ])
        
        prompt = f"""
        أنت خبير في المنتجات التقنية. اكتب دليل شراء شامل للمنتجات التالية:
        
        الفئة: {category_ar}
        المنتجات:
        {products_list}
        
        اكتب دليل شراء بالعربية يتضمن:
        1. مقدمة عن الفئة (فقرة واحدة)
        2. ما يجب البحث عنه (5-6 معايير)
        3. مقارنة بين المنتجات (جدول)
        4. نصائح الشراء (4-5 نصائح)
        5. الخلاصة والتوصيات (فقرة واحدة)
        
        استخدم لغة سهلة وشاملة.
        """
    else:
        category_en = products[0].get("category_en", "") if products else ""
        products_list = "\n".join([
            f"- {p.get('name', {}).get('en', '')}: ${p.get('price', 0)} (Rating: {p.get('rating', 0)}/5)"
            for p in products[:5]
        ])
        
        prompt = f"""
        You are a tech product expert. Write a comprehensive buying guide for:
        
        Category: {category_en}
        Products:
        {products_list}
        
        Write a buying guide in English including:
        1. Category introduction (1 paragraph)
        2. What to look for (5-6 criteria)
        3. Product comparison (table format)
        4. Buying tips (4-5 tips)
        5. Conclusion and recommendations (1 paragraph)
        
        Use clear and comprehensive language.
        """
    
    return call_gemini(prompt, temperature=0.7, max_tokens=3000)


# ─────────────────────────────────────────────────────────────
# HTML Generation
# ─────────────────────────────────────────────────────────────

def create_review_html(product: Dict, review_content: str, language: str = "ar") -> str:
    """إنشاء ملف HTML لمراجعة المنتج"""
    
    if language == "ar":
        title = product.get("name", {}).get("ar", "مراجعة المنتج")
        affiliate_link = product.get("affiliate_amazon", "")
        
        html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - مراجعة شاملة | NEO PULSE HUB</title>
    <meta name="description" content="مراجعة شاملة لـ {title} - السعر والمواصفات والتقييم">
    <meta name="keywords" content="{title}, مراجعة, تقييم, سعر">
    <link rel="canonical" href="https://neo-pulse-hub.it.com/blog/ar/{product.get('id', 'review')}.html">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Cairo', Arial, sans-serif; background: #020510; color: #e2e8f0; line-height: 1.8; }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 2rem; }}
        h1 {{ font-size: 2.5rem; margin: 1rem 0; color: #60a5fa; }}
        h2 {{ font-size: 1.8rem; margin: 1.5rem 0 1rem; color: #22d3ee; border-bottom: 2px solid #3b82f6; padding-bottom: 0.5rem; }}
        p {{ margin: 1rem 0; text-align: justify; }}
        .product-header {{ background: rgba(59, 130, 246, 0.1); padding: 2rem; border-radius: 12px; margin: 2rem 0; }}
        .price {{ font-size: 2rem; color: #10b981; font-weight: bold; }}
        .rating {{ color: #f59e0b; font-size: 1.2rem; }}
        .affiliate-btn {{ 
            display: inline-block;
            background: linear-gradient(135deg, #3b82f6, #7c3aed);
            color: white;
            padding: 1rem 2rem;
            border-radius: 8px;
            text-decoration: none;
            margin: 1rem 0;
            font-weight: bold;
            transition: all 0.3s ease;
        }}
        .affiliate-btn:hover {{ transform: translateY(-2px); box-shadow: 0 10px 20px rgba(59, 130, 246, 0.3); }}
        .content {{ background: rgba(10, 13, 26, 0.5); padding: 2rem; border-radius: 12px; margin: 2rem 0; }}
        ul, ol {{ margin-right: 2rem; margin: 1rem 0; }}
        li {{ margin: 0.5rem 0; }}
        .meta {{ color: #94a3b8; font-size: 0.9rem; margin-bottom: 1rem; }}
        footer {{ text-align: center; margin-top: 3rem; padding-top: 2rem; border-top: 1px solid #3b82f6; color: #64748b; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="meta">
            📅 {datetime.now().strftime('%d/%m/%Y')} | 👤 فريق NEO PULSE HUB
        </div>
        
        <h1>{title}</h1>
        
        <div class="product-header">
            <div class="price">${product.get('price', 0)}</div>
            <div class="rating">⭐ {product.get('rating', 0)}/5 ({product.get('reviews', 0)} تقييم)</div>
            <a href="{affiliate_link}" class="affiliate-btn" target="_blank">🛒 شراء من أمازون</a>
        </div>
        
        <div class="content">
            {review_content.replace(chr(10), '<br>')}
        </div>
        
        <footer>
            <p>© 2026 NEO PULSE HUB | جميع الحقوق محفوظة</p>
            <p>هذا المحتوى يحتوي على روابط أفلييت - نحصل على عمولة عند الشراء</p>
        </footer>
    </div>
</body>
</html>"""
    else:
        title = product.get("name", {}).get("en", "Product Review")
        affiliate_link = product.get("affiliate_amazon", "")
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Full Review | NEO PULSE HUB</title>
    <meta name="description" content="Comprehensive review of {title} - Price, specs, and rating">
    <meta name="keywords" content="{title}, review, rating, price">
    <link rel="canonical" href="https://neo-pulse-hub.it.com/blog/en/{product.get('id', 'review')}.html">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Poppins', Arial, sans-serif; background: #020510; color: #e2e8f0; line-height: 1.8; }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 2rem; }}
        h1 {{ font-size: 2.5rem; margin: 1rem 0; color: #60a5fa; }}
        h2 {{ font-size: 1.8rem; margin: 1.5rem 0 1rem; color: #22d3ee; border-bottom: 2px solid #3b82f6; padding-bottom: 0.5rem; }}
        p {{ margin: 1rem 0; text-align: justify; }}
        .product-header {{ background: rgba(59, 130, 246, 0.1); padding: 2rem; border-radius: 12px; margin: 2rem 0; }}
        .price {{ font-size: 2rem; color: #10b981; font-weight: bold; }}
        .rating {{ color: #f59e0b; font-size: 1.2rem; }}
        .affiliate-btn {{ 
            display: inline-block;
            background: linear-gradient(135deg, #3b82f6, #7c3aed);
            color: white;
            padding: 1rem 2rem;
            border-radius: 8px;
            text-decoration: none;
            margin: 1rem 0;
            font-weight: bold;
            transition: all 0.3s ease;
        }}
        .affiliate-btn:hover {{ transform: translateY(-2px); box-shadow: 0 10px 20px rgba(59, 130, 246, 0.3); }}
        .content {{ background: rgba(10, 13, 26, 0.5); padding: 2rem; border-radius: 12px; margin: 2rem 0; }}
        ul, ol {{ margin-left: 2rem; margin: 1rem 0; }}
        li {{ margin: 0.5rem 0; }}
        .meta {{ color: #94a3b8; font-size: 0.9rem; margin-bottom: 1rem; }}
        footer {{ text-align: center; margin-top: 3rem; padding-top: 2rem; border-top: 1px solid #3b82f6; color: #64748b; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="meta">
            📅 {datetime.now().strftime('%m/%d/%Y')} | 👤 NEO PULSE HUB Team
        </div>
        
        <h1>{title}</h1>
        
        <div class="product-header">
            <div class="price">${product.get('price', 0)}</div>
            <div class="rating">⭐ {product.get('rating', 0)}/5 ({product.get('reviews', 0)} reviews)</div>
            <a href="{affiliate_link}" class="affiliate-btn" target="_blank">🛒 Buy on Amazon</a>
        </div>
        
        <div class="content">
            {review_content.replace(chr(10), '<br>')}
        </div>
        
        <footer>
            <p>© 2026 NEO PULSE HUB | All rights reserved</p>
            <p>This content contains affiliate links - we earn a commission on purchases</p>
        </footer>
    </div>
</body>
</html>"""
    
    return html


# ─────────────────────────────────────────────────────────────
# File Management
# ─────────────────────────────────────────────────────────────

def save_blog_post(product: Dict, content: str, language: str = "ar") -> str:
    """حفظ مقالة المدونة"""
    
    # إنشاء اسم الملف
    product_name = product.get("name", {}).get("ar" if language == "ar" else "en", "product")
    slug = product_name.replace(" ", "-").replace("ـ", "-").lower()[:50]
    filename = f"{slug}-review.html"
    
    # اختيار المجلد
    blog_dir = BLOG_DIR_AR if language == "ar" else BLOG_DIR_EN
    blog_dir.mkdir(parents=True, exist_ok=True)
    
    # إنشاء HTML
    html_content = create_review_html(product, content, language)
    
    # حفظ الملف
    filepath = blog_dir / filename
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    log.info(f"✅ Saved blog post: {filepath}")
    return str(filepath)


# ─────────────────────────────────────────────────────────────
# Main Functions
# ─────────────────────────────────────────────────────────────

def publish_product_review(product: Dict) -> bool:
    """نشر مراجعة منتج"""
    
    try:
        log.info(f"📝 Publishing review for: {product.get('name', {}).get('ar', '')}")
        
        # توليد المحتوى بالعربية
        review_ar = generate_product_review(product, "ar")
        if review_ar:
            save_blog_post(product, review_ar, "ar")
        
        # توليد المحتوى بالإنجليزية
        review_en = generate_product_review(product, "en")
        if review_en:
            save_blog_post(product, review_en, "en")
        
        log.info(f"✅ Review published successfully")
        return True
    
    except Exception as e:
        log.error(f"❌ Error publishing review: {e}")
        return False


def publish_category_guide(category: str, products: List[Dict]) -> bool:
    """نشر دليل شراء لفئة معينة"""
    
    try:
        log.info(f"📚 Publishing buying guide for: {category}")
        
        # توليد الدليل بالعربية
        guide_ar = generate_buying_guide(category, products, "ar")
        if guide_ar:
            # حفظ الدليل
            slug = category.replace("-", "_")
            filename = f"buying-guide-{slug}-ar.html"
            filepath = BLOG_DIR_AR / filename
            BLOG_DIR_AR.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(guide_ar)
            
            log.info(f"✅ Arabic guide saved: {filepath}")
        
        # توليد الدليل بالإنجليزية
        guide_en = generate_buying_guide(category, products, "en")
        if guide_en:
            slug = category.replace("-", "_")
            filename = f"buying-guide-{slug}-en.html"
            filepath = BLOG_DIR_EN / filename
            BLOG_DIR_EN.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(guide_en)
            
            log.info(f"✅ English guide saved: {filepath}")
        
        return True
    
    except Exception as e:
        log.error(f"❌ Error publishing guide: {e}")
        return False


def auto_publish_daily() -> int:
    """نشر مقالات يومية تلقائياً"""
    
    try:
        # قراءة المنتجات
        products_file = BASE_DIR / "products.json"
        if not products_file.exists():
            log.warning("⚠️ products.json not found")
            return 0
        
        with open(products_file, "r", encoding="utf-8") as f:
            products = json.load(f)
        
        if not products:
            log.warning("⚠️ No products found")
            return 0
        
        # اختر منتج عشوائي
        product = random.choice(products)
        
        # انشر مراجعة
        if publish_product_review(product):
            return 1
        
        return 0
    
    except Exception as e:
        log.error(f"❌ Error in auto_publish_daily: {e}")
        return 0


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    log.info("🚀 Starting Content Automation Bot...")
    
    # نشر مقالة يومية
    count = auto_publish_daily()
    log.info(f"✅ Published {count} articles")
