#!/usr/bin/env python3
import os, re, json, time, logging, requests
from typing import Optional

log = logging.getLogger("ai_engine")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
STORE_SYSTEM = "انت مساعد خدمة عملاء لمتجر NEO PULSE HUB للمنتجات الذكية. تحدث بالعربية دائما."

def _call(prompt, temperature=0.6, max_tokens=1500, system=None):
    if not GEMINI_API_KEY:
        return "مفتاح Gemini غير موجود"
    contents = []
    if system:
        contents.append({"role": "user", "parts": [{"text": system}]})
        contents.append({"role": "model", "parts": [{"text": "مفهوم."}]})
    contents.append({"role": "user", "parts": [{"text": prompt}]})
    for attempt in range(3):
        try:
            r = requests.post(
                GEMINI_URL + "?key=" + GEMINI_API_KEY,
                json={
                    "contents": contents,
                    "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens, "topP": 0.9},
                    "safetySettings": [
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                    ]
                },
                headers={"Content-Type": "application/json"},
                timeout=30,
            )
            if r.status_code == 200:
                return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            elif r.status_code == 429:
                time.sleep(2 ** attempt)
                continue
            else:
                return "عذرا حدث خطا"
        except:
            return "عذرا حدث خطا غير متوقع"
    return "الخادم مشغول"

def _call_json(prompt, temperature=0.3):
    result = _call(prompt + "\nارجع JSON فقط بدون اي نص او backticks.", temperature)
    try:
        clean = re.sub(r'```json|```', '', result).strip()
        match = re.search(r'[\[\{][\s\S]*[\]\}]', clean)
        if match:
            return json.loads(match.group())
    except Exception as e:
        log.error("JSON error: " + str(e))
    return None

def answer_customer(question, products_context="", faqs_context="", user_history=""):
    parts = [STORE_SYSTEM]
    if products_context:
        parts.append("المنتجات: " + products_context)
    if faqs_context:
        parts.append("الاسئلة الشائعة: " + faqs_context)
    if user_history:
        parts.append("تاريخ المحادثة: " + user_history)
    parts.append("سؤال الزبون: " + question)
    parts.append("اجب بشكل مختصر ومفيد.")
    return _call("\n\n".join(parts), temperature=0.5, max_tokens=500)

def analyze_sentiment(text):
    result = _call('حلل مشاعر هذا النص وأجب بكلمة واحدة (positive/negative/neutral/urgent): "' + text + '"', temperature=0.1, max_tokens=10)
    for s in ["positive", "negative", "neutral", "urgent"]:
        if s in result.lower():
            return s
    return "neutral"

def is_purchase_intent(text):
    result = _call('هل يعبر هذا النص عن نية شراء؟ أجب بـ yes أو no فقط: "' + text + '"', temperature=0.1, max_tokens=5)
    return "yes" in result.lower()

def categorize_query(text):
    result = _call('صنف هذا الاستفسار بكلمة واحدة (شكوى/استفسار_منتج/دعم_تقني/شحن_دفع/توصية/أخرى): "' + text + '"', temperature=0.1, max_tokens=20)
    for c in ["شكوى", "استفسار_منتج", "دعم_تقني", "شحن_دفع", "توصية", "أخرى"]:
        if c in result:
            return c
    return "أخرى"

def recommend_products(user_query, products, budget=None, preferences=None):
    lines = []
    for p in products[:20]:
        lines.append("ID:" + p["id"] + " | " + p.get("name_ar","") + " | $" + str(p["price"]) + " | " + p.get("category","") + " | تقييم:" + str(p.get("rating",0)))
    products_summary = "\n".join(lines)
    parts = [
        "انت محرك توصيات لمتجر تقنية ذكية.",
        "المنتجات المتاحة:",
        products_summary,
        'طلب الزبون: "' + user_query + '"',
    ]
    if budget:
        parts.append("الميزانية: $" + str(budget))
    if preferences:
        parts.append("التفضيلات: " + ", ".join(preferences))
    parts.append('ارجع JSON: {"recommendations": ["ID1","ID2","ID3"], "reason": "السبب"}')
    result = _call_json("\n".join(parts))
    if result and "recommendations" in result:
        return result.get("recommendations", [])
    return [p["id"] for p in sorted(products, key=lambda x: x.get("rating", 0), reverse=True)[:3]]

def extract_budget(text):
    result = _call('استخرج الميزانية بالدولار من هذا النص وارجع رقما فقط، اذا لم توجد ارجع null: "' + text + '"', temperature=0.1, max_tokens=20)
    try:
        clean = re.sub(r'[^\d.]', '', result.strip())
        val = float(clean)
        return val if 1 < val < 100000 else None
    except:
        return None

def generate_product_description(product_data):
    name = product_data.get("name_ar", "")
    features = ", ".join(product_data.get("features_ar", [])[:4])
    return _call("اكتب وصفا تسويقيا جذابا بالعربية لهذا المنتج (جملتان):\nالاسم: " + name + "\nالمزايا: " + features, temperature=0.7, max_tokens=200)

def search_product_by_description(query):
    prompt = (
        'انت خبير منتجات تقنية. ابحث عن افضل منتج حقيقي لهذا الوصف: "' + query + '"\n\n'
        'ارجع JSON:\n'
        '{\n'
        '  "found": true,\n'
        '  "name_en": "Product Name",\n'
        '  "name_ar": "اسم المنتج",\n'
        '  "brand": "الماركة",\n'
        '  "category": "smartwatch|smart-glasses|health|smart-home|earbuds|productivity",\n'
        '  "category_ar": "الفئة",\n'
        '  "estimated_price_usd": 99.99,\n'
        '  "original_retail_usd": 129.99,\n'
        '  "rating": 4.5,\n'
        '  "reviews_count": 1250,\n'
        '  "stock": 30,\n'
        '  "shipping_days": "7-14",\n'
        '  "features_ar": ["ميزة1","ميزة2","ميزة3"],\n'
        '  "description_ar": "وصف تسويقي",\n'
        '  "tags": ["tag1","tag2"],\n'
        '  "image_search_query": "product name",\n'
        '  "why_recommended": "السبب"\n'
        '}'
    )
    return _call_json(prompt)

def generate_mini_report(product):
    name = product.get("name_ar", "")
    price = str(product.get("price", 0))
    rating = str(product.get("rating", 0))
    features = ", ".join(product.get("features_ar", [])[:4])
    return _call(
        "اكتب تقريرا مصغرا بالعربية في 5 نقاط عن:\n" + name + " - $" + price + "\nالتقييم: " + rating + "/5\nالمزايا: " + features + "\nالنقاط: 1-نقاط القوة 2-لمن مناسب 3-قيمة السعر 4-ضعف محتمل 5-التوصية",
        temperature=0.5, max_tokens=500
    )

def generate_marketing_post(product, platform="telegram"):
    chars = {"telegram": 500, "instagram": 300, "whatsapp": 400}
    name = product.get("name_ar", "")
    price = str(product.get("price", 0))
    discount = str(product.get("discount", 0))
    feature = product.get("features_ar", [""])[0] if product.get("features_ar") else ""
    limit = str(chars.get(platform, 400))
    return _call("اكتب منشورا تسويقيا ل" + platform + " بالعربية:\nالمنتج: " + name + "\nالسعر: $" + price + " (خصم " + discount + "%)\nابرز مزية: " + feature + "\nالحد: " + limit + " حرف. استخدم emoji مناسبة.", temperature=0.8, max_tokens=400)

def generate_store_report(analytics):
    return _call(
        "انت مستشار تجارة الكترونية. حلل هذه الاحصائيات واعط توصيات:\n\n"
        "المستخدمون: " + str(analytics.get("total_users", 0)) + "\n"
        "الطلبات: " + str(analytics.get("total_orders", 0)) + "\n"
        "الايرادات: $" + str(analytics.get("total_revenue", 0)) + "\n"
        "المنتجات: " + str(analytics.get("total_products", 0)) + "\n"
        "الطلبات المعلقة: " + str(analytics.get("pending_orders", 0)) + "\n"
        "مخزون منخفض: " + str(analytics.get("low_stock_count", 0)) + " منتج\n\n"
        "اكتب تقريرا بالعربية في 4 فقرات.",
        temperature=0.5, max_tokens=600
    )

def suggest_price(product, market_data=""):
    name = product.get("name_ar", "")
    base_cost = str(round(product.get("base_cost", product.get("price", 0) * 0.7), 2))
    cur_price = str(product.get("price", 0))
    rating = str(product.get("rating", 0))
    prompt = "اقترح سعرا مثاليا للبيع:\nالمنتج: " + name + "\nالتكلفة: $" + base_cost + "\nالسعر الحالي: $" + cur_price + "\nالتقييم: " + rating + "/5"
    if market_data:
        prompt = prompt + "\nبيانات السوق: " + market_data
    prompt = prompt + "\nاجب بـ: السعر المقترح، نسبة الربح، والتبرير في 2 جمل."
    return _call(prompt, temperature=0.4, max_tokens=200)

def continue_conversation(history, new_message, context=""):
    history_lines = []
    for h in history[-6:]:
        role = "زبون" if h["role"] == "user" else "مساعد"
        history_lines.append(role + ": " + h["content"])
    history_text = "\n".join(history_lines)
    parts = [STORE_SYSTEM]
    if context:
        parts.append("سياق: " + context)
    if history_text:
        parts.append("تاريخ المحادثة:\n" + history_text)
    parts.append("زبون: " + new_message)
    parts.append("مساعد:")
    return _call("\n\n".join(parts), temperature=0.6, max_tokens=400)

def summarize_conversation(history):
    lines = [h["role"] + ": " + h["content"] for h in history]
    return _call("لخص هذه المحادثة في جملة واحدة بالعربية:\n" + "\n".join(lines), temperature=0.3, max_tokens=100)
