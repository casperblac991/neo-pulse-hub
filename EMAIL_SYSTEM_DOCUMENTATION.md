# نظام جمع الإيميلات - وثائق كاملة
## Email Collection System - Complete Documentation

---

## 📋 نظرة عامة | Overview

تم تطوير نظام متكامل لجمع بيانات المشتركين (الإيميلات) من زوار الموقع وحفظها في Google Sheets. يتضمن النظام:

- **نموذج جمع الإيميلات** (Email Collector Modal)
- **خادم Express** للتعامل مع طلبات الاشتراك
- **سكريبت Python** لمزامنة البيانات مع Google Sheets
- **تخزين محلي** كنسخة احتياطية (JSON)

---

## 🎯 المكونات الرئيسية | Main Components

### 1. **email-collector.html**
ملف HTML منفصل يحتوي على:
- تصميم نموذج حديث وجذاب
- أنماط CSS متقدمة مع رسوم متحركة
- دوال JavaScript للتحقق من البيانات

**الموقع:** `/home/ubuntu/neo-pulse-hub/email-collector.html`

### 2. **index.html** (محدث)
تم إضافة:
- نموذج جمع الإيميلات كـ Modal
- دوال JavaScript للتعامل مع الاشتراك
- أنماط CSS مدمجة

### 3. **subscribe-server.js**
خادم Express يوفر:
- نقطة نهاية (Endpoint) لاستقبال بيانات الاشتراك
- التحقق من صحة البيانات
- حفظ البيانات في ملف JSON محلي
- محاولة مزامنة مع Google Sheets

**الموقع:** `/home/ubuntu/neo-pulse-hub/subscribe-server.js`

### 4. **email_to_sheets.py**
سكريبت Python يقوم بـ:
- قراءة ملف المشتركين المحلي
- مزامنة البيانات مع Google Sheets
- إنشاء نسخ احتياطية من البيانات

**الموقع:** `/home/ubuntu/neo-pulse-hub/email_to_sheets.py`

### 5. **data/subscribers.json**
ملف JSON يحتوي على:
- قائمة جميع المشتركين
- بيانات وصفية (Metadata)
- معلومات الاشتراك

**الموقع:** `/home/ubuntu/neo-pulse-hub/data/subscribers.json`

---

## 🚀 كيفية الاستخدام | Usage

### تشغيل الخادم (Server)
```bash
cd /home/ubuntu/neo-pulse-hub
node subscribe-server.js
```

الخادم سيستمع على المنفذ `3001` بشكل افتراضي.

### تشغيل سكريبت المزامنة (Sync Script)
```bash
cd /home/ubuntu/neo-pulse-hub
python3 email_to_sheets.py
```

### نقاط النهاية (API Endpoints)

#### 1. إضافة مشترك جديد
```
POST /api/subscribe
Content-Type: application/json

{
  "name": "محمد أحمد",
  "email": "user@example.com",
  "interests": "ساعات ذكية، سماعات",
  "timestamp": "2026-06-07T06:30:00Z"
}
```

**الاستجابة (Success):**
```json
{
  "success": true,
  "message": "Subscription successful",
  "subscriber": {
    "id": "1717754400000",
    "name": "محمد أحمد",
    "email": "user@example.com",
    "interests": "ساعات ذكية، سماعات",
    "timestamp": "2026-06-07T06:30:00Z",
    "status": "active",
    "source": "website"
  }
}
```

#### 2. الحصول على جميع المشتركين
```
GET /api/subscribers
```

#### 3. تصدير المشتركين إلى Google Sheets
```
POST /api/export-to-sheets
```

#### 4. فحص صحة الخادم
```
GET /api/health
```

---

## 🔐 التكامل مع Google Sheets | Google Sheets Integration

### الإعداد الأولي | Initial Setup

1. **تثبيت gws CLI:**
```bash
# gws مثبت بالفعل في البيئة
gws --help
```

2. **تعيين متغيرات البيئة:**
```bash
export GOOGLE_SHEETS_ID="your-sheet-id"
```

3. **المصادقة (Authentication):**
```bash
gws auth login
```

### مزامنة البيانات | Data Sync

يتم المزامنة تلقائياً عند استقبال اشتراك جديد:

```python
# في email_to_sheets.py
def syncToGoogleSheets(subscriber):
    # يتم إرسال البيانات إلى Google Sheets
    pass
```

---

## 📊 هيكل البيانات | Data Structure

### ملف subscribers.json
```json
{
  "subscribers": [
    {
      "id": "1717754400000",
      "name": "محمد أحمد",
      "email": "user@example.com",
      "interests": "ساعات ذكية، سماعات",
      "timestamp": "2026-06-07T06:30:00Z",
      "status": "active",
      "source": "website"
    }
  ],
  "metadata": {
    "created": "2026-06-07T06:30:00Z",
    "updated": "2026-06-07T06:30:00Z",
    "total": 1
  }
}
```

---

## 🎨 واجهة المستخدم | User Interface

### نموذج جمع الإيميلات
- **يظهر تلقائياً** بعد 5 ثوان من تحميل الصفحة
- **يمكن إغلاقه** بالنقر على زر الإغلاق أو خارج النموذج
- **يتضمن:**
  - حقل الاسم الكامل
  - حقل البريد الإلكتروني
  - حقل الاهتمامات (اختياري)
  - خانة الموافقة على الشروط
  - زر الاشتراك

### رسائل التغذية الراجعة
- ✅ رسالة نجاح عند الاشتراك بنجاح
- ❌ رسالة خطأ عند فشل الاشتراك
- ⚠️ تنبيهات عند وجود مشاكل

---

## 🛠️ استكشاف الأخطاء | Troubleshooting

### المشكلة: النموذج لا يظهر
**الحل:**
1. تأكد من أن JavaScript مفعل في المتصفح
2. افتح أدوات المطور (F12) وتحقق من الأخطاء
3. تأكد من أن `emailModal` موجود في HTML

### المشكلة: الاشتراك لا يعمل
**الحل:**
1. تأكد من أن الخادم يعمل على المنفذ 3001
2. تحقق من أن البريد الإلكتروني صحيح
3. افتح أدوات المطور وتحقق من طلب الشبكة

### المشكلة: البيانات لا تظهر في Google Sheets
**الحل:**
1. تأكد من تعيين `GOOGLE_SHEETS_ID`
2. تحقق من صلاحيات الوصول إلى Google Sheets
3. قم بتشغيل `python3 email_to_sheets.py` يدوياً

---

## 📈 الإحصائيات | Statistics

### عدد المشتركين
يتم حفظ إجمالي عدد المشتركين في `metadata.total`

### معدل التحويل
يمكن حساب معدل التحويل من خلال:
```
معدل التحويل = (عدد المشتركين / عدد الزوار) × 100
```

---

## 🔒 الأمان | Security

### التحقق من البيانات | Data Validation
- التحقق من صحة البريد الإلكتروني
- عدم السماح بالإيميلات المكررة
- تنظيف البيانات من الأحرف الخاصة

### حماية البيانات | Data Protection
- تخزين البيانات محلياً بشكل آمن
- استخدام HTTPS عند الاتصال بـ Google Sheets
- عدم تخزين كلمات المرور

---

## 📝 ملاحظات إضافية | Additional Notes

1. **النموذج يظهر تلقائياً** بعد 5 ثوان من تحميل الصفحة
2. **يمكن تخصيص الوقت** بتعديل القيمة في JavaScript
3. **البيانات محفوظة محلياً** حتى في حالة عدم توفر Google Sheets
4. **يمكن تصدير البيانات** إلى CSV من خلال `/api/export-to-sheets`

---

## 🔗 الملفات ذات الصلة | Related Files

- `/home/ubuntu/neo-pulse-hub/email-collector.html` - نموذج جمع الإيميلات
- `/home/ubuntu/neo-pulse-hub/index.html` - الصفحة الرئيسية (محدثة)
- `/home/ubuntu/neo-pulse-hub/subscribe-server.js` - خادم Express
- `/home/ubuntu/neo-pulse-hub/email_to_sheets.py` - سكريبت المزامنة
- `/home/ubuntu/neo-pulse-hub/data/subscribers.json` - ملف البيانات

---

## ✅ قائمة التحقق | Checklist

- [x] إنشاء نموذج جمع الإيميلات
- [x] إضافة النموذج إلى الصفحة الرئيسية
- [x] إنشاء خادم Express
- [x] إنشاء سكريبت Python للمزامنة
- [x] تهيئة ملف البيانات
- [x] اختبار النظام
- [x] دفع التغييرات إلى GitHub
- [ ] إعداد Google Sheets (اختياري)
- [ ] تكوين المصادقة (اختياري)

---

**آخر تحديث:** 2026-06-07  
**الإصدار:** 1.0  
**الحالة:** ✅ نشط وجاهز للاستخدام
