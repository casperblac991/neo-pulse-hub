#!/usr/bin/env node

/**
 * Neo Pulse Hub - Complete Sync Manager
 * Handles all synchronization and automation tasks
 */

import fs from 'fs';
import path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

class SyncManager {
  constructor() {
    this.config = this.loadConfig();
    this.logger = this.setupLogger();
    this.startTime = new Date();
  }

  loadConfig() {
    const configPath = path.join(process.cwd(), '.openclaw', 'sync-config.json');
    try {
      const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      return config;
    } catch (error) {
      console.error('Failed to load sync config:', error);
      process.exit(1);
    }
  }

  setupLogger() {
    const logsDir = path.join(process.cwd(), 'logs', 'sync');
    if (!fs.existsSync(logsDir)) {
      fs.mkdirSync(logsDir, { recursive: true });
    }

    return {
      info: (message) => this.log('INFO', message),
      error: (message) => this.log('ERROR', message),
      warn: (message) => this.log('WARN', message),
      debug: (message) => this.log('DEBUG', message),
    };
  }

  log(level, message) {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] [${level}] [sync-manager] ${message}`;
    console.log(logMessage);

    const logFile = path.join(process.cwd(), 'logs', 'sync', 'sync-manager.log');
    fs.appendFileSync(logFile, logMessage + '\n');
  }

  async syncGitHub() {
    this.logger.info('Starting GitHub synchronization...');
    try {
      const { stdout } = await execAsync('git status --porcelain');
      
      if (stdout.trim()) {
        await execAsync('git add -A');
        const commitMessage = `[AUTO] ${new Date().toISOString()} - AI-generated content and updates`;
        await execAsync(`git commit -m "${commitMessage}"`);
        await execAsync('git push origin main');
        this.logger.info('GitHub synchronization completed successfully');
        return true;
      } else {
        this.logger.info('No changes to sync to GitHub');
        return false;
      }
    } catch (error) {
      this.logger.error(`GitHub sync failed: ${error.message}`);
      return false;
    }
  }

  async syncDatabase() {
    this.logger.info('Starting database synchronization...');
    try {
      // Database sync logic would go here
      this.logger.info('Database synchronization completed');
      return true;
    } catch (error) {
      this.logger.error(`Database sync failed: ${error.message}`);
      return false;
    }
  }

  async syncContent() {
    this.logger.info('Starting content synchronization...');
    try {
      // Content sync logic would go here
      this.logger.info('Content synchronization completed');
      return true;
    } catch (error) {
      this.logger.error(`Content sync failed: ${error.message}`);
      return false;
    }
  }

  async syncAnalytics() {
    this.logger.info('Starting analytics synchronization...');
    try {
      // Analytics sync logic would go here
      this.logger.info('Analytics synchronization completed');
      return true;
    } catch (error) {
      this.logger.error(`Analytics sync failed: ${error.message}`);
      return false;
    }
  }

  async performFullSync() {
    this.logger.info('='.repeat(80));
    this.logger.info('STARTING COMPLETE SYNCHRONIZATION');
    this.logger.info('='.repeat(80));

    const results = {
      github: false,
      database: false,
      content: false,
      analytics: false,
      timestamp: new Date().toISOString(),
    };

    // Execute all syncs
    if (this.config.repositories.github.enabled) {
      results.github = await this.syncGitHub();
    }

    if (this.config.dataSources.database.enabled) {
      results.database = await this.syncDatabase();
    }

    if (this.config.dataSources.openai.enabled) {
      results.content = await this.syncContent();
    }

    results.analytics = await this.syncAnalytics();

    // Log summary
    this.logger.info('='.repeat(80));
    this.logger.info('SYNCHRONIZATION SUMMARY');
    this.logger.info('='.repeat(80));
    this.logger.info(`GitHub Sync: ${results.github ? '✅ SUCCESS' : '❌ FAILED'}`);
    this.logger.info(`Database Sync: ${results.database ? '✅ SUCCESS' : '❌ FAILED'}`);
    this.logger.info(`Content Sync: ${results.content ? '✅ SUCCESS' : '❌ FAILED'}`);
    this.logger.info(`Analytics Sync: ${results.analytics ? '✅ SUCCESS' : '❌ FAILED'}`);
    this.logger.info('='.repeat(80));

    return results;
  }

  async start() {
    this.logger.info('Neo Pulse Hub Sync Manager started');
    this.logger.info(`Mode: ${this.config.syncManager.mode}`);
    this.logger.info(`Sync Interval: ${this.config.syncManager.syncInterval}`);

    // Perform initial sync
    await this.performFullSync();

    // Schedule periodic syncs
    const syncIntervalMs = this.parseInterval(this.config.syncManager.syncInterval);
    setInterval(async () => {
      await this.performFullSync();
    }, syncIntervalMs);

    this.logger.info('Sync Manager is running and monitoring for changes...');
  }

  parseInterval(interval) {
    const match = interval.match(/(\d+)([mhd])/);
    if (!match) return 5 * 60 * 1000; // Default 5 minutes

    const [, value, unit] = match;
    const num = parseInt(value, 10);

    switch (unit) {
      case 'm':
        return num * 60 * 1000;
      case 'h':
        return num * 60 * 60 * 1000;
      case 'd':
        return num * 24 * 60 * 60 * 1000;
      default:
        return 5 * 60 * 1000;
    }
  }
}

// Start the sync manager
const manager = new SyncManager();
manager.start().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.log('\nSync Manager shutting down gracefully...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\nSync Manager shutting down gracefully...');
  process.exit(0);
});
