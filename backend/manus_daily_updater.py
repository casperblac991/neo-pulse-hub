# -*- coding: utf-8 -*-
"""
NEO PULSE HUB — Manus API Daily Updater
سكربت الربط الرسمي مع Manus لتحديث المتجر تلقائياً
"""

import os
import requests
import json
import time
import logging

# ── الإعدادات ────────────────────────────────────────────────────────
MANUS_API_KEY = os.environ.get("MANUS_API_KEY", "")
BASE_URL = "https://api.manus.ai"

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("manus_updater")

def create_manus_task(prompt):
    """إنشاء مهمة جديدة لـ Manus"""
    if not MANUS_API_KEY:
        log.error("❌ MANUS_API_KEY is missing!")
        return None

    headers = {
        "x-manus-api-key": MANUS_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "goal": prompt,
        "agent_profile": "standard" # يمكن استخدام lite لتوفير التكلفة أو max للمهام المعقدة
    }

    # في v2، المسار هو task.create والهدف يوضع في message.content
    payload = {
        "message": {
            "content": prompt
        }
    }

    try:
        response = requests.post(f"{BASE_URL}/v2/task.create", json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            task_id = data.get("task_id")
            log.info(f"✅ Task created successfully! Task ID: {task_id}")
            return task_id
        else:
            log.error(f"❌ Failed to create task: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        log.error(f"❌ Error during API call: {e}")
        return None

def check_task_status(task_id):
    """التحقق من حالة المهمة"""
    headers = {"x-manus-api-key": MANUS_API_KEY}
    try:
        response = requests.get(f"{BASE_URL}/v2/task.detail?task_id={task_id}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            # في v2، الحالة قد تكون في مستوى أعلى أو داخل الكائن
            status = data.get("status") or data.get("data", {}).get("status")
            log.info(f"🔄 Task {task_id} status: {status}")
            return status
        return "error"
    except:
        return "error"

def run_daily_update():
    """تشغيل مهمة التحديث اليومي"""
    prompt = """
    أنت المساعد الذكي لمنصة Neo Pulse Hub. 
    المطلوب منك اليوم:
    1. البحث عن أحدث 3 منتجات تقنية ذكية (ساعات أو سماعات) صدرت هذا الأسبوع.
    2. إضافتها لملف products.json مع أسماء عربية وإنجليزية وصور عالية الجودة.
    3. كتابة مقال مراجعة احترافي لكل منتج جديد ونشره في المدونة باللغتين.
    4. تأكد من أن الروابط تعمل وأن الصور فريدة.
    بعد الانتهاء، ارفع التغييرات لمستودع GitHub.
    """
    
    log.info("🚀 Starting Daily Update via Manus API...")
    task_id = create_manus_task(prompt)
    
    if task_id:
        # انتظر حتى تكتمل المهمة (Polling)
        # ملاحظة: في الإنتاج يفضل استخدام Webhooks بدلاً من الانتظار
        while True:
            status = check_task_status(task_id)
            if status in ["completed", "stopped", "failed"]:
                log.info(f"🏁 Task finished with status: {status}")
                break
            time.sleep(60) # انتظر دقيقة قبل الفحص التالي

if __name__ == "__main__":
    # هذا السكربت يحتاج MANUS_API_KEY ليعمل
    if MANUS_API_KEY:
        run_daily_update()
    else:
        print("💡 يرجى ضبط MANUS_API_KEY في متغيرات البيئة للبدء.")
