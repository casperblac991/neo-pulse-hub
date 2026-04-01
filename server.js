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
  const now = new Date();
  const date = now.toLocaleDateString('ar-EG');
  const timestamp = Date.now();
  const fileName = `تقرير-منتجات-${timestamp}.html`;
  const dir = path.join(__dirname, 'blog', 'ar');
  
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  
  const filePath = path.join(dir, fileName);
  
  const fullHtml = `<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${title} | NEO PULSE HUB</title>
<style>
body{font-family:Arial,sans-serif;background:#020510;color:#fff;padding:20px}
a{color:#3b82f6}
.product-card{border:1px solid #3b82f6;padding:1rem;margin:1rem 0;border-radius:12px}
.price{color:#3b82f6;font-size:1.2rem}
</style>
</head>
<body>
<h1>📊 ${title}</h1>
<div>📅 ${date}</div>
${content}
<hr>
<p><a href="/">🏠 الرئيسية</a> | <a href="/products.html">🛍️ المنتجات</a></p>
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
  <h2>🏆 أفضل المنتجات هذا الأسبوع</h2>
  <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:20px;">
    ${featured.map(p => `
    <div class="product-card">
      <h3>${p.name?.ar || p.name}</h3>
      <div class="price">${p.price}$</div>
      <p>⭐ ${p.rating}/5 (${(p.reviews || 0).toLocaleString()} مراجعة)</p>
      <a href="${(p.affiliate_amazon || '#').replace('YOUR_AMAZON_TAG', 'neopulsehub-20')}" target="_blank" class="buy-btn" style="display:inline-block;background:#ff9900;color:#fff;padding:8px 16px;border-radius:50px;text-decoration:none;margin-top:10px;">🛒 شراء من أمازون</a>
    </div>
    `).join('')}
  </div>
  
  <h2>⭐ أفضل المنتجات حسب الفئة</h2>
  <ul>
    <li>🔹 <strong>الأكثر مبيعاً:</strong> ${bestSeller?.name?.ar || bestSeller?.name} - ${bestSeller?.price}$</li>
    <li>🔹 <strong>أعلى تقييم:</strong> ${bestRating?.name?.ar || bestRating?.name} - ${bestRating?.rating}/5</li>
    <li>🔹 <strong>أفضل خصم:</strong> ${bestDiscount?.name?.ar || bestDiscount?.name} - خصم ${bestDiscount?.discount || 0}%</li>
  </ul>
  
  <p style="text-align:center; font-size:0.8rem; margin-top:2rem;">⚠️ روابط أمازون هي روابط أفلييت - نحصل على عمولة صغيرة بدون تكلفة إضافية عليك</p>
  `;
}

// ============================================
// الاتصال بـ Groq API
// ============================================
async function getAIResponse(message) {
  if (!GROQ_API_KEY) return 'مرحباً! أنا مساعد NEO PULSE HUB. اكتب "انزل تقرير" لنشر تقرير المنتجات.';
  
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
            content: `أنت مساعد ذكي لمتجر NEO PULSE HUB. المنتجات: Apple Watch (399$), Samsung Galaxy Watch (299$), AirPods Pro 2 (249$). أجب بالعربية مختصراً.`
          },
          { role: 'user', content: message }
        ],
        temperature: 0.7,
        max_tokens: 300
      })
    });
    
    const data = await response.json();
    return data.choices?.[0]?.message?.content || 'عذراً، حدث خطأ';
  } catch (error) {
    return 'عذراً، حدث خطأ في الاتصال.';
  }
}

// ============================================
// نقطة نشر تقرير
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
    
    res.json({ success: true, message: '✅ تم نشر التقرير', url: result.url });
  } catch(e) {
    res.json({ success: false, error: e.message });
  }
});

// ============================================
// شات بوت
// ============================================
app.post('/api/chat', async (req, res) => {
  const { message } = req.body;
  console.log(`📩: ${message}`);
  
  // أمر نشر التقرير (فقط إذا قال "انزل تقرير" أو "نشر تقرير")
  if (message.includes('انزل') && message.includes('تقرير') || message.includes('نشر') && message.includes('تقرير')) {
    let products = [];
    const pPath = path.join(__dirname, 'products.json');
    if (fs.existsSync(pPath)) products = JSON.parse(fs.readFileSync(pPath, 'utf8'));
    
    const content = await generateReport(products);
    const now = new Date();
    const title = `تقرير منتجات - ${now.toLocaleDateString('ar-EG')}`;
    const result = await saveToBlog(content, title);
    
    return res.json({ success: true, answer: `✅ تم نشر التقرير في المدونة!\n\n🔗 الرابط: ${result.url}` });
  }
  
  // الأسئلة العادية
  const answer = await getAIResponse(message);
  res.json({ success: true, answer });
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
  console.log(`✅ /api/post-report - نشر تقرير`);
  console.log(`✅ /api/status - فحص الحالة`);
});
