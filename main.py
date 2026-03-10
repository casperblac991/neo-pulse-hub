import sys
import os
import logging
import threading
import time
import requests

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
log = logging.getLogger("launcher")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bots'))


# ══════════════════════════════════════════════════════════
# KILL OLD SESSIONS — يوقف أي polling قديم قبل البدء
# ══════════════════════════════════════════════════════════

def kill_old_sessions():
    """يحذف كل webhooks قديمة ويمسح updates معلقة لكل البوتات"""
    tokens = {
        "CUSTOMER_BOT_TOKEN":    os.environ.get("CUSTOMER_BOT_TOKEN", ""),
        "ADMIN_BOT_TOKEN":       os.environ.get("ADMIN_BOT_TOKEN", ""),
        "SUPPLIER_BOT_TOKEN":    os.environ.get("SUPPLIER_BOT_TOKEN", ""),
        "RECO_BOT_TOKEN":        os.environ.get("RECO_BOT_TOKEN", ""),
    }
    for name, token in tokens.items():
        if not token:
            continue
        try:
            r = requests.post(
                f"https://api.telegram.org/bot{token}/deleteWebhook",
                json={"drop_pending_updates": True},
                timeout=10
            )
            status = r.json().get("result", False)
            log.info(f"deleteWebhook {name}: {'✅' if status else '⚠️'} {r.json()}")
        except Exception as e:
            log.warning(f"deleteWebhook {name} error: {e}")
    # انتظر 3 ثواني بعد الحذف
    time.sleep(3)
    log.info("✅ Old sessions cleared")


# ══════════════════════════════════════════════════════════
# AUTO-POPULATE SCHEDULER
# ══════════════════════════════════════════════════════════

def start_auto_populate_scheduler():
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
        import pytz
        import smart_supplier_bot as ssb

        def daily_auto_populate():
            log.info("⏰ Daily auto-populate started...")
            try:
                added = ssb.auto_add_products(count=5)
                log.info(f"✅ Auto-populate: added {len(added)} products")
                admin_id = int(os.environ.get("ADMIN_USER_ID", "0"))
                if admin_id and added:
                    names = "\n".join([f"• {p['name_ar']}" for p in added])
                    ssb.send(
                        admin_id,
                        f"🤖 *تقرير يومي — Auto Bot*\n\n"
                        f"تمت إضافة {len(added)} منتجات:\n{names}\n\n"
                        f"🌐 https://neo-pulse-hub.it.com/products.html",
                        token=os.environ.get("SUPPLIER_BOT_TOKEN", "")
                    )
            except Exception as e:
                log.error(f"daily_auto_populate error: {e}")

        scheduler = BackgroundScheduler(timezone=pytz.UTC)
        scheduler.add_job(
            daily_auto_populate,
            CronTrigger(hour=3, minute=0),
            id="daily_populate", replace_existing=True
        )
        scheduler.add_job(
            daily_auto_populate,
            "date",
            id="startup_populate"
        )
        scheduler.start()
        log.info("✅ Scheduler started — daily 03:00 UTC + immediate startup run")
        return scheduler
    except Exception as e:
        log.error(f"Scheduler error: {e}")
        return None


# ══════════════════════════════════════════════════════════
# BOT RUNNERS
# ══════════════════════════════════════════════════════════

def run_admin():
    time.sleep(1)
    try:
        import admin_bot as ab
        log.info("Starting Admin Bot...")
        ab.main()
    except Exception as e:
        log.error("Admin error: " + str(e))

def run_recommendation():
    time.sleep(2)
    try:
        import recommendation_bot as rb
        log.info("Starting Recommendation Bot...")
        rb.main()
    except Exception as e:
        log.error("Recommendation error: " + str(e))

def run_supplier():
    time.sleep(3)
    try:
        import supplier_bot as sb
        log.info("Starting Supplier Bot...")
        sb.main()
    except Exception as e:
        log.error("Supplier error: " + str(e))

def run_webhook():
    time.sleep(1)
    try:
        import webhook_server as ws
        log.info("Starting Webhook/Flask Server...")
        ws.main()
    except Exception as e:
        log.error("Webhook error: " + str(e))


# ══════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════

if __name__ == "__main__":
    log.info("🚀 NEO PULSE HUB Starting...")

    # أولاً: امسح كل sessions قديمة
    kill_old_sessions()

    # ثانياً: بدء scheduler التلقائي
    start_auto_populate_scheduler()

    # ثالثاً: شغّل البوتات في خيوط منفصلة
    threads = [
        threading.Thread(target=run_admin,          name="Admin",    daemon=True),
        threading.Thread(target=run_recommendation, name="Reco",     daemon=True),
        threading.Thread(target=run_supplier,       name="Supplier", daemon=True),
        threading.Thread(target=run_webhook,        name="Webhook",  daemon=True),
    ]
    for t in threads:
        t.start()
        log.info("Started thread: " + t.name)

    # رابعاً: Customer bot في الخيط الرئيسي
    time.sleep(4)
    try:
        import customer_bot as cb
        log.info("Starting Customer Bot in main thread...")
        cb.main()
    except Exception as e:
        log.error("Customer error: " + str(e))
