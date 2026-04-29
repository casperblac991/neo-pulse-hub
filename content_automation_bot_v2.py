#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO PULSE HUB — Content Automation Bot v3.0
ينشر مقالات احترافية على المدونة مع قالب محسّن
يستخدم OpenAI GPT-4.1-mini
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
TEMPLATE_FILE = BASE_DIR / "blog_template.html"

# ─────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
log = logging.getLogger("content_automation_v3")


# ─────────────────────────────────────────────────────────────
# AI Helper
# ─────────────────────────────────────────────────────────────

def call_ai(prompt: str, temperature: float = 0.7, max_tokens: int = 4000) -> str:
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
# Content Generation (2000+ characters)
# ─────────────────────────────────────────────────────────────

def generate_product_review_2000(product: Dict, language: str = "ar") -> str:
    """توليد مراجعة منتج شاملة بـ 2000+ حرف"""
    
    if language == "ar":
        name = product.get("name", {}).get("ar", "")
        category = product.get("category_ar", "")
        
        prompt = f"""
        أنت كاتب محتوى متخصص في المنتجات التقنية. اكتب مراجعة شاملة وتفصيلية للمنتج التالي:
        
        اسم المنتج: {name}
        الفئة: {category}
        السعر: ${product.get('price', 0)}
        السعر الأصلي: ${product.get('original_price', 0)}
        التقييم: {product.get('rating', 0)}/5 ({product.get('reviews', 0)} تقييم)
        
        اكتب مراجعة بالعربية بطول **2000 حرف على الأقل** تتضمن:
        
        1. **المقدمة** (200-300 حرف): مقدمة جذابة تشرح سبب اختيارك لهذا المنتج
        2. **المواصفات التقنية** (300-400 حرف): شرح مفصل للمواصفات الرئيسية
        3. **المميزات الرئيسية** (400-500 حرف): 5-6 مميزات مع شرح كل واحدة
        4. **العيوب والتحديات** (300-400 حرف): 3-4 عيوب محتملة
        5. **الأداء العملي** (400-500 حرف): تجربة استخدام المنتج في الحياة اليومية
        6. **القيمة مقابل السعر** (200-300 حرف): هل يستحق السعر؟
        7. **الخلاصة والتوصيات** (200-300 حرف): من يجب أن يشتري هذا المنتج؟
        
        استخدم لغة سهلة وجذابة وتجنب الكلمات المعقدة. أضف أمثلة عملية وحقيقية.
        """
    else:
        name = product.get("name", {}).get("en", "")
        category = product.get("category_en", "")
        
        prompt = f"""
        You are a professional tech product content writer. Write a comprehensive and detailed review for:
        
        Product: {name}
        Category: {category}
        Price: ${product.get('price', 0)}
        Original Price: ${product.get('original_price', 0)}
        Rating: {product.get('rating', 0)}/5 ({product.get('reviews', 0)} reviews)
        
        Write a review in English with at least **2000 characters** including:
        
        1. **Introduction** (200-300 chars): Engaging intro explaining why you chose this product
        2. **Technical Specifications** (300-400 chars): Detailed explanation of main specs
        3. **Key Features** (400-500 chars): 5-6 features with detailed explanations
        4. **Drawbacks** (300-400 chars): 3-4 potential weaknesses
        5. **Real-world Performance** (400-500 chars): Practical daily usage experience
        6. **Value for Money** (200-300 chars): Is it worth the price?
        7. **Conclusion & Recommendations** (200-300 chars): Who should buy this product?
        
        Use simple and engaging language with practical examples.
        """
    
    return call_ai(prompt, temperature=0.7, max_tokens=4000)


def calculate_read_time(text: str) -> int:
    """حساب وقت القراءة بالدقائق (متوسط 200 كلمة في الدقيقة)"""
    words = len(text.split())
    return max(1, round(words / 200))


def format_html_content(review_text: str, product: Dict, language: str = "ar") -> str:
    """تنسيق محتوى المراجعة بـ HTML"""
    
    if language == "ar":
        # تقسيم المراجعة إلى أقسام
        sections = {
            "intro": f"<h2 id='intro'>المقدمة</h2><p>{review_text[:300]}</p>",
            "specs": f"<h2 id='specs'>المواصفات التقنية</h2><p>{review_text[300:700]}</p>",
            "features": f"<h2 id='features'>المميزات والعيوب</h2><div class='pros-cons-container'><div class='pros'><h4>✓ المميزات</h4><ul><li>سهولة الاستخدام</li><li>جودة البناء</li><li>الأداء العالي</li></ul></div><div class='cons'><h4>✗ العيوب</h4><ul><li>السعر مرتفع نسبياً</li><li>البطارية قد تكون أقصر</li></ul></div></div>",
            "performance": f"<h2 id='performance'>الأداء العملي</h2><p>{review_text[700:1200]}</p>",
            "value": f"<h2 id='value'>القيمة مقابل السعر</h2><p>{review_text[1200:1500]}</p>",
            "conclusion": f"<h2 id='conclusion'>الخلاصة</h2><p>{review_text[1500:]}</p>"
        }
        
        # إضافة قسم التقييم
        rating_html = f"""
        <div class="rating-section">
            <h3>التقييم النهائي</h3>
            <div class="stars">{'⭐' * int(product.get('rating', 4))}</div>
            <div class="rating-text">{product.get('rating', 4)}/5 - بناءً على {product.get('reviews', 0)} تقييم</div>
        </div>
        """
        
        html = "\n".join(sections.values()) + rating_html
    else:
        sections = {
            "intro": f"<h2 id='intro'>Introduction</h2><p>{review_text[:300]}</p>",
            "specs": f"<h2 id='specs'>Technical Specifications</h2><p>{review_text[300:700]}</p>",
            "features": f"<h2 id='features'>Pros & Cons</h2><div class='pros-cons-container'><div class='pros'><h4>✓ Pros</h4><ul><li>Easy to use</li><li>Great build quality</li><li>High performance</li></ul></div><div class='cons'><h4>✗ Cons</h4><ul><li>Price is relatively high</li><li>Battery life could be longer</li></ul></div></div>",
            "performance": f"<h2 id='performance'>Real-world Performance</h2><p>{review_text[700:1200]}</p>",
            "value": f"<h2 id='value'>Value for Money</h2><p>{review_text[1200:1500]}</p>",
            "conclusion": f"<h2 id='conclusion'>Conclusion</h2><p>{review_text[1500:]}</p>"
        }
        
        rating_html = f"""
        <div class="rating-section">
            <h3>Final Rating</h3>
            <div class="stars">{'⭐' * int(product.get('rating', 4))}</div>
            <div class="rating-text">{product.get('rating', 4)}/5 - Based on {product.get('reviews', 0)} reviews</div>
        </div>
        """
        
        html = "\n".join(sections.values()) + rating_html
    
    return html


# ─────────────────────────────────────────────────────────────
# File Management
# ─────────────────────────────────────────────────────────────

def save_blog_post(product: Dict, content: str, language: str = "ar") -> str:
    """حفظ مقالة المدونة باستخدام القالب الجديد"""
    
    product_name = product.get("name", {}).get("ar" if language == "ar" else "en", "product")
    slug = product_name.replace(" ", "-").lower()[:50]
    filename = f"{slug}-review.html"
    
    blog_dir = BLOG_DIR_AR if language == "ar" else BLOG_DIR_EN
    blog_dir.mkdir(parents=True, exist_ok=True)
    
    # قراءة القالب
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        template = f.read()
    
    # حساب وقت القراءة
    read_time = calculate_read_time(content)
    
    # تنسيق المحتوى
    formatted_content = format_html_content(content, product, language)
    
    # تاريخ اليوم
    today = datetime.now().strftime("%Y-%m-%d")
    
    # استبدال المتغيرات
    if language == "ar":
        title_ar = product.get("name", {}).get("ar", "")
        title_en = product.get("name", {}).get("en", "")
        html = template.replace("{TITLE_AR}", title_ar)
        html = html.replace("{TITLE_EN}", title_en)
        html = html.replace("{DATE}", today)
        html = html.replace("{READ_TIME}", str(read_time))
        html = html.replace("{CONTENT}", formatted_content)
        html = html.replace("{AFFILIATE_LINK}", product.get("affiliate_amazon", "#"))
        html = html.replace("{UPDATE_DATE}", today)
        html = html.replace("{META_DESCRIPTION}", f"مراجعة شاملة لـ {title_ar} - السعر والمواصفات والتقييم")
        html = html.replace("{META_KEYWORDS}", f"{title_ar}, مراجعة, أمازون, سعر")
    else:
        title_ar = product.get("name", {}).get("ar", "")
        title_en = product.get("name", {}).get("en", "")
        html = template.replace("{TITLE_AR}", title_en)
        html = html.replace("{TITLE_EN}", title_en)
        html = html.replace("{DATE}", today)
        html = html.replace("{READ_TIME}", str(read_time))
        html = html.replace("{CONTENT}", formatted_content)
        html = html.replace("{AFFILIATE_LINK}", product.get("affiliate_amazon", "#"))
        html = html.replace("{UPDATE_DATE}", today)
        html = html.replace("{META_DESCRIPTION}", f"Complete review of {title_en} - Price, Specs & Rating")
        html = html.replace("{META_KEYWORDS}", f"{title_en}, review, amazon, price")
    
    filepath = blog_dir / filename
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    
    log.info(f"✅ Saved blog post: {filepath}")
    return str(filepath)


# ─────────────────────────────────────────────────────────────
# Main Functions
# ─────────────────────────────────────────────────────────────

def publish_product_review(product: Dict) -> bool:
    """نشر مراجعة منتج احترافية"""
    try:
        log.info(f"📝 Publishing review for: {product.get('name', {}).get('ar', '')}")
        
        # توليد المراجعة بالعربية
        review_ar = generate_product_review_2000(product, "ar")
        if review_ar and len(review_ar) > 500:
            save_blog_post(product, review_ar, "ar")
        
        # توليد المراجعة بالإنجليزية
        review_en = generate_product_review_2000(product, "en")
        if review_en and len(review_en) > 500:
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
    log.info("🚀 Starting Content Automation Bot v3.0...")
    count = auto_publish_daily()
    log.info(f"✅ Published {count} articles")
