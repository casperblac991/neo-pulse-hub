---
name: e-commerce-automation
description: AI-powered automation for NEO PULSE HUB e-commerce store - products, customer service, marketing, and affiliate management
version: 1.0.0
triggers:
  - e-commerce
  - store management
  - customer bot
  - product automation
  - affiliate links
---

# E-Commerce Automation Skill

This skill provides comprehensive AI-powered automation for the NEO PULSE HUB e-commerce store.

## When to Use

- Managing product data and images
- Running AI customer service bot
- Automating marketing campaigns
- Fixing Amazon affiliate links
- Generating product content

## Quick Start

### 1. Update Product Images
```bash
python3 fix_images_and_links.py
```

### 2. Run Customer Service Bot
```bash
python3 customer_bot.py
```

### 3. Generate Marketing Content
```bash
python3 daily_article_generator.py
```

### 4. Social Media Automation
```bash
python3 social_media_automation.py
```

## Capabilities

### Product Management
- **Image Matching**: Automatically match products with real Amazon images
- **Link Fixing**: Validate and update Amazon affiliate links with proper ASIN
- **Data Synchronization**: Keep product data consistent across all platforms

### Customer Service Bot
- **AI-Powered Responses**: Use Gemini AI for intelligent customer support
- **Lead Tracking**: Track customer interactions and preferences
- **Product Recommendations**: Suggest products based on customer queries
- **Multi-language Support**: Arabic and English

### Marketing Automation
- **Daily Articles**: Generate product-focused content automatically
- **Social Campaigns**: Schedule and manage social media posts
- **Telegram Integration**: Send campaigns to Telegram subscribers

### Affiliate Management
- **Link Validation**: Ensure all Amazon links are direct product links
- **Tag Management**: Maintain consistent affiliate tags
- **Commission Tracking**: Monitor affiliate performance

## Configuration

### Environment Variables
```bash
CUSTOMER_BOT_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key
SITE_URL=https://neo-pulse-hub.it.com
AMAZON_AFFILIATE_TAG=neopulsehub-20
```

## File Structure
```
.
├── customer_bot.py           # AI customer service bot
├── fix_images_and_links.py  # Product data fixer
├── daily_article_generator.py
├── social_media_automation.py
├── recommendation_bot.py
├── leads.json              # Customer tracking
├── products.json           # Product database
└── products_fixed.html     # Updated store page
```

## Bot Commands

| Command | Description |
|---------|-------------|
| /start | Welcome message with main menu |
| /products | Show featured products |
| track | Order tracking |
| shipping | Shipping info |
| returns | Return policy |
| contact | Contact information |

## Best Practices

1. **Daily**: Run `fix_images_and_links.py` to keep images updated
2. **Weekly**: Review leads.json for customer insights
3. **Monthly**: Update product prices based on Amazon changes
4. **Continuous**: Monitor affiliate link performance

## Integration with Store

The bot connects to the store at `https://neo-pulse-hub.it.com` and provides:
- Real-time product information
- Direct Amazon affiliate links
- Order tracking integration
- Customer support 24/7

## Examples

- `Update all product images with real Amazon photos`
- `Fix broken Amazon affiliate links`
- `Run the customer service bot`
- `Generate daily marketing article`
- `Create Telegram campaign for new products`