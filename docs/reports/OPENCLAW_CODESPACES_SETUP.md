# OpenClaw AI Agent - GitHub Codespaces Setup Guide

## Overview

This guide explains how to set up and run the OpenClaw AI Agent on GitHub Codespaces. The agent autonomously manages your entire Neo Pulse Hub platform with full AI automation.

## Prerequisites

- GitHub account with Codespaces access
- Repository: `casperblac991/neo-pulse-hub`
- Required API keys:
  - OpenAI API key (GPT-4o)
  - Amazon Product Advertising API credentials
  - Telegram Bot token
  - GitHub personal access token

## Quick Start (5 Minutes)

### Step 1: Open Repository in Codespaces

1. Go to https://github.com/casperblac991/neo-pulse-hub
2. Click **Code** → **Codespaces** → **Create codespace on main**
3. Wait for the environment to initialize (2-3 minutes)

### Step 2: Configure Environment Variables

Create a `.env` file in the root directory:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o

# Amazon API Configuration
AMAZON_ACCESS_KEY=...
AMAZON_SECRET_KEY=...
AMAZON_ASSOCIATE_TAG=...

# Telegram Configuration
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHANNEL_ID=...

# GitHub Configuration
GITHUB_TOKEN=ghp_...
GITHUB_REPO=casperblac991/neo-pulse-hub

# Database Configuration
DATABASE_URL=mysql://user:password@localhost:3306/neo_pulse_hub

# Agent Configuration
AGENT_MODE=autonomous
AGENT_LOG_LEVEL=info
```

### Step 3: Install Dependencies

```bash
npm install --legacy-peer-deps
```

### Step 4: Start the Agent

```bash
node openclaw-agent.js
```

The agent will start and begin executing scheduled tasks automatically.

## Detailed Setup Instructions

### 1. Repository Setup

```bash
# Clone the repository (if not already in Codespaces)
git clone https://github.com/casperblac991/neo-pulse-hub.git
cd neo-pulse-hub

# Verify the structure
ls -la
# You should see:
# - openclaw-agent.js
# - .openclaw/
# - .devcontainer/
# - scripts/
# - client/
# - server/
```

### 2. Environment Configuration

#### OpenAI API Setup

1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Add to `.env`:
   ```
   OPENAI_API_KEY=sk-your-key-here
   OPENAI_MODEL=gpt-4o
   ```

#### Amazon API Setup

1. Register for Amazon Product Advertising API
2. Get your access key and secret key
3. Add to `.env`:
   ```
   AMAZON_ACCESS_KEY=your-access-key
   AMAZON_SECRET_KEY=your-secret-key
   AMAZON_ASSOCIATE_TAG=your-tag
   ```

#### Telegram Bot Setup

1. Create a bot with @BotFather on Telegram
2. Get your bot token
3. Add to `.env`:
   ```
   TELEGRAM_BOT_TOKEN=your-bot-token
   TELEGRAM_CHANNEL_ID=your-channel-id
   ```

#### GitHub Setup

1. Go to https://github.com/settings/tokens
2. Create a personal access token with `repo` scope
3. Add to `.env`:
   ```
   GITHUB_TOKEN=ghp_your-token
   ```

### 3. Database Setup

```bash
# Start MySQL (if using Docker)
docker run -d \
  --name mysql \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=neo_pulse_hub \
  -p 3306:3306 \
  mysql:8.0

# Or connect to existing database
# Update DATABASE_URL in .env
```

### 4. Build and Run

```bash
# Install dependencies
npm install --legacy-peer-deps

# Build the project
npm run build

# Start the agent
node openclaw-agent.js
```

## Agent Architecture

### Core Components

```
┌─────────────────────────────────────────┐
│     OpenClaw AI Agent (Main Process)    │
├─────────────────────────────────────────┤
│  Task Scheduler (Cron-based)            │
│  ├─ fetch-products (6:00 AM UTC)        │
│  ├─ generate-content (7:00 AM UTC)      │
│  ├─ publish-social (8:00 AM UTC)        │
│  ├─ generate-reports (9:00 AM UTC)      │
│  ├─ health-check (every 30 min)         │
│  └─ sync-github (6:00 PM UTC)           │
├─────────────────────────────────────────┤
│  Task Executor (Parallel Processing)    │
│  ├─ Content Generation Engine           │
│  ├─ Product Management System           │
│  ├─ Social Media Automation             │
│  ├─ Analytics & Reporting               │
│  └─ System Monitoring                   │
├─────────────────────────────────────────┤
│  Integration Layer                      │
│  ├─ OpenAI API                          │
│  ├─ Amazon API                          │
│  ├─ Telegram API                        │
│  ├─ GitHub API                          │
│  └─ Database Connection                 │
└─────────────────────────────────────────┘
```

### Task Schedule

| Time (UTC) | Task | Duration | Status |
|-----------|------|----------|--------|
| 06:00 | Fetch Products | 30 min | Automated |
| 07:00 | Generate Content | 45 min | Automated |
| 08:00 | Publish Social | 30 min | Automated |
| 09:00 | Generate Reports | 30 min | Automated |
| Every 30 min | Health Check | 5 min | Automated |
| 18:00 | Sync GitHub | 15 min | Automated |

## Monitoring and Logging

### View Agent Logs

```bash
# Real-time logs
tail -f logs/agent/agent-core.log

# Task execution logs
tail -f logs/agent/task-executor.log

# Scheduler logs
tail -f logs/agent/scheduler.log
```

### Check Agent Status

```bash
# View current agent status
curl http://localhost:8080/api/agent/status

# View task history
curl http://localhost:8080/api/tasks/history

# View system health
curl http://localhost:8080/api/health
```

### Dashboard Access

The dashboard is available at:
- **Development**: http://localhost:5173
- **Production**: https://neopulsedash-yqrezpyq.manus.space

## Advanced Configuration

### Custom Task Scheduling

Edit `.openclaw/agent-config.json`:

```json
{
  "scheduling": {
    "tasks": [
      {
        "name": "custom-task",
        "schedule": "0 12 * * *",
        "description": "Custom task at noon",
        "priority": "medium",
        "timeout": "30m"
      }
    ]
  }
}
```

### Performance Tuning

```json
{
  "performance": {
    "maxConcurrentTasks": 5,
    "taskTimeout": "30m",
    "retryAttempts": 3,
    "retryDelay": "5m",
    "caching": {
      "enabled": true,
      "ttl": "24h"
    }
  }
}
```

### Alerting Configuration

```json
{
  "monitoring": {
    "alerting": {
      "enabled": true,
      "channels": ["email", "telegram", "dashboard"],
      "thresholds": {
        "errorRate": 5,
        "responseTime": 5000,
        "cpuUsage": 80,
        "memoryUsage": 85
      }
    }
  }
}
```

## Troubleshooting

### Agent Won't Start

```bash
# Check Node.js version
node --version  # Should be >= 20.0.0

# Check dependencies
npm list

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

### API Connection Errors

```bash
# Test API connectivity
curl -I https://api.openai.com
curl -I https://api.amazon.com
curl -I https://api.telegram.org

# Check environment variables
env | grep API
```

### Database Connection Issues

```bash
# Test database connection
mysql -h localhost -u root -p neo_pulse_hub

# Check database URL format
echo $DATABASE_URL
```

### Task Execution Failures

```bash
# Check task logs
tail -f logs/agent/task-executor.log

# View error details
grep ERROR logs/agent/*.log

# Check task configuration
cat .openclaw/agent-config.json | jq '.scheduling.tasks'
```

## Performance Optimization

### Resource Limits

```bash
# Set memory limit
NODE_OPTIONS="--max-old-space-size=2048" node openclaw-agent.js

# Set CPU limit (if using Docker)
docker run --cpus="2" --memory="2g" ...
```

### Caching Strategy

- Product data: 24-hour cache
- Generated content: 7-day cache
- Analytics data: 1-hour cache
- API responses: Variable TTL

### Database Optimization

```sql
-- Create indexes for faster queries
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_blog_posts_language ON blog_posts(language);
CREATE INDEX idx_campaigns_timestamp ON telegram_campaigns(timestamp);
```

## Security Best Practices

### API Key Management

1. Never commit `.env` files
2. Rotate API keys every 90 days
3. Use separate keys for development and production
4. Enable API key restrictions

### Access Control

```bash
# Set file permissions
chmod 600 .env
chmod 700 .openclaw/
chmod 700 logs/
```

### Audit Logging

All agent activities are logged to:
- `logs/agent/agent-core.log` - Main agent logs
- `logs/agent/task-executor.log` - Task execution logs
- `logs/agent/scheduler.log` - Scheduler logs

## Deployment Options

### Option 1: GitHub Codespaces (Recommended)
- ✅ Always available
- ✅ Pre-configured environment
- ✅ Free tier available
- ✅ Easy to manage

### Option 2: Docker Container
```bash
docker build -t neo-pulse-agent .
docker run -d --name agent \
  -e OPENAI_API_KEY=... \
  -e DATABASE_URL=... \
  neo-pulse-agent
```

### Option 3: Cloud Deployment
- AWS EC2
- Google Cloud Run
- Azure Container Instances
- DigitalOcean App Platform

## Maintenance

### Regular Tasks

- **Weekly**: Review logs and error rates
- **Monthly**: Update dependencies
- **Quarterly**: Rotate API keys
- **Annually**: Security audit

### Backup Strategy

```bash
# Backup database
mysqldump -u root -p neo_pulse_hub > backup.sql

# Backup configuration
cp -r .openclaw/ .openclaw.backup/

# Backup logs
tar -czf logs-backup.tar.gz logs/
```

## Support and Resources

- **Documentation**: See `OPENCLAW_AI_AGENT_ARCHITECTURE.md`
- **Configuration**: `.openclaw/agent-config.json`
- **Logs**: `logs/agent/`
- **GitHub Issues**: https://github.com/casperblac991/neo-pulse-hub/issues
- **API Documentation**: See individual API provider docs

## Next Steps

1. ✅ Set up environment variables
2. ✅ Configure API keys
3. ✅ Start the agent
4. ✅ Monitor logs
5. ✅ Access dashboard
6. ✅ Customize tasks as needed

Your OpenClaw AI Agent is now ready to autonomously manage your Neo Pulse Hub platform!
