const express = require('express');
const fs = require('fs');
const fetch = require('node-fetch');
const path = require('path');
const app = express();

app.use(express.json());
app.use(express.static(path.join(__dirname))); // لخدمة ملفات HTML

// ═══════════════════════════════════════════════════════════
// 📌 قراءة المتغيرات البيئية (خزّنها في Render)
// ═══════════════════════════════════════════════════════════
const CJ_API_KEY = process.env.CJ_API_KEY;
const CJ_EMAIL = process.env.CJ_EMAIL;

// ═══════════════════════════════════════════════════════════
// 📌 API: جلب المنتجات المخزنة
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
// 📌 API: إنشاء طلب جديد (عند الشراء)
// ═══════════════════════════════════════════════════════════
app.post('/api/order', async (req, res) => {
  const orderData = req.body;
  console.log('📦 New order:', orderData);

  try {
    const response = await fetch('https://developers.cjdropshipping.com/api2.0/v1/order/create', {
      method: 'POST',
      headers: {
        'CJ-Access-Token': CJ_API_KEY,
        'Email': CJ_EMAIL,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(orderData)
    });
    const result = await response.json();
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: 'Order failed' });
  }
});

// ═══════════════════════════════════════════════════════════
// 📌 تحديث المنتجات من CJ كل 6 ساعات
// ═══════════════════════════════════════════════════════════
async function updateProducts() {
  try {
    const response = await fetch('https://developers.cjdropshipping.com/api2.0/v1/product/list', {
      headers: {
        'CJ-Access-Token': CJ_API_KEY,
        'Email': CJ_EMAIL
      }
    });
    const data = await response.json();
    fs.writeFileSync('./products.json', JSON.stringify(data.data || [], null, 2));
    console.log('✅ Products updated');
  } catch (error) {
    console.error('❌ Update failed:', error);
  }
}

updateProducts();
setInterval(updateProducts, 6 * 60 * 60 * 1000);

// ═══════════════════════════════════════════════════════════
// 📌 تشغيل الخادم
// ═══════════════════════════════════════════════════════════
const PORT = process.env.PORT || 10000;
app.listen(PORT, () => console.log(`🚀 Server on port ${PORT}`));
