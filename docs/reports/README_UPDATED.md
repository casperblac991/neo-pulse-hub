# 🚀 NEO PULSE HUB - متجر ذكي متقدم
## NEO PULSE HUB - Advanced Smart Store

![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Version](https://img.shields.io/badge/Version-2.0-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📝 نظرة عامة | Overview

**NEO PULSE HUB** هو متجر إلكتروني ذكي متقدم يجمع بين:
- 🤖 **الذكاء الاصطناعي** للتوصيات الذكية
- 💰 **روابط Affiliate** لـ Amazon و AliExpress
- 📧 **نظام جمع الإيميلات** مع Google Sheets
- 🔄 **أتمتة المحتوى** بتقارير يومية
- 🎯 **صفحات ذكية** للمقارنة والعروض

---

## ✨ الميزات الرئيسية | Key Features

### 1. 🎁 **مكتشف الهدايا الذكي**
```
الملف: gift-finder.html
الميزات:
- تصفية حسب الفئة والميزانية
- توصيات ذكية بناءً على الاهتمامات
- روابط Amazon مباشرة
- واجهة سهلة الاستخدام
```

### 2. ⏰ **عروض الساعة المحدودة**
```
الملف: deals-of-the-hour.html
الميزات:
- عروض محدودة الوقت
- عداد تنازلي حي
- تنبيهات الأسعار
- تحديث تلقائي
```

### 3. ⚔️ **معركة المنتجات**
```
الملف: product-battle.html
الميزات:
- مقارنة تفاعلية بين المنتجات
- نظام التصويت الحي
- رسوم بيانية للنتائج
- تحديث فوري
```

### 4. 📧 **نظام جمع الإيميلات**
```
الملفات: email-collector.html, subscribe-server.js
الميزات:
- نموذج جذاب يظهر تلقائياً
- التحقق من البيانات
- حفظ آمن في Google Sheets
- نسخة احتياطية محلية
```

### 5. 🤖 **روبوت المدونة الذكي**
```
الملف: content_automation_bot_v3.py
الميزات:
- توليد تقارير يومية
- دعم اللغة العربية والإنجليزية
- تحليل المنتجات
- نشر تلقائي
```

---

## 🛠️ التثبيت والإعداد | Installation & Setup

### المتطلبات | Requirements
```bash
- Node.js 22.13.0+
- Python 3.11+
- Git
- npm/pnpm
```

### التثبيت | Installation
```bash
# استنساخ المستودع
git clone https://github.com/casperblac991/neo-pulse-hub.git
cd neo-pulse-hub

# تثبيت المكتبات
npm install
pip install -r requirements.txt

# تشغيل الخادم
node subscribe-server.js

# تشغيل روبوت المدونة
python3 content_automation_bot_v3.py
```

---

## 📁 هيكل المشروع | Project Structure

```
neo-pulse-hub/
├── index.html                      # الصفحة الرئيسية
├── gift-finder.html               # مكتشف الهدايا
├── deals-of-the-hour.html         # عروض الساعة
├── product-battle.html            # معركة المنتجات
├── email-collector.html           # نموذج الإيميلات
├── subscribe-server.js            # خادم Express
├── email_to_sheets.py             # سكريبت المزامنة
├── content_automation_bot_v3.py   # روبوت المدونة
├── data/
│   └── subscribers.json           # قاعدة البيانات
├── EMAIL_SYSTEM_DOCUMENTATION.md  # وثائق الإيميلات
└── README.md                      # هذا الملف
```

---

## 🚀 كيفية الاستخدام | Usage

### تشغيل الخادم
```bash
cd /home/ubuntu/neo-pulse-hub
node subscribe-server.js
```

### تشغيل روبوت المدونة
```bash
python3 content_automation_bot_v3.py
```

### مزامنة الإيميلات مع Google Sheets
```bash
python3 email_to_sheets.py
```

---

## 🔗 نقاط النهاية | API Endpoints

### إضافة مشترك جديد
```
POST /api/subscribe
Content-Type: application/json

{
  "name": "محمد أحمد",
  "email": "user@example.com",
  "interests": "ساعات ذكية، سماعات"
}
```

### الحصول على المشتركين
```
GET /api/subscribers
```

### فحص صحة الخادم
```
GET /api/health
```

---

## 🎨 التصميم | Design

### الألوان | Colors
```
- الأساسي: #00d4ff (أزرق سماوي)
- الثانوي: #7c3aed (بنفسجي)
- التركيز: #ff00c8 (وردي)
- الخلفية: #0a0a0a (أسود)
```

### الخطوط | Fonts
```
- الخط الرئيسي: Segoe UI, Arial
- حجم العنوان: 2.5rem
- حجم النص: 1rem
```

---

## 📊 الإحصائيات | Statistics

| المقياس | القيمة |
|--------|--------|
| عدد الصفحات | 8+ |
| عدد المنتجات | 50+ |
| المشتركين | 1+ |
| معدل التحويل | قيد التحسين |
| سرعة التحميل | ⚡ سريع |

---

## 🔐 الأمان | Security

- ✅ التحقق من صحة البيانات
- ✅ عدم السماح بالإيميلات المكررة
- ✅ تنظيف البيانات من الأحرف الخاصة
- ✅ استخدام HTTPS
- ✅ حماية من هجمات XSS

---

## 🐛 استكشاف الأخطاء | Troubleshooting

### المشكلة: النموذج لا يظهر
**الحل:** تأكد من تفعيل JavaScript وأن `emailModal` موجود

### المشكلة: الاشتراك لا يعمل
**الحل:** تأكد من تشغيل الخادم على المنفذ 3001

### المشكلة: البيانات لا تظهر في Google Sheets
**الحل:** تأكد من تعيين `GOOGLE_SHEETS_ID`

---

## 🤝 المساهمة | Contributing

نرحب بالمساهمات! يرجى:
1. Fork المستودع
2. إنشاء فرع جديد (`git checkout -b feature/AmazingFeature`)
3. Commit التغييرات (`git commit -m 'Add some AmazingFeature'`)
4. Push إلى الفرع (`git push origin feature/AmazingFeature`)
5. فتح Pull Request

---

## 📄 الترخيص | License

هذا المشروع مرخص تحت رخصة MIT. انظر ملف `LICENSE` للمزيد.

---

## 📞 التواصل | Contact

- **البريد الإلكتروني:** support@neopulsehub.com
- **الموقع:** https://casperblac991.github.io/neo-pulse-hub/
- **GitHub:** https://github.com/casperblac991/neo-pulse-hub
- **Twitter:** @neopulsehub

---

## 🙏 شكر وتقدير | Acknowledgments

شكر خاص لـ:
- OpenAI و Groq لتوفير خدمات الذكاء الاصطناعي
- Amazon و AliExpress للبرامج الإحالية
- Google Sheets للتخزين السحابي
- GitHub Pages للاستضافة المجانية

---

## 📚 المراجع | References

- [Email System Documentation](EMAIL_SYSTEM_DOCUMENTATION.md)
- [OpenAI API](https://openai.com/api/)
- [Express.js](https://expressjs.com/)
- [Google Sheets API](https://developers.google.com/sheets/api)

---

## 🎯 الخطط المستقبلية | Future Plans

- [ ] إضافة نظام الدفع
- [ ] تحسين SEO
- [ ] إضافة تطبيق موبايل
- [ ] توسيع إلى أسواق جديدة
- [ ] إضافة ميزات AI متقدمة

---

**آخر تحديث:** 2026-06-07  
**الإصدار:** 2.0  
**الحالة:** ✅ نشط وجاهز للاستخدام

---

## ⭐ إذا أعجبك المشروع، لا تنسَ إضافة نجمة! ⭐
