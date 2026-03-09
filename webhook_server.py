#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO PULSE HUB — Webhook Server (Multi-Bot)
مسار منفصل لكل بوت مع ردود كاملة
"""

import os, sys, json, logging, requests
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, abort
from flask_cors import CORS

try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from shared_db import (
        get_products, get_product, search_products, get_products_by_category,
        get_featured_products, create_order, upsert_user, subscribe_email,
        add_review, get_product_reviews, track_event, track_product_view,
        get_analytics_summary, get_orders_by_user, get_low_stock,
        get_out_of_stock, update_product, init_db
    )
    from ai_engine import (
        answer_customer, recommend_products, extract_budget,
        continue_conversation, generate_store_report
    )
    DB_OK = True
except ImportError as e:
    print("Warning: " + str(e))
    DB_OK = False
    def get_products(): return []
    def get_product(p): return None
    def search_products(q): return []
    def get_products_by_category(c): return []
    def get_featured_products(n): return []
    def create_order(*a, **k): return {"id":"X","total":0}
    def upsert_user(*a, **k): return {"id":0}
    def subscribe_email(e): return True
    def add_review(*a, **k): return {}
    def get_product_reviews(p): return []
    def track_event(e,d): pass
    def track_product_view(p): pass
    def get_analytics_summary(): return {}
    def get_orders_by_user(u): return []
    def get_low_stock(t=5): return []
    def get_out_of_stock(): return []
    def update_product(p,d): return False
    def init_db(): pass
    def answer_customer(*a,**k): return "AI غير متوفر"
    def recommend_products(*a,**k): return []
    def extract_budget(t): return None
    def continue_conversation(*a,**k): return "AI غير متوفر"
    def generate_store_report(a): return "AI غير متوفر"

# ── Config ──────────────────────────────────────────────────────────
PORT      = int(os.environ.get("PORT", 10000))
HOST      = "0.0.0.0"
ADMIN_KEY = os.environ.get("ADMIN_API_KEY", "admin_nph_2026")
ADMIN_ID  = int(os.environ.get("ADMIN_USER_ID", "0"))
SITE_URL  = os.environ.get("SITE_URL", "https://neo-pulse-hub.it.com")
PAYPAL    = os.environ.get("PAYPAL_EMAIL", "Saidchaik@gmail.com")

BOT_TOKENS = {
    "customer":       os.environ.get("CUSTOMER_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN",""),
    "admin":          os.environ.get("ADMIN_BOT_TOKEN",""),
    "recommendation": os.environ.get("RECO_BOT_TOKEN") or os.environ.get("RECOMMEND_BOT_TOKEN",""),
    "supplier":       os.environ.get("SUPPLIER_BOT_TOKEN",""),
}

logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
log = logging.getLogger("webhook")

app = Flask(__name__)
CORS(app, origins=["*"])

_conversations = {}

# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════

def send_msg(chat_id, text, token, parse_mode="Markdown"):
    if not token:
        log.error("No token!")
        return False
    try:
        r = requests.post(
            "https://api.telegram.org/bot" + token + "/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
            timeout=10
        )
        return r.status_code == 200
    except Exception as e:
        log.error("send_msg error: " + str(e))
        return False

def send_keyboard(chat_id, text, keyboard, token):
    if not token: return False
    try:
        r = requests.post(
            "https://api.telegram.org/bot" + token + "/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown",
                "reply_markup": {"inline_keyboard": keyboard}
            },
            timeout=10
        )
        return r.status_code == 200
    except Exception as e:
        log.error("send_keyboard error: " + str(e))
        return False

def ok(data=None, message="success", **kwargs):
    resp = {"success": True, "message": message}
    if data is not None: resp["data"] = data
    resp.update(kwargs)
    return jsonify(resp)

def err(message, code=400):
    return jsonify({"success": False, "error": message}), code

def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("X-Admin-Key") or request.args.get("admin_key")
        if key != ADMIN_KEY: abort(403)
        return f(*args, **kwargs)
    return decorated

# ══════════════════════════════════════════════════════════════════
# BOT 1 — CUSTOMER
# ══════════════════════════════════════════════════════════════════

def handle_customer(chat_id, text, first_name, token):
    text = text.strip()

    if text == "/start":
        msg = (
            "👋 *مرحباً " + first_name + " في NEO PULSE HUB!*\n\n"
            "🛍️ متجرك الذكي للمنتجات التقنية\n\n"
            "*الأوامر المتاحة:*\n"
            "/products — تصفح المنتجات\n"
            "/search — بحث عن منتج\n"
            "/recommend — توصية AI\n"
            "/orders — طلباتي\n"
            "/help — المساعدة\n\n"
            "أو اكتب سؤالك مباشرة 🤖"
        )
        send_keyboard(chat_id, msg, [
            [{"text": "🛍️ المنتجات", "callback_data": "products"},
             {"text": "🤖 توصية AI", "callback_data": "recommend"}],
            [{"text": "🌐 الموقع", "url": SITE_URL}]
        ], token)

    elif text == "/products":
        products = get_products()[:6]
        if not products:
            send_msg(chat_id, "لا توجد منتجات حالياً.", token)
            return
        msg = "🛍️ *أبرز منتجاتنا:*\n\n"
        for p in products:
            msg += "• *" + p.get("name_ar","") + "* — $" + str(p.get("price",0)) + "\n"
        msg += "\n🌐 [تصفح الكل](" + SITE_URL + ")"
        send_msg(chat_id, msg, token)

    elif text == "/help":
        send_msg(chat_id,
            "*المساعدة:*\n\n"
            "/products — المنتجات\n"
            "/search [اسم] — بحث\n"
            "/recommend [وصف] — توصية\n"
            "/orders — طلباتي\n"
            "/start — الرئيسية", token)

    elif text.startswith("/search "):
        q = text.replace("/search ", "").strip()
        results = search_products(q)
        if not results:
            send_msg(chat_id, "لم أجد نتائج لـ: " + q, token)
        else:
            msg = "🔍 *نتائج البحث عن \"" + q + "\":*\n\n"
            for p in results[:5]:
                msg += "• *" + p.get("name_ar","") + "* — $" + str(p.get("price",0)) + "\n"
            send_msg(chat_id, msg, token)

    elif text.startswith("/recommend"):
        q = text.replace("/recommend","").strip() or "منتج تقني جيد"
        products = get_products()
        rec_ids  = recommend_products(q, products)
        recs     = [get_product(pid) for pid in rec_ids if get_product(pid)]
        if not recs:
            recs = get_featured_products(3)
        msg = "🤖 *توصياتي لك:*\n\n"
        for p in recs[:3]:
            msg += "⭐ *" + p.get("name_ar","") + "*\n💰 $" + str(p.get("price",0)) + "\n\n"
        send_msg(chat_id, msg, token)

    else:
        # AI chat
        history  = _conversations.setdefault(str(chat_id), [])
        products = get_featured_products(6)
        context  = "\n".join(["• " + p.get("name_ar","") + " $" + str(p["price"]) for p in products])
        reply    = answer_customer(text, context)
        history.append({"role":"user","content":text})
        history.append({"role":"assistant","content":reply})
        if len(history) > 20: _conversations[str(chat_id)] = history[-20:]
        send_msg(chat_id, reply, token)

    track_event("customer_msg", {"chat_id": chat_id, "text": text[:50]})

# ══════════════════════════════════════════════════════════════════
# BOT 2 — ADMIN
# ══════════════════════════════════════════════════════════════════

def handle_admin(chat_id, text, user_id, token):
    if ADMIN_ID and user_id != ADMIN_ID:
        send_msg(chat_id, "🚫 هذا البوت للمدير فقط.", token)
        return

    text = text.strip()

    if text == "/start":
        s = get_analytics_summary()
        msg = (
            "👑 *لوحة تحكم NEO PULSE HUB*\n\n"
            "📊 *الإحصائيات:*\n"
            "🛍️ المنتجات: *" + str(s.get("total_products",0)) + "*\n"
            "📦 الطلبات: *" + str(s.get("total_orders",0)) + "*\n"
            "👥 المستخدمون: *" + str(s.get("total_users",0)) + "*\n"
            "💰 الإيرادات: *$" + str(s.get("total_revenue",0)) + "*\n\n"
            "*الأوامر:*\n"
            "/stats — إحصائيات تفصيلية\n"
            "/stock — حالة المخزون\n"
            "/report — تقرير AI\n"
        )
        send_msg(chat_id, msg, token)

    elif text == "/stats":
        s = get_analytics_summary()
        low = get_low_stock()
        out = get_out_of_stock()
        msg = (
            "📊 *الإحصائيات التفصيلية:*\n\n"
            "🛍️ المنتجات: " + str(s.get("total_products",0)) + "\n"
            "📦 الطلبات الكلية: " + str(s.get("total_orders",0)) + "\n"
            "⏳ المعلقة: " + str(s.get("pending_orders",0)) + "\n"
            "👥 المستخدمون: " + str(s.get("total_users",0)) + "\n"
            "💰 الإيرادات: $" + str(s.get("total_revenue",0)) + "\n"
            "⚠️ مخزون منخفض: " + str(len(low)) + "\n"
            "❌ نفد مخزونه: " + str(len(out)) + "\n"
        )
        send_msg(chat_id, msg, token)

    elif text == "/stock":
        low = get_low_stock()
        out = get_out_of_stock()
        if not low and not out:
            send_msg(chat_id, "✅ المخزون كافٍ لجميع المنتجات.", token)
        else:
            msg = "📦 *تقرير المخزون:*\n\n"
            for p in out[:5]:
                msg += "❌ " + p.get("name_ar","") + " — *نفد!*\n"
            for p in low[:5]:
                msg += "⚠️ " + p.get("name_ar","") + " — " + str(p.get("stock",0)) + " وحدة\n"
            send_msg(chat_id, msg, token)

    elif text == "/report":
        send_msg(chat_id, "⏳ جاري إنشاء التقرير بالـ AI...", token)
        s      = get_analytics_summary()
        report = generate_store_report(s)
        send_msg(chat_id, "📈 *تقرير المتجر:*\n\n" + report, token)

    elif text.startswith("/broadcast "):
        broadcast_text = text.replace("/broadcast ","").strip()
        if not broadcast_text:
            send_msg(chat_id, "❌ أرسل النص بعد /broadcast", token)
            return
        send_msg(chat_id, "✅ تم إرسال الرسالة:\n\n" + broadcast_text, token)

    else:
        send_msg(chat_id,
            "👑 *أوامر الإدارة:*\n\n"
            "/start — لوحة التحكم\n"
            "/stats — الإحصائيات\n"
            "/stock — المخزون\n"
            "/report — تقرير AI\n"
            "/broadcast [رسالة] — بث للمستخدمين", token)

# ══════════════════════════════════════════════════════════════════
# BOT 3 — RECOMMENDATION
# ══════════════════════════════════════════════════════════════════

def handle_recommendation(chat_id, text, first_name, token):
    text = text.strip()

    if text == "/start":
        send_keyboard(chat_id,
            "🎯 *بوت التوصيات الذكي*\n\n"
            "مرحباً " + first_name + "! سأساعدك في اختيار المنتج المناسب.\n\n"
            "اكتب وصف ما تريد أو اختر:",
            [
                [{"text": "⌚ ساعات ذكية", "callback_data": "reco_smartwatch"},
                 {"text": "🎧 سماعات", "callback_data": "reco_earbuds"}],
                [{"text": "🏠 منزل ذكي", "callback_data": "reco_home"},
                 {"text": "💪 صحة ولياقة", "callback_data": "reco_health"}],
                [{"text": "💰 ضمن ميزانيتي", "callback_data": "reco_budget"}],
            ], token)

    elif text.startswith("/recommend") or text.startswith("/reco"):
        q        = text.split(" ",1)[1].strip() if " " in text else "منتج تقني جيد"
        budget   = extract_budget(q)
        products = get_products()
        if budget:
            products = [p for p in products if p.get("price",9999) <= budget * 1.1]
        rec_ids  = recommend_products(q, products, budget)
        recs     = [get_product(pid) for pid in rec_ids if get_product(pid)]
        if not recs: recs = get_featured_products(3)
        msg = "🤖 *أنصحك بهذه المنتجات:*\n\n"
        for p in recs[:3]:
            msg += (
                "⭐ *" + p.get("name_ar","") + "*\n"
                "💰 $" + str(p.get("price",0)) + " | ⭐ " + str(p.get("rating",0)) + "/5\n"
                "🔗 [شاهد المنتج](" + SITE_URL + ")\n\n"
            )
        send_msg(chat_id, msg, token)

    elif text.startswith("/compare "):
        parts = text.replace("/compare ","").split(" vs ")
        if len(parts) == 2:
            p1 = search_products(parts[0].strip())
            p2 = search_products(parts[1].strip())
            if p1 and p2:
                a, b = p1[0], p2[0]
                msg = (
                    "⚖️ *المقارنة:*\n\n"
                    "*" + a.get("name_ar","") + "*\n"
                    "💰 $" + str(a.get("price",0)) + " | ⭐ " + str(a.get("rating",0)) + "\n\n"
                    "VS\n\n"
                    "*" + b.get("name_ar","") + "*\n"
                    "💰 $" + str(b.get("price",0)) + " | ⭐ " + str(b.get("rating",0)) + "\n"
                )
                send_msg(chat_id, msg, token)
            else:
                send_msg(chat_id, "لم أجد المنتجين للمقارنة.", token)
        else:
            send_msg(chat_id, "الاستخدام: /compare منتج1 vs منتج2", token)

    else:
        # AI recommendation from free text
        budget   = extract_budget(text)
        products = get_products()
        if budget:
            products = [p for p in products if p.get("price",9999) <= budget * 1.1]
        rec_ids  = recommend_products(text, products, budget)
        recs     = [get_product(pid) for pid in rec_ids if get_product(pid)]
        if not recs: recs = get_featured_products(3)
        msg = "🎯 *بناءً على طلبك أنصحك بـ:*\n\n"
        for p in recs[:3]:
            msg += "• *" + p.get("name_ar","") + "* — $" + str(p.get("price",0)) + "\n"
        send_msg(chat_id, msg, token)

# ══════════════════════════════════════════════════════════════════
# BOT 4 — SUPPLIER
# ══════════════════════════════════════════════════════════════════

def handle_supplier(chat_id, text, user_id, token):
    if ADMIN_ID and user_id != ADMIN_ID:
        send_msg(chat_id, "🚫 هذا البوت للمدير فقط.", token)
        return

    text = text.strip()

    if text == "/start":
        low = get_low_stock()
        out = get_out_of_stock()
        msg = (
            "📦 *بوت الموردين والمخزون*\n\n"
            "⚠️ مخزون منخفض: *" + str(len(low)) + "* منتج\n"
            "❌ نفد مخزونه: *" + str(len(out)) + "* منتج\n\n"
            "*الأوامر:*\n"
            "/stock — حالة المخزون\n"
            "/low — المنتجات المنخفضة\n"
            "/restock [ID] [كمية] — تحديث مخزون\n"
            "/price [ID] [سعر] — تحديث سعر\n"
            "/products — قائمة المنتجات\n"
        )
        send_msg(chat_id, msg, token)

    elif text == "/stock":
        products = get_products()
        ok_count  = sum(1 for p in products if p.get("stock",0) > 5)
        low_count = sum(1 for p in products if 0 < p.get("stock",0) <= 5)
        out_count = sum(1 for p in products if p.get("stock",0) == 0)
        msg = (
            "📦 *تقرير المخزون:*\n\n"
            "✅ كافٍ: " + str(ok_count) + "\n"
            "⚠️ منخفض: " + str(low_count) + "\n"
            "❌ نفد: " + str(out_count) + "\n"
            "📊 الكلي: " + str(len(products)) + " منتج"
        )
        send_msg(chat_id, msg, token)

    elif text == "/low":
        low = get_low_stock()
        out = get_out_of_stock()
        if not low and not out:
            send_msg(chat_id, "✅ لا توجد مشاكل في المخزون.", token)
        else:
            msg = "⚠️ *يحتاج إعادة تخزين:*\n\n"
            for p in out[:5]:
                msg += "❌ `" + p["id"] + "` " + p.get("name_ar","") + "\n"
            for p in low[:5]:
                msg += "⚠️ `" + p["id"] + "` " + p.get("name_ar","") + " — " + str(p.get("stock",0)) + " وحدة\n"
            send_msg(chat_id, msg, token)

    elif text == "/products":
        products = get_products()
        msg = "📋 *قائمة المنتجات (" + str(len(products)) + "):*\n\n"
        for p in products[:10]:
            s    = p.get("stock",0)
            icon = "❌" if s==0 else "⚠️" if s<=5 else "✅"
            msg += icon + " `" + p["id"] + "` " + p.get("name_ar","")[:20] + " — " + str(s) + "\n"
        send_msg(chat_id, msg, token)

    elif text.startswith("/restock "):
        parts = text.replace("/restock ","").split()
        if len(parts) >= 2:
            pid, qty = parts[0], parts[1]
            try:
                ok_update = update_product(pid, {"stock": int(qty)})
                send_msg(chat_id,
                    ("✅ تم تحديث مخزون `" + pid + "` إلى " + qty + " وحدة")
                    if ok_update else "❌ المنتج غير موجود: " + pid, token)
            except:
                send_msg(chat_id, "❌ الكمية يجب أن تكون رقماً", token)
        else:
            send_msg(chat_id, "الاستخدام: /restock NPH-001 50", token)

    elif text.startswith("/price "):
        parts = text.replace("/price ","").split()
        if len(parts) >= 2:
            pid, price = parts[0], parts[1]
            try:
                ok_update = update_product(pid, {"price": float(price)})
                send_msg(chat_id,
                    ("✅ تم تحديث سعر `" + pid + "` إلى $" + price)
                    if ok_update else "❌ المنتج غير موجود: " + pid, token)
            except:
                send_msg(chat_id, "❌ السعر يجب أن يكون رقماً", token)
        else:
            send_msg(chat_id, "الاستخدام: /price NPH-001 149.99", token)

    else:
        send_msg(chat_id,
            "📦 *أوامر بوت الموردين:*\n\n"
            "/start — الرئيسية\n"
            "/stock — المخزون\n"
            "/low — المنخفض\n"
            "/products — القائمة\n"
            "/restock [ID] [كمية]\n"
            "/price [ID] [سعر]", token)

# ══════════════════════════════════════════════════════════════════
# WEBHOOK ROUTES
# ══════════════════════════════════════════════════════════════════

def process_update(bot_name, update):
    token     = BOT_TOKENS.get(bot_name,"")
    message   = update.get("message") or update.get("edited_message")
    callback  = update.get("callback_query")

    if message and "text" in message:
        chat_id    = message["chat"]["id"]
        text       = message["text"]
        user_id    = message["from"]["id"]
        first_name = message["from"].get("first_name","صديقي")

        log.info(bot_name + " ← " + str(chat_id) + ": " + text[:50])

        if bot_name == "customer":
            handle_customer(chat_id, text, first_name, token)
        elif bot_name == "admin":
            handle_admin(chat_id, text, user_id, token)
        elif bot_name == "recommendation":
            handle_recommendation(chat_id, text, first_name, token)
        elif bot_name == "supplier":
            handle_supplier(chat_id, text, user_id, token)

    elif callback:
        chat_id = callback["message"]["chat"]["id"]
        data    = callback.get("data","")
        token   = BOT_TOKENS.get(bot_name,"")

        if data == "products":
            handle_customer(chat_id, "/products", "", token)
        elif data == "recommend":
            handle_customer(chat_id, "/recommend منتج تقني مميز", "", token)
        elif data.startswith("reco_"):
            cats = {"reco_smartwatch":"ساعة ذكية","reco_earbuds":"سماعات",
                    "reco_home":"منزل ذكي","reco_health":"صحة","reco_budget":"ضمن ميزانيتي"}
            q = cats.get(data,"منتج تقني")
            handle_recommendation(chat_id, q, "", token)

        # Answer callback
        try:
            requests.post(
                "https://api.telegram.org/bot" + token + "/answerCallbackQuery",
                json={"callback_query_id": callback["id"]}, timeout=5
            )
        except: pass

@app.route("/webhook/customer", methods=["POST"])
def wh_customer():
    try: process_update("customer", request.get_json())
    except Exception as e: log.error("customer webhook: " + str(e))
    return "OK", 200

@app.route("/webhook/admin", methods=["POST"])
def wh_admin():
    try: process_update("admin", request.get_json())
    except Exception as e: log.error("admin webhook: " + str(e))
    return "OK", 200

@app.route("/webhook/recommendation", methods=["POST"])
def wh_recommendation():
    try: process_update("recommendation", request.get_json())
    except Exception as e: log.error("recommendation webhook: " + str(e))
    return "OK", 200

@app.route("/webhook/supplier", methods=["POST"])
def wh_supplier():
    try: process_update("supplier", request.get_json())
    except Exception as e: log.error("supplier webhook: " + str(e))
    return "OK", 200

# ══════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ══════════════════════════════════════════════════════════════════

@app.route("/api/products", methods=["GET"])
def api_products():
    cat      = request.args.get("cat")
    limit    = min(int(request.args.get("limit",50)),100)
    featured = request.args.get("featured") == "1"
    q        = request.args.get("q","").strip()
    sort_by  = request.args.get("sort","")

    if q:          products = search_products(q)
    elif cat:      products = get_products_by_category(cat)
    elif featured: products = get_featured_products(limit)
    else:          products = get_products()

    if sort_by == "price_asc":  products = sorted(products, key=lambda x: x.get("price",0))
    elif sort_by == "price_desc": products = sorted(products, key=lambda x: x.get("price",0), reverse=True)
    elif sort_by == "rating":   products = sorted(products, key=lambda x: x.get("rating",0), reverse=True)

    products = [p for p in products if p.get("active",True) is not False]
    return ok(products[:limit], count=len(products[:limit]))

@app.route("/api/products/<pid>", methods=["GET"])
def api_product(pid):
    p = get_product(pid)
    if not p: return err("Not found", 404)
    track_product_view(pid)
    p["product_reviews"] = get_product_reviews(pid)[:5]
    return ok(p)

@app.route("/api/newsletter", methods=["POST"])
def api_newsletter():
    body  = request.get_json(silent=True) or {}
    email = body.get("email","").strip()
    if not email or "@" not in email: return err("Valid email required")
    new = subscribe_email(email)
    track_event("newsletter", {"email": email})
    return ok({"subscribed": True}, message="Subscribed!" if new else "Already subscribed")

@app.route("/api/orders", methods=["POST"])
def api_orders():
    body = request.get_json(silent=True) or {}
    pid  = body.get("product_id","")
    qty  = max(1, int(body.get("qty",1)))
    uid  = int(body.get("user_id",0))
    p    = get_product(pid)
    if not p: return err("Product not found",404)
    if p.get("stock",0) < qty: return err("Insufficient stock")
    order = create_order(pid, uid, qty, "paypal")
    return ok(order), 201

@app.route("/api/ai/chat", methods=["POST"])
def api_chat():
    body    = request.get_json(silent=True) or {}
    message = body.get("message","").strip()
    sid     = body.get("session_id","anon")
    if not message: return err("message required")
    history  = _conversations.setdefault(sid, [])
    products = get_featured_products(6)
    context  = "\n".join(["• " + p.get("name_ar","") + " $" + str(p["price"]) for p in products])
    reply    = continue_conversation(history, message, context)
    history.append({"role":"user","content":message})
    history.append({"role":"assistant","content":reply})
    if len(history) > 20: _conversations[sid] = history[-20:]
    return ok({"reply": reply, "session_id": sid})

@app.route("/api/analytics", methods=["GET"])
@require_admin
def api_analytics():
    return ok(get_analytics_summary())

@app.route("/api/health", methods=["GET"])
def api_health():
    products = get_products()
    return ok({
        "status":    "healthy",
        "products":  len(products),
        "bots":      {k: "✅" if v else "❌" for k,v in BOT_TOKENS.items()},
        "timestamp": datetime.now().isoformat(),
        "version":   "3.0.0"
    })

@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "name":    "NEO PULSE HUB API v3",
        "webhooks":["/webhook/customer","/webhook/admin",
                    "/webhook/recommendation","/webhook/supplier"],
        "store":   SITE_URL
    })

@app.errorhandler(404)
def not_found(e): return err("Not found",404)

@app.errorhandler(500)
def server_error(e): return err("Server error",500)

if __name__ == "__main__":
    init_db()
    log.info("NEO PULSE HUB Webhook Server v3 starting on port " + str(PORT))
    for name, token in BOT_TOKENS.items():
        log.info(name + ": " + ("✅" if token else "❌ MISSING"))
    app.run(host=HOST, port=PORT, threaded=True)
    grep -n "supplier" /home/claude/neopulse/webhook_server.py | head -30
