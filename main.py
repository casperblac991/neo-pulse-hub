#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════╗
║   NEO PULSE HUB - Bot Launcher (Webhook Only)                  ║
║   يشغل جميع البوتات مع تعطيل Polling نهائياً                   ║
╚══════════════════════════════════════════════════════════════════╝
"""

# Force disable polling completely
import os
os.environ['PYTHON_TELEGRAM_BOT_POLLING'] = 'false'
os.environ['PTB_POLLING'] = 'false'

import sys
import time
import logging
import asyncio
import threading
from datetime import datetime

from dotenv import load_dotenv

# تحميل المتغيرات البيئية
load_dotenv()

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot_launcher.log', encoding='utf-8')
    ]
)
logger = logging.getLogger("launcher")

# إضافة مسار المجلد الحالي للمكتبات
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ══════════════════════════════════════════════════════════════════
# استيراد البوتات
# ══════════════════════════════════════════════════════════════════

try:
    import customer_bot
    import admin_bot
    import recommendation_bot
    import supplier_bot
    import webhook_server
    logger.info("✅ تم استيراد جميع البوتات بنجاح")
except ImportError as e:
    logger.error(f"❌ فشل استيراد بوت: {e}")
    sys.exit(1)

# ══════════════════════════════════════════════════════════════════
# التحقق من المتغيرات البيئية
# ══════════════════════════════════════════════════════════════════

def check_environment():
    """التحقق من وجود المتغيرات البيئية الأساسية"""
    token = os.environ.get('TELEGRAM_TOKEN')
    if not token:
        logger.error("❌ TELEGRAM_TOKEN غير موجود في المتغيرات البيئية!")
        return False
    
    # التحقق من طول التوكن (تقريبي)
    if len(token) < 40:
        logger.error(f"❌ TELEGRAM_TOKEN يبدو غير صحيح (طوله {len(token)})")
        return False
    
    logger.info(f"✅ TELEGRAM_TOKEN موجود (آخر 4 أحرف: ...{token[-4:]})")
    return True

# ══════════════════════════════════════════════════════════════════
# دوال تشغيل البوتات (مع Webhook فقط)
# ══════════════════════════════════════════════════════════════════

def run_webhook():
    """تشغيل خادم API (الطريقة الوحيدة المسموح بها)"""
    try:
        logger.info("🌐 بدء تشغيل Webhook Server...")
        port = int(os.environ.get('PORT', 10000))
        logger.info(f"📡 Webhook listening on port {port}")
        
        # تشغيل Flask
        webhook_server.app.run(
            host='0.0.0.0',
            port=port,
            threaded=True
        )
    except Exception as e:
        logger.error(f"💥 Webhook error: {e}")

# ══════════════════════════════════════════════════════════════════
# الدالة الرئيسية
# ══════════════════════════════════════════════════════════════════

def main():
    """تشغيل Webhook Server فقط"""
    
    logger.info("=" * 60)
    logger.info("🤖 NEO PULSE HUB - Bot Launcher (Webhook Only)")
    logger.info(f"📅 تاريخ التشغيل: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    # التحقق من المتغيرات البيئية
    if not check_environment():
        logger.error("❌ فشل التحقق من المتغيرات البيئية. إيقاف التشغيل.")
        sys.exit(1)
    
    # تحذير مهم
    logger.info("⚠️ تم تعطيل Polling نهائياً. استخدام Webhook فقط.")
    
    # تشغيل Webhook Server فقط (بدون أي بوتات Polling)
    try:
        run_webhook()
    except KeyboardInterrupt:
        logger.info("👋 إيقاف الخادم...")
    except Exception as e:
        logger.error(f"💥 خطأ غير متوقع: {e}")
    finally:
        logger.info("🏁 تم إنهاء التشغيل")

if __name__ == "__main__":
    main()
