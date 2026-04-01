// server.js - تشغيل المدير مع API
const express = require('express');
const cors = require('cors');
const { NeoPulseManager } = require('./bot-manager');

const app = express();
app.use(cors());
app.use(express.json());

// تحميل المنتجات
const products = require('./products.json');

// إعدادات المدير
const manager = new NeoPulseManager({
  apiUrl: process.env.API_URL || 'https://neo-pulse-api.onrender.com',
  adminEmail: process.env.ADMIN_EMAIL || 'admin@neo-pulse-hub.it.com',
  products: products,
  contentUpdateInterval: 6 * 60 * 60 * 1000,
  syncInterval: 24 * 60 * 60 * 1000
});

// تشغيل المدير
manager.start();

// ============================================
// API Endpoints
// ============================================

// 1. شات بوت (موجود)
app.post('/api/chat', async (req, res) => {
  const { message, userId, userData } = req.body;
  const response = await manager.customerBot.handleMessage(userId, message, userData);
  manager.analyticsBot.trackQuestion(message);
  res.json({ success: true, answer: response });
});

// 2. توليد مقال
app.post('/api/generate-article', async (req, res) => {
  const { topic, language } = req.body;
  const article = await manager.contentBot.generateArticle({ title: topic }, language);
  res.json({ success: true, article });
});

// 3. توليد مراجعة منتج
app.post('/api/generate-review', async (req, res) => {
  const { productId, language } = req.body;
  const product = products.find(p => p.id === productId);
  if (!product) {
    return res.status(404).json({ success: false, error: 'Product not found' });
  }
  const review = await manager.contentBot.generateProductReview(product, language);
  res.json({ success: true, review });
});

// 4. توصيات منتجات
app.post('/api/recommend', async (req, res) => {
  const { preferences, budget } = req.body;
  const recommendations = manager.salesBot.recommendProducts(preferences, budget);
  res.json({ success: true, recommendations });
});

// 5. مقارنة منتجين
app.post('/api/compare', async (req, res) => {
  const { product1Id, product2Id } = req.body;
  const comparison = manager.salesBot.compareProducts(product1Id, product2Id);
  res.json({ success: true, comparison });
});

// 6. العروض
app.get('/api/deals', (req, res) => {
  const deals = manager.salesBot.getDeals();
  res.json({ success: true, deals });
});

// 7. تحليلات
app.get('/api/analytics', (req, res) => {
  const report = manager.analyticsBot.generateReport();
  res.json({ success: true, report });
});

// 8. حالة المدير
app.get('/api/status', (req, res) => {
  const status = manager.getStatus();
  res.json({ success: true, status });
});

// 9. مزامنة يدوية
app.post('/api/sync', async (req, res) => {
  const result = await manager.syncBot.syncProductsFromAmazon();
  res.json({ success: true, result });
});

// 10. تقرير فوري
app.get('/api/report', async (req, res) => {
  const result = await manager.reportBot.sendDailyReport();
  res.json({ success: true, result });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 NEO PULSE HUB AI Manager running on port ${PORT}`);
  console.log(`📊 Status: ${JSON.stringify(manager.getStatus(), null, 2)}`);
});
