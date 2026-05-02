#!/usr/bin/env node

/**
 * Blog Content Generator for Neo Pulse Hub
 * Generates comprehensive blog posts about products
 * Triggered daily via OpenClaw scheduler
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
  blogDir: path.join(__dirname, '../blog'),
  productsDir: path.join(__dirname, '../products'),
  logsDir: path.join(__dirname, '../logs'),
  postsPerDay: 2,
};

// Ensure directories exist
function ensureDirectories() {
  [CONFIG.blogDir, CONFIG.logsDir].forEach((dir) => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  });
}

// Get random products for blog posts
function getRandomProducts(count) {
  const productFiles = fs.readdirSync(CONFIG.productsDir).filter(f => f.endsWith('.json'));
  const shuffled = productFiles.sort(() => Math.random() - 0.5);
  const selected = shuffled.slice(0, count);

  return selected.map(file => {
    const content = fs.readFileSync(path.join(CONFIG.productsDir, file), 'utf-8');
    return JSON.parse(content);
  });
}

// Generate blog post content using AI
async function generateBlogPost(product, language = 'en') {
  console.log(`[AI Writer] Generating ${language} blog post for: ${product.title}`);

  const languagePrompt = language === 'ar' ? 'Arabic' : 'English';

  const prompt = `
Generate a comprehensive and engaging blog post for an e-commerce website.
The post should be 2000+ words, SEO-optimized, and include multiple sections.

Product Details:
- Title: ${product.title}
- Price: $${product.price}
- Rating: ${product.rating}/5 (${product.reviews} reviews)
- Category: ${product.category}
- Features: ${product.features.join(', ')}
- Description: ${product.descriptions[language === 'ar' ? 'ar' : 'en']}

Blog Post Requirements:
1. Write in ${languagePrompt}
2. Include SEO keywords naturally
3. Create an engaging headline
4. Write an introduction section
5. Include 5-7 main sections with subheadings
6. Add comparison with competitors
7. Include customer testimonials (mock if needed)
8. Add pros and cons section
9. Include technical specifications
10. End with a strong call-to-action
11. Add internal links suggestions
12. Include meta description (160 chars)

Format the response as JSON with keys:
- "title": Blog post title
- "metaDescription": SEO meta description
- "content": Full blog post content (markdown format)
- "keywords": Array of 10 SEO keywords
- "internalLinks": Array of suggested internal links
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
      max_tokens: 3000,
    });

    const content = response.choices[0].message.content;
    return JSON.parse(content);
  } catch (error) {
    console.error(`[Error] Failed to generate blog post:`, error.message);
    return {
      title: `Complete Guide to ${product.title}`,
      metaDescription: `Learn everything about ${product.title}. Rated ${product.rating}/5 by ${product.reviews} customers.`,
      content: `# ${product.title}\n\n${product.descriptions[language === 'ar' ? 'ar' : 'en']}\n\n## Price: $${product.price}\n\n## Rating: ${product.rating}/5`,
      keywords: [product.title, product.category, 'review', 'guide', 'best'],
      internalLinks: [],
    };
  }
}

// Save blog post as markdown
function saveBlogPost(product, blogData, language) {
  const slug = blogData.title
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');

  const filename = path.join(CONFIG.blogDir, `${slug}-${language}-${Date.now()}.md`);

  const markdownContent = `---
title: ${blogData.title}
description: ${blogData.metaDescription}
keywords: ${blogData.keywords.join(', ')}
language: ${language}
productId: ${product.id}
createdAt: ${new Date().toISOString()}
---

# ${blogData.title}

${blogData.content}

## Internal Links
${blogData.internalLinks.map(link => `- [${link.text}](${link.url})`).join('\n')}

---

**Last Updated**: ${new Date().toISOString()}
`;

  fs.writeFileSync(filename, markdownContent);
  console.log(`[Saved] Blog post saved to: ${filename}`);

  return {
    filename,
    slug,
    language,
  };
}

// Generate social media snippet
async function generateSocialSnippet(product, platform = 'telegram') {
  console.log(`[Social Generator] Creating ${platform} snippet for: ${product.title}`);

  const prompt = `
Create a short, engaging social media post for ${platform}.
Keep it under 280 characters.
Include relevant emojis.
Add a call-to-action.
Include the product price and rating.

Product: ${product.title}
Price: $${product.price}
Rating: ${product.rating}/5
Category: ${product.category}

Return only the social media post text.
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
      temperature: 0.8,
      max_tokens: 100,
    });

    return response.choices[0].message.content;
  } catch (error) {
    console.error(`[Error] Failed to generate social snippet:`, error.message);
    return `🎉 Check out ${product.title}! ⭐${product.rating}/5 | $${product.price} | Shop now! 🛍️`;
  }
}

// Log execution
function logExecution(status, details) {
  const timestamp = new Date().toISOString();
  const logEntry = {
    timestamp,
    status,
    details,
  };

  const logFile = path.join(CONFIG.logsDir, `generate-content-${new Date().toISOString().split('T')[0]}.log`);
  const existingLogs = fs.existsSync(logFile) ? JSON.parse(fs.readFileSync(logFile, 'utf-8')) : [];
  existingLogs.push(logEntry);
  fs.writeFileSync(logFile, JSON.stringify(existingLogs, null, 2));

  console.log(`[Log] Execution logged: ${status}`);
}

// Main execution
async function main() {
  try {
    console.log('📝 [Writer] Starting blog content generation cycle...');
    ensureDirectories();

    // Check if products exist
    if (!fs.existsSync(CONFIG.productsDir)) {
      throw new Error('Products directory not found. Run fetch-products.js first.');
    }

    const productFiles = fs.readdirSync(CONFIG.productsDir).filter(f => f.endsWith('.json'));
    if (productFiles.length === 0) {
      throw new Error('No products found. Run fetch-products.js first.');
    }

    const products = getRandomProducts(CONFIG.postsPerDay);
    let postsGenerated = 0;
    const generatedPosts = [];

    for (const product of products) {
      // Generate blog posts in both languages
      for (const language of ['en', 'ar']) {
        const blogData = await generateBlogPost(product, language);
        const savedPost = saveBlogPost(product, blogData, language);
        generatedPosts.push(savedPost);
        postsGenerated++;

        // Generate social media snippet
        const socialSnippet = await generateSocialSnippet(product, 'telegram');
        console.log(`[Social] ${language}: ${socialSnippet}`);
      }
    }

    const successMessage = `Successfully generated ${postsGenerated} blog posts`;
    console.log(`✅ [Success] ${successMessage}`);
    logExecution('success', {
      postsGenerated,
      posts: generatedPosts,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('❌ [Error] Content generation failed:', error.message);
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

module.exports = { generateBlogPost, saveBlogPost, generateSocialSnippet };
