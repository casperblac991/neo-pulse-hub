#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEO PULSE HUB — AI Analytics Dashboard
 لوحة تحكم التحليلات الذكية
 تقارير وتوصيات لتحسين الأداء
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ─────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────

class Config:
    PRODUCTS_FILE = "products.json"
    LEADS_FILE = "leads.json"
    ORDERS_FILE = "orders.json"
    ANALYTICS_FILE = "analytics_history.json"
    SITE_URL = os.getenv("SITE_URL", "https://neo-pulse-hub.it.com")

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
log = logging.getLogger("ai_analytics")

# ─────────────────────────────────────────────────────────────
# Analytics Data Classes
# ─────────────────────────────────────────────────────────────

@dataclass
class ProductMetrics:
    product_id: str
    name: str
    views: int
    conversions: int
    revenue: float
    conversion_rate: float
    performance_score: float  # 0-100

@dataclass  
class CustomerMetrics:
    customer_id: int
    total_purchases: int
    total_spent: float
    last_purchase: str
    lifetime_value: float
    engagement_score: int

@dataclass
class StoreMetrics:
    total_revenue: float
    total_orders: int
    avg_order_value: float
    conversion_rate: float
    returning_customers: int
    new_customers: int

# ─────────────────────────────────────────────────────────────
# AI Analytics Engine
# ─────────────────────────────────────────────────────────────

class AIAnalyticsEngine:
    """محرك التحليلات الذكي"""
    
    def __init__(self):
        self.config = Config()
        self.products = self._load_products()
        self.leads = self._load_leads()
    
    def _load_products(self) -> List[Dict]:
        try:
            with open(self.config.PRODUCTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def _load_leads(self) -> Dict:
        try:
            with open(self.config.LEADS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"total_users": 0, "users": []}
    
    def calculate_store_metrics(self) -> StoreMetrics:
        """حساب مقاييس المتجر"""
        total_revenue = sum(p.get('price', 0) * p.get('sales', 0) for p in self.products)
        total_orders = sum(p.get('sales', 0) for p in self.products)
        total_views = sum(p.get('views', 0) for p in self.products)
        
        avg_order = total_revenue / total_orders if total_orders > 0 else 0
        conversion = (total_orders / total_views * 100) if total_views > 0 else 0
        
        users = self.leads.get('users', [])
        new_today = len([u for u in users if datetime.now().isoformat()[:10] in u.get('joined', '')[:10]])
        
        return StoreMetrics(
            total_revenue=round(total_revenue, 2),
            total_orders=total_orders,
            avg_order_value=round(avg_order, 2),
            conversion_rate=round(conversion, 2),
            returning_customers=len(users) - new_today,
            new_customers=new_today
        )
    
    def get_top_products(self, limit: int = 10) -> List[ProductMetrics]:
        """الحصول على أفضل المنتجات"""
        metrics = []
        
        for p in self.products:
            views = p.get('views', 0)
            sales = p.get('sales', 0)
            price = p.get('price', 0)
            
            conversion_rate = (sales / views * 100) if views > 0 else 0
            revenue = price * sales
            
            # Performance score (0-100)
            score = min(100, (conversion_rate * 10) + (sales * 2) + (revenue / 100))
            
            metrics.append(ProductMetrics(
                product_id=p.get('id', ''),
                name=p.get('name', {}).get('ar', 'N/A'),
                views=views,
                conversions=sales,
                revenue=round(revenue, 2),
                conversion_rate=round(conversion_rate, 2),
                performance_score=round(score, 1)
            ))
        
        # Sort by performance score
        metrics.sort(key=lambda x: x.performance_score, reverse=True)
        return metrics[:limit]
    
    def get_underperforming_products(self, threshold: float = 2.0, limit: int = 100) -> List[ProductMetrics]:
        """الحصول على المنتجات ضعيفة الأداء"""
        all_products = self.get_top_products(limit=1000)
        underperforming = [p for p in all_products if p.conversion_rate < threshold]
        return underperforming[:limit]
    
    def analyze_customer_segments(self) -> Dict[str, Any]:
        """تحليل شرائح العملاء"""
        users = self.leads.get('users', [])
        
        segments = {
            "vip": [],      # +5 orders
            "active": [],   # 2-4 orders
            "new": [],      # 1 order
            "dormant": []   # 0 orders, old account
        }
        
        for u in users:
            orders = u.get('orders', 0)
            chats = u.get('chats', 0)
            
            if orders >= 5:
                segments["vip"].append(u)
            elif orders >= 2:
                segments["active"].append(u)
            elif orders == 1:
                segments["new"].append(u)
            else:
                segments["dormant"].append(u)
        
        return {
            "vip_count": len(segments["vip"]),
            "active_count": len(segments["active"]),
            "new_count": len(segments["new"]),
            "dormant_count": len(segments["dormant"]),
            "total_customers": len(users)
        }
    
    def generate_insights(self) -> List[str]:
        """توليد رؤى تحليلية"""
        insights = []
        
        # Store metrics
        metrics = self.calculate_store_metrics()
        
        if metrics.conversion_rate < 1:
            insights.append("⚠️ معدل التحويل منخفض (<1%) - يحتاج تحسين")
        elif metrics.conversion_rate > 3:
            insights.append("🎉 معدل التحويل ممتاز!")
        
        if metrics.avg_order_value < 30:
            insights.append("💡平均值订单价值低 - 可以推广更高价值的产品")
        
        # Product insights
        top = self.get_top_products(limit=1)
        if top:
            insights.append(f"🏆 أفضل منتج: {top[0].name}")
        
        # Customer insights
        segments = self.analyze_customer_segments()
        dormant_pct = (segments["dormant_count"] / segments["total_customers"] * 100) if segments["total_customers"] > 0 else 0
        
        if dormant_pct > 50:
            insights.append(f"📧 {dormant_pct:.0f}% من العملاء غير نشطين - يُنصح بحملة إعادة تفعيل")
        
        # Category performance
        categories = {}
        for p in self.products:
            cat = p.get('category', 'other')
            if cat not in categories:
                categories[cat] = {"sales": 0, "views": 0}
            categories[cat]["sales"] += p.get('sales', 0)
            categories[cat]["views"] += p.get('views', 0)
        
        best_cat = max(categories.items(), key=lambda x: x[1]["sales"], default=(None, None))
        if best_cat[0]:
            insights.append(f"📦 الفئة الأفضل: {best_cat[0]}")
        
        return insights
    
    def predict_trends(self) -> Dict:
        """التنبؤ بالاتجاهات"""
        # Simple trend analysis based on recent activity
        return {
            "next_best_selling": self.get_top_products(limit=3),
            "needs_attention": self.get_underperforming_products(limit=5),
            "seasonal_forecast": "Q2 tends to be strong for electronics",
            "recommendation": "Focus on high-conversion products"
        }
    
    def generate_recommendations(self) -> List[Dict]:
        """توليد توصيات لتحسين الأداء"""
        recommendations = []
        
        # Conversion optimization
        metrics = self.calculate_store_metrics()
        if metrics.conversion_rate < 2:
            recommendations.append({
                "category": "conversion",
                "priority": "high",
                "action": "تحسين صور المنتجات والأوصاف",
                "impact": "قد يرفع التحويل بنسبة 20-30%"
            })
        
        # Product mix
        underperforming = self.get_underperforming_products()
        if len(underperforming) > 10:
            recommendations.append({
                "category": "inventory",
                "priority": "medium",
                "action": "مراجعة المنتجات ضعيفة الأداء",
                "impact": "تحسين إدارة المخزون"
            })
        
        # Customer retention
        segments = self.analyze_customer_segments()
        if segments["dormant_count"] > segments["active_count"]:
            recommendations.append({
                "category": "marketing",
                "priority": "high",
                "action": "حملة إعادة تفعيل العملاء",
                "impact": "زيادة المبيعات المتكررة"
            })
        
        # Pricing
        avg_price = sum(p.get('price', 0) for p in self.products) / len(self.products) if self.products else 0
        if avg_price < 50:
            recommendations.append({
                "category": "pricing",
                "priority": "medium",
                "action": "إضافة منتجات بأسعار أعلى",
                "impact": "رفع قيمة متوسط الطلب"
            })
        
        return recommendations
    
    def create_daily_report(self) -> Dict:
        """إنشاء تقرير يومي شامل"""
        metrics = self.calculate_store_metrics()
        top_products = self.get_top_products(limit=5)
        underperforming = self.get_underperforming_products(limit=5)
        segments = self.analyze_customer_segments()
        insights = self.generate_insights()
        recommendations = self.generate_recommendations()
        
        report = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "generated_at": datetime.now().isoformat(),
            "store_metrics": asdict(metrics),
            "top_products": [asdict(p) for p in top_products],
            "products_needing_attention": [asdict(p) for p in underperforming],
            "customer_segments": segments,
            "ai_insights": insights,
            "recommendations": recommendations,
            "next_actions": [
                r["action"] for r in recommendations[:3]
            ]
        }
        
        return report
    
    def save_analytics_history(self, report: Dict):
        """حفظ تاريخ التحليلات"""
        try:
            history = []
            try:
                with open(self.config.ANALYTICS_FILE, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except:
                pass
            
            history.append(report)
            
            # Keep last 30 days
            if len(history) > 30:
                history = history[-30:]
            
            with open(self.config.ANALYTICS_FILE, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log.error(f"Error saving analytics: {e}")
    
    def get_trend_data(self, days: int = 7) -> List[Dict]:
        """الحصول على بيانات الاتجاه"""
        try:
            with open(self.config.ANALYTICS_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
            return history[-days:] if history else []
        except:
            return []


def asdict(obj):
    """Convert dataclass to dict"""
    if hasattr(obj, '__dataclass_fields__'):
        return {f: getattr(obj, f) for f in obj.__dataclass_fields__}
    return obj


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("📊 NEO PULSE HUB — AI Analytics Dashboard")
    print("=" * 70)
    
    analytics = AIAnalyticsEngine()
    
    # Generate report
    print("\n📈 Generating Analytics Report...")
    report = analytics.create_daily_report()
    
    # Store metrics
    print("\n🏪 Store Metrics:")
    sm = report['store_metrics']
    print(f"   Total Revenue: ${sm['total_revenue']}")
    print(f"   Total Orders: {sm['total_orders']}")
    print(f"   Avg Order Value: ${sm['avg_order_value']}")
    print(f"   Conversion Rate: {sm['conversion_rate']}%")
    
    # Top products
    print("\n🏆 Top 5 Products:")
    for i, p in enumerate(report['top_products'][:5], 1):
        print(f"   {i}. {p['name']}")
        print(f"      Sales: {p['conversions']} | Revenue: ${p['revenue']} | Score: {p['performance_score']}")
    
    # Customer segments
    print("\n👥 Customer Segments:")
    cs = report['customer_segments']
    print(f"   VIP: {cs['vip_count']} | Active: {cs['active_count']} | New: {cs['new_count']} | Dormant: {cs['dormant_count']}")
    
    # AI Insights
    print("\n💡 AI Insights:")
    for insight in report['ai_insights']:
        print(f"   {insight}")
    
    # Recommendations
    print("\n📋 Recommendations:")
    for rec in report['recommendations'][:3]:
        print(f"   [{rec['priority'].upper()}] {rec['action']}")
    
    # Save report
    analytics.save_analytics_history(report)
    print("\n✅ Report saved to analytics_history.json")
    
    print("\n" + "=" * 70)
    print("✅ Analytics Dashboard Complete!")
    print("=" * 70)

if __name__ == "__main__":
    main()