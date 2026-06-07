#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO PULSE HUB — Full Store Integration Hub
يتكامل مع جميع أنظمة الذكاء الاصطناعي
يشغل المتجر بالكامل بشكل متكامل
"""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# Setup
# ─────────────────────────────────────────────────────────────

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
log = logging.getLogger("store_hub")

# ─────────────────────────────────────────────────────────────
# Import AI Systems
# ─────────────────────────────────────────────────────────────

def import_ai_systems():
    """استيراد جميع أنظمة الذكاء الاصطناعي"""
    systems = {}
    
    try:
        from ai_store_manager import AIStoreManager
        systems['store_manager'] = AIStoreManager()
        log.info("✅ AI Store Manager loaded")
    except Exception as e:
        log.error(f"❌ AI Store Manager: {e}")
    
    try:
        from ai_customer_service import CustomerServiceBot, LeadManager
        systems['customer_service'] = CustomerServiceBot()
        systems['lead_manager'] = LeadManager()
        log.info("✅ AI Customer Service loaded")
    except Exception as e:
        log.error(f"❌ AI Customer Service: {e}")
    
    try:
        from ai_marketing import AIMarketingEngine, SocialMediaScheduler
        systems['marketing'] = AIMarketingEngine()
        systems['scheduler'] = SocialMediaScheduler()
        log.info("✅ AI Marketing loaded")
    except Exception as e:
        log.error(f"❌ AI Marketing: {e}")
    
    try:
        from ai_analytics import AIAnalyticsEngine
        systems['analytics'] = AIAnalyticsEngine()
        log.info("✅ AI Analytics loaded")
    except Exception as e:
        log.error(f"❌ AI Analytics: {e}")
    
    return systems

# ─────────────────────────────────────────────────────────────
# Store API
# ─────────────────────────────────────────────────────────────

class StoreAPI:
    """API المتجر للتكامل"""
    
    def __init__(self, systems):
        self.systems = systems
        self.products_file = "products.json"
        self.orders_file = "orders.json"
    
    def get_products(self, limit: int = 20, category: str = None):
        """جلب المنتجات"""
        try:
            with open(self.products_file, 'r', encoding='utf-8') as f:
                products = json.load(f)
            
            if category:
                products = [p for p in products if p.get('category') == category]
            
            return products[:limit]
        except:
            return []
    
    def search_products(self, query: str, limit: int = 10):
        """البحث في المنتجات"""
        products = self.get_products(limit=1000)
        query_lower = query.lower()
        
        results = []
        for p in products:
            name_ar = p.get('name', {}).get('ar', '').lower()
            name_en = p.get('name', {}).get('en', '').lower()
            cat = p.get('category', '').lower()
            
            if (query_lower in name_ar or query_lower in name_en or 
                query_lower in cat):
                results.append(p)
                if len(results) >= limit:
                    break
        
        return results
    
    def get_product_by_id(self, product_id: str):
        """جلب منتج واحد"""
        products = self.get_products(limit=1000)
        for p in products:
            if p.get('id') == product_id:
                return p
        return None
    
    def get_recommendations(self, user_id: int = None, limit: int = 5):
        """الحصول على توصيات"""
        try:
            sm = self.systems.get('store_manager')
            if sm:
                return sm.get_product_recommendations(user_id or 0, limit)
        except:
            pass
        
        # Fallback
        return self.get_products(limit=limit)
    
    def record_interaction(self, user_id: int, product_id: str, action: str):
        """تسجيل تفاعل المستخدم"""
        try:
            products = self.get_products(limit=1000)
            for p in products:
                if p.get('id') == product_id:
                    if action == 'view':
                        p['views'] = p.get('views', 0) + 1
                    elif action == 'buy':
                        p['sales'] = p.get('sales', 0) + 1
                    
                    with open(self.products_file, 'w', encoding='utf-8') as f:
                        json.dump(products, f, ensure_ascii=False, indent=2)
                    return True
        except Exception as e:
            log.error(f"Error recording interaction: {e}")
        return False
    
    def get_trending_products(self, limit: int = 5):
        """المنتجات الرائجة"""
        products = self.get_products(limit=100)
        
        # Sort by engagement
        trending = sorted(
            products,
            key=lambda x: x.get('views', 0) + x.get('sales', 0) * 5,
            reverse=True
        )
        
        return trending[:limit]
    
    def get_deals(self, limit: int = 10):
        """العروض الخاصة"""
        products = self.get_products(limit=100)
        
        # Products with high views but low sales (potential deals)
        deals = []
        for p in products:
            views = p.get('views', 0)
            sales = p.get('sales', 0)
            
            if views > 10 and sales < views * 0.05:
                deals.append({
                    **p,
                    'deal_score': views * 0.1
                })
        
        deals.sort(key=lambda x: x['deal_score'], reverse=True)
        return deals[:limit]
    
    def get_stats(self):
        """إحصائيات المتجر"""
        products = self.get_products(limit=1000)
        
        total_revenue = sum(p.get('price', 0) * p.get('sales', 0) for p in products)
        total_views = sum(p.get('views', 0) for p in products)
        total_sales = sum(p.get('sales', 0) for p in products)
        
        # Categories
        categories = {}
        for p in products:
            cat = p.get('category', 'other')
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            "total_products": len(products),
            "total_revenue": round(total_revenue, 2),
            "total_views": total_views,
            "total_sales": total_sales,
            "conversion_rate": round((total_sales / total_views * 100) if total_views > 0 else 0, 2),
            "categories": categories,
            "top_category": max(categories.items(), key=lambda x: x[1], default=(None, 0))[0]
        }

# ─────────────────────────────────────────────────────────────
# Telegram Integration
# ─────────────────────────────────────────────────────────────

class TelegramStoreBot:
    """بوت تيليجرام المتجر"""
    
    def __init__(self, systems, api):
        self.systems = systems
        self.api = api
        self.token = os.getenv("CUSTOMER_BOT_TOKEN", "")
        
        log.info(f"🤖 Telegram Bot initialized (token: {self.token[:15]}...)")
    
    async def start(self):
        """بدء البوت"""
        if not self.token:
            log.error("❌ No bot token!")
            return
        
        try:
            from telegram import Update
            from telegram.ext import (Application, CommandHandler, 
                                       MessageHandler, CallbackQueryHandler,
                                       filters, ContextTypes)
            
            app = Application.builder().token(self.token).build()
            
            # Register handlers
            app.add_handler(CommandHandler("start", self.cmd_start))
            app.add_handler(CommandHandler("products", self.cmd_products))
            app.add_handler(CommandHandler("search", self.cmd_search))
            app.add_handler(CommandHandler("deals", self.cmd_deals))
            app.add_handler(CommandHandler("stats", self.cmd_stats))
            app.add_handler(CommandHandler("help", self.cmd_help))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
            
            log.info("✅ Telegram Bot handlers registered")
            return app
            
        except Exception as e:
            log.error(f"❌ Telegram Bot error: {e}")
            return None
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر start"""
        user = update.effective_user
        
        # Track user
        lm = self.systems.get('lead_manager')
        if lm:
            lm.track_user(user.id, user.username or "", user.full_name or "")
        
        welcome = f"""👋 مرحباً {user.first_name}!

🛒 *NEO PULSE HUB* - متجر التقنية الذكي

🔍 الأوامر:
/products - عرض المنتجات
/search - البحث
/deals - العروض
/stats - الإحصائيات
/help - المساعدة

أو اكتب سؤالك وسأجيب! 🤖"""

        await update.message.reply_text(welcome, parse_mode="Markdown")
    
    async def cmd_products(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر products"""
        products = self.api.get_products(limit=5)
        
        msg = "🛍️ *منتجاتنا المميزة:*\n\n"
        for p in products:
            name = p.get('name', {}).get('ar', 'N/A')
            price = p.get('price', 0)
            link = p.get('affiliate_amazon', '')
            msg += f"📦 *{name}*\n💰 ${price}\n🔗 [اطلب الآن]({link})\n\n"
        
        await update.message.reply_text(msg, parse_mode="Markdown")
    
    async def cmd_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر search"""
        query = ' '.join(context.args) if context.args else ""
        
        if not query:
            await update.message.reply_text("🔍 اكتب: /search <اسم المنتج>")
            return
        
        results = self.api.search_products(query, limit=5)
        
        if not results:
            await update.message.reply_text(f"❌ لم أجد: {query}")
            return
        
        msg = f"🔍 *نتائج البحث عن:* {query}\n\n"
        for p in results:
            name = p.get('name', {}).get('ar', 'N/A')
            price = p.get('price', 0)
            link = p.get('affiliate_amazon', '')
            msg += f"📦 {name}\n💰 ${price}\n🔗 [اطلب]({link})\n\n"
        
        await update.message.reply_text(msg, parse_mode="Markdown")
    
    async def cmd_deals(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر deals"""
        deals = self.api.get_deals(limit=5)
        
        msg = "🔥 *عروض حصرية!*\n\n"
        for p in deals:
            name = p.get('name', {}).get('ar', 'N/A')
            price = p.get('price', 0)
            link = p.get('affiliate_amazon', '')
            msg += f"⚡ *{name}*\n💰 ${price}\n🔗 [اطلب]({link})\n\n"
        
        await update.message.reply_text(msg, parse_mode="Markdown")
    
    async def cmd_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر stats"""
        stats = self.api.get_stats()
        
        msg = f"""📊 *إحصائيات المتجر*

🏪 المنتجات: {stats['total_products']}
👁️ المشاهدات: {stats['total_views']}
🛒 المبيعات: {stats['total_sales']}
💰 الإيرادات: ${stats['total_revenue']}
📈 التحويل: {stats['conversion_rate']}%

🏆 الفئة الأفضل: {stats['top_category'] or 'N/A'}"""

        await update.message.reply_text(msg, parse_mode="Markdown")
    
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر help"""
        help_text = """📖 *دليل الاستخدام*

🔍 *الأوامر:*
• /start - بدء المحادثة
• /products - عرض المنتجات
• /search <اسم> - البحث
• /deals - العروض
• /stats - الإحصائيات
• /help - المساعدة

💬 *أو اكتب سؤالك مباشرة!*

أجيب على أسئلتك عن المنتجات والأسعار والشحن والعروض. 🛒"""

        await update.message.reply_text(help_text, parse_mode="Markdown")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة الرسائل"""
        user = update.effective_user
        text = update.message.text
        
        # Track user
        lm = self.systems.get('lead_manager')
        if lm:
            lm.track_user(user.id, user.username or "", user.full_name or "")
        
        # Use AI Customer Service
        cs = self.systems.get('customer_service')
        if cs:
            response = cs.process_message(user.id, text)
            await update.message.reply_text(response[:4000])  # Telegram limit
        else:
            await update.message.reply_text("عذراً، خدمة الذكاء الاصطناعي غير متاحة")


# ─────────────────────────────────────────────────────────────
# Store Website API
# ─────────────────────────────────────────────────────────────

class WebsiteAPI:
    """API للموقع"""
    
    def __init__(self, api):
        self.api = api
    
    def get_json_response(self):
        """إنشاء استجابة JSON للموقع"""
        return {
            "status": "ok",
            "products": self.api.get_products(limit=20),
            "trending": self.api.get_trending_products(5),
            "deals": self.api.get_deals(5),
            "stats": self.api.get_stats(),
            "timestamp": datetime.now().isoformat()
        }


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

async def main():
    """تشغيل نظام المتجر المتكامل"""
    print("=" * 70)
    print("🛒 NEO PULSE HUB — Full Store Integration")
    print("=" * 70)
    
    # Load AI systems
    print("\n📦 Loading AI Systems...")
    systems = import_ai_systems()
    
    if not systems:
        print("❌ No AI systems loaded!")
        return
    
    print(f"\n✅ Loaded: {', '.join(systems.keys())}")
    
    # Create API
    api = StoreAPI(systems)
    
    # Initialize Telegram Bot
    print("\n🤖 Initializing Telegram Bot...")
    telegram_bot = TelegramStoreBot(systems, api)
    app = await telegram_bot.start()
    
    if app:
        print("\n🌐 Starting Flask API Server...")
        try:
            from flask import Flask, jsonify, request
            from flask_cors import CORS
            
            flask_app = Flask(__name__)
            CORS(flask_app)
            
            @flask_app.route('/api/products')
            def get_products():
                return jsonify(api.get_products(limit=50))
            
            @flask_app.route('/api/products/<product_id>')
            def get_product(product_id):
                return jsonify(api.get_product_by_id(product_id) or {})
            
            @flask_app.route('/api/search')
            def search():
                q = request.args.get('q', '')
                return jsonify(api.search_products(q, limit=20))
            
            @flask_app.route('/api/recommendations')
            def recommendations():
                uid = request.args.get('user_id', 0, type=int)
                return jsonify(api.get_recommendations(uid, limit=10))
            
            @flask_app.route('/api/trending')
            def trending():
                return jsonify(api.get_trending_products(10))
            
            @flask_app.route('/api/deals')
            def deals():
                return jsonify(api.get_deals(10))
            
            @flask_app.route('/api/stats')
            def stats():
                return jsonify(api.get_stats())
            
            @flask_app.route('/api/ai/report')
            def ai_report():
                analytics = systems.get('analytics')
                if analytics:
                    return jsonify(analytics.create_daily_report())
                return jsonify({})
            
            @flask_app.route('/api/ai/insights')
            def ai_insights():
                analytics = systems.get('analytics')
                if analytics:
                    return jsonify({
                        "insights": analytics.generate_insights(),
                        "recommendations": analytics.generate_recommendations()
                    })
                return jsonify({})
            
            @flask_app.route('/api/interact', methods=['POST'])
            def interact():
                data = request.json
                api.record_interaction(
                    data.get('user_id', 0),
                    data.get('product_id', ''),
                    data.get('action', 'view')
                )
                return jsonify({"status": "ok"})
            
            @flask_app.route('/api/health')
            def health():
                return jsonify({
                    "status": "ok",
                    "systems": list(systems.keys()),
                    "timestamp": datetime.now().isoformat()
                })
            
            print("\n" + "=" * 70)
            print("✅ FULL STORE SYSTEM RUNNING!")
            print("=" * 70)
            print("\n🌐 API Endpoints:")
            print("   /api/products      - List products")
            print("   /api/search?q=     - Search products")
            print("   /api/recommendations - AI recommendations")
            print("   /api/trending      - Trending products")
            print("   /api/deals         - Special deals")
            print("   /api/stats         - Store statistics")
            print("   /api/ai/report     - AI daily report")
            print("   /api/health        - System health")
            print("\n🤖 Telegram Bot: Ready")
            print("\n🛒 Run: python3 store_hub.py")
            print("=" * 70)
            
            # Run Flask in background
            import threading
            def run_flask():
                flask_app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
            
            thread = threading.Thread(target=run_flask, daemon=True)
            thread.start()
            print("\n✅ Flask API running on http://localhost:8080")
            
            # Keep running
            while True:
                await asyncio.sleep(10)
                
        except ImportError:
            print("⚠️ Flask not installed. Running Telegram bot only...")
            if app:
                print("\n✅ Starting Telegram Bot...")
                await app.run_polling()
    else:
        print("\n⚠️ Telegram bot not configured")
        print("💡 Add CUSTOMER_BOT_TOKEN to .env file")


if __name__ == "__main__":
    asyncio.run(main())