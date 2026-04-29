#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO PULSE HUB — Scheduler Integration
يدمج جميع الأنظمة الآلية في جدول زمني موحد
"""

import os
import sys
import logging
from datetime import datetime, timedelta

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    import pytz
except ImportError:
    print("❌ apscheduler not installed. Run: pip install apscheduler")
    sys.exit(1)

# ─────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("scheduler.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("scheduler_integration")


# ─────────────────────────────────────────────────────────────
# Job Functions
# ─────────────────────────────────────────────────────────────

def job_fetch_amazon_products():
    """جلب منتجات من أمازون كل 6 ساعات"""
    try:
        log.info("🔍 Starting Amazon product fetch...")
        import amazon_ai_fetcher
        
        products = amazon_ai_fetcher.fetch_all_categories(products_per_category=2)
        log.info(f"✅ Fetched {len(products)} products from Amazon")
        
        # دمج مع products.json الموجود
        import json
        from pathlib import Path
        
        products_file = Path(__file__).parent / "products.json"
        existing_products = []
        
        if products_file.exists():
            with open(products_file, "r", encoding="utf-8") as f:
                existing_products = json.load(f)
        
        # إضافة المنتجات الجديدة في البداية
        all_products = products + existing_products
        
        # الحفاظ على أفضل 200 منتج
        all_products = all_products[:200]
        
        with open(products_file, "w", encoding="utf-8") as f:
            json.dump(all_products, f, ensure_ascii=False, indent=2)
        
        log.info(f"💾 Saved {len(all_products)} products to products.json")
        
    except Exception as e:
        log.error(f"❌ Error in job_fetch_amazon_products: {e}")


def job_publish_daily_article():
    """نشر مقالة مراجعة يومية"""
    try:
        log.info("📝 Starting daily article publication...")
        import content_automation_bot
        
        count = content_automation_bot.auto_publish_daily()
        log.info(f"✅ Published {count} articles")
        
    except Exception as e:
        log.error(f"❌ Error in job_publish_daily_article: {e}")


def job_publish_social_campaigns():
    """نشر حملات تسويقية على وسائل التواصل"""
    try:
        log.info("📢 Starting social media campaigns...")
        import social_media_automation
        
        results = social_media_automation.publish_daily_campaigns(count=3)
        log.info(f"✅ Published {len(results)} campaigns")
        
    except Exception as e:
        log.error(f"❌ Error in job_publish_social_campaigns: {e}")


def job_generate_buying_guides():
    """توليد أدلة شراء شاملة"""
    try:
        log.info("📚 Starting buying guides generation...")
        import content_automation_bot
        import json
        from pathlib import Path
        
        products_file = Path(__file__).parent / "products.json"
        if not products_file.exists():
            log.warning("⚠️ products.json not found")
            return
        
        with open(products_file, "r", encoding="utf-8") as f:
            products = json.load(f)
        
        # تجميع المنتجات حسب الفئة
        categories = {}
        for product in products:
            cat = product.get("category", "")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(product)
        
        # توليد دليل لكل فئة
        for category, cat_products in categories.items():
            if cat_products:
                content_automation_bot.publish_category_guide(category, cat_products)
        
        log.info(f"✅ Generated guides for {len(categories)} categories")
        
    except Exception as e:
        log.error(f"❌ Error in job_generate_buying_guides: {e}")


def job_cleanup_old_data():
    """تنظيف البيانات القديمة"""
    try:
        log.info("🧹 Starting cleanup job...")
        import json
        from pathlib import Path
        
        # تنظيف ملف السجلات
        log_file = Path(__file__).parent / "campaigns_log.json"
        if log_file.exists():
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # الاحتفاظ بآخر 1000 سطر فقط
            if len(lines) > 1000:
                with open(log_file, "w", encoding="utf-8") as f:
                    f.writelines(lines[-1000:])
                log.info("✅ Cleaned up campaigns_log.json")
        
    except Exception as e:
        log.error(f"❌ Error in job_cleanup_old_data: {e}")


# ─────────────────────────────────────────────────────────────
# Scheduler Setup
# ─────────────────────────────────────────────────────────────

def setup_scheduler():
    """إعداد جدول المهام"""
    
    tz = pytz.UTC
    scheduler = BackgroundScheduler(timezone=tz)
    
    log.info("⚙️ Setting up scheduler...")
    
    # 1. جلب منتجات من أمازون كل 6 ساعات (00:00, 06:00, 12:00, 18:00 UTC)
    scheduler.add_job(
        job_fetch_amazon_products,
        CronTrigger(hour="0,6,12,18", minute=0, timezone=tz),
        id="fetch_amazon_products",
        name="Fetch Amazon Products",
        misfire_grace_time=3600
    )
    log.info("✅ Added job: Fetch Amazon Products (every 6 hours)")
    
    # 2. نشر مقالة يومية في الساعة 10 صباحاً UTC
    scheduler.add_job(
        job_publish_daily_article,
        CronTrigger(hour=10, minute=0, timezone=tz),
        id="publish_daily_article",
        name="Publish Daily Article",
        misfire_grace_time=3600
    )
    log.info("✅ Added job: Publish Daily Article (10:00 UTC)")
    
    # 3. نشر حملات تسويقية 3 مرات يومياً (08:00, 14:00, 20:00 UTC)
    scheduler.add_job(
        job_publish_social_campaigns,
        CronTrigger(hour="8,14,20", minute=0, timezone=tz),
        id="publish_social_campaigns",
        name="Publish Social Campaigns",
        misfire_grace_time=3600
    )
    log.info("✅ Added job: Publish Social Campaigns (3x daily)")
    
    # 4. توليد أدلة شراء أسبوعياً (كل يوم الاثنين في الساعة 02:00 UTC)
    scheduler.add_job(
        job_generate_buying_guides,
        CronTrigger(day_of_week=0, hour=2, minute=0, timezone=tz),
        id="generate_buying_guides",
        name="Generate Buying Guides",
        misfire_grace_time=3600
    )
    log.info("✅ Added job: Generate Buying Guides (weekly)")
    
    # 5. تنظيف البيانات القديمة يومياً (في الساعة 03:00 UTC)
    scheduler.add_job(
        job_cleanup_old_data,
        CronTrigger(hour=3, minute=0, timezone=tz),
        id="cleanup_old_data",
        name="Cleanup Old Data",
        misfire_grace_time=3600
    )
    log.info("✅ Added job: Cleanup Old Data (daily)")
    
    # تشغيل المجدول
    try:
        scheduler.start()
        log.info("🚀 Scheduler started successfully!")
        return scheduler
    except Exception as e:
        log.error(f"❌ Error starting scheduler: {e}")
        return None


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    log.info("=" * 60)
    log.info("NEO PULSE HUB — Scheduler Integration")
    log.info("=" * 60)
    
    scheduler = setup_scheduler()
    
    if scheduler:
        try:
            log.info("📋 Scheduled jobs:")
            for job in scheduler.get_jobs():
                log.info(f"  - {job.name} ({job.id})")
            
            log.info("\n⏳ Scheduler is running. Press Ctrl+C to stop.")
            
            # Keep the scheduler running
            import time
            while True:
                time.sleep(1)
        
        except KeyboardInterrupt:
            log.info("\n⏹️ Scheduler stopped by user")
            scheduler.shutdown()
    else:
        log.error("❌ Failed to start scheduler")
        sys.exit(1)
