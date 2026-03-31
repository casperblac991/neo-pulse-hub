const express = require('express');
const fs = require('fs');
const fetch = require('node-fetch');
const path = require('path');
const app = express();

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname)));

// ═══════════════════════════════════════════════════════════
// 📌 المتغيرات البيئية
// ═══════════════════════════════════════════════════════════
const GROQ_API_KEY = process.env.GROQ_API_KEY; // مفتاح xAI
const CJ_API_KEY = process.env.CJ_API_KEY;
const CJ_EMAIL = process.env.CJ_EMAIL;

// ═══════════════════════════════════════════════════════════
// 📌 Health Check
// ═══════════════════════════════════════════════════════════
app.get('/health', (req, res) => {
    res.json({ status: 'healthy', service: 'NEO PULSE HUB API' });
});

// ═══════════════════════════════════════════════════════════
// 📌 جلب المنتجات (يستخدمه المتجر)
// ═══════════════════════════════════════════════════════════
app.get('/api/products', (req, res) => {
    try {
        const products = JSON.parse(fs.readFileSync('./products.json', 'utf8'));
        res.json(products);
    } catch (error) {
        res.json([]);
    }
});

// ═══════════════════════════════════════════════════════════
// 📌 تحديث المنتجات من CJ API (كل 6 ساعات)
// ═══════════════════════════════════════════════════════════
async function updateProductsFromCJ() {
    if (!CJ_API_KEY || !CJ_EMAIL) {
        console.log('⚠️ CJ API keys not set, skipping update');
        return;
    }
    
    try {
        const response = await fetch('https://developers.cjdropshipping.com/api2.0/v1/product/list', {
            method: 'POST',
            headers: {
                'CJ-Access-Token': CJ_API_KEY,
                'Email': CJ_EMAIL,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ pageNum: 1, pageSize: 20 })
        });
        
        const data = await response.json();
        
        if (data && data.data && data.data.length > 0) {
            fs.writeFileSync('./products.json', JSON.stringify(data.data, null, 2));
            console.log(`✅ Updated ${data.data.length} products from CJ`);
        }
    } catch (error) {
        console.error('❌ CJ update failed:', error);
    }
}

// تشغيل التحديث أول مرة
setTimeout(updateProductsFromCJ, 5000);
// كل 6 ساعات
setInterval(updateProductsFromCJ, 6 * 60 * 60 * 1000);

// ═══════════════════════════════════════════════════════════
// 📌 بوت Groq (xAI) - محادثة ذكية
// ═══════════════════════════════════════════════════════════
app.post('/api/chat', async (req, res) => {
    const { message } = req.body;
    
    if (!message) {
        return res.status(400).json({ error: 'الرجاء إرسال رسالة' });
    }
    
    if (!GROQ_API_KEY) {
        return res.status(500).json({ error: 'API key not configured' });
    }
    
    try {
        const response = await fetch('https://api.x.ai/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${GROQ_API_KEY}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model: 'grok-4-1-fast',
                messages: [
                    { role: 'system', content: 'أنت مساعد ذكي لمتجر NEO PULSE HUB المتخصص في منتجات الذكاء الاصطناعي والتقنية. أجب بالعربية بلطف واحترافية.' },
                    { role: 'user', content: message }
                ],
                temperature: 0.7,
                max_tokens: 500
            })
        });
        
        const data = await response.json();
        const reply = data.choices?.[0]?.message?.content || 'عذراً، لم أستطع الرد حالياً';
        
        res.json({ reply });
        
    } catch (error) {
        console.error('❌ Groq API error:', error);
        res.status(500).json({ error: 'حدث خطأ في الخادم' });
    }
});

// ═══════════════════════════════════════════════════════════
// 📌 توصيات المنتجات (من متجرك)
// ═══════════════════════════════════════════════════════════
app.get('/api/recommendations', (req, res) => {
    try {
        let products = [];
        try {
            products = JSON.parse(fs.readFileSync('./products.json', 'utf8'));
        } catch(e) {}
        
        const recommendations = products.sort((a,b) => (b.rating||0) - (a.rating||0)).slice(0, 5);
        res.json(recommendations);
        
    } catch (error) {
        res.status(500).json({ error: 'فشل جلب التوصيات' });
    }
});

// ═══════════════════════════════════════════════════════════
// 📌 الاشتراك في النشرة البريدية
// ═══════════════════════════════════════════════════════════
app.post('/api/subscribe', (req, res) => {
    const { email } = req.body;
    
    if (!email || !email.includes('@')) {
        return res.status(400).json({ error: 'بريد إلكتروني غير صحيح' });
    }
    
    // حفظ البريد (مؤقتاً في ملف)
    let subscribers = [];
    try {
        subscribers = JSON.parse(fs.readFileSync('./subscribers.json', 'utf8'));
    } catch(e) {}
    
    if (!subscribers.includes(email)) {
        subscribers.push(email);
        fs.writeFileSync('./subscribers.json', JSON.stringify(subscribers, null, 2));
    }
    
    res.json({ success: true, message: 'تم الاشتراك بنجاح' });
});

// ═══════════════════════════════════════════════════════════
// 📌 إنشاء طلب (للتكامل مع CJ أو Amazon)
// ═══════════════════════════════════════════════════════════
app.post('/api/order', async (req, res) => {
    const orderData = req.body;
    console.log('📦 New order received:', orderData);
    
    // هنا تضيف كود إرسال الطلب لـ CJ أو Amazon
    res.json({ success: true, orderId: Date.now() });
});

// ═══════════════════════════════════════════════════════════
// 📌 تحليلات بسيطة
// ═══════════════════════════════════════════════════════════
app.get('/api/analytics', (req, res) => {
    let products = [];
    try {
        products = JSON.parse(fs.readFileSync('./products.json', 'utf8'));
    } catch(e) {}
    
    res.json({
        products_count: products.length,
        subscribers_count: 0,
        status: 'active'
    });
});

// ═══════════════════════════════════════════════════════════
// 📌 تشغيل الخادم
// ═══════════════════════════════════════════════════════════
const PORT = process.env.PORT || 10000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 Server running on port ${PORT}`);
    console.log(`✅ Health check: http://localhost:${PORT}/health`);
    console.log(`✅ Products API: http://localhost:${PORT}/api/products`);
});
