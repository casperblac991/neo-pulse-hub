# نشر NEO PULSE HUB كتطبيق React + Node.js

## الاختيار الموصى به

استخدم **Render Web Service** كبداية: يتصل مباشرة بمستودع GitHub، يبني التطبيق عند كل push، يدعم متغيرات البيئة والنطاق المخصص وHealth Check. Railway بديل ممتاز إذا احتجت توسعًا أسرع أو عدة خدمات منفصلة.

> GitHub Pages يبقى مناسبًا للنسخة الثابتة فقط، لكنه لا يشغّل Express أو قاعدة البيانات أو خادم AI بصورة دائمة.

## ما تم تجهيزه في المستودع

- `render.yaml`: إعداد Web Service جاهز.
- `server/_core/index.ts`: نقطة صحة `GET /healthz`.
- `package.json`: أوامر البناء والتشغيل:

```text
Build: npm exec --yes pnpm@10.15.1 -- install --frozen-lockfile && npm exec --yes pnpm@10.15.1 -- run build
Start: node dist/index.js
Health: /healthz
```

## خطوات النشر على Render

1. افتح Render وأنشئ **New → Blueprint** أو **New → Web Service**.
2. اربط حساب GitHub واختر `casperblac991/neo-pulse-hub` والفرع `main`.
3. إذا استخدمت Blueprint، اختر ملف `render.yaml` الموجود في جذر المشروع.
4. إذا أنشأت الخدمة يدويًا، استخدم:
   - **Runtime:** Node
   - **Build Command:** الأمر الموجود في `render.yaml`
   - **Start Command:** `node dist/index.js`
   - **Health Check Path:** `/healthz`
5. أضف الأسرار من لوحة Render، ولا تضع قيمها في GitHub:

```text
DATABASE_URL
OPENAI_API_KEY
GROQ_API_KEY
GEMINI_API_KEY
API_SECRET
ADMIN_API_KEY
```

6. اضبط:

```text
NODE_ENV=production
SITE_URL=https://neo-pulse-hub.it.com
```

7. شغّل Deploy وانتظر نجاح البناء.
8. اختبر قبل تغيير DNS:

```bash
curl -i https://YOUR-SERVICE.onrender.com/healthz
curl -i https://YOUR-SERVICE.onrender.com/
```

يجب أن تعيد `/healthz` حالة JSON فيها `status: "ok"`.

## ربط النطاق الحالي

لا تغيّر DNS قبل التأكد من أن خدمة Render تعمل على نطاقها المؤقت.

1. من Render افتح الخدمة ثم **Settings → Custom Domains**.
2. أضف `neo-pulse-hub.it.com`.
3. سيعرض Render سجل DNS المطلوب؛ استخدم القيم التي يعرضها Render حرفيًا.
4. في مزود DNS:
   - احذف سجل GitHub Pages القديم المتعارض للنطاق نفسه.
   - أضف سجل CNAME أو السجل المطلوب من Render.
   - اترك سجلات البريد MX كما هي.
5. انتظر انتشار DNS وشهادة TLS.
6. تحقق:

```bash
curl -i https://neo-pulse-hub.it.com/healthz
```

لا حاجة لإزالة GitHub Pages من المستودع فورًا؛ يمكن إبقاؤه كخطة رجوع حتى نجاح الخدمة الديناميكية.

## قاعدة البيانات

إذا كان `DATABASE_URL` يشير إلى MySQL خارجي، اسمح باتصالات Render من خلال مزود قاعدة البيانات واستخدم SSL إذا كان المزود يطلبه. لا تعتمد على ملف محلي داخل الحاوية لتخزين البيانات؛ التخزين المحلي قد يضيع عند إعادة النشر.

قبل الإنتاج:

- أنشئ قاعدة إنتاج منفصلة عن التطوير.
- خذ نسخة احتياطية.
- شغّل migrations من بيئة موثوقة.
- اختبر تسجيل الدخول ومسارات tRPC والكتالوج.

## خادم AI

خادم Node لا يحتاج إلى كشف مفاتيح AI للمتصفح. ضع المفاتيح في متغيرات Render فقط. يجب أن تمر طلبات Copilot عبر `/api/trpc/ai.chat`، مع بقاء الإجراء محميًا بتسجيل الدخول. لا تضع `OPENAI_API_KEY` أو `GROQ_API_KEY` أو `GEMINI_API_KEY` في ملفات `client/`.

## بعد نجاح النشر

1. اجعل Render هو أصل النطاق الرسمي.
2. حدّث `SITE_URL` وOAuth callbacks وCORS إن وجدت.
3. اختبر:
   - الصفحة الرئيسية.
   - صفحة المنتجات.
   - تسجيل الدخول.
   - Neo Copilot.
   - تحميل الصور والتخزين.
   - `/healthz`.
4. راقب السجلات والتنبيهات.
5. احتفظ بـ GitHub Pages كنسخة رجوع حتى يستقر التطبيق.

## Railway كبديل

في Railway اختر **Deploy from GitHub repo** ثم نفس أوامر Build/Start، أضف المتغيرات من تبويب Variables، ولّد Domain من Settings → Networking، ثم اربط النطاق من DNS. ميزة Railway المهمة هي سهولة فصل التطبيق وقاعدة البيانات والعمال Workers إلى خدمات مستقلة لاحقًا.
