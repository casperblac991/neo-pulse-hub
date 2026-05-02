# Neo Pulse Hub - AI Automation Dashboard

A comprehensive dark-themed neon-accented dashboard for monitoring and controlling your AI-powered e-commerce automation system.

## Features

### 1. Dashboard Home
- **KPI Cards**: Real-time metrics showing:
  - Total products fetched today
  - Blog posts generated
  - Telegram campaigns sent
  - Successful automation tasks
- **Task Status Overview**: Live status for all 4 automation tasks:
  - `fetch-products` - Retrieves products from Amazon
  - `generate-content` - Creates AI-generated blog posts
  - `publish-social` - Sends Telegram campaigns
  - `sync-github` - Syncs content to GitHub
- **Recent Execution Logs**: Timestamped activity feed with status badges

### 2. Products Catalog (`/products`)
- Browse all fetched products with full details
- Search functionality to find products by title
- Filter by product category
- View product ratings, prices, and reviews
- Direct links to Amazon product pages

### 3. Blog Posts Library (`/blogs`)
- View all AI-generated blog content
- Filter by language: English (EN) or Arabic (AR)
- Expandable preview of blog content
- Markdown rendering support
- Track product associations for each post

### 4. Telegram Campaigns (`/campaigns`)
- Monitor all sent marketing campaigns
- Track delivery status (delivered, failed, pending)
- View campaign messages and timestamps
- Statistics on total, delivered, pending, and failed campaigns
- Error tracking for failed deliveries

### 5. System Health Monitor (`/health`)
- Real-time service status for:
  - **OpenClaw Gateway**: Automation engine status
  - **OpenAI API**: Content generation service
  - **Telegram Bot**: Social media integration
  - **Amazon API**: Product data source
- Last check timestamps
- Service connectivity indicators
- System information display

## Design System

### Color Palette
- **Primary (Cyan)**: `#00D9FF` - Main accent color
- **Secondary (Magenta)**: `#FF00FF` - Alternative accent
- **Accent (Lime)**: `#00FF00` - Highlight color
- **Background**: Near-black (`oklch(0.08 0 0)`)
- **Foreground**: Off-white (`oklch(0.95 0.01 65)`)

### Visual Elements
- Grid pattern background throughout
- Neon glow effects on hover
- Status badges with color coding:
  - Green: Success
  - Red: Error
  - Yellow: Warning
  - Blue: Pending
  - Cyan: Running (animated)
- Smooth transitions and animations

## Database Schema

### Tables
- **automation_tasks**: Tracks scheduled task status and execution history
- **execution_logs**: Detailed logs for each task run
- **products**: Fetched product data with pricing and ratings
- **blog_posts**: Generated blog content with language tags
- **telegram_campaigns**: Sent campaign history and delivery status
- **system_health**: Service connectivity and status monitoring

## API Endpoints

All endpoints are protected with authentication and use tRPC protocol.

### Automation
- `automation.tasks` - Get all automation tasks
- `automation.taskByName` - Get specific task details
- `automation.updateTask` - Update task configuration

### Logs
- `logs.recent` - Get recent execution logs
- `logs.byTask` - Get logs for specific task

### Products
- `products.all` - Get all products
- `products.byCategory` - Filter products by category

### Blogs
- `blogs.all` - Get all blog posts
- `blogs.byLanguage` - Filter by language (EN/AR)

### Campaigns
- `campaigns.all` - Get all telegram campaigns

### Health
- `health.all` - Get all service health status
- `health.byService` - Get specific service status

## Getting Started

1. **Access the Dashboard**: Navigate to the deployed URL
2. **Sign In**: Use Manus OAuth to authenticate
3. **Monitor KPIs**: Check the home page for real-time metrics
4. **Browse Content**: Explore products, blogs, and campaigns
5. **Check System Health**: Monitor service connectivity

## Features in Development

- Real-time log streaming with WebSocket
- Manual task trigger functionality
- Advanced filtering and search
- Export reports as PDF
- Webhook integration for live updates
- Custom alert thresholds
- Performance analytics

## Troubleshooting

### No Data Showing
- Ensure automation tasks have been run
- Check system health for API connectivity
- Verify database connection

### Slow Performance
- Clear browser cache
- Check network connectivity
- Monitor system resources

### Authentication Issues
- Clear cookies and sign in again
- Check OAuth configuration
- Verify user permissions

## Support

For issues or feature requests, contact the development team or check the system logs for detailed error information.
