const express = require('express');
const cors = require('cors');
const app = express();

app.use(cors({ origin: '*' }));
app.use(express.json());

// مفتاح Groq من المتغيرات (الموجود عندك)
const GROQ_API_KEY = process.env.GROQ_API_KEY;

// ============================================
// الاتصال بـ Groq API (ذكاء اصطناعي حقيقي)
// ============================================
async function getAIResponse(message) {
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
            content: `أنت مساعد ذكي لمتجر NEO PULSE HUB.
            
            المنتجات:
            - ساعات: Apple Watch Series 9 (399$), Samsung Galaxy Watch 6 (299$), Garmin Venu 3 (449$), Amazfit GTR 4 (149$)
            - سماعات: AirPods Pro 2 (249$), Sony WH-1000XM5 (349$), Galaxy Buds2 Pro (179$)
            - منزل ذكي: Echo Show 10 (249$), Nest Thermostat (129$), Philips Hue (179$)
            
            أجب بالعربية، مختصر، مفيد.`
          },
          { role: 'user', content: message }
        ],
        temperature: 0.7,
        max_tokens: 400
      })
    });
    
    const data = await response.json();
    return data.choices[0].message.content;
    
  } catch (error) {
    console.error('AI Error:', error.message);
    return null;
  }
}

// ============================================
// نقطة الشات
// ============================================
app.post('/api/chat', async (req, res) => {
  const { message } = req.body;
  console.log('📩:', message);
  
  const answer = await getAIResponse(message);
  
  res.json({ 
    success: true, 
    answer: answer || 'عذراً، حدث خطأ. حاول مرة أخرى.'
  });
});

// ============================================
// فحص الصحة
// ============================================
app.get('/api/status', (req, res) => {
  res.json({ 
    success: true, 
    ai: GROQ_API_KEY ? 'Groq ✅' : '❌',
    status: 'running'
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Server running on port ${PORT}`);
  console.log(`🤖 AI: ${GROQ_API_KEY ? 'Groq ✅' : '❌'}`);
});
