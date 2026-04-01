const express = require('express');
const cors = require('cors');
const app = express();

// ✅ CORS مفتوح
app.use(cors({ origin: '*' }));
app.use(express.json());

// ✅ مفتاح Ollama
const OLLAMA_API_KEY = process.env.OLLAMA_API_KEY;
const OLLAMA_URL = 'https://api.ollama.com/v1/chat/completions';

// ============================================
// قاعدة البيانات المحلية (احتياط)
// ============================================
const PRODUCTS_DB = {
  smartwatches: [
    { name: "Apple Watch Series 9", price: 399, features: "شاشة Always-On، مستشعرات صحية", bestFor: "مستخدمي آيفون" },
    { name: "Samsung Galaxy Watch 6", price: 299, features: "إطار دوار، مراقبة صحية", bestFor: "مستخدمي أندرويد" },
    { name: "Garmin Venu 3", price: 449, features: "GPS دقيق، بطارية 14 يوم", bestFor: "الرياضيين" },
    { name: "Amazfit GTR 4", price: 149, features: "GPS مدمج، بطارية 14 يوم", bestFor: "الميزانية المحدودة" }
  ],
  earbuds: [
    { name: "AirPods Pro 2", price: 249, features: "إلغاء ضوضاء، صوت مكاني", bestFor: "مستخدمي آيفون" },
    { name: "Sony WH-1000XM5", price: 349, features: "أفضل إلغاء ضوضاء", bestFor: "عشاق الصوت" }
  ]
};

// ============================================
// دالة الردود الاحتياطية (إذا فشل Ollama)
// ============================================
function getSmartResponse(message) {
  const msg = message.toLowerCase();
  
  if (msg.includes('ساعة') || msg.includes('watch')) {
    let response = "⌚ **الساعات الذكية المتوفرة:**\n\n";
    PRODUCTS_DB.smartwatches.forEach(p => {
      response += `• **${p.name}** - ${p.price}$\n   ✨ ${p.features}\n   👤 مناسب لـ: ${p.bestFor}\n\n`;
    });
    return response;
  }
  
  if (msg.includes('سماعة') || msg.includes('headphone')) {
    let response = "🎧 **السماعات المتوفرة:**\n\n";
    PRODUCTS_DB.earbuds.forEach(p => {
      response += `• **${p.name}** - ${p.price}$\n   ✨ ${p.features}\n   👤 مناسب لـ: ${p.bestFor}\n\n`;
    });
    return response;
  }
  
  return `شكراً لتواصلك مع NEO PULSE HUB! 😊\n\nأنا مساعدك الذكي، أقدر أساعدك في:\n⌚ الساعات الذكية\n🎧 السماعات\n🏠 المنزل الذكي\n❤️ الصحة الذكية\n💼 الإنتاجية\n\nجرب تسألني عن: "وش أفضل ساعة ذكية؟"`;
}

// ============================================
// دالة الاتصال بـ Ollama AI
// ============================================
async function getAIResponse(message) {
  if (!OLLAMA_API_KEY) {
    console.log('⚠️ OLLAMA_API_KEY not set');
    return null;
  }
  
  try {
    const response = await fetch(OLLAMA_URL, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${OLLAMA_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'llama3',
        messages: [
          {
            role: 'system',
            content: `أنت مساعد ذكي لمتجر NEO PULSE HUB للمنتجات التقنية.
            
            المنتجات المتوفرة:
            - ساعات ذكية: Apple Watch Series 9 (399$), Samsung Galaxy Watch 6 (299$), Garmin Venu 3 (449$), Amazfit GTR 4 (149$)
            - سماعات: AirPods Pro 2 (249$), Sony WH-1000XM5 (349$), Galaxy Buds2 Pro (179$), Beats Studio Pro (299$)
            - المنزل الذكي: Echo Show 10 (249$), Nest Thermostat (129$), Philips Hue (179$), Ring Doorbell (179$)
            - الصحة الذكية: Fitbit Charge 6 (149$), Oura Ring (299$), Withings Body+ (99$), Xiaomi Band 8 Pro (59$)
            - الإنتاجية: Logitech MX Master 3S (99$), Keychron K2 Pro (109$), iPad Pro M4 (999$)
            
            أجب على أسئلة الزوار بلباقة، اقترح منتجات مناسبة حسب احتياجهم، وقدم معلومات عن الأسعار والمميزات.
            خلي ردودك مختصرة ومفيدة، واستخدم إيموجيات مناسبة.`
          },
          { role: 'user', content: message }
        ],
        temperature: 0.7,
        max_tokens: 500
      })
    });
    
    const data = await response.json();
    return data.choices[0].message.content;
    
  } catch (error) {
    console.error('Ollama Error:', error.message);
    return null;
  }
}

// ============================================
// نقطة نهاية الشات
// ============================================
app.post('/api/chat', async (req, res) => {
  try {
    const { message } = req.body;
    
    if (!message) {
      return res.json({ success: false, answer: 'الرجاء كتابة سؤالك.' });
    }
    
    console.log(`📩 سؤال: ${message}`);
    
    let answer = await getAIResponse(message);
    
    if (!answer) {
      console.log('⚠️ باستخدام الردود الاحتياطية');
      answer = getSmartResponse(message);
    }
    
    res.json({ success: true, answer: answer });
    
  } catch (error) {
    console.error('❌ خطأ:', error);
    res.json({ success: false, answer: 'عذراً، حدث خطأ. حاول مرة أخرى.' });
  }
});

// ============================================
// نقطة نهاية التحقق
// ============================================
app.get('/api/status', (req, res) => {
  res.json({ 
    success: true, 
    status: {
      running: true,
      ollama: OLLAMA_API_KEY ? 'configured' : 'missing',
      uptime: process.uptime()
    }
  });
});

// ============================================
// تشغيل الخادم
// ============================================
const PORT = process.env.PORT || 3000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 NEO PULSE HUB AI Manager running on port ${PORT}`);
  console.log(`🔑 Ollama API Key: ${OLLAMA_API_KEY ? '✅ configured' : '❌ missing'}`);
});
