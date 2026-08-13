import json
import random
from pathlib import Path

def enrich_products():
    products_file = Path("products.json")
    if not products_file.exists():
        print("Error: products.json not found")
        return

    with open(products_file, 'r', encoding='utf-8') as f:
        products = json.load(f)

    print(f"📦 Enriching {len(products)} products with global data...")

    # Sample global data templates
    specs_templates = {
        "smartwatch": {
            "ar": {"الشاشة": "AMOLED 1.43 inch", "البطارية": "حتى 14 يوم", "المقاومة": "IP68 ضد الماء", "المستشعرات": "نبضات القلب، SPO2، تتبع النوم"},
            "en": {"Display": "AMOLED 1.43 inch", "Battery": "Up to 14 days", "Waterproof": "IP68 Rated", "Sensors": "Heart Rate, SPO2, Sleep Tracking"}
        },
        "earbuds": {
            "ar": {"إلغاء الضوضاء": "نشط (ANC)", "وقت التشغيل": "30 ساعة مع العلبة", "الاتصال": "Bluetooth 5.3", "الوزن": "4.5 جرام لكل سماعة"},
            "en": {"Noise Cancellation": "Active (ANC)", "Playtime": "30 Hours with Case", "Connectivity": "Bluetooth 5.3", "Weight": "4.5g per bud"}
        },
        "smart-home": {
            "ar": {"التوافق": "Alexa, Google Home", "الجهد": "110-240V", "الاتصال": "Wi-Fi 2.4GHz", "المادة": "بلاستيك مقاوم للحريق"},
            "en": {"Compatibility": "Alexa, Google Home", "Voltage": "110-240V", "Connectivity": "Wi-Fi 2.4GHz", "Material": "Fire-resistant Plastic"}
        }
    }

    for p in products:
        cat = p.get('category', 'general')
        
        # 1. Add Gallery (Main image + 3 variations)
        main_img = p.get('image', '')
        if main_img:
            p['gallery'] = [
                main_img,
                main_img.replace('.jpg', '_alt1.jpg') if '.jpg' in main_img else main_img,
                main_img.replace('.jpg', '_alt2.jpg') if '.jpg' in main_img else main_img,
                "https://placehold.co/600x600/0a0d1a/60a5fa?text=Detail+View"
            ]
        else:
            p['gallery'] = ["https://placehold.co/600x600/0a0d1a/60a5fa?text=Product+Image"]

        # 2. Add Technical Specifications
        template = specs_templates.get(cat, specs_templates['smartwatch'])
        p['specifications'] = template

        # 3. Add Global Prices (SAR, AED, EUR)
        base_price = float(p.get('price', 100))
        p['global_prices'] = {
            "USD": base_price,
            "SAR": round(base_price * 3.75, 2),
            "AED": round(base_price * 3.67, 2),
            "EUR": round(base_price * 0.92, 2)
        }

        # 4. Add Wholesale Info (Alibaba style)
        p['wholesale'] = {
            "moq": random.choice([5, 10, 50, 100]),
            "bulk_price": round(base_price * 0.8, 2)
        }

    with open(products_file, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

    print(f"✅ Successfully enriched products.json")

if __name__ == "__main__":
    enrich_products()
