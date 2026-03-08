#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════╗
║   NEO PULSE HUB — Shared Database Layer                        ║
║   قاعدة البيانات المشتركة بين جميع البوتات                     ║
║                                                                  ║
║   يُستخدم من: customer_bot, admin_bot, recommendation_bot,     ║
║               supplier_bot, smart_product_bot                   ║
╚══════════════════════════════════════════════════════════════════╝
"""

import json, os, fcntl, logging
from pathlib import Path
from datetime import datetime
from typing import Optional

log = logging.getLogger("shared_db")

# ── Paths (relative to bots/ folder, data in parent) ──────────────
BASE = Path(__file__).parent.parent
DB   = {
    "products":  BASE / "products.json",
    "orders":    BASE / "orders.json",
    "leads":     BASE / "leads.json",
    "faqs":      BASE / "faqs.json",
    "cart":      BASE / "carts.json",
    "analytics": BASE / "analytics.json",
    "suppliers": BASE / "suppliers.json",
    "reviews":   BASE / "reviews.json",
    "newsletter":BASE / "newsletter.json",
}

# ══════════════════════════════════════════════════════════════════
# LOW-LEVEL JSON I/O (thread-safe with file locking)
# ══════════════════════════════════════════════════════════════════

def _read(path: Path, default):
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                fcntl.flock(f, fcntl.LOCK_SH)
                data = json.load(f)
                fcntl.flock(f, fcntl.LOCK_UN)
                return data
    except Exception as e:
        log.error(f"read {path.name}: {e}")
    return default() if callable(default) else default

def _write(path: Path, data):
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            json.dump(data, f, ensure_ascii=False, indent=2)
            fcntl.flock(f, fcntl.LOCK_UN)
        tmp.replace(path)  # atomic replace
    except Exception as e:
        log.error(f"write {path.name}: {e}")

# ══════════════════════════════════════════════════════════════════
# PRODUCTS
# ══════════════════════════════════════════════════════════════════

def get_products() -> list:
    return _read(DB["products"], list)

def get_product(pid: str) -> Optional[dict]:
    return next((p for p in get_products() if p["id"] == pid), None)

def save_products(products: list):
    _write(DB["products"], products)

def add_product(product: dict) -> dict:
    products = get_products()
    # Auto-generate ID
    ids = [p.get("id","") for p in products]
    n   = len(products) + 1
    while f"NPH-{n:03d}" in ids: n += 1
    product["id"]       = f"NPH-{n:03d}"
    product["added_at"] = datetime.now().isoformat()
    product["active"]   = True
    products.append(product)
    save_products(products)
    log.info(f"Product added: {product['id']} — {product.get('name_ar','')}")
    return product

def update_product(pid: str, updates: dict) -> bool:
    products = get_products()
    for i, p in enumerate(products):
        if p["id"] == pid:
            products[i].update(updates)
            products[i]["updated_at"] = datetime.now().isoformat()
            save_products(products)
            return True
    return False

def get_products_by_category(cat: str) -> list:
    return [p for p in get_products() if p.get("category") == cat and p.get("active", True)]

def search_products(query: str) -> list:
    q = query.lower()
    return [p for p in get_products()
            if q in p.get("name_ar","").lower()
            or q in p.get("name_en","").lower()
            or q in p.get("category","").lower()
            or any(q in f.lower() for f in p.get("features_ar",[]))]

def get_low_stock(threshold=5) -> list:
    return [p for p in get_products() if 0 < p.get("stock",99) <= threshold]

def get_out_of_stock() -> list:
    return [p for p in get_products() if p.get("stock",1) == 0]

def get_featured_products(n=6) -> list:
    active = [p for p in get_products() if p.get("active", True)]
    return sorted(active, key=lambda x: x.get("rating",0), reverse=True)[:n]

# ══════════════════════════════════════════════════════════════════
# ORDERS
# ══════════════════════════════════════════════════════════════════

def get_orders() -> dict:
    return _read(DB["orders"], lambda: {"orders":[], "total_revenue":0})

def get_order(oid: str) -> Optional[dict]:
    return next((o for o in get_orders()["orders"] if o["id"] == oid), None)

def create_order(product_id: str, user_id: int, qty: int = 1,
                 payment_method: str = "paypal") -> dict:
    product = get_product(product_id)
    if not product:
        raise ValueError(f"Product {product_id} not found")

    data  = get_orders()
    order = {
        "id":             f"ORD-{len(data['orders'])+1:04d}",
        "product_id":     product_id,
        "product_name":   product.get("name_ar",""),
        "price":          product["price"],
        "qty":            qty,
        "total":          round(product["price"] * qty, 2),
        "user_id":        user_id,
        "payment_method": payment_method,
        "status":         "pending_payment",
        "created_at":     datetime.now().isoformat(),
        "updated_at":     datetime.now().isoformat(),
    }
    data["orders"].append(order)
    data["total_revenue"] = round(data.get("total_revenue",0) + order["total"], 2)
    _write(DB["orders"], data)

    # Decrease stock
    update_product(product_id, {"stock": max(0, product.get("stock",0) - qty)})
    log.info(f"Order created: {order['id']} — ${order['total']}")
    return order

def update_order_status(oid: str, status: str) -> bool:
    data = get_orders()
    for o in data["orders"]:
        if o["id"] == oid:
            o["status"]     = status
            o["updated_at"] = datetime.now().isoformat()
            _write(DB["orders"], data)
            return True
    return False

def get_orders_by_user(user_id: int) -> list:
    return [o for o in get_orders()["orders"] if o.get("user_id") == user_id]

def get_recent_orders(n=10) -> list:
    orders = get_orders()["orders"]
    return sorted(orders, key=lambda x: x.get("created_at",""), reverse=True)[:n]

# ══════════════════════════════════════════════════════════════════
# LEADS / USERS
# ══════════════════════════════════════════════════════════════════

def get_leads() -> dict:
    return _read(DB["leads"], lambda: {"total_users":0, "users":[]})

def get_user(user_id: int) -> Optional[dict]:
    return next((u for u in get_leads()["users"] if int(u.get("id",0)) == user_id), None)

def upsert_user(tg_user, extra: dict = None) -> dict:
    data = get_leads()
    for u in data["users"]:
        if int(u.get("id",0)) == tg_user.id:
            u["last_seen"]  = datetime.now().isoformat()
            u["messages"]   = u.get("messages",0) + 1
            if extra: u.update(extra)
            _write(DB["leads"], data)
            return u
    new_user = {
        "id":         tg_user.id,
        "username":   tg_user.username or "",
        "name":       tg_user.full_name or "",
        "joined":     datetime.now().isoformat(),
        "last_seen":  datetime.now().isoformat(),
        "messages":   1,
        "orders":     0,
        "total_spent":0,
        "lang":       "ar",
        "preferences":[],
        "cart":       [],
    }
    if extra: new_user.update(extra)
    data["users"].append(new_user)
    data["total_users"] = len(data["users"])
    _write(DB["leads"], data)
    log.info(f"New user: {tg_user.id} — {tg_user.full_name}")
    return new_user

def update_user(user_id: int, updates: dict) -> bool:
    data = get_leads()
    for u in data["users"]:
        if int(u.get("id",0)) == user_id:
            u.update(updates)
            _write(DB["leads"], data)
            return True
    return False

def get_all_users() -> list:
    return get_leads()["users"]

def get_total_users() -> int:
    return len(get_leads()["users"])

# ══════════════════════════════════════════════════════════════════
# USER CART (persistent per user)
# ══════════════════════════════════════════════════════════════════

def get_user_cart(user_id: int) -> list:
    carts = _read(DB["cart"], dict)
    return carts.get(str(user_id), [])

def save_user_cart(user_id: int, cart: list):
    carts = _read(DB["cart"], dict)
    carts[str(user_id)] = cart
    _write(DB["cart"], carts)

def add_to_cart(user_id: int, product_id: str, qty: int = 1) -> list:
    cart = get_user_cart(user_id)
    item = next((i for i in cart if i["product_id"] == product_id), None)
    if item:
        item["qty"] = item.get("qty",1) + qty
    else:
        p = get_product(product_id)
        if p:
            cart.append({
                "product_id": product_id,
                "name_ar":    p.get("name_ar",""),
                "price":      p["price"],
                "qty":        qty,
                "image":      p.get("image",""),
            })
    save_user_cart(user_id, cart)
    return cart

def clear_cart(user_id: int):
    save_user_cart(user_id, [])

def get_cart_total(user_id: int) -> float:
    cart = get_user_cart(user_id)
    return round(sum(i["price"] * i.get("qty",1) for i in cart), 2)

# ══════════════════════════════════════════════════════════════════
# ANALYTICS
# ══════════════════════════════════════════════════════════════════

def track_event(event: str, data: dict = None):
    """تسجيل حدث تحليلي."""
    analytics = _read(DB["analytics"], lambda: {"events":[], "page_views":0, "product_views":{}})
    analytics["events"].append({
        "event": event,
        "data":  data or {},
        "time":  datetime.now().isoformat(),
    })
    # Keep last 1000 events only
    if len(analytics["events"]) > 1000:
        analytics["events"] = analytics["events"][-1000:]
    _write(DB["analytics"], analytics)

def track_product_view(product_id: str, user_id: int = None):
    analytics = _read(DB["analytics"], lambda: {"events":[], "page_views":0, "product_views":{}})
    pv = analytics.setdefault("product_views", {})
    pv[product_id] = pv.get(product_id, 0) + 1
    analytics["page_views"] = analytics.get("page_views",0) + 1
    _write(DB["analytics"], analytics)

def get_analytics_summary() -> dict:
    a  = _read(DB["analytics"], lambda: {"events":[], "page_views":0, "product_views":{}})
    o  = get_orders()
    u  = get_leads()
    ps = get_products()
    return {
        "total_users":    len(u["users"]),
        "total_orders":   len(o["orders"]),
        "total_revenue":  o.get("total_revenue", 0),
        "total_products": len(ps),
        "page_views":     a.get("page_views", 0),
        "top_products":   sorted(
            a.get("product_views",{}).items(),
            key=lambda x: x[1], reverse=True
        )[:5],
        "pending_orders": len([x for x in o["orders"] if x.get("status")=="pending_payment"]),
        "low_stock_count":len(get_low_stock()),
    }

# ══════════════════════════════════════════════════════════════════
# FAQs
# ══════════════════════════════════════════════════════════════════

def get_faqs() -> list:
    return _read(DB["faqs"], list)

def add_faq(question: str, answer: str, category: str = "general"):
    faqs = get_faqs()
    faqs.append({
        "id":       len(faqs) + 1,
        "question": question,
        "answer":   answer,
        "category": category,
        "added_at": datetime.now().isoformat(),
    })
    _write(DB["faqs"], faqs)

# ══════════════════════════════════════════════════════════════════
# NEWSLETTER
# ══════════════════════════════════════════════════════════════════

def subscribe_email(email: str, user_id: int = None) -> bool:
    data = _read(DB["newsletter"], lambda: {"subscribers":[]})
    if any(s["email"] == email for s in data["subscribers"]):
        return False  # already subscribed
    data["subscribers"].append({
        "email":     email,
        "user_id":   user_id,
        "subscribed":datetime.now().isoformat(),
        "active":    True,
    })
    _write(DB["newsletter"], data)
    return True

def get_subscribers() -> list:
    return _read(DB["newsletter"], lambda: {"subscribers":[]})["subscribers"]

# ══════════════════════════════════════════════════════════════════
# REVIEWS
# ══════════════════════════════════════════════════════════════════

def add_review(product_id: str, user_id: int, rating: int, comment: str) -> dict:
    reviews = _read(DB["reviews"], list)
    review  = {
        "id":         len(reviews) + 1,
        "product_id": product_id,
        "user_id":    user_id,
        "rating":     max(1, min(5, rating)),
        "comment":    comment,
        "date":       datetime.now().isoformat(),
        "verified":   False,
    }
    reviews.append(review)
    _write(DB["reviews"], reviews)

    # Update product rating
    product_reviews = [r for r in reviews if r["product_id"] == product_id]
    avg_rating = sum(r["rating"] for r in product_reviews) / len(product_reviews)
    update_product(product_id, {
        "rating":  round(avg_rating, 1),
        "reviews": len(product_reviews),
    })
    return review

def get_product_reviews(product_id: str) -> list:
    return [r for r in _read(DB["reviews"], list) if r["product_id"] == product_id]

# ══════════════════════════════════════════════════════════════════
# BROADCAST LIST (for admin_bot mass messages)
# ══════════════════════════════════════════════════════════════════

def get_all_user_ids() -> list:
    return [u["id"] for u in get_all_users() if u.get("id")]

# ══════════════════════════════════════════════════════════════════
# INIT — create all DB files if missing
# ══════════════════════════════════════════════════════════════════

def init_db():
    defaults = {
        "orders":     {"orders": [], "total_revenue": 0},
        "leads":      {"total_users": 0, "users": []},
        "cart":       {},
        "analytics":  {"events": [], "page_views": 0, "product_views": {}},
        "reviews":    [],
        "newsletter": {"subscribers": []},
    }
    for key, default in defaults.items():
        if not DB[key].exists():
            _write(DB[key], default)
            log.info(f"Initialized {key}.json")

if __name__ == "__main__":
    init_db()
    print("✅ Database initialized")
    s = get_analytics_summary()
    print(f"📊 Products: {s['total_products']} | Users: {s['total_users']} | Orders: {s['total_orders']}")
