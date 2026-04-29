#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO PULSE HUB — Content Automation Bot v2.1
ينشر مقالات مراجعة تلقائياً على المدونة مع روابط أفلييت
يستخدم OpenAI GPT-4.1-mini لكتابة محتوى عالي الجودة
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
# AI Helper
# ─────────────────────────────────────────────────────────────

def call_ai(prompt: str, temperature: float = 0.7, max_tokens: int = 3000) -> str:
    """استدعاء OpenAI API (gpt-4.1-mini)"""
    try:
        from openai import OpenAI
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        log.error(f"❌ AI call error: {e}")
        return ""


# ─────────────────────────────────────────────────────────────
# Content Generation
# ─────────────────────────────────────────────────────────────

def generate_product_review(product: Dict, language: str = "ar") -> str:
    """توليد مراجعة منتج باستخدام AI"""
    
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
    
    return call_ai(prompt)


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
    
    return call_ai(prompt)


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
    <link rel="stylesheet" href="../../css/style.css">
    <style>
        body {{ font-family: 'Cairo', sans-serif; background: #020510; color: #e2e8f0; line-height: 1.8; padding: 20px; }}
        .container {{ max-width: 800px; margin: auto; background: rgba(10, 13, 26, 0.8); padding: 30px; border-radius: 15px; border: 1px solid #3b82f6; }}
        h1 {{ color: #60a5fa; text-align: center; }}
        .price {{ font-size: 24px; color: #10b981; font-weight: bold; margin: 20px 0; }}
        .content {{ margin-top: 30px; }}
        .btn {{ display: block; width: 200px; margin: 30px auto; padding: 15px; background: #3b82f6; color: white; text-align: center; text-decoration: none; border-radius: 5px; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="price">السعر الحالي: ${product.get('price', 0)}</div>
        <div class="content">{review_content.replace(chr(10), '<br>')}</div>
        <a href="{affiliate_link}" class="btn">عرض على أمازون</a>
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
    <style>
        body {{ font-family: Arial, sans-serif; background: #020510; color: #e2e8f0; line-height: 1.8; padding: 20px; }}
        .container {{ max-width: 800px; margin: auto; background: rgba(10, 13, 26, 0.8); padding: 30px; border-radius: 15px; border: 1px solid #3b82f6; }}
        h1 {{ color: #60a5fa; text-align: center; }}
        .price {{ font-size: 24px; color: #10b981; font-weight: bold; margin: 20px 0; }}
        .content {{ margin-top: 30px; }}
        .btn {{ display: block; width: 200px; margin: 30px auto; padding: 15px; background: #3b82f6; color: white; text-align: center; text-decoration: none; border-radius: 5px; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="price">Current Price: ${product.get('price', 0)}</div>
        <div class="content">{review_content.replace(chr(10), '<br>')}</div>
        <a href="{affiliate_link}" class="btn">View on Amazon</a>
    </div>
</body>
</html>"""
    
    return html


# ─────────────────────────────────────────────────────────────
# File Management
# ─────────────────────────────────────────────────────────────

def save_blog_post(product: Dict, content: str, language: str = "ar") -> str:
    """حفظ مقالة المدونة"""
    product_name = product.get("name", {}).get("ar" if language == "ar" else "en", "product")
    slug = product_name.replace(" ", "-").lower()[:50]
    filename = f"{slug}-review.html"
    
    blog_dir = BLOG_DIR_AR if language == "ar" else BLOG_DIR_EN
    blog_dir.mkdir(parents=True, exist_ok=True)
    
    html_content = create_review_html(product, content, language)
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
        review_ar = generate_product_review(product, "ar")
        if review_ar:
            save_blog_post(product, review_ar, "ar")
        
        review_en = generate_product_review(product, "en")
        if review_en:
            save_blog_post(product, review_en, "en")
        
        return True
    except Exception as e:
        log.error(f"❌ Error publishing review: {e}")
        return False


def auto_publish_daily() -> int:
    """نشر مقالات يومية تلقائياً"""
    try:
        products_file = BASE_DIR / "products.json"
        if not products_file.exists():
            return 0
        
        with open(products_file, "r", encoding="utf-8") as f:
            products = json.load(f)
        
        if not products:
            return 0
        
        product = random.choice(products)
        if publish_product_review(product):
            return 1
        return 0
    except Exception as e:
        log.error(f"❌ Error in auto_publish_daily: {e}")
        return 0


if __name__ == "__main__":
    log.info("🚀 Starting Content Automation Bot...")
    count = auto_publish_daily()
    log.info(f"✅ Published {count} articles")
