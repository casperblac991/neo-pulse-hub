#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO PULSE HUB — Admin Bot v2.0
✅ ADMIN_BOT_TOKEN (صح)
✅ _register_handlers (للـ webhook)
✅ إحصائيات + إدارة المنتجات + broadcast
"""
import os, json, logging
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
GEMINI_API_KEY  = (os.environ.get("GEMINI_API_KEY") or
                   os.environ.get("GOOGLE_API_KEY") or "")
ADMIN_USER_ID   = int(os.environ.get("ADMIN_USER_ID", "0"))
BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
PRODUCTS_FILE   = os.path.join(BASE_DIR, "products.json")
ORDERS_FILE     = os.path.join(BASE_DIR, "orders.json")
LEADS_FILE      = os.path.join(BASE_DIR, "leads.json")

log = logging.getLogger("admin_bot")

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

def is_admin(uid):
    return ADMIN_USER_ID and int(uid) == ADMIN_USER_ID

def ask_gemini(prompt: str) -> str:
    key = (os.environ.get("GEMINI_API_KEY") or
           os.environ.get("GOOGLE_API_KEY") or "")
    if not key:
        log.error("GEMINI_API_KEY missing!")
        return ""
    import requests as _r
    url = ("https://generativelanguage.googleapis.com/v1beta/models/"
           "gemini-2.5-flash:generateContent?key=" + key)
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 2000,
            "thinkingConfig": {"thinkingBudget": 0}
        }
    }
    try:
        resp = _r.post(url, json=body, timeout=30)
        if resp.status_code != 200:
            log.error(f"Gemini HTTP {resp.status_code}: {resp.text[:150]}")
            return ""
        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            log.error(f"Gemini no candidates: {str(data)[:150]}")
            return ""
        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            log.error(f"Gemini empty parts. finishReason: {candidates[0].get('finishReason')}")
            return ""
        return parts[0].get("text", "")
    except Exception as e:
        log.error(f"Gemini exception: {e}")
        return ""

def _register_handlers(app):
    app.add_handler(CommandHandler("start",      cmd_start))
    app.add_handler(CommandHandler("stats",      cmd_stats))
    app.add_handler(CommandHandler("orders",     cmd_orders))
    app.add_handler(CommandHandler("products",   cmd_products))
    app.add_handler(CommandHandler("broadcast",  cmd_broadcast))
    app.add_handler(CommandHandler("ai",         cmd_ai))
    app.add_error_handler(error_handler)

if __name__ == "__main__":
    if not ADMIN_BOT_TOKEN:
        print("❌ ADMIN_BOT_TOKEN missing!"); exit(1)
    app = Application.builder().token(ADMIN_BOT_TOKEN).build()
    _register_handlers(app)
    print("🛡️ Admin Bot running...")
    app.run_polling(drop_pending_updates=True)
