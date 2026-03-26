const express = require('express');
const fs = require('fs');
const fetch = require('node-fetch');
const app = express();

app.use(express.json());

// ═══════════════════════════════════════════════════════════
// 📌 API: جلب المنتجات المخزنة (يستخدمه المتجر)
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
        'CJ-Access-Token': process.env.CJ_API_KEY,
        'Email': process.env.CJ_EMAIL,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(orderData)
    });
    const result = await response.json();
    res.json(result);
  } catch (error) {
    console.error('❌ Order error:', error);
    res.status(500).json({ error: 'Order failed' });
  }
});

// ═══════════════════════════════════════════════════════════
// 📌 تحديث المنتجات من CJ API (كل 6 ساعات)
// ═══════════════════════════════════════════════════════════
async function updateProducts() {
  console.log('🔄 Fetching products from CJ API...');
  try {
    // استخدام POST مع body (كما هو موثق في CJ API)
    const response = await fetch('https://developers.cjdropshipping.com/api2.0/v1/product/list', {
      method: 'POST',
      headers: {
        'CJ-Access-Token': process.env.CJ_API_KEY,
        'Email': process.env.CJ_EMAIL,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        pageNum: 1,
        pageSize: 20,
        category: "Consumer Electronics" // الفئة الرئيسية للمنتجات التقنية
      })
    });
    
    const data = await response.json();
    
    if (data && data.data && data.data.length > 0) {
      fs.writeFileSync('./products.json', JSON.stringify(data.data, null, 2));
      console.log(`✅ Products updated: ${data.data.length} products`);
    } else {
      console.log('⚠️ No products found in response:', data);
      fs.writeFileSync('./products.json', JSON.stringify([], null, 2));
    }
  } catch (error) {
    console.error('❌ Update failed:', error);
  }
}

// تشغيل التحديث أول مرة
updateProducts();

// ثم كل 6 ساعات
setInterval(updateProducts, 6 * 60 * 60 * 1000);

// ═══════════════════════════════════════════════════════════
// 📌 تشغيل الخادم
// ═══════════════════════════════════════════════════════════
const PORT = process.env.PORT || 10000;
app.listen(PORT, () => console.log(`🚀 Server on port ${PORT}`));
