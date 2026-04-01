const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const app = express();

app.use(cors({ origin: '*' }));
app.use(express.json());

// 🔑 مفتاح Groq من المتغيرات البيئية
const GROQ_API_KEY = process.env.GROQ_API_KEY;

if (!GROQ_API_KEY) {
  console.log('❌ GROQ_API_KEY غير موجود');
}

// ============================================
// 1. الاتصال بـ Groq API (ذكاء اصطناعي)
// ============================================
async function getAIResponse(message) {
  if (!GROQ_API_KEY) return 'عذراً، مفتاح API غير متوفر.';
  
  try {
    const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${GROQ_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'llama-3.1-8b-instant',
        messages: [
          {
            role: 'system',
            content: `أنت مساعد ذكي لمتجر NEO PULSE HUB للمنتجات التقنية.
            
            المنتجات المتوفرة:
            - ساعات: Apple Watch Series 9 (399$), Samsung Galaxy Watch 6 (299$), Garmin Venu 3 (449$), Amazfit GTR 4 (149$)
            - سماعات: AirPods Pro 2 (249$), Sony WH-1000XM5 (349$), Galaxy Buds2 Pro (179$)
            - منزل ذكي: Echo Show 10 (249$), Nest Thermostat (129$), Philips Hue (179$)
            
            أجب بالعربية، مختصر، مفيد.`
          },
          { role: 'user', content: message }
        ],
        temperature: 0.7,
        max_tokens: 500
      })
    });
    
    const data = await response.json();
    return data.choices?.[0]?.message?.content || 'عذراً، حدث خطأ';
  } catch (error) {
    return 'عذراً، حدث خطأ في الاتصال.';
  }
}

// ============================================
// 2. حفظ المقال في المدونة
// ============================================
async function saveToBlog(content, title, type = 'report', language = 'ar') {
  const slug = title.toLowerCase().replace(/[^\w\s]/g, '').replace(/\s+/g, '-').substring(0, 50);
  const fileName = `${slug}.html`;
  const dir = path.join(__dirname, 'blog', language === 'ar' ? 'ar' : 'en');
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  const filePath = path.join(dir, fileName);
  const now = new Date();
  const date = now.toLocaleDateString('ar-EG');
  
  const fullHtml = `<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${title} | NEO PULSE HUB</title>
<meta name="description" content="تقرير شامل عن أفضل منتجات التقنية">
<meta name="keywords" content="تقرير, منتجات تقنية, مراجعات, NEO PULSE HUB">
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Cairo',sans-serif;background:#020510;color:#e2e8f0;line-height:1.7}
.container{max-width:900px;margin:0 auto;padding:2rem}
h1{color:#3b82f6;font-size:2rem;margin-bottom:1rem;border-right:4px solid #3b82f6;padding-right:1rem}
h2{color:#06b6d4;margin:1.5rem 0 1rem}
h3{color:#a855f7;margin:1rem 0}
p{margin-bottom:1rem;color:#cbd5e1}
a{color:#06b6d4;text-decoration:none}
.product-card{background:#0a0d1a;border:1px solid #3b82f6;border-radius:16px;padding:1.5rem;margin:1.5rem 0}
.product-price{font-size:1.5rem;color:#3b82f6;font-weight:bold}
.buy-btn{display:inline-block;background:linear-gradient(135deg,#ff9900,#e47911);color:white;padding:10px 20px;border-radius:50px;text-decoration:none;margin-top:1rem;font-weight:bold}
.buy-btn:hover{transform:translateY(-2px);box-shadow:0 4px 15px rgba(255,153,0,.4)}
.date{color:#6b6b8a;font-size:0.85rem;margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:1px solid #1e1e2e}
table{width:100%;border-collapse:collapse;margin:1.5rem 0;background:#0a0d1a;border-radius:12px;overflow:hidden}
th,td{padding:12px;border:1px solid #1e1e2e;text-align:right}
th{background:#3b82f6;color:white}
hr{border-color:#1e1e2e;margin:2rem 0}
.footer-links{text-align:center;margin-top:2rem;padding-top:1rem;border-top:1px solid #1e1e2e;color:#6b6b8a}
@media(max-width:768px){.container{padding:1rem}h1{font-size:1.5rem}}
</style>
</head>
<body>
<div class="container">
<div class="date">📅 ${date} | 📊 ${type === 'report' ? 'تقرير منتجات' : 'مقال'}</div>
${content}
<div class="footer-links">
<a href="/">🏠 الرئيسية</a> | 
<a href="/products.html">🛍️ المنتجات</a> | 
<a href="/blog/ar">📝 المدونة</a>
</div>
</div>
</body>
</html>`;
  
  fs.writeFileSync(filePath, fullHtml, 'utf8');
  console.log(`✅ تم النشر: ${filePath}`);
  return { success: true, url: `/blog/${language === 'ar' ? 'ar' : 'en'}/${fileName}`, filePath };
}

// ============================================
// 3. توليد تقرير منتجات
// ============================================
async function generateProductsReport(products) {
  const featured = products.filter(p => p.featured).slice(0, 8);
  const bestSeller = products.sort((a,b) => b.reviews - a.reviews)[0];
  const bestRating = products.sort((a,b) => b.rating - a.rating)[0];
  const bestDiscount = products.sort((a,b) => (b.discount||0) - (a.discount||0))[0];
  
  return `
  <h1>📊 تقرير منتجات NEO PULSE HUB</h1>
  <p>مرحباً بك في تقريرنا الأسبوعي لأفضل منتجات التقنية. نقدم لك مجموعة مختارة من أفضل الساعات الذكية، السماعات، ومنتجات المنزل الذكي مع مراجعات سريعة وأسعار محدثة.</p>
  
  <h2>🏆 أفضل المنتجات هذا الأسبوع</h2>
  <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:20px; margin:20px 0;">
    ${featured.slice(0, 4).map(p => `
    <div class="product-card">
      <h3>${p.name?.ar || p.name}</h3>
      <div class="product-price">${p.price}$</div>
      <p>⭐ ${p.rating}/5 (${(p.reviews || 0).toLocaleString()} مراجعة)</p>
      <p>${p.description?.ar?.substring(0, 100) || 'منتج تقني مميز'}</p>
      <a href="${(p.affiliate_amazon || '#').replace('YOUR_AMAZON_TAG', 'neopulsehub-20')}" target="_blank" class="buy-btn" rel="sponsored nofollow">🛒 شراء من أمازون</a>
    </div>
    `).join('')}
  </div>
  
  <h2>📊 جدول المقارنة السريع</h2>
  <table>
    <tr><th>المنتج</th><th>السعر</th><th>التقييم</th><th>المميزات</th></tr>
    ${featured.slice(0, 6).map(p => `
    <tr>
      <td><strong>${p.name?.ar || p.name}</strong></td>
      <td>${p.price}$</td>
      <td>${p.rating} ★</td>
      <td>${p.features?.ar?.substring(0, 60) || 'مميزات متعددة'}</td>
    </tr>
    `).join('')}
   </table>
  
  <h2>⭐ أفضل المنتجات حسب الفئة</h2>
  <ul style="list-style:none; padding:0">
    <li style="background:#0f1423; margin:8px 0; padding:12px; border-radius:8px">🔹 <strong>الأكثر مبيعاً:</strong> ${bestSeller?.name?.ar || bestSeller?.name} - ${bestSeller?.price}$ (${(bestSeller?.reviews || 0).toLocaleString()} مراجعة)</li>
    <li style="background:#0f1423; margin:8px 0; padding:12px; border-radius:8px">🔹 <strong>أعلى تقييم:</strong> ${bestRating?.name?.ar || bestRating?.name} - ${bestRating?.rating}/5</li>
    <li style="background:#0f1423; margin:8px 0; padding:12px; border-radius:8px">🔹 <strong>أفضل خصم:</strong> ${bestDiscount?.name?.ar || bestDiscount?.name} - خصم ${bestDiscount?.discount || 0}%</li>
  </ul>
  
  <h2>💡 نصائح للشراء</h2>
  <ul>
    <li>✅ تحقق من توافق المنتج مع أجهزتك</li>
    <li>✅ قارن الأسعار بين البائعين</li>
    <li>✅ اقرأ مراجعات المستخدمين</li>
    <li>✅ تأكد من سياسة الإرجاع</li>
  </ul>
  
  <hr>
  <p style="text-align:center; font-size:0.85rem; color:#6b6b8a;">⚠️ روابط أمازون هي روابط أفلييت - نحصل على عمولة صغيرة بدون تكلفة إضافية عليك.</p>
  `;
}

// ============================================
// 4. توليد مقال عادي
// ============================================
async function generateArticle(topic, language) {
  const prompt = `اكتب مقالة باللغة ${language === 'ar' ? 'العربية' : 'الإنجليزية'} بعنوان "${topic}" بطول 600 كلمة، مع مقدمة وخاتمة، بأسلوب احترافي مناسب لمدونة تقنية.`;
  const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${GROQ_API_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ model: 'llama-3.1-8b-instant', messages: [{ role: 'user', content: prompt }], temperature: 0.7, max_tokens: 1500 })
  });
  const data = await response.json();
  return data.choices?.[0]?.message?.content || '<p>عذراً، فشل توليد المقال</p>';
}

// ============================================
// 5. نقاط API
// ============================================

// شات بوت
app.post('/api/chat', async (req, res) => {
  const { message } = req.body;
  console.log(`📩: ${message}`);
  
  if (message.includes('تقرير') && (message.includes('انزل') || message.includes('نشر'))) {
    let products = [];
    const productsPath = path.join(__dirname, 'products.json');
    if (fs.existsSync(productsPath)) products = JSON.parse(fs.readFileSync(productsPath, 'utf8'));
    const content = await generateProductsReport(products);
    const now = new Date();
    const title = `تقرير منتجات NEO PULSE HUB - ${now.toLocaleDateString('ar-EG')}`;
    const result = await saveToBlog(content, title, 'report', 'ar');
    return res.json({ success: true, answer: `✅ تم نشر التقرير في المدونة!\n\n🔗 الرابط: ${result.url}` });
  }
  
  const answer = await getAIResponse(message);
  res.json({ success: true, answer });
});

// نشر تقرير
app.post('/api/post-report', async (req, res) => {
  try {
    let products = [];
    const productsPath = path.join(__dirname, 'products.json');
    if (fs.existsSync(productsPath)) products = JSON.parse(fs.readFileSync(productsPath, 'utf8'));
    const content = await generateProductsReport(products);
    const now = new Date();
    const title = `تقرير منتجات NEO PULSE HUB - ${now.toLocaleDateString('ar-EG')}`;
    const result = await saveToBlog(content, title, 'report', 'ar');
    res.json({ success: true, message: '✅ تم نشر التقرير', url: result.url });
  } catch (error) {
    res.json({ success: false, error: error.message });
  }
});

// نشر مقال
app.post('/api/post-article', async (req, res) => {
  try {
    const { topic, language = 'ar' } = req.body;
    const content = await generateArticle(topic, language);
    const title = topic;
    const result = await saveToBlog(content, title, 'article', language);
    res.json({ success: true, message: '✅ تم نشر المقال', url: result.url });
  } catch (error) {
    res.json({ success: false, error: error.message });
  }
});

// حالة الخادم
app.get('/api/status', (req, res) => {
  res.json({ success: true, status: 'running', time: new Date().toISOString() });
});

// ============================================
// 6. تشغيل الخادم
// ============================================
const PORT = process.env.PORT || 3000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Server running on port ${PORT}`);
  console.log(`📝 تقارير المدونة: ✅ جاهزة`);
  console.log(`🤖 Groq AI: ${GROQ_API_KEY ? '✅' : '❌'}`);
});
