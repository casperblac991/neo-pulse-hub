#!/usr/bin/env node

/**
 * Social Media Publisher for Neo Pulse Hub
 * Publishes marketing campaigns to Telegram
 * Triggered by OpenClaw scheduler or on-demand
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

// Configuration
const CONFIG = {
  telegramBotToken: process.env.TELEGRAM_BOT_TOKEN,
  telegramChannelId: process.env.TELEGRAM_CHANNEL_ID || '@noepulsehub_bot',
  productsDir: path.join(__dirname, '../products'),
  logsDir: path.join(__dirname, '../logs'),
  postsPerCycle: 5,
};

// Ensure directories exist
function ensureDirectories() {
  if (!fs.existsSync(CONFIG.logsDir)) {
    fs.mkdirSync(CONFIG.logsDir, { recursive: true });
  }
}

// Send HTTP request to Telegram Bot API
function sendTelegramRequest(method, params) {
  return new Promise((resolve, reject) => {
    const url = `https://api.telegram.org/bot${CONFIG.telegramBotToken}/${method}`;

    const postData = JSON.stringify(params);

    const options = {
      hostname: 'api.telegram.org',
      path: `/bot${CONFIG.telegramBotToken}/${method}`,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData),
      },
    };

    const req = https.request(options, (res) => {
      let data = '';

      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          reject(new Error(`Failed to parse response: ${data}`));
        }
      });
    });

    req.on('error', reject);
    req.write(postData);
    req.end();
  });
}

// Get random products for posting
function getRandomProducts(count) {
  const productFiles = fs.readdirSync(CONFIG.productsDir).filter(f => f.endsWith('.json'));
  if (productFiles.length === 0) {
    throw new Error('No products found');
  }

  const shuffled = productFiles.sort(() => Math.random() - 0.5);
  const selected = shuffled.slice(0, count);

  return selected.map(file => {
    const content = fs.readFileSync(path.join(CONFIG.productsDir, file), 'utf-8');
    return JSON.parse(content);
  });
}

// Format product as Telegram message
function formatProductMessage(product) {
  const affiliateUrl = `${product.url}?tag=${process.env.AMAZON_AFFILIATE_TAG || 'neopulsehub-20'}`;

  const message = `
🎯 *${product.title}*

⭐ Rating: ${product.rating}/5 (${product.reviews} reviews)
💰 Price: $${product.price}

📝 ${product.descriptions.en.substring(0, 200)}...

🔗 [View Product](${affiliateUrl})

#${product.category.replace(/[^a-z0-9]/g, '')} #neopulsehub #deals
`;

  return message;
}

// Send product message to Telegram
async function sendProductMessage(product) {
  console.log(`[Telegram] Sending message for: ${product.title}`);

  const message = formatProductMessage(product);

  try {
    const response = await sendTelegramRequest('sendMessage', {
      chat_id: CONFIG.telegramChannelId,
      text: message,
      parse_mode: 'Markdown',
      disable_web_page_preview: false,
    });

    if (response.ok) {
      console.log(`✅ [Telegram] Message sent successfully`);
      return {
        success: true,
        messageId: response.result.message_id,
        product: product.id,
      };
    } else {
      throw new Error(`Telegram API error: ${response.description}`);
    }
  } catch (error) {
    console.error(`❌ [Telegram] Failed to send message:`, error.message);
    return {
      success: false,
      error: error.message,
      product: product.id,
    };
  }
}

// Send promotional campaign
async function sendPromotionalCampaign() {
  console.log(`[Campaign] Starting promotional campaign...`);

  const campaignMessage = `
🎉 *DAILY DEALS ALERT* 🎉

Check out today's hottest products! 🔥

Don't miss these amazing offers:
✨ Premium quality
✨ Best prices
✨ Fast shipping
✨ Money-back guarantee

Browse our latest collection now! 👇

#neopulsehub #dailydeals #shopping
`;

  try {
    await sendTelegramRequest('sendMessage', {
      chat_id: CONFIG.telegramChannelId,
      text: campaignMessage,
      parse_mode: 'Markdown',
    });

    console.log(`✅ [Campaign] Promotional message sent`);
    return { success: true };
  } catch (error) {
    console.error(`❌ [Campaign] Failed to send campaign:`, error.message);
    return { success: false, error: error.message };
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

  const logFile = path.join(CONFIG.logsDir, `publish-social-${new Date().toISOString().split('T')[0]}.log`);
  const existingLogs = fs.existsSync(logFile) ? JSON.parse(fs.readFileSync(logFile, 'utf-8')) : [];
  existingLogs.push(logEntry);
  fs.writeFileSync(logFile, JSON.stringify(existingLogs, null, 2));

  console.log(`[Log] Execution logged: ${status}`);
}

// Main execution
async function main() {
  try {
    console.log('📱 [Publisher] Starting social media publication cycle...');
    ensureDirectories();

    if (!CONFIG.telegramBotToken) {
      throw new Error('TELEGRAM_BOT_TOKEN environment variable not set');
    }

    // Send promotional campaign
    await sendPromotionalCampaign();

    // Add delay between messages
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Get and send product messages
    const products = getRandomProducts(CONFIG.postsPerCycle);
    const results = [];

    for (const product of products) {
      const result = await sendProductMessage(product);
      results.push(result);

      // Add delay between messages to avoid rate limiting
      await new Promise(resolve => setTimeout(resolve, 1000));
    }

    const successCount = results.filter(r => r.success).length;
    const successMessage = `Successfully published ${successCount}/${results.length} posts`;
    console.log(`✅ [Success] ${successMessage}`);
    logExecution('success', {
      postsPublished: successCount,
      totalAttempts: results.length,
      results,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('❌ [Error] Social media publication failed:', error.message);
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

module.exports = { sendProductMessage, sendPromotionalCampaign, formatProductMessage };
