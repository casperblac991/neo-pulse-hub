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

const CATEGORY_ALIASES = {
  smartwatch: ['smartwatch', 'smart watch', 'ساعة ذكية', 'ساعات ذكية', 'ساعة رياضية', 'ساعات رياضية', 'watch'],
  earbuds: ['earbuds', 'سماعات اذن', 'سماعات أذن', 'ايربودز', 'إيربودز', 'سماعات لاسلكية'],
  headphones: ['headphones', 'سماعات رأس', 'سماعة رأس', 'عازلة للضوضاء'],
  smartglasses: ['smart glasses', 'نظارات ذكية', 'نظارة ذكية', 'نظارات'],
  smarthome: ['smart home', 'منزل ذكي', 'المنزل الذكي', 'مقبس ذكي', 'كاميرا منزلية'],
  health: ['health', 'صحة', 'لياقة', 'رياضة', 'fitness', 'خاتم ذكي', 'سوار صحي'],
  productivity: ['productivity', 'إنتاجية', 'لوحة مفاتيح', 'ماوس', 'طابعة'],
};

function normalizeArabic(value) {
  return String(value || '')
    .toLowerCase()
    .normalize('NFKD')
    .replace(/[\u064B-\u065F\u0670]/g, '')
    .replace(/[إأآ]/g, 'ا')
    .replace(/ة/g, 'ه')
    .replace(/ى/g, 'ي')
    .replace(/ـ/g, '')
    .replace(/[^\p{L}\p{N}]+/gu, ' ')
    .trim();
}

function requestedCategories(text) {
  const normalized = normalizeArabic(text);
  return Object.entries(CATEGORY_ALIASES)
    .filter(([, aliases]) => aliases.some((alias) => normalized.includes(normalizeArabic(alias))))
    .map(([category]) => category);
}

function productCategoryText(product) {
  return normalizeArabic([
    product.category,
    product.category_ar,
    product.category_en,
    productName(product),
    product.description?.ar,
    JSON.stringify(product.specifications || {}),
  ].filter(Boolean).join(' '));
}

function matchesRequestedCategory(product, categories) {
  if (!categories.length) return true;
  const text = productCategoryText(product);
  return categories.some((category) => CATEGORY_ALIASES[category].some((alias) => text.includes(normalizeArabic(alias))));
}

function safeRecommendationCandidates(products, budget) {
  const maximum = Number.isFinite(Number(budget)) && Number(budget) > 0 ? Number(budget) * 1.1 : Infinity;
  return products
    .filter((product) => Number(product.price) <= maximum)
    .sort((left, right) => Number(right.rating || 0) - Number(left.rating || 0))
    .slice(0, 30);
}

function localRecommendations(products, interests, budget) {
  const normalizedInput = normalizeArabic(interests);
  const terms = normalizedInput.split(/\s+/).filter((term) => term.length > 1);
  const categories = requestedCategories(normalizedInput);
  const primaryCategories = categories.filter((category) => ['smartwatch', 'earbuds', 'headphones', 'smartglasses', 'smarthome', 'productivity'].includes(category));
  const filterCategories = primaryCategories.length ? primaryCategories : categories;
  const candidates = safeRecommendationCandidates(products, budget);
  const categoryCandidates = candidates.filter((product) => matchesRequestedCategory(product, filterCategories));
  const pool = categoryCandidates.length ? categoryCandidates : candidates;
  return pool
    .map((product) => {
      const searchable = productCategoryText(product);
      const matches = terms.reduce((count, term) => count + (searchable.includes(term) ? 1 : 0), 0);
      const categoryBonus = filterCategories.length && matchesRequestedCategory(product, filterCategories) ? 500 : 0;
      return { product, score: categoryBonus + Number(product.rating || 0) * 10 + matches * 30 };
    })
    .sort((left, right) => right.score - left.score)
    .slice(0, 3)
    .map((entry) => entry.product);
}

function parseGeminiJson(text) {
  const cleaned = String(text || '').replace(/```(?:json)?/gi, '').trim();
  const start = cleaned.indexOf('{');
  const end = cleaned.lastIndexOf('}');
  if (start < 0 || end <= start) throw new Error('Gemini response contains no JSON object');
  const candidate = cleaned.slice(start, end + 1);
  try {
    return JSON.parse(candidate);
  } catch (error) {
    // Handle a common harmless formatting issue without accepting arbitrary text.
    const repaired = candidate.replace(/,\s*([}\]])/g, '$1');
    return JSON.parse(repaired);
  }
}

async function geminiRecommendations({ query, recipient, interests, budget, products }) {
  if (!GEMINI_API_KEY) return null;
  const candidates = safeRecommendationCandidates(products, budget);
  const allowedIds = new Set(candidates.map((product) => product.id));
  const catalog = candidates.map((product, index) => ({
    index: index + 1,
    id: product.id,
    name: productName(product),
    category: product.category,
    price: product.price,
    rating: product.rating,
  }));
  const prompt = `أنت مساعد توصيات هدايا عربي. اختر حتى 3 منتجات فقط من القائمة المرقمة. ملف الهدية: ${recipient || 'غير محدد'}. الاهتمامات: ${interests || 'غير محددة'}. الطلب: ${query}. الميزانية: ${budget || 'غير محددة'}. أعد JSON صالحاً فقط بالشكل {"indexes":[1,2,3],"reason":"سبب عربي قصير"}. استخدم أرقام index المعروضة حصراً ولا تختر منتجاً خارج القائمة. المنتجات: ${JSON.stringify(catalog)}`;

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
    const result = parseGeminiJson(text);
    const indexes = Array.isArray(result.indexes)
      ? result.indexes.map((index) => Number(index)).filter((index) => Number.isInteger(index) && index >= 1 && index <= candidates.length).slice(0, 3)
      : [];
    const rawIds = Array.isArray(result.ids) ? result.ids
      : Array.isArray(result.products) ? result.products.map((product) => typeof product === 'string' ? product : product?.id)
      : Array.isArray(result.recommendations) ? result.recommendations.map((product) => typeof product === 'string' ? product : product?.id)
      : [];
    const ids = rawIds.filter((id) => allowedIds.has(id)).slice(0, 3);
    let recommended = indexes.map((index) => candidates[index - 1]).filter(Boolean);
    if (!recommended.length) recommended = ids.map((id) => candidates.find((product) => product.id === id)).filter(Boolean);
    if (!recommended.length) {
      // بديل parsing آمن عندما يعيد النموذج أسماء منتجات بدلاً من المعرفات المطلوبة.
      const normalizedText = normalizeArabic(text);
      recommended = candidates.filter((product) => normalizedText.includes(normalizeArabic(productName(product)))).slice(0, 3);
    }
    const categories = requestedCategories(`${query || ''} ${interests || ''}`);
    const primaryCategories = categories.filter((category) => ['smartwatch', 'earbuds', 'headphones', 'smartglasses', 'smarthome', 'productivity'].includes(category));
    const filterCategories = primaryCategories.length ? primaryCategories : categories;
    const categorySafe = recommended.filter((product) => matchesRequestedCategory(product, filterCategories));
    if (filterCategories.length && categorySafe.length) recommended = categorySafe;
    if (filterCategories.length && !categorySafe.length) return null;
    if (!recommended.length) return null;
    return { products: recommended, reason: String(result.reason || 'اختيرت المنتجات وفق الفئة والاهتمامات والميزانية.'), mode: 'ai' };
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
function buildCatalogContext(products) {
  return products.slice(0, 60).map((product) => ({
    id: product.id,
    name: productName(product),
    category: product.category || 'غير محدد',
    price: product.price ?? null,
    rating: product.rating ?? null,
    reviews: product.reviews ?? null,
    discount: product.discount ?? null,
  }));
}

async function getAIResponse(message) {
  const catalog = buildCatalogContext(loadProducts());
  const systemInstruction = `أنت Neo Copilot، مساعد ذكي لمتجر NEO PULSE HUB. أجب بالعربية باختصار وبصورة مفيدة عن المنتجات التقنية والمقارنات. استخدم كتالوج المنتجات المرفق عند التوصية، ولا تختلق أسعاراً أو توفراً أو مواصفات غير موجودة. إذا لم تكفِ البيانات، صرّح بذلك ووجّه المستخدم إلى صفحة المنتجات أو مكتشف الهدايا. لا تنفذ شراءً أو نشرًا خارجيًا من تلقاء نفسك.\\n\\nالكتالوج الحالي بصيغة JSON:\\n${JSON.stringify(catalog)}`;

  if (GEMINI_API_KEY) {
    try {
      const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${encodeURIComponent(GEMINI_MODEL)}:generateContent?key=${encodeURIComponent(GEMINI_API_KEY)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          systemInstruction: { parts: [{ text: systemInstruction }] },
          contents: [{ role: 'user', parts: [{ text: message }] }],
          generationConfig: { temperature: 0.45, maxOutputTokens: 300 },
        }),
      });
      if (response.ok) {
        const data = await response.json();
        const answer = data?.candidates?.[0]?.content?.parts?.map((part) => part.text || '').join('').trim();
        if (answer) return answer;
      } else {
        console.error(`Gemini chat error: ${response.status}`);
      }
    } catch (error) {
      console.error(`Gemini chat failure: ${error.message}`);
    }
  }

  if (!GROQ_API_KEY) return 'مرحباً! أنا مساعد NEO PULSE HUB. أستطيع مساعدتك في اختيار منتج أو توجيهك إلى مكتشف الهدايا.';
  
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
            content: systemInstruction
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
  const message = String(req.body?.message || '').trim();
  if (!message || message.length > 500) {
    return res.status(400).json({ success: false, error: 'message is required and must be at most 500 characters' });
  }
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

  const fallback = localRecommendations(products, `${normalizedQuery} ${interests}`, budget);
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
