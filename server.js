// server.js - خادم المدير الذكي لـ NEO PULSE HUB
const express = require('express');
const cors = require('cors');
const axios = require('axios');

const app = express();

// ✅ حل مشكلة CORS بشكل كامل (يسمح لأي موقع)
app.use(cors({
  origin: '*'
}));

app.use(express.json());

// ============================================
// معرفة المنتجات (من موقعك)
// ============================================
const PRODUCTS_DB = {
  smartwatches: [
    { name: "Apple Watch Series 9", price: 399, category: "ساعات ذكية", features: "شاشة Always-On، مستشعرات صحية متقدمة", bestFor: "مستخدمي آيفون" },
    { name: "Samsung Galaxy Watch 6", price: 299, category: "ساعات ذكية", features: "إطار دوار، مراقبة صحية دقيقة", bestFor: "مستخدمي أندرويد" },
    { name: "Garmin Venu 3", price: 449, category: "ساعات ذكية", features: "GPS دقيق، بطارية 14 يوم", bestFor: "الرياضيين" },
    { name: "Amazfit GTR 4", price: 149, category: "ساعات ذكية", features: "GPS مدمج، بطارية 14 يوم", bestFor: "الميزانية المحدودة" }
  ],
  earbuds: [
    { name: "AirPods Pro 2", price: 249, category: "سماعات", features: "إلغاء ضوضاء فعال، صوت مكاني", bestFor: "مستخدمي آيفون" },
    { name: "Sony WH-1000XM5", price: 349, category: "سماعات", features: "أفضل إلغاء ضوضاء، 30 ساعة بطارية", bestFor: "عشاق الصوت" },
    { name: "Galaxy Buds2 Pro", price: 179, category: "سماعات", features: "صوت Hi-Fi 24bit، إلغاء ضوضاء", bestFor: "مستخدمي أندرويد" },
    { name: "Beats Studio Pro", price: 299, category: "سماعات", features: "ANC، صوت عالي الدقة", bestFor: "مستخدمي Apple و Android" }
  ],
  smartHome: [
    { name: "Echo Show 10", price: 249, category: "منزل ذكي", features: "شاشة دوارة، Alexa مدمج", bestFor: "التحكم الصوتي" },
    { name: "Nest Thermostat", price: 129, category: "منزل ذكي", features: "توفير الطاقة، تعلم العادات", bestFor: "توفير الكهرباء" },
    { name: "Philips Hue Kit", price: 179, category: "منزل ذكي", features: "16 مليون لون، تحكم بالصوت", bestFor: "إضاءة ذكية" },
    { name: "Ring Doorbell 4", price: 179, category: "منزل ذكي", features: "كاميرا 1080HD، كشف حركة", bestFor: "أمان المنزل" }
  ],
  health: [
    { name: "Fitbit Charge 6", price: 149, category: "صحة ذكية", features: "GPS مدمج، تتبع نوم متقدم", bestFor: "متابعة اللياقة" },
    { name: "Oura Ring Gen 3", price: 299, category: "صحة ذكية", features: "تتبع نوم، نشاط، صحة", bestFor: "تتبع صحي بدون شاشة" },
    { name: "Withings Body+", price: 99, category: "صحة ذكية", features: "وزن، دهون، عضلات", bestFor: "مراقبة الوزن" },
    { name: "Xiaomi Band 8 Pro", price: 59, category: "صحة ذكية", features: "AMOLED، 150+ رياضة", bestFor: "الميزانية المحدودة" }
  ],
  productivity: [
    { name: "Logitech MX Master 3S", price: 99, category: "إنتاجية", features: "عجلة صامتة، بطارية 70 يوم", bestFor: "المحترفين" },
    { name: "Keychron K2 Pro", price: 109, category: "إنتاجية", features: "ميكانيكي، لاسلكي، RGB", bestFor: "الكتابة والبرمجة" },
    { name: "iPad Pro M4", price: 999, category: "إنتاجية", features: "شريحة M4، شاشة Ultra Retina", bestFor: "الإبداع والإنتاجية" }
  ]
};

// ============================================
// نظام الردود الذكي
// ============================================
function getSmartResponse(message) {
  const msg = message.toLowerCase();
  
  // ساعات ذكية
  if (msg.includes('ساعة') || msg.includes('watch') || msg.includes('سوار')) {
    let response = "⌚ **الساعات الذكية المتوفرة:**\n\n";
    PRODUCTS_DB.smartwatches.forEach(p => {
      response += `• **${p.name}** - ${p.price}$\n   ✨ ${p.features}\n   👤 مناسب لـ: ${p.bestFor}\n\n`;
    });
    return response;
  }
  
  // سماعات
  if (msg.includes('سماعة') || msg.includes('headphone') || msg.includes('earbuds')) {
    let response = "🎧 **السماعات المتوفرة:**\n\n";
    PRODUCTS_DB.earbuds.forEach(p => {
      response += `• **${p.name}** - ${p.price}$\n   ✨ ${p.features}\n   👤 مناسب لـ: ${p.bestFor}\n\n`;
    });
    return response;
  }
  
  // منزل ذكي
  if (msg.includes('منزل') || msg.includes('smart home') || msg.includes('echo')) {
    let response = "🏠 **منتجات المنزل الذكي:**\n\n";
    PRODUCTS_DB.smartHome.forEach(p => {
      response += `• **${p.name}** - ${p.price}$\n   ✨ ${p.features}\n   👤 مناسب لـ: ${p.bestFor}\n\n`;
    });
    return response;
  }
  
  // صحة ذكية
  if (msg.includes('صحة') || msg.includes('health') || msg.includes('fitbit')) {
    let response = "❤️ **منتجات الصحة الذكية:**\n\n";
    PRODUCTS_DB.health.forEach(p => {
      response += `• **${p.name}** - ${p.price}$\n   ✨ ${p.features}\n   👤 مناسب لـ: ${p.bestFor}\n\n`;
    });
    return response;
  }
  
  // إنتاجية
  if (msg.includes('ماوس') || msg.includes('كيبورد') || msg.includes('mouse')) {
    let response = "💼 **منتجات الإنتاجية:**\n\n";
    PRODUCTS_DB.productivity.forEach(p => {
      response += `• **${p.name}** - ${p.price}$\n   ✨ ${p.features}\n   👤 مناسب لـ: ${p.bestFor}\n\n`;
    });
    return response;
  }
  
  // أسعار
  if (msg.includes('سعر') || msg.includes('كم') || msg.includes('دولار')) {
    return `💰 **فئات الأسعار:**\n\n• أقل من 100$: Xiaomi Band 8 Pro (59$)\n• 100-200$: Amazfit GTR 4 (149$)\n• 200-300$: Galaxy Watch 6 (299$)\n• أكثر من 300$: Apple Watch Series 9 (399$)`;
  }
  
  // شحن
  if (msg.includes('شحن') || msg.includes('توصيل')) {
    return `🚚 **معلومات الشحن:**\n\n• جميع المنتجات تشحن من أمازون\n• شحن سريع لجميع الدول العربية\n• يمكنك تتبع الطلب من حساب أمازون\n• سياسة الإرجاع 30 يوم`;
  }
  
  // ضمان
  if (msg.includes('ضمان')) {
    return `🛡️ **الضمان:**\n\n• جميع المنتجات أصلية 100%\n• ضمان المصنع شامل\n• الإرجاع خلال 30 يوم\n• دعم فني عبر التيليجرام`;
  }
  
  // تحية
  if (msg.includes('السلام') || msg.includes('مرحب') || msg.includes('هلا')) {
    return `👋 وعليكم السلام ورحمة الله!\n\nأنا مساعد NEO PULSE HUB الذكي. أقدر أساعدك في:\n• اختيار المنتجات المناسبة\n• مقارنة المنتجات\n• الأسعار والعروض\n• الشحن والضمان\n\nوش تبحث عنه اليوم؟`;
  }
  
  // الرد الافتراضي
  return `شكراً لتواصلك مع NEO PULSE HUB! 😊\n\nأنا مساعدك الذكي، أقدر أساعدك في:\n\n⌚ **الساعات الذكية** - Apple, Samsung, Garmin\n🎧 **السماعات** - AirPods, Sony, Galaxy Buds\n🏠 **المنزل الذكي** - Echo, Nest, Philips Hue\n❤️ **الصحة الذكية** - Fitbit, Oura, Xiaomi\n💼 **الإنتاجية** - Logitech, Keychron, iPad\n\n**جرب تسألني عن:**\n• "وش أفضل ساعة ذكية؟"\n• "أبي سماعة للجيم"\n• "قارن Apple Watch و Galaxy Watch"`;
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
    const answer = getSmartResponse(message);
    console.log(`🤖 رد: ${answer.substring(0, 100)}...`);
    
    res.json({ success: true, answer: answer });
    
  } catch (error) {
    console.error('❌ خطأ:', error);
    res.json({ success: false, answer: 'عذراً، حدث خطأ. حاول مرة أخرى.' });
  }
});

// ============================================
// نقطة نهاية للتحقق من صحة الخادم
// ============================================
app.get('/api/status', (req, res) => {
  res.json({ 
    success: true, 
    status: {
      running: true,
      uptime: process.uptime(),
      bots: {
        customer: "active",
        content: "active",
        analytics: "active",
        sales: "active",
        sync: "active",
        report: "active"
      }
    }
  });
});

// ============================================
// نقطة نهاية العروض
// ============================================
app.get('/api/deals', (req, res) => {
  const deals = [
    { name: "Xiaomi Band 8 Pro", price: 59, original: 79, discount: 25 },
    { name: "Amazfit GTR 4", price: 149, original: 199, discount: 25 },
    { name: "Galaxy Buds2 Pro", price: 179, original: 229, discount: 22 }
  ];
  res.json({ success: true, deals });
});

// ============================================
// نقطة نهاية توصيات
// ============================================
app.post('/api/recommend', (req, res) => {
  const { budget } = req.body;
  let recommendations = PRODUCTS_DB.smartwatches;
  if (budget) {
    recommendations = recommendations.filter(p => p.price <= budget);
  }
  res.json({ success: true, recommendations: recommendations.slice(0, 3) });
});

// ============================================
// تشغيل الخادم
// ============================================
const PORT = process.env.PORT || 3000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 NEO PULSE HUB AI Manager running on port ${PORT}`);
  console.log(`📊 Status: ${JSON.stringify({ running: true, uptime: 0 }, null, 2)}`);
});
