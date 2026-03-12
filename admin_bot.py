#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO PULSE HUB — Admin Bot v2.0
✅ ADMIN_BOT_TOKEN (صح)
✅ _register_handlers (للـ webhook)
✅ إحصائيات + إدارة المنتجات + broadcast
"""
import os, json, logging
from datetime import datetime
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Application, CommandHandler, MessageHandler,
                           CallbackQueryHandler, filters, ContextTypes)
from telegram.constants import ParseMode

try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass

ADMIN_BOT_TOKEN = os.environ.get("ADMIN_BOT_TOKEN", "")
GEMINI_API_KEY  = (os.environ.get("GEMINI_API_KEY") or
                   os.environ.get("GOOGLE_API_KEY") or "")
ADMIN_USER_ID   = int(os.environ.get("ADMIN_USER_ID", "0"))
BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
PRODUCTS_FILE   = os.path.join(BASE_DIR, "products.json")
ORDERS_FILE     = os.path.join(BASE_DIR, "orders.json")
LEADS_FILE      = os.path.join(BASE_DIR, "leads.json")

log = logging.getLogger("admin_bot")

def load_json(path, default):
    try:
        p = Path(path)
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default
    except:
        return default

def save_json(path, data):
    try:
        Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        log.error(f"save_json: {e}")

def is_admin(uid):
    return ADMIN_USER_ID and int(uid) == ADMIN_USER_ID

def ask_gemini(prompt: str) -> str:
    if not GEMINI_API_KEY:
        return "❌ Gemini غير متاح"
    import requests as _r
    try:
        url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
               f"gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}")
        body = {"contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.7, "maxOutputTokens": 800}}
        data = _r.post(url, json=body, timeout=15).json()
        return (data.get("candidates", [{}])[0]
                    .get("content", {}).get("parts", [{}])[0]
                    .get("text", "❌ لا توجد إجابة"))
    except Exception as e:
        log.error(f"Gemini: {e}"); return "❌ خطأ في Gemini"

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        await update.message.reply_text("⛔ غير مصرح.")
        return
    await update.message.reply_text(
        "🛡️ *لوحة تحكم الأدمين — NEO PULSE HUB*\n\n"
        "الأوامر المتاحة:\n"
        "/stats — إحصائيات المتجر\n"
        "/orders — آخر الطلبات\n"
        "/products — عدد المنتجات\n"
        "/broadcast — إرسال رسالة للكل\n"
        "/addproduct — إضافة منتج يدوياً\n"
        "/ai — تحليل AI للمتجر",
        parse_mode=ParseMode.MARKDOWN
    )

async def cmd_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    products = load_json(PRODUCTS_FILE, [])
    orders   = load_json(ORDERS_FILE, {"total_orders": 0, "total_revenue": 0, "orders": []})
    leads    = load_json(LEADS_FILE, {"total_users": 0, "support_chats": 0})

    active_products = [p for p in products if p.get("active", True)]
    recent_orders   = orders.get("orders", [])[:5]
    recent_txt = "\n".join([
        f"• {o.get('id','')} | ${o.get('total',0)} | {o.get('date','')[:10]}"
        for o in recent_orders
    ]) or "لا توجد طلبات بعد"

    await update.message.reply_text(
        f"📊 *إحصائيات NEO PULSE HUB*\n\n"
        f"🛍️ المنتجات النشطة: {len(active_products)}/{len(products)}\n"
        f"📦 إجمالي الطلبات: {orders.get('total_orders', 0)}\n"
        f"💰 إجمالي الإيرادات: ${orders.get('total_revenue', 0):.2f}\n"
        f"👥 إجمالي العملاء: {leads.get('total_users', 0)}\n"
        f"💬 محادثات الدعم: {leads.get('support_chats', 0)}\n\n"
        f"📋 *آخر الطلبات:*\n{recent_txt}",
        parse_mode=ParseMode.MARKDOWN
    )

async def cmd_orders(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    orders = load_json(ORDERS_FILE, {"orders": []})
    recent = orders.get("orders", [])[:10]
    if not recent:
        await update.message.reply_text("📦 لا توجد طلبات بعد.")
        return
    lines = "\n\n".join([
        f"🆔 {o.get('id','')}\n"
        f"📦 {o.get('product','')}\n"
        f"💰 ${o.get('total',0)} | الكمية: {o.get('qty',1)}\n"
        f"📅 {o.get('date','')[:16]}\n"
        f"✅ {o.get('status','confirmed')}"
        for o in recent
    ])
    await update.message.reply_text(f"📦 *آخر الطلبات:*\n\n{lines}", parse_mode=ParseMode.MARKDOWN)

async def cmd_products(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    products = load_json(PRODUCTS_FILE, [])
    cats = {}
    for p in products:
        c = p.get("category", "other")
        cats[c] = cats.get(c, 0) + 1
    lines = "\n".join([f"• {k}: {v}" for k, v in cats.items()])
    active = len([p for p in products if p.get("active", True)])
    await update.message.reply_text(
        f"🛍️ *المنتجات*\n\nالإجمالي: {len(products)}\nنشط: {active}\n\n{lines}",
        parse_mode=ParseMode.MARKDOWN
    )

async def cmd_ai(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    products = load_json(PRODUCTS_FILE, [])
    orders   = load_json(ORDERS_FILE, {"total_orders": 0, "total_revenue": 0})
    msg = await update.message.reply_text("🤖 جاري تحليل المتجر بالذكاء الاصطناعي...")
    prompt = f"""أنت خبير تحليل متاجر إلكترونية. حلّل هذه البيانات وأعطِ توصيات:

المتجر: NEO PULSE HUB — أجهزة ذكية
المنتجات: {len(products)} منتج في {len(set(p.get('category','') for p in products))} فئات
الطلبات: {orders.get('total_orders', 0)}
الإيرادات: ${orders.get('total_revenue', 0)}
أغلى منتج: ${max((p.get('price',0) for p in products), default=0)}
أرخص منتج: ${min((p.get('price',0) for p in products), default=0)}

أعطِ 5 توصيات عملية لزيادة المبيعات باللغة العربية."""
    answer = ask_gemini(prompt)
    await msg.edit_text(f"🤖 *تحليل AI:*\n\n{answer}", parse_mode=ParseMode.MARKDOWN)

async def cmd_broadcast(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    args = ctx.args
    if not args:
        await update.message.reply_text(
            "📢 استخدام: /broadcast رسالتك هنا\n\nمثال: /broadcast عرض خاص 20% خصم اليوم فقط!"
        )
        return
    message = " ".join(args)
    leads = load_json(LEADS_FILE, {"users": []})
    users = leads.get("users", [])
    if not users:
        await update.message.reply_text("❌ لا يوجد مستخدمون بعد.")
        return
    import requests as _r
    token = os.environ.get("CUSTOMER_BOT_TOKEN", "")
    sent = 0
    for user in users:
        try:
            _r.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": user["id"], "text": f"📢 {message}", "parse_mode": "Markdown"},
                timeout=5
            )
            sent += 1
        except:
            pass
    await update.message.reply_text(f"✅ تم الإرسال لـ {sent}/{len(users)} مستخدم.")

async def error_handler(update, ctx: ContextTypes.DEFAULT_TYPE):
    log.error(f"Admin bot error: {ctx.error}")

# ✅ يُستدعى من main.py
def _register_handlers(app):
    app.add_handler(CommandHandler("start",      cmd_start))
    app.add_handler(CommandHandler("stats",      cmd_stats))
    app.add_handler(CommandHandler("orders",     cmd_orders))
    app.add_handler(CommandHandler("products",   cmd_products))
    app.add_handler(CommandHandler("broadcast",  cmd_broadcast))
    app.add_handler(CommandHandler("ai",         cmd_ai))
    app.add_error_handler(error_handler)

if __name__ == "__main__":
    if not ADMIN_BOT_TOKEN:
        print("❌ ADMIN_BOT_TOKEN missing!"); exit(1)
    app = Application.builder().token(ADMIN_BOT_TOKEN).build()
    _register_handlers(app)
    print("🛡️ Admin Bot running...")
    app.run_polling(drop_pending_updates=True)
