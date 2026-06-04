# 🌐 NEO PULSE HUB - متجر منتجات الذكاء الاصطناعي

## 🚀 نبذة عن المشروع
متجر إلكتروني متخصص في بيع منتجات الذكاء الاصطناعي والتقنية الذكية. يدعم اللغتين العربية والإنجليزية، مع تصميم عصري وخلفية داكنة بتقنية Cyberpunk.

---

## 🤖 أنظمة الذكاء الاصطناعي (5 agents)

| النظام | الملف | الوظيفة |
|--------|-------|---------|
| 🧠 AI Store Manager | `ai_store_manager.py` | الدماغ المركزي للمتجر |
| 🔍 AI Product Sourcing | `ai_product_sourcing.py` | جلب المنتجات من أمازون |
| 🤖 AI Customer Service | `ai_customer_service.py` | بوت خدمة العملاء |
| 📢 AI Marketing | `ai_marketing.py` | التسويق التلقائي |
| 📊 AI Analytics | `ai_analytics.py` | لوحة تحكم التحليلات |

---

## 📁 الملفات الرئيسية

- `products.json` - قاعدة المنتجات (701 منتج)
- `leads.json` - بيانات العملاء
- `store.html` - واجهة المتجر الحديثة
- `store_hub.py` - مركز التكامل
- `test_store.py` - اختبار الأنظمة

---

## 🚀 التشغيل

```bash
# تثبيت المكتبات
pip install -r requirements.txt

# تشغيل الأنظمة
python3 ai_store_manager.py     # مدير المتجر
python3 ai_marketing.py          # التسويق
python3 ai_analytics.py          # التحليلات
python3 store_hub.py              # Flask API
```

---

## 📱 أوامر بوت تيليجرام

- `/start` - بدء المحادثة
- `/products` - عرض المنتجات
- `/search <اسم>` - البحث
- `/deals` - العروض
- `/stats` - الإحصائيات

---

## 🧪 الاختبار

```bash
python3 test_store.py
# ✅ ALL TESTS PASSED!
```

---

## 🌐 API Endpoints

- `GET /api/products` - المنتجات
- `GET /api/search?q=` - البحث
- `GET /api/recommendations` - التوصيات
- `GET /api/trending` - الرائجة
- `GET /api/stats` - الإحصائيات
- `GET /api/ai/report` - تقرير AI

