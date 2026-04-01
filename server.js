const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const app = express();

app.use(cors({ origin: '*' }));
app.use(express.json());

const GROQ_API_KEY = process.env.GROQ_API_KEY;

async function saveToBlog(content, title) {
  let slug = title.toLowerCase().replace(/[^\w\s]/g, '').replace(/\s+/g, '-').substring(0, 50);
  if (!slug || slug === '' || slug === '-') {
    slug = `تقرير-منتجات-${Date.now()}`;
  }
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
<style>
body{font-family:Arial,sans-serif;background:#020510;color:#fff;padding:20px}
a{color:#3b82f6}
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
  return { success: true, url: `/blog/ar/${fileName}` };
}

async function generateReport(products) {
  const featured = products.filter(p => p.featured).slice(0, 6);
  return `
  <h2>🏆 أفضل المنتجات</h2>
  ${featured.map(p => `
  <div style="border:1px solid #3b82f6;padding:1rem;margin:1rem 0">
    <h3>${p.name?.ar || p.name}</h3>
    <p>💰 ${p.price}$</p>
    <p>⭐ ${p.rating}/5</p>
    <a href="${(p.affiliate_amazon || '#').replace('YOUR_AMAZON_TAG', 'neopulsehub-20')}" target="_blank">🛒 شراء من أمازون</a>
  </div>
  `).join('')}
  <p>⚠️ روابط أمازون أفلييت</p>
  `;
}

app.post('/api/post-report', async (req, res) => {
  try {
    let products = [];
    const pPath = path.join(__dirname, 'products.json');
    if (fs.existsSync(pPath)) products = JSON.parse(fs.readFileSync(pPath, 'utf8'));
    const content = await generateReport(products);
    const now = new Date();
    const title = `تقرير منتجات - ${now.toLocaleDateString('ar-EG')}`;
    const result = await saveToBlog(content, title);
    res.json({ success: true, message: '✅ تم النشر', url: result.url });
  } catch(e) {
    res.json({ success: false, error: e.message });
  }
});

app.post('/api/chat', async (req, res) => {
  const { message } = req.body;
  if (message.includes('تقرير')) {
    let products = [];
    const pPath = path.join(__dirname, 'products.json');
    if (fs.existsSync(pPath)) products = JSON.parse(fs.readFileSync(pPath, 'utf8'));
    const content = await generateReport(products);
    const now = new Date();
    const title = `تقرير منتجات - ${now.toLocaleDateString('ar-EG')}`;
    const result = await saveToBlog(content, title);
    return res.json({ success: true, answer: `✅ تم النشر: ${result.url}` });
  }
  res.json({ success: true, answer: 'اكتب "تقرير" لنشر تقرير' });
});

app.get('/api/status', (req, res) => {
  res.json({ success: true, status: 'running' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, '0.0.0.0', () => console.log(`🚀 Server on port ${PORT}`));
