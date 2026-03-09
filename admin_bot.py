#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════╗
║   BOT 2: بوت الإدارة الكامل v2.0 (Webhook Only)               ║
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

# التوكن من المتغيرات البيئية
TOKEN = os.environ.get("ADMIN_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN", "")
if not TOKEN:
    print("❌ ADMIN_BOT_TOKEN or TELEGRAM_TOKEN is missing!")
    sys.exit(1)

ADMIN_ID = int(os.environ.get("ADMIN_USER_ID", "0"))

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(), logging.FileHandler("admin_bot.log", encoding="utf-8")]
)
log = logging.getLogger("admin_bot")

_awaiting: dict = {}

# ══════════════════════════════════════════════════════════════════
# MAIN (Webhook Mode)
# ══════════════════════════════════════════════════════════════════

def main():
    """تشغيل البوت باستخدام webhook (بدون polling)"""
    print("👑 Admin Bot is ready for webhook mode.")
    # لا تقم بتشغيل polling، فقط ابقَ حياً
    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()
