#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO PULSE HUB — Recommendation Bot v2.0
✅ RECO_BOT_TOKEN (صح)
✅ _register_handlers (للـ webhook)
✅ توصيات AI بـ Gemini
✅ فلترة بالميزانية والفئة
"""
import os, json, logging
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Application, CommandHandler, MessageHandler,
                           CallbackQueryHandler, filters, ContextTypes)
from telegram.constants import ParseMode, ChatAction

try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass

RECO_BOT_TOKEN = os.environ.get("RECO_BOT_TOKEN", "")
GEMINI_API_KEY  = (os.environ.get("GEMINI_API_KEY") or
                   os.environ.get("GOOGLE_API_KEY") or "")
BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
PRODUCTS_FILE  = os.path.join(BASE_DIR, "products.json")
LEADS_FILE     = os.path.join(BASE_DIR, "leads.json")

log = logging.getLogger("recommendation_bot")

_user_state = {}  # {uid: {"budget": None, "category": None, "step": "start"}}

def load_products():
    try:
        p = Path(PRODUCTS_FILE)
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []
    except:
        return []

def save_lead(uid, prefs):
    try:
        p = Path(LEADS_FILE)
        data = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"users": []}
        for u in data.get("users", []):
            if int(u.get("id", 0)) == uid:
                u["preferences"] = prefs
                p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
                return
    except:
        pass

def ask_gemini(prompt: str) -> str:
    if not GEMINI_API_KEY:
        return None
    import requests as _r
    try:
        url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
               f"gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}")
        body = {"contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.8, "maxOutputTokens": 600}}
        data = _r.post(url, json=body, timeout=15).json()
        return (data.get("candidates", [{}])[0]
                    .get("content", {}).get("parts", [{}])[0]
                    .get("text", None))
    except Exception as e:
        log.error(f"Gemini: {e}"); return None

def get_recommendations(budget=None, category=None, query=None):
    products = load_products()
    filtered = [p for p in products if p.get("active", True)]

    if budget:
        filtered = [p for p in filtered if p.get("price", 999) <= budget]
    if category and category != "all":
        filtered = [p for p in filtered if p.get("category") == category]
    if query:
        q = query.lower()
        filtered = [p for p in filtered
                    if q in (p.get("name_ar","") + p.get("name_en","") +
                             p.get("description_ar","")).lower()]

    return sorted(filtered, key=lambda x: (x.get("rating",0) * 0.6 +
                                            (x.get("discount",0)/100) * 0.4), reverse=True)[:5]

def format_products(products, lang="ar"):
    if not products:
        return "😔 لم أجد منتجات تناسب معاييرك."
    lines = []
    for i, p in enumerate(products, 1):
        name  = p.get("name_ar", "")
        price = p.get("price", 0)
        orig  = p.get("original_price", 0)
        disc  = p.get("discount", 0)
        rat   = p.get("rating", 0)
        pid   = p.get("id", "")
        url   = f"https://neo-pulse-hub.it.com/product-detail.html?id={pid}"
        discount_txt = f" | 🔥 خصم {disc}%" if disc else ""
        orig_txt     = f" ~~${orig}~~" if orig else ""
        lines.append(
            f"{i}. *{name}*\n"
            f"   💰 ${price}{orig_txt}{discount_txt}\n"
            f"   ⭐ {rat}/5 | [عرض المنتج]({url})"
        )
    return "\n\n".join(lines)

def kb_categories():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⌚ ساعات ذكية",  callback_data="cat_smartwatch"),
         InlineKeyboardButton("🕶️ نظارات AR",   callback_data="cat_smart-glasses")],
        [InlineKeyboardButton("💪 صحة ولياقة", callback_data="cat_health"),
         InlineKeyboardButton("🏠 منزل ذكي",   callback_data="cat_smart-home")],
        [InlineKeyboardButton("🎧 سماعات",      callback_data="cat_earbuds"),
         InlineKeyboardButton("💼 إنتاجية",     callback_data="cat_productivity")],
        [InlineKeyboardButton("🌟 الكل",        callback_data="cat_all")]
    ])

def kb_budget():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("تحت $100",  callback_data="bud_100"),
         InlineKeyboardButton("تحت $200",  callback_data="bud_200")],
        [InlineKeyboardButton("تحت $300",  callback_data="bud_300"),
         InlineKeyboardButton("تحت $500",  callback_data="bud_500")],
        [InlineKeyboardButton("أي ميزانية", callback_data="bud_0")]
    ])

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    _user_state[uid] = {"step": "category"}
    await update.message.reply_text(
        "🛍️ *مرحباً في نظام التوصيات الذكي!*\n\n"
        "سأساعدك في اختيار المنتج المثالي.\n\n"
        "أولاً: ما الفئة التي تهمك؟",
        parse_mode=ParseMode.MARKDOWN, reply_markup=kb_categories()
    )

async def cmd_recommend(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await cmd_start(update, ctx)

async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid  = update.effective_user.id
    text = update.message.text.strip()

    await update.message.chat.send_action(ChatAction.TYPING)

    state = _user_state.get(uid, {})
    budget   = state.get("budget")
    category = state.get("category")

    # بحث مباشر بـ AI
    products = get_recommendations(budget=budget, category=category, query=text)

    if products and GEMINI_API_KEY:
        prod_summary = "\n".join([
            f"- {p.get('name_ar','')} | ${p.get('price',0)} | ⭐{p.get('rating',0)}"
            for p in products
        ])
        prompt = f"""أنت مستشار تسوق ذكي لمتجر NEO PULSE HUB.
طلب العميل: {text}
الميزانية: {f'تحت ${budget}' if budget else 'غير محددة'}
الفئة: {category or 'كل الفئات'}

المنتجات المتاحة:
{prod_summary}

اكتب توصية شخصية ودودة ومختصرة (3 جمل) لهذه المنتجات. اذكر أبرز ميزة لكل منتج."""
        ai_note = ask_gemini(prompt)
    else:
        ai_note = None

    msg = format_products(products)
    if ai_note:
        msg = f"🤖 *رأي المساعد الذكي:*\n{ai_note}\n\n━━━━━━━━━━━━━━\n\n{msg}"

    await update.message.reply_text(
        msg, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 بحث جديد", callback_data="restart")],
            [InlineKeyboardButton("🛍️ تصفح الكل", url="https://neo-pulse-hub.it.com/products.html")]
        ])
    )

async def handle_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q   = update.callback_query
    await q.answer()
    d   = q.data
    uid = update.effective_user.id

    if d.startswith("cat_"):
        cat = d[4:]
        _user_state[uid] = {"step": "budget", "category": cat if cat != "all" else None}
        cat_name = {
            "smartwatch": "ساعات ذكية", "smart-glasses": "نظارات AR",
            "health": "صحة ولياقة", "smart-home": "منزل ذكي",
            "earbuds": "سماعات", "productivity": "إنتاجية", "all": "الكل"
        }.get(cat, cat)
        await q.edit_message_text(
            f"✅ اخترت: *{cat_name}*\n\nما هي ميزانيتك؟",
            parse_mode=ParseMode.MARKDOWN, reply_markup=kb_budget()
        )

    elif d.startswith("bud_"):
        budget = int(d[4:]) or None
        state  = _user_state.get(uid, {})
        state["budget"] = budget
        state["step"]   = "results"
        _user_state[uid] = state

        category = state.get("category")
        products = get_recommendations(budget=budget, category=category)

        ai_note = None
        if products and GEMINI_API_KEY:
            prod_summary = "\n".join([
                f"- {p.get('name_ar','')} | ${p.get('price',0)} | ⭐{p.get('rating',0)}"
                for p in products
            ])
            prompt = f"""أنت مستشار تسوق لمتجر NEO PULSE HUB.
الفئة: {category or 'كل الفئات'} | الميزانية: {f'تحت ${budget}' if budget else 'مفتوحة'}
المنتجات:
{prod_summary}
اكتب توصية شخصية مختصرة وجذابة (جملتان) لهذه المنتجات بالعربية."""
            ai_note = ask_gemini(prompt)

        msg = format_products(products)
        if ai_note:
            msg = f"🤖 *{ai_note}*\n\n━━━━━━━━━━━━━━\n\n{msg}"

        await q.edit_message_text(
            f"🌟 *أفضل التوصيات لك:*\n\n{msg}",
            parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔍 بحث جديد", callback_data="restart")],
                [InlineKeyboardButton("🛍️ تصفح الكل", url="https://neo-pulse-hub.it.com/products.html")]
            ])
        )
        save_lead(uid, {"budget": budget, "category": category})

    elif d == "restart":
        _user_state[uid] = {"step": "category"}
        await q.edit_message_text(
            "🔍 *بحث جديد*\n\nاختر الفئة:",
            parse_mode=ParseMode.MARKDOWN, reply_markup=kb_categories()
        )

async def error_handler(update, ctx: ContextTypes.DEFAULT_TYPE):
    log.error(f"Reco bot error: {ctx.error}")

# ✅ يُستدعى من main.py
def _register_handlers(app):
    app.add_handler(CommandHandler("start",     cmd_start))
    app.add_handler(CommandHandler("recommend", cmd_recommend))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

if __name__ == "__main__":
    if not RECO_BOT_TOKEN:
        print("❌ RECO_BOT_TOKEN missing!"); exit(1)
    app = Application.builder().token(RECO_BOT_TOKEN).build()
    _register_handlers(app)
    print("🛍️ Recommendation Bot running...")
    app.run_polling(drop_pending_updates=True)
