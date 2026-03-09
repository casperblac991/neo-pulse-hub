#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════╗
║   BOT 3: بوت التوصيات الذكية v2.0 (Webhook Only)              ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import logging
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.constants import ParseMode, ChatAction

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# التوكن من المتغيرات البيئية
TOKEN = os.environ.get("RECOMMEND_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN", "")
if not TOKEN:
    print("❌ RECOMMEND_BOT_TOKEN or TELEGRAM_TOKEN is missing!")
    sys.exit(1)

ADMIN_ID = int(os.environ.get("ADMIN_USER_ID", "0"))
SITE_URL = os.environ.get("SITE_URL", "https://neo-pulse-hub.it.com")
PAYPAL = os.environ.get("PAYPAL_EMAIL", "Saidchaik@gmail.com")

logging.basicConfig(format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO, handlers=[logging.StreamHandler(),
    logging.FileHandler("recommendation_bot.log", encoding="utf-8")])
log = logging.getLogger("recommendation_bot")

_awaiting: dict = {}
_sessions: dict = {}

# ══════════════════════════════════════════════════════════════════
# MAIN (Webhook Mode)
# ══════════════════════════════════════════════════════════════════

def main():
    """تشغيل البوت باستخدام webhook (بدون polling)"""
    print("🎯 Recommendation Bot is ready for webhook mode.")
    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()
