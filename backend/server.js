import express from 'express';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();

app.use(express.json());

// ═══════════════════════════════════════════════════════════
// 📌 Serve static files from root directory (not just backend)
// ═══════════════════════════════════════════════════════════
app.use(express.static(path.join(__dirname, '..')));

// ═══════════════════════════════════════════════════════════
// 📌 API: جلب المنتجات من ملف JSON الثابت (682 منتج)
// ═══════════════════════════════════════════════════════════
app.get('/api/products', async (req, res) => {
  try {
    const productsPath = path.join(__dirname, '..', 'products.json');
    const productsData = fs.readFileSync(productsPath, 'utf8');
    const products = JSON.parse(productsData);
    console.log(`📦 Serving ${products.length} products from static JSON`);
    res.json(products);
  } catch (error) {
    console.error('❌ Error loading products:', error);
    res.status(500).json({ error: 'Failed to load products' });
  }
});

// ═══════════════════════════════════════════════════════════
// 📌 Health check
// ═══════════════════════════════════════════════════════════
app.get('/health', (req, res) => {
  res.json({ status: 'ok', products: 682, timestamp: new Date().toISOString() });
});

// ═══════════════════════════════════════════════════════════
// 📌 Serve index.html for all other routes (SPA support)
// ═══════════════════════════════════════════════════════════
app.get('*', (req, res) => {
  const indexPath = path.join(__dirname, '..', 'index.html');
  res.sendFile(indexPath);
});

// ═══════════════════════════════════════════════════════════
// 📌 تشغيل الخادم
// ═══════════════════════════════════════════════════════════
const PORT = process.env.PORT || 10000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 NEO PULSE HUB Server running on port ${PORT}`);
  console.log(`📦 Serving 682 products from static JSON`);
});

export default app;
