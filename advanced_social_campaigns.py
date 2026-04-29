#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Social Media Campaign Generator
منظومة متقدمة لإنشاء حملات تسويقية على وسائل التواصل الاجتماعي
"""

import json
import os
from datetime import datetime
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class SocialMediaCampaignGenerator:
    def __init__(self):
        self.campaigns = []
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_channel = os.getenv('TELEGRAM_CHANNEL_ID')
        
    def generate_campaign_variations(self, product):
        """توليد عدة صيغ للحملة الواحدة"""
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """أنت خبير تسويق رقمي. أنشئ 5 صيغ مختلفة وجذابة جداً لحملة تسويقية على وسائل التواصل الاجتماعي.
كل صيغة يجب أن تكون:
- قصيرة (150-200 حرف)
- تحتوي على emoji جذابة
- تحفز على الشراء
- تشمل call-to-action واضح
أرجع الإجابة بصيغة JSON مع مصفوفة campaigns"""
                    },
                    {
                        "role": "user",
                        "content": f"المنتج: {product['name']}\nالفئة: {product['category']}\nالسعر: ${product['price']}\nالتقييم: {product['rating']}/5\nالوصف: {product['description']}"
                    }
                ],
                temperature=0.8,
                max_tokens=1000
            )
            
            try:
                result = json.loads(response.choices[0].message.content)
                return result.get('campaigns', [])
            except:
                return [response.choices[0].message.content]
        except Exception as e:
            print(f"خطأ في توليد الحملات: {e}")
            return []
    
    def create_telegram_campaign(self, product, campaign_text):
        """إنشاء حملة تيليجرام"""
        affiliate_link = f"https://www.amazon.com/dp/{product['asin']}?tag=neopulsehub-20"
        
        message = f"""
{campaign_text}

📦 المنتج: {product['name']}
⭐ التقييم: {product['rating']}/5 ({product['reviews']} تقييم)
💰 السعر: ${product['price']}

🔗 اشتري الآن: {affiliate_link}

#تسوق_ذكي #أمازون #منتجات_تقنية
"""
        return message
    
    def create_instagram_campaign(self, product, campaign_text):
        """إنشاء حملة إنستجرام"""
        hashtags = "#تسوق_ذكي #أمازون #منتجات_تقنية #تقنية #ذكاء_اصطناعي #أفضل_الأسعار #عروض_حصرية"
        
        message = f"""
{campaign_text}

📦 {product['name']}
⭐ {product['rating']}/5
💰 ${product['price']}

{hashtags}
"""
        return message
    
    def create_whatsapp_campaign(self, product, campaign_text):
        """إنشاء حملة واتساب"""
        affiliate_link = f"https://www.amazon.com/dp/{product['asin']}?tag=neopulsehub-20"
        
        message = f"""
🎉 عرض حصري! 🎉

{campaign_text}

📦 {product['name']}
⭐ التقييم: {product['rating']}/5
💰 السعر: ${product['price']}

👉 اشتري الآن: {affiliate_link}

#NEO_PULSE_HUB
"""
        return message
    
    def generate_daily_campaigns(self, products):
        """توليد حملات يومية متعددة"""
        all_campaigns = []
        
        for product in products:
            print(f"📝 توليد حملات لـ: {product['name']}")
            
            # Generate multiple variations
            variations = self.generate_campaign_variations(product)
            
            for i, variation in enumerate(variations):
                campaign = {
                    "product": product['name'],
                    "category": product['category'],
                    "price": product['price'],
                    "asin": product['asin'],
                    "timestamp": datetime.now().isoformat(),
                    "variation": i + 1,
                    "telegram": self.create_telegram_campaign(product, variation),
                    "instagram": self.create_instagram_campaign(product, variation),
                    "whatsapp": self.create_whatsapp_campaign(product, variation)
                }
                all_campaigns.append(campaign)
        
        # Save campaigns
        with open('daily_campaigns.json', 'w', encoding='utf-8') as f:
            json.dump(all_campaigns, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ تم توليد {len(all_campaigns)} حملة تسويقية")
        return all_campaigns
    
    def send_telegram_campaigns(self, campaigns):
        """إرسال الحملات إلى تيليجرام"""
        if not self.telegram_token or not self.telegram_channel:
            print("⚠️ لم يتم تكوين بيانات تيليجرام")
            return
        
        try:
            import requests
            
            for campaign in campaigns:
                url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
                
                payload = {
                    "chat_id": self.telegram_channel,
                    "text": campaign['telegram'],
                    "parse_mode": "HTML"
                }
                
                response = requests.post(url, json=payload)
                
                if response.status_code == 200:
                    print(f"✅ تم إرسال حملة: {campaign['product']}")
                else:
                    print(f"❌ خطأ في إرسال الحملة: {response.text}")
        
        except Exception as e:
            print(f"❌ خطأ في الاتصال بـ تيليجرام: {e}")
    
    def print_campaigns_preview(self, campaigns):
        """طباعة معاينة للحملات"""
        print("\n" + "="*60)
        print("📊 معاينة الحملات التسويقية")
        print("="*60)
        
        for i, campaign in enumerate(campaigns[:3]):  # Show first 3
            print(f"\n🎯 الحملة #{i+1} - {campaign['product']}")
            print("-" * 60)
            print("📱 تيليجرام:")
            print(campaign['telegram'][:150] + "...")
            print("\n📸 إنستجرام:")
            print(campaign['instagram'][:150] + "...")
            print("\n💬 واتساب:")
            print(campaign['whatsapp'][:150] + "...")
            print("-" * 60)

if __name__ == "__main__":
    # Sample products
    sample_products = [
        {
            "name": "Apple Watch Series 9",
            "asin": "B0CQSW5P6N",
            "category": "ساعات ذكية",
            "price": 399.99,
            "rating": 4.7,
            "reviews": 2543,
            "description": "أحدث ساعة ذكية من أبل"
        },
        {
            "name": "Sony WH-1000XM5",
            "asin": "B0BDHZZ4LT",
            "category": "سماعات",
            "price": 399.99,
            "rating": 4.8,
            "reviews": 4521,
            "description": "أفضل سماعات إلغاء ضوضاء"
        }
    ]
    
    generator = SocialMediaCampaignGenerator()
    campaigns = generator.generate_daily_campaigns(sample_products)
    generator.print_campaigns_preview(campaigns)
    
    print("\n✅ تم حفظ الحملات في: daily_campaigns.json")
