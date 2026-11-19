#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NEO PULSE HUB - Customer Bot v3.2
v3.2: fix name:{ar,en} crash in /products; plain-text fallback when
Markdown fails; friendly fallback when AI providers fail."""
import os, json, logging
from datetime import datetime
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Application, CommandHandler, MessageHandler,
                           CallbackQueryHandler, filters)
from telegram.constants import ParseMode, ChatAction

try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass

TOKEN = os.environ.get("CUSTOMER_BOT_TOKEN", "")
SITE_URL = os.environ.get("SITE_URL", "https://neo-pulse-hub.it.com")
BASE = os.path.dirname(os.path.abspath(__file__))
PRODUCTS_FILE = os.path.join(BASE, "products.json")
LEADS_FILE = os.path.join(BASE, "leads.json")
log = logging.getLogger("customer_bot")
_histories = {}

def add_history(uid, role, text):
    h = _histories.setdefault(uid, [])
    h.append({"role": role, "text": text[:400]})
    if len(h) > 8: h.pop(0)

def load_json(path, default):
    try:
        p = Path(path)
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default
    except Exception:
        return default

def save_json(path, data):
    try:
        Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        log.error(f"save_json: {e}")

def load_products():
    return load_json(PRODUCTS_FILE, [])

def product_name(p):
    name = p.get("name", {})
    if isinstance(name, dict):
        return name.get("ar") or name.get("en") or "منتج"
    return str(name or p.get("name_ar", "") or p.get("name_en", "") or "منتج")

def upsert_lead(u):
    data = load_json(LEADS_FILE, {"total_users": 0, "users": [], "support_chats": 0})
    for x in data["users"]:
        if int(x["id"]) == u.id:
            x["last_seen"] = datetime.now().isoformat()
            x["chats"] = x.get("chats", 0) + 1
            save_json(LEADS_FILE, data); return
    data["users"].append({"id": u.id, "username": u.username or "",
        "name": u.full_name or "", "joined": datetime.now().isoformat(),
        "last_seen": datetime.now().isoformat(), "chats": 1})
    data["total_users"] = len(data["users"])
    save_json(LEADS_FILE, data)

def ask_ai(prompt):
    groq_key = os.environ.get("GROQ_API_KEY", "")
    if groq_key and groq_key != "YOUR_API_KEY_HERE":
        try:
            import groq
            c = groq.Groq(api_key=groq_key)
            r = c.chat.completions.create(model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7, max_tokens=1500)
            return r.choices[0].message.content
        except Exception as e:
            log.warning(f"Groq error: {e}")
    gkey = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
    if not gkey:
        return ""
    import requests
    url = ("https://generativelanguage.googleapis.com/v1beta/models/"
           "gemini-2.5-flash:generateContent?key=" + gkey)
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1500,
                                 "thinkingConfig": {"thinkingBudget": 0}}}
    try:
        r = requests.post(url, json=body, timeout=30)
        if r.status_code != 200:
            log.error(f"Gemini HTTP {r.status_code}"); return ""
        cand = r.json().get("candidates", [])
        if not cand: return ""
        parts = cand[0].get("content", {}).get("parts", [])
        return parts[0].get("text", "") if parts else ""
    except Exception as e:
        log.error(f"Gemini exception: {e}"); return ""

def build_prompt(user_msg, uid):
    products = load_products()
    kws = user_msg.lower().split()
    relevant = [p for p in products
                if any(k in (product_name(p) + " " + str(p.get("category", ""))).lower()
                       for k in kws)]
    if not relevant:
        relevant = sorted(products, key=lambda x: x.get("rating", 0), reverse=True)[:6]
    prod_lines = "\n".join([
        "- " + product_name(p) + " | $" + str(p.get("price", 0)) +
        " | " + SITE_URL + "/product-detail.html?id=" + str(p.get("id", ""))
        for p in relevant[:6]])
    hist = "\n".join([h["role"] + ": " + h["text"] for h in _histories.get(uid, [])])
    return ("أنت مساعد خدمة عملاء لمتجر NEO PULSE HUB للأجهزة الذكية.\n"
            "المتجر: " + SITE_URL + "\n"
            "الشحن: 3-7 أيام | الإرجاع: 30 يوم مجاناً\n"
            "المنتجات المتاحة:\n" + prod_lines + "\n\n"
            "سجل المحادثة:\n" + (hist if hist else "بداية") + "\n\n"
            "سؤال العميل: " + user_msg + "\n\n"
            "أجب بالعربية بأسلوب ودود ومختصر (3-4 جمل) بدون رموز Markdown. "
            "إذا سأل عن منتج اذكر السعر ورابطه.")

def kb_main():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍️ تصفح المنتجات", url=SITE_URL + "/products.html")],
        [InlineKeyboardButton("📦 تتبع طلب", callback_data="track"),
         InlineKeyboardButton("🚚 الشحن", callback_data="shipping")],
        [InlineKeyboardButton("🔄 الإرجاع", callback_data="returns"),
         InlineKeyboardButton("📞 تواصل", callback_data="contact")]])

async def safe_reply(msg_obj, text):
    if not text:
        text = "عذراً، خلل مؤقت في الرد الذكي. جرب إعادة السؤال أو اكتب /start"
    try:
        await msg_obj.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        log.warning(f"Markdown failed ({e}) - plain fallback")
        try:
            await msg_obj.reply_text(text)
        except Exception as e2:
            log.error(f"plain reply failed: {e2}")

async def cmd_start(update, ctx):
    upsert_lead(update.effective_user)
    _histories.pop(update.effective_user.id, None)
    name = update.effective_user.first_name or "عزيزنا"
    await update.message.reply_text(
        "👋 أهلاً *" + name + "*!\n\nأنا مساعد *NEO PULSE HUB* الذكي 🤖\n\n"
        "• 🛍️ اختيار المنتج المناسب\n• 📦 تتبع طلبك\n"
        "• 💳 الدفع والشحن\n• 🔄 سياسة الإرجاع\n\nاكتب سؤالك وسأجيبك فوراً! 💬",
        parse_mode=ParseMode.MARKDOWN, reply_markup=kb_main())

async def cmd_products(update, ctx):
    products = load_products()
    featured = sorted(products, key=lambda x: x.get("rating", 0), reverse=True)[:5]
    lines = "\n".join([
        "• *" + product_name(p) + "* — $" + str(p.get("price", 0)) +
        "\n  [عرض المنتج](" + SITE_URL + "/product-detail.html?id=" + str(p.get("id", "")) + ")"
        for p in featured])
    await update.message.reply_text(
        "🌟 *أبرز منتجاتنا:*\n\n" + lines + "\n\n[← تصفح الكل](" + SITE_URL + "/products.html)",
        parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

async def handle_message(update, ctx):
    upsert_lead(update.effective_user)
    text = update.message.text.strip()
    uid = update.effective_user.id
    if len(text) < 2: return
    await update.message.chat.send_action(ChatAction.TYPING)
    answer = ""
    try:
        from ai_orchestrator import customer_reply
        history = "\n".join([h["role"] + ": " + h["text"] for h in _histories.get(uid, [])])
        answer = customer_reply(text, history=history, products=load_products())
    except Exception as e:
        log.error(f"orchestrator error: {e}")
        answer = ask_ai(build_prompt(text, uid))
    if not answer:
        answer = ("عذراً، تواجهني صعوبة مؤقتة. جرّب صياغة سؤالك بشكل آخر، "
                  "أو تصفح منتجاتنا:\n" + SITE_URL + "/products.html")
    add_history(uid, "user", text)
    add_history(uid, "assistant", answer)
    await safe_reply(update.message, answer)

PAGES = {
    "track": ("📦 *تتبع طلبك*\n\nأرسل رقم طلبك أو تتبع من الموقع مباشرة:",
               "track.html", "🔍 تتبع الطلب"),
    "shipping": ("🚚 *الشحن والدفع*\n\n• الشحن: 3-7 أيام عمل\n• مجاني فوق $200\n• الدفع: PayPal آمن 100%",
                 "shipping.html", "📄 سياسة الشحن"),
    "returns": ("🔄 *سياسة الإرجاع*\n\n• إرجاع مجاني خلال 30 يوم\n• استرداد كامل خلال 3-5 أيام",
                 "returns.html", "📄 سياسة الإرجاع"),
    "contact": ("📞 *تواصل معنا*\n\n• تيليجرام: @NeoPulseSupport\n• إيميل: Saidchaik@gmail.com",
                 None, "✈️ تواصل عبر تيليجرام"),
}

async def handle_callback(update, ctx):
    q = update.callback_query
    await q.answer()
    d = q.data
    if d in PAGES:
        msg, path, label = PAGES[d]
        url = ("https://t.me/NeoPulseSupport" if d == "contact"
               else SITE_URL + "/" + path)
        await q.edit_message_text(msg, parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(label, url=url)],
                [InlineKeyboardButton("🔙 رجوع", callback_data="back")]]))
    elif d == "back":
        name = update.effective_user.first_name or "عزيزنا"
        await q.edit_message_text("👋 أهلاً *" + name + "*! كيف يمكنني مساعدتك؟",
            parse_mode=ParseMode.MARKDOWN, reply_markup=kb_main())

async def error_handler(update, ctx):
    log.error(f"Error: {ctx.error}")

def _register_handlers(app):
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("products", cmd_products))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

if __name__ == "__main__":
    if not TOKEN:
        print("CUSTOMER_BOT_TOKEN missing!"); exit(1)
    app = Application.builder().token(TOKEN).build()
    _register_handlers(app)
    print("Customer Bot v3.2 running...")
    app.run_polling(drop_pending_updates=True)
