#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO PULSE HUB — Webhook Server + Multi-Bot Handler v3
"""

import os
import sys
import json
import logging
import requests
import random
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, abort
from flask_cors import CORS

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

sys.path.insert(0, os.path.dirname(__file__))

try:
    from shared_db import (
        get_products, get_product, search_products, get_products_by_category,
        get_featured_products, create_order, upsert_user, subscribe_email,
        add_review, get_product_reviews, track_event, track_product_view,
        get_analytics_summary, get_orders_by_user, init_db
    )
    from ai_engine import (
        answer_customer, recommend_products, extract_budget,
        continue_conversation, search_product_by_description
    )
except ImportError as e:
    print("Warning: " + str(e))
    def get_products(): return []
    def get_product(pid): return None
    def search_products(q): return []
    def get_products_by_category(cat): return []
    def get_featured_products(limit=6): return []
    def create_order(*a, **k): return {"id": "dummy"}
    def upsert_user(*a, **k): return {"id": 0}
    def subscribe_email(e): return True
    def add_review(*a, **k): return {}
    def get_product_reviews(pid): return []
    def track_event(e, d): pass
    def track_product_view(pid): pass
    def get_analytics_summary(): return {}
    def get_orders_by_user(uid): return []
    def init_db(): pass
    def answer_customer(*a, **k): return "مرحباً"
    def recommend_products(*a, **k): return []
    def extract_budget(t): return None
    def continue_conversation(*a, **k): return "مرحباً"
    def search_product_by_description(q): return None

# ── Config ──
PORT      = int(os.environ.get("PORT", 10000))
HOST      = os.environ.get("API_HOST", "0.0.0.0")
ADMIN_KEY = os.environ.get("ADMIN_API_KEY", "admin_nph_2026")
DEBUG     = os.environ.get("FLASK_DEBUG", "0") == "1"
ADMIN_ID  = int(os.environ.get("ADMIN_USER_ID", "0"))
SITE_URL  = os.environ.get("SITE_URL", "https://neo-pulse-hub.it.com")

BOT_TOKENS = {
    "customer":       os.environ.get("CUSTOMER_BOT_TOKEN", "") or os.environ.get("TELEGRAM_TOKEN", ""),
    "admin":          os.environ.get("ADMIN_BOT_TOKEN", ""),
    "recommendation": os.environ.get("RECO_BOT_TOKEN", "") or os.environ.get("RECOMMEND_BOT_TOKEN", ""),
    "supplier":       os.environ.get("SUPPLIER_BOT_TOKEN", ""),
}

logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
log = logging.getLogger("webhook_server")

app = Flask(__name__)
CORS(app, origins=[
    "https://neo-pulse-hub.it.com",
    "https://www.neo-pulse-hub.it.com",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
])

_conversations = {}

# ══════════════════════════════════════════════════════════════════
# GITHUB SYNC
# ══════════════════════════════════════════════════════════════════

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO  = os.environ.get("GITHUB_REPO", "casperblac991/neo-pulse-hub")
GITHUB_FILE  = "products.json"
GITHUB_API   = "https://api.github.com"

def _gh_headers():
    return {
        "Authorization": "token " + GITHUB_TOKEN,
        "Accept": "application/vnd.github.v3+json",
    }

def _get_sha():
    try:
        r = requests.get(
            GITHUB_API + "/repos/" + GITHUB_REPO + "/contents/" + GITHUB_FILE,
            headers=_gh_headers(), timeout=10
        )
        if r.status_code == 200:
            return r.json().get("sha", "")
    except:
        pass
    return ""

def push_products_github(products, message="Bot: update products"):
    if not GITHUB_TOKEN:
        log.error("GITHUB_TOKEN missing")
        return False
    try:
        import base64
        content = base64.b64encode(
            json.dumps(products, ensure_ascii=False, indent=2).encode()
        ).decode()
        sha = _get_sha()
        payload = {"message": message, "content": content, "branch": "main"}
        if sha:
            payload["sha"] = sha
        r = requests.put(
            GITHUB_API + "/repos/" + GITHUB_REPO + "/contents/" + GITHUB_FILE,
            headers=_gh_headers(), json=payload, timeout=20
        )
        if r.status_code in [200, 201]:
            log.info("Products pushed to GitHub")
            return True
        log.error("GitHub push: " + str(r.status_code))
        return False
    except Exception as e:
        log.error("push_products_github: " + str(e))
        return False

def pull_products_github():
    if not GITHUB_TOKEN:
        return []
    try:
        import base64
        r = requests.get(
            GITHUB_API + "/repos/" + GITHUB_REPO + "/contents/" + GITHUB_FILE,
            headers=_gh_headers(), timeout=10
        )
        if r.status_code == 200:
            return json.loads(base64.b64decode(r.json()["content"]).decode())
    except Exception as e:
        log.error("pull_products_github: " + str(e))
    return []

# ══════════════════════════════════════════════════════════════════
# TELEGRAM HELPERS
# ══════════════════════════════════════════════════════════════════

def send_message(chat_id, text, bot_token, parse_mode="Markdown"):
    if not bot_token:
        return False
    try:
        r = requests.post(
            "https://api.telegram.org/bot" + bot_token + "/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
            timeout=8
        )
        return r.status_code == 200
    except Exception as e:
        log.error("send_message: " + str(e))
        return False

WELCOME_MESSAGES = {
    "customer": (
        "👋 مرحباً في *NEO PULSE HUB!*\n\n"
        "🛍️ متجرك الذكي للمنتجات التقنية\n\n"
        "الأوامر:\n"
        "/products — تصفح المنتجات\n"
        "/search كلمة — بحث\n"
        "/recommend وصف — توصية AI\n"
        "/help — المساعدة\n\n"
        "أو اكتب سؤالك مباشرة 🤖"
    ),
    "admin": (
        "👑 *لوحة تحكم NEO PULSE HUB*\n\n"
        "الأوامر:\n"
        "/stats — إحصائيات تفصيلية\n"
        "/stock — حالة المخزون\n"
        "/report — تقرير AI"
    ),
    "recommendation": (
        "🎯 *بوت التوصيات الذكي*\n\n"
        "الأوامر:\n"
        "/recommend وصف — توصية مخصصة\n"
        "/budget مبلغ — منتجات ضمن الميزانية\n\n"
        "أو اكتب ما تبحث عنه مباشرة"
    ),
    "supplier": (
        "📦 *بوت الموردين*\n\n"
        "الأوامر:\n"
        "/stock — حالة المخزون\n"
        "/products — قائمة المنتجات\n"
        "/add اسم — إضافة منتج بـ AI\n"
        "/restock ID كمية — تحديث مخزون\n"
        "/price ID سعر — تحديث سعر"
    ),
}

# ══════════════════════════════════════════════════════════════════
# WEBHOOK HANDLERS
# ══════════════════════════════════════════════════════════════════

def handle_webhook(bot_name):
    try:
        update = request.get_json()
        if not update:
            return "OK", 200

        bot_token = BOT_TOKENS.get(bot_name, "")
        if not bot_token:
            return "OK", 200

        if "message" not in update or "text" not in update.get("message", {}):
            return "OK", 200

        msg      = update["message"]
        chat_id  = msg["chat"]["id"]
        text     = msg["text"].strip()
        username = msg["chat"].get("first_name", "صديقي")
        reply    = ""

        log.info(bot_name + " | " + str(chat_id) + ": " + text)

        # ══ CUSTOMER ══
        if bot_name == "customer":
            if text == "/start":
                reply = "👋 مرحباً *" + username + "* في NEO PULSE HUB!\n\n🛍️ متجرك الذكي للمنتجات التقنية\n\nالأوامر:\n/products — المنتجات\n/recommend وصف — توصية AI\n/help — المساعدة\n\nأو اكتب سؤالك مباشرة 🤖"
            elif text == "/products":
                products = get_products()
                if products:
                    reply = "🛍️ *المنتجات المتوفرة:*\n\n"
                    for i, p in enumerate(products[:6], 1):
                        reply += str(i) + ". " + p.get("name_ar","") + " — *$" + str(p.get("price",0)) + "*\n"
                    reply += "\n🌐 [تصفح المتجر](" + SITE_URL + ")"
                else:
                    reply = "🛍️ لا توجد منتجات حالياً."
            elif text == "/help":
                reply = "📖 الأوامر:\n/products /recommend /help\n\nأو اكتب سؤالك مباشرة"
            elif text.startswith("/search "):
                q = text[8:].strip()
                results = search_products(q)
                if results:
                    reply = "🔍 *نتائج \"" + q + "\":*\n\n"
                    for p in results[:5]:
                        reply += "• " + p.get("name_ar","") + " — $" + str(p.get("price",0)) + "\n"
                else:
                    reply = "❌ لا توجد نتائج لـ \"" + q + "\""
            elif text.startswith("/recommend"):
                query = text[10:].strip() or username
                products = get_products()
                ids = recommend_products(query, products)
                recs = [get_product(pid) for pid in ids if get_product(pid)]
                if not recs:
                    recs = get_featured_products(3)
                if recs:
                    reply = "🤖 *توصيات لك:*\n\n"
                    for i, p in enumerate(recs[:3], 1):
                        reply += str(i) + ". *" + p.get("name_ar","") + "* — $" + str(p.get("price",0)) + "\n"
                else:
                    reply = "لا توجد توصيات حالياً."
            else:
                products = get_products()
                ctx = "\n".join([p.get("name_ar","") + " $" + str(p.get("price",0)) for p in products[:6]])
                reply = answer_customer(text, products_context=ctx)

        # ══ ADMIN ══
        elif bot_name == "admin":
            if text == "/start":
                s = get_analytics_summary()
                reply = (
                    "👑 *لوحة تحكم NEO PULSE HUB*\n\n"
                    "🛍️ المنتجات: *" + str(s.get("total_products", 0)) + "*\n"
                    "📦 الطلبات: *" + str(s.get("total_orders", 0)) + "*\n"
                    "👥 المستخدمون: *" + str(s.get("total_users", 0)) + "*\n"
                    "💰 الإيرادات: *$" + str(s.get("total_revenue", 0)) + "*\n\n"
                    "الأوامر:\n/stats /stock /report"
                )
            elif text == "/stats":
                s = get_analytics_summary()
                reply = (
                    "📊 *الإحصائيات التفصيلية:*\n\n"
                    "🛍️ المنتجات: *" + str(s.get("total_products", 0)) + "*\n"
                    "📦 الطلبات الكلية: *" + str(s.get("total_orders", 0)) + "*\n"
                    "⏳ المعلقة: *" + str(s.get("pending_orders", 0)) + "*\n"
                    "👥 المستخدمون: *" + str(s.get("total_users", 0)) + "*\n"
                    "💰 الإيرادات: *$" + str(s.get("total_revenue", 0)) + "*\n"
                    "⚠️ مخزون منخفض: *" + str(s.get("low_stock_count", 0)) + "*\n"
                    "❌ نفد مخزونه: *" + str(s.get("out_of_stock_count", 0)) + "*"
                )
            elif text == "/stock":
                products = get_products()
                if products:
                    reply = "📦 *حالة المخزون:*\n\n"
                    for p in products[:10]:
                        stock = p.get("stock", 0)
                        icon = "✅" if stock > 5 else ("⚠️" if stock > 0 else "❌")
                        reply += icon + " " + p.get("name_ar","") + " — " + str(stock) + " قطعة\n"
                else:
                    reply = "لا توجد منتجات."
            elif text == "/report":
                send_message(chat_id, "⏳ جاري إنشاء التقرير بال AI...", bot_token)
                try:
                    from ai_engine import generate_store_report
                    s = get_analytics_summary()
                    report = generate_store_report(s)
                    reply = "📈 *تقرير المتجر:*\n\n" + report
                except:
                    reply = "❌ عذرا حدث خطأ في إنشاء التقرير."
            else:
                reply = "الأوامر: /stats /stock /report"

        # ══ RECOMMENDATION ══
        elif bot_name == "recommendation":
            if text == "/start":
                reply = WELCOME_MESSAGES["recommendation"]
            elif text.startswith("/recommend"):
                query = text[10:].strip() or "منتج تقني"
                send_message(chat_id, "🔍 جاري البحث...", bot_token)
                products = get_products()
                ids = recommend_products(query, products)
                recs = [get_product(pid) for pid in ids if get_product(pid)]
                if not recs:
                    recs = get_featured_products(3)
                if recs:
                    reply = "🎯 *توصيات لك:*\n\n"
                    for i, p in enumerate(recs[:3], 1):
                        reply += str(i) + ". *" + p.get("name_ar","") + "*\n"
                        reply += "   💰 $" + str(p.get("price",0)) + " | ⭐ " + str(p.get("rating",0)) + "/5\n\n"
                    reply += "🌐 [تصفح المتجر](" + SITE_URL + ")"
                else:
                    reply = "❌ لم أجد توصيات."
            elif text.startswith("/budget "):
                try:
                    budget = float(text[8:].strip())
                    products = [p for p in get_products() if p.get("price",0) <= budget]
                    if products:
                        reply = "💰 *منتجات ضمن $" + str(budget) + ":*\n\n"
                        for p in products[:5]:
                            reply += "• " + p.get("name_ar","") + " — $" + str(p.get("price",0)) + "\n"
                    else:
                        reply = "❌ لا توجد منتجات ضمن هذه الميزانية."
                except:
                    reply = "❌ الصيغة: /budget 100"
            else:
                products = get_products()
                ids = recommend_products(text, products)
                recs = [get_product(pid) for pid in ids if get_product(pid)]
                if recs:
                    reply = "🎯 *توصيات لك:*\n\n"
                    for i, p in enumerate(recs[:3], 1):
                        reply += str(i) + ". *" + p.get("name_ar","") + "* — $" + str(p.get("price",0)) + "\n"
                else:
                    reply = WELCOME_MESSAGES["recommendation"]

        # ══ SUPPLIER ══
        elif bot_name == "supplier":
            if text == "/start":
                reply = WELCOME_MESSAGES["supplier"]

            elif text == "/stock":
                products = get_products()
                if not products:
                    reply = "📦 لا توجد منتجات حالياً."
                else:
                    reply = "📦 *حالة المخزون:*\n\n"
                    for p in products[:15]:
                        stock = p.get("stock", 0)
                        icon = "✅" if stock > 5 else ("⚠️" if stock > 0 else "❌")
                        reply += icon + " `" + p.get("id","") + "` " + p.get("name_ar","") + " — " + str(stock) + " قطعة\n"

            elif text == "/products":
                products = get_products()
                if not products:
                    reply = "لا توجد منتجات."
                else:
                    reply = "🛍️ *قائمة المنتجات:*\n\n"
                    for p in products[:15]:
                        reply += "• `" + p.get("id","") + "` — " + p.get("name_ar","") + " — $" + str(p.get("price",0)) + "\n"

            elif text.startswith("/restock "):
                parts = text.split()
                if len(parts) == 3:
                    pid = parts[1]
                    try:
                        qty = int(parts[2])
                        products = pull_products_github() or get_products()
                        updated = False
                        for p in products:
                            if p.get("id") == pid:
                                p["stock"] = p.get("stock", 0) + qty
                                updated = True
                                break
                        if updated:
                            ok_push = push_products_github(products, "Restock " + pid + " +" + str(qty))
                            reply = "✅ تم تحديث مخزون `" + pid + "` — أضفت " + str(qty) + " قطعة." if ok_push else "❌ فشل الحفظ على GitHub."
                        else:
                            reply = "❌ المنتج `" + pid + "` غير موجود."
                    except:
                        reply = "❌ الصيغة: /restock NPH-001 10"
                else:
                    reply = "❌ الصيغة: /restock ID كمية\nمثال: /restock NPH-001 10"

            elif text.startswith("/price "):
                parts = text.split()
                if len(parts) == 3:
                    pid = parts[1]
                    try:
                        price = float(parts[2])
                        products = pull_products_github() or get_products()
                        updated = False
                        for p in products:
                            if p.get("id") == pid:
                                p["price"] = price
                                updated = True
                                break
                        if updated:
                            ok_push = push_products_github(products, "Price update " + pid)
                            reply = "✅ تم تحديث سعر `" + pid + "` إلى $" + str(price) if ok_push else "❌ فشل الحفظ."
                        else:
                            reply = "❌ المنتج غير موجود."
                    except:
                        reply = "❌ الصيغة: /price NPH-001 99.99"
                else:
                    reply = "❌ الصيغة: /price ID سعر"

            elif text.startswith("/add "):
                product_name = text[5:].strip()
                if product_name:
                    send_message(chat_id, "🔍 جاري البحث عن *" + product_name + "* بالذكاء الاصطناعي...", bot_token)
                    try:
                        result = search_product_by_description(product_name)
                        if result and result.get("found"):
                            products = pull_products_github() or get_products()
                            new_id = "NPH-" + str(random.randint(200, 999))
                            while any(p.get("id") == new_id for p in products):
                                new_id = "NPH-" + str(random.randint(200, 999))
                            new_product = {
                                "id": new_id,
                                "name_ar": result.get("name_ar", product_name),
                                "name_en": result.get("name_en", product_name),
                                "price": result.get("estimated_price_usd", 99),
                                "original_price": result.get("original_retail_usd", 129),
                                "category": result.get("category", "smart-home"),
                                "category_ar": result.get("category_ar", "منزل ذكي"),
                                "rating": result.get("rating", 4.5),
                                "reviews": result.get("reviews_count", 0),
                                "stock": 50,
                                "discount": 10,
                                "featured": False,
                                "active": True,
                                "features_ar": result.get("features_ar", []),
                                "description_ar": result.get("description_ar", ""),
                                "tags": result.get("tags", []),
                                "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400"
                            }
                            products.append(new_product)
                            ok_push = push_products_github(products, "Add: " + new_product["name_ar"])
                            if ok_push:
                                reply = (
                                    "✅ *تم إضافة المنتج بنجاح!*\n\n"
                                    "🆔 ID: `" + new_id + "`\n"
                                    "📦 الاسم: " + new_product["name_ar"] + "\n"
                                    "💰 السعر: $" + str(new_product["price"]) + "\n"
                                    "⭐ التقييم: " + str(new_product["rating"]) + "/5\n"
                                    "📊 المخزون: 50 قطعة\n\n"
                                    "🌐 يظهر على المتجر خلال دقيقة!"
                                )
                            else:
                                reply = "❌ فشل الحفظ على GitHub."
                        else:
                            reply = "❌ لم يجد AI معلومات كافية. جرب اسماً أكثر تحديداً."
                    except Exception as e:
                        reply = "❌ خطأ: " + str(e)
                else:
                    reply = "❌ اكتب اسم المنتج.\nمثال: /add ساعة ذكية آبل"

            else:
                reply = WELCOME_MESSAGES["supplier"]

        if reply:
            send_message(chat_id, reply, bot_token)
        return "OK", 200

    except Exception as e:
        log.error("handle_webhook " + bot_name + ": " + str(e))
        return "OK", 200


@app.route("/webhook/customer", methods=["POST"])
def webhook_customer():
    return handle_webhook("customer")

@app.route("/webhook/admin", methods=["POST"])
def webhook_admin():
    return handle_webhook("admin")

@app.route("/webhook/recommendation", methods=["POST"])
def webhook_recommendation():
    return handle_webhook("recommendation")

@app.route("/webhook/supplier", methods=["POST"])
def webhook_supplier():
    return handle_webhook("supplier")

# ══════════════════════════════════════════════════════════════════
# API HELPERS
# ══════════════════════════════════════════════════════════════════

def ok(data=None, message="success", **kwargs):
    resp = {"success": True, "message": message}
    if data is not None:
        resp["data"] = data
    resp.update(kwargs)
    return jsonify(resp)

def err(message, code=400):
    return jsonify({"success": False, "error": message}), code

def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("X-Admin-Key") or request.args.get("admin_key")
        if key != ADMIN_KEY:
            abort(403)
        return f(*args, **kwargs)
    return decorated

def get_client_ip():
    return (request.headers.get("X-Forwarded-For","").split(",")[0].strip()
            or request.remote_addr or "unknown")

# ══════════════════════════════════════════════════════════════════
# PRODUCTS API
# ══════════════════════════════════════════════════════════════════

@app.route("/api/products", methods=["GET"])
def api_products():
    cat      = request.args.get("cat")
    limit    = min(int(request.args.get("limit", 50)), 100)
    featured = request.args.get("featured") == "1"
    sort_by  = request.args.get("sort", "")
    q        = request.args.get("q","").strip()

    if q:
        products = search_products(q)
    elif cat:
        products = get_products_by_category(cat)
    elif featured:
        products = get_featured_products(limit)
    else:
        products = get_products()

    if sort_by == "price_asc":
        products = sorted(products, key=lambda x: x.get("price",0))
    elif sort_by == "price_desc":
        products = sorted(products, key=lambda x: x.get("price",0), reverse=True)
    elif sort_by == "rating":
        products = sorted(products, key=lambda x: x.get("rating",0), reverse=True)
    elif sort_by == "discount":
        products = sorted(products, key=lambda x: x.get("discount",0), reverse=True)

    admin_key = request.headers.get("X-Admin-Key")
    if admin_key != ADMIN_KEY:
        products = [p for p in products if p.get("active", True) is not False]

    return ok(products[:limit], count=len(products[:limit]))

@app.route("/api/products/<pid>", methods=["GET"])
def api_product_detail(pid):
    p = get_product(pid)
    if not p:
        return err("Product not found", 404)
    track_product_view(pid)
    p["product_reviews"] = get_product_reviews(pid)[:5]
    return ok(p)

@app.route("/api/products/search", methods=["GET"])
def api_search():
    q = request.args.get("q","").strip()
    if not q:
        return err("Query required")
    return ok(search_products(q))

# ══════════════════════════════════════════════════════════════════
# ORDERS
# ══════════════════════════════════════════════════════════════════

@app.route("/api/orders", methods=["POST"])
def api_create_order():
    body = request.get_json(silent=True) or {}
    pid  = body.get("product_id","").strip()
    qty  = max(1, int(body.get("qty", 1)))
    pay  = body.get("payment_method","paypal")
    uid  = int(body.get("user_id", 0))
    if not pid:
        return err("product_id required")
    p = get_product(pid)
    if not p:
        return err("Product not found", 404)
    if p.get("stock",0) < qty:
        return err("Insufficient stock")
    try:
        order = create_order(pid, uid, qty, pay)
        track_event("order_created", {"order_id": order["id"]})
        return ok(order), 201
    except Exception as e:
        return err(str(e), 500)

@app.route("/api/orders/user/<int:user_id>", methods=["GET"])
def api_user_orders(user_id):
    return ok(get_orders_by_user(user_id))

# ══════════════════════════════════════════════════════════════════
# LEADS / NEWSLETTER / REVIEWS
# ══════════════════════════════════════════════════════════════════

@app.route("/api/leads", methods=["POST"])
def api_create_lead():
    body  = request.get_json(silent=True) or {}
    email = body.get("email","").strip()
    name  = body.get("name","").strip() or "زائر"
    if not email or "@" not in email:
        return err("Valid email required")
    class FakeTGUser:
        id        = abs(hash(email)) % 999999999
        username  = email.split("@")[0]
        full_name = name
    user = upsert_user(FakeTGUser(), extra={"email": email, "source": body.get("source","website")})
    return ok({"id": user.get("id"), "email": email}), 201

@app.route("/api/newsletter", methods=["POST"])
def api_newsletter():
    body  = request.get_json(silent=True) or {}
    email = body.get("email","").strip()
    if not email or "@" not in email:
        return err("Valid email required")
    new = subscribe_email(email)
    return ok({"subscribed": True, "new": new})

@app.route("/api/reviews", methods=["POST"])
def api_add_review():
    body       = request.get_json(silent=True) or {}
    product_id = body.get("product_id","")
    rating     = int(body.get("rating", 5))
    comment    = body.get("comment","").strip()
    user_id    = int(body.get("user_id", 0))
    if not product_id or not get_product(product_id):
        return err("Product not found", 404)
    if not 1 <= rating <= 5:
        return err("Rating 1-5")
    return ok(add_review(product_id, user_id, rating, comment)), 201

@app.route("/api/reviews/<pid>", methods=["GET"])
def api_get_reviews(pid):
    return ok(get_product_reviews(pid))

# ══════════════════════════════════════════════════════════════════
# AI
# ══════════════════════════════════════════════════════════════════

@app.route("/api/ai/chat", methods=["POST"])
def api_ai_chat():
    body       = request.get_json(silent=True) or {}
    message    = body.get("message","").strip()
    session_id = body.get("session_id","anon")
    if not message:
        return err("message required")
    history  = _conversations.setdefault(session_id, [])
    products = get_featured_products(6)
    context  = "\n".join([p.get("name_ar","") + " $" + str(p["price"]) for p in products])
    response = continue_conversation(history, message, context)
    history.append({"role":"user","content": message})
    history.append({"role":"assistant","content": response})
    if len(history) > 20:
        _conversations[session_id] = history[-20:]
    return ok({"reply": response, "session_id": session_id})

@app.route("/api/ai/recommend", methods=["POST"])
def api_ai_recommend():
    body     = request.get_json(silent=True) or {}
    query    = body.get("query","").strip()
    budget   = body.get("budget")
    category = body.get("category","")
    if not query:
        return err("query required")
    products = get_products_by_category(category) if category else get_products()
    if not budget:
        budget = extract_budget(query)
    if budget:
        products = [p for p in products if p.get("price",9999) <= float(budget) * 1.1]
    rec_ids = recommend_products(query, products, budget)
    recs = [get_product(pid) for pid in rec_ids if get_product(pid)]
    if not recs:
        recs = get_featured_products(3)
    return ok(recs[:3])

# ══════════════════════════════════════════════════════════════════
# ANALYTICS / HEALTH
# ══════════════════════════════════════════════════════════════════

@app.route("/api/analytics", methods=["GET"])
@require_admin
def api_analytics():
    return ok(get_analytics_summary())

@app.route("/api/analytics/track", methods=["POST"])
def api_track():
    body  = request.get_json(silent=True) or {}
    event = body.get("event","")
    data  = body.get("data",{})
    if event:
        track_event(event, data)
    return ok(message="tracked")

@app.route("/api/health", methods=["GET"])
def api_health():
    products = get_products()
    return ok({
        "status":    "healthy",
        "products":  len(products),
        "bots":      {name: "✅" if token else "❌" for name, token in BOT_TOKENS.items()},
        "github":    "✅" if GITHUB_TOKEN else "❌",
        "timestamp": datetime.now().isoformat(),
        "version":   "3.0.0"
    })

@app.route("/", methods=["GET"])
def root():
    return jsonify({"name": "NEO PULSE HUB API v3", "store": SITE_URL, "health": "/api/health"})

@app.errorhandler(404)
def not_found(e): return err("Not found", 404)

@app.errorhandler(403)
def forbidden(e): return err("Forbidden", 403)

@app.errorhandler(500)
def server_error(e): return err("Server error", 500)

if __name__ == "__main__":
    init_db()
    log.info("NEO PULSE HUB starting on port " + str(PORT))
    app.run(host=HOST, port=PORT, debug=DEBUG, threaded=True)
