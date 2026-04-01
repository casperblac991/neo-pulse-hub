const express = require('express');
const cors = require('cors');
const app = express();

app.use(cors({ origin: '*' }));
app.use(express.json());

// 🔑 مفتاح Ollama (من المتغيرات)
const OLLAMA_API_KEY = process.env.OLLAMA_API_KEY;

// ============================================
// الاتصال بـ Ollama API
// ============================================
async function getOllamaResponse(message) {
  if (!OLLAMA_API_KEY) {
    console.log('❌ OLLAMA_API_KEY غير موجود');
    return null;
  }
  
  try {
    const response = await fetch('https://api.ollama.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${OLLAMA_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'llama3.2',
        messages: [
          {
            role: 'system',
            content: `أنت مساعد لمتجر NEO PULSE HUB للمنتجات التقنية.
            
            المنتجات المتوفرة:
            - Apple Watch Series 9: 399$، شريحة S9 مع Neural Engine للذكاء الاصطناعي
            - Samsung Galaxy Watch 6: 299$، Bixby AI مدمج
            - Garmin Venu 3: 449$، Coach AI للرياضة
            - Amazfit GTR 4: 149$، خيار اقتصادي
            - AirPods Pro 2: 249$، أفضل سماعة لآيفون
            - Sony WH-1000XM5: 349$، أفضل إلغاء ضوضاء
            
            أجب باختصار وبالعربية. استخدم إيموجيات.`
          },
          { role: 'user', content: message }
        ],
        temperature: 0.7,
        max_tokens: 500
      })
    });
    
    const data = await response.json();
    console.log('✅ Ollama رد:', data.choices?.[0]?.message?.content?.substring(0, 100));
    
    if (data.choices && data.choices[0]) {
      return data.choices[0].message.content;
    }
    
    return null;
    
  } catch (error) {
    console.error('❌ Ollama خطأ:', error.message);
    return null;
  }
}

// ============================================
// الردود الاحتياطية
// ============================================
function getFallbackResponse(message) {
  const msg = message.toLowerCase();
  
  if (msg.includes('ساعة') && (msg.includes('ذكاء') || msg.includes('ai'))) {
    return `⌚ **الساعات المدعومة بالذكاء الاصطناعي:**

1. **Apple Watch Series 9** - 399$
   🔹 شريحة S9 مع Neural Engine
   🔹 Siri تتعلم عاداتك

2. **Samsung Galaxy Watch 6** - 299$
   🔹 Bixby AI مدمج
   🔹 تتبع النوم بالذكاء الاصطناعي

3. **Garmin Venu 3** - 449$
   🔹 Coach AI لتحسين الأداء الرياضي

**الخلاصة:** آيفون → Apple Watch، أندرويد → Galaxy Watch`;
  }
  
  if (msg.includes('ساعة')) {
    return `⌚ **الساعات المتوفرة:**
• Apple Watch Series 9 - 399$
• Samsung Galaxy Watch 6 - 299$
• Garmin Venu 3 - 449$
• Amazfit GTR 4 - 149$`;
  }
  
  return `👋 مرحباً في NEO PULSE HUB!

أنا مساعدك الذكي، أساعدك في:
• اختيار الساعات الذكية
• مقارنة المنتجات
• معرفة الأسعار

جرب تسأل: "وش أفضل ساعة ذكية؟"`;
}

// ============================================
// نقطة الشات
// ============================================
app.post('/api/chat', async (req, res) => {
  try {
    const { message } = req.body;
    console.log(`📩 سؤال: ${message}`);
    
    let answer = await getOllamaResponse(message);
    
    if (!answer) {
      console.log('⚠️ استخدام الرد الاحتياطي');
      answer = getFallbackResponse(message);
    }
    
    res.json({ success: true, answer: answer });
    
  } catch (error) {
    res.json({ success: true, answer: getFallbackResponse(req.body.message) });
  }
});

// ============================================
// نقطة الفحص
// ============================================
app.get('/api/status', (req, res) => {
  res.json({ 
    success: true, 
    ollama_key: OLLAMA_API_KEY ? '✅ موجود' : '❌ غير موجود',
    status: 'running'
  });
});

// ============================================
// تشغيل الخادم
// ============================================
const PORT = process.env.PORT || 3000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 NEO PULSE HUB AI Manager running on port ${PORT}`);
  console.log(`🔑 Ollama Key: ${OLLAMA_API_KEY ? '✅ موجود' : '❌ غير موجود'}`);
});
