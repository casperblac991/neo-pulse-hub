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
        from apscheduler.triggers.interval import IntervalTrigger
        import pytz

        def refresh_job():
            """تجديد المتجر كل 6 ساعات — يحذف القديم ويضيف الجديد"""
            log.info("🔄 Auto store refresh starting...")
            try:
                import supplier_bot as sb
                result = sb.refresh_store(keep_per_cat=12, add_per_cat=3)
                log.info(f"✅ Refresh done: +{result['added']} -{result['deleted']}")
                sb.notify_admin_refresh(result)
            except Exception as e:
                log.error(f"refresh_job error: {e}")

        def startup_job():
            """عند الإقلاع — أضف منتجات إذا كان العدد قليلاً"""
            log.info("⚡ Startup check...")
            try:
                import supplier_bot as sb
                products = sb.load_products()
                if len(products) < 80:
                    log.info(f"Only {len(products)} products — adding more...")
                    added = sb.auto_add_products(count=6)
                    log.info(f"✅ Startup added {len(added)} products")
            except Exception as e:
                log.error(f"startup_job error: {e}")

        tz = pytz.UTC
        s = BackgroundScheduler(timezone=tz)

        # تشغيل فوري عند الإقلاع
        from datetime import datetime, timedelta
        start_time = datetime.now(tz) + timedelta(seconds=10)
        s.add_job(startup_job, "date", run_date=start_time, id="startup")

        # تجديد كل 6 ساعات: 00:00, 06:00, 12:00, 18:00 UTC
        s.add_job(refresh_job, CronTrigger(hour="0,6,12,18", minute=0, timezone=tz), id="refresh_6h")

        s.start()
        log.info("✅ Scheduler started — refresh every 6 hours")
    except Exception as e:
        log.error(f"start_scheduler: {e}")

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
    # ── /api/order — استقبال طلب جديد وإشعار الأدمين ─────────────
    @app.route("/api/order", methods=["POST"])
    def api_order():
        try:
            data = request.get_json(silent=True) or {}
            order_id   = data.get("order_id", "")
            product_id = data.get("product_id", "")
            product    = data.get("product", "غير محدد")
            qty        = data.get("qty", 1)
            total      = data.get("total", 0)
            lang       = data.get("lang", "ar")

            # حفظ في orders.json على GitHub عبر github_sync
            try:
                import json as _json2
                orders_path = os.path.join(os.path.dirname(__file__), "orders.json")
                with open(orders_path, "r", encoding="utf-8") as f:
                    orders_data = _json2.load(f)
                orders_data.setdefault("orders", [])
                orders_data.setdefault("total_revenue", 0)
                orders_data.setdefault("total_orders", 0)
                orders_data["orders"].insert(0, {
                    "id": order_id,
                    "product_id": product_id,
                    "product": product,
                    "qty": qty,
                    "total": total,
                    "status": "confirmed",
                    "date": __import__("datetime").datetime.utcnow().isoformat()
                })
                orders_data["total_orders"] += 1
                if total:
                    orders_data["total_revenue"] = round(orders_data["total_revenue"] + float(total), 2)
                with open(orders_path, "w", encoding="utf-8") as f:
                    _json2.dump(orders_data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                log.error(f"orders.json save error: {e}")

            # إشعار تيليجرام للأدمين
            admin_token = TOKENS.get("admin", "") or os.environ.get("ADMIN_BOT_TOKEN", "")
            admin_id    = os.environ.get("ADMIN_USER_ID", "6790340715")
            if admin_token and admin_id:
                try:
                    msg = (
                        f"🛒 *طلب جديد!*\n\n"
                        f"📦 المنتج: {product}\n"
                        f"🆔 رقم المنتج: {product_id}\n"
                        f"🔢 الكمية: {qty}\n"
                        f"💰 المبلغ: ${total}\n"
                        f"🏷️ رقم الطلب: {order_id}\n"
                        f"🌐 اللغة: {lang}"
                    )
                    requests.post(
                        f"https://api.telegram.org/bot{admin_token}/sendMessage",
                        json={"chat_id": admin_id, "text": msg, "parse_mode": "Markdown"},
                        timeout=8
                    )
                except Exception as e:
                    log.error(f"Telegram notify error: {e}")

            return jsonify({"ok": True, "order_id": order_id})
        except Exception as e:
            log.error(f"api_order error: {e}")
            return jsonify({"ok": False, "error": str(e)}), 500

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

    @app.route("/test-gemini")
    def test_gemini():
        import requests as _r
        key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
        if not key:
            return {"error": "NO GEMINI KEY"}, 400
        # اختبر كل الموديلات
        models = [
            "gemini-2.5-flash",
            "gemini-2.5-flash-preview-04-17",
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-1.5-flash-latest",
            "gemini-1.5-flash-8b",
        ]
        results = {}
        for model in models:
            try:
                url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
                       f"{model}:generateContent?key={key}")
                r = _r.post(url,
                    json={"contents":[{"parts":[{"text":"say hi"}]}],
                          "generationConfig":{"maxOutputTokens":20,"thinkingConfig":{"thinkingBudget":0}}},
                    timeout=8)
                if r.status_code == 200:
                    data = r.json()
                    parts = (data.get("candidates",[{}])[0]
                                 .get("content",{}).get("parts",[{}]))
                    text = parts[0].get("text","(empty parts)") if parts else "(no parts)"
                    results[model] = "✅ " + text[:50]
                else:
                    results[model] = f"❌ {r.status_code}"
            except Exception as e:
                results[model] = f"❌ {str(e)[:50]}"
        return {"key_prefix": key[:8]+"...", "models": results}

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
