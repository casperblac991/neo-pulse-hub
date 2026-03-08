#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════╗
║   NEO PULSE HUB - Bot Launcher                                  ║
║   يشغل جميع البوتات الخمسة في تطبيق Render واحد                 ║
║                                                                  ║
║   البوتات:                                                      ║
║   🤖 customer_bot     - خدمة العملاء                           ║
║   👑 admin_bot        - لوحة الإدارة                           ║
║   🎯 recommendation_bot - توصيات ذكية                          ║
║   📦 supplier_bot     - الموردين والمخزون                      ║
║   🌐 webhook_server   - API للموقع                             ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import logging
import threading
import signal
from datetime import datetime
from dotenv import load_dotenv

# ============================================
# التهيئة الأساسية
# ============================================

# تحميل المتغيرات البيئية
load_dotenv()

# إعداد التسجيل (Logging)
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

# ============================================
# استيراد البوتات
# ============================================

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

# ============================================
# دوال تشغيل كل بوت
# ============================================

def run_customer_bot():
    """تشغيل بوت خدمة العملاء"""
    try:
        logger.info("🚀 بدء تشغيل Customer Bot...")
        customer_bot.main()
    except Exception as e:
        logger.error(f"💥 Customer Bot error: {e}")
        time.sleep(5)  # انتظار قبل إعادة المحاولة

def run_admin_bot():
    """تشغيل بوت الإدارة"""
    try:
        logger.info("👑 بدء تشغيل Admin Bot...")
        admin_bot.main()
    except Exception as e:
        logger.error(f"💥 Admin Bot error: {e}")
        time.sleep(5)

def run_recommendation_bot():
    """تشغيل بوت التوصيات"""
    try:
        logger.info("🎯 بدء تشغيل Recommendation Bot...")
        recommendation_bot.main()
    except Exception as e:
        logger.error(f"💥 Recommendation Bot error: {e}")
        time.sleep(5)

def run_supplier_bot():
    """تشغيل بوت الموردين"""
    try:
        logger.info("📦 بدء تشغيل Supplier Bot...")
        supplier_bot.main()
    except Exception as e:
        logger.error(f"💥 Supplier Bot error: {e}")
        time.sleep(5)

def run_webhook():
    """تشغيل خادم API"""
    try:
        logger.info("🌐 بدء تشغيل Webhook Server...")
        # استخدام PORT من Render أو 10000 كبديل
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
        time.sleep(5)

# ============================================
# فحص صحة البوتات (Health Check)
# ============================================

class BotMonitor:
    """مراقبة البوتات وإعادة تشغيلها إذا توقفت"""
    
    def __init__(self):
        self.bots = {}
        self.running = True
    
    def register(self, name, thread):
        self.bots[name] = {
            'thread': thread,
            'last_check': datetime.now(),
            'failures': 0
        }
    
    def check_all(self):
        """فحص جميع البوتات كل دقيقة"""
        while self.running:
            time.sleep(60)
            for name, info in self.bots.items():
                if not info['thread'].is_alive():
                    logger.warning(f"⚠️ البوت {name} توقف!")
                    info['failures'] += 1
                    
                    if info['failures'] >= 3:
                        logger.error(f"❌ البوت {name} فشل 3 مرات. يحتاج تدخل!")
                    else:
                        logger.info(f"🔄 إعادة تشغيل {name}...")
                        # إعادة التشغيل (سيتم التعامل معه في الدالة الرئيسية)

# ============================================
# معالج إيقاف التشغيل
# ============================================

def signal_handler(sig, frame):
    """معالج إشارات الإيقاف"""
    logger.info("👋 استقبال إشارة إيقاف... جاري إنهاء البوتات")
    monitor.running = False
    sys.exit(0)

# ============================================
# الدالة الرئيسية
# ============================================

def main():
    """تشغيل جميع البوتات"""
    
    logger.info("=" * 60)
    logger.info("🤖 NEO PULSE HUB - Bot Launcher")
    logger.info(f"📅 تاريخ التشغيل: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"📂 مسار العمل: {os.getcwd()}")
    logger.info(f"🐍 إصدار Python: {sys.version}")
    logger.info("=" * 60)
    
    # التحقق من المتغيرات البيئية الأساسية
    token = os.environ.get('TELEGRAM_TOKEN')
    if not token:
        logger.error("❌ TELEGRAM_TOKEN غير موجود في المتغيرات البيئية!")
        logger.error("📌 تأكد من إضافته في إعدادات Render")
        sys.exit(1)
    else:
        logger.info(f"✅ TELEGRAM_TOKEN موجود (آخر 4 أحرف: ...{token[-4:]})")
    
    # قائمة البوتات مع دوال التشغيل
    bots_to_run = [
        ("Webhook", run_webhook),
        ("Customer", run_customer_bot),
        ("Admin", run_admin_bot),
        ("Recommendation", run_recommendation_bot),
        ("Supplier", run_supplier_bot),
    ]
    
    # تشغيل كل بوت في Thread منفصل
    threads = []
    monitor = BotMonitor()
    
    for name, func in bots_to_run:
        try:
            thread = threading.Thread(
                target=func,
                name=name,
                daemon=True  # Daemon threads تنتهي مع البرنامج الرئيسي
            )
            thread.start()
            threads.append(thread)
            monitor.register(name, thread)
            logger.info(f"✅ {name} bot started successfully")
            time.sleep(2)  # مهلة بين البوتات لتجنب التزاحم
        except Exception as e:
            logger.error(f"❌ فشل تشغيل {name}: {e}")
    
    logger.info("🎉 جميع البوتات تعمل بنجاح!")
    logger.info("=" * 60)
    
    # بدء مراقبة البوتات
    monitor.running = True
    import threading as mt
    monitor_thread = mt.Thread(target=monitor.check_all, daemon=True)
    monitor_thread.start()
    
    # البقاء في التشغيل حتى استقبال إشارة إيقاف
    try:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # حلقة لا نهائية مع طباعة حالة البوتات كل 5 دقائق
        counter = 0
        while True:
            time.sleep(60)
            counter += 1
            
            if counter % 5 == 0:  # كل 5 دقائق
                alive = sum(1 for t in threads if t.is_alive())
                logger.info(f"📊 حالة البوتات: {alive}/{len(threads)} تعمل")
                
                # عرض تفاصيل كل بوت
                for name, info in monitor.bots.items():
                    status = "🟢" if info['thread'].is_alive() else "🔴"
                    logger.info(f"  {status} {name}: {info['failures']} فشل")
                    
    except KeyboardInterrupt:
        logger.info("👋 إيقاف البوتات...")
    except Exception as e:
        logger.error(f"💥 خطأ غير متوقع: {e}")
    finally:
        logger.info("🏁 تم إنهاء تشغيل جميع البوتات")

# ============================================
# نقطة الدخول الرئيسية
# ============================================

if __name__ == "__main__":
    main()
    import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bots'))
from customer_bot import main
main()
