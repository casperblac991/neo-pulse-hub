#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════╗
║   BOT 2: بوت الإدارة الكامل v2.0                               ║
║   Admin Dashboard Bot                                           ║
║                                                                  ║
║   الوظائف:                                                      ║
║   ✅ إحصائيات المتجر الكاملة                                    ║
║   ✅ إدارة المنتجات (إضافة/تعديل/حذف/تفعيل)                    ║
║   ✅ إدارة الطلبات وتغيير حالتها                                ║
║   ✅ بث رسائل للمستخدمين                                        ║
║   ✅ تقارير AI ذكية                                             ║
║   ✅ تنبيهات تلقائية (مخزون منخفض، طلبات جديدة)               ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os, logging, asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Application, CommandHandler, MessageHandler,
                           CallbackQueryHandler, filters, ContextTypes)
from telegram.constants import ParseMode, ChatAction

try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass

import sys; sys.path.insert(0, os.path.dirname(__file__))
from shared_db import (get_products, get_product, save_products, add_product,
                        update_product, get_orders, get_recent_orders,
                        update_order_status, get_all_users, get_total_users,
                        get_analytics_summary, get_low_stock, get_out_of_stock,
                        get_subscribers, init_db)
from ai_engine import (generate_store_report, generate_marketing_post,
                        generate_product_description, suggest_price)

# ── Config ─────────────────────────────────────────────────────────
TOKEN    = os.environ.get("ADMIN_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN","")
ADMIN_ID = int(os.environ.get("ADMIN_USER_ID","0"))

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(), logging.FileHandler("admin_bot.log", encoding="utf-8")]
)
log = logging.getLogger("admin_bot")

_awaiting: dict = {}

# ══════════════════════════════════════════════════════════════════
# AUTH GUARD
# ══════════════════════════════════════════════════════════════════

def admin_only(func):
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id
        if ADMIN_ID and uid != ADMIN_ID:
            await update.message.reply_text("🚫 هذا البوت للمدير فقط.")
            return
        return await func(update, ctx)
    return wrapper

def admin_only_cb(func):
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id
        if ADMIN_ID and uid != ADMIN_ID:
            await update.callback_query.answer("🚫 غير مصرح", show_alert=True)
            return
        return await func(update, ctx)
    return wrapper

# ══════════════════════════════════════════════════════════════════
# KEYBOARDS
# ══════════════════════════════════════════════════════════════════

def kb_main_admin():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 الإحصائيات",     callback_data="stats"),
         InlineKeyboardButton("🛍️ المنتجات",        callback_data="manage_products")],
        [InlineKeyboardButton("📦 الطلبات",          callback_data="manage_orders"),
         InlineKeyboardButton("👥 المستخدمون",        callback_data="manage_users")],
        [InlineKeyboardButton("📢 بث رسالة",         callback_data="broadcast"),
         InlineKeyboardButton("🤖 تقرير AI",          callback_data="ai_report")],
        [InlineKeyboardButton("⚙️ إعدادات",           callback_data="settings"),
         InlineKeyboardButton("🔄 تحديث المخزون",     callback_data="sync_stock")],
    ])

def kb_products_admin():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ إضافة منتج",        callback_data="add_product_manual"),
         InlineKeyboardButton("🤖 إضافة بالـ AI",     callback_data="add_product_ai")],
        [InlineKeyboardButton("📋 عرض الكل",          callback_data="list_products"),
         InlineKeyboardButton("⚠️ مخزون منخفض",       callback_data="low_stock")],
        [InlineKeyboardButton("🔙 رجوع",              callback_data="back_main")],
    ])

def kb_orders_admin():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 آخر الطلبات",       callback_data="recent_orders"),
         InlineKeyboardButton("⏳ معلقة",             callback_data="pending_orders")],
        [InlineKeyboardButton("✅ مكتملة",             callback_data="completed_orders"),
         InlineKeyboardButton("🔍 بحث بـ ID",          callback_data="search_order")],
        [InlineKeyboardButton("🔙 رجوع",              callback_data="back_main")],
    ])

# ══════════════════════════════════════════════════════════════════
# HANDLERS
# ══════════════════════════════════════════════════════════════════

@admin_only
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    s = get_analytics_summary()
    text = (
        f"👑 *لوحة تحكم NEO PULSE HUB*\n\n"
        f"📊 لمحة سريعة:\n"
        f"• 👥 المستخدمون: *{s['total_users']}*\n"
        f"• 📦 الطلبات: *{s['total_orders']}*\n"
        f"• 💰 الإيرادات: *${s['total_revenue']:,.2f}*\n"
        f"• 🛍️ المنتجات: *{s['total_products']}*\n"
        f"• ⏳ طلبات معلقة: *{s['pending_orders']}*\n"
        f"• ⚠️ مخزون منخفض: *{s['low_stock_count']}*\n\n"
        f"اختر عملية 👇"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb_main_admin())

@admin_only
async def cmd_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    s = get_analytics_summary()
    orders = get_orders()
    today  = datetime.now().date().isoformat()
    today_orders = [o for o in orders["orders"] if o.get("created_at","").startswith(today)]
    today_rev    = sum(o["total"] for o in today_orders)

    text = (
        f"📊 *تقرير مفصل — {datetime.now().strftime('%Y-%m-%d')}*\n\n"
        f"━━━━ 👥 المستخدمون ━━━━\n"
        f"إجمالي: *{s['total_users']}* مستخدم\n"
        f"المشتركين بالنشرة: *{len(get_subscribers())}*\n\n"
        f"━━━━ 💰 المبيعات ━━━━\n"
        f"إجمالي الطلبات: *{s['total_orders']}*\n"
        f"الإيرادات الكلية: *${s['total_revenue']:,.2f}*\n"
        f"اليوم: *{len(today_orders)}* طلب / *${today_rev:.2f}*\n"
        f"معلقة الدفع: *{s['pending_orders']}*\n\n"
        f"━━━━ 🛍️ المنتجات ━━━━\n"
        f"الإجمالي: *{s['total_products']}*\n"
        f"مخزون منخفض: *{s['low_stock_count']}*\n"
        f"نفد مخزونه: *{len(get_out_of_stock())}*\n\n"
        f"━━━━ 👁️ الأكثر مشاهدة ━━━━\n"
    )
    for pid, views in s.get("top_products",[])[:5]:
        p = get_product(pid)
        name = p.get("name_ar","؟") if p else pid
        text += f"• {name}: *{views}* مشاهدة\n"

    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN,
                                     reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🤖 تقرير AI", callback_data="ai_report"),InlineKeyboardButton("🔙", callback_data="back_main")]]))

@admin_only
async def cmd_broadcast(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if ctx.args:
        message = " ".join(ctx.args)
        users   = get_all_users()
        sent = failed = 0
        for user in users:
            try:
                await ctx.bot.send_message(
                    chat_id=user["id"],
                    text=f"📢 *رسالة من NEO PULSE HUB:*\n\n{message}",
                    parse_mode=ParseMode.MARKDOWN
                )
                sent += 1
                await asyncio.sleep(0.05)
            except Exception as e:
                failed += 1
                log.error(f"Broadcast to {user['id']}: {e}")
        await update.message.reply_text(
            f"📢 *تم الإرسال!*\n✅ نجح: {sent}\n❌ فشل: {failed}",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        _awaiting[update.effective_user.id] = "broadcast"
        await update.message.reply_text(
            "📢 *اكتب الرسالة للبث:*\n\nستُرسل لجميع المستخدمين.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء", callback_data="back_main")]])
        )

@admin_only
async def cmd_add_product(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    _awaiting[update.effective_user.id] = "add_product_ai"
    await update.message.reply_text(
        "🤖 *إضافة منتج بالذكاء الاصطناعي*\n\nأرسل اسم المنتج أو وصفه:",
        parse_mode=ParseMode.MARKDOWN
    )

@admin_only
async def cmd_update_order(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if len(ctx.args) >= 2:
        oid, status = ctx.args[0], ctx.args[1]
        ok = update_order_status(oid, status)
        await update.message.reply_text(
            f"{'✅' if ok else '❌'} {'تم تحديث الطلب' if ok else 'الطلب غير موجود'} `{oid}` → `{status}`",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await update.message.reply_text("⚠️ الاستخدام: /update_order [ID] [status]\nالحالات: pending_payment | paid | shipped | delivered | cancelled")

# ── Message handler ────────────────────────────────────────────────
@admin_only
async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid  = update.effective_user.id
    text = update.message.text.strip()
    state = _awaiting.pop(uid, None)

    if state == "broadcast":
        users = get_all_users()
        await update.message.reply_text(f"⏳ جاري الإرسال لـ {len(users)} مستخدم...")
        sent = failed = 0
        for user in users:
            try:
                await ctx.bot.send_message(chat_id=user["id"],
                    text=f"📢 *رسالة من NEO PULSE HUB:*\n\n{text}",
                    parse_mode=ParseMode.MARKDOWN)
                sent += 1
                await asyncio.sleep(0.05)
            except: failed += 1
        await update.message.reply_text(
            f"✅ أُرسلت لـ {sent} مستخدم | ❌ فشل: {failed}",
            reply_markup=kb_main_admin()
        )

    elif state == "add_product_ai":
        await update.message.reply_text("🤖 جاري البحث عن المنتج...", parse_mode=ParseMode.MARKDOWN)
        await update.message.chat.send_action(ChatAction.TYPING)
        from ai_engine import search_product_by_description
        data = search_product_by_description(text)
        if not data or not data.get("found"):
            return await update.message.reply_text("❌ لم يُعثر على المنتج. جرب وصفاً أوضح.",
                                                    reply_markup=kb_main_admin())
        base = float(data.get("estimated_price_usd", 99))
        sell = round(base * 1.35, 2)
        orig = float(data.get("original_retail_usd", sell * 1.25))
        _awaiting[uid] = f"confirm_add_{uid}"
        ctx.user_data["pending_product"] = data
        text_preview = (
            f"🛍️ *{data.get('name_ar','')}*\n"
            f"_{data.get('brand','')} — {data.get('category_ar','')}_\n\n"
            f"💰 سعر البيع: *${sell}*\n"
            f"📦 التكلفة: ${base:.2f}\n"
            f"📈 الربح: {round((sell-base)/sell*100,1)}%\n"
            f"⭐ التقييم: {data.get('rating',4.4)}/5\n"
            f"🔑 {', '.join(data.get('features_ar',[])[:3])}\n\n"
            f"هل تضيفه للمتجر؟"
        )
        await update.message.reply_text(text_preview, parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ أضف للمتجر", callback_data="confirm_add_product"),
                 InlineKeyboardButton("❌ إلغاء",       callback_data="back_main")]
            ])
        )

    elif state and state.startswith("edit_price_"):
        pid = state.replace("edit_price_","")
        try:
            new_price = float(text.replace("$","").strip())
            ok = update_product(pid, {"price": new_price})
            await update.message.reply_text(
                f"{'✅ تم التحديث' if ok else '❌ المنتج غير موجود'}: ${new_price}",
                reply_markup=kb_main_admin()
            )
        except:
            await update.message.reply_text("❌ أدخل رقماً صحيحاً للسعر")

    elif state and state.startswith("edit_stock_"):
        pid = state.replace("edit_stock_","")
        try:
            new_stock = int(text)
            ok = update_product(pid, {"stock": new_stock})
            await update.message.reply_text(
                f"{'✅ تم التحديث' if ok else '❌ غير موجود'}: {new_stock} وحدة",
                reply_markup=kb_main_admin()
            )
        except:
            await update.message.reply_text("❌ أدخل رقماً صحيحاً")

    else:
        await update.message.reply_text("👑 لوحة التحكم:", reply_markup=kb_main_admin())

# ── Callback handler ───────────────────────────────────────────────
@admin_only_cb
async def handle_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    d   = query.data

    if d == "back_main":
        s = get_analytics_summary()
        await query.edit_message_text(
            f"👑 *لوحة تحكم NEO PULSE HUB*\n\n"
            f"👥 {s['total_users']} مستخدم | 📦 {s['total_orders']} طلب | 💰 ${s['total_revenue']:,.0f}",
            parse_mode=ParseMode.MARKDOWN, reply_markup=kb_main_admin()
        )

    elif d == "stats":
        s    = get_analytics_summary()
        text = (
            f"📊 *الإحصائيات الكاملة*\n\n"
            f"👥 المستخدمون: *{s['total_users']}*\n"
            f"📦 الطلبات: *{s['total_orders']}*\n"
            f"💰 الإيرادات: *${s['total_revenue']:,.2f}*\n"
            f"🛍️ المنتجات: *{s['total_products']}*\n"
            f"⏳ معلقة: *{s['pending_orders']}*\n"
            f"⚠️ مخزون منخفض: *{s['low_stock_count']}*\n"
            f"👁️ مشاهدات: *{s['page_views']}*"
        )
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🤖 تقرير AI", callback_data="ai_report")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="back_main")]
            ])
        )

    elif d == "ai_report":
        await query.edit_message_text("⏳ *AI يحلل أداء المتجر...*", parse_mode=ParseMode.MARKDOWN)
        s      = get_analytics_summary()
        report = generate_store_report(s)
        await query.edit_message_text(
            f"🤖 *تقرير AI عن المتجر*\n\n{report}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back_main")]])
        )

    elif d == "manage_products":
        ps = get_products()
        await query.edit_message_text(
            f"🛍️ *إدارة المنتجات*\n\nالإجمالي: *{len(ps)}* منتج",
            parse_mode=ParseMode.MARKDOWN, reply_markup=kb_products_admin()
        )

    elif d == "list_products":
        ps = get_products()
        buttons = []
        for p in ps[:10]:
            status = "🟢" if p.get("active",True) else "🔴"
            buttons.append([InlineKeyboardButton(
                f"{status} {p.get('name_ar','')[:25]} — ${p['price']}",
                callback_data=f"prod_detail_{p['id']}"
            )])
        buttons.append([InlineKeyboardButton("🔙 رجوع", callback_data="manage_products")])
        await query.edit_message_text(
            f"🛍️ *المنتجات ({len(ps)}):*",
            parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif d.startswith("prod_detail_"):
        pid = d.replace("prod_detail_","")
        p   = get_product(pid)
        if not p: return await query.answer("غير موجود", show_alert=True)
        text = (
            f"🛍️ *{p.get('name_ar','')}*\n"
            f"🆔 `{p['id']}`\n"
            f"💰 السعر: ${p['price']} | التكلفة: ${p.get('base_cost','?')}\n"
            f"📦 المخزون: {p.get('stock',0)}\n"
            f"⭐ التقييم: {p.get('rating',0)}/5\n"
            f"🔁 الحالة: {'نشط 🟢' if p.get('active',True) else 'معطل 🔴'}"
        )
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✏️ تعديل السعر", callback_data=f"edit_price_{pid}"),
                 InlineKeyboardButton("📦 تعديل المخزون", callback_data=f"edit_stock_{pid}")],
                [InlineKeyboardButton("🤖 وصف AI", callback_data=f"regen_desc_{pid}"),
                 InlineKeyboardButton("📣 منشور AI", callback_data=f"marketing_post_{pid}")],
                [InlineKeyboardButton("🚫 تعطيل" if p.get("active",True) else "✅ تفعيل",
                                      callback_data=f"toggle_prod_{pid}")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="list_products")]
            ])
        )

    elif d.startswith("edit_price_"):
        pid = d.replace("edit_price_","")
        _awaiting[uid] = f"edit_price_{pid}"
        await query.edit_message_text(f"✏️ *أرسل السعر الجديد لـ `{pid}`:*",
                                       parse_mode=ParseMode.MARKDOWN)

    elif d.startswith("edit_stock_"):
        pid = d.replace("edit_stock_","")
        _awaiting[uid] = f"edit_stock_{pid}"
        await query.edit_message_text(f"📦 *أرسل الكمية الجديدة لـ `{pid}`:*",
                                       parse_mode=ParseMode.MARKDOWN)

    elif d.startswith("toggle_prod_"):
        pid = d.replace("toggle_prod_","")
        p   = get_product(pid)
        if p:
            new_state = not p.get("active", True)
            update_product(pid, {"active": new_state})
            await query.answer(f"{'✅ فُعّل' if new_state else '🚫 عُطّل'}")
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 رجوع", callback_data="list_products")]]))

    elif d.startswith("regen_desc_"):
        pid = d.replace("regen_desc_","")
        p   = get_product(pid)
        if not p: return
        await query.edit_message_text("⏳ AI يكتب الوصف...", parse_mode=ParseMode.MARKDOWN)
        desc = generate_product_description(p)
        update_product(pid, {"description_ar": desc})
        await query.edit_message_text(
            f"✅ *تم تحديث الوصف:*\n\n{desc}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data=f"prod_detail_{pid}")]]))

    elif d.startswith("marketing_post_"):
        pid = d.replace("marketing_post_","")
        p   = get_product(pid)
        if not p: return
        await query.edit_message_text("⏳ AI يكتب المنشور...", parse_mode=ParseMode.MARKDOWN)
        post = generate_marketing_post(p, "telegram")
        await query.edit_message_text(
            f"📣 *منشور تسويقي:*\n\n{post}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data=f"prod_detail_{pid}")]]))

    elif d == "add_product_ai":
        _awaiting[uid] = "add_product_ai"
        await query.edit_message_text(
            "🤖 *إضافة منتج بالـ AI*\n\nأرسل اسم أو وصف المنتج:",
            parse_mode=ParseMode.MARKDOWN)

    elif d == "confirm_add_product":
        data = ctx.user_data.get("pending_product")
        if not data:
            return await query.edit_message_text("❌ انتهت المهلة. ابدأ من جديد.",
                                                  reply_markup=kb_main_admin())
        base = float(data.get("estimated_price_usd",99))
        sell = round(base * 1.35, 2)
        orig = float(data.get("original_retail_usd", sell*1.25))
        product = {
            "name_ar":      data["name_ar"],
            "name_en":      data.get("name_en",""),
            "brand":        data.get("brand",""),
            "category":     data.get("category","productivity"),
            "category_ar":  data.get("category_ar","منتجات ذكية"),
            "price":        sell,
            "original_price": round(orig,2),
            "base_cost":    round(base,2),
            "profit_margin":round((sell-base)/sell*100,1),
            "discount":     max(5, round((1-sell/orig)*100)) if orig > sell else 20,
            "rating":       float(data.get("rating",4.4)),
            "reviews":      int(data.get("reviews_count",0)),
            "stock":        int(data.get("stock",25)),
            "image":        f"https://source.unsplash.com/400x400/?{data.get('image_search_query','tech+gadget').replace(' ','+')}",
            "description_ar": data.get("description_ar",""),
            "features_ar":  data.get("features_ar",[]),
            "tags":         data.get("tags",[]) + ["AI","ذكي"],
            "shipping_days":data.get("shipping_days","7-14"),
            "badge":        "جديد 🔥",
        }
        added = add_product(product)
        ctx.user_data.pop("pending_product", None)
        await query.edit_message_text(
            f"✅ *تم إضافة المنتج!*\n\n"
            f"🆔 `{added['id']}`\n"
            f"🛍️ {added['name_ar']}\n"
            f"💰 ${added['price']} (ربح {added['profit_margin']}%)\n"
            f"📦 مخزون: {added['stock']}",
            parse_mode=ParseMode.MARKDOWN, reply_markup=kb_main_admin()
        )

    elif d == "low_stock":
        ps = get_low_stock()
        if not ps:
            return await query.edit_message_text("✅ لا يوجد مخزون منخفض.",
                                                  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙",callback_data="manage_products")]]))
        text = "⚠️ *مخزون منخفض:*\n\n"
        for p in ps:
            text += f"• `{p['id']}` {p.get('name_ar','')} — *{p.get('stock',0)}* وحدة متبقية\n"
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN,
                                       reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙",callback_data="manage_products")]]))

    elif d == "manage_orders":
        await query.edit_message_text("📦 *إدارة الطلبات:*",
                                       parse_mode=ParseMode.MARKDOWN, reply_markup=kb_orders_admin())

    elif d == "recent_orders":
        orders = get_recent_orders(10)
        if not orders:
            return await query.edit_message_text("📦 لا توجد طلبات.",
                                                  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙",callback_data="manage_orders")]]))
        text = "📦 *آخر 10 طلبات:*\n\n"
        for o in orders:
            icons = {"pending_payment":"⏳","paid":"✅","shipped":"🚚","delivered":"📬","cancelled":"❌"}
            text += (f"{icons.get(o.get('status',''),'❓')} `{o['id']}` — "
                     f"{o['product_name'][:20]} — *${o['total']}*\n"
                     f"   👤 UID:{o.get('user_id',0)} | {o.get('created_at','')[:10]}\n")
        buttons = []
        for o in orders[:5]:
            buttons.append([InlineKeyboardButton(f"✏️ {o['id']}", callback_data=f"update_ord_{o['id']}")])
        buttons.append([InlineKeyboardButton("🔙 رجوع", callback_data="manage_orders")])
        await query.edit_message_text(text[:3500], parse_mode=ParseMode.MARKDOWN,
                                       reply_markup=InlineKeyboardMarkup(buttons))

    elif d.startswith("update_ord_"):
        oid = d.replace("update_ord_","")
        await query.edit_message_text(
            f"📦 تحديث حالة الطلب `{oid}`:*",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ مدفوع",    callback_data=f"ord_status_{oid}_paid")],
                [InlineKeyboardButton("🚚 مشحون",    callback_data=f"ord_status_{oid}_shipped")],
                [InlineKeyboardButton("📬 تم توصيله",callback_data=f"ord_status_{oid}_delivered")],
                [InlineKeyboardButton("❌ ملغي",     callback_data=f"ord_status_{oid}_cancelled")],
                [InlineKeyboardButton("🔙 رجوع",    callback_data="recent_orders")],
            ])
        )

    elif d.startswith("ord_status_"):
        parts  = d.replace("ord_status_","").rsplit("_",1)
        oid, status = parts[0], parts[1]
        ok = update_order_status(oid, status)
        await query.answer(f"{'✅ تم' if ok else '❌ خطأ'}: {oid} → {status}", show_alert=True)

    elif d == "manage_users":
        users = get_all_users()
        text  = (
            f"👥 *المستخدمون ({len(users)}):*\n\n"
            + "\n".join([
                f"• {u.get('name','')} (@{u.get('username','')}) — "
                f"رسائل:{u.get('messages',0)} | طلبات:{u.get('orders',0)}"
                for u in users[-8:]
            ])
        )
        await query.edit_message_text(text[:3500], parse_mode=ParseMode.MARKDOWN,
                                       reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙",callback_data="back_main")]]))

    elif d == "broadcast":
        _awaiting[uid] = "broadcast"
        await query.edit_message_text(
            f"📢 *بث رسالة*\n\n"
            f"سيتم الإرسال لـ *{get_total_users()}* مستخدم.\n\n"
            f"أرسل نص الرسالة:",
            parse_mode=ParseMode.MARKDOWN)

    elif d == "sync_stock":
        await query.edit_message_text("⏳ جاري مزامنة المخزون...", parse_mode=ParseMode.MARKDOWN)
        low = get_low_stock()
        out = get_out_of_stock()
        text = (
            f"✅ *تمت المزامنة*\n\n"
            f"⚠️ مخزون منخفض: {len(low)} منتج\n"
            f"❌ نفد مخزونه: {len(out)} منتج\n\n"
        )
        if low:
            text += "📋 *تحتاج إعادة تخزين:*\n"
            for p in low:
                text += f"• {p.get('name_ar','')} — {p.get('stock',0)} وحدة\n"
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN,
                                       reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙",callback_data="back_main")]]))

# ══════════════════════════════════════════════════════════════════
# AUTO ALERTS (scheduled job)
# ══════════════════════════════════════════════════════════════════

async def daily_report_job(ctx: ContextTypes.DEFAULT_TYPE):
    """تقرير يومي تلقائي للمدير."""
    if not ADMIN_ID: return
    s    = get_analytics_summary()
    low  = get_low_stock()
    report = (
        f"📊 *التقرير اليومي — {datetime.now().strftime('%Y-%m-%d')}*\n\n"
        f"👥 المستخدمون: {s['total_users']}\n"
        f"📦 الطلبات اليوم: {s['total_orders']}\n"
        f"💰 الإيرادات: ${s['total_revenue']:,.2f}\n"
        f"⚠️ مخزون منخفض: {len(low)} منتج"
    )
    try:
        await ctx.bot.send_message(chat_id=ADMIN_ID, text=report, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        log.error(f"Daily report: {e}")

async def low_stock_alert_job(ctx: ContextTypes.DEFAULT_TYPE):
    """تنبيه مخزون منخفض كل 6 ساعات."""
    if not ADMIN_ID: return
    low = get_low_stock(threshold=3)
    if low:
        text = f"⚠️ *تنبيه: مخزون منخفض جداً!*\n\n"
        for p in low:
            text += f"• {p.get('name_ar','')} — {p.get('stock',0)} وحدة فقط!\n"
        try:
            await ctx.bot.send_message(chat_id=ADMIN_ID, text=text, parse_mode=ParseMode.MARKDOWN)
        except: pass

# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

def main():
    if not TOKEN:
        print("❌ ADMIN_BOT_TOKEN or TELEGRAM_TOKEN missing!")
        return

    init_db()
    print(f"👑 Admin Bot starting...")

    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start",        cmd_start))
    app.add_handler(CommandHandler("stats",        cmd_stats))
    app.add_handler(CommandHandler("broadcast",    cmd_broadcast))
    app.add_handler(CommandHandler("add",          cmd_add_product))
    app.add_handler(CommandHandler("update_order", cmd_update_order))

    # Callbacks & Messages
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Scheduled jobs
    jq = app.job_queue
    if jq:
        jq.run_daily(daily_report_job, time=datetime.strptime("08:00","%H:%M").time())
        jq.run_repeating(low_stock_alert_job, interval=21600)  # every 6h

    print(f"✅ Admin Bot running! Admin: {ADMIN_ID}")
    app.run_polling(allowed_updates=["message","callback_query"], drop_pending_updates=True)

if __name__ == "__main__":
    main()
