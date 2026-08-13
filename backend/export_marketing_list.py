import json
import csv
from pathlib import Path
from datetime import datetime

def export_marketing_list():
    # 1. Collect from subscribers.json
    subscribers_file = Path("data/subscribers.json")
    leads_file = Path("leads.json")
    newsletter_file = Path("newsletter.json")
    
    all_emails = {} # email -> {name, source, date}

    # Load from subscribers.json (Website & OAuth)
    if subscribers_file.exists():
        try:
            with open(subscribers_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for s in data.get('subscribers', []):
                    email = s.get('email', '').lower().strip()
                    if email:
                        all_emails[email] = {
                            "name": s.get('name', 'User'),
                            "source": s.get('source', 'website'),
                            "date": s.get('timestamp', '')
                        }
        except Exception as e:
            print(f"Error reading subscribers.json: {e}")

    # Load from leads.json (Telegram & Backend)
    if leads_file.exists():
        try:
            with open(leads_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for u in data.get('users', []):
                    email = u.get('email', '').lower().strip()
                    if email:
                        all_emails[email] = {
                            "name": u.get('name', u.get('username', 'User')),
                            "source": "telegram/lead",
                            "date": u.get('joined', '')
                        }
        except Exception as e:
            print(f"Error reading leads.json: {e}")

    # Export to CSV
    output_dir = Path("docs/exports")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = output_dir / f"marketing_campaign_list_{timestamp}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Email', 'Name', 'Source', 'Date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for email, info in all_emails.items():
            writer.writerow({
                'Email': email,
                'Name': info['name'],
                'Source': info['source'],
                'Date': info['date']
            })

    print(f"🚀 Successfully exported {len(all_emails)} unique emails for marketing.")
    print(f"📁 File location: {filename}")
    return filename

if __name__ == "__main__":
    export_marketing_list()
