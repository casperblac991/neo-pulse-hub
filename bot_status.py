#!/usr/bin/env python3
"""
NEO PULSE HUB - Bot Status Checker
فحص حالة البوت والمتطلبات
"""

import os
import sys

def check_dependencies():
    """فحص المكتبات المطلوبة"""
    print("🔍 فحص المكتبات...")
    
    deps = {
        'telegram': 'python-telegram-bot',
        'telegram.ext': 'python-telegram-bot',
        'requests': 'requests',
        'dotenv': 'python-dotenv',
    }
    
    missing = []
    for mod, pkg in deps.items():
        try:
            __import__(mod)
            print(f"  ✅ {pkg}")
        except ImportError:
            print(f"  ❌ {pkg} - غير مثبت")
            missing.append(pkg)
    
    return len(missing) == 0

def check_env_vars():
    """فحص متغيرات البيئة"""
    print("\n🔧 فحص متغيرات البيئة...")
    
    token = os.environ.get('CUSTOMER_BOT_TOKEN', '')
    gemini = os.environ.get('GEMINI_API_KEY', '')
    
    if token:
        print(f"  ✅ CUSTOMER_BOT_TOKEN: {token[:10]}...")
    else:
        print("  ⚠️ CUSTOMER_BOT_TOKEN: غير موجود")
        print("     → انسخ .env.example إلى .env وأضف التوكن")
    
    if gemini:
        print(f"  ✅ GEMINI_API_KEY: موجود")
    else:
        print("  ⚠️ GEMINI_API_KEY: غير موجود")
        print("     → احصل على مفتاح من Google AI Studio")

def check_files():
    """فحص الملفات المطلوبة"""
    print("\n📁 فحص الملفات...")
    
    files = {
        'products.json': 'قاعدة بيانات المنتجات',
        'leads.json': 'ملف تتبع العملاء',
        'customer_bot.py': 'بوت خدمة العملاء',
    }
    
    for file, desc in files.items():
        if os.path.exists(file):
            print(f"  ✅ {file} - {desc}")
        else:
            print(f"  ❌ {file} - مفقود!")

def show_start_instructions():
    """عرض تعليمات التشغيل"""
    print("\n" + "="*50)
    print("🚀 لتشغيل البوت:")
    print("="*50)
    print()
    print("1. أنشئ ملف .env من .env.example:")
    print("   cp .env.example .env")
    print()
    print("2. أضف التوكن في .env:")
    print("   CUSTOMER_BOT_TOKEN=...")
    print("   GEMINI_API_KEY=...")
    print()
    print("3. شغل البوت:")
    print("   python3 customer_bot.py")
    print()
    print("="*50)

if __name__ == "__main__":
    print("="*50)
    print("🤖 NEO PULSE HUB - فحص حالة البوت")
    print("="*50)
    
    deps_ok = check_dependencies()
    check_env_vars()
    check_files()
    show_start_instructions()
    
    if not deps_ok:
        print("\n⚠️ يجب تثبيت المكتبات المفقودة:")
        print("   pip install python-telegram-bot requests python-dotenv")