const express = require('express');
const fs = require('fs');
const fetch = require('node-fetch');
const app = express();

app.use(express.json());

// ═══════════════════════════════════════════════════════════
// 📌 قراءة مفتاح Apify من متغيرات البيئة (آمن)
// ═══════════════════════════════════════════════════════════
const APIFY_API_TOKEN = process.env.APIFY_API_TOKEN;

if (!APIFY_API_TOKEN) {
  console.error('❌ APIFY_API_TOKEN not found in environment variables!');
}

// ═══════════════════════════════════════════════════════════
// 📌 API: جلب المنتجات
// ═══════════════════════════════════════════════════════════
app.get('/api/products', async (req, res) => {
  try {
    // محاولة قراءة المنتجات المخزنة
    let products = [];
    try {
      products = JSON.parse(fs.readFileSync('./products.json', 'utf8'));
      if (products.length > 0) {
        return res.json(products);
      }
    } catch (e) {}
    
    // جلب منتجات جديدة
    products = await fetchFromApify();
    fs.writeFileSync('./products.json', JSON.stringify(products, null, 2));
    res.json(products);
    
  } catch (error) {
    console.error('❌ Error:', error);
    res.json(getDemoProducts());
  }
});

// ═══════════════════════════════════════════════════════════
// 📌 جلب منتجات من AliExpress عبر Apify
// ═══════════════════════════════════════════════════════════
async function fetchFromApify() {
  if (!APIFY_API_TOKEN) return getDemoProducts();
  
  const products = [];
  const categories = [
    { name: 'smartwatch', search: 'smart watch', category_ar: 'ساعات ذكية', category_en: 'Smartwatches' },
    { name: 'earbuds', search: 'wireless earbuds', category_ar: 'سماعات لاسلكية', category_en: 'Wireless Earbuds' },
    { name: 'smart-glasses', search: 'smart glasses', category_ar: 'نظارات ذكية', category_en: 'Smart Glasses' }
  ];
  
  for (const cat of categories) {
    try {
      const url = `https://api.apify.com/v2/acts/logical_scrapers~aliexpress-scraper/runs?token=${APIFY_API_TOKEN}`;
      
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          search_urls: [`https://www.aliexpress.com/w/wholesale-${cat.search}.html`],
          maxItems: 5
        })
      });
      
      const runData = await response.json();
      
      if (runData.data && runData.data.defaultDatasetId) {
        const resultsResponse = await fetch(`https://api.apify.com/v2/datasets/${runData.data.defaultDatasetId}/items?token=${APIFY_API_TOKEN}`);
        const items = await resultsResponse.json();
        
        for (const item of items) {
          products.push({
            id: item.productId || `APIFY-${Date.now()}-${products.length}`,
            name: { ar: item.title || cat.search, en: item.title || cat.search },
            price: parseFloat(item.price) || 29.99,
            original_price: parseFloat(item.originalPrice) || (parseFloat(item.price) * 1.3) || 39.99,
            rating: item.rating || 4.5,
            reviews: item.reviewsCount || 100,
            image: item.mainImageUrl || `https://via.placeholder.com/300?text=${cat.search}`,
            category: cat.name,
            category_ar: cat.category_ar,
            category_en: cat.category_en,
            in_stock: true,
            featured: true
          });
        }
      }
      
      await new Promise(r => setTimeout(r, 2000));
      
    } catch (err) {
      console.error(`Error fetching ${cat.name}:`, err);
    }
  }
  
  return products.length > 0 ? products : getDemoProducts();
}

// ═══════════════════════════════════════════════════════════
// 📌 منتجات تجريبية (احتياطي)
// ═══════════════════════════════════════════════════════════
function getDemoProducts() {
  return [
    {
      id: "DEMO-001",
      name: { ar: "ساعة ذكية فائقة الجودة", en: "Premium Smart Watch" },
      price: 49.99,
      original_price: 99.99,
      rating: 4.8,
      reviews: 1234,
      image: "https://via.placeholder.com/300?text=Smart+Watch",
      category: "smartwatch",
      category_ar: "ساعات ذكية",
      category_en: "Smartwatches",
      in_stock: true,
      featured: true
    },
    {
      id: "DEMO-002",
      name: { ar: "سماعات لاسلكية", en: "Wireless Earbuds" },
      price: 29.99,
      original_price: 59.99,
      rating: 4.6,
      reviews: 856,
      image: "https://via.placeholder.com/300?text=Earbuds",
      category: "earbuds",
      category_ar: "سماعات",
      category_en: "Earbuds",
      in_stock: true,
      featured: true
    },
    {
      id: "DEMO-003",
      name: { ar: "نظارة واقع معزز", en: "AR Glasses" },
      price: 199.99,
      original_price: 299.99,
      rating: 4.7,
      reviews: 432,
      image: "https://via.placeholder.com/300?text=AR+Glasses",
      category: "smart-glasses",
      category_ar: "نظارات ذكية",
      category_en: "Smart Glasses",
      in_stock: true,
      featured: true
    }
  ];
}

// ═══════════════════════════════════════════════════════════
// 📌 تحديث المنتجات كل 12 ساعة
// ═══════════════════════════════════════════════════════════
async function refreshProducts() {
  console.log('🔄 Refreshing products...');
  const products = await fetchFromApify();
  fs.writeFileSync('./products.json', JSON.stringify(products, null, 2));
  console.log(`✅ Products refreshed: ${products.length} products`);
}

setTimeout(refreshProducts, 10000);
setInterval(refreshProducts, 12 * 60 * 60 * 1000);

// ═══════════════════════════════════════════════════════════
// 📌 تشغيل الخادم
// ═══════════════════════════════════════════════════════════
const PORT = process.env.PORT || 10000;
app.listen(PORT, '0.0.0.0', () => console.log(`🚀 Server on port ${PORT}`));
