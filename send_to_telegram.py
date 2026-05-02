import os
import json
import requests
import time
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = "6790340715" # تم استخراجه من getUpdates

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def run():
    if not TOKEN or not CHANNEL_ID:
        print("Missing TG Config")
        return

    campaigns_file = "/home/ubuntu/neo-pulse-hub/real_campaigns.json"
    if not os.path.exists(campaigns_file):
        print("Campaigns file not found")
        return

    with open(campaigns_file, 'r', encoding='utf-8') as f:
        campaigns = json.load(f)

    print(f"Starting to send {len(campaigns)} campaigns...")
    for campaign in campaigns:
        name = campaign.get("product_name")
        tg_text = campaign.get("platforms", {}).get("telegram", "")
        
        # Clean up JSON if present in text
        if "```json" in tg_text:
            try:
                import re
                match = re.search(r'\{.*\}', tg_text, re.DOTALL)
                if match:
                    data = json.loads(match.group())
                    if "texts" in data and len(data["texts"]) > 0:
                        clean_text = data["texts"][0]
                        # Rebuild message
                        tg_text = f"🚀 <b>{name}</b>\n\n{clean_text}\n\n💰 السعر: ${campaign.get('product_price')}\n⭐ التقييم: {campaign.get('product_rating')}\n\n🔗 <b>رابط الشراء:</b> {campaign.get('affiliate_link')}\n\n#NeoPulseHub #Amazon"
            except:
                pass

        print(f"Sending campaign for: {name}")
        res = send_message(tg_text)
        if res and res.get("ok"):
            print(f"✅ Success: {name}")
        else:
            print(f"❌ Failed: {name} - {res}")
        
        time.sleep(2) # Avoid flood

if __name__ == "__main__":
    run()
