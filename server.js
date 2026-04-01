const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const app = express();

app.use(cors({ origin: '*' }));
app.use(express.json());

// 🔑 المفتاح من المتغيرات البيئية فقط (آمن)
const GROQ_API_KEY = process.env.GROQ_API_KEY;

if (!GROQ_API_KEY) {
  console.log('❌ GROQ_API_KEY غير موجود في المتغيرات البيئية');
}

// ============================================
// الاتصال بـ Groq API (ذكاء اصطناعي حقيقي)
// ============================================
async function getAIResponse(message) {
  if (!GROQ_API_KEY) {
    return 'عذراً، مفتاح API غير متوفر. يرجى التواصل مع الدعم الفني.';
  }
  
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
            - صحة ذكية: Fitbit Charge 6 (149$), Oura Ring (299$), Xiaomi Band 8 Pro (59$)
            
            أجب بالعربية، مختصر، مفيد. استخدم إيموجيات مناسبة.`
          },
          { role: 'user', content: message }
        ],
        temperature: 0.7,
        max_tokens: 500
      })
    });
    
    const data = await response.json();
    if (data.choices && data.choices[0]) {
      return data.choices[0].message.content;
    }
    return 'عذراً، حدث خطأ في الرد. حاول مرة أخرى.';
    
  } catch (error) {
    console.error('AI Error:', error.message);
    return 'عذراً، حدث خطأ في الاتصال. حاول مرة أخرى.';
  }
}

// ============================================
// توليد مقال جديد
// ============================================
async function generateArticle(topic, language) {
  if (!GROQ_API_KEY) return null;
  
  const prompt = `اكتب مقالة احترافية باللغة ${language === 'ar' ? 'العربية' : 'الإنجليزية'} بعنوان: "${topic}"
  
  المتطلبات:
  - طول المقال: 800-1000 كلمة
  - يتضمن مقدمة، 5-7 أقسام رئيسية، خاتمة
  - يحتوي على كلمات مفتاحية SEO
  - يتضمن روابط لمنتجات NEO PULSE HUB
  - نبرة المقال: احترافية، مفيدة، تشجع على الشراء
  
  اكتب المقال كامل بتنسيق HTML مع CSS بسيط.`;
  
  const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${GROQ_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: 'llama-3.1-8b-instant',
      messages: [{ role: 'user', content: prompt }],
      temperature: 0.7,
      max_tokens: 2500
    })
  });
  
  const data = await response.json();
  return data.choices[0].message.content;
}

// ============================================
// حفظ المقال في مجلد المدونة
// ============================================
async function saveArticle(content, title, language, category = 'general') {
  const slug = title
    .toLowerCase()
    .replace(/[^\w\s]/g, '')
    .replace(/\s+/g, '-')
    .substring(0, 50);
  
  const fileName = `${slug}.html`;
  const dir = path.join(__dirname, 'blog', language === 'ar' ? 'ar' : 'en');
  
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  
  const filePath = path.join(dir, fileName);
  const now = new Date();
  const date = now.toLocaleDateString(language === 'ar' ? 'ar-EG' : 'en-US');
  
  const fullHtml = `<!DOCTYPE html>
<html lang="${language === 'ar' ? 'ar' : 'en'}" dir="${language === 'ar' ? 'rtl' : 'ltr'}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${title} | NEO PULSE HUB</title>
<meta name="description" content="مراجعة شاملة لـ ${title} - أفضل المنتجات التقنية">
<meta name="keywords" content="${title}, مراجعة, منتجات تقنية, NEO PULSE HUB">
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
a:hover{text-decoration:underline}
img{max-width:100%;border-radius:12px;margin:1rem 0}
table{width:100%;border-collapse:collapse;margin:1.5rem 0;background:#0a0d1a;border-radius:12px;overflow:hidden}
th,td{padding:12px;border:1px solid #1e1e2e;text-align:${language === 'ar' ? 'right' : 'left'}}
th{background:#3b82f6;color:white}
.product-card{background:#0a0d1a;border:1px solid #3b82f6;border-radius:16px;padding:1.5rem;margin:1.5rem 0}
.product-price{font-size:1.5rem;color:#3b82f6;font-weight:bold}
.buy-btn{display:inline-block;background:linear-gradient(135deg,#ff9900,#e47911);color:white;padding:10px 20px;border-radius:50px;text-decoration:none;margin-top:1rem;font-weight:bold}
.buy-btn:hover{transform:translateY(-2px);box-shadow:0 4px 15px rgba(255,153,0,.4)}
.date{color:#6b6b8a;font-size:0.85rem;margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:1px solid #1e1e2e}
hr{border-color:#1e1e2e;margin:2rem 0}
.footer-links{text-align:center;margin-top:2rem;padding-top:1rem;border-top:1px solid #1e1e2e;color:#6b6b8a}
.footer-links a{margin:0 0.5rem}
@media(max-width:768px){.container{padding:1rem}h1{font-size:1.5rem}}
</style>
</head>
<body>
<div class="container">
<div class="date">📅 ${date} | 📝 ${category === 'review' ? 'مراجعة' : category === 'report' ? 'تقرير' : 'مقال'}</div>
${content}
<div class="footer-links">
<a href="/">🏠 الرئيسية</a> | 
<a href="/products.html">🛍️ المنتجات</a> | 
<a href="/blog/${language === 'ar' ? 'ar' : 'en'}">📝 المدونة</a>
</div>
</div>
</body>
</html>`;
  
  fs.writeFileSync(filePath, fullHtml, 'utf8');
  console.log(`✅ تم حفظ المقال: ${filePath}`);
  return { success: true, path: filePath, slug, url: `/blog/${language === 'ar' ? 'ar' : 'en'}/${fileName}` };
}

// ============================================
// الموضوعات المقترحة للمقالات
// ============================================
const TOPICS = {
  ar: [
    "أفضل 10 ساعات ذكية 2026",
    "دليل شراء الساعات الذكية للمبتدئين",
    "مقارنة: Apple Watch vs Samsung Galaxy Watch",
    "كيف تختار السماعة اللاسلكية المناسبة",
    "أفضل 5 منتجات للمنزل الذكي",
    "مراجعة شاملة: AirPods Pro 2",
    "الفرق بين الساعات الذكية وأساور اللياقة",
    "أحدث تقنيات الذكاء الاصطناعي في المنزل"
  ],
  en: [
    "Top 10 Smartwatches 2026",
    "Smartwatch Buying Guide for Beginners",
    "Comparison: Apple Watch vs Samsung Galaxy Watch",
    "How to Choose the Right Wireless Earbuds",
    "Top 5 Smart Home Products",
    "Complete Review: AirPods Pro 2",
    "Smartwatches vs Fitness Trackers",
    "Latest AI Technologies for Home"
  ]
};

// ============================================
// تخزين أسئلة الزوار للتحليل
// ============================================
let questionsDB = [];

function trackQuestion(question, productMentioned) {
  questionsDB.push({
    question,
    productMentioned,
    time: new Date().toISOString()
  });
  if (questionsDB.length > 100) questionsDB.shift();
}

function getTopQuestions(limit = 5) {
  const counts = {};
  questionsDB.forEach(q => {
    counts[q.question] = (counts[q.question] || 0) + 1;
  });
  
  return Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, limit)
    .map(([question, count]) => ({ question, count }));
}

// ============================================
// توليد تقرير منتجات (لـ AdSense)
// ============================================
async function generateProductsReport(products, type = 'weekly', language = 'ar') {
  const now = new Date();
  const date = now.toLocaleDateString(language === 'ar' ? 'ar-EG' : 'en-US');
  const weekStart = new Date(now.setDate(now.getDate() - now.getDay()));
  const weekEnd = new Date(now.setDate(now.getDate() - now.getDay() + 6));
  
  const featuredProducts = products.filter(p => p.featured).slice(0, 8);
  const bestSeller = products.sort((a, b) => b.reviews - a.reviews)[0];
  const bestRating = products.sort((a, b) => b.rating - a.rating)[0];
  const bestDiscount = products.sort((a, b) => (b.discount || 0) - (a.discount || 0))[0];
  
  const prompt = `اكتب تقريراً عن أفضل منتجات التقنية لعام 2026 باللغة العربية.
  
  المنتجات المميزة:
  ${featuredProducts.map(p => `- ${p.name.ar}: ${p.price}$، تقييم ${p.rating}/5، ${p.description?.ar?.substring(0, 100) || ''}`).join('\n')}
  
  أفضل منتج مبيعاً: ${bestSeller?.name?.ar} - ${bestSeller?.price}$
  أعلى تقييم: ${bestRating?.name?.ar} - ${bestRating?.rating}/5
  أفضل خصم: ${bestDiscount?.name?.ar} - خصم ${bestDiscount?.discount}%
  
  المتطلبات:
  - عنوان جذاب لتحسين SEO
  - مقدمة عن أهمية هذه المنتجات
  - مراجعة مختصرة لكل منتج (المميزات، السعر، لمن يناسب)
  - جدول مقارنة بين أفضل 3 منتجات
  - خاتمة وتوصية للقارئ
  - نصائح للشراء
  - إضافة روابط للمنتجات في المتجر
  
  اكتب المقال كامل بتنسيق HTML مع CSS متجاوب.`;
  
  const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${GROQ_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: 'llama-3.1-8b-instant',
      messages: [{ role: 'user', content: prompt }],
      temperature: 0.7,
      max_tokens: 3000
    })
  });
  
  const data = await response.json();
  let content = data.choices[0].message.content;
  
  // إضافة جدول المقارنة إذا لم يكن موجوداً
  if (!content.includes('مقارنة') && !content.includes('جدول')) {
    const comparisonTable = `
    <h2>📊 جدول مقارنة سريع</h2>
    <table>
      <tr><th>المنتج</th><th>السعر</th><th>التقييم</th><th>المميزات</th></tr>
      ${featuredProducts.slice(0, 4).map(p => `
      <tr>
        <td><strong>${p.name.ar}</strong></td>
        <td>${p.price}$</td>
        <td>${p.rating} ★</td>
        <td>${p.description?.ar?.substring(0, 80) || 'مميزات متعددة'}</td>
      </tr>
      `).join('')}
    </table>
    `;
    content += comparisonTable;
  }
  
  // إضافة قسم المنتجات مع روابط الشراء
  const productsSection = `
  <h2>🛒 أين تشتري هذه المنتجات؟</h2>
  <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:20px; margin:20px 0;">
    ${featuredProducts.slice(0, 4).map(p => {
      let amazonLink = p.affiliate_amazon || '#';
      if (!amazonLink.includes('tag=')) {
        amazonLink += (amazonLink.includes('?') ? '&' : '?') + `tag=neopulsehub-20`;
      }
      return `
      <div class="product-card">
        <h3>${p.name.ar}</h3>
        <div class="product-price">${p.price}$</div>
        <p>⭐ ${p.rating}/5 (${p.reviews?.toLocaleString() || 0} مراجعة)</p>
        <p>${p.description?.ar?.substring(0, 100) || ''}</p>
        <a href="${amazonLink}" target="_blank" class="buy-btn" rel="sponsored nofollow">🛒 شراء من أمازون</a>
      </div>
      `;
    }).join('')}
  </div>
  <p style="text-align:center; font-size:0.85rem; color:#6b6b8a;">⚠️ روابط أمازون هي روابط أفلييت - نحصل على عمولة صغيرة بدون تكلفة إضافية عليك</p>
  `;
  
  content += productsSection;
  
  return content;
}

// ============================================
// توليد تقرير يومي
// ============================================
async function generateDailyReport(analyticsData, language = 'ar') {
  const now = new Date();
  const date = now.toLocaleDateString(language === 'ar' ? 'ar-EG' : 'en-US');
  const time = now.toLocaleTimeString(language === 'ar' ? 'ar-EG' : 'en-US');
  
  if (language === 'ar') {
    return `
📊 **تقرير NEO PULSE HUB اليومي**
📅 التاريخ: ${date}
🕐 الوقت: ${time}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 **إحصائيات الزوار:**
• إجمالي الزوار: ${analyticsData.totalVisits || 0}
• الزوار الجدد: ${analyticsData.newVisits || 0}
• مشاهدات الصفحات: ${analyticsData.pageViews || 0}

🛒 **المبيعات:**
• عدد الطلبات: ${analyticsData.orders || 0}
• إجمالي المبيعات: $${analyticsData.sales || 0}
• العمولات: $${analyticsData.commission || 0}

🔥 **المنتجات الأكثر مبيعاً:**
${analyticsData.topProducts?.map((p, i) => `${i+1}. ${p.name} - ${p.sales} عملية`).join('\n') || '• لا توجد بيانات'}

❓ **أكثر الأسئلة تكراراً:**
${analyticsData.topQuestions?.map((q, i) => `${i+1}. "${q.question}" - ${q.count} مرة`).join('\n') || '• لا توجد بيانات'}

💡 **توصيات:**
${analyticsData.recommendations?.map(r => `• ${r}`).join('\n') || '• لا توجد توصيات'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 NEO PULSE HUB AI Manager
    `;
  } else {
    return `
📊 **NEO PULSE HUB Daily Report**
📅 Date: ${date}
🕐 Time: ${time}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 **Visitor Statistics:**
• Total Visitors: ${analyticsData.totalVisits || 0}
• New Visitors: ${analyticsData.newVisits || 0}
• Page Views: ${analyticsData.pageViews || 0}

🛒 **Sales:**
• Orders: ${analyticsData.orders || 0}
• Total Sales: $${analyticsData.sales || 0}
• Commission: $${analyticsData.commission || 0}

🔥 **Top Selling Products:**
${analyticsData.topProducts?.map((p, i) => `${i+1}. ${p.name} - ${p.sales} sales`).join('\n') || '• No data'}

❓ **Most Asked Questions:**
${analyticsData.topQuestions?.map((q, i) => `${i+1}. "${q.question}" - ${q.count} times`).join('\n') || '• No data'}

💡 **Recommendations:**
${analyticsData.recommendations?.map(r => `• ${r}`).join('\n') || '• No recommendations'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 NEO PULSE HUB AI Manager
    `;
  }
}

// ============================================
// إرسال التقرير
// ============================================
async function sendReport(report) {
  console.log('📊 التقرير:');
  console.log(report);
  
  const reportDir = path.join(__dirname, 'reports');
  if (!fs.existsSync(reportDir)) {
    fs.mkdirSync(reportDir, { recursive: true });
  }
  
  const fileName = `report-${new Date().toISOString().split('T')[0]}.txt`;
  fs.writeFileSync(path.join(reportDir, fileName), report, 'utf8');
  console.log(`✅ تم حفظ التقرير: ${fileName}`);
}

// ============================================
// نقاط API
// ============================================

// نقطة الشات
app.post('/api/chat', async (req, res) => {
  try {
    const { message } = req.body;
    console.log(`📩 سؤال: ${message}`);
    
    trackQuestion(message);
    const answer = await getAIResponse(message);
    
    res.json({ success: true, answer: answer || 'عذراً، حدث خطأ. حاول مرة أخرى.' });
    
  } catch (error) {
    console.error('❌ خطأ:', error);
    res.json({ success: true, answer: 'عذراً، حدث خطأ. حاول مرة أخرى.' });
  }
});

// نقطة توليد مقال
app.post('/api/generate-article', async (req, res) => {
  try {
    const { topic, language = 'ar' } = req.body;
    const articleTopic = topic || TOPICS[language][0];
    
    console.log(`📝 جاري كتابة مقال: ${articleTopic}`);
    const content = await generateArticle(articleTopic, language);
    const result = await saveArticle(content, articleTopic, language, 'article');
    
    res.json({ success: true, article: result, content: content.substring(0, 500) });
  } catch (error) {
    console.error('❌ خطأ:', error);
    res.json({ success: false, error: error.message });
  }
});

// نقطة توليد تقرير منتجات ونشره في المدونة (لـ AdSense)
app.post('/api/generate-products-report', async (req, res) => {
  try {
    const { type = 'weekly', language = 'ar' } = req.body;
    
    // قراءة المنتجات
    let products = [];
    const productsPath = path.join(__dirname, 'products.json');
    if (fs.existsSync(productsPath)) {
      products = JSON.parse(fs.readFileSync(productsPath, 'utf8'));
    } else {
      return res.json({ success: false, error: 'products.json غير موجود' });
    }
    
    console.log(`📊 جاري توليد تقرير منتجات ${type}...`);
    const content = await generateProductsReport(products, type, language);
    
    const title = language === 'ar' 
      ? `تقرير ${type === 'weekly' ? 'أسبوعي' : type === 'monthly' ? 'شهري' : 'يومي'} - أفضل منتجات التقنية ${new Date().getFullYear()}`
      : `${type === 'weekly' ? 'Weekly' : type === 'monthly' ? 'Monthly' : 'Daily'} Report - Best Tech Products ${new Date().getFullYear()}`;
    
    const result = await saveArticle(content, title, language, 'report');
    
    res.json({ 
      success: true, 
      message: `✅ تم نشر تقرير ${type} في المدونة`,
      url: result.url,
      title: title
    });
    
  } catch (error) {
    console.error('❌ خطأ:', error);
    res.json({ success: false, error: error.message });
  }
});

// نقطة توليد مقالات متعددة
app.post('/api/generate-batch', async (req, res) => {
  try {
    const { language = 'ar', count = 3 } = req.body;
    const topics = TOPICS[language].slice(0, count);
    const results = [];
    
    for (const topic of topics) {
      console.log(`📝 جاري كتابة: ${topic}`);
      const content = await generateArticle(topic, language);
      const result = await saveArticle(content, topic, language, 'article');
      results.push(result);
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
    
    res.json({ success: true, articles: results });
  } catch (error) {
    console.error('❌ خطأ:', error);
    res.json({ success: false, error: error.message });
  }
});

// نقطة توليد مراجعة منتج
app.post('/api/generate-review', async (req, res) => {
  try {
    const { productId, language = 'ar' } = req.body;
    
    let products = [];
    const productsPath = path.join(__dirname, 'products.json');
    if (fs.existsSync(productsPath)) {
      products = JSON.parse(fs.readFileSync(productsPath, 'utf8'));
    }
    
    const product = products.find(p => p.id === productId);
    if (!product) {
      return res.json({ success: false, error: 'المنتج غير موجود' });
    }
    
    const productName = product.name?.[language] || product.name?.ar || product.name;
    const prompt = `اكتب مراجعة مفصلة لمنتج ${productName} باللغة ${language === 'ar' ? 'العربية' : 'الإنجليزية'}.
    
    المعلومات:
    - السعر: ${product.price}$
    - التقييم: ${product.rating || 4.5}/5
    - الفئة: ${product.category_ar || product.category}
    - الوصف: ${product.description?.[language] || product.description?.ar || ''}
    
    المتطلبات:
    - مراجعة 500-700 كلمة
    - المميزات (4-6 نقاط)
    - العيوب (2-3 نقاط)
    - مقارنة مع منتج منافس
    - الخلاصة والتوصية
    - من يناسب هذا المنتج
    
    اكتب المراجعة كاملة بتنسيق HTML.`;
    
    const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${GROQ_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'llama-3.1-8b-instant',
        messages: [{ role: 'user', content: prompt }],
        temperature: 0.7,
        max_tokens: 2000
      })
    });
    
    const data = await response.json();
    const review = data.choices[0].message.content;
    
    const title = `${language === 'ar' ? 'مراجعة' : 'Review'}: ${productName}`;
    const result = await saveArticle(review, title, language, 'review');
    
    res.json({ success: true, review: review.substring(0, 500), article: result });
  } catch (error) {
    console.error('❌ خطأ:', error);
    res.json({ success: false, error: error.message });
  }
});

// نقطة الحصول على تقرير يومي
app.get('/api/daily-report', async (req, res) => {
  try {
    const language = req.query.lang || 'ar';
    
    const analyticsData = {
      totalVisits: Math.floor(Math.random() * 200) + 100,
      newVisits: Math.floor(Math.random() * 60) + 20,
      pageViews: Math.floor(Math.random() * 500) + 200,
      orders: Math.floor(Math.random() * 20) + 5,
      sales: Math.floor(Math.random() * 5000) + 1000,
      commission: Math.floor(Math.random() * 250) + 50,
      topProducts: [
        { name: "Apple Watch Series 9", sales: Math.floor(Math.random() * 10) + 1 },
        { name: "AirPods Pro 2", sales: Math.floor(Math.random() * 8) + 1 },
        { name: "Samsung Galaxy Watch 6", sales: Math.floor(Math.random() * 6) + 1 }
      ],
      topQuestions: getTopQuestions(5),
      recommendations: language === 'ar' 
        ? ["الزوار يسألون كثير عن الساعات الذكية، ركز على تسويقها", "أضف مقالة جديدة عن AirPods Pro 2", "عزز عروض المنزل الذكي"]
        : ["Visitors ask a lot about smartwatches", "Add a new article about AirPods Pro 2", "Boost smart home offers"]
    };
    
    const report = await generateDailyReport(analyticsData, language);
    await sendReport(report);
    
    res.json({ success: true, report, language });
  } catch (error) {
    console.error('❌ خطأ:', error);
    res.json({ success: false, error: error.message });
  }
});

// نقطة فحص الصحة
app.get('/api/status', (req, res) => {
  res.json({ 
    success: true, 
    ai: GROQ_API_KEY ? 'Groq ✅' : '❌',
    status: 'running',
    time: new Date().toISOString(),
    bots: {
      chat: 'active',
      articles: 'active',
      reviews: 'active',
      reports: 'active',
      products_report: 'active'
    }
  });
});

// نقطة العروض
app.get('/api/deals', (req, res) => {
  res.json({
    success: true,
    deals: [
      { name: "Xiaomi Band 8 Pro", price: 59, original: 79, discount: 25 },
      { name: "Amazfit GTR 4", price: 149, original: 199, discount: 25 },
      { name: "Galaxy Buds2 Pro", price: 179, original: 229, discount: 22 }
    ]
  });
});

// ============================================
// تشغيل التقرير التلقائي كل أسبوع (الأحد)
// ============================================
setInterval(async () => {
  const now = new Date();
  // كل يوم أحد الساعة 9 صباحاً
  if (now.getDay() === 0 && now.getHours() === 9 && now.getMinutes() < 5) {
    console.log('📊 تشغيل تقرير المنتجات الأسبوعي التلقائي...');
    try {
      let products = [];
      const productsPath = path.join(__dirname, 'products.json');
      if (fs.existsSync(productsPath)) {
        products = JSON.parse(fs.readFileSync(productsPath, 'utf8'));
      }
      
      const content = await generateProductsReport(products, 'weekly', 'ar');
      const title = `تقرير أسبوعي - أفضل منتجات التقنية ${new Date().getFullYear()}`;
      await saveArticle(content, title, 'ar', 'report');
      console.log('✅ تم نشر تقرير المنتجات الأسبوعي');
    } catch (e) {
      console.error('❌ خطأ في التقرير التلقائي:', e);
    }
  }
}, 60 * 60 * 1000);

// ============================================
// تشغيل الخادم
// ============================================
const PORT = process.env.PORT || 3000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 NEO PULSE HUB AI Manager running on port ${PORT}`);
  console.log(`🤖 Groq AI: ${GROQ_API_KEY ? '✅ شغال' : '❌ غير موجود'}`);
  console.log(`📝 بوت المحتوى: ✅ شغال`);
  console.log(`📊 بوت التقارير: ✅ شغال`);
  console.log(`📈 بوت تقارير المنتجات: ✅ شغال`);
});
