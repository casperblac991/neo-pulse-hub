#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO PULSE HUB — AI Store Manager v1.0
الدماغ المركزي لإدارة المتجر بالكامل بالذكاء الاصطناعي
يدير جميع العمليات من جلب المنتجات حتى التقارير
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ─────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────

class Config:
    """إعدادات المتجر"""
    SITE_URL = os.getenv("SITE_URL", "https://neo-pulse-hub.it.com")
    PRODUCTS_FILE = "products.json"
    LEADS_FILE = "leads.json"
    ORDERS_FILE = "orders.json"
    ANALYTICS_FILE = "analytics.json"
    
    # AI Settings
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", os.getenv("GOOGLE_API_KEY", ""))
    
    # Affiliate
    AMAZON_TAG = os.getenv("AMAZON_AFFILIATE_TAG", "neopulsehub-20")

# ─────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
log = logging.getLogger("ai_store_manager")

# ─────────────────────────────────────────────────────────────
# Data Classes
# ─────────────────────────────────────────────────────────────

class OperationStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Product:
    id: str
    name: Dict[str, str]
    price: float
    category: str
    image: str
    affiliate_link: str
    asin: str = ""
    stock: int = 100
    views: int = 0
    sales: int = 0

@dataclass
class Order:
    id: str
    customer_id: str
    products: List[Dict]
    total: float
    status: str
    created_at: str
    updated_at: str

@dataclass
class Lead:
    id: int
    username: str
    name: str
    joined: str
    last_seen: str
    chats: int
    orders: int = 0

@dataclass
class Operation:
    id: str
    type: str  # product_sourcing, pricing, marketing, etc.
    status: OperationStatus
    result: Any = None
    error: str = ""
    created_at: str = ""
    completed_at: str = ""

# ─────────────────────────────────────────────────────────────
# AI Store Manager
# ─────────────────────────────────────────────────────────────

class AIStoreManager:
    """
    الدماغ المركزي للمتجر الذكي
    يدير جميع العمليات بالذكاء الاصطناعي
    """
    
    def __init__(self):
        self.config = Config()
        self.operations_history: List[Operation] = []
        log.info("🧠 AI Store Manager initialized")
    
    # ─────────────────────────────────────────────────────────
    # AI Integration
    # ─────────────────────────────────────────────────────────
    
    def ask_ai(self, prompt: str, max_tokens: int = 2000) -> str:
        """استدعاء الذكاء الاصطناعي (Groq أو Gemini)"""
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
                    max_tokens=max_tokens
                )
                return resp.choices[0].message.content
            except Exception as e:
                log.warning(f"Groq error: {e}")
        
        # Fallback to Gemini
        gemini_key = self.config.GEMINI_API_KEY
        if not gemini_key:
            log.error("No AI API key available!")
            return ""
        
        try:
            import requests
            url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
                   f"gemini-2.5-flash:generateContent?key={gemini_key}")
            body = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.7, "maxOutputTokens": max_tokens}
            }
            resp = requests.post(url, json=body, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            log.error(f"Gemini error: {e}")
        return ""
    
    # ─────────────────────────────────────────────────────────
    # Product Management
    # ─────────────────────────────────────────────────────────
    
    def load_products(self) -> List[Dict]:
        """تحميل المنتجات من قاعدة البيانات"""
        try:
            with open(self.config.PRODUCTS_FILE, 'r', encoding='utf-8') as f:
                products = json.load(f)
                # Fix string prices
                for p in products:
                    if isinstance(p.get('price'), str):
                        try:
                            p['price'] = float(p['price'].replace('$', '').replace(',', ''))
                        except:
                            p['price'] = 0
                return products
        except Exception as e:
            log.error(f"Error loading products: {e}")
            return []
    
    def save_products(self, products: List[Dict]) -> bool:
        """حفظ المنتجات"""
        try:
            with open(self.config.PRODUCTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            log.error(f"Error saving products: {e}")
            return False
    
    def get_product_recommendations(self, user_id: int, limit: int = 5) -> List[Dict]:
        """توصيات منتجات مخصصة للعميل"""
        products = self.load_products()
        
        # Simple recommendation: top rated, in stock
        recommendations = [
            p for p in products 
            if p.get('stock', 0) > 0
        ]
        
        # Sort by views and sales
        recommendations.sort(
            key=lambda x: (x.get('views', 0) + x.get('sales', 0) * 10), 
            reverse=True
        )
        
        return recommendations[:limit]
    
    def analyze_product_performance(self, product_id: str) -> Dict:
        """تحليل أداء منتج معين"""
        products = self.load_products()
        product = next((p for p in products if p.get('id') == product_id), None)
        
        if not product:
            return {"error": "Product not found"}
        
        views = product.get('views', 0)
        sales = product.get('sales', 0)
        conversion_rate = (sales / views * 100) if views > 0 else 0
        
        return {
            "product_id": product_id,
            "name": product.get('name', {}).get('ar', 'N/A'),
            "views": views,
            "sales": sales,
            "conversion_rate": round(conversion_rate, 2),
            "revenue": round(product.get('price', 0) * sales, 2),
            "status": "good" if conversion_rate > 2 else "needs_improvement"
        }
    
    # ─────────────────────────────────────────────────────────
    # Customer Management
    # ─────────────────────────────────────────────────────────
    
    def load_leads(self) -> Dict:
        """تحميل بيانات العملاء"""
        try:
            with open(self.config.LEADS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            log.error(f"Error loading leads: {e}")
            return {"total_users": 0, "users": []}
    
    def save_leads(self, data: Dict) -> bool:
        """حفظ بيانات العملاء"""
        try:
            with open(self.config.LEADS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            log.error(f"Error saving leads: {e}")
            return False
    
    def get_customer_insights(self, user_id: int) -> Dict:
        """تحليل سلوك العميل"""
        leads = self.load_leads()
        user = next((u for u in leads.get('users', []) if u.get('id') == user_id), None)
        
        if not user:
            return {"error": "Customer not found"}
        
        return {
            "user_id": user_id,
            "name": user.get('name', 'N/A'),
            "total_chats": user.get('chats', 0),
            "total_orders": user.get('orders', 0),
            "engagement_score": min(100, user.get('chats', 0) * 10),
            "customer_type": "VIP" if user.get('orders', 0) > 5 else "Regular"
        }
    
    # ─────────────────────────────────────────────────────────
    # Marketing
    # ─────────────────────────────────────────────────────────
    
    def generate_marketing_campaign(self, product_id: str = None) -> Dict:
        """إنشاء حملة تسويقية"""
        products = self.load_products()
        
        if product_id:
            target_products = [p for p in products if p.get('id') == product_id]
        else:
            # Top products
            target_products = sorted(
                products, 
                key=lambda x: x.get('sales', 0), 
                reverse=True
            )[:3]
        
        campaign = {
            "id": f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "created_at": datetime.now().isoformat(),
            "products": [],
            "content": {}
        }
        
        for product in target_products:
            name = product.get('name', {}).get('ar', 'Product')
            price = product.get('price', 0)
            
            # AI generated content
            prompt = f"""اكتب منشور تيليجرام جذاب للمنتج: {name}
السعر: ${price}
يجب أن يكون قصير ومغري مع ايموجي.
أضف رابط_affiliate."""
            
            content = self.ask_ai(prompt, max_tokens=300)
            
            campaign["products"].append({
                "id": product.get('id'),
                "name": name,
                "link": product.get('affiliate_amazon', '')
            })
            campaign["content"][product.get('id')] = content
        
        return campaign
    
    def analyze_marketing_performance(self) -> Dict:
        """تحليل أداء التسويق"""
        products = self.load_products()
        
        total_views = sum(p.get('views', 0) for p in products)
        total_sales = sum(p.get('sales', 0) for p in products)
        total_revenue = sum(p.get('price', 0) * p.get('sales', 0) for p in products)
        
        return {
            "total_products": len(products),
            "total_views": total_views,
            "total_sales": total_sales,
            "total_revenue": round(total_revenue, 2),
            "conversion_rate": round((total_sales / total_views * 100) if total_views > 0 else 0, 2),
            "top_product": max(products, key=lambda x: x.get('sales', 0)).get('name', {}).get('ar', 'N/A') if products else "N/A"
        }
    
    # ─────────────────────────────────────────────────────────
    # Inventory Management
    # ─────────────────────────────────────────────────────────
    
    def check_low_stock(self, threshold: int = 10) -> List[Dict]:
        """فحص المنتجات منخفضة المخزون"""
        products = self.load_products()
        low_stock = [p for p in products if p.get('stock', 100) < threshold]
        
        return [
            {
                "id": p.get('id'),
                "name": p.get('name', {}).get('ar', 'N/A'),
                "stock": p.get('stock', 0),
                "sales": p.get('sales', 0)
            }
            for p in low_stock
        ]
    
    def restock_recommendation(self, product_id: str, target_stock: int = 100) -> Dict:
        """توصية بإعادة التخزين"""
        products = self.load_products()
        product = next((p for p in products if p.get('id') == product_id), None)
        
        if not product:
            return {"error": "Product not found"}
        
        current_stock = product.get('stock', 0)
        needed = target_stock - current_stock if current_stock < target_stock else 0
        
        return {
            "product_id": product_id,
            "product_name": product.get('name', {}).get('ar', 'N/A'),
            "current_stock": current_stock,
            "recommended_stock": target_stock,
            "quantity_to_order": needed,
            "estimated_cost": round(needed * (product.get('price', 0) * 0.6), 2),  # 60% of selling price
            "priority": "high" if current_stock < 5 else "medium" if current_stock < 10 else "low"
        }
    
    # ─────────────────────────────────────────────────────────
    # Pricing Intelligence
    # ─────────────────────────────────────────────────────────
    
    def analyze_pricing(self, product_id: str) -> Dict:
        """تحليل تسعير منتج"""
        products = self.load_products()
        product = next((p for p in products if p.get('id') == product_id), None)
        
        if not product:
            return {"error": "Product not found"}
        
        price = product.get('price', 0)
        sales = product.get('sales', 0)
        
        # Simple pricing analysis
        return {
            "product_id": product_id,
            "current_price": price,
            "total_units_sold": sales,
            "total_revenue": round(price * sales, 2),
            "suggested_price": round(price * 0.95, 2),  # 5% discount suggestion
            "price_tier": "premium" if price > 200 else "mid" if price > 50 else "budget"
        }
    
    def generate_price_adjustment(self, product_id: str) -> Dict:
        """توليد توصية لتعديل السعر"""
        analysis = self.analyze_pricing(product_id)
        
        if "error" in analysis:
            return analysis
        
        conversion_rate = 0
        products = self.load_products()
        product = next((p for p in products if p.get('id') == product_id), None)
        
        if product:
            views = product.get('views', 0)
            sales = product.get('sales', 0)
            conversion_rate = (sales / views * 100) if views > 0 else 0
        
        adjustment = "no_change"
        new_price = analysis['current_price']
        
        if conversion_rate < 1:  # Low conversion
            adjustment = "reduce_price"
            new_price = round(analysis['current_price'] * 0.9, 2)  # 10% off
        elif conversion_rate > 5:  # High conversion
            adjustment = "increase_price"
            new_price = round(analysis['current_price'] * 1.1, 2)  # 10% increase
        
        return {
            **analysis,
            "recommended_action": adjustment,
            "new_price": new_price,
            "reason": {
                "reduce_price": "Low conversion rate - reducing price to boost sales",
                "increase_price": "High conversion rate - can increase price for more profit",
                "no_change": "Conversion rate is optimal"
            }.get(adjustment, "")
        }
    
    # ─────────────────────────────────────────────────────────
    # Analytics & Reporting
    # ─────────────────────────────────────────────────────────
    
    def generate_daily_report(self) -> Dict:
        """إنشاء تقرير يومي"""
        products = self.load_products()
        leads = self.load_leads()
        
        # Calculate metrics
        total_products = len(products)
        total_views = sum(p.get('views', 0) for p in products)
        total_sales = sum(p.get('sales', 0) for p in products)
        total_revenue = sum(p.get('price', 0) * p.get('sales', 0) for p in products)
        
        # Top products
        top_products = sorted(
            products, 
            key=lambda x: x.get('sales', 0), 
            reverse=True
        )[:5]
        
        # Low stock items
        low_stock = self.check_low_stock()
        
        # Customer stats
        total_customers = leads.get('total_users', 0)
        active_customers = len([
            u for u in leads.get('users', [])
            if datetime.now().isoformat()[:10] in u.get('last_seen', '')
        ])
        
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "generated_at": datetime.now().isoformat(),
            "store_metrics": {
                "total_products": total_products,
                "total_views": total_views,
                "total_sales": total_sales,
                "total_revenue": round(total_revenue, 2),
                "conversion_rate": round((total_sales / total_views * 100) if total_views > 0 else 0, 2)
            },
            "customer_metrics": {
                "total_customers": total_customers,
                "active_today": active_customers
            },
            "inventory": {
                "low_stock_count": len(low_stock),
                "low_stock_items": low_stock[:5]
            },
            "top_products": [
                {"id": p.get('id'), "name": p.get('name', {}).get('ar', 'N/A'), "sales": p.get('sales', 0)}
                for p in top_products
            ],
            "ai_recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """توليد توصيات الذكاء الاصطناعي"""
        recommendations = []
        
        # Analyze products
        products = self.load_products()
        
        # Low stock warning
        low_stock = self.check_low_stock()
        if len(low_stock) > 0:
            recommendations.append(f"⚠️ {len(low_stock)} منتجات منخفضة المخزون - يُنصح بإعادة التوريد")
        
        # Top performer
        if products:
            top = max(products, key=lambda x: x.get('sales', 0))
            recommendations.append(f"🏆 أفضل منتج: {top.get('name', {}).get('ar', 'N/A')} ({top.get('sales', 0)} مبيعات)")
        
        # Conversion analysis
        total_views = sum(p.get('views', 0) for p in products)
        total_sales = sum(p.get('sales', 0) for p in products)
        if total_views > 0:
            rate = (total_sales / total_views) * 100
            if rate < 1:
                recommendations.append("📈 معدل التحويل منخفض - يُنصح بتحسين الصور والأوصاف")
            elif rate > 3:
                recommendations.append("🎉 معدل التحويل ممتاز!")
        
        return recommendations
    
    # ─────────────────────────────────────────────────────────
    # Store Status
    # ─────────────────────────────────────────────────────────
    
    def get_store_status(self) -> Dict:
        """الحصول على حالة المتجر"""
        products = self.load_products()
        leads = self.load_leads()
        
        return {
            "status": "operational",
            "store_url": self.config.SITE_URL,
            "total_products": len(products),
            "total_customers": leads.get('total_users', 0),
            "ai_connected": bool(self.config.GROQ_API_KEY or self.config.GEMINI_API_KEY),
            "amazon_connected": bool(self.config.AMAZON_TAG),
            "uptime": "24/7",
            "last_update": datetime.now().isoformat()
        }

# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

def main():
    """تشغيل مدير المتجر الذكي"""
    print("=" * 60)
    print("🧠 NEO PULSE HUB — AI Store Manager")
    print("=" * 60)
    
    manager = AIStoreManager()
    
    # Show store status
    print("\n📊 حالة المتجر:")
    status = manager.get_store_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    # Generate daily report
    print("\n📝 التقرير اليومي:")
    report = manager.generate_daily_report()
    print(f"   التاريخ: {report['date']}")
    print(f"   إجمالي المبيعات: {report['store_metrics']['total_sales']}")
    print(f"   إجمالي الإيرادات: ${report['store_metrics']['total_revenue']}")
    print(f"   معدل التحويل: {report['store_metrics']['conversion_rate']}%")
    
    print("\n💡 توصيات AI:")
    for rec in report['ai_recommendations']:
        print(f"   {rec}")
    
    print("\n" + "=" * 60)
    print("✅ AI Store Manager running successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
