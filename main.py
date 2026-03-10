#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO PULSE HUB — Main Entry Point
نظام Webhook بدل Polling — لا تعارض أبداً
"""
import sys, os, logging, threading, time, requests

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
log = logging.getLogger("launcher")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bots'))

# ── Config ────────────────────────────────────────────────────────
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL", "https://neo-pulse-hub.onrender.com")

TOKENS = {
    "customer":       os.environ.get("CUSTOMER_BOT_TOKEN", ""),
    "admin":          os.environ.get("ADMIN_BOT_TOKEN", ""),
    "supplier":       os.environ.get("SUPPLIER_BOT_TOKEN", ""),
    "recommendation": os.environ.get("RECO_BOT_TOKEN", ""),
}

# ══════════════════════════════════════════════════════════════════
# STEP 1 — سجّل Webhooks على Telegram
# ══════════════════════════════════════════════════════════════════

def register_webhooks():
    """يحذف polling القديم ويسجل webhook جديد لكل بوت"""
    time.sleep(5)  # انتظر Flask يبدأ أولاً
    routes = {
        "customer":       "/webhook/customer",
        "admin":          "/webhook/admin",
        "supplier":       "/webhook/supplier",
        "recommendation": "/webhook/recommendation",
    }
    for name, token in TOKENS.items():
        if not token:
            log.warning(f"⚠️ {name}: no token")
            continue
        url = f"{RENDER_URL}{routes[name]}"
        try:
            # احذف webhook/polling القديم
            requests.post(
                f"https://api.telegram.org/bot{token}/deleteWebhook",
                json={"drop_pending_updates": True}, timeout=10
            )
            time.sleep(1)
            # سجّل webhook جديد
            r = requests.post(
                f"https://api.telegram.org/bot{token}/setWebhook",
                json={"url": url, "drop_pending_updates": True},
                timeout=10
            )
            result = r.json()
            if result.get("ok"):
                log.info(f"✅ Webhook set: {name} → {url}")
            else:
                log.error(f"❌ Webhook failed {name}: {result}")
        except Exception as e:
            log.error(f"❌ register_webhooks {name}: {e}")


# ══════════════════════════════════════════════════════════════════
# STEP 2 — Auto-Populate Scheduler
# ══════════════════════════════════════════════════════════════════

def start_scheduler():
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
        import pytz, smart_supplier_bot as ssb

        def daily_job():
            log.info("⏰ Daily auto-populate...")
            try:
                added = ssb.auto_add_products(count=5)
                log.info(f"✅ Added {len(added)} products")
                admin_id = int(os.environ.get("ADMIN_USER_ID", "0"))
                tok = os.environ.get("SUPPLIER_BOT_TOKEN", "")
                if admin_id and added and tok:
                    names = "\n".join([f"• {p['name_ar']}" for p in added])
                    ssb.send(admin_id,
                        f"🤖 *تقرير يومي*\n\nأُضيف {len(added)} منتجات:\n{names}",
                        token=tok)
            except Exception as e:
                log.error(f"daily_job error: {e}")

        s = BackgroundScheduler(timezone=pytz.UTC)
        s.add_job(daily_job, CronTrigger(hour=3, minute=0), id="daily", replace_existing=True)
        s.add_job(daily_job, "date", id="startup")
        s.start()
        log.info("✅ Scheduler started")
    except Exception as e:
        log.error(f"Scheduler error: {e}")


# ══════════════════════════════════════════════════════════════════
# STEP 3 — Flask app يستقبل Webhooks + API
# ══════════════════════════════════════════════════════════════════

def build_flask_app():
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    import json as _json

    app = Flask(__name__)
    CORS(app, origins=["https://neo-pulse-hub.it.com", "https://www.neo-pulse-hub.it.com",
                        "http://localhost:*", "http://127.0.0.1:*"])

    # ── lazy-load بوتات Telegram (Application objects) ──────────
    _bots = {}

    def get_bot(name):
        if name in _bots:
            return _bots[name]
        token = TOKENS.get(name, "")
        if not token:
            return None
        try:
            from telegram import Bot
            _bots[name] = Bot(token=token)
            return _bots[name]
        except Exception as e:
            log.error(f"get_bot {name}: {e}")
            return None

    # ── استيراد معالجات الرسائل من كل بوت ───────────────────────
    try:
        import customer_bot as cb_module
        import admin_bot as ab_module
        import supplier_bot as sb_module
        import recommendation_bot as rb_module
        log.info("✅ All bot modules imported")
    except Exception as e:
        log.error(f"❌ Bot import error: {e}")
        cb_module = ab_module = sb_module = rb_module = None

    # ── helper: process update through python-telegram-bot ───────
    import asyncio

    def process_update(module, token, update_data):
        """يعالج update واحد بشكل sync"""
        try:
            from telegram import Update
            from telegram.ext import Application
            import asyncio

            async def _run():
                app_tg = (
                    Application.builder()
                    .token(token)
                    .updater(None)   # ← بدون updater = بدون polling
                    .build()
                )
                # أضف الـ handlers من الـ module
                module._register_handlers(app_tg)
                await app_tg.initialize()
                update = Update.de_json(update_data, app_tg.bot)
                await app_tg.process_update(update)
                await app_tg.shutdown()

            asyncio.run(_run())
        except Exception as e:
            log.error(f"process_update error: {e}")

    # ════════════════════════════════════════════════════════════
    # Webhook routes
    # ════════════════════════════════════════════════════════════

    @app.route("/webhook/customer", methods=["POST"])
    def wh_customer():
        if cb_module:
            threading.Thread(
                target=process_update,
                args=(cb_module, TOKENS["customer"], request.json),
                daemon=True
            ).start()
        return jsonify({"ok": True})

    @app.route("/webhook/admin", methods=["POST"])
    def wh_admin():
        if ab_module:
            threading.Thread(
                target=process_update,
                args=(ab_module, TOKENS["admin"], request.json),
                daemon=True
            ).start()
        return jsonify({"ok": True})

    @app.route("/webhook/supplier", methods=["POST"])
    def wh_supplier():
        if sb_module:
            threading.Thread(
                target=process_update,
                args=(sb_module, TOKENS["supplier"], request.json),
                daemon=True
            ).start()
        return jsonify({"ok": True})

    @app.route("/webhook/recommendation", methods=["POST"])
    def wh_reco():
        if rb_module:
            threading.Thread(
                target=process_update,
                args=(rb_module, TOKENS["recommendation"], request.json),
                daemon=True
            ).start()
        return jsonify({"ok": True})

    # ── Health check ─────────────────────────────────────────────
    @app.route("/", methods=["GET"])
    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "ok",
            "service": "NEO PULSE HUB",
            "mode": "webhook",
            "bots": list(TOKENS.keys())
        })

    # ── إعادة توجيه باقي API endpoints من webhook_server ─────────
    try:
        import webhook_server as ws
        # أضف كل routes من webhook_server لنفس app
        for rule in ws.app.url_map.iter_rules():
            endpoint = ws.app.view_functions[rule.endpoint]
            if rule.rule not in [r.rule for r in app.url_map.iter_rules()]:
                app.add_url_rule(rule.rule, rule.endpoint + "_ws",
                                  endpoint, methods=rule.methods)
        log.info("✅ API routes merged from webhook_server")
    except Exception as e:
        log.warning(f"webhook_server merge: {e}")

    return app


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    log.info("🚀 NEO PULSE HUB — Webhook Mode Starting...")

    PORT = int(os.environ.get("PORT", 10000))

    # Scheduler في background
    start_scheduler()

    # سجّل webhooks بعد 5 ثواني (في background)
    threading.Thread(target=register_webhooks, daemon=True).start()

    # ابن Flask app
    flask_app = build_flask_app()

    log.info(f"🌐 Flask starting on 0.0.0.0:{PORT}")
    flask_app.run(host="0.0.0.0", port=PORT, debug=False, threaded=True)
