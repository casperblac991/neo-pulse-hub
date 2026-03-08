#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════╗
║   NEO PULSE HUB — Webhook API Server                           ║
║   يربط الموقع (HTML/JS) بقاعدة البيانات والبوتات               ║
║                                                                  ║
║   Endpoints:                                                    ║
║   GET  /api/products          — جلب جميع المنتجات              ║
║   GET  /api/products/<id>     — منتج محدد                       ║
║   GET  /api/products/search   — بحث                             ║
║   POST /api/orders            — إنشاء طلب جديد                 ║
║   POST /api/leads             — تسجيل مستخدم جديد              ║
║   POST /api/newsletter        — اشتراك بالنشرة                 ║
║   POST /api/reviews           — إضافة تقييم                     ║
║   GET  /api/analytics         — إحصائيات (admin only)          ║
║   POST /api/ai/recommend      — توصيات AI                       ║
║   POST /api/ai/chat           — محادثة AI                       ║
║   POST /webhook               — استقبال تحديثات تيليجرام        ║
╚══════════════════════════════════════════════════════════════════╝

تشغيل: python webhook_server.py
المنفذ الافتراضي: 5000
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
PORT = int(os.environ.get("API_PORT", 5000))
HOST = os.environ.get("API_HOST", "0.0.0.0")
API_SECRET = os.environ.get("API_SECRET", "neopulse_secret_2026")
ADMIN_KEY = os.environ.get("ADMIN_API_KEY", "admin_nph_2026")
DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")

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
# TELEGRAM WEBHOOK - معالج الرسائل
# ══════════════════════════════════════════════════════════════════

@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    """استقبال التحديثات من تيليجرام والرد عليها"""
    try:
        update = request.get_json()
        update_id = update.get('update_id')
        log.info(f"📩 Received Telegram update: {update_id}")
        
        # التحقق من وجود رسالة نصية
        if 'message' in update and 'text' in update['message']:
            chat_id = update['message']['chat']['id']
            text = update['message']['text']
            first_name = update['message']['chat'].get('first_name', 'صديقي')
            log.info(f"💬 Message from {chat_id} ({first_name}): {text}")
            
            # التحقق من وجود التوكن
            if not TELEGRAM_TOKEN:
                log.error("❌ TELEGRAM_TOKEN not found in environment")
                return "OK", 200
            
            # معالجة الأوامر المختلفة
            reply_text = ""
            
            if text == '/start':
                reply_text = (
                    f"👋 مرحباً {first_name}!\n\n"
                    f"🤖 أنا بوت **NEO PULSE HUB**\n"
                    f"متجرك للمنتجات الذكية والذكاء الاصطناعي 🚀\n\n"
                    f"📋 **الأوامر المتاحة:**\n"
                    f"• /start - الصفحة الرئيسية\n"
                    f"• /products - عرض المنتجات\n"
                    f"• /help - المساعدة\n\n"
                    f"كيف يمكنني مساعدتك؟"
                )
            elif text == '/products':
                # جلب بعض المنتجات
                products = get_products()
                if products and len(products) > 0:
                    reply_text = "🛍️ **منتجاتنا المتوفرة:**\n\n"
                    for i, p in enumerate(products[:5], 1):
                        name = p.get('name_ar', p.get('name_en', 'منتج'))
                        price = p.get('price', 0)
                        reply_text += f"{i}. {name} — *${price}*\n"
                    reply_text += "\nللمزيد زور موقعنا: https://neo-pulse-hub.it.com"
                else:
                    reply_text = "🛍️ لا توجد منتجات متاحة حالياً. قريباً..."
            elif text == '/help':
                reply_text = (
                    "📖 **المساعدة:**\n\n"
                    "الأوامر المتاحة:\n"
                    "/start - الصفحة الرئيسية\n"
                    "/products - عرض المنتجات\n"
                    "/help - هذه الرسالة\n\n"
                    "🌐 الموقع: https://neo-pulse-hub.it.com\n"
                    "📧 للدعم: info@neo-pulse-hub.it.com"
                )
            else:
                # رد على أي رسالة أخرى
                reply_text = (
                    f"🤖 استقبلت رسالتك: \"{text}\"\n\n"
                    f"شكراً لتواصلك! أنا لا أزال في طور التطوير.\n"
                    f"استخدم /help لمعرفة الأوامر المتاحة."
                )
            
            # إرسال الرد إلى تيليجرام
            send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': reply_text,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(send_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                log.info(f"✅ Replied to {chat_id}")
            else:
                log.error(f"❌ Failed to reply: {response.status_code} - {response.text}")
        
        return "OK", 200
    except Exception as e:
        log.error(f"💥 Webhook error: {e}")
        return "Error", 500

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
    if request.path.startswith("/api") or request.path == "/webhook":
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
    sort_by = request.args.get("sort", "")  # price_asc|price_desc|rating|discount
    q = request.args.get("q", "").strip()

    if q:
        products = search_products(q)
    elif cat:
        products = get_products_by_category(cat)
    elif featured:
        products = get_featured_products(limit)
    else:
        products = get_products()

    # Sort
    if sort_by == "price_asc":
        products = sorted(products, key=lambda x: x.get("price", 0))
    elif sort_by == "price_desc":
        products = sorted(products, key=lambda x: x.get("price", 0), reverse=True)
    elif sort_by == "rating":
        products = sorted(products, key=lambda x: x.get("rating", 0), reverse=True)
    elif sort_by == "discount":
        products = sorted(products, key=lambda x: x.get("discount", 0), reverse=True)

    # Filter active only (unless admin)
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
    # Track view
    session_id = request.headers.get("X-Session-Id", "")
    track_product_view(pid)
    track_event("product_view", {"product_id": pid, "session": session_id})
    # Include reviews
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
    """
    POST /api/orders
    Body: {product_id, qty?, payment_method?, user_id?}
    """
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
    """
    POST /api/leads
    Body: {name, email, phone?, source?}
    """
    body = request.get_json(silent=True) or {}
    email = body.get("email", "").strip()
    name = body.get("name", "").strip() or "زائر"

    if not email or "@" not in email:
        return err("Valid email is required")

    # Create a fake TG user-like object
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
    """POST /api/newsletter  Body: {email}"""
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
    """POST /api/reviews  Body: {product_id, rating, comment, user_id?}"""
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
    """
    POST /api/ai/chat
    Body: {message, session_id?}
    الدردشة الذكية للموقع — يُرجع رد الـ AI
    """
    body = request.get_json(silent=True) or {}
    message = body.get("message", "").strip()
    session_id = body.get("session_id", "anon")

    if not message:
        return err("message is required")

    # Get conversation history
    history = _conversations.setdefault(session_id, [])
    products = get_featured_products(6)
    context = "\n".join([
        f"• {p.get('name_ar', '')} ${p['price']}"
        for p in products
    ])

    response = continue_conversation(history, message, context)

    # Update history
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": response})
    if len(history) > 20:
        _conversations[session_id] = history[-20:]

    track_event("ai_chat", {"session": session_id, "query_len": len(message)})
    return ok({"reply": response, "session_id": session_id})

@app.route("/api/ai/recommend", methods=["POST"])
def api_ai_recommend():
    """
    POST /api/ai/recommend
    Body: {query, budget?, category?}
    يُرجع قائمة منتجات مُوصى بها
    """
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
    """POST /api/analytics/track  Body: {event, data?}"""
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
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    })

@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "name": "NEO PULSE HUB API",
        "version": "2.0.0",
        "docs": "/api/health",
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
    log.info(f"🌐 Webhook Server starting on {HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=DEBUG, threaded=True)
