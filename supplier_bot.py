#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO PULSE HUB — Supplier Bot v2.0
✅ SUPPLIER_BOT_TOKEN (صح)
✅ _register_handlers (للـ webhook)
✅ auto_add_products (للـ scheduler في main.py)
✅ Gemini يولّد بيانات المنتج
✅ github_sync لرفع products.json
"""
import os, json, logging, random
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

SUPPLIER_BOT_TOKEN = os.environ.get("SUPPLIER_BOT_TOKEN", "")
GEMINI_API_KEY     = (os.environ.get("GEMINI_API_KEY") or
                      os.environ.get("GOOGLE_API_KEY") or "")
ADMIN_USER_ID      = int(os.environ.get("ADMIN_USER_ID", "0"))
GITHUB_TOKEN       = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO        = os.environ.get("GITHUB_REPO", "casperblac991/neo-pulse-hub")
BASE_DIR           = os.path.dirname(os.path.abspath(__file__))
PRODUCTS_FILE      = os.path.join(BASE_DIR, "products.json")

log = logging.getLogger("supplier_bot")

# ── Data ───────────────────────────────────────────────────────
def load_products():
    try:
        p = Path(PRODUCTS_FILE)
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []
    except:
        return []

def save_products(products):
    try:
        Path(PRODUCTS_FILE).write_text(
            json.dumps(products, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return True
    except Exception as e:
        log.error(f"save_products: {e}"); return False

def push_to_github(products):
    """يرفع products.json على GitHub"""
    if not GITHUB_TOKEN or not GITHUB_REPO:
        log.warning("GitHub credentials missing — skipping push")
        return False
    import requests as _r, base64
    try:
        api = f"https://api.github.com/repos/{GITHUB_REPO}/contents/products.json"
        headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

        # احصل على SHA الحالي
        r = _r.get(api, headers=headers, timeout=10)
        sha = r.json().get("sha", "") if r.status_code == 200 else ""

        content = json.dumps(products, ensure_ascii=False, indent=2)
        encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")

        payload = {
            "message": f"🤖 Auto-add products — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "content": encoded,
            "branch": "main"
        }
        if sha:
            payload["sha"] = sha

        r2 = _r.put(api, headers=headers, json=payload, timeout=15)
        if r2.status_code in (200, 201):
            log.info("✅ products.json pushed to GitHub")
            return True
        else:
            log.error(f"GitHub push failed: {r2.status_code} {r2.text[:200]}")
            return False
    except Exception as e:
        log.error(f"push_to_github: {e}"); return False

# ── Gemini ─────────────────────────────────────────────────────
def ask_gemini(prompt: str) -> str:
    if not GEMINI_API_KEY:
        log.error("GEMINI_API_KEY is MISSING in environment variables!")
        return ""
    import requests as _r
    try:
        url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
               f"gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}")
        body = {"contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.7, "maxOutputTokens": 2000}}
        resp = _r.post(url, json=body, timeout=20)
        if resp.status_code != 200:
            log.error(f"Gemini HTTP {resp.status_code}: {resp.text[:200]}")
            return ""
        data = resp.json()
        # فحص safety blocks
        candidates = data.get("candidates", [])
        if not candidates:
            reason = data.get("promptFeedback", {}).get("blockReason", "unknown")
            log.error(f"Gemini no candidates, blockReason: {reason}")
            return ""
        text = (candidates[0].get("content", {})
                              .get("parts", [{}])[0]
                              .get("text", ""))
        if not text:
            log.error(f"Gemini empty text. Full response: {str(data)[:200]}")
        return text
    except Exception as e:
        log.error(f"Gemini exception: {e}")
        return ""

CATEGORIES = [
    {"id": "smartwatch",    "ar": "ساعات ذكية",    "en": "Smart Watches"},
    {"id": "smart-glasses", "ar": "نظارات ذكية",   "en": "Smart Glasses"},
    {"id": "health",        "ar": "صحة ولياقة",    "en": "Health & Fitness"},
    {"id": "smart-home",    "ar": "منزل ذكي",      "en": "Smart Home"},
    {"id": "earbuds",       "ar": "سماعات ذكية",   "en": "Smart Earbuds"},
    {"id": "productivity",  "ar": "إنتاجية",       "en": "Productivity"},
]

PRODUCT_IMAGES = {
    "smartwatch":    "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=600&q=80",
    "smart-glasses": "https://images.unsplash.com/photo-1574258495973-f010dfbb5371?w=600&q=80",
    "health":        "https://images.unsplash.com/photo-1559757175-5700dde675bc?w=600&q=80",
    "smart-home":    "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&q=80",
    "earbuds":       "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&q=80",
    "productivity":  "https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=600&q=80",
}

def generate_product_with_ai(category):
    """يستخدم Gemini لتوليد بيانات منتج جديد"""
    cat_ar = category.get("ar", "")
    cat_en = category.get("en", "")
    prompt = (
        "Generate a realistic tech product for category: " + cat_en + "\n"
        "Respond with ONLY valid JSON, no extra text, no markdown:\n"
        "{"
        '"name_ar":"اسم المنتج بالعربية",'
        '"name_en":"Product Name in English",'
        '"price":199,'
        '"original_price":249,'
        '"discount":17,'
        '"rating":4.7,'
        '"reviews":1500,'
        '"description_ar":"وصف تسويقي جذاب بالعربية جملتان",'
        '"description_en":"Two sentences marketing description in English",'
        '"features_ar":["ميزة 1","ميزة 2","ميزة 3","ميزة 4"],'
        '"features_en":["Feature 1","Feature 2","Feature 3","Feature 4"],'
        '"badge":"جديد",'
        '"badge_en":"New",'
        '"shipping_days":5'
        "}\n"
        "Rules: price between 50-500 USD, realistic product name, category: " + cat_ar
    )

    raw = ask_gemini(prompt)
    if not raw:
        log.warning("Gemini returned empty for " + cat_ar)
        return None

    import re as _re
    # تنظيف markdown
    cleaned = raw.strip()
    cleaned = _re.sub(r"```(?:json)?\s*", "", cleaned).strip()
    cleaned = cleaned.strip("`").strip()

    # استخرج JSON
    match = _re.search(r"\{[\s\S]*\}", cleaned)
    if not match:
        match = _re.search(r"\{[\s\S]+", cleaned)
        if not match:
            log.warning("No JSON in response: " + raw[:100])
            return None

    fragment = match.group()
    try:
        return json.loads(fragment)
    except Exception:
        # إصلاح JSON ناقص
        if fragment.count('"') % 2 == 1:
            fragment += '"'
        open_arr  = fragment.count("[")
        close_arr = fragment.count("]")
        if open_arr > close_arr:
            fragment += "]" * (open_arr - close_arr)
        open_b  = fragment.count("{")
        close_b = fragment.count("}")
        if open_b > close_b:
            fragment += "}" * (open_b - close_b)
        try:
            return json.loads(fragment)
        except Exception as e:
            log.error("JSON parse failed " + cat_ar + ": " + str(e))
            return None


def create_product(data: dict, category: dict, new_id: str) -> dict:
    """يبني المنتج الكامل"""
    return {
        "id": new_id,
        "name_ar": data.get("name_ar", "منتج جديد"),
        "name_en": data.get("name_en", "New Product"),
        "category": category["id"],
        "category_ar": category["ar"],
        "category_en": category["en"],
        "price": int(data.get("price", 199)),
        "original_price": int(data.get("original_price", 0)) or None,
        "discount": int(data.get("discount", 0)),
        "rating": float(data.get("rating", 4.5)),
        "reviews": int(data.get("reviews", 100)),
        "stock": random.randint(10, 100),
        "image": PRODUCT_IMAGES.get(category["id"], PRODUCT_IMAGES["smartwatch"]),
        "badge": data.get("badge", "جديد"),
        "badge_en": data.get("badge_en", "New"),
        "active": True,
        "featured": False,
        "description_ar": data.get("description_ar", ""),
        "description_en": data.get("description_en", ""),
        "features_ar": data.get("features_ar", []),
        "features_en": data.get("features_en", []),
        "tags": [category["id"], "smart", "tech"],
        "shipping_days": int(data.get("shipping_days", 5)),
        "added_at": datetime.now().isoformat(),
        "added_by": "auto_ai"
    }

# ══════════════════════════════════════════════════════════════
# auto_add_products — يُستدعى من main.py scheduler
# ══════════════════════════════════════════════════════════════
def auto_add_products(count: int = 5) -> list:
    """يضيف count منتجات جديدة بالذكاء الاصطناعي ويرفعها على GitHub"""
    products = load_products()
    existing_ids = {p.get("id", "") for p in products}

    # احسب الـ ID التالي
    nums = []
    import re
    for pid in existing_ids:
        m = re.match(r'NPH-(\d+)', pid)
        if m:
            nums.append(int(m.group(1)))
    next_num = max(nums, default=0) + 1

    added = []
    cats_cycle = CATEGORIES * 2  # دوّر على الفئات

    for i in range(count):
        cat = cats_cycle[i % len(CATEGORIES)]
        new_id = f"NPH-{next_num + i:03d}"

        log.info(f"Generating product {new_id} in {cat['ar']}...")
        data = generate_product_with_ai(cat)

        if data:
            product = create_product(data, cat, new_id)
            products.append(product)
            added.append(product)
            log.info(f"✅ Added: {product['name_ar']}")
        else:
            log.warning(f"⚠️ Failed to generate product for {cat['ar']}")

    if added:
        save_products(products)
        push_to_github(products)

    return added

# ── Bot Handlers ───────────────────────────────────────────────
def is_admin(uid):
    return ADMIN_USER_ID and int(uid) == ADMIN_USER_ID

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ غير مصرح.")
        return
    await update.message.reply_text(
        "🏭 *بوت الموردين — NEO PULSE HUB*\n\n"
        "/add — إضافة منتجات AI تلقائياً\n"
        "/report — تقرير المخزون\n"
        "/lowstock — منتجات المخزون المنخفض",
        parse_mode=ParseMode.MARKDOWN
    )

async def cmd_add(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    args = ctx.args
    count = int(args[0]) if args and args[0].isdigit() else 3

    msg = await update.message.reply_text(f"🤖 جاري توليد {count} منتجات بالذكاء الاصطناعي...")
    added = auto_add_products(count=count)

    if added:
        lines = "\n".join([
            f"✅ *{p['name_ar']}* — ${p['price']} | {p['id']}"
            for p in added
        ])
        await msg.edit_text(
            f"🎉 *تم إضافة {len(added)} منتجات:*\n\n{lines}\n\n✅ رُفعت على GitHub",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await msg.edit_text("❌ فشل توليد المنتجات. تحقق من GEMINI_API_KEY.")

async def cmd_report(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    products = load_products()
    active   = [p for p in products if p.get("active", True)]
    cats     = {}
    for p in active:
        c = p.get("category_ar", "أخرى")
        cats[c] = cats.get(c, 0) + 1
    lines = "\n".join([f"• {k}: {v} منتج" for k, v in cats.items()])
    total_val = sum(p.get("price", 0) * p.get("stock", 0) for p in active)
    await update.message.reply_text(
        f"📊 *تقرير المخزون*\n\n"
        f"إجمالي المنتجات: {len(products)}\n"
        f"المنتجات النشطة: {len(active)}\n"
        f"قيمة المخزون: ${total_val:,}\n\n"
        f"*توزيع الفئات:*\n{lines}",
        parse_mode=ParseMode.MARKDOWN
    )

async def cmd_lowstock(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    products = load_products()
    low = [p for p in products if p.get("stock", 50) <= 5 and p.get("active", True)]
    if not low:
        await update.message.reply_text("✅ لا توجد منتجات بمخزون منخفض.")
        return
    lines = "\n".join([
        f"⚠️ *{p['name_ar']}* — {p.get('stock',0)} قطعة | {p.get('id','')}"
        for p in low[:10]
    ])
    await update.message.reply_text(
        f"⚠️ *منتجات المخزون المنخفض ({len(low)}):*\n\n{lines}",
        parse_mode=ParseMode.MARKDOWN
    )

async def error_handler(update, ctx: ContextTypes.DEFAULT_TYPE):
    log.error(f"Supplier bot error: {ctx.error}")

# ✅ يُستدعى من main.py
def _register_handlers(app):
    app.add_handler(CommandHandler("start",    cmd_start))
    app.add_handler(CommandHandler("add",      cmd_add))
    app.add_handler(CommandHandler("report",   cmd_report))
    app.add_handler(CommandHandler("lowstock", cmd_lowstock))
    app.add_error_handler(error_handler)

if __name__ == "__main__":
    if not SUPPLIER_BOT_TOKEN:
        print("❌ SUPPLIER_BOT_TOKEN missing!"); exit(1)
    app = Application.builder().token(SUPPLIER_BOT_TOKEN).build()
    _register_handlers(app)
    print("🏭 Supplier Bot running...")
    app.run_polling(drop_pending_updates=True)
