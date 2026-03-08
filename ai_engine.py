#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════╗
║   NEO PULSE HUB — AI Engine (Gemini)                           ║
║   محرك الذكاء الاصطناعي المشترك لجميع البوتات                  ║
╚══════════════════════════════════════════════════════════════════╝

يُستخدم من جميع البوتات لـ:
  - الإجابة على أسئلة الزبائن
  - توليد توصيات المنتجات
  - إنشاء أوصاف المنتجات
  - تحليل المشاعر
  - توليد تقارير
"""

import os, re, json, time, logging, requests
from typing import Optional

log = logging.getLogger("ai_engine")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL   = "gemini-2.0-flash"
GEMINI_URL     = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

# ══════════════════════════════════════════════════════════════════
# CORE CALL
# ══════════════════════════════════════════════════════════════════

def _call(prompt: str, temperature: float = 0.6,
          max_tokens: int = 1500, system: str = None) -> str:
    """الاستدعاء الأساسي لـ Gemini."""
    if not GEMINI_API_KEY:
        return "⚠️ مفتاح Gemini غير موجود"

    contents = []
    if system:
        contents.append({"role": "user",   "parts": [{"text": system}]})
        contents.append({"role": "model",  "parts": [{"text": "مفهوم، سأتبع هذه التعليمات."}]})
    contents.append({"role": "user", "parts": [{"text": prompt}]})

    for attempt in range(3):
        try:
            r = requests.post(
                f"{GEMINI_URL}?key={GEMINI_API_KEY}",
                json={
                    "contents": contents,
                    "generationConfig": {
                        "temperature":    temperature,
                        "maxOutputTokens":max_tokens,
                        "topP":           0.9,
                    },
                    "safetySettings": [
                        {"category": "HARM_CATEGORY_HARASSMENT",         "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH",        "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",  "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT",  "threshold": "BLOCK_NONE"},
                    ]
                },
                headers={"Content-Type": "application/json"},
                timeout=30,
            )
            if r.status_code == 200:
                return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            elif r.status_code == 429:
                wait = 2 ** attempt
                log.warning(f"Rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue
            else:
                log.error(f"Gemini {r.status_code}: {r.text[:200]}")
                return f"عذراً، حدث خطأ في الذكاء الاصطناعي (كود {r.status_code})"
        except requests.exceptions.Timeout:
            log.error("Gemini timeout")
            return "عذراً، انتهت مهلة الاتصال. جرب مرة أخرى."
        except Exception as e:
            log.error(f"Gemini error: {e}")
            return "عذراً، حدث خطأ غير متوقع."
    return "عذراً، الخادم مشغول حالياً. جرب بعد دقيقة."

def _call_json(prompt: str, temperature: float = 0.3) -> Optional[dict]:
    """يطلب JSON فقط ويُحلله."""
    result = _call(prompt + "\n\nأرجع JSON فقط بدون أي نص إضافي أو backticks.", temperature)
    try:
        clean = re.sub(r'```json|```', '', result).strip()
        match = re.search(r'[\[\{][\s\S]*[\]\}]', clean)
        if match:
            return json.loads(match.group())
    except Exception as e:
        log.error(f"JSON parse error: {e}\nRaw: {result[:200]}")
    return None

# ══════════════════════════════════════════════════════════════════
# CUSTOMER SERVICE AI
# ══════════════════════════════════════════════════════════════════

STORE_SYSTEM = """أنت مساعد خدمة عملاء ذكي لمتجر NEO PULSE HUB.
المتجر متخصص في منتجات الذكاء الاصطناعي والتقنية الذكية.
تحدث بالعربية دائماً. كن ودوداً، محترفاً، ومختصراً.
لا تخترع معلومات — إذا لم تعرف أجب بصدق."""

def answer_customer(question: str, products_context: str = "",
                    faqs_context: str = "", user_history: str = "") -> str:
    """يجيب على سؤال الزبون."""
    prompt = f"""
{STORE_SYSTEM}

{f"سياق المنتجات:\n{products_context}" if products_context else ""}
{f"الأسئلة الشائعة:\n{faqs_context}" if faqs_context else ""}
{f"تاريخ المحادثة:\n{user_history}" if user_history else ""}

سؤال الزبون: {question}

أجب بشكل مختصر ومفيد (3-5 جمل كحد أقصى).
"""
    return _call(prompt, temperature=0.5, max_tokens=500)

def analyze_sentiment(text: str) -> str:
    """يحلل مشاعر الرسالة: positive/negative/neutral/urgent."""
    result = _call(
        f'حلل مشاعر هذا النص وأجب بكلمة واحدة فقط (positive/negative/neutral/urgent): "{text}"',
        temperature=0.1, max_tokens=10
    )
    for s in ["positive","negative","neutral","urgent"]:
        if s in result.lower():
            return s
    return "neutral"

def is_purchase_intent(text: str) -> bool:
    """هل النص يعبر عن نية شراء؟"""
    result = _call(
        f'هل يعبر هذا النص عن نية شراء؟ أجب بـ yes أو no فقط: "{text}"',
        temperature=0.1, max_tokens=5
    )
    return "yes" in result.lower()

# ══════════════════════════════════════════════════════════════════
# PRODUCT RECOMMENDATION AI
# ══════════════════════════════════════════════════════════════════

def recommend_products(user_query: str, products: list,
                       budget: float = None, preferences: list = None) -> list:
    """يوصي بمنتجات مناسبة للزبون — يُرجع قائمة IDs."""
    products_summary = "\n".join([
        f"ID:{p['id']} | {p.get('name_ar','')} | ${p['price']} | {p.get('category','')} | تقييم:{p.get('rating',0)}"
        for p in products[:20]
    ])

    prompt = f"""أنت محرك توصيات لمتجر تقنية ذكية.

المنتجات المتاحة:
{products_summary}

طلب الزبون: "{user_query}"
{f"الميزانية: ${budget}" if budget else ""}
{f"التفضيلات: {', '.join(preferences)}" if preferences else ""}

أرجع JSON بهذا الشكل:
{{
  "recommendations": ["ID1", "ID2", "ID3"],
  "reason": "سبب التوصية بجملة واحدة",
  "alternative": "ID إذا لم تناسب الأولى"
}}"""

    result = _call_json(prompt)
    if result and "recommendations" in result:
        return result.get("recommendations", [])
    return [p["id"] for p in sorted(products, key=lambda x: x.get("rating",0), reverse=True)[:3]]

def extract_budget(text: str) -> Optional[float]:
    """يستخرج الميزانية من النص العربي."""
    result = _call(
        f'استخرج الميزانية بالدولار من هذا النص وأرجع رقماً فقط (مثال: 150.00)، إذا لم توجد أرجع null: "{text}"',
        temperature=0.1, max_tokens=20
    )
    try:
        clean = re.sub(r'[^\d.]', '', result.strip())
        val = float(clean)
        return val if 1 < val < 100000 else None
    except:
        return None

def categorize_query(text: str) -> str:
    """يصنف استفسار الزبون."""
    result = _call(
        f'صنف هذا الاستفسار بكلمة واحدة (شكوى/استفسار_منتج/دعم_تقني/شحن_دفع/توصية/أخرى): "{text}"',
        temperature=0.1, max_tokens=20
    )
    cats = ["شكوى","استفسار_منتج","دعم_تقني","شحن_دفع","توصية","أخرى"]
    for c in cats:
        if c in result: return c
    return "أخرى"

# ══════════════════════════════════════════════════════════════════
# PRODUCT CONTENT AI
# ══════════════════════════════════════════════════════════════════

def generate_product_description(product_data: dict) -> str:
    """يولد وصف تسويقي عربي للمنتج."""
    return _call(f"""اكتب وصفاً تسويقياً جذاباً بالعربية لهذا المنتج (جملتان):
الاسم: {product_data.get('name_ar','')}.
المزايا: {', '.join(product_data.get('features_ar',[])[:4])}.
أسلوب: مقنع، يركز على الفائدة للمستخدم.""",
        temperature=0.7, max_tokens=200)

def search_product_by_description(query: str) -> Optional[dict]:
    """يبحث عن منتج بالوصف ويُرجع بياناته الكاملة."""
    prompt = f"""أنت خبير منتجات تقنية. ابحث في معرفتك عن أفضل منتج حقيقي لهذا الوصف:
"{query}"

أرجع JSON:
{{
  "found": true,
  "name_en": "الاسم بالإنجليزية",
  "name_ar": "الاسم بالعربية",
  "brand": "الماركة",
  "category": "smartwatch|smart-glasses|health|smart-home|earbuds|productivity",
  "category_ar": "الفئة العربية",
  "estimated_price_usd": 99.99,
  "original_retail_usd": 129.99,
  "rating": 4.5,
  "reviews_count": 1250,
  "stock": 30,
  "shipping_days": "7-14",
  "features_ar": ["ميزة1","ميزة2","ميزة3","ميزة4","ميزة5"],
  "description_ar": "وصف تسويقي جذاب",
  "tags": ["tag1","tag2"],
  "image_search_query": "product name for image search",
  "why_recommended": "لماذا هذا المنتج مناسب"
}}"""
    return _call_json(prompt)

def generate_mini_report(product: dict) -> str:
    """يولد تقرير مصغر ذكي عن منتج."""
    return _call(f"""اكتب تقريراً مصغراً بالعربية في 5 نقاط عن:
{product.get('name_ar','')} — ${product.get('price',0)}
التقييم: {product.get('rating',0)}/5
المزايا: {', '.join(product.get('features_ar',[])[:4])}

النقاط: 1-نقاط القوة 2-للمن مناسب 3-قيمة السعر 4-ضعف محتمل 5-التوصية""",
        temperature=0.5, max_tokens=500)

def generate_marketing_post(product: dict, platform: str = "telegram") -> str:
    """يولد منشور تسويقي للمنتج."""
    chars = {"telegram": 500, "instagram": 300, "whatsapp": 400}
    return _call(f"""اكتب منشوراً تسويقياً لـ {platform} بالعربية:
المنتج: {product.get('name_ar','')}
السعر: ${product.get('price',0)} (خصم {product.get('discount',0)}%)
أبرز مزية: {product.get('features_ar',[''])[0] if product.get('features_ar') else ''}
الحد: {chars.get(platform, 400)} حرف. استخدم emoji مناسبة.""",
        temperature=0.8, max_tokens=400)

# ══════════════════════════════════════════════════════════════════
# ADMIN / ANALYTICS AI
# ══════════════════════════════════════════════════════════════════

def generate_store_report(analytics: dict) -> str:
    """يولد تقرير ذكي عن أداء المتجر."""
    return _call(f"""أنت مستشار تجارة إلكترونية. حلل هذه الإحصائيات وأعط توصيات:

المستخدمون: {analytics.get('total_users',0)}
الطلبات: {analytics.get('total_orders',0)}
الإيرادات: ${analytics.get('total_revenue',0)}
المنتجات: {analytics.get('total_products',0)}
الطلبات المعلقة: {analytics.get('pending_orders',0)}
مخزون منخفض: {analytics.get('low_stock_count',0)} منتج

اكتب تقريراً بالعربية في 4 فقرات: الأداء الحالي، نقاط القوة، نقاط الضعف، التوصيات.""",
        temperature=0.5, max_tokens=600)

def suggest_price(product: dict, market_data: str = "") -> str:
    """يقترح سعراً مثالياً للمنتج."""
    return _call(f"""اقترح سعراً مثالياً للبيع في متجر عربي:
المنتج: {product.get('name_ar','')}
التكلفة: ${product.get('base_cost', product.get('price',0)*0.7):.2f}
السعر الحالي: ${product.get('price',0)}
التقييم: {product.get('rating',0)}/5
{f'بيانات السوق: {market_data}' if market_data else ''}

أجب بـ: السعر المقترح، نسبة الربح، والتبرير في 2 جمل.""",
        temperature=0.4, max_tokens=200)

# ══════════════════════════════════════════════════════════════════
# CONVERSATION MEMORY (for multi-turn chat)
# ══════════════════════════════════════════════════════════════════

def continue_conversation(history: list, new_message: str,
                          context: str = "") -> str:
    """يكمل محادثة متعددة الأدوار مع الزبون."""
    history_text = "\n".join([
        f"{'زبون' if h['role']=='user' else 'مساعد'}: {h['content']}"
        for h in history[-6:]  # last 6 exchanges
    ])
    prompt = f"""{STORE_SYSTEM}
{f'سياق: {context}' if context else ''}

تاريخ المحادثة:
{history_text}

زبون: {new_message}
مساعد:"""
    return _call(prompt, temperature=0.6, max_tokens=400)

def summarize_conversation(history: list) -> str:
    """يلخص المحادثة لحفظها."""
    text = "\n".join([f"{h['role']}: {h['content']}" for h in history])
    return _call(
        f"لخص هذه المحادثة في جملة واحدة بالعربية:\n{text}",
        temperature=0.3, max_tokens=100
    )
