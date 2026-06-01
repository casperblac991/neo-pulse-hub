#!/usr/bin/env python3
"""
NEO PULSE HUB - Script to install all improvements
==================================================
This script updates index.html and products.html with all improvements
"""

import json
import re
import os

def install_improvements():
    print("🚀 بدء تثبيت التحسينات...")
    
    # 1. تحديث index.html
    print("📝 تحديث index.html...")
    update_index_html()
    
    # 2. تحديث products.html
    print("📝 تحديث products.html...")
    update_products_html()
    
    print("✅ تم تثبيت جميع التحسينات بنجاح!")
    print("\n📋 الخطوات التالية:")
    print("1. افتح index.html وقم بمراجعة التغييرات")
    print("2. اختبر Countdown timer و Badges")
    print("3. أضف صفحة best-smartwatches-guide.html للموقع")
    print("4. ادفع التغييرات على GitHub")

def update_index_html():
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # إضافة تحسينات Badges
    if 'badges-system.js' not in content:
        # إضافة Script قبل </body>
        scripts_to_add = '''
    <!-- NEO PULSE HUB Improvements -->
    <script src="improvements/badges-system.js"></script>
    <script src="improvements/countdown-timer.js"></script>
    <script src="improvements/social-proof.js"></script>
    <script src="improvements/email-capture.js"></script>
    <script src="improvements/integrate-improvements.js"></script>
'''
        content = content.replace('</body>', scripts_to_add + '</body>')
    
    # تحديث Meta tags للـ SEO
    if 'أفضل ساعات ذكية 2026' not in content:
        content = content.replace(
            '<meta name="description" id="metaDescription"',
            '<meta name="description" id="metaDescription" content="متجر NEO PULSE HUB - أفضل ساعات ذكية، سماعات، منتجات تقنية بأسعار منافسة. أكثر من 682 منتج مع تقييمات ومراجعات. تسوق من أمازون بأفضل الأسعار."'
        )
    
    # تحديث Statistics
    content = re.sub(
        r'>\d+\+\s*منتج ذكي<',
        '>682+ منتج ذكي<',
        content
    )
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("  ✅ index.html تم تحديثه")

def update_products_html():
    with open('products.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # إضافة Script قبل </body>
    if 'badges-system.js' not in content:
        scripts_to_add = '''
    <!-- NEO PULSE HUB Improvements -->
    <script src="improvements/badges-system.js"></script>
    <script src="improvements/countdown-timer.js"></script>
    <script src="improvements/social-proof.js"></script>
    <script src="improvements/email-capture.js"></script>
    <script src="improvements/integrate-improvements.js"></script>
'''
        content = content.replace('</body>', scripts_to_add + '</body>')
    
    # تحديث Meta tags
    if '682 منتج' not in content:
        content = re.sub(
            r'content="تسوق أحدث منتجات.*?>',
            'content="تسوق 682+ منتج من أفضل الساعات الذكية والسماعات. مقارنة أسعار، تقييمات، ومراجعات. خصومات حتى 50%. تسوق من أمازون الآن!"',
            content
        )
    
    with open('products.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("  ✅ products.html تم تحديثه")

if __name__ == "__main__":
    install_improvements()