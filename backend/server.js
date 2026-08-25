import express from 'express';
import cors from 'cors';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();

app.use(cors({ origin: '*' }));
app.use(express.json());

const GROQ_API_KEY = process.env.GROQ_API_KEY;
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
const GEMINI_MODEL = process.env.GEMINI_MODEL || 'gemini-2.5-flash';
const CATALOG_PATH = path.resolve(__dirname, '..', 'products.json');

// تُعاد بيانات الكتالوج من جذر المشروع حتى تعمل الخدمة من backend/ على Render.
function loadProducts() {
  if (!fs.existsSync(CATALOG_PATH)) return [];
  const products = JSON.parse(fs.readFileSync(CATALOG_PATH, 'utf8'));
  return Array.isArray(products) ? products : [];
}

function productName(product) {
  if (typeof product?.name === 'object') return product.name.ar || product.name.en || '';
  return product?.name || '';
}

function safeRecommendationCandidates(products, budget) {
  const maximum = Number.isFinite(Number(budget)) && Number(budget) > 0 ? Number(budget) * 1.1 : Infinity;
  return products
    .filter((product) => Number(product.price) <= maximum)
    .sort((left, right) => Number(right.rating || 0) - Number(left.rating || 0))
    .slice(0, 30);
}

function localRecommendations(products, interests, budget) {
  const terms = String(interests || '').toLowerCase().split(/[،,\s]+/).map((term) => term.trim()).filter((term) => term.length > 1);
  const candidates = safeRecommendationCandidates(products, budget);
  return candidates
    .map((product) => {
      const searchable = `${productName(product)} ${product.name?.en || ''} ${product.category || ''} ${JSON.stringify(product.specifications || {})}`.toLowerCase();
      const matches = terms.reduce((count, term) => count + (searchable.includes(term) ? 1 : 0), 0);
      return { product, score: Number(product.rating || 0) * 10 + matches * 30 };
    })
    .sort((left, right) => right.score - left.score)
    .slice(0, 3)
    .map((entry) => entry.product);
}

async function geminiRecommendations({ query, recipient, interests, budget, products }) {
  if (!GEMINI_API_KEY) return null;
  const candidates = safeRecommendationCandidates(products, budget);
  const allowedIds = new Set(candidates.map((product) => product.id));
  const catalog = candidates.map((product) => ({
    id: product.id,
    name: productName(product),
    category: product.category,
    price: product.price,
    rating: product.rating,
  }));
  const prompt = `أنت مساعد توصيات هدايا عربي. اختر حتى 3 معرفات فقط من قائمة المنتجات المعطاة. ملف الهدية: ${recipient || 'غير محدد'}. الاهتمامات: ${interests || 'غير محددة'}. الطلب: ${query}. الميزانية: ${budget || 'غير محددة'}. أعد JSON صالحاً فقط بالشكل {"ids":["id"],"reason":"سبب عربي قصير"}. المنتجات: ${JSON.stringify(catalog)}`;

  try {
    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${encodeURIComponent(GEMINI_MODEL)}:generateContent?key=${encodeURIComponent(GEMINI_API_KEY)}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }], generationConfig: { temperature: 0.2, maxOutputTokens: 250, responseMimeType: 'application/json' } }),
    });
    if (!response.ok) {
      console.error(`Gemini recommendation error: ${response.status}`);
      return null;
    }
    const data = await response.json();
    const text = data?.candidates?.[0]?.content?.parts?.map((part) => part.text || '').join('') || '';
    const result = JSON.parse(text.replace(/^```json\s*|\s*```$/g, ''));
    const ids = Array.isArray(result.ids) ? result.ids.filter((id) => allowedIds.has(id)).slice(0, 3) : [];
    const recommended = ids.map((id) => candidates.find((product) => product.id === id)).filter(Boolean);
    if (!recommended.length) return null;
    return { products: recommended, reason: String(result.reason || 'اختيرت المنتجات وفق الاهتمامات والميزانية.'), mode: 'ai' };
  } catch (error) {
    console.error(`Gemini recommendation failure: ${error.message}`);
    return null;
  }
}

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
      <a href="${(p.affiliate_amazon || '#').replace('YOUR_AMAZON_TAG', 'neopulsehub-20')}" target="_blank" class="buy-btn" style="display:inline-block;background:#ff9900;color:#fff;padding:8px 16px;border-radius:6px;text-decoration:none;">اشتر الآن 🛒</a>
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
    const products = loadProducts();
    
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
    const products = loadProducts();
    
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

// توصيات هدايا مخصصة: Gemini عند توفر المفتاح، وترتيب كتالوج محلي واضح عند عدم توفره.
app.post('/api/ai/recommend', async (req, res) => {
  const { query = '', recipient = '', interests = '', budget = null } = req.body || {};
  const normalizedQuery = String(query).trim();
  if (!normalizedQuery || normalizedQuery.length > 500) {
    return res.status(400).json({ success: false, error: 'query is required and must be at most 500 characters' });
  }
  const products = loadProducts();
  if (!products.length) return res.status(503).json({ success: false, error: 'catalog unavailable' });

  const aiResult = await geminiRecommendations({ query: normalizedQuery, recipient: String(recipient).slice(0, 160), interests: String(interests).slice(0, 300), budget, products });
  if (aiResult) return res.json({ success: true, data: aiResult.products, reason: aiResult.reason, recommendation_mode: aiResult.mode });

  const fallback = localRecommendations(products, interests || normalizedQuery, budget);
  return res.json({
    success: true,
    data: fallback,
    reason: 'تعذر الوصول إلى نموذج الذكاء الاصطناعي؛ رتّبنا المنتجات محلياً حسب الاهتمامات والميزانية.',
    recommendation_mode: 'fallback',
  });
});

// ============================================
// نقطة فحص الحالة
// ============================================
app.get('/api/status', (req, res) => {
  res.json({ success: true, status: 'running', time: new Date().toISOString() });
});

app.get('/api/health', (_req, res) => {
  res.json({ success: true, status: 'healthy', service: 'neo-pulse-node-api', products: loadProducts().length, geminiConfigured: Boolean(GEMINI_API_KEY) });
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
  console.log(`✅ /api/ai/recommend - توصيات الهدايا`);
  console.log(`✅ /api/health - فحص الصحة`);
});

export default app;
