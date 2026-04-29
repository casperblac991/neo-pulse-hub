#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real Marketing Campaigns - حملات تسويقية حقيقية بدون محاكاة
تستخدم بيانات منتجات حقيقية وتولد نصوص جذابة فعلية
"""

import json
import os
from datetime import datetime
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class RealMarketingCampaigns:
    def __init__(self):
        self.campaigns = []
        self.products = []
        self.load_products()
    
    def load_products(self):
        """تحميل المنتجات الحقيقية"""
        if os.path.exists('real_products.json'):
            with open('real_products.json', 'r', encoding='utf-8') as f:
                self.products = json.load(f)
    
    def generate_real_campaign(self, product):
        """توليد حملة حقيقية بناءً على بيانات المنتج"""
        try:
            # طلب من GPT لتوليد نصوص حقيقية وجذابة
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """أنت خبير تسويق رقمي. أنشئ 3 نصوص حملات تسويقية حقيقية وجذابة لمنتج معين.
كل نص يجب أن يكون:
- قصير (100-150 حرف)
- يحتوي على emoji جذابة
- يحفز على الشراء الفوري
- يتضمن call-to-action واضح
أرجع الإجابة بصيغة JSON مع مصفوفة texts"""
                    },
                    {
                        "role": "user",
                        "content": f"""المنتج: {product['name']}
الفئة: {product['category']}
السعر: ${product['price']}
التقييم: {product['rating']}/5 ({product['reviews']:,} تقييم)
المصدر: {product['source']}
الوصف: {product['description']}"""
                    }
                ],
                temperature=0.8,
                max_tokens=500
            )
            
            result = response.choices[0].message.content
            try:
                data = json.loads(result)
                return data.get('texts', [result])
            except:
                return [result]
        except Exception as e:
            print(f"❌ خطأ في توليد الحملة: {e}")
            return []
    
    def create_telegram_post(self, product, campaign_text):
        """إنشاء منشور تيليجرام"""
        return f"""
{campaign_text}

📦 {product['name']}
⭐ {product['rating']}/5 ({product['reviews']:,} تقييم)
💰 ${product['price']}
📌 المصدر: {product['source']}

🔗 اشتري الآن: {product['affiliate_link']}

#تسوق_ذكي #أمازون #{product['category'].replace(' ', '_')}
"""
    
    def create_instagram_post(self, product, campaign_text):
        """إنشاء منشور إنستجرام"""
        return f"""
{campaign_text}

📦 {product['name']}
⭐ {product['rating']}/5
💰 ${product['price']}

#تسوق_ذكي #أمازون #منتجات_تقنية #عروض_حصرية
"""
    
    def create_whatsapp_message(self, product, campaign_text):
        """إنشاء رسالة واتساب"""
        return f"""
🎉 عرض حصري! 🎉

{campaign_text}

📦 {product['name']}
⭐ التقييم: {product['rating']}/5
💰 السعر: ${product['price']}
📌 المصدر: {product['source']}

👉 اشتري الآن: {product['affiliate_link']}

#NEO_PULSE_HUB
"""
    
    def generate_all_campaigns(self):
        """توليد حملات لجميع المنتجات"""
        print("\n" + "="*60)
        print("📢 بدء توليد الحملات التسويقية الحقيقية")
        print("="*60 + "\n")
        
        all_campaigns = []
        
        for i, product in enumerate(self.products, 1):
            print(f"📝 [{i}/{len(self.products)}] توليد حملات لـ: {product['name']}")
            
            # توليد نصوص حقيقية
            campaign_texts = self.generate_real_campaign(product)
            
            if not campaign_texts:
                print(f"   ⚠️ لم يتم توليد نصوص للمنتج")
                continue
            
            # إنشاء حملات لكل نص
            for j, text in enumerate(campaign_texts, 1):
                campaign = {
                    "id": f"{product['asin']}_campaign_{j}",
                    "product_name": product['name'],
                    "product_price": product['price'],
                    "product_rating": product['rating'],
                    "product_source": product['source'],
                    "affiliate_link": product['affiliate_link'],
                    "created_at": datetime.now().isoformat(),
                    "campaign_text": text,
                    "platforms": {
                        "telegram": self.create_telegram_post(product, text),
                        "instagram": self.create_instagram_post(product, text),
                        "whatsapp": self.create_whatsapp_message(product, text)
                    }
                }
                all_campaigns.append(campaign)
                print(f"   ✅ تم توليد حملة #{j}")
        
        # حفظ الحملات
        with open('real_campaigns.json', 'w', encoding='utf-8') as f:
            json.dump(all_campaigns, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ تم توليد {len(all_campaigns)} حملة تسويقية حقيقية")
        return all_campaigns
    
    def print_campaign_samples(self, campaigns):
        """طباعة عينات من الحملات"""
        print("\n" + "="*60)
        print("📊 عينات من الحملات المولدة")
        print("="*60)
        
        for i, campaign in enumerate(campaigns[:2]):
            print(f"\n🎯 الحملة #{i+1} - {campaign['product_name']}")
            print("-" * 60)
            print("📱 تيليجرام:")
            print(campaign['platforms']['telegram'][:200] + "...")
            print("\n📸 إنستجرام:")
            print(campaign['platforms']['instagram'][:200] + "...")
            print("\n💬 واتساب:")
            print(campaign['platforms']['whatsapp'][:200] + "...")
            print("-" * 60)

if __name__ == "__main__":
    generator = RealMarketingCampaigns()
    campaigns = generator.generate_all_campaigns()
    generator.print_campaign_samples(campaigns)
    
    print(f"\n✅ تم حفظ الحملات في: real_campaigns.json")
