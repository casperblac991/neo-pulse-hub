#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════╗
║   NEO PULSE HUB - Bot Launcher (Final Fix)                     ║
║   يشغل جميع البوتات مع Event Loop منفصل لكل بوت                ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import logging
import asyncio
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

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
# دالة تشغيل بوت مع Event Loop منفصل
# ══════════════════════════════════════════════════════════════════

def run_bot(bot_name, bot_module):
    """تشغيل بوت مع Event Loop خاص به"""
    try:
        logger.info(f"🚀 بدء تشغيل {bot_name}...")
        
        # إنشاء Event Loop جديد لهذا الـ thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # تشغيل البوت
        if hasattr(bot_module, 'main'):
            bot_module.main()
        else:
            logger.error(f"❌ {bot_name} لا يحتوي على دالة main()")
            
    except Exception as e:
        logger.error(f"💥 {bot_name} error: {e}")
        time.sleep(5)

def run_webhook():
    """تشغيل خادم API"""
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
    """تشغيل جميع البوتات"""
    
    logger.info("=" * 60)
    logger.info("🤖 NEO PULSE HUB - Bot Launcher (Final Fix)")
    logger.info(f"📅 تاريخ التشغيل: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    # التحقق من المتغيرات البيئية الأساسية
    token = os.environ.get('TELEGRAM_TOKEN')
    if not token:
        logger.error("❌ TELEGRAM_TOKEN غير موجود في المتغيرات البيئية!")
        sys.exit(1)
    else:
        logger.info(f"✅ TELEGRAM_TOKEN موجود (آخر 4 أحرف: ...{token[-4:]})")
    
    # قائمة البوتات
    bots = [
        ("Webhook", run_webhook, None),
        ("Customer", run_bot, customer_bot),
        ("Admin", run_bot, admin_bot),
        ("Recommendation", run_bot, recommendation_bot),
        ("Supplier", run_bot, supplier_bot),
    ]
    
    # تشغيل كل بوت في Thread منفصل
    threads = []
    for name, func, module in bots:
        try:
            if module:
                thread = threading.Thread(
                    target=func,
                    args=(name, module),
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
    
    # مراقبة البوتات وإعادة تشغيلها إذا توقفت
    failed_attempts = {}
    
    try:
        while True:
            time.sleep(30)  # فحص كل 30 ثانية
            
            for thread in threads:
                if not thread.is_alive():
                    name = thread.name
                    failed_attempts[name] = failed_attempts.get(name, 0) + 1
                    
                    if failed_attempts[name] >= 3:
                        logger.error(f"❌ البوت {name} فشل 3 مرات. يحتاج تدخل!")
                    else:
                        logger.warning(f"⚠️ البوت {name} توقف! إعادة تشغيل... (محاولة {failed_attempts[name]})")
                        
                        # إعادة تشغيل البوت
                        for n, func, module in bots:
                            if n == name:
                                try:
                                    if module:
                                        new_thread = threading.Thread(
                                            target=func,
                                            args=(name, module),
                                            name=name,
                                            daemon=True
                                        )
                                    else:
                                        new_thread = threading.Thread(
                                            target=func,
                                            name=name,
                                            daemon=True
                                        )
                                    new_thread.start()
                                    threads[threads.index(thread)] = new_thread
                                    logger.info(f"✅ {name} restarted successfully")
                                except Exception as e:
                                    logger.error(f"❌ فشل إعادة تشغيل {name}: {e}")
            
            # طباعة حالة البوتات كل دقيقتين
            alive = sum(1 for t in threads if t.is_alive())
            logger.info(f"📊 حالة البوتات: {alive}/{len(threads)} تعمل")
            
    except KeyboardInterrupt:
        logger.info("👋 إيقاف البوتات...")
    except Exception as e:
        logger.error(f"💥 خطأ غير متوقع: {e}")
    finally:
        logger.info("🏁 تم إنهاء تشغيل جميع البوتات")

if __name__ == "__main__":
    main()
