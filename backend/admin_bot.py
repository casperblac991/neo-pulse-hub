# -*- coding: utf-8 -*-
import os, json, logging, csv
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
ADMIN_USER_ID   = int(os.environ.get("ADMIN_USER_ID", "0"))
BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
PRODUCTS_FILE   = os.path.join(BASE_DIR, "products.json")
ORDERS_FILE     = os.path.join(BASE_DIR, "orders.json")
LEADS_FILE      = os.path.join(BASE_DIR, "leads.json")

log = logging.getLogger("admin_bot")

def is_admin(uid):
    return ADMIN_USER_ID and int(uid) == ADMIN_USER_ID

def load_json(path, default):
    try:
        p = Path(path)
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default
    except:
        return default

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ عذراً، هذا البوت مخصص للمديرين فقط.")
        return
    
    await update.message.reply_text(
        "🛡️ *مرحباً بك في لوحة تحكم NEO PULSE HUB*\n\n"
        "يمكنك إدارة المتجر وتنزيل التقارير من هنا.\n\n"
        "📋 *الأوامر المتاحة:*\n"
        "• /stats - إحصائيات المتجر\n"
        "• /report - تنزيل تقرير المراجعات (CSV)\n"
        "• /orders - آخر الطلبات\n"
        "• /products - حالة المخزون\n"
        "• /broadcast [رسالة] - إرسال لكل المشتركين",
        parse_mode=ParseMode.MARKDOWN
    )

async def cmd_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    
    products = load_json(PRODUCTS_FILE, [])
    orders = load_json(ORDERS_FILE, {"orders": [], "total_revenue": 0})
    leads = load_json(LEADS_FILE, {"users": []})
    
    msg = (
        "📊 *إحصائيات المتجر الحالية:*\n\n"
        f"📦 عدد المنتجات: {len(products)}\n"
        f"🛒 إجمالي الطلبات: {len(orders.get('orders', []))}\n"
        f"💰 إجمالي الإيرادات: ${orders.get('total_revenue', 0)}\n"
        f"👥 عدد المشتركين: {len(leads.get('users', []))}\n"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

async def cmd_report(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """توليد وتنزيل تقرير المراجعات والمنتجات"""
    if not is_admin(update.effective_user.id): return
    
    await update.message.reply_text("⏳ جاري توليد التقارير (CSV & PDF)...")
    
    products = load_json(PRODUCTS_FILE, [])
    csv_path = os.path.join(BASE_DIR, "store_report.csv")
    
    try:
        # 1. Generate CSV
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'المنتج', 'السعر', 'التقييم', 'الفئة', 'رابط أمازون'])
            for p in products:
                writer.writerow([
                    p.get('id', ''),
                    p.get('name', {}).get('ar', ''),
                    p.get('price', 0),
                    p.get('rating', 0),
                    p.get('category', ''),
                    p.get('affiliate_amazon', '')
                ])
        
        await update.message.reply_document(
            document=open(csv_path, 'rb'),
            filename=f"NPH_Report_{datetime.now().strftime('%Y%m%d')}.csv",
            caption="📊 تقرير CSV جاهز."
        )

        # 2. Generate PDF
        try:
            from generate_pdf_report import generate_pdf
            pdf_path = generate_pdf()
            if pdf_path and os.path.exists(pdf_path):
                await update.message.reply_document(
                    document=open(pdf_path, 'rb'),
                    filename=f"NPH_Analysis_{datetime.now().strftime('%Y%m%d')}.pdf",
                    caption="📄 تقرير التحليل PDF جاهز."
                )
        except Exception as pe:
            log.error(f"PDF generation error: {pe}")
            
    except Exception as e:
        log.error(f"Report error: {e}")
        await update.message.reply_text(f"❌ فشل توليد التقرير: {e}")

async def cmd_orders(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    orders_data = load_json(ORDERS_FILE, {"orders": []})
    orders = orders_data.get("orders", [])[:5]
    
    if not orders:
        await update.message.reply_text("📭 لا توجد طلبات حالياً.")
        return
        
    msg = "🛒 *آخر 5 طلبات:*\n\n"
    for o in orders:
        msg += f"🔹 طلب #{o['id']}\n   المنتج: {o['product']}\n   المبلغ: ${o['total']}\n\n"
    
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

async def cmd_products(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    products = load_json(PRODUCTS_FILE, [])
    low_stock = [p for p in products if p.get('stock', 10) < 5]
    
    msg = f"📦 *حالة المخزون:*\n\nإجمالي المنتجات: {len(products)}\n"
    if low_stock:
        msg += f"⚠️ تنبيه: {len(low_stock)} منتجات مخزونها منخفض!"
    else:
        msg += "✅ جميع المنتجات متوفرة بشكل جيد."
        
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

async def cmd_broadcast(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    
    text = " ".join(ctx.args)
    if not text:
        await update.message.reply_text("❌ يرجى كتابة الرسالة بعد الأمر. مثال: /broadcast عرض جديد!")
        return
        
    leads = load_json(LEADS_FILE, {"users": []})
    users = leads.get("users", [])
    
    await update.message.reply_text(f"📢 جاري إرسال الرسالة إلى {len(users)} مشترك...")
    
    # في الواقع سنحتاج لبوت العملاء للإرسال للمستخدمين
    # هنا فقط محاكاة أو استخدام توكن بوت العملاء إذا كان متاحاً
    await update.message.reply_text("✅ تمت العملية (محاكاة - يتطلب ربط توكن بوت العملاء للإرسال الفعلي).")

async def error_handler(update, ctx: ContextTypes.DEFAULT_TYPE):
    log.error(f"Error: {ctx.error}")

def _register_handlers(app):
    app.add_handler(CommandHandler("start",      cmd_start))
    app.add_handler(CommandHandler("stats",      cmd_stats))
    app.add_handler(CommandHandler("report",     cmd_report))
    app.add_handler(CommandHandler("orders",     cmd_orders))
    app.add_handler(CommandHandler("products",   cmd_products))
    app.add_handler(CommandHandler("broadcast",  cmd_broadcast))
    app.add_error_handler(error_handler)

if __name__ == "__main__":
    if not ADMIN_BOT_TOKEN:
        print("❌ ADMIN_BOT_TOKEN missing!"); exit(1)
    app = Application.builder().token(ADMIN_BOT_TOKEN).build()
    _register_handlers(app)
    print("🛡️ Admin Bot running...")
    app.run_polling(drop_pending_updates=True)
