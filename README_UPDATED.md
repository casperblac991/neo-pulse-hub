# 🌟 NEO PULSE HUB — منصة ذكية للتسويق الإلكتروني

## 📌 نظرة عامة

**NEO PULSE HUB** هي منصة تسويق إلكترونية ذكية تعمل بالذكاء الاصطناعي (Gemini) لجلب المنتجات من أمازون وتسويقها تلقائياً.

### الميزات الرئيسية

🤖 **ذكاء اصطناعي متقدم**
- توليد محتوى بالعربية والإنجليزية
- توصيات منتجات ذكية
- تحليل المشاعر والنوايا

📦 **جلب منتجات تلقائي**
- ربط مع أمازون أفلييت
- تحديث يومي للمنتجات
- أسعار وتقييمات حقيقية

📝 **محتوى ذكي**
- مقالات مراجعة يومية
- أدلة شراء شاملة
- محتوى محسّن للـ SEO

📢 **تسويق آلي**
- حملات على Telegram
- منشورات Instagram
- رسائل WhatsApp

💰 **تحسين الأرباح**
- روابط أفلييت في كل مقالة
- محتوى عالي الجودة لـ AdSense
- تحسين معدل التحويل

---

## 🚀 البدء السريع

### المتطلبات

```bash
# Python 3.8+
# pip

# تثبيت المكتبات
pip install -r requirements.txt
```

### التثبيت

```bash
# 1. استنساخ المستودع
git clone https://github.com/casperblac991/neo-pulse-hub.git
cd neo-pulse-hub

# 2. إعداد المتغيرات البيئية
cp .env.example .env
# ثم عدّل .env بمفاتيحك

# 3. تشغيل المجدول
python scheduler_integration.py
```

---

## 📚 الأنظمة الرئيسية

### 1. Amazon AI Fetcher
جلب منتجات من أمازون بذكاء اصطناعي

```bash
python amazon_ai_fetcher.py
```

### 2. Content Automation Bot
نشر مقالات مراجعة تلقائياً

```bash
python content_automation_bot.py
```

### 3. Social Media Automation
نشر حملات تسويقية على وسائل التواصل

```bash
python social_media_automation.py
```

### 4. Scheduler Integration
تنسيق جميع الأنظمة الآلية

```bash
python scheduler_integration.py
```

---

## 📖 الدليل الكامل

- 📘 [دليل الأتمتة الشامل](AUTOMATION_GUIDE.md)
- 📊 [ملخص التحديثات](IMPLEMENTATION_SUMMARY.md)
- 🔧 [دليل التثبيت](INSTALLATION.md)

---

## 🎯 جدول المهام

| المهمة | التكرار | الوقت |
|-------|--------|------|
| جلب منتجات | كل 6 ساعات | 00:00, 06:00, 12:00, 18:00 |
| نشر مقالة | يومياً | 10:00 |
| حملات تسويقية | 3 مرات يومياً | 08:00, 14:00, 20:00 |
| أدلة شراء | أسبوعياً | الاثنين 02:00 |
| تنظيف بيانات | يومياً | 03:00 |

---

## 💡 الاستخدام

### جلب منتجات من أمازون

```python
import amazon_ai_fetcher

# جلب منتجات من جميع الفئات
products = amazon_ai_fetcher.fetch_all_categories(2)
print(f"تم جلب {len(products)} منتج")
```

### نشر مقالة مراجعة

```python
import content_automation_bot

# نشر مقالة يومية
content_automation_bot.auto_publish_daily()
```

### نشر حملة تسويقية

```python
import social_media_automation

# نشر حملات على وسائل التواصل
results = social_media_automation.publish_daily_campaigns(3)
```

---

## 🔐 الأمان

### حماية API Keys

```bash
# استخدم متغيرات البيئة
export GEMINI_API_KEY=your_key_here
export GITHUB_TOKEN=your_token_here
```

### عدم الكشف عن البيانات

- لا تكتب المفاتيح في الكود
- استخدم .env للبيانات الحساسة
- لا تشارك المفاتيح علناً

---

## 📈 الأداء

### المؤشرات الرئيسية

```bash
# عدد المقالات
grep "✅ Saved" scheduler.log | wc -l

# عدد الحملات
grep "✅ Campaign" scheduler.log | wc -l

# عدد المنتجات
grep "✅ Added" scheduler.log | wc -l
```

### الأهداف الشهرية

- 30+ مقالة جديدة
- 90+ حملة تسويقية
- 60+ منتج جديد
- 10,000+ زيارة

---

## 🐛 استكشاف الأخطاء

### لا توجد منتجات

```bash
python amazon_ai_fetcher.py
```

### Gemini API غير متاح

```bash
export GEMINI_API_KEY=your_key_here
```

### Telegram لا يعمل

```bash
export CUSTOMER_BOT_TOKEN=your_token_here
```

---

## 📞 الدعم

- 📧 البريد: support@neo-pulse-hub.it.com
- 💬 Telegram: @neo_pulse_hub_bot
- 🌐 الموقع: https://neo-pulse-hub.it.com

---

## 📝 الترخيص

هذا المشروع مرخص تحت MIT License

---

## 🙏 شكر خاص

شكر لـ:
- Gemini AI لتوليد المحتوى
- Amazon للمنتجات والأفلييت
- Telegram للتسويق الآلي

---

**آخر تحديث**: 29 أبريل 2026
**الإصدار**: 2.0
**الحالة**: ✅ جاهز للإنتاج
