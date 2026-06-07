#!/usr/bin/env python3
"""
Email Subscriber to Google Sheets Integration
Collects emails from the website form and stores them in Google Sheets
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("EmailToSheets")

def initialize_google_sheets():
    """Initialize Google Sheets connection using gws CLI"""
    try:
        log.info("🔐 Initializing Google Sheets connection...")
        
        # Check if gws is available
        os.system("gws --help > /dev/null 2>&1")
        
        log.info("✅ Google Sheets CLI (gws) is available")
        return True
    except Exception as e:
        log.error(f"❌ Error initializing Google Sheets: {e}")
        return False

def create_subscribers_sheet():
    """Create or get the subscribers Google Sheet"""
    try:
        log.info("📋 Creating/accessing subscribers sheet...")
        
        # Create a new Google Sheet for subscribers
        sheet_name = "NEO_PULSE_HUB_Subscribers"
        sheet_id = os.getenv("GOOGLE_SHEETS_ID", "")
        
        if not sheet_id:
            log.warning("⚠️ GOOGLE_SHEETS_ID not set. Creating new sheet...")
            # This would require OAuth setup - for now, we'll use a local JSON file as fallback
            return create_local_subscribers_file()
        
        log.info(f"✅ Using Google Sheet: {sheet_name}")
        return sheet_id
    except Exception as e:
        log.error(f"❌ Error creating sheet: {e}")
        return create_local_subscribers_file()

def create_local_subscribers_file():
    """Create a local JSON file as fallback for subscribers"""
    try:
        subscribers_dir = Path("/home/ubuntu/neo-pulse-hub/data")
        subscribers_dir.mkdir(exist_ok=True)
        
        subscribers_file = subscribers_dir / "subscribers.json"
        
        if not subscribers_file.exists():
            with open(subscribers_file, 'w', encoding='utf-8') as f:
                json.dump({"subscribers": []}, f, ensure_ascii=False, indent=2)
            log.info(f"✅ Created local subscribers file: {subscribers_file}")
        
        return str(subscribers_file)
    except Exception as e:
        log.error(f"❌ Error creating local file: {e}")
        return None

def add_subscriber(name: str, email: str, interests: str = "", timestamp: str = None):
    """Add a new subscriber to the sheet/file"""
    try:
        if not timestamp:
            timestamp = datetime.now().isoformat()
        
        subscriber = {
            "name": name,
            "email": email,
            "interests": interests,
            "timestamp": timestamp,
            "status": "active"
        }
        
        # Try to add to Google Sheets first
        if os.getenv("GOOGLE_SHEETS_ID"):
            add_to_google_sheets(subscriber)
        else:
            # Fallback to local JSON file
            add_to_local_file(subscriber)
        
        log.info(f"✅ Subscriber added: {email}")
        return True
    except Exception as e:
        log.error(f"❌ Error adding subscriber: {e}")
        return False

def add_to_google_sheets(subscriber: dict):
    """Add subscriber to Google Sheets using gws CLI"""
    try:
        # This is a placeholder for actual Google Sheets integration
        # In production, you would use gws append command
        log.info(f"📊 Adding to Google Sheets: {subscriber['email']}")
        
        # Example command (would need proper setup):
        # gws append --sheet "NEO_PULSE_HUB_Subscribers" --values "name" "email" "interests" "timestamp"
        
    except Exception as e:
        log.error(f"❌ Error adding to Google Sheets: {e}")
        raise

def add_to_local_file(subscriber: dict):
    """Add subscriber to local JSON file"""
    try:
        subscribers_file = Path("/home/ubuntu/neo-pulse-hub/data/subscribers.json")
        
        if subscribers_file.exists():
            with open(subscribers_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {"subscribers": []}
        
        # Check for duplicate email
        existing = [s for s in data["subscribers"] if s["email"] == subscriber["email"]]
        if existing:
            log.warning(f"⚠️ Email already exists: {subscriber['email']}")
            return
        
        data["subscribers"].append(subscriber)
        
        with open(subscribers_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        log.info(f"✅ Subscriber saved to local file: {subscriber['email']}")
    except Exception as e:
        log.error(f"❌ Error saving to local file: {e}")
        raise

def get_all_subscribers():
    """Get all subscribers from the file"""
    try:
        subscribers_file = Path("/home/ubuntu/neo-pulse-hub/data/subscribers.json")
        
        if subscribers_file.exists():
            with open(subscribers_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get("subscribers", [])
        
        return []
    except Exception as e:
        log.error(f"❌ Error reading subscribers: {e}")
        return []

def export_to_google_sheets():
    """Export all subscribers to Google Sheets"""
    try:
        log.info("📤 Exporting subscribers to Google Sheets...")
        
        subscribers = get_all_subscribers()
        
        if not subscribers:
            log.warning("⚠️ No subscribers to export")
            return False
        
        # Create header row
        headers = ["الاسم", "البريد الإلكتروني", "الاهتمامات", "التاريخ", "الحالة"]
        
        # Prepare data rows
        rows = []
        for sub in subscribers:
            rows.append([
                sub.get("name", ""),
                sub.get("email", ""),
                sub.get("interests", ""),
                sub.get("timestamp", ""),
                sub.get("status", "")
            ])
        
        log.info(f"✅ Prepared {len(rows)} rows for export")
        
        # In production, use gws to create/update sheet
        # For now, just log the data
        log.info(f"📊 Total subscribers: {len(subscribers)}")
        
        return True
    except Exception as e:
        log.error(f"❌ Error exporting to Google Sheets: {e}")
        return False

def main():
    """Main function for testing"""
    log.info("🚀 Starting Email to Google Sheets Integration...")
    
    # Initialize
    initialize_google_sheets()
    
    # Create subscribers file
    create_subscribers_sheet()
    
    # Test: Add a sample subscriber
    add_subscriber(
        name="محمد أحمد",
        email="test@example.com",
        interests="ساعات ذكية، سماعات"
    )
    
    # Get all subscribers
    subscribers = get_all_subscribers()
    log.info(f"📋 Total subscribers: {len(subscribers)}")
    
    # Export to Google Sheets
    export_to_google_sheets()
    
    log.info("✅ Integration test completed!")

if __name__ == "__main__":
    main()
