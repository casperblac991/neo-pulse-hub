#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO PULSE HUB — Customer Bot v2.0
✅ CUSTOMER_BOT_TOKEN (صح)
✅ _register_handlers (للـ webhook)
✅ chat history
✅ بحث في المنتجات
"""
import os, json, logging
from datetime import datetime
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Application, CommandHandler, MessageHandler,
                           CallbackQueryHandler, filters, ContextTypes)
from telegram.constants import ParseMode, ChatAction

try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass

CUSTOMER_BOT_TOKEN = os.environ.get("CUSTOMER_BOT_TOKEN", "")
GEMINI_API_KEY     = (os.environ.get("GEMINI_API_KEY") or
                      os.environ.get("GOOGLE_API_KEY") or "")
ADMIN_USER_ID      = int(os.environ.get("ADMIN_USER_ID", "0"))
BASE_DIR           = os.path.dirname(os.path.abspath(__file__))
PRODUCTS_FILE      = os.path.join(BASE_DIR, "products.json")
LEADS_FILE         = os.path.join(BASE_DIR, "leads.json")

log = logging.getLogger("customer_bot")

_histories = {}

def get_history(uid):
    return _histories.get(uid, [])

def add_history(uid, role, text):
    h = _histories.setdefault(uid, [])
    h.append({"role": role, "text": text[:400]})
    if len(h) > 8:
        h.pop(0)

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

def load_products():
    return load_json(PRODUCTS_FILE, [])

def upsert_lead(tg_user):
    data = load_json(LEADS_FILE, {"total_users": 0, "users": [], "support_chats": 0})
    for u in data["users"]:
        if int(u["id"]) == tg_user.id:
            u["last_seen"] = datetime.now().isoformat()
            u["chats"] = u.get("chats", 0) + 1
            save_json(LEADS_FILE, data)
            return
    data["users"].append({
        "id": tg_user.id, "username": tg_user.username or "",
        "name": tg_user.full_name or "", "joined": datetime.now().isoformat(),
        "last_seen": datetime.now().isoformat(), "chats": 1
    })
    data["total_users"] = len(data["users"])
    save_json(LEADS_FILE, data)

def ask_gemini(prompt: str) -> str:
    if not GEMINI_API_KEY:
        return "❌ خدمة الذكاء الاصطناعي غير متاحة حالياً."
    import requests as _r
    try:
        url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
               f"gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}")
        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 500}
        }
        resp = _r.post(url, json=body, timeout=15)
        data = resp.json()
        return (data.get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "⚠️ لا توجد إجابة."))
    except Exception as e:
        log.error(f"Gemini: {e}")
        return "⚠️ حدث خطأ. حاول مرة أخرى."

def build_prompt(user_msg: str, uid: int) -> str:
    products = load_products()
    keywords = user_msg.lower().split()
    relevant = [p for p in products
                if any(kw in (p.get("name_ar","") + p.get("name_en","") +
                              p.get("category_ar","")).lower()
                       for kw in keywords)]
    if not relevant:
        relevant = sorted(products, key=lambda x: x.get("reviews", 0), reverse=True)[:6]

    prod_lines = "\n".join([
        f"- {p.get('name_ar','')} | ${p.get('price',0)} | ⭐{p.get('rating',0)} | "
        f"https://neo-pulse-hub.it.com/product-detail.html?id={p.get('id','')}"
        for p in relevant[:6]
    ])
    history = get_history(uid)
    hist_text = "\n".join([
        f"{'العميل' if h['role']=='user' else 'المساعد'}: {h['text']}"
        for h in history
    ])
    return f"""أنت مساعد خدمة عملاء ذكي لمتجر NEO PULSE HUB للأجهزة الذكية.

المتجر: https://neo-pulse-hub.it.com
الدفع: PayPal | الشحن: 3-7 أيام | الإرجاع: 30 يوم مجاناً

المنتجات المتاحة:
{prod_lines}

سجل المحادثة:
{hist_text if hist_text else "بداية المحادثة"}

سؤال العميل: {user_msg}

أجب بالعربية بشكل ودود ومختصر (3-4 جمل). إذا سأل عن منتج أعطه السعر والرابط."""

def kb_main():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍️ تصفح المنتجات", url="https://neo-pulse-hub.it.com/products.html")],
        [InlineKeyboardButton("📦 تتبع طلب", callback_data="track"),
         InlineKeyboardButton("🚚 الشحن", callback_data="shipping")],
        [InlineKeyboardButton("🔄 الإرجاع", callback_data="returns"),
         InlineKeyboardButton("📞 تواصل", callback_data="contact")]
    ])

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    upsert_lead(update.effective_user)
    _histories.pop(update.effective_user.id, None)
    name = update.effective_user.first_name or "عزيزنا"
    await update.message.reply_text(
        f"👋 أهلاً *{name}*!\n\n"
        "أنا مساعد *NEO PULSE HUB* الذكي 🤖\n\n"
        "• 🛍️ اختيار المنتج المناسب\n"
        "• 📦 تتبع طلبك\n"
        "• 💳 الدفع والشحن\n"
        "• 🔄 سياسة الإرجاع\n\n"
        "اكتب سؤالك وسأجيبك فوراً! 💬",
        parse_mode=ParseMode.MARKDOWN, reply_markup=kb_main()
    )

async def cmd_products(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    products = load_products()
    featured = [p for p in products if p.get("featured") and p.get("active", True)][:5]
    if not featured:
        featured = sorted(products, key=lambda x: x.get("rating", 0), reverse=True)[:5]
    lines = "\n".join([
        f"• *{p['name_ar']}* — ${p['price']} ⭐{p.get('rating',0)}\n"
        f"  [عرض المنتج](https://neo-pulse-hub.it.com/product-detail.html?id={p['id']})"
        for p in featured
    ])
    await update.message.reply_text(
        f"🌟 *أبرز منتجاتنا:*\n\n{lines}\n\n"
        f"[← تصفح الكل](https://neo-pulse-hub.it.com/products.html)",
        parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True
    )

async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    upsert_lead(update.effective_user)
    text = update.message.text.strip()
    uid  = update.effective_user.id
    if len(text) < 2:
        return
    await update.message.chat.send_action(ChatAction.TYPING)
    msg = await update.message.reply_text("⏳ جاري البحث...")
    add_history(uid, "user", text)
    answer = ask_gemini(build_prompt(text, uid))
    add_history(uid, "assistant", answer)
    await msg.edit_text(answer, parse_mode=ParseMode.MARKDOWN)

async def handle_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    d = q.data
    if d == "track":
        await q.edit_message_text(
            "📦 *تتبع طلبك*\n\nأرسل رقم طلبك أو تتبع من الموقع مباشرة:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔍 تتبع الطلب", url="https://neo-pulse-hub.it.com/track.html")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="back")]
            ])
        )
    elif d == "shipping":
        await q.edit_message_text(
            "🚚 *الشحن والدفع*\n\n• الشحن: 3-7 أيام عمل\n• مجاني فوق $200\n• الدفع: PayPal آمن 100%",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📄 سياسة الشحن", url="https://neo-pulse-hub.it.com/shipping.html")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="back")]
            ])
        )
    elif d == "returns":
        await q.edit_message_text(
            "🔄 *سياسة الإرجاع*\n\n• إرجاع مجاني خلال 30 يوم\n• استرداد كامل خلال 3-5 أيام",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📄 سياسة الإرجاع", url="https://neo-pulse-hub.it.com/returns.html")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="back")]
            ])
        )
    elif d == "contact":
        await q.edit_message_text(
            "📞 *تواصل معنا*\n\n• تيليجرام: @NeoPulseSupport\n• إيميل: Saidchaik@gmail.com\n• الأحد-الخميس 9ص-9م",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✈️ تواصل عبر تيليجرام", url="https://t.me/NeoPulseSupport")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="back")]
            ])
        )
    elif d == "back":
        name = update.effective_user.first_name or "عزيزنا"
        await q.edit_message_text(
            f"👋 أهلاً *{name}*! كيف يمكنني مساعدتك؟",
            parse_mode=ParseMode.MARKDOWN, reply_markup=kb_main()
        )

async def error_handler(update, ctx: ContextTypes.DEFAULT_TYPE):
    log.error(f"Error: {ctx.error}")

# ✅ هذه الدالة يستدعيها main.py
def _register_handlers(app):
    app.add_handler(CommandHandler("start",    cmd_start))
    app.add_handler(CommandHandler("products", cmd_products))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

if __name__ == "__main__":
    if not CUSTOMER_BOT_TOKEN:
        print("❌ CUSTOMER_BOT_TOKEN missing!"); exit(1)
    app = Application.builder().token(CUSTOMER_BOT_TOKEN).build()
    _register_handlers(app)
    print("🤖 Customer Bot running...")
    app.run_polling(drop_pending_updates=True)
