#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════╗
║   NEO PULSE HUB — Webhook API Server (Multi-Bot - Paths)       ║
║   مسارات منفصلة لكل بوت لضمان عدم التداخل                      ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import logging
import requests
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, abort
from flask_cors import CORS

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# إضافة مسار المجلد الحالي للمكتبات
sys.path.insert(0, os.path.dirname(__file__))

# استيراد دوال قاعدة البيانات
try:
    from shared_db import (
        get_products, get_product, search_products, get_products_by_category,
        get_featured_products, create_order, upsert_user, subscribe_email,
        add_review, get_product_reviews, track_event, track_product_view,
        get_analytics_summary, get_orders_by_user, init_db
    )
    from ai_engine import (
        answer_customer, recommend_products, extract_budget,
        continue_conversation
    )
except ImportError as e:
    print(f"⚠️ Warning: Could not import shared_db or ai_engine: {e}")
    # Define dummy functions if imports fail
    def get_products(): return []
    def get_product(pid): return None
    def search_products(q): return []
    def get_products_by_category(cat): return []
    def get_featured_products(limit): return []
    def create_order(*args, **kwargs): return {"id": "dummy"}
    def upsert_user(*args, **kwargs): return {"id": 0}
    def subscribe_email(email): return True
    def add_review(*args, **kwargs): return {}
    def get_product_reviews(pid): return []
    def track_event(event, data): pass
    def track_product_view(pid, uid=None): pass
    def get_analytics_summary(): return {}
    def get_orders_by_user(uid): return []
    def init_db(): pass
    def answer_customer(*args, **kwargs): return "AI response"
    def recommend_products(*args, **kwargs): return []
    def extract_budget(text): return None
    def continue_conversation(*args, **kwargs): return "Conversation"

# ── Config ─────────────────────────────────────────────────────────
PORT = int(os.environ.get("PORT", 10000))
HOST = os.environ.get("API_HOST", "0.0.0.0")
API_SECRET = os.environ.get("API_SECRET", "neopulse_secret_2026")
ADMIN_KEY = os.environ.get("ADMIN_API_KEY", "admin_nph_2026")
DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"

# توكنات البوتات (كلها من المتغيرات البيئية)
BOT_TOKENS = {
    'customer': os.environ.get('TELEGRAM_TOKEN', ''),
    'admin': os.environ.get('ADMIN_BOT_TOKEN', ''),
    'recommendation': os.environ.get('RECOMMEND_BOT_TOKEN', ''),
    'supplier': os.environ.get('SUPPLIER_BOT_TOKEN', ''),
}

# رسائل الترحيب لكل بوت
WELCOME_MESSAGES = {
    'customer': (
        "👋 مرحباً بك في **NEO PULSE HUB**!\n\n"
        "أنا بوت خدمة العملاء. كيف يمكنني مساعدتك؟\n\n"
        "الأوامر المتاحة:\n"
        "/start - الترحيب\n"
        "/products - عرض المنتجات\n"
        "/help - المساعدة"
    ),
    'admin': (
        "👑 مرحباً بك في **بوت الإدارة**\n\n"
        "هذا البوت مخصص للمدير فقط.\n\n"
        "الأوامر المتاحة:\n"
        "/stats - إحصائيات المتجر\n"
        "/broadcast [رسالة] - بث للمستخدمين\n"
        "/add_product - إضافة منتج"
    ),
    'recommendation': (
        "🎯 مرحباً بك في **بوت التوصيات الذكي**\n\n"
        "سأساعدك في اختيار المنتج المناسب.\n\n"
        "الأوامر المتاحة:\n"
        "/recommend [وصف] - توصية مخصصة\n"
        "/compare [منتج1] vs [منتج2] - مقارنة\n"
        "/budget [مبلغ] - منتجات ضمن الميزانية"
    ),
    'supplier': (
        "📦 مرحباً بك في **بوت الموردين**\n\n"
        "هذا البوت لإدارة المخزون والمنتجات.\n\n"
        "الأوامر المتاحة:\n"
        "/add [وصف] - إضافة منتج بالذكاء الاصطناعي\n"
        "/stock - حالة المخزون\n"
        "/restock [ID] [كمية] - تحديث المخزون"
    )
}

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
log = logging.getLogger("webhook_server")

app = Flask(__name__)
CORS(app, origins=[
    "https://neo-pulse-hub.it.com",
    "https://www.neo-pulse-hub.it.com",
    "http://localhost:*",
    "http://127.0.0.1:*",
])

# ── In-memory conversation store ───────────────────────────────────
_conversations: dict = {}  # {session_id: [history]}

# ══════════════════════════════════════════════════════════════════
# دالة مساعدة لإرسال الرسائل
# ══════════════════════════════════════════════════════════════════

def send_message(chat_id, text, bot_token, parse_mode='Markdown'):
    """إرسال رسالة إلى تيليجرام باستخدام بوت معين"""
    try:
        if not bot_token:
            log.error("❌ No bot token provided for sending message")
            return False
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode
        }
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            log.info(f"✅ Message sent to {chat_id}")
            return True
        else:
            log.error(f"❌ Failed to send: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        log.error(f"Error sending message: {e}")
        return False

# ══════════════════════════════════════════════════════════════════
# TELEGRAM WEBHOOKS - مسار منفصل لكل بوت
# ══════════════════════════════════════════════════════════════════

def handle_webhook(bot_name):
    """معالج موحد لجميع الـ webhooks"""
    try:
        update = request.get_json()
        update_id = update.get('update_id')
        log.info(f"📩 {bot_name} bot received update: {update_id}")
        
        # الحصول على توكن البوت المناسب
        bot_token = BOT_TOKENS.get(bot_name)
        if not bot_token:
            log.error(f"❌ No token found for {bot_name} bot")
            return "Error", 500
        
        # معالجة الرسالة
        if 'message' in update and 'text' in update['message']:
            chat_id = update['message']['chat']['id']
            text = update['message']['text']
            first_name = update['message']['chat'].get('first_name', 'صديقي')
            
            log.info(f"💬 {bot_name} bot received from {chat_id}: {text}")
            
            # تحديد الرد المناسب
            reply_text = ""
            
            if text == '/start':
                reply_text = WELCOME_MESSAGES.get(bot_name, WELCOME_MESSAGES['customer'])
            elif text == '/products' and bot_name == 'customer':
                products = get_products()
                if products:
                    reply_text = "🛍️ **المنتجات المتوفرة:**\n\n"
                    for i, p in enumerate(products[:5], 1):
                        name = p.get('name_ar', p.get('name_en', 'منتج'))
                        price = p.get('price', 0)
                        reply_text += f"{i}. {name} — *${price}*\n"
                else:
                    reply_text = "🛍️ لا توجد منتجات متاحة حالياً."
            elif text == '/help' and bot_name == 'customer':
                reply_text = (
                    "📖 **المساعدة:**\n\n"
                    "/start - الترحيب\n"
                    "/products - عرض المنتجات\n"
                    "/help - هذه الرسالة"
                )
            else:
                reply_text = f"🤖 تم استلام أمر '{text}' بواسطة بوت {bot_name}"
            
            # إرسال الرد
            if reply_text:
                send_message(chat_id, reply_text, bot_token)
                log.info(f"✅ Reply sent to {chat_id} from {bot_name} bot")
        
        return "OK", 200
    except Exception as e:
        log.error(f"💥 Webhook error in {bot_name}: {e}")
        return "Error", 500

@app.route("/webhook/customer", methods=["POST"])
def webhook_customer():
    """Webhook خاص ببوت خدمة العملاء"""
    return handle_webhook('customer')

@app.route("/webhook/admin", methods=["POST"])
def webhook_admin():
    """Webhook خاص ببوت الإدارة"""
    return handle_webhook('admin')

@app.route("/webhook/recommendation", methods=["POST"])
def webhook_recommendation():
    """Webhook خاص ببوت التوصيات"""
    return handle_webhook('recommendation')

@app.route("/webhook/supplier", methods=["POST"])
def webhook_supplier():
    """Webhook خاص ببوت الموردين"""
    return handle_webhook('supplier')

# ══════════════════════════════════════════════════════════════════
# HELPERS
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
    return (request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
            or request.remote_addr or "unknown")

# ══════════════════════════════════════════════════════════════════
# MIDDLEWARE
# ══════════════════════════════════════════════════════════════════

@app.before_request
def log_request():
    if request.path.startswith("/api") or request.path.startswith("/webhook"):
        log.info(f"{request.method} {request.path} — {get_client_ip()}")

@app.after_request
def add_headers(response):
    response.headers["X-Powered-By"] = "NEO PULSE HUB API"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

# ══════════════════════════════════════════════════════════════════
# PRODUCTS ENDPOINTS
# ══════════════════════════════════════════════════════════════════

@app.route("/api/products", methods=["GET"])
def api_products():
    """GET /api/products?cat=smartwatch&limit=6&featured=1"""
    cat = request.args.get("cat")
    limit = min(int(request.args.get("limit", 50)), 100)
    featured = request.args.get("featured") == "1"
    sort_by = request.args.get("sort", "")
    q = request.args.get("q", "").strip()

    if q:
        products = search_products(q)
    elif cat:
        products = get_products_by_category(cat)
    elif featured:
        products = get_featured_products(limit)
    else:
        products = get_products()

    if sort_by == "price_asc":
        products = sorted(products, key=lambda x: x.get("price", 0))
    elif sort_by == "price_desc":
        products = sorted(products, key=lambda x: x.get("price", 0), reverse=True)
    elif sort_by == "rating":
        products = sorted(products, key=lambda x: x.get("rating", 0), reverse=True)
    elif sort_by == "discount":
        products = sorted(products, key=lambda x: x.get("discount", 0), reverse=True)

    admin_key = request.headers.get("X-Admin-Key")
    if admin_key != ADMIN_KEY:
        products = [p for p in products if p.get("active", True) is not False]

    products = products[:limit]
    return ok(products, count=len(products))

@app.route("/api/products/<pid>", methods=["GET"])
def api_product_detail(pid: str):
    """GET /api/products/NPH-001"""
    p = get_product(pid)
    if not p:
        return err("Product not found", 404)
    session_id = request.headers.get("X-Session-Id", "")
    track_product_view(pid)
    track_event("product_view", {"product_id": pid, "session": session_id})
    p["product_reviews"] = get_product_reviews(pid)[:5]
    return ok(p)

@app.route("/api/products/search", methods=["GET"])
def api_search():
    """GET /api/products/search?q=ساعة ذكية"""
    q = request.args.get("q", "").strip()
    if not q:
        return err("Query parameter 'q' is required")
    products = search_products(q)
    track_event("search", {"query": q, "results": len(products)})
    return ok(products, count=len(products))

# ══════════════════════════════════════════════════════════════════
# ORDERS
# ══════════════════════════════════════════════════════════════════

@app.route("/api/orders", methods=["POST"])
def api_create_order():
    body = request.get_json(silent=True) or {}
    pid = body.get("product_id", "").strip()
    qty = max(1, int(body.get("qty", 1)))
    pay = body.get("payment_method", "paypal")
    uid = int(body.get("user_id", 0))

    if not pid:
        return err("product_id is required")

    p = get_product(pid)
    if not p:
        return err("Product not found", 404)
    if p.get("stock", 0) < qty:
        return err(f"Insufficient stock. Available: {p.get('stock', 0)}")

    try:
        order = create_order(pid, uid, qty, pay)
        track_event("order_created", {
            "order_id": order["id"],
            "product_id": pid,
            "total": order["total"],
            "ip": get_client_ip()
        })
        log.info(f"Order created: {order['id']} — ${order['total']}")
        return ok(order, message="Order created successfully"), 201
    except Exception as e:
        log.error(f"Order creation error: {e}")
        return err(str(e), 500)

@app.route("/api/orders/user/<int:user_id>", methods=["GET"])
def api_user_orders(user_id: int):
    orders = get_orders_by_user(user_id)
    return ok(orders)

# ══════════════════════════════════════════════════════════════════
# LEADS / USERS
# ══════════════════════════════════════════════════════════════════

@app.route("/api/leads", methods=["POST"])
def api_create_lead():
    body = request.get_json(silent=True) or {}
    email = body.get("email", "").strip()
    name = body.get("name", "").strip() or "زائر"

    if not email or "@" not in email:
        return err("Valid email is required")

    class FakeTGUser:
        id = abs(hash(email)) % 999999999
        username = email.split("@")[0]
        full_name = name

    user = upsert_user(FakeTGUser(), extra={
        "email": email,
        "phone": body.get("phone", ""),
        "source": body.get("source", "website"),
    })
    track_event("lead_created", {"email": email, "source": body.get("source", "website")})
    return ok({"id": user.get("id"), "email": email}, message="Lead saved"), 201

# ══════════════════════════════════════════════════════════════════
# NEWSLETTER
# ══════════════════════════════════════════════════════════════════

@app.route("/api/newsletter", methods=["POST"])
def api_newsletter():
    body = request.get_json(silent=True) or {}
    email = body.get("email", "").strip()
    if not email or "@" not in email or "." not in email:
        return err("Valid email required")
    new = subscribe_email(email)
    track_event("newsletter_subscribe", {"email": email})
    return ok({"subscribed": True, "new": new},
              message="Subscribed!" if new else "Already subscribed")

# ══════════════════════════════════════════════════════════════════
# REVIEWS
# ══════════════════════════════════════════════════════════════════

@app.route("/api/reviews", methods=["POST"])
def api_add_review():
    body = request.get_json(silent=True) or {}
    product_id = body.get("product_id", "")
    rating = int(body.get("rating", 5))
    comment = body.get("comment", "").strip()
    user_id = int(body.get("user_id", 0))

    if not product_id:
        return err("product_id required")
    if not get_product(product_id):
        return err("Product not found", 404)
    if not 1 <= rating <= 5:
        return err("Rating must be 1-5")

    review = add_review(product_id, user_id, rating, comment)
    return ok(review, message="Review added"), 201

@app.route("/api/reviews/<pid>", methods=["GET"])
def api_get_reviews(pid: str):
    reviews = get_product_reviews(pid)
    return ok(reviews, count=len(reviews))

# ══════════════════════════════════════════════════════════════════
# AI ENDPOINTS
# ══════════════════════════════════════════════════════════════════

@app.route("/api/ai/chat", methods=["POST"])
def api_ai_chat():
    body = request.get_json(silent=True) or {}
    message = body.get("message", "").strip()
    session_id = body.get("session_id", "anon")

    if not message:
        return err("message is required")

    history = _conversations.setdefault(session_id, [])
    products = get_featured_products(6)
    context = "\n".join([
        f"• {p.get('name_ar', '')} ${p['price']}"
        for p in products
    ])

    response = continue_conversation(history, message, context)

    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": response})
    if len(history) > 20:
        _conversations[session_id] = history[-20:]

    track_event("ai_chat", {"session": session_id, "query_len": len(message)})
    return ok({"reply": response, "session_id": session_id})

@app.route("/api/ai/recommend", methods=["POST"])
def api_ai_recommend():
    body = request.get_json(silent=True) or {}
    query = body.get("query", "").strip()
    budget = body.get("budget")
    category = body.get("category", "")

    if not query:
        return err("query is required")

    products = get_products()
    if category:
        cat_products = get_products_by_category(category)
        if cat_products:
            products = cat_products

    if not budget:
        budget = extract_budget(query)
    if budget:
        products = [p for p in products if p.get("price", 9999) <= float(budget) * 1.1]

    rec_ids = recommend_products(query, products, budget)
    recs = [get_product(pid) for pid in rec_ids if get_product(pid)]
    if not recs:
        recs = get_featured_products(3)

    track_event("ai_recommend", {"query": query, "budget": budget})
    return ok(recs[:3], count=len(recs[:3]))

# ══════════════════════════════════════════════════════════════════
# ANALYTICS (admin only)
# ══════════════════════════════════════════════════════════════════

@app.route("/api/analytics", methods=["GET"])
@require_admin
def api_analytics():
    return ok(get_analytics_summary())

@app.route("/api/analytics/track", methods=["POST"])
def api_track():
    body = request.get_json(silent=True) or {}
    event = body.get("event", "")
    data = body.get("data", {})
    data["ip"] = get_client_ip()
    if event:
        track_event(event, data)
    return ok(message="tracked")

# ══════════════════════════════════════════════════════════════════
# HEALTH CHECK
# ══════════════════════════════════════════════════════════════════

@app.route("/api/health", methods=["GET"])
def api_health():
    products = get_products()
    return ok({
        "status": "healthy",
        "products": len(products),
        "bots": {name: "✅" if token else "❌" for name, token in BOT_TOKENS.items()},
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    })

@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "name": "NEO PULSE HUB API (Multi-Bot - Paths)",
        "version": "2.0.0",
        "docs": "/api/health",
        "bots": list(BOT_TOKENS.keys()),
        "store": "https://neo-pulse-hub.it.com"
    })

# ══════════════════════════════════════════════════════════════════
# ERROR HANDLERS
# ══════════════════════════════════════════════════════════════════

@app.errorhandler(404)
def not_found(e):
    return err("Endpoint not found", 404)

@app.errorhandler(403)
def forbidden(e):
    return err("Forbidden — invalid admin key", 403)

@app.errorhandler(500)
def server_error(e):
    log.error(f"Server error: {e}")
    return err("Internal server error", 500)

# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    init_db()
    log.info("=" * 60)
    log.info("🌐 Starting NEO PULSE HUB Webhook Server (Multi-Bot - Paths)")
    log.info("=" * 60)
    
    active_bots = []
    for name, token in BOT_TOKENS.items():
        if token:
            log.info(f"✅ {name.capitalize()} Bot token configured")
            active_bots.append(name)
        else:
            log.warning(f"⚠️ {name.capitalize()} Bot token missing")
    
    log.info(f"🎯 Active bots: {', '.join(active_bots)}")
    log.info(f"🚀 Server running on port {PORT}")
    log.info(f"📌 Webhook paths:")
    for name in active_bots:
        log.info(f"   • /webhook/{name}")
    
    app.run(host=HOST, port=PORT, debug=DEBUG, threaded=True)
