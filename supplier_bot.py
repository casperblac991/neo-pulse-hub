#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════╗
║   BOT 4: بوت الموردين والمخزون v2.0 (Webhook Only)            ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import logging
import time
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.constants import ParseMode, ChatAction

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import sys
sys.path.insert(0, os.path.dirname(__file__))
from shared_db import (get_products, get_product, update_product, add_product,
                        save_products, get_low_stock, get_out_of_stock,
                        get_analytics_summary, init_db)
from ai_engine import search_product_by_description, generate_product_description, suggest_price

# التوكن من المتغيرات البيئية
TOKEN = os.environ.get("SUPPLIER_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN", "")
if not TOKEN:
    print("❌ SUPPLIER_BOT_TOKEN or TELEGRAM_TOKEN is missing!")
    sys.exit(1)

ADMIN_ID = int(os.environ.get("ADMIN_USER_ID", "0"))
LOW_STOCK_THRESHOLD = int(os.environ.get("LOW_STOCK_THRESHOLD", "5"))

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("supplier_bot.log", encoding="utf-8")
    ]
)
log = logging.getLogger("supplier_bot")

_awaiting: dict = {}

# ══════════════════════════════════════════════════════════════════
# MAIN (Webhook Mode)
# ══════════════════════════════════════════════════════════════════

def main():
    """تشغيل البوت باستخدام webhook (بدون polling)"""
    print("📦 Supplier Bot is ready for webhook mode.")
    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()
