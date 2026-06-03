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
// 📌 API: Search products by keyword
// ═══════════════════════════════════════════════════════════
app.get('/api/search', async (req, res) => {
  try {
    const { q } = req.query;
    if (!q) {
      return res.json([]);
    }
    
    const productsPath = path.join(__dirname, '..', 'products.json');
    const productsData = fs.readFileSync(productsPath, 'utf8');
    const products = JSON.parse(productsData);
    
    const query = q.toLowerCase();
    const results = products.filter(p => 
      p.name?.ar?.toLowerCase().includes(query) || 
      p.name?.en?.toLowerCase().includes(query) ||
      p.name?.toLowerCase().includes(query) ||
      p.category?.toLowerCase().includes(query)
    ).slice(0, 10);
    
    res.json(results);
  } catch (error) {
    console.error('❌ Error searching products:', error);
    res.status(500).json({ error: 'Failed to search products' });
  }
});

// ═══════════════════════════════════════════════════════════
// 📌 API: Get product by ID
// ═══════════════════════════════════════════════════════════
app.get('/api/products/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const productsPath = path.join(__dirname, '..', 'products.json');
    const productsData = fs.readFileSync(productsPath, 'utf8');
    const products = JSON.parse(productsData);
    
    const product = products.find(p => p.id === id);
    if (!product) {
      return res.status(404).json({ error: 'Product not found' });
    }
    
    res.json(product);
  } catch (error) {
    console.error('❌ Error fetching product:', error);
    res.status(500).json({ error: 'Failed to fetch product' });
  }
});

// ═══════════════════════════════════════════════════════════
// 📌 Health check
// ═══════════════════════════════════════════════════════════
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    products: 682, 
    timestamp: new Date().toISOString(),
    version: '1.0.0'
  });
});

// ═══════════════════════════════════════════════════════════
// 📌 Stats endpoint
// ═══════════════════════════════════════════════════════════
app.get('/api/stats', (req, res) => {
  res.json({
    totalProducts: 682,
    categories: 6,
    timestamp: new Date().toISOString(),
    server: 'NEO PULSE HUB Backend'
  });
});

// ═══════════════════════════════════════════════════════════
// 📌 Serve index.html for all other routes (SPA support)
// ═══════════════════════════════════════════════════════════
app.get('*', (req, res) => {
  const indexPath = path.join(__dirname, '..', 'index.html');
  res.sendFile(indexPath, (err) => {
    if (err) {
      console.error('❌ Error sending index.html:', err);
      res.status(500).send('Server error');
    }
  });
});

// ═══════════════════════════════════════════════════════════
// 📌 Error handler middleware
// ═══════════════════════════════════════════════════════════
app.use((err, req, res, next) => {
  console.error('❌ Unhandled error:', err);
  res.status(500).json({ 
    error: 'Internal server error',
    message: process.env.NODE_ENV === 'development' ? err.message : undefined
  });
});

// ═══════════════════════════════════════════════════════════
// 📌 تشغيل الخادم
// ═══════════════════════════════════════════════════════════
const PORT = process.env.PORT || 10000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 NEO PULSE HUB Server running on port ${PORT}`);
  console.log(`📦 Serving 682 products from static JSON`);
  console.log(`✅ /api/products - Get all products`);
  console.log(`✅ /api/search - Search products by keyword`);
  console.log(`✅ /api/products/:id - Get product by ID`);
  console.log(`✅ /health - Health check`);
  console.log(`✅ /api/stats - Server statistics`);
});

export default app;
