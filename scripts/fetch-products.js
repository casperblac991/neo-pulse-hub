#!/usr/bin/env node

/**
 * Amazon Product Fetcher for Neo Pulse Hub
 * Fetches products from Amazon Affiliate API and generates AI descriptions
 * Triggered hourly via OpenClaw scheduler
 */

const fs = require('fs');
const path = require('path');
const { OpenAI } = require('openai');

// The fetcher is opt-in. Never generate random/mock commercial products.
const openai = process.env.OPENAI_API_KEY
  ? new OpenAI({ apiKey: process.env.OPENAI_API_KEY })
  : null;

// Configuration
const CONFIG = {
  productsDir: path.join(__dirname, '../products'),
  logsDir: path.join(__dirname, '../logs'),
  affiliateTag: process.env.AMAZON_AFFILIATE_TAG || 'neopulsehub-20',
  maxProducts: 10, // Fetch up to 10 new products per run
  productCategories: [
    'electronics',
    'smart-home',
    'gadgets',
    'tech-accessories',
    'computers',
  ],
};

// Ensure directories exist
function ensureDirectories() {
  [CONFIG.productsDir, CONFIG.logsDir].forEach((dir) => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  });
}

async function fetchFromAmazon(category) {
  const endpoint = process.env.AMAZON_PRODUCTS_API_URL;
  if (!endpoint) {
    console.warn('[Fetcher] AMAZON_PRODUCTS_API_URL is not configured; no products fetched.');
    return [];
  }
  const url = new URL(endpoint);
  url.searchParams.set('category', category);
  const response = await fetch(url, {
    headers: {
      Accept: 'application/json',
      ...(process.env.AMAZON_PRODUCTS_API_KEY
        ? { Authorization: `Bearer ${process.env.AMAZON_PRODUCTS_API_KEY}` }
        : {}),
    },
  });
  if (!response.ok) throw new Error(`Product source returned HTTP ${response.status}`);
  const payload = await response.json();
  const products = Array.isArray(payload) ? payload : payload.products;
  if (!Array.isArray(products)) throw new Error('Product source must return an array or { products: [] }');
  return products.filter((product) => product && product.id && product.title && product.price != null);
}

// Generate AI-powered product description
async function generateProductDescription(product) {
  console.log(`[AI Generator] Generating description for: ${product.title}`);

  if (!openai) return { en: '', ar: '' };

  const prompt = `
Generate a comprehensive and engaging product description for an e-commerce store.
Make it 2000+ characters, professional, and persuasive.

Product Details:
- Title: ${product.title}
- Price: $${product.price}
- Rating: ${product.rating}/5 (${product.reviews} reviews)
- Category: ${product.category}
- Features: ${product.features.join(', ')}

Requirements:
1. Write in both Arabic and English (separate sections)
2. Include SEO keywords
3. Highlight key benefits
4. Add call-to-action
5. Include technical specifications
6. Mention customer reviews
7. Provide value proposition

Format the response as JSON with keys: "en" and "ar"
`;

  try {
    const response = await openai.chat.completions.create({
      model: 'gpt-4.1-mini',
      messages: [
        {
          role: 'user',
          content: prompt,
        },
      ],
      temperature: 0.7,
      max_tokens: 2000,
    });

    const content = response.choices[0].message.content;
    return JSON.parse(content);
  } catch (error) {
    console.error(`[Error] Failed to generate description:`, error.message);
    return { en: '', ar: '' };
  }
}

// Save product to JSON file
function saveProduct(product, descriptions) {
  const productData = {
    id: product.id,
    title: product.title,
    price: product.price,
    rating: product.rating,
    reviews: product.reviews,
    image: product.image,
    url: product.url,
    category: product.category,
    features: product.features,
    descriptions: descriptions,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };

  const filename = path.join(CONFIG.productsDir, `${product.id}.json`);
  fs.writeFileSync(filename, JSON.stringify(productData, null, 2));
  console.log(`[Saved] Product saved to: ${filename}`);

  return productData;
}

// Log execution
function logExecution(status, details) {
  const timestamp = new Date().toISOString();
  const logEntry = {
    timestamp,
    status,
    details,
  };

  const logFile = path.join(CONFIG.logsDir, `fetch-products-${new Date().toISOString().split('T')[0]}.log`);
  const existingLogs = fs.existsSync(logFile) ? JSON.parse(fs.readFileSync(logFile, 'utf-8')) : [];
  existingLogs.push(logEntry);
  fs.writeFileSync(logFile, JSON.stringify(existingLogs, null, 2));

  console.log(`[Log] Execution logged: ${status}`);
}

// Main execution
async function main() {
  try {
    console.log('🚀 [Fetcher] Starting Amazon product fetch cycle...');
    ensureDirectories();

    let totalFetched = 0;
    let totalProcessed = 0;

    // Fetch products from multiple categories
    for (const category of CONFIG.productCategories) {
      const products = await fetchFromAmazon(category);

      for (const product of products) {
        if (totalFetched >= CONFIG.maxProducts) break;

        // Generate AI description
        const descriptions = await generateProductDescription(product);

        // Save product
        saveProduct(product, descriptions);

        totalFetched++;
        totalProcessed++;
      }

      if (totalFetched >= CONFIG.maxProducts) break;
    }

    const successMessage = `Successfully fetched and processed ${totalProcessed} products`;
    console.log(`✅ [Success] ${successMessage}`);
    logExecution('success', {
      productsProcessed: totalProcessed,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('❌ [Error] Fetch cycle failed:', error.message);
    logExecution('error', {
      error: error.message,
      timestamp: new Date().toISOString(),
    });
    process.exit(1);
  }
}

// Run if executed directly
if (require.main === module) {
  main();
}

module.exports = { fetchFromAmazon, generateProductDescription, saveProduct };
