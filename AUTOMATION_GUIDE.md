# 🚀 دليل أتمتة منصة NEO PULSE HUB

## نظرة عامة

تم تحديث منصة NEO PULSE HUB بثلاث أنظمة أتمتة قوية:

1. **Amazon AI Fetcher** - جلب المنتجات من أمازون بذكاء اصطناعي
2. **Content Automation Bot** - نشر مقالات مراجعة تلقائياً على المدونة
3. **Social Media Automation** - نشر حملات تسويقية على وسائل التواصل

---

## 📋 المتطلبات

### المتغيرات البيئية المطلوبة

```bash
# API Keys
GEMINI_API_KEY=your_gemini_api_key_here
GITHUB_TOKEN=your_github_token_here

# Telegram (اختياري)
CUSTOMER_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHANNEL=@your_channel_name

# Amazon (اختياري)
AMAZON_AFFILIATE_TAG=neopulsehub-20
```

### تثبيت المكتبات

```bash
pip install -r requirements.txt
```

---

## 🔧 1. Amazon AI Fetcher

### الوصف
يقوم بجلب منتجات من أمازون بشكل آلي باستخدام الذكاء الاصطناعي (Gemini) لتحليل البيانات وتوليد أوصاف جذابة.

### الاستخدام

```bash
# جلب منتجات من جميع الفئات
python amazon_ai_fetcher.py

# النتيجة: ملف amazon_ai_products.json
```

### الفئات المدعومة

- `smartwatch` - ساعات ذكية
- `smart-glasses` - نظارات ذكية
- `earbuds` - سماعات ذكية
- `smart-home` - المنزل الذكي
- `health` - الصحة الذكية

### الميزات

✅ جلب بيانات منتجات حقيقية من أمازون
✅ توليد أوصاف تسويقية جذابة بالعربية والإنجليزية
✅ جلب صور عالية الجودة من Unsplash
✅ توليد روابط أفلييت تلقائياً
✅ حفظ البيانات في JSON للاستخدام الفوري

### مثال الإخراج

```json
{
  "id": "NPH-AI-1234567890-0",
  "name": {
    "ar": "ساعة أبل Watch Series 9",
    "en": "Apple Watch Series 9"
  },
  "price": 399,
  "original_price": 449,
  "discount": 11,
  "rating": 4.8,
  "reviews": 12430,
  "image": "https://images.unsplash.com/...",
  "affiliate_amazon": "https://www.amazon.com/s?k=...",
  "description": {
    "ar": "وصف تسويقي جذاب...",
    "en": "Attractive marketing description..."
  }
}
```

---

## 📝 2. Content Automation Bot

### الوصف
ينشر مقالات مراجعة تلقائياً على المدونة مع روابط أفلييت، مما يزيد من محتوى الموقع وتحسين SEO.

### الاستخدام

```bash
# نشر مراجعة يومية عشوائية
python content_automation_bot.py

# النتيجة: ملفات HTML في blog/ar/ و blog/en/
```

### الميزات

✅ توليد مراجعات منتجات شاملة بالعربية والإنجليزية
✅ نشر تلقائي على المدونة بصيغة HTML محسّنة
✅ دعم روابط أفلييت الأمازون
✅ تحسين SEO مع Meta Tags
✅ تصميم جذاب وسهل القراءة

### هيكل المقالة

1. **مقدمة جذابة** (2-3 جمل)
2. **المواصفات الرئيسية** (3-4 نقاط)
3. **المميزات والعيوب** (4-5 نقاط لكل)
4. **الأداء العملي** (2-3 فقرات)
5. **القيمة مقابل السعر** (فقرة واحدة)
6. **التوصيات النهائية** (فقرة واحدة)

### مثال الملف المُنشأ

```
blog/ar/ساعة-أبل-watch-series-9-review.html
blog/en/apple-watch-series-9-review.html
```

---

## 📢 3. Social Media Automation

### الوصف
ينشر حملات تسويقية تلقائياً على Telegram و Instagram و WhatsApp بمحتوى مُخصص لكل منصة.

### الاستخدام

```bash
# نشر حملات يومية
python social_media_automation.py

# النتيجة: حملات على Telegram و تسجيل في campaigns_log.json
```

### المنصات المدعومة

| المنصة | الحالة | الملاحظات |
|--------|--------|---------|
| **Telegram** | ✅ مفعّل | يتطلب TELEGRAM_BOT_TOKEN |
| **Instagram** | 📋 جاهز | يتطلب Instagram API |
| **WhatsApp** | 📋 جاهز | يتطلب WhatsApp Business API |

### محتوى كل منصة

#### Telegram
- منشور قصير وجذاب (حد أقصى 800 حرف)
- استخدام Emoji مناسب
- صورة المنتج
- عبارة تحفيزية للشراء

#### Instagram
- تعليق احترافي (حد أقصى 2000 حرف)
- Hashtags شهيرة (10-15)
- تنسيق جميل مع line breaks
- Call-to-action واضح

#### WhatsApp
- رسالة احترافية وودية
- معلومات مفيدة عن المنتج
- رابط الشراء
- لغة محفزة

### مثال الحملة

```json
{
  "product_id": "NPH-001",
  "product_name": "ساعة أبل Watch Series 9",
  "timestamp": "2026-04-29T17:30:00",
  "platforms": {
    "telegram": {
      "success": true,
      "content": "⌚ ساعة أبل الأفضل في فئتها..."
    },
    "instagram": {
      "success": true,
      "content": "✨ أفضل ساعة ذكية في 2026..."
    }
  }
}
```

---

## ⏰ جدولة المهام التلقائية

### إضافة إلى main.py

```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import amazon_ai_fetcher
import content_automation_bot
import social_media_automation

scheduler = BackgroundScheduler()

# جلب منتجات جديدة كل 6 ساعات
scheduler.add_job(
    lambda: amazon_ai_fetcher.fetch_all_categories(2),
    CronTrigger(hour="0,6,12,18", minute=0),
    id="fetch_products"
)

# نشر مقالة يومية في الساعة 10 صباحاً
scheduler.add_job(
    content_automation_bot.auto_publish_daily,
    CronTrigger(hour=10, minute=0),
    id="publish_article"
)

# نشر حملات تسويقية 3 مرات يومياً
scheduler.add_job(
    lambda: social_media_automation.publish_daily_campaigns(3),
    CronTrigger(hour="8,14,20", minute=0),
    id="publish_campaigns"
)

scheduler.start()
```

---

## 📊 تحسين أدسينس (AdSense)

### 1. تحسين SEO

```html
<!-- في رأس الصفحة -->
<meta name="description" content="وصف غني بالكلمات المفتاحية">
<meta name="keywords" content="ساعة ذكية, أفضل منتجات, مراجعة">
<link rel="canonical" href="https://neo-pulse-hub.it.com/...">
```

### 2. توزيع الإعلانات

```html
<!-- إعلان في رأس المقالة -->
<ins class="adsbygoogle" data-ad-slot="..."></ins>

<!-- إعلان في منتصف المحتوى -->
<ins class="adsbygoogle" data-ad-slot="..."></ins>

<!-- إعلان في نهاية المقالة -->
<ins class="adsbygoogle" data-ad-slot="..."></ins>
```

### 3. تحسين سرعة الموقع

- استخدام CDN للصور
- ضغط الملفات
- تقليل الطلبات الخارجية
- استخدام Lazy Loading

### 4. محتوى عالي الجودة

✅ مقالات طويلة (1500+ كلمة)
✅ صور عالية الجودة
✅ روابط داخلية
✅ محتوى أصلي وفريد

---

## 🔐 الأمان والخصوصية

### حماية API Keys

```bash
# في .env
GEMINI_API_KEY=sk-...
GITHUB_TOKEN=ghp_...
TELEGRAM_BOT_TOKEN=123456:ABC...
```

### عدم الكشف عن البيانات الحساسة

```python
# ❌ خطأ
api_key = "sk-12345"

# ✅ صحيح
api_key = os.environ.get("GEMINI_API_KEY", "")
```

---

## 📈 المراقبة والتقارير

### تسجيل الأنشطة

```python
import logging

logging.basicConfig(
    filename="automation.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
```

### تقارير يومية

```bash
# عرض ملخص الأنشطة
tail -n 50 automation.log
```

---

## 🐛 استكشاف الأخطاء

### المشكلة: لا توجد منتجات

```
❌ No products found
```

**الحل:**
```bash
# تأكد من وجود products.json
ls -la products.json

# إذا لم يكن موجوداً، قم بتشغيل:
python amazon_ai_fetcher.py
```

### المشكلة: Gemini API غير متاح

```
❌ GEMINI_API_KEY not found
```

**الحل:**
```bash
# تأكد من تعيين المتغير
export GEMINI_API_KEY=your_key_here

# أو في .env
GEMINI_API_KEY=your_key_here
```

### المشكلة: Telegram لا يعمل

```
❌ TELEGRAM_BOT_TOKEN not found
```

**الحل:**
```bash
# احصل على token من @BotFather
# ثم عيّنه:
export CUSTOMER_BOT_TOKEN=your_token_here
```

---

## 📞 الدعم والمساعدة

للمزيد من المساعدة:
- 📧 البريد الإلكتروني: support@neo-pulse-hub.it.com
- 💬 Telegram: @neo_pulse_hub_bot
- 🌐 الموقع: https://neo-pulse-hub.it.com

---

## 📝 ملاحظات مهمة

⚠️ **تحديث المنتجات**: تأكد من تشغيل `amazon_ai_fetcher.py` بانتظام لجلب منتجات جديدة

⚠️ **جودة المحتوى**: راجع المقالات المُنشأة تلقائياً قبل نشرها على الموقع الرسمي

⚠️ **الامتثال القانوني**: تأكد من الامتثال لسياسات أمازون والمنصات الأخرى

⚠️ **الحد من المعدل**: تجنب إرسال طلبات كثيرة جداً في وقت قصير

---

**آخر تحديث**: 29 أبريل 2026
**الإصدار**: 2.0
