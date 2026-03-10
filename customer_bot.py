#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════╗
║   BOT 1: بوت خدمة العملاء الذكي v2.0                          ║
║   @NeoPulseBot — Customer Service                               ║
║                                                                  ║
║   الوظائف:                                                      ║
║   ✅ إجابة أسئلة الزبائن بـ Gemini AI                          ║
║   ✅ سلة تسوق دائمة                                             ║
║   ✅ تتبع الطلبات                                               ║
║   ✅ نقل للدفع PayPal                                           ║
║   ✅ حفظ المحادثات                                              ║
║   ✅ إشعار للأدمين عند مشاكل حرجة                              ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os, logging, asyncio
from datetime import datetime
from telegram import (Update, InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup, KeyboardButton)
from telegram.ext import (Application, CommandHandler, MessageHandler,
                           CallbackQueryHandler, filters, ContextTypes)
from telegram.constants import ParseMode, ChatAction

try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass

import sys; sys.path.insert(0, os.path.dirname(__file__))
from shared_db import (upsert_user, update_user, get_user,
                        get_products, get_product, get_featured_products,
                        search_products, get_products_by_category,
                        add_to_cart, get_user_cart, save_user_cart,
                        get_cart_total, clear_cart,
                        create_order, get_orders_by_user,
                        get_faqs, subscribe_email,
                        track_event, add_review, init_db)
from ai_engine import (answer_customer, recommend_products, extract_budget,
                        categorize_query, analyze_sentiment, is_purchase_intent,
                        continue_conversation, summarize_conversation)

# ── Config ─────────────────────────────────────────────────────────
TOKEN        = os.environ.get("CUSTOMER_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN","")
ADMIN_ID     = int(os.environ.get("ADMIN_USER_ID", "0"))
PAYPAL_EMAIL = os.environ.get("PAYPAL_EMAIL", "Saidchaik@gmail.com")
SITE_URL     = os.environ.get("SITE_URL", "https://neo-pulse-hub.it.com")
CURRENCY     = "USD"

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(), logging.FileHandler("customer_bot.log", encoding="utf-8")]
)
log = logging.getLogger("customer_bot")

# ── Per-user conversation history (RAM cache) ─────────────────────
_conv_history: dict = {}   # {user_id: [{"role":..,"content":..}]}
_awaiting:     dict = {}   # {user_id: "state"}

def get_history(uid: int) -> list:
    return _conv_history.setdefault(uid, [])

def add_to_history(uid: int, role: str, content: str):
    h = get_history(uid)
    h.append({"role": role, "content": content})
    if len(h) > 20: _conv_history[uid] = h[-20:]

# ══════════════════════════════════════════════════════════════════
# KEYBOARDS
# ══════════════════════════════════════════════════════════════════

def kb_main():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍️ تصفح المنتجات",  callback_data="browse"),
         InlineKeyboardButton("🛒 سلتي",            callback_data="my_cart")],
        [InlineKeyboardButton("📦 طلباتي",           callback_data="my_orders"),
         InlineKeyboardButton("🔍 بحث عن منتج",      callback_data="search")],
        [InlineKeyboardButton("❓ أسئلة شائعة",       callback_data="faqs"),
         InlineKeyboardButton("⭐ أضف تقييم",         callback_data="add_review")],
        [InlineKeyboardButton("🤖 تحدث مع AI",       callback_data="ai_chat")],
    ])

def kb_categories():
    cats = [
        ("⌚ ساعات ذكية",      "cat_smartwatch"),
        ("🥽 نظارات ذكية",     "cat_smart-glasses"),
        ("❤️ الصحة الذكية",    "cat_health"),
        ("🏠 المنزل الذكي",    "cat_smart-home"),
        ("🎧 سماعات ذكية",     "cat_earbuds"),
        ("💼 الإنتاجية",       "cat_productivity"),
    ]
    buttons = [[InlineKeyboardButton(n, callback_data=d)] for n,d in cats]
    buttons.append([InlineKeyboardButton("🔙 رجوع", callback_data="back_main")])
    return InlineKeyboardMarkup(buttons)

def kb_product(product: dict, show_back: str = "browse"):
    paypal_url = _paypal_link(product)
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🛒 أضف للسلة",      callback_data=f"add_{product['id']}")],
        [InlineKeyboardButton(f"💳 اشتر ${product['price']}", url=paypal_url)],
        [InlineKeyboardButton("📊 تقرير AI",         callback_data=f"report_{product['id']}"),
         InlineKeyboardButton("⭐ قيّم",              callback_data=f"review_{product['id']}")],
        [InlineKeyboardButton("🔙 رجوع",             callback_data=show_back)],
    ])

def kb_cart(user_id: int):
    cart  = get_user_cart(user_id)
    total = get_cart_total(user_id)
    btns  = []
    for item in cart:
        btns.append([
            InlineKeyboardButton(f"➖", callback_data=f"rmv_{item['product_id']}"),
            InlineKeyboardButton(f"{item['name_ar'][:20]} x{item.get('qty',1)}", callback_data="noop"),
            InlineKeyboardButton(f"➕", callback_data=f"plus_{item['product_id']}"),
        ])
    if cart:
        btns.append([InlineKeyboardButton(f"💳 ادفع ${total} عبر PayPal", callback_data="checkout")])
        btns.append([InlineKeyboardButton("🗑️ إفراغ السلة", callback_data="clear_cart")])
    btns.append([InlineKeyboardButton("🔙 رجوع", callback_data="back_main")])
    return InlineKeyboardMarkup(btns)

def _paypal_link(product: dict, qty: int = 1) -> str:
    from urllib.parse import urlencode
    total = round(product["price"] * qty, 2)
    params = urlencode({
        "cmd": "_xclick", "business": PAYPAL_EMAIL,
        "item_name": product.get("name_ar","")[:127],
        "item_number": product["id"],
        "amount": str(total), "currency_code": CURRENCY,
        "return": f"{SITE_URL}/thanks.html?id={product['id']}&total={total}",
        "cancel_return": f"{SITE_URL}/products.html",
        "no_note":"1", "no_shipping":"2",
    })
    return f"https://www.paypal.com/cgi-bin/webscr?{params}"

def _checkout_paypal_multi(cart: list) -> str:
    from urllib.parse import urlencode
    total = round(sum(i["price"]*i.get("qty",1) for i in cart), 2)
    desc  = ", ".join([f"{i['name_ar']} x{i.get('qty',1)}" for i in cart])[:127]
    params = urlencode({
        "cmd":"_xclick","business":PAYPAL_EMAIL,
        "item_name":desc,"amount":str(total),"currency_code":CURRENCY,
        "return":f"{SITE_URL}/thanks.html?total={total}",
        "cancel_return":f"{SITE_URL}/products.html",
        "no_note":"1","no_shipping":"2",
    })
    return f"https://www.paypal.com/cgi-bin/webscr?{params}"

# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════

def products_context_str(limit=10) -> str:
    ps = get_featured_products(limit)
    return "\n".join([
        f"• {p.get('name_ar','')} | ${p['price']} | {p.get('category','')} | تقييم {p.get('rating',0)}"
        for p in ps
    ])

def faqs_context_str() -> str:
    faqs = get_faqs()
    if not faqs: return ""
    lines = []
    for f in faqs[:10]:
        if isinstance(f, dict):
            lines.append(f"س: {f.get('question','')}\nج: {f.get('answer','')}")
        elif isinstance(f, list) and len(f) >= 2:
            lines.append(f"س: {f[0]}\nج: {f[1]}")
    return "\n\n".join(lines)

def product_card_text(p: dict) -> str:
    features = "\n".join([f"  ✦ {f}" for f in p.get("features_ar",[])[:4]])
    discount  = f" (خصم {p['discount']}%)" if p.get("discount") else ""
    return (
        f"🛍️ *{p.get('name_ar','')}*\n"
        f"_{p.get('category_ar','')} • {p.get('brand','')} _\n\n"
        f"💰 السعر: *${p['price']}*{discount}\n"
        f"⭐ التقييم: {p.get('rating',0)}/5 ({p.get('reviews',0)} تقييم)\n"
        f"📦 المخزون: {p.get('stock',0)} وحدة\n"
        f"🚚 الشحن: {p.get('shipping_days','7-14')} يوم\n\n"
        f"🔑 *المميزات:*\n{features}\n\n"
        f"📝 {p.get('description_ar','')}"
    )

async def notify_admin(bot, message: str):
    if ADMIN_ID:
        try:
            await bot.send_message(chat_id=ADMIN_ID, text=f"🔔 {message}", parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            log.error(f"Admin notify failed: {e}")

# ══════════════════════════════════════════════════════════════════
# HANDLERS
# ══════════════════════════════════════════════════════════════════

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    upsert_user(user)
    track_event("bot_start", {"user_id": user.id})
    name = user.first_name or "صديقي"
    text = (
        f"🤖 أهلاً *{name}*!\n\n"
        f"مرحباً في *NEO PULSE HUB*\n"
        f"متجرك للمنتجات الذكية والذكاء الاصطناعي 🚀\n\n"
        f"يمكنني مساعدتك في:\n"
        f"• تصفح وشراء المنتجات\n"
        f"• الإجابة على أسئلتك\n"
        f"• تتبع طلباتك\n"
        f"• توصيات مخصصة بالـ AI\n\n"
        f"ماذا تحتاج؟ 👇"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb_main())

async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *الأوامر المتاحة:*\n\n"
        "/start — الصفحة الرئيسية\n"
        "/products — جميع المنتجات\n"
        "/cart — سلة التسوق\n"
        "/orders — طلباتي\n"
        "/search [اسم المنتج] — بحث\n"
        "/recommend [وصفك] — توصية AI\n"
        "/help — هذه الرسالة",
        parse_mode=ParseMode.MARKDOWN
    )

async def cmd_products(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛍️ *اختر الفئة:*", parse_mode=ParseMode.MARKDOWN,
        reply_markup=kb_categories()
    )

async def cmd_cart(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid   = update.effective_user.id
    cart  = get_user_cart(uid)
    total = get_cart_total(uid)
    if not cart:
        return await update.message.reply_text(
            "🛒 *سلتك فارغة!*\n\nتصفح المنتجات وأضف ما يعجبك.",
            parse_mode=ParseMode.MARKDOWN, reply_markup=kb_main()
        )
    items_text = "\n".join([
        f"• {i['name_ar']} × {i.get('qty',1)} = *${i['price']*i.get('qty',1):.2f}*"
        for i in cart
    ])
    await update.message.reply_text(
        f"🛒 *سلة التسوق*\n\n{items_text}\n\n💰 *الإجمالي: ${total}*",
        parse_mode=ParseMode.MARKDOWN, reply_markup=kb_cart(uid)
    )

async def cmd_orders(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid    = update.effective_user.id
    orders = get_orders_by_user(uid)
    if not orders:
        return await update.message.reply_text("📦 لا توجد طلبات بعد.")
    text = "📦 *طلباتك:*\n\n"
    for o in orders[-5:]:
        status_map = {"pending_payment":"⏳ انتظار الدفع","paid":"✅ مدفوع",
                      "shipped":"🚚 مشحون","delivered":"📬 تم التوصيل","cancelled":"❌ ملغي"}
        text += (f"`{o['id']}` — {o['product_name']}\n"
                 f"💰 ${o['total']} | {status_map.get(o['status'],o['status'])}\n"
                 f"📅 {o['created_at'][:10]}\n\n")
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def cmd_search(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if ctx.args:
        query    = " ".join(ctx.args)
        products = search_products(query)
        await _send_product_list(update, products, query)
    else:
        _awaiting[update.effective_user.id] = "search"
        await update.message.reply_text(
            "🔍 *اكتب اسم المنتج أو وصفه:*",
            parse_mode=ParseMode.MARKDOWN
        )

async def cmd_recommend(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if ctx.args:
        query = " ".join(ctx.args)
        await _do_recommend(update, ctx, query)
    else:
        _awaiting[update.effective_user.id] = "recommend"
        await update.message.reply_text(
            "💡 *صف ما تحتاجه وسأوصي لك:*\n\n"
            "مثال: _ساعة لرياضي ميزانيتي 200 دولار_",
            parse_mode=ParseMode.MARKDOWN
        )

# ── Main message handler ───────────────────────────────────────────
async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text.strip()
    uid  = user.id

    upsert_user(user)
    track_event("message", {"user_id": uid, "length": len(text)})

    # Handle awaiting states
    state = _awaiting.pop(uid, None)
    if state == "search":
        products = search_products(text)
        return await _send_product_list(update, products, text)
    if state == "recommend":
        return await _do_recommend(update, ctx, text)
    if state and state.startswith("review_"):
        return await _handle_review_text(update, ctx, state.replace("review_",""), text)
    if state == "email_subscribe":
        ok = subscribe_email(text, uid)
        return await update.message.reply_text(
            "✅ تم الاشتراك!" if ok else "ℹ️ أنت مشترك مسبقاً.",
            reply_markup=kb_main()
        )

    # Detect intent
    await update.message.chat.send_action(ChatAction.TYPING)
    sentiment = analyze_sentiment(text)
    category  = categorize_query(text)

    # Alert admin on complaints
    if sentiment == "negative" or category == "شكوى":
        await notify_admin(ctx.bot,
            f"⚠️ *شكوى من مستخدم*\n"
            f"المستخدم: {user.full_name} (@{user.username or 'N/A'})\n"
            f"الرسالة: {text[:200]}")

    # Purchase intent → show products
    if is_purchase_intent(text) or category == "توصية":
        return await _do_recommend(update, ctx, text)

    # AI conversation
    add_to_history(uid, "user", text)
    context = products_context_str(6) + "\n\n" + faqs_context_str()
    response = continue_conversation(get_history(uid), text, context)
    add_to_history(uid, "assistant", response)

    await update.message.reply_text(
        response, parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🛍️ تصفح المنتجات", callback_data="browse"),
             InlineKeyboardButton("🏠 الرئيسية",        callback_data="back_main")]
        ])
    )

# ══════════════════════════════════════════════════════════════════
# CALLBACK HANDLERS
# ══════════════════════════════════════════════════════════════════

async def handle_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid  = query.from_user.id
    d    = query.data

    upsert_user(query.from_user)

    if d == "noop":
        return

    elif d == "back_main":
        await query.edit_message_text(
            "🤖 *NEO PULSE HUB*\nماذا تحتاج؟",
            parse_mode=ParseMode.MARKDOWN, reply_markup=kb_main()
        )

    elif d == "browse":
        await query.edit_message_text(
            "🛍️ *اختر الفئة:*", parse_mode=ParseMode.MARKDOWN,
            reply_markup=kb_categories()
        )

    elif d.startswith("cat_"):
        cat      = d.replace("cat_", "")
        products = get_products_by_category(cat)
        if not products:
            return await query.edit_message_text(
                "❌ لا توجد منتجات في هذه الفئة حالياً.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="browse")]]))
        buttons = []
        for p in products[:8]:
            buttons.append([InlineKeyboardButton(
                f"{p.get('name_ar','')} — ${p['price']}",
                callback_data=f"view_{p['id']}"
            )])
        buttons.append([InlineKeyboardButton("🔙 رجوع", callback_data="browse")])
        await query.edit_message_text(
            f"🛍️ *{products[0].get('category_ar','المنتجات')}*\nاختر منتجاً:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif d.startswith("view_"):
        pid = d.replace("view_","")
        p   = get_product(pid)
        if not p:
            return await query.answer("المنتج غير موجود", show_alert=True)
        track_product_view = track_event
        track_product_view("product_view", {"product_id": pid, "user_id": uid})
        text = product_card_text(p)
        try:
            if p.get("image"):
                await ctx.bot.send_photo(
                    chat_id=query.message.chat_id,
                    photo=p["image"], caption=text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=kb_product(p)
                )
                await query.delete_message()
            else:
                await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN,
                                               reply_markup=kb_product(p))
        except:
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN,
                                           reply_markup=kb_product(p))

    elif d.startswith("add_"):
        pid  = d.replace("add_","")
        cart = add_to_cart(uid, pid)
        p    = get_product(pid)
        name = p.get("name_ar","المنتج") if p else "المنتج"
        total = get_cart_total(uid)
        await query.answer(f"✅ أُضيف: {name}")
        # Update cart button in message
        try:
            await query.edit_message_reply_markup(reply_markup=kb_product(p))
        except: pass

    elif d.startswith("plus_") or d.startswith("rmv_"):
        pid   = d.split("_",1)[1]
        cart  = get_user_cart(uid)
        item  = next((i for i in cart if i["product_id"]==pid), None)
        if item:
            if d.startswith("plus_"):
                item["qty"] = item.get("qty",1) + 1
            else:
                item["qty"] = item.get("qty",1) - 1
                if item["qty"] <= 0:
                    cart = [i for i in cart if i["product_id"]!=pid]
            save_user_cart(uid, cart)
        total = get_cart_total(uid)
        if not get_user_cart(uid):
            return await query.edit_message_text("🛒 السلة فارغة.", reply_markup=kb_main())
        items_text = "\n".join([
            f"• {i['name_ar']} × {i.get('qty',1)} = *${i['price']*i.get('qty',1):.2f}*"
            for i in get_user_cart(uid)
        ])
        await query.edit_message_text(
            f"🛒 *السلة*\n\n{items_text}\n\n💰 *الإجمالي: ${total}*",
            parse_mode=ParseMode.MARKDOWN, reply_markup=kb_cart(uid)
        )

    elif d == "my_cart":
        cart  = get_user_cart(uid)
        total = get_cart_total(uid)
        if not cart:
            return await query.edit_message_text(
                "🛒 *سلتك فارغة!*", parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛍️ تسوق", callback_data="browse")]]))
        items_text = "\n".join([
            f"• {i['name_ar']} × {i.get('qty',1)} = *${i['price']*i.get('qty',1):.2f}*"
            for i in cart
        ])
        await query.edit_message_text(
            f"🛒 *سلة التسوق*\n\n{items_text}\n\n💰 *الإجمالي: ${total}*",
            parse_mode=ParseMode.MARKDOWN, reply_markup=kb_cart(uid)
        )

    elif d == "clear_cart":
        clear_cart(uid)
        await query.edit_message_text("🗑️ تم إفراغ السلة.", reply_markup=kb_main())

    elif d == "checkout":
        cart = get_user_cart(uid)
        if not cart:
            return await query.answer("السلة فارغة!", show_alert=True)
        total = get_cart_total(uid)
        url   = _checkout_paypal_multi(cart)
        # Log order
        try:
            for item in cart:
                create_order(item["product_id"], uid, item.get("qty",1), "paypal")
        except Exception as e:
            log.error(f"Order creation error: {e}")
        await query.edit_message_text(
            f"💳 *إتمام الدفع*\n\n"
            f"💰 الإجمالي: *${total}*\n"
            f"📧 PayPal: `{PAYPAL_EMAIL}`\n\n"
            f"اضغط الزر لإتمام الدفع على PayPal 👇",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"💳 ادفع ${total} عبر PayPal", url=url)],
                [InlineKeyboardButton("🔙 رجوع للسلة", callback_data="my_cart")]
            ])
        )
        await notify_admin(ctx.bot,
            f"🛒 *طلب جديد!*\n"
            f"المستخدم: {query.from_user.full_name}\n"
            f"الإجمالي: ${total}\n"
            f"المنتجات: {', '.join(i['name_ar'] for i in cart)}")

    elif d == "my_orders":
        orders = get_orders_by_user(uid)
        if not orders:
            return await query.edit_message_text(
                "📦 لا توجد طلبات بعد.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛍️ تسوق الآن", callback_data="browse")]]))
        text = "📦 *طلباتك الأخيرة:*\n\n"
        for o in orders[-5:]:
            status_icons = {"pending_payment":"⏳","paid":"✅","shipped":"🚚","delivered":"📬","cancelled":"❌"}
            icon = status_icons.get(o.get("status",""),"❓")
            text += f"{icon} `{o['id']}` — {o['product_name']} — *${o['total']}*\n"
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN,
                                       reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back_main")]]))

    elif d == "search":
        _awaiting[uid] = "search"
        await query.edit_message_text(
            "🔍 *اكتب اسم المنتج:*", parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء", callback_data="back_main")]]))

    elif d == "ai_chat":
        _awaiting[uid] = "ai_free"
        await query.edit_message_text(
            "🤖 *وضع المحادثة الحرة مع AI*\n\nاسألني أي شيء عن المنتجات أو التقنية الذكية!",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ إنهاء", callback_data="back_main")]]))

    elif d == "faqs":
        faqs = get_faqs()
        if not faqs:
            return await query.edit_message_text("❓ لا توجد أسئلة شائعة حالياً.",
                                                  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back_main")]]))
        text = "❓ *الأسئلة الشائعة:*\n\n"
        for f in faqs[:8]:
            if isinstance(f, dict):
                text += f"*س:* {f.get('question','')}\n*ج:* {f.get('answer','')}\n\n"
        await query.edit_message_text(text[:3000], parse_mode=ParseMode.MARKDOWN,
                                       reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back_main")]]))

    elif d == "add_review":
        _awaiting[uid] = "review_pick"
        orders = get_orders_by_user(uid)
        if not orders:
            return await query.edit_message_text("❌ يجب أن تكون قد اشتريت منتجاً أولاً.",
                                                  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="back_main")]]))
        bought = list({o["product_id"]: o for o in orders}.values())[:5]
        buttons = [[InlineKeyboardButton(o["product_name"], callback_data=f"to_review_{o['product_id']}")] for o in bought]
        buttons.append([InlineKeyboardButton("🔙 رجوع", callback_data="back_main")])
        await query.edit_message_text("⭐ *اختر المنتج للتقييم:*",
                                       parse_mode=ParseMode.MARKDOWN,
                                       reply_markup=InlineKeyboardMarkup(buttons))

    elif d.startswith("to_review_"):
        pid = d.replace("to_review_","")
        _awaiting[uid] = f"review_{pid}"
        await query.edit_message_text(
            "⭐ *أرسل تقييمك:*\n\nاكتب رقماً من 1-5 متبوعاً بتعليقك\n_مثال: 5 منتج ممتاز جداً!_",
            parse_mode=ParseMode.MARKDOWN)

    elif d.startswith("report_"):
        pid = d.replace("report_","")
        p   = get_product(pid)
        if not p:
            return await query.answer("المنتج غير موجود", show_alert=True)
        await query.edit_message_text("⏳ جاري توليد التقرير بالـ AI...", parse_mode=ParseMode.MARKDOWN)
        from ai_engine import generate_mini_report
        report = generate_mini_report(p)
        await query.edit_message_text(
            f"📊 *تقرير: {p.get('name_ar','')}*\n\n{report}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🛒 أضف للسلة", callback_data=f"add_{pid}")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="browse")]
            ])
        )

# ── Helpers ────────────────────────────────────────────────────────

async def _send_product_list(update: Update, products: list, query: str):
    if not products:
        await update.message.reply_text(
            f"❌ لم أجد منتجات لـ *{query}*\n\nجرب كلمات مختلفة.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛍️ تصفح الفئات", callback_data="browse")]]))
        return
    buttons = [[InlineKeyboardButton(
        f"{p.get('name_ar','')} — ${p['price']}",
        callback_data=f"view_{p['id']}"
    )] for p in products[:8]]
    buttons.append([InlineKeyboardButton("🔙 رجوع", callback_data="browse")])
    await update.message.reply_text(
        f"🔍 *نتائج البحث عن:* `{query}`\n\nوجدت *{len(products)}* منتج:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def _do_recommend(update: Update, ctx: ContextTypes.DEFAULT_TYPE, query: str):
    msg = update.message or (update.callback_query.message if update.callback_query else None)
    if not msg: return

    loading = await msg.reply_text("🤖 *أحلل طلبك وأختار أفضل المنتجات...*", parse_mode=ParseMode.MARKDOWN)
    await msg.chat.send_action(ChatAction.TYPING)

    products = get_products()
    budget   = extract_budget(query)
    if budget:
        products = [p for p in products if p.get("price",9999) <= budget * 1.2]

    rec_ids  = recommend_products(query, products, budget)
    recs     = [p for pid in rec_ids for p in [get_product(pid)] if p]

    if not recs:
        recs = get_featured_products(3)

    await loading.delete()

    for p in recs[:3]:
        text = product_card_text(p)
        try:
            if p.get("image"):
                await msg.reply_photo(photo=p["image"], caption=text,
                                       parse_mode=ParseMode.MARKDOWN,
                                       reply_markup=kb_product(p))
            else:
                await msg.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb_product(p))
        except:
            await msg.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb_product(p))

async def _handle_review_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE,
                                product_id: str, text: str):
    uid  = update.effective_user.id
    parts = text.strip().split(None, 1)
    try:
        rating  = int(parts[0])
        comment = parts[1] if len(parts) > 1 else ""
        if not 1 <= rating <= 5:
            raise ValueError()
    except:
        _awaiting[uid] = f"review_{product_id}"
        return await update.message.reply_text("❌ أرسل رقماً من 1-5 متبوعاً بتعليق. مثال: _5 منتج رائع!_",
                                                parse_mode=ParseMode.MARKDOWN)
    add_review(product_id, uid, rating, comment)
    await update.message.reply_text(
        f"✅ *شكراً على تقييمك!* {'⭐'*rating}\n_{comment}_",
        parse_mode=ParseMode.MARKDOWN, reply_markup=kb_main()
    )

# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

def _register_handlers(app):
    """يُستخدم في Webhook mode"""
    from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters
    app.add_handler(CommandHandler("start",     cmd_start))
    app.add_handler(CommandHandler("help",      cmd_help))
    app.add_handler(CommandHandler("products",  cmd_products))
    app.add_handler(CommandHandler("cart",      cmd_cart))
    app.add_handler(CommandHandler("orders",    cmd_orders))
    app.add_handler(CommandHandler("search",    cmd_search))
    app.add_handler(CommandHandler("recommend", cmd_recommend))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

def main():
    if not TOKEN:
        print("❌ CUSTOMER_BOT_TOKEN or TELEGRAM_TOKEN missing!")
        return

    init_db()
    print(f"🤖 Customer Bot starting...")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start",     cmd_start))
    app.add_handler(CommandHandler("help",      cmd_help))
    app.add_handler(CommandHandler("products",  cmd_products))
    app.add_handler(CommandHandler("cart",      cmd_cart))
    app.add_handler(CommandHandler("orders",    cmd_orders))
    app.add_handler(CommandHandler("search",    cmd_search))
    app.add_handler(CommandHandler("recommend", cmd_recommend))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print(f"✅ Customer Bot running! Token: {TOKEN[:10]}...")
    for attempt in range(10):
        try:
            app.run_polling(allowed_updates=["message","callback_query"], drop_pending_updates=True)
            break
        except Exception as e:
            if "Conflict" in str(e):
                import time
                print(f"⚠️ Customer Conflict, retry {attempt+1}/10 in 10s...")
                time.sleep(10)
            else:
                raise

if __name__ == "__main__":
    main()
