#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO PULSE HUB — AI Marketing Automation
 نظام التسويق الذكي
 ينشئ حملات تسويقية تلقائياً
"""

import os
import json
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ─────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────

class Config:
    SITE_URL = os.getenv("SITE_URL", "https://neo-pulse-hub.it.com")
    PRODUCTS_FILE = "products.json"
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    TELEGRAM_BOT_TOKEN = os.getenv("CUSTOMER_BOT_TOKEN", "")
    TELEGRAM_CHANNEL = os.getenv("TELEGRAM_CHANNEL_ID", "@noepulsehub_bot")

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
log = logging.getLogger("ai_marketing")

# ─────────────────────────────────────────────────────────────
# Content Templates
# ─────────────────────────────────────────────────────────────

ARABIC_CONTENT = {
    "greeting": ["🔥 عرض خاص!", "⚡ خصم كبير!", "🎉 لفترة محدودة!", "💎 عرض حصري!"],
    "cta": ["اطلب الآن!", "لا تفوت الفرصة!", "احجز طلبك!", "الكمية محدودة!"],
    "urgency": ["العرض ينتهي قريباً!", "فقط {} قطعة متبقية!", "خصم {}% فقط اليوم!"],
    "emoji": ["🛒", "📦", "⚡", "🔥", "💰", "🎁", "⭐", "🚀", "💎", "🎊"]
}

# ─────────────────────────────────────────────────────────────
# AI Marketing Engine
# ─────────────────────────────────────────────────────────────

class AIMarketingEngine:
    """محرك التسويق الذكي"""
    
    def __init__(self):
        self.config = Config()
        self.products = self._load_products()
    
    def _load_products(self) -> List[Dict]:
        try:
            with open(self.config.PRODUCTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def ask_ai(self, prompt: str, max_tokens: int = 500) -> str:
        """استدعاء AI"""
        groq_key = self.config.GROQ_API_KEY
        if groq_key and "YOUR_" not in groq_key:
            try:
                from groq import Groq
                client = Groq(api_key=groq_key)
                resp = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.8,
                    max_tokens=max_tokens
                )
                return resp.choices[0].message.content
            except Exception as e:
                log.warning(f"Groq error: {e}")
        
        return ""  # Return empty if no AI
    
    def generate_telegram_post(self, product: Dict) -> str:
        """إنشاء منشور تيليجرام"""
        name = product.get('name', {}).get('ar', 'منتج')
        price = product.get('price', 0)
        link = product.get('affiliate_amazon', '')
        
        # Template-based generation
        greeting = random.choice(ARABIC_CONTENT["greeting"])
        emoji = random.choice(ARABIC_CONTENT["emoji"])
        
        post = f"""{greeting} {emoji}

📦 *{name}*

💰 السعر: ${price}
🔗 {link}

{ARABIC_CONTENT["cta"][0]}

🏪 {self.config.SITE_URL}"""
        
        return post
    
    def generate_ai_post(self, product: Dict) -> str:
        """إنشاء منشور بالذكاء الاصطناعي"""
        name = product.get('name', {}).get('ar', 'منتج')
        price = product.get('price', 0)
        
        prompt = f"""اكتب منشور تيليجرام جذاب ومختصر للمنتج:
- الاسم: {name}
- السعر: ${price}

الشروط:
- باللغة العربية
- لا يتجاوز 200 حرف
- يحتوي على ايموجي
- يطلب من العميل الطلب
- يضاف رابط_affiliate_link
- أسلوب تسويقي مغري"""
        
        ai_content = self.ask_ai(prompt, max_tokens=300)
        if ai_content:
            product_link = product.get('affiliate_amazon', '')
            return f"{ai_content}\n\n🔗 {product_link}"
        
        # Fallback to template
        return self.generate_telegram_post(product)
    
    def create_campaign(self, product_ids: List[str] = None) -> Dict:
        """إنشاء حملة تسويقية"""
        if product_ids:
            products = [p for p in self.products if p.get('id') in product_ids]
        else:
            # Top products
            products = sorted(
                self.products, 
                key=lambda x: x.get('sales', 0), 
                reverse=True
            )[:5]
        
        campaign = {
            "id": f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "created_at": datetime.now().isoformat(),
            "products": len(products),
            "posts": []
        }
        
        for product in products:
            post = self.generate_ai_post(product)
            campaign["posts"].append({
                "product_id": product.get('id'),
                "content": post,
                "channel": self.config.TELEGRAM_CHANNEL
            })
        
        return campaign
    
    def generate_daily_content(self) -> List[Dict]:
        """توليد محتوى يومي"""
        # Select random products
        selected = random.sample(
            self.products[:20], 
            min(3, len(self.products))
        )
        
        content = []
        for product in selected:
            content.append({
                "type": "telegram",
                "product": product.get('name', {}).get('ar', 'N/A'),
                "post": self.generate_ai_post(product),
                "scheduled_for": (datetime.now() + timedelta(hours=random.randint(1, 6))).isoformat()
            })
        
        return content
    
    def analyze_campaign_performance(self) -> Dict:
        """تحليل أداء الحملات"""
        total_products = len(self.products)
        total_views = sum(p.get('views', 0) for p in self.products)
        total_sales = sum(p.get('sales', 0) for p in self.products)
        
        return {
            "total_posts": len(self.products),
            "estimated_reach": total_views,
            "conversion_rate": round((total_sales / total_views * 100) if total_views > 0 else 0, 2),
            "top_performer": max(self.products, key=lambda x: x.get('sales', 0)).get('name', {}).get('ar', 'N/A') if self.products else "N/A",
            "recommendations": self._get_marketing_recommendations()
        }
    
    def _get_marketing_recommendations(self) -> List[str]:
        """توصيات تسويقية"""
        recommendations = []
        
        # Analyze conversion
        total_views = sum(p.get('views', 0) for p in self.products)
        total_sales = sum(p.get('sales', 0) for p in self.products)
        
        if total_views > 0:
            rate = (total_sales / total_views) * 100
            if rate < 1:
                recommendations.append("📸 تحسين الصور قد يزيد المبيعات")
                recommendations.append("📝 أوصاف أفضل للمنتجات")
            elif rate > 3:
                recommendations.append("🎉 معدل التحويل ممتاز!")
        
        # Product diversity
        categories = set(p.get('category', '') for p in self.products)
        if len(categories) < 5:
            recommendations.append("📦 إضافة منتجات من فئات جديدة")
        
        return recommendations


# ─────────────────────────────────────────────────────────────
# Social Media Scheduler
# ─────────────────────────────────────────────────────────────

class SocialMediaScheduler:
    """جدولة السوشيال ميديا"""
    
    def __init__(self):
        self.engine = AIMarketingEngine()
        self.schedule_file = "schedule.json"
    
    def create_schedule(self, days: int = 7) -> Dict:
        """إنشاء جدول نشر"""
        schedule = {
            "created_at": datetime.now().isoformat(),
            "posts": []
        }
        
        for day in range(days):
            date = datetime.now() + timedelta(days=day)
            # 3 posts per day
            for hour in [9, 14, 19]:
                content = self.engine.generate_daily_content()
                if content:
                    schedule["posts"].append({
                        "date": date.strftime("%Y-%m-%d"),
                        "hour": hour,
                        "content": content[0] if content else None,
                        "status": "scheduled"
                    })
        
        self._save_schedule(schedule)
        return schedule
    
    def _save_schedule(self, schedule: Dict):
        try:
            with open(self.schedule_file, 'w', encoding='utf-8') as f:
                json.dump(schedule, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log.error(f"Error saving schedule: {e}")
    
    def get_schedule(self) -> Dict:
        try:
            with open(self.schedule_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"posts": []}


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("📢 NEO PULSE HUB — AI Marketing Automation")
    print("=" * 60)
    
    engine = AIMarketingEngine()
    scheduler = SocialMediaScheduler()
    
    # Create campaign
    print("\n🚀 Creating Marketing Campaign...")
    campaign = engine.create_campaign()
    print(f"   Campaign ID: {campaign['id']}")
    print(f"   Products: {campaign['products']}")
    
    # Show sample posts
    print("\n📝 Sample Posts:")
    for i, post in enumerate(campaign["posts"][:2], 1):
        print(f"\n--- Post {i} ---")
        print(post["content"][:150] + "...")
    
    # Analyze performance
    print("\n📊 Marketing Performance:")
    analysis = engine.analyze_campaign_performance()
    print(f"   Total Posts: {analysis['total_posts']}")
    print(f"   Conversion Rate: {analysis['conversion_rate']}%")
    print(f"   Top Performer: {analysis['top_performer']}")
    
    print("\n💡 Recommendations:")
    for rec in analysis['recommendations']:
        print(f"   {rec}")
    
    print("\n" + "=" * 60)
    print("✅ AI Marketing Ready!")
    print("=" * 60)

if __name__ == "__main__":
    main()
