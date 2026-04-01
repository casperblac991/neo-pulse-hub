const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const app = express();

app.use(cors({ origin: '*' }));
app.use(express.json());

const GROQ_API_KEY = process.env.GROQ_API_KEY;

// ============================================
// حفظ في المدونة
// ============================================
async function saveToBlog(content, title) {
  const slug = title.toLowerCase().replace(/[^\w\s]/g, '').replace(/\s+/g, '-').substring(0, 50);
  const fileName = `${slug}.html`;
  const dir = path.join(__dirname, 'blog', 'ar');
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
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Cairo',sans-serif;background:#020510;color:#e2e8f0;line-height:1.7}
.container{max-width:900px;margin:0 auto;padding:2rem}
h1{color:#3b82f6;border-right:4px solid #3b82f6;padding-right:1rem;margin-bottom:1rem}
h2{color:#06b6d4;margin:1.5rem 0 1rem}
.product-card{background:#0a0d1a;border:1px solid #3b82f6;border-radius:16px;padding:1.5rem;margin:1rem 0}
.product-price{font-size:1.5rem;color:#3b82f6;font-weight:bold}
.buy-btn{display:inline-block;background:linear-gradient(135deg,#ff9900,#e47911);color:white;padding:10px 20px;border-radius:50px;text-decoration:none;margin-top:1rem}
.date{color:#6b6b8a;margin-bottom:1rem;padding-bottom:1rem;border-bottom:1px solid #1e1e2e}
table{width:100%;border-collapse:collapse;margin:1rem 0}
th,td{padding:10px;border:1px solid #1e1e2e;text-align:right}
th{background:#3b82f6}
</style>
</head>
<body>
<div class="container">
<div class="date">📅 ${date}</div>
${content}
<div style="text-align:center; margin-top:2rem; padding-top:1rem; border-top:1px solid #1e1e2e">
<a href="/">🏠 الرئيسية</a> | <a href="/products.html">🛍️ المنتجات</a> | <a href="/blog/ar">📝 المدونة</a>
</div>
</div>
</body>
</html>`;
  
  fs.writeFileSync(filePath, fullHtml, 'utf8');
  console.log(`✅ تم النشر: ${filePath}`);
  return { success: true, url: `/blog/ar/${fileName}` };
}

// ============================================
// توليد تقرير المنتجات
// ============================================
async function generateReport(products) {
  const featured = products.filter(p => p.featured).slice(0, 6);
  const bestSeller = products.sort((a,b) => b.reviews - a.reviews)[0];
  const bestRating = products.sort((a,b) => b.rating - a.rating)[0];
  const bestDiscount = products.sort((a,b) => (b.discount||0) - (a.discount||0))[0];
  
  return `
  <h1>📊 تقرير منتجات NEO PULSE HUB</h1>
  <p>تقريرنا الأسبوعي لأفضل منتجات التقنية مع الأسعار والتقييمات.</p>
  
  <h2>🏆 أفضل المنتجات هذا الأسبوع</h2>
  <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:20px;">
    ${featured.map(p => `
    <div class="product-card">
      <h3>${p.name?.ar || p.name}</h3>
      <div class="product-price">${p.price}$</div>
      <p>⭐ ${p.rating}/5 (${(p.reviews || 0).toLocaleString()} مراجعة)</p>
      <a href="${(p.affiliate_amazon || '#').replace('YOUR_AMAZON_TAG', 'neopulsehub-20')}" target="_blank" class="buy-btn" rel="sponsored">🛒 شراء من أمازون</a>
    </div>
    `).join('')}
  </div>
  
  <h2>⭐ أفضل المنتجات حسب الفئة</h2>
  <ul>
    <li>🔹 <strong>الأكثر مبيعاً:</strong> ${bestSeller?.name?.ar || bestSeller?.name} - ${bestSeller?.price}$</li>
    <li>🔹 <strong>أعلى تقييم:</strong> ${bestRating?.name?.ar || bestRating?.name} - ${bestRating?.rating}/5</li>
    <li>🔹 <strong>أفضل خصم:</strong> ${bestDiscount?.name?.ar || bestDiscount?.name} - خصم ${bestDiscount?.discount || 0}%</li>
  </ul>
  
  <h2>📊 جدول المقارنة السريع</h2>
   <div
    <thead> <tr><th>المنتج</th><th>السعر</th><th>التقييم</th><th>الخصم</th></tr> </thead>
    <tbody>
    ${featured.slice(0,5).map(p => `
    <tr><td><strong>${p.name?.ar || p.name}</strong></td><td>${p.price}$</td><td>${p.rating} ★</td><td>${p.discount || 0}%</td></tr>
    `).join('')}
    </tbody>
   </div>
  
  <h2>💡 نصائح للشراء</h2>
  <ul>
    <li>✅ تحقق من توافق المنتج مع أجهزتك</li>
    <li>✅ قارن الأسعار بين البائعين</li>
    <li>✅ اقرأ مراجعات المستخدمين قبل الشراء</li>
    <li>✅ تأكد من سياسة الإرجاع والضمان</li>
  </ul>
  
  <p style="text-align:center; font-size:0.8rem; margin-top:2rem;">⚠️ روابط أمازون هي روابط أفلييت - نحصل على عمولة صغيرة بدون تكلفة إضافية عليك</p>
  `;
}

// ============================================
// شات بوت
// ============================================
app.post('/api/chat', async (req, res) => {
  const { message } = req.body;
  console.log(`📩: ${message}`);
  
  if (message.includes('تقرير') && (message.includes('انزل') || message.includes('نشر'))) {
    let products = [];
    const pPath = path.join(__dirname, 'products.json');
    if (fs.existsSync(pPath)) products = JSON.parse(fs.readFileSync(pPath, 'utf8'));
    const content = await generateReport(products);
    const now = new Date();
    const title = `تقرير منتجات - ${now.toLocaleDateString('ar-EG')}`;
    const result = await saveToBlog(content, title);
    return res.json({ success: true, answer: `✅ تم نشر التقرير في المدونة!\n\n🔗 الرابط: ${result.url}` });
  }
  
  let answer = 'مرحباً! أنا مساعد NEO PULSE HUB.\n\nاكتب "انزل تقرير" لنشر تقرير المنتجات في المدونة.';
  
  if (GROQ_API_KEY) {
    try {
      const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${GROQ_API_KEY}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ model: 'llama-3.1-8b-instant', messages: [{ role: 'user', content: message }], max_tokens: 300 })
      });
      const data = await response.json();
      if (data.choices) answer = data.choices[0].message.content;
    } catch(e) { console.log(e); }
  }
  res.json({ success: true, answer });
});

// ============================================
// نقطة نشر تقرير (API)
// ============================================
app.post('/api/post-report', async (req, res) => {
  try {
    let products = [];
    const pPath = path.join(__dirname, 'products.json');
    if (fs.existsSync(pPath)) products = JSON.parse(fs.readFileSync(pPath, 'utf8'));
    const content = await generateReport(products);
    const now = new Date();
    const title = `تقرير منتجات - ${now.toLocaleDateString('ar-EG')}`;
    const result = await saveToBlog(content, title);
    res.json({ success: true, message: '✅ تم نشر التقرير في المدونة', url: result.url });
  } catch(e) {
    res.json({ success: false, error: e.message });
  }
});

// ============================================
// نقطة فحص الحالة
// ============================================
app.get('/api/status', (req, res) => {
  res.json({ success: true, status: 'running', time: new Date().toISOString() });
});

// ============================================
// تشغيل الخادم
// ============================================
const PORT = process.env.PORT || 3000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Server running on port ${PORT}`);
  console.log(`✅ /api/chat - شات بوت`);
  console.log(`✅ /api/post-report - نشر تقرير في المدونة`);
  console.log(`✅ /api/status - فحص الحالة`);
});
