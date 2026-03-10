#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════╗
║   BOT 3: بوت التوصيات الذكية v2.0                             ║
║   AI Recommendation Engine                                      ║
║                                                                  ║
║   الوظائف:                                                      ║
║   ✅ توصيات مخصصة بالـ AI بناءً على احتياجات الزبون           ║
║   ✅ مقارنة بين منتجين                                         ║
║   ✅ "مثل هذا المنتج ولكن بسعر أقل"                            ║
║   ✅ توصيات بالميزانية                                          ║
║   ✅ حفظ تفضيلات المستخدم                                      ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os, logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Application, CommandHandler, MessageHandler,
                           CallbackQueryHandler, filters, ContextTypes)
from telegram.constants import ParseMode, ChatAction

try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass

import sys; sys.path.insert(0, os.path.dirname(__file__))
from shared_db import (upsert_user, update_user, get_user, get_products,
                        get_product, get_featured_products, get_products_by_category,
                        add_to_cart, track_event, init_db)
from ai_engine import (recommend_products, extract_budget, generate_mini_report,
                        _call as ai_call)

TOKEN    = os.environ.get("RECO_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN","")
ADMIN_ID = int(os.environ.get("ADMIN_USER_ID","0"))
SITE_URL = os.environ.get("SITE_URL","https://neo-pulse-hub.it.com")
PAYPAL   = os.environ.get("PAYPAL_EMAIL","Saidchaik@gmail.com")

logging.basicConfig(format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO, handlers=[logging.StreamHandler(),
    logging.FileHandler("recommendation_bot.log", encoding="utf-8")])
log = logging.getLogger("recommendation_bot")

_awaiting: dict = {}
_sessions: dict = {}  # user quiz sessions

# ══════════════════════════════════════════════════════════════════
# KEYBOARDS
# ══════════════════════════════════════════════════════════════════

def kb_main():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎯 احصل على توصية",     callback_data="start_quiz"),
         InlineKeyboardButton("💰 حسب الميزانية",      callback_data="by_budget")],
        [InlineKeyboardButton("🔄 قارن منتجين",        callback_data="compare"),
         InlineKeyboardButton("🔍 مثله ولكن أرخص",    callback_data="cheaper_alt")],
        [InlineKeyboardButton("⭐ الأعلى تقييماً",      callback_data="top_rated"),
         InlineKeyboardButton("🔥 الأكثر مبيعاً",      callback_data="best_sellers")],
        [InlineKeyboardButton("🌐 زيارة المتجر",        url=SITE_URL)],
    ])

def kb_categories_quiz():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⌚ ساعة ذكية",           callback_data="quiz_cat_smartwatch"),
         InlineKeyboardButton("🥽 نظارات/VR",           callback_data="quiz_cat_smart-glasses")],
        [InlineKeyboardButton("❤️ صحة ولياقة",          callback_data="quiz_cat_health"),
         InlineKeyboardButton("🏠 منزل ذكي",            callback_data="quiz_cat_smart-home")],
        [InlineKeyboardButton("🎧 سماعات",              callback_data="quiz_cat_earbuds"),
         InlineKeyboardButton("💼 إنتاجية",             callback_data="quiz_cat_productivity")],
        [InlineKeyboardButton("🤷 لا أعرف — AI يختار", callback_data="quiz_cat_any")],
    ])

def kb_budget_quiz():
    budgets = [
        ("أقل من $50",   "bdg_50"),
        ("$50 - $100",   "bdg_100"),
        ("$100 - $200",  "bdg_200"),
        ("$200 - $500",  "bdg_500"),
        ("فوق $500",     "bdg_1000"),
    ]
    return InlineKeyboardMarkup([[InlineKeyboardButton(n, callback_data=d)] for n,d in budgets] +
                                 [[InlineKeyboardButton("🔙 رجوع", callback_data="back_main")]])

def kb_use_case():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏋️ رياضة",      callback_data="use_sport"),
         InlineKeyboardButton("💼 عمل",         callback_data="use_work")],
        [InlineKeyboardButton("🏠 المنزل",       callback_data="use_home"),
         InlineKeyboardButton("📱 ترفيه",        callback_data="use_fun")],
        [InlineKeyboardButton("🎁 هدية",         callback_data="use_gift"),
         InlineKeyboardButton("❤️ صحة",          callback_data="use_health")],
    ])

def kb_product_reco(p: dict):
    from urllib.parse import urlencode
    params = urlencode({
        "cmd":"_xclick","business":PAYPAL,
        "item_name":p.get("name_ar","")[:127],
        "amount":str(p["price"]),"currency_code":"USD",
        "return":f"{SITE_URL}/thanks.html","cancel_return":f"{SITE_URL}/products.html",
        "no_note":"1","no_shipping":"2",
    })
    paypal_url = f"https://www.paypal.com/cgi-bin/webscr?{params}"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🛒 أضف للسلة",       callback_data=f"radd_{p['id']}")],
        [InlineKeyboardButton(f"💳 اشتر ${p['price']}", url=paypal_url)],
        [InlineKeyboardButton("📊 تقرير مفصل",        callback_data=f"rpt_{p['id']}"),
         InlineKeyboardButton("🔄 اقتراح بديل",       callback_data=f"alt_{p['id']}")],
        [InlineKeyboardButton("🔙 توصية أخرى",        callback_data="back_main")],
    ])

# ══════════════════════════════════════════════════════════════════
# QUIZ STATE MACHINE
# ══════════════════════════════════════════════════════════════════

class QuizSession:
    def __init__(self, user_id):
        self.user_id  = user_id
        self.category = None
        self.budget   = None
        self.use_case = None
        self.free_text= None

    def is_complete(self):
        return self.category is not None and self.budget is not None

    def to_query(self) -> str:
        parts = []
        if self.category: parts.append(f"فئة: {self.category}")
        if self.budget:   parts.append(f"ميزانية: ${self.budget}")
        if self.use_case: parts.append(f"الاستخدام: {self.use_case}")
        if self.free_text:parts.append(self.free_text)
        return " | ".join(parts)

# ══════════════════════════════════════════════════════════════════
# HANDLERS
# ══════════════════════════════════════════════════════════════════

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    upsert_user(user)
    name = user.first_name or "صديقي"
    await update.message.reply_text(
        f"🎯 أهلاً *{name}*!\n\n"
        f"أنا بوت التوصيات الذكي لـ *NEO PULSE HUB*.\n\n"
        f"أساعدك تختار المنتج الأنسب بالذكاء الاصطناعي.\n"
        f"فقط أخبرني ما تحتاج وسأجد لك المثالي! 🤖",
        parse_mode=ParseMode.MARKDOWN, reply_markup=kb_main()
    )

async def cmd_compare(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    _awaiting[update.effective_user.id] = "compare_1"
    await update.message.reply_text(
        "🔄 *مقارنة منتجين*\n\nأرسل اسم المنتج الأول:",
        parse_mode=ParseMode.MARKDOWN
    )

async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text.strip()
    uid  = user.id
    upsert_user(user)

    state = _awaiting.pop(uid, None)

    if state == "free_reco":
        return await _do_full_reco(update, ctx, text)

    elif state == "by_budget_text":
        budget = extract_budget(text) or float(text.replace("$","").strip() or "100")
        return await _reco_by_budget(update, ctx, budget)

    elif state == "compare_1":
        _awaiting[uid] = "compare_2"
        ctx.user_data["compare_p1"] = text
        await update.message.reply_text("👍 الآن أرسل اسم المنتج الثاني:")

    elif state == "compare_2":
        p1 = ctx.user_data.pop("compare_p1","")
        p2 = text
        await _do_compare(update, ctx, p1, p2)

    elif state and state.startswith("quiz_free_"):
        session = _sessions.get(uid, QuizSession(uid))
        session.free_text = text
        _sessions[uid]    = session
        await _do_quiz_reco(update, ctx, session)

    else:
        # Free text — treat as recommendation query
        await _do_full_reco(update, ctx, text)

async def handle_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid  = query.from_user.id
    d    = query.data
    upsert_user(query.from_user)

    if d == "back_main":
        await query.edit_message_text(
            "🎯 *بوت التوصيات الذكي*\nاختر نوع التوصية:",
            parse_mode=ParseMode.MARKDOWN, reply_markup=kb_main()
        )

    elif d == "start_quiz":
        _sessions[uid] = QuizSession(uid)
        await query.edit_message_text(
            "🎯 *اختار فئة المنتج:*",
            parse_mode=ParseMode.MARKDOWN, reply_markup=kb_categories_quiz()
        )

    elif d.startswith("quiz_cat_"):
        cat = d.replace("quiz_cat_","")
        session = _sessions.setdefault(uid, QuizSession(uid))
        session.category = None if cat == "any" else cat
        _sessions[uid] = session
        await query.edit_message_text(
            "💰 *ما ميزانيتك؟*",
            parse_mode=ParseMode.MARKDOWN, reply_markup=kb_budget_quiz()
        )

    elif d.startswith("bdg_"):
        bdg_map = {"bdg_50":50,"bdg_100":100,"bdg_200":200,"bdg_500":500,"bdg_1000":1000}
        session = _sessions.setdefault(uid, QuizSession(uid))
        session.budget = bdg_map.get(d, 200)
        _sessions[uid] = session
        await query.edit_message_text(
            "🎯 *ما هو الاستخدام الرئيسي؟*",
            parse_mode=ParseMode.MARKDOWN, reply_markup=kb_use_case()
        )

    elif d.startswith("use_"):
        use_map = {"use_sport":"رياضة","use_work":"عمل","use_home":"منزل",
                   "use_fun":"ترفيه","use_gift":"هدية","use_health":"صحة"}
        session = _sessions.setdefault(uid, QuizSession(uid))
        session.use_case = use_map.get(d,"")
        _sessions[uid]   = session

        await query.edit_message_text("⏳ *AI يختار أفضل منتج لك...*", parse_mode=ParseMode.MARKDOWN)
        await _do_quiz_reco(query, ctx, session)

    elif d == "by_budget":
        await query.edit_message_text(
            "💰 *أرسل ميزانيتك بالدولار:*\n\nمثال: _150_ أو _أقل من 200 دولار_",
            parse_mode=ParseMode.MARKDOWN
        )
        _awaiting[uid] = "by_budget_text"

    elif d == "compare":
        _awaiting[uid] = "compare_1"
        await query.edit_message_text(
            "🔄 *مقارنة منتجين*\n\nأرسل اسم المنتج الأول:",
            parse_mode=ParseMode.MARKDOWN
        )

    elif d == "cheaper_alt":
        _awaiting[uid] = "free_reco"
        await query.edit_message_text(
            "🔍 *أرسل اسم المنتج الذي تريد بديلاً أرخص منه:*",
            parse_mode=ParseMode.MARKDOWN
        )

    elif d == "top_rated":
        products = sorted(get_products(), key=lambda x: x.get("rating",0), reverse=True)[:3]
        await query.delete_message()
        for p in products:
            await _send_product_card(query.message.chat_id, ctx, p)

    elif d == "best_sellers":
        products = sorted(get_products(), key=lambda x: x.get("reviews",0), reverse=True)[:3]
        await query.delete_message()
        for p in products:
            await _send_product_card(query.message.chat_id, ctx, p)

    elif d.startswith("radd_"):
        pid  = d.replace("radd_","")
        cart = add_to_cart(uid, pid)
        p    = get_product(pid)
        await query.answer(f"✅ أُضيف: {p.get('name_ar','') if p else pid}")

    elif d.startswith("rpt_"):
        pid = d.replace("rpt_","")
        p   = get_product(pid)
        if not p: return await query.answer("المنتج غير موجود",show_alert=True)
        await query.edit_message_text("⏳ AI يولد التقرير...", parse_mode=ParseMode.MARKDOWN)
        report = generate_mini_report(p)
        await query.edit_message_text(
            f"📊 *تقرير: {p.get('name_ar','')}*\n\n{report}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🛒 أضف للسلة",callback_data=f"radd_{pid}")],
                [InlineKeyboardButton("🔙 رجوع",     callback_data="back_main")]
            ])
        )

    elif d.startswith("alt_"):
        pid = d.replace("alt_","")
        p   = get_product(pid)
        if not p: return
        await query.edit_message_text("🔍 AI يبحث عن بديل...", parse_mode=ParseMode.MARKDOWN)
        products    = [x for x in get_products() if x["id"] != pid]
        alt_query   = f"مثل {p.get('name_ar','')} ولكن بسعر أقل من ${p['price']}"
        alt_ids     = recommend_products(alt_query, products, p["price"]*0.9)
        alt_product = get_product(alt_ids[0]) if alt_ids else None
        if alt_product:
            await query.delete_message()
            await _send_product_card(query.message.chat_id, ctx, alt_product,
                                      prefix=f"💡 *بديل لـ {p.get('name_ar','')}:*\n\n")
        else:
            await query.edit_message_text("❌ لم أجد بديلاً مناسباً.", reply_markup=kb_main())

# ══════════════════════════════════════════════════════════════════
# CORE LOGIC
# ══════════════════════════════════════════════════════════════════

async def _do_full_reco(update: Update, ctx: ContextTypes.DEFAULT_TYPE, query: str):
    loading = await update.message.reply_text(
        "🤖 *أحلل طلبك...*", parse_mode=ParseMode.MARKDOWN
    )
    await update.message.chat.send_action(ChatAction.TYPING)
    products = get_products()
    budget   = extract_budget(query)
    if budget:
        products = [p for p in products if p.get("price",9999) <= budget * 1.2]

    ids  = recommend_products(query, products, budget)
    recs = [get_product(pid) for pid in ids if get_product(pid)]
    if not recs:
        recs = sorted(products, key=lambda x: x.get("rating",0), reverse=True)[:3]

    await loading.delete()
    for p in recs[:3]:
        await _send_product_card(update.message.chat_id, ctx, p)

    # Save preference
    update_user(update.effective_user.id, {"last_query": query})
    track_event("recommendation", {"query": query, "user_id": update.effective_user.id})

async def _reco_by_budget(update, ctx, budget: float):
    loading = await update.message.reply_text(
        f"💰 *أبحث في المنتجات ضمن ${budget}...*", parse_mode=ParseMode.MARKDOWN
    )
    products = [p for p in get_products() if p.get("price",9999) <= budget]
    products = sorted(products, key=lambda x: x.get("rating",0), reverse=True)[:3]
    await loading.delete()
    if not products:
        return await update.message.reply_text(
            f"❌ لا توجد منتجات بأقل من ${budget} حالياً.",
            reply_markup=kb_main()
        )
    for p in products:
        await _send_product_card(update.message.chat_id, ctx, p)

async def _do_quiz_reco(source, ctx, session: QuizSession):
    chat_id = (source.message.chat_id if hasattr(source,"message") else source.chat_id
               if hasattr(source,"chat_id") else None)
    if not chat_id: return

    query   = session.to_query()
    products = get_products()
    if session.category:
        filtered = get_products_by_category(session.category)
        if filtered: products = filtered
    if session.budget:
        products = [p for p in products if p.get("price",9999) <= session.budget * 1.1]

    ids  = recommend_products(query, products, session.budget)
    recs = [get_product(pid) for pid in ids if get_product(pid)]
    if not recs:
        recs = sorted(products, key=lambda x: x.get("rating",0), reverse=True)[:2]

    # Send intro
    intro = ai_call(
        f"اكتب جملة ترحيب قصيرة (جملة واحدة) لتقديم توصية:\n"
        f"الفئة: {session.category or 'متنوعة'}, الميزانية: ${session.budget}, الاستخدام: {session.use_case}",
        temperature=0.7, max_tokens=80
    )
    try:
        if hasattr(source,"edit_message_text"):
            await source.edit_message_text(f"🎯 {intro}", parse_mode=ParseMode.MARKDOWN)
        else:
            await ctx.bot.send_message(chat_id=chat_id, text=f"🎯 {intro}", parse_mode=ParseMode.MARKDOWN)
    except: pass

    for p in recs[:2]:
        await _send_product_card(chat_id, ctx, p)

    _sessions.pop(session.user_id, None)

async def _do_compare(update: Update, ctx: ContextTypes.DEFAULT_TYPE, p1_name: str, p2_name: str):
    loading = await update.message.reply_text("⏳ *AI يقارن المنتجين...*", parse_mode=ParseMode.MARKDOWN)
    await update.message.chat.send_action(ChatAction.TYPING)

    p1_list = search_products_local(p1_name)
    p2_list = search_products_local(p2_name)
    p1 = p1_list[0] if p1_list else None
    p2 = p2_list[0] if p2_list else None

    if not p1 or not p2:
        await loading.delete()
        return await update.message.reply_text(
            "❌ لم أجد أحد المنتجين. تأكد من الأسماء.",
            reply_markup=kb_main()
        )

    comparison = ai_call(
        f"""قارن بين هذين المنتجين بالعربية في جدول مختصر:
المنتج 1: {p1.get('name_ar','')} — ${p1['price']} — تقييم {p1.get('rating',0)}/5
المزايا: {', '.join(p1.get('features_ar',[])[:3])}

المنتج 2: {p2.get('name_ar','')} — ${p2['price']} — تقييم {p2.get('rating',0)}/5
المزايا: {', '.join(p2.get('features_ar',[])[:3])}

أجب بـ: أوجه التشابه، الفروق الرئيسية، من الأفضل ولماذا، التوصية النهائية.""",
        temperature=0.5, max_tokens=500
    )

    await loading.delete()
    from urllib.parse import urlencode
    def plink(p):
        params = urlencode({"cmd":"_xclick","business":PAYPAL,
            "item_name":p.get("name_ar","")[:127],"amount":str(p["price"]),"currency_code":"USD",
            "return":f"{SITE_URL}/thanks.html","cancel_return":f"{SITE_URL}/products.html",
            "no_note":"1","no_shipping":"2"})
        return f"https://www.paypal.com/cgi-bin/webscr?{params}"

    await update.message.reply_text(
        f"🔄 *مقارنة: {p1.get('name_ar','')} vs {p2.get('name_ar','')}*\n\n{comparison}",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(f"💳 {p1.get('name_ar','')[:20]} ${p1['price']}", url=plink(p1))],
            [InlineKeyboardButton(f"💳 {p2.get('name_ar','')[:20]} ${p2['price']}", url=plink(p2))],
            [InlineKeyboardButton("🔄 مقارنة أخرى", callback_data="compare"),
             InlineKeyboardButton("🔙 رجوع", callback_data="back_main")],
        ])
    )

def search_products_local(query: str) -> list:
    from shared_db import search_products
    return search_products(query)

async def _send_product_card(chat_id: int, ctx, p: dict, prefix: str = ""):
    text = (
        f"{prefix}"
        f"🛍️ *{p.get('name_ar','')}*\n"
        f"_{p.get('category_ar','')} • {p.get('brand','')}_\n\n"
        f"💰 *${p['price']}*"
        + (f" ~~${p.get('original_price',0)}~~ (-{p.get('discount',0)}%)" if p.get("original_price") else "") + "\n"
        f"⭐ {p.get('rating',0)}/5 ({p.get('reviews',0):,} تقييم)\n"
        f"📦 المخزون: {p.get('stock',0)} | 🚚 {p.get('shipping_days','7-14')} يوم\n\n"
        f"🔑 {' • '.join(p.get('features_ar',[])[:3])}\n\n"
        f"_{p.get('description_ar','')}_"
    )
    kb = kb_product_reco(p)
    try:
        if p.get("image"):
            await ctx.bot.send_photo(chat_id=chat_id, photo=p["image"],
                                      caption=text[:1024], parse_mode=ParseMode.MARKDOWN, reply_markup=kb)
        else:
            await ctx.bot.send_message(chat_id=chat_id, text=text,
                                        parse_mode=ParseMode.MARKDOWN, reply_markup=kb)
    except Exception as e:
        log.error(f"send card: {e}")
        try:
            await ctx.bot.send_message(chat_id=chat_id, text=text,
                                        parse_mode=ParseMode.MARKDOWN, reply_markup=kb)
        except: pass

# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

def main():
    if not TOKEN:
        print("❌ RECO_BOT_TOKEN or TELEGRAM_TOKEN missing!")
        return
    init_db()
    print("🎯 Recommendation Bot starting...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start",   cmd_start))
    app.add_handler(CommandHandler("compare", cmd_compare))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Recommendation Bot running!")
    for attempt in range(10):
        try:
            app.run_polling(allowed_updates=["message","callback_query"], drop_pending_updates=True)
            break
        except Exception as e:
            if "Conflict" in str(e):
                import time
                print(f"⚠️ Reco Conflict, retry {attempt+1}/10 in 10s...")
                time.sleep(10)
            else:
                raise

if __name__ == "__main__":
    main()
