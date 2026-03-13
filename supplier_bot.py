#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO PULSE HUB — Supplier Bot v3.0
✅ تجديد تلقائي كل 6 ساعات
✅ يحذف المنتجات القديمة ويضيف جديدة
✅ صور حقيقية من Unsplash
✅ Gemini يولّد بيانات المنتج
✅ إشعار أدمين بعد كل تجديد
"""
import os, json, logging, random, time
from datetime import datetime
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Application, CommandHandler,
                           filters, ContextTypes)
from telegram.constants import ParseMode

try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass

SUPPLIER_BOT_TOKEN  = os.environ.get("SUPPLIER_BOT_TOKEN", "")
GEMINI_API_KEY      = (os.environ.get("GEMINI_API_KEY") or
                       os.environ.get("GOOGLE_API_KEY") or "")
ADMIN_USER_ID       = int(os.environ.get("ADMIN_USER_ID", "0"))
GITHUB_TOKEN        = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO         = os.environ.get("GITHUB_REPO", "casperblac991/neo-pulse-hub")
BASE_DIR            = os.path.dirname(os.path.abspath(__file__))
PRODUCTS_FILE       = os.path.join(BASE_DIR, "products.json")

log = logging.getLogger("supplier_bot")

# ── Data ────────────────────────────────────────────────────────
def load_products():
    try:
        p = Path(PRODUCTS_FILE)
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []
    except Exception as e:
        log.error(f"load_products: {e}"); return []

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
        log.warning("GitHub credentials missing"); return False
    import requests as _r, base64
    try:
        api = f"https://api.github.com/repos/{GITHUB_REPO}/contents/products.json"
        headers = {"Authorization": f"token {GITHUB_TOKEN}",
                   "Accept": "application/vnd.github.v3+json"}
        r = _r.get(api, headers=headers, timeout=10)
        sha = r.json().get("sha", "") if r.status_code == 200 else ""
        content = json.dumps(products, ensure_ascii=False, indent=2)
        encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        payload = {
            "message": f"🔄 Auto-refresh — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "content": encoded, "branch": "main"
        }
        if sha:
            payload["sha"] = sha
        r2 = _r.put(api, headers=headers, json=payload, timeout=20)
        if r2.status_code in (200, 201):
            log.info("✅ GitHub pushed OK"); return True
        log.error(f"GitHub push {r2.status_code}: {r2.text[:100]}")
        return False
    except Exception as e:
        log.error(f"push_to_github: {e}"); return False


CATEGORIES = [
    {"id": "smartwatch",    "ar": "ساعات ذكية",  "en": "Smart Watches"},
    {"id": "smart-glasses", "ar": "نظارات ذكية", "en": "Smart Glasses AR"},
    {"id": "health",        "ar": "صحة ولياقة",  "en": "Health & Fitness"},
    {"id": "smart-home",    "ar": "منزل ذكي",    "en": "Smart Home"},
    {"id": "earbuds",       "ar": "سماعات ذكية", "en": "Smart Earbuds"},
    {"id": "productivity",  "ar": "إنتاجية",     "en": "Productivity Tech"},
]

IMAGE_LIBRARY = {
    "smartwatch": [
        "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=600&q=80",
        "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&q=80",
        "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=600&q=80",
        "https://images.unsplash.com/photo-1617043786394-f977fa12eddf?w=600&q=80",
        "https://images.unsplash.com/photo-1434494878577-86c23bcb06b9?w=600&q=80",
        "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=600&q=80",
        "https://images.unsplash.com/photo-1544117519-31a4b719223d?w=600&q=80",
        "https://images.unsplash.com/photo-1551816230-ef5deaed4a26?w=600&q=80",
        "https://images.unsplash.com/photo-1630989809082-9e2f671d56db?w=600&q=80",
        "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=600&q=80",
        "https://images.unsplash.com/photo-1461141346587-763ab02bced9?w=600&q=80",
        "https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=600&q=80",
        "https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?w=600&q=80",
        "https://images.unsplash.com/photo-1620625515032-6ed0c1790c75?w=600&q=80",
        "https://images.unsplash.com/photo-1541643600914-78b084683702?w=600&q=80",
        "https://images.unsplash.com/photo-1615655406736-b37c4fabf923?w=600&q=80",
        "https://images.unsplash.com/photo-1585366119957-e9730b6d0f60?w=600&q=80",
    ],
    "smart-glasses": [
        "https://images.unsplash.com/photo-1574258495973-f010dfbb5371?w=600&q=80",
        "https://images.unsplash.com/photo-1577803645773-f96470509666?w=600&q=80",
        "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=600&q=80",
        "https://images.unsplash.com/photo-1584543178269-0e3a22b95827?w=600&q=80",
        "https://images.unsplash.com/photo-1603400521630-9f2de124b33b?w=600&q=80",
        "https://images.unsplash.com/photo-1560343776-97e7d202ff0e?w=600&q=80",
        "https://images.unsplash.com/photo-1629904853716-f0bc54eea481?w=600&q=80",
        "https://images.unsplash.com/photo-1526374870839-e155464bb9b2?w=600&q=80",
        "https://images.unsplash.com/photo-1501159599894-155982264a55?w=600&q=80",
        "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=600&q=80",
        "https://images.unsplash.com/photo-1542219550-37153d387c27?w=600&q=80",
        "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=600&q=80",
    ],
    "health": [
        "https://images.unsplash.com/photo-1559757175-5700dde675bc?w=600&q=80",
        "https://images.unsplash.com/photo-1576678927484-cc907957088c?w=600&q=80",
        "https://images.unsplash.com/photo-1530026186672-2cd00ffc50fe?w=600&q=80",
        "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600&q=80",
        "https://images.unsplash.com/photo-1510771463146-e89e6e86560e?w=600&q=80",
        "https://images.unsplash.com/photo-1607962837359-5e7e89f86776?w=600&q=80",
        "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?w=600&q=80",
        "https://images.unsplash.com/photo-1549476464-37392f717541?w=600&q=80",
        "https://images.unsplash.com/photo-1434682772747-f16d3ea162c3?w=600&q=80",
        "https://images.unsplash.com/photo-1526506118085-60ce8714f8c5?w=600&q=80",
        "https://images.unsplash.com/photo-1540497077202-7c8a3999166f?w=600&q=80",
        "https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=600&q=80",
        "https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=600&q=80",
        "https://images.unsplash.com/photo-1532938911079-1b06ac7ceec7?w=600&q=80",
        "https://images.unsplash.com/photo-1594882645560-3e93f0b74e31?w=600&q=80",
    ],
    "smart-home": [
        "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=600&q=80",
        "https://images.unsplash.com/photo-1558002038-1055907df827?w=600&q=80",
        "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=600&q=80",
        "https://images.unsplash.com/photo-1567721913486-6585f069b332?w=600&q=80",
        "https://images.unsplash.com/photo-1484154218962-a197022b5858?w=600&q=80",
        "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&q=80",
        "https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=600&q=80",
        "https://images.unsplash.com/photo-1601924582970-9238bcb495d9?w=600&q=80",
        "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&q=80",
        "https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=600&q=80",
        "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=600&q=80",
        "https://images.unsplash.com/photo-1527430253228-e93688616381?w=600&q=80",
        "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=600&q=80",
        "https://images.unsplash.com/photo-1505843513577-22bb7d21e455?w=600&q=80",
        "https://images.unsplash.com/photo-1574944985070-8f3ebc6b79d2?w=600&q=80",
    ],
    "earbuds": [
        "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&q=80",
        "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=600&q=80",
        "https://images.unsplash.com/photo-1606220588913-b3aacb4d2f46?w=600&q=80",
        "https://images.unsplash.com/photo-1545127398-14699f92334b?w=600&q=80",
        "https://images.unsplash.com/photo-1610894636781-8e5b4dc4c3d9?w=600&q=80",
        "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=600&q=80",
        "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&q=80",
        "https://images.unsplash.com/photo-1524678606370-a47ad25cb82a?w=600&q=80",
        "https://images.unsplash.com/photo-1613040809024-b4ef7ba99bc3?w=600&q=80",
        "https://images.unsplash.com/photo-1585298723682-7115561c51b7?w=600&q=80",
        "https://images.unsplash.com/photo-1572536147248-ac59a8abegood?w=600&q=80",
        "https://images.unsplash.com/photo-1631867675167-90a456a90863?w=600&q=80",
        "https://images.unsplash.com/photo-1560393464-5c69a73c5770?w=600&q=80",
        "https://images.unsplash.com/photo-1625245488600-968c1e394821?w=600&q=80",
        "https://images.unsplash.com/photo-1608156639585-b3a032ef9689?w=600&q=80",
    ],
    "productivity": [
        "https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=600&q=80",
        "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=600&q=80",
        "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=600&q=80",
        "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=600&q=80",
        "https://images.unsplash.com/photo-1587614382346-4ec70e388b28?w=600&q=80",
        "https://images.unsplash.com/photo-1542744173-8e7e53415bb0?w=600&q=80",
        "https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=600&q=80",
        "https://images.unsplash.com/photo-1498049794561-7780e7231661?w=600&q=80",
        "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=600&q=80",
        "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=600&q=80",
        "https://images.unsplash.com/photo-1484788984921-03950022c9ef?w=600&q=80",
        "https://images.unsplash.com/photo-1581287053822-fd7bf4f4bfec?w=600&q=80",
        "https://images.unsplash.com/photo-1531297484001-80022131f5a1?w=600&q=80",
        "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=600&q=80",
        "https://images.unsplash.com/photo-1488590528505-98d2b5aba04b?w=600&q=80",
    ],
}

_used_images = {}  # لتجنب تكرار نفس الصورة

def fetch_image(category_id: str, product_name_en: str = "") -> str:
    """يجيب صورة حقيقية من Unsplash — بدون تكرار"""
    unsplash_key = os.environ.get("UNSPLASH_ACCESS_KEY", "")
    
    if unsplash_key:
        import requests as _r
        # كلمات بحث محددة لكل فئة
        kw = {
            "smartwatch":    product_name_en or "smartwatch wearable tech",
            "smart-glasses": product_name_en or "smart glasses AR technology",
            "health":        product_name_en or "fitness health wearable tracker",
            "smart-home":    product_name_en or "smart home device technology",
            "earbuds":       product_name_en or "wireless earbuds bluetooth audio",
            "productivity":  product_name_en or "laptop computer productivity tech",
        }
        query = kw.get(category_id, product_name_en or "tech gadget")
        try:
            r = _r.get(
                "https://api.unsplash.com/search/photos",
                params={
                    "query": query,
                    "per_page": 20,
                    "orientation": "squarish",
                    "content_filter": "high",
                    "client_id": unsplash_key
                },
                timeout=8
            )
            if r.status_code == 200:
                results = r.json().get("results", [])
                # تجنب الصور المستخدمة
                used = _used_images.get(category_id, [])
                unused = [p for p in results if p["urls"]["regular"] not in used]
                pool = unused if unused else results
                if pool:
                    photo = random.choice(pool[:8])
                    url = photo["urls"]["regular"] + "&w=600&q=80"
                    _used_images.setdefault(category_id, []).append(url)
                    return url
            else:
                log.warning(f"Unsplash {r.status_code}: {r.text[:80]}")
        except Exception as e:
            log.warning(f"Unsplash error: {e}")

    # fallback: مكتبة محلية بدون تكرار
    imgs = IMAGE_LIBRARY.get(category_id, list(IMAGE_LIBRARY.values())[0])
    used = _used_images.get(category_id, [])
    available = [img for img in imgs if img not in used]
    if not available:
        _used_images[category_id] = []
        available = imgs
    chosen = random.choice(available)
    _used_images.setdefault(category_id, []).append(chosen)
    return chosen


def ask_gemini(prompt: str) -> str:
    key = (os.environ.get("GEMINI_API_KEY") or
           os.environ.get("GOOGLE_API_KEY") or "")
    if not key:
        log.error("No Gemini key!"); return ""
    import requests as _r
    url = ("https://generativelanguage.googleapis.com/v1beta/models/"
           "gemini-2.5-flash:generateContent?key=" + key)
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.8,
            "maxOutputTokens": 2000,
            "thinkingConfig": {"thinkingBudget": 0}
        }
    }
    for attempt in range(3):
        try:
            resp = _r.post(url, json=body, timeout=30)
            if resp.status_code == 429:
                wait = 30 * (attempt + 1)
                log.warning(f"Rate limit, wait {wait}s")
                time.sleep(wait); continue
            if resp.status_code != 200:
                log.error(f"Gemini {resp.status_code}: {resp.text[:100]}")
                return ""
            data = resp.json()
            candidates = data.get("candidates", [])
            if not candidates: return ""
            parts = candidates[0].get("content", {}).get("parts", [])
            if not parts: return ""
            return parts[0].get("text", "")
        except Exception as e:
            log.error(f"Gemini attempt {attempt+1}: {e}")
            time.sleep(5)
    return ""

def generate_product_with_ai(category: dict):
    cat_ar = category.get("ar", "")
    cat_en = category.get("en", "")
    prompt = (
        "Generate a realistic premium tech product for: " + cat_en + "\n"
        "ONLY valid JSON, no markdown:\n"
        '{"name_ar":"اسم المنتج العربي","name_en":"Brand Product Name",'
        '"price":199,"original_price":249,"discount":17,'
        '"rating":4.7,"reviews":1500,'
        '"description_ar":"وصف تسويقي جذاب جملتان",'
        '"description_en":"Two exciting marketing sentences",'
        '"features_ar":["ميزة 1","ميزة 2","ميزة 3","ميزة 4"],'
        '"features_en":["Feature 1","Feature 2","Feature 3","Feature 4"],'
        '"badge":"جديد","badge_en":"New","shipping_days":5}\n'
        "Price: 50-450 USD. Use realistic brand-style names. Category: " + cat_ar
    )
    raw = ask_gemini(prompt)
    if not raw: return None
    import re as _re
    cleaned = _re.sub(r"```(?:json)?\s*", "", raw.strip()).strip().strip("`")
    match = _re.search(r"\{[\s\S]*\}", cleaned) or _re.search(r"\{[\s\S]+", cleaned)
    if not match: return None
    fragment = match.group()
    try:
        return json.loads(fragment)
    except:
        if fragment.count('"') % 2 == 1: fragment += '"'
        oa = fragment.count("["); ca = fragment.count("]")
        if oa > ca: fragment += "]" * (oa - ca)
        ob = fragment.count("{"); cb = fragment.count("}")
        if ob > cb: fragment += "}" * (ob - cb)
        try: return json.loads(fragment)
        except: return None

def create_product(data: dict, category: dict, new_id: str) -> dict:
    name_en = data.get("name_en", "Smart Device")
    return {
        "id": new_id,
        "name_ar": data.get("name_ar", "منتج ذكي"),
        "name_en": name_en,
        "category": category["id"],
        "category_ar": category["ar"],
        "category_en": category["en"],
        "price": int(data.get("price", 199)),
        "original_price": int(data.get("original_price", 0)) or None,
        "discount": int(data.get("discount", 0)),
        "rating": float(data.get("rating", 4.5)),
        "reviews": int(data.get("reviews", 100)),
        "stock": random.randint(15, 80),
        "image": fetch_image(category["id"], name_en),
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
        "added_by": "auto_ai_v3"
    }

def auto_add_products(count: int = 3) -> list:
    products = load_products()
    import re
    existing_ids = {p.get("id", "") for p in products}
    nums = [int(m.group(1)) for p in existing_ids
            if (m := re.match(r'NPH-(\d+)', p))]
    next_num = max(nums, default=100) + 1
    added = []
    for i in range(count):
        cat = CATEGORIES[i % len(CATEGORIES)]
        new_id = f"NPH-{next_num + i:03d}"
        log.info(f"Generating {new_id} — {cat['ar']}")
        data = generate_product_with_ai(cat)
        if data:
            product = create_product(data, cat, new_id)
            products.append(product)
            added.append(product)
            log.info(f"✅ {product['name_ar']}")
            time.sleep(10)
        else:
            log.warning(f"Failed: {cat['ar']}")
    if added:
        save_products(products)
        push_to_github(products)
    return added

def refresh_store(keep_per_cat: int = 12, add_per_cat: int = 3) -> dict:
    """
    يجدد المتجر كل 6 ساعات:
    1. يحتفظ بأفضل keep_per_cat منتج من كل فئة
    2. يحذف الباقي
    3. يضيف add_per_cat منتج جديد لكل فئة بصور جديدة
    """
    products = load_products()
    log.info(f"🔄 Refresh start — {len(products)} products")

    new_store = []
    deleted_count = 0

    for cat in CATEGORIES:
        cat_prods = [p for p in products if p.get("category") == cat["id"]]
        cat_prods.sort(
            key=lambda x: x.get("rating", 0) * 1000 + x.get("reviews", 0),
            reverse=True
        )
        kept = cat_prods[:keep_per_cat]
        deleted_count += len(cat_prods) - len(kept)
        new_store.extend(kept)
        log.info(f"  {cat['ar']}: kept {len(kept)}, removed {len(cat_prods)-len(kept)}")

    import re
    existing_ids = {p.get("id", "") for p in new_store}
    nums = [int(m.group(1)) for p in existing_ids
            if (m := re.match(r'NPH-(\d+)', p))]
    next_num = max(nums, default=100) + 1

    added_products = []
    for cat in CATEGORIES:
        for j in range(add_per_cat):
            new_id = f"NPH-{next_num:03d}"
            next_num += 1
            log.info(f"  New {new_id} — {cat['ar']}")
            data = generate_product_with_ai(cat)
            if data:
                product = create_product(data, cat, new_id)
                new_store.append(product)
                added_products.append(product)
                log.info(f"  ✅ {product['name_ar']}")
            time.sleep(10)

    save_products(new_store)
    push_to_github(new_store)

    result = {
        "total": len(new_store),
        "deleted": deleted_count,
        "added": len(added_products),
        "new_products": added_products
    }
    log.info(f"✅ Refresh done: +{len(added_products)} -{deleted_count}")
    return result

def notify_admin_refresh(result: dict):
    token = os.environ.get("ADMIN_BOT_TOKEN", "")
    if not ADMIN_USER_ID or not token: return
    import requests as _r
    new_names = "\n".join([
        f"• {p['name_ar']} — ${p['price']}"
        for p in result.get("new_products", [])[:8]
    ])
    msg = (
        f"🔄 *تجديد المتجر التلقائي*\n\n"
        f"🗑️ حُذف: {result['deleted']} منتج قديم\n"
        f"✅ أُضيف: {result['added']} منتج جديد\n"
        f"📦 المجموع: {result['total']} منتج\n\n"
        f"*الجديد:*\n{new_names}\n\n"
        f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    try:
        _r.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": ADMIN_USER_ID, "text": msg, "parse_mode": "Markdown"},
            timeout=8
        )
    except Exception as e:
        log.error(f"notify: {e}")

def is_admin(uid):
    return ADMIN_USER_ID and int(uid) == ADMIN_USER_ID

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ غير مصرح."); return
    await update.message.reply_text(
        "🏭 *بوت الموردين v3 — NEO PULSE HUB*\n\n"
        "/add [عدد] — إضافة منتجات جديدة\n"
        "/refresh — تجديد المتجر الآن\n"
        "/report — تقرير المخزون\n"
        "/lowstock — مخزون منخفض\n\n"
        "⏰ *التجديد التلقائي:* كل 6 ساعات",
        parse_mode=ParseMode.MARKDOWN
    )

async def cmd_add(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    args = ctx.args
    count = min(int(args[0]) if args and args[0].isdigit() else 3, 3)
    msg = await update.message.reply_text(
        f"🤖 جاري توليد {count} منتجات... (دقيقة تقريباً)"
    )
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
        await msg.edit_text("⚠️ Rate Limit — انتظر دقيقتين وحاول مجدداً.")

async def cmd_refresh(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    msg = await update.message.reply_text(
        "🔄 *تجديد المتجر...*\n"
        "• حذف المنتجات الأقل تقييماً\n"
        "• إضافة منتجات جديدة بصور حقيقية\n"
        "⏳ 3-5 دقائق...",
        parse_mode=ParseMode.MARKDOWN
    )
    result = refresh_store(keep_per_cat=14, add_per_cat=1)
    new_names = "\n".join([
        f"• {p['name_ar']} — ${p['price']}"
        for p in result.get("new_products", [])[:8]
    ])
    await msg.edit_text(
        f"✅ *تم تجديد المتجر!*\n\n"
        f"🗑️ حُذف: {result['deleted']} منتج\n"
        f"✅ أُضيف: {result['added']} منتج\n"
        f"📦 المجموع: {result['total']} منتج\n\n"
        f"*الجديد:*\n{new_names}",
        parse_mode=ParseMode.MARKDOWN
    )

async def cmd_report(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    products = load_products()
    active = [p for p in products if p.get("active", True)]
    cats = {}
    for p in active:
        c = p.get("category_ar", "أخرى")
        cats[c] = cats.get(c, 0) + 1
    lines = "\n".join([f"• {k}: {v} منتج" for k, v in cats.items()])
    total_val = sum(p.get("price", 0) * p.get("stock", 0) for p in active)
    await update.message.reply_text(
        f"📊 *تقرير المخزون*\n\n"
        f"الإجمالي: {len(products)} | نشط: {len(active)}\n"
        f"قيمة المخزون: ${total_val:,}\n\n{lines}\n\n"
        f"⏰ تجديد تلقائي كل 6 ساعات",
        parse_mode=ParseMode.MARKDOWN
    )

async def cmd_lowstock(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    products = load_products()
    low = [p for p in products if p.get("stock", 50) <= 5 and p.get("active", True)]
    if not low:
        await update.message.reply_text("✅ لا توجد منتجات بمخزون منخفض."); return
    lines = "\n".join([
        f"⚠️ *{p['name_ar']}* — {p.get('stock',0)} قطعة | {p.get('id','')}"
        for p in low[:10]
    ])
    await update.message.reply_text(
        f"⚠️ *مخزون منخفض ({len(low)}):*\n\n{lines}",
        parse_mode=ParseMode.MARKDOWN
    )

async def error_handler(update, ctx: ContextTypes.DEFAULT_TYPE):
    log.error(f"Supplier bot error: {ctx.error}")

def _register_handlers(app):
    app.add_handler(CommandHandler("start",    cmd_start))
    app.add_handler(CommandHandler("add",      cmd_add))
    app.add_handler(CommandHandler("refresh",  cmd_refresh))
    app.add_handler(CommandHandler("report",   cmd_report))
    app.add_handler(CommandHandler("lowstock", cmd_lowstock))
    app.add_error_handler(error_handler)

if __name__ == "__main__":
    if not SUPPLIER_BOT_TOKEN:
        print("❌ SUPPLIER_BOT_TOKEN missing!"); exit(1)
    app = Application.builder().token(SUPPLIER_BOT_TOKEN).build()
    _register_handlers(app)
    print("🏭 Supplier Bot v3 running...")
    app.run_polling(drop_pending_updates=True)
