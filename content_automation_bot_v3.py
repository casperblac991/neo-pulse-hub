#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO PULSE HUB — Content Automation Bot v3.0 (Daily Reports Edition)
تطوير: Manus AI
الوظيفة: توليد تقارير يومية شاملة للمنتجات (أسعار، مواصفات، عيوب، نصائح)
"""

import os
import json
import random
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Config
BASE_DIR = Path(__file__).parent
BLOG_DIR_AR = BASE_DIR / "blog" / "ar"
BLOG_DIR_EN = BASE_DIR / "blog" / "en"
TEMPLATE_FILE = BASE_DIR / "blog_template.html"
PRODUCTS_FILE = BASE_DIR / "products.json"

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("BlogBotV3")

def call_ai(prompt: str) -> str:
    """استدعاء OpenAI API عبر requests"""
    try:
        import requests
        api_key = os.getenv("OPENAI_API_KEY")
        api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-5-mini",
            "messages": [
                {"role": "system", "content": "You are a professional tech reviewer and market analyst."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        
        response = requests.post(f"{api_base}/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        if 'choices' not in result:
            log.error(f"❌ AI API Error: {result}")
            return ""
        return result['choices'][0]['message']['content'].strip()
    except Exception as e:
        log.error(f"❌ AI Error: {e}")
        return ""

def generate_report(product: Dict, lang: str = "ar") -> str:
    """توليد تقرير شامل للمنتج"""
    name = product.get("name", {}).get(lang, product.get("name", {}).get("en", ""))
    price = product.get("price", "N/A")
    rating = product.get("rating", "N/A")
    category = product.get("category", "Tech")
    
    if lang == "ar":
        prompt = f"""
        اكتب تقرير مراجعة احترافي وشامل للمنتج التالي لمدونة تقنية:
        المنتج: {name}
        الفئة: {category}
        السعر الحالي: ${price}
        التقييم: {rating}/5
        
        يجب أن يتضمن التقرير الأقسام التالية بوضوح باستخدام هذه العلامات [SECTION_NAME]:
        
        [INTRO]: مقدمة جذابة عن المنتج ومكانته في السوق.
        [SPECS]: قائمة مفصلة بالمواصفات التقنية.
        [PROS]: قائمة بالمميزات والايجابيات.
        [CONS]: قائمة بالعيوب والتحديات بكل صراحة.
        [PRICE_ANALYSIS]: تحليل للسعر وهل يستحق الشراء حالياً.
        [VERDICT]: التقييم النهائي ولمن يصلح هذا المنتج (نصيحة للزبون).
        
        اكتب بأسلوب مشوق ومفيد للقارئ العربي.
        """
    else:
        prompt = f"""
        Write a professional and comprehensive product review report for:
        Product: {name}
        Category: {category}
        Current Price: ${price}
        Rating: {rating}/5
        
        The report must include these sections clearly using [SECTION_NAME] markers:
        
        [INTRO]: Engaging introduction about the product.
        [SPECS]: Detailed technical specifications list.
        [PROS]: Key advantages and pros.
        [CONS]: Honest drawbacks and cons.
        [PRICE_ANALYSIS]: Price analysis and value for money.
        [VERDICT]: Final verdict and who should buy this (customer advice).
        
        Write in an engaging style for a tech blog.
        """
    
    return call_ai(prompt)

def parse_sections(text: str) -> Dict[str, str]:
    """تقسيم النص إلى أقسام بناءً على العلامات"""
    sections = {}
    patterns = {
        "intro": r"\[INTRO\]:(.*?)(?=\[|$)",
        "specs": r"\[SPECS\]:(.*?)(?=\[|$)",
        "pros": r"\[PROS\]:(.*?)(?=\[|$)",
        "cons": r"\[CONS\]:(.*?)(?=\[|$)",
        "price_analysis": r"\[PRICE_ANALYSIS\]:(.*?)(?=\[|$)",
        "verdict": r"\[VERDICT\]:(.*?)(?=\[|$)"
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.DOTALL)
        if match:
            sections[key] = match.group(1).strip()
        else:
            sections[key] = ""
    return sections

def format_report_html(sections: Dict, product: Dict, lang: str = "ar") -> str:
    """تنسيق الأقسام في قالب HTML"""
    titles = {
        "ar": {"intro": "المقدمة", "specs": "المواصفات التقنية", "pros": "المميزات", "cons": "العيوب", "price": "تحليل السعر", "verdict": "الخلاصة والنصيحة"},
        "en": {"intro": "Introduction", "specs": "Technical Specs", "pros": "Pros", "cons": "Cons", "price": "Price Analysis", "verdict": "Final Verdict"}
    }
    t = titles[lang]
    
    html = f"""
    <div class="product-report">
        <section id="intro">
            <h2>{t['intro']}</h2>
            <p>{sections['intro']}</p>
        </section>
        
        <section id="specs">
            <h2>{t['specs']}</h2>
            <div class="specs-box">{sections['specs'].replace('\n', '<br>')}</div>
        </section>
        
        <div class="pros-cons-container">
            <div class="pros">
                <h4>✅ {t['pros']}</h4>
                <p>{sections['pros'].replace('\n', '<br>')}</p>
            </div>
            <div class="cons">
                <h4>❌ {t['cons']}</h4>
                <p>{sections['cons'].replace('\n', '<br>')}</p>
            </div>
        </div>
        
        <section id="price">
            <h2>{t['price']}</h2>
            <div class="price-section">
                <div class="price-value">${product.get('price', '0')}</div>
                <p>{sections['price_analysis']}</p>
            </div>
        </section>
        
        <section id="verdict">
            <h2>{t['verdict']}</h2>
            <div class="feature-box">
                <p>{sections['verdict']}</p>
            </div>
        </section>
    </div>
    """
    return html

def run_daily_update():
    """تشغيل التحديث اليومي"""
    log.info("🚀 Starting Daily Product Report Bot...")
    
    if not PRODUCTS_FILE.exists():
        log.error("❌ products.json not found!")
        return
        
    with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
        products = json.load(f)
    
    # اختيار منتج عشوائي لتقرير اليوم
    product = random.choice(products)
    log.info(f"📦 Selected product: {product.get('name', {}).get('en')}")
    
    # توليد التقارير
    for lang in ["ar", "en"]:
        report_text = generate_report(product, lang)
        if not report_text: continue
        
        sections = parse_sections(report_text)
        html_content = format_report_html(sections, product, lang)
        
        # حفظ الملف
        save_path = save_to_blog(product, html_content, lang)
        log.info(f"✅ Report saved ({lang}): {save_path}")

def save_to_blog(product: Dict, html_content: str, lang: str) -> str:
    """حفظ التقرير في ملف HTML باستخدام القالب"""
    if not TEMPLATE_FILE.exists():
        log.error("❌ blog_template.html not found!")
        return ""
        
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        template = f.read()
    
    name_ar = product.get("name", {}).get("ar", "")
    name_en = product.get("name", {}).get("en", "")
    date_str = datetime.now().strftime("%Y-%m-%d")
    slug = name_en.lower().replace(" ", "-")[:50]
    filename = f"{date_str}-{slug}.html"
    
    # استبدال المتغيرات في القالب
    final_html = template
    final_html = final_html.replace("{TITLE_AR}", name_ar if lang == "ar" else name_en)
    final_html = final_html.replace("{TITLE_EN}", name_en)
    final_html = final_html.replace("{DATE}", date_str)
    final_html = final_html.replace("{READ_TIME}", "5")
    final_html = final_html.replace("{CONTENT}", html_content)
    final_html = final_html.replace("{AFFILIATE_LINK}", product.get("affiliate_amazon", "#"))
    final_html = final_html.replace("{UPDATE_DATE}", date_str)
    final_html = final_html.replace("{META_DESCRIPTION}", f"تقرير شامل عن {name_ar}: السعر، المواصفات، المميزات والعيوب.")
    final_html = final_html.replace("{META_KEYWORDS}", f"{name_ar}, مراجعة, سعر, مميزات, عيوب")
    
    dest_dir = BLOG_DIR_AR if lang == "ar" else BLOG_DIR_EN
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = dest_dir / filename
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(final_html)
    
    return str(file_path)

if __name__ == "__main__":
    run_daily_update()
