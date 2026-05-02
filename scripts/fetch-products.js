#!/usr/bin/env node

/**
 * Amazon Product Fetcher for Neo Pulse Hub
 * Fetches products from Amazon Affiliate API and generates AI descriptions
 * Triggered hourly via OpenClaw scheduler
 */

const fs = require('fs');
const path = require('path');
const { OpenAI } = require('openai');

// Initialize OpenAI client
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

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

// Mock Amazon API call (replace with real API integration)
async function fetchFromAmazon(category) {
  console.log(`[Fetcher] Fetching products from category: ${category}`);

  // This is a mock implementation
  // In production, integrate with Amazon Product Advertising API
  const mockProducts = [
    {
      id: `PROD-${Date.now()}-1`,
      title: `Premium ${category} Device`,
      price: Math.floor(Math.random() * 500) + 50,
      rating: (Math.random() * 2 + 3).toFixed(1),
      reviews: Math.floor(Math.random() * 5000) + 100,
      image: `https://via.placeholder.com/300?text=${category}`,
      url: `https://amazon.com/s?k=${category}&tag=${CONFIG.affiliateTag}`,
      category: category,
      features: [
        'High quality',
        'Durable',
        'Fast shipping',
        'Great value',
      ],
    },
  ];

  return mockProducts;
}

// Generate AI-powered product description
async function generateProductDescription(product) {
  console.log(`[AI Generator] Generating description for: ${product.title}`);

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
    return {
      en: `${product.title} - Premium quality product at $${product.price}. Rated ${product.rating}/5 by ${product.reviews} customers.`,
      ar: `${product.title} - منتج عالي الجودة بسعر $${product.price}. تقييم ${product.rating}/5 من ${product.reviews} عميل.`,
    };
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
