#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════╗
║   NEO PULSE HUB - Bot Launcher (All Bots)                      ║
║   يشغل جميع البوتات الأربعة معاً                               ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import logging
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
# استيراد جميع البوتات
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
    """التحقق من وجود جميع التوكنات"""
    tokens = {
        'TELEGRAM_TOKEN': os.environ.get('TELEGRAM_TOKEN'),
        'ADMIN_BOT_TOKEN': os.environ.get('ADMIN_BOT_TOKEN'),
        'RECOMMEND_BOT_TOKEN': os.environ.get('RECOMMEND_BOT_TOKEN'),
        'SUPPLIER_BOT_TOKEN': os.environ.get('SUPPLIER_BOT_TOKEN'),
    }
    
    all_ok = True
    for name, token in tokens.items():
        if not token:
            logger.error(f"❌ {name} غير موجود في المتغيرات البيئية!")
            all_ok = False
        else:
            logger.info(f"✅ {name} موجود (آخر 4 أحرف: ...{token[-4:]})")
    
    return all_ok

# ══════════════════════════════════════════════════════════════════
# دوال تشغيل البوتات
# ══════════════════════════════════════════════════════════════════

def run_bot(bot_name, bot_module, token_env):
    """تشغيل بوت معين مع التوكن الخاص به"""
    try:
        logger.info(f"🚀 بدء تشغيل {bot_name}...")
        
        # تعيين التوكن المناسب للبوت
        token = os.environ.get(token_env)
        if not token:
            logger.error(f"❌ {token_env} غير موجود!")
            return
        
        os.environ['TELEGRAM_TOKEN'] = token
        
        if hasattr(bot_module, 'main'):
            bot_module.main()
        else:
            logger.error(f"❌ {bot_name} لا يحتوي على دالة main()")
    except Exception as e:
        logger.error(f"💥 {bot_name} error: {e}")

def run_webhook():
    """تشغيل خادم API"""
    try:
        logger.info("🌐 بدء تشغيل Webhook Server...")
        port = int(os.environ.get('PORT', 10000))
        logger.info(f"📡 Webhook listening on port {port}")
        
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
    """تشغيل جميع البوتات"""
    
    logger.info("=" * 60)
    logger.info("🤖 NEO PULSE HUB - All Bots Launcher")
    logger.info(f"📅 تاريخ التشغيل: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    # التحقق من المتغيرات البيئية
    if not check_environment():
        logger.error("❌ فشل التحقق من المتغيرات البيئية. إيقاف التشغيل.")
        sys.exit(1)
    
    # قائمة البوتات
    bots = [
        ("Webhook", run_webhook, None, None),
        ("Customer", run_bot, customer_bot, 'TELEGRAM_TOKEN'),
        ("Admin", run_bot, admin_bot, 'ADMIN_BOT_TOKEN'),
        ("Recommendation", run_bot, recommendation_bot, 'RECOMMEND_BOT_TOKEN'),
        ("Supplier", run_bot, supplier_bot, 'SUPPLIER_BOT_TOKEN'),
    ]
    
    # تشغيل كل بوت في Thread منفصل
    threads = []
    
    for name, func, module, token_env in bots:
        try:
            if module:
                thread = threading.Thread(
                    target=func,
                    args=(name, module, token_env),
                    name=name,
                    daemon=True
                )
            else:
                thread = threading.Thread(
                    target=func,
                    name=name,
                    daemon=True
                )
            
            thread.start()
            threads.append(thread)
            logger.info(f"✅ {name} thread started successfully")
            time.sleep(2)  # مهلة بين البوتات
        except Exception as e:
            logger.error(f"❌ فشل تشغيل {name}: {e}")
    
    logger.info("🎉 جميع البوتات تعمل بنجاح!")
    logger.info("=" * 60)
    
    # مراقبة البوتات
    try:
        while True:
            time.sleep(60)
            alive = sum(1 for t in threads if t.is_alive())
            logger.info(f"📊 حالة البوتات: {alive}/{len(threads)} تعمل")
    except KeyboardInterrupt:
        logger.info("👋 إيقاف البوتات...")
    except Exception as e:
        logger.error(f"💥 خطأ غير متوقع: {e}")

if __name__ == "__main__":
    main()
