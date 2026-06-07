#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO PULSE HUB — AI Customer Service Agent v3.1
 بوت خدمة العملاء الذكي
 يعمل 24/7 بدون تدخل بشري
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ─────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv("CUSTOMER_BOT_TOKEN", "")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", os.getenv("GOOGLE_API_KEY", ""))
    SITE_URL = os.getenv("SITE_URL", "https://neo-pulse-hub.it.com")
    ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "0"))
    PRODUCTS_FILE = "products.json"
    LEADS_FILE = "leads.json"

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
log = logging.getLogger("ai_customer_service")

# ─────────────────────────────────────────────────────────────
# Chat History
# ─────────────────────────────────────────────────────────────

class ChatHistory:
    """إدارة سجل المحادثات"""
    
    def __init__(self, max_history: int = 10):
        self._histories: Dict[int, List[Dict]] = {}
        self.max_history = max_history
    
    def get(self, user_id: int) -> List[Dict]:
        return self._histories.get(user_id, [])
    
    def add(self, user_id: int, role: str, text: str):
        history = self._histories.setdefault(user_id, [])
        history.append({"role": role, "text": text[:500]})
        if len(history) > self.max_history:
            history.pop(0)
    
    def clear(self, user_id: int):
        if user_id in self._histories:
            del self._histories[user_id]

chat_history = ChatHistory()

# ─────────────────────────────────────────────────────────────
# AI Response Engine
# ─────────────────────────────────────────────────────────────

class AIResponseEngine:
    """محرك الاستجابة بالذكاء الاصطناعي"""
    
    def __init__(self):
        self.config = Config()
        self.products = self._load_products()
    
    def _load_products(self) -> List[Dict]:
        try:
            with open(self.config.PRODUCTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def ask_ai(self, prompt: str) -> str:
        """استدعاء AI (Groq أو Gemini)"""
        # Try Groq first
        groq_key = self.config.GROQ_API_KEY
        if groq_key and "YOUR_" not in groq_key:
            try:
                from groq import Groq
                client = Groq(api_key=groq_key)
                resp = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=1500
                )
                return resp.choices[0].message.content
            except Exception as e:
                log.warning(f"Groq error: {e}")
        
        # Fallback to Gemini
        gemini_key = self.config.GEMINI_API_KEY
        if not gemini_key:
            return "عذراً، خدمة الذكاء الاصطناعي غير متاحة حالياً."
        
        try:
            import requests
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
            body = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1500}
            }
            resp = requests.post(url, json=body, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            log.error(f"Gemini error: {e}")
        
        return "عذراً، حدث خطأ. حاول مرة أخرى."
    
    def find_products(self, query: str, limit: int = 3) -> List[Dict]:
        """البحث عن منتجات"""
        query_lower = query.lower()
        results = []
        
        for p in self.products:
            name_ar = p.get('name', {}).get('ar', '').lower()
            name_en = p.get('name', {}).get('en', '').lower()
            category = p.get('category', '').lower()
            
            if (query_lower in name_ar or query_lower in name_en or 
                query_lower in category):
                results.append(p)
                if len(results) >= limit:
                    break
        
        return results
    
    def build_context(self, user_id: int) -> str:
        """بناء سياق المحادثة"""
        history = chat_history.get(user_id)
        if history:
            context = "\n".join([f"{h['role']}: {h['text']}" for h in history[-3:]])
            return f"\nآخر المحادثة:\n{context}\n"
        return ""
    
    def generate_response(self, user_id: int, message: str) -> str:
        """توليد استجابة ذكية"""
        context = self.build_context(user_id)
        products = self.find_products(message)
        
        # Product context
        product_context = ""
        if products:
            product_context = "\nمنتجات متوفرة:\n"
            for p in products:
                name = p.get('name', {}).get('ar', 'N/A')
                price = p.get('price', 0)
                link = p.get('affiliate_amazon', '')
                product_context += f"- {name} (${price}): {link}\n"
        
        prompt = f"""أنت مساعد متجر NEO PULSE HUB للذكاء الاصطناعي.
المتجر يبيع منتجات تقنية ذكية وأجهزة إلكترونية.

{context}

رسالة العميل: {message}
{product_context}

أجب بالعربية بشكل ودود ومهني.
إذا سأل عن منتج، اقترح المنتجات المتاحة.
إذا سأل عن السعر، اذكر السعر من المنتجات.
أضف روابط المنتجات عند الحاجة.
الموقع: {self.config.SITE_URL}"""
        
        response = self.ask_ai(prompt)
        
        # Save to history
        chat_history.add(user_id, "user", message)
        chat_history.add(user_id, "assistant", response)
        
        return response

# ─────────────────────────────────────────────────────────────
# Customer Service Bot
# ─────────────────────────────────────────────────────────────

class CustomerServiceBot:
    """بوت خدمة العملاء"""
    
    def __init__(self):
        self.config = Config()
        self.ai = AIResponseEngine()
        self._register_handlers()
        log.info("🤖 Customer Service Bot initialized")
    
    def _register_handlers(self):
        """تسجيل الأوامر والردود"""
        # This will be implemented with telegram.ext in actual usage
        pass
    
    def process_message(self, user_id: int, message: str) -> str:
        """معالجة رسالة العميل"""
        message_lower = message.lower().strip()
        
        # Handle commands
        if message_lower in ['/start', 'مرحبا', 'hello', 'hi', 'اهلا']:
            return self._welcome_message()
        
        if message_lower in ['/products', 'المنتجات', 'عرض المنتجات']:
            return self._show_products()
        
        if message_lower in ['/help', 'مساعدة', 'help']:
            return self._help_message()
        
        if 'سعر' in message_lower or 'price' in message_lower:
            return self._handle_price_query(message)
        
        if 'شحن' in message_lower or 'shipping' in message_lower:
            return self._shipping_info()
        
        if 'استرجاع' in message_lower or 'return' in message_lower:
            return self._return_policy()
        
        if 'تتبع' in message_lower or 'track' in message_lower:
            return self._track_order()
        
        # Default: AI response
        return self.ai.generate_response(user_id, message)
    
    def _welcome_message(self) -> str:
        return """👋 مرحباً بك في NEO PULSE HUB!

🛒 متجر المنتجات التقنية الذكية

كيف يمكنني مساعدتك اليوم؟

📋 الأوامر المتاحة:
• /products - عرض المنتجات
• /help - المساعدة
• اكتب سؤالك وسأجيب!

🔗 الموقع: {SITE_URL}""".format(SITE_URL=self.config.SITE_URL)
    
    def _show_products(self) -> str:
        products = self.ai.products[:5]
        if not products:
            return "عذراً، لا توجد منتجات متوفرة حالياً."
        
        msg = "🛍️ *منتجاتنا المميزة:*\n\n"
        for p in products:
            name = p.get('name', {}).get('ar', 'N/A')
            price = p.get('price', 0)
            link = p.get('affiliate_amazon', '')
            msg += f"📦 {name}\n💰 السعر: ${price}\n🔗 {link}\n\n"
        
        return msg
    
    def _help_message(self) -> str:
        return """📖 *كيف يمكنني مساعدتك؟*

• 💬 اسأل عن أي منتج وسأقترح عليك الأفضل
• 💰 اسأل عن الأسعار والعروض
• 📦 اسأل عن طرق الشحن والتوصيل
• 🔙 اسأل عن سياسة الاسترجاع
• 📍 اسأل عن موقعنا

اكتب سؤالك وسأجيب فوراً! 🤖"""
    
    def _handle_price_query(self, message: str) -> str:
        products = self.ai.find_products(message)
        if products:
            msg = "💰 *الأسعار:*\n\n"
            for p in products[:3]:
                name = p.get('name', {}).get('ar', 'N/A')
                price = p.get('price', 0)
                msg += f"📦 {name}: ${price}\n"
            return msg
        return "لم أجد منتجات مطابقة. اكتب اسم المنتج وسأبحث لك."
    
    def _shipping_info(self) -> str:
        return """📦 *معلومات الشحن:*

🕐 وقت التوصيل: 3-7 أيام عمل
🚚 الشحن: مجاني للطلبات فوق $50
💰 الدفع عند الاستلام متاح

🔗 للمزيد: {SITE_URL}/shipping""".format(SITE_URL=self.config.SITE_URL)
    
    def _return_policy(self) -> str:
        return """🔄 *سياسة الاسترجاع:*

✅ استرجاع خلال 14 يوم
✅ المنتج في حالته الأصلية
✅ استرداد كامل المبلغ

📞 تواصل معنا لأي استفسار

🔗 للمزيد: {SITE_URL}/returns""".format(SITE_URL=self.config.SITE_URL)
    
    def _track_order(self) -> str:
        return """📍 *تتبع الطلب:*

للأسف، نظام التتبع غير متصل حالياً.

🛒 لمتابعة طلبك:
1. راجع بريدك الإلكتروني
2. تواصل معنا مع رقم الطلب

📞 الدعم: @noepulsehub_bot"""


# ─────────────────────────────────────────────────────────────
# Lead Management
# ─────────────────────────────────────────────────────────────

class LeadManager:
    """إدارة العملاء المحتملين"""
    
    def __init__(self):
        self.leads_file = Config.LEADS_FILE
    
    def load(self) -> Dict:
        try:
            with open(self.leads_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"total_users": 0, "users": [], "support_chats": 0}
    
    def save(self, data: Dict) -> bool:
        try:
            with open(self.leads_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False
    
    def track_user(self, user_id: int, username: str = "", full_name: str = ""):
        """تتبع مستخدم جديد"""
        data = self.load()
        
        # Check if exists
        for u in data["users"]:
            if int(u.get("id", 0)) == user_id:
                u["last_seen"] = datetime.now().isoformat()
                u["chats"] = u.get("chats", 0) + 1
                self.save(data)
                return
        
        # New user
        data["users"].append({
            "id": user_id,
            "username": username,
            "name": full_name,
            "joined": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
            "chats": 1
        })
        data["total_users"] = len(data["users"])
        self.save(data)
    
    def get_stats(self) -> Dict:
        """إحصائيات العملاء"""
        data = self.load()
        return {
            "total_users": data.get("total_users", 0),
            "support_chats": data.get("support_chats", 0),
            "active_today": len([
                u for u in data.get("users", [])
                if datetime.now().isoformat()[:10] in u.get("last_seen", "")
            ])
        }


# ─────────────────────────────────────────────────────────────
# Main (Test)
# ─────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("🤖 NEO PULSE HUB — AI Customer Service")
    print("=" * 60)
    
    bot = CustomerServiceBot()
    lead_manager = LeadManager()
    
    # Test messages
    test_messages = [
        "مرحبا",
        "أريد ساعة ذكية",
        "ما هو السعر؟",
        "كيف أشحن؟"
    ]
    
    print("\n🧪 Testing Bot Responses:")
    print("-" * 40)
    
    for msg in test_messages:
        print(f"\n👤 User: {msg}")
        response = bot.process_message(user_id=123, message=msg)
        print(f"🤖 Bot: {response[:100]}...")
    
    print("\n" + "-" * 40)
    stats = lead_manager.get_stats()
    print(f"\n📊 Lead Stats: {stats}")
    
    print("\n" + "=" * 60)
    print("✅ Customer Service AI Ready!")
    print("=" * 60)

if __name__ == "__main__":
    main()
