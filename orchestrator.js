#!/usr/bin/env node

/**
 * Neo Pulse Hub - Master Orchestrator
 * Coordinates all AI agents and automation systems
 */

import fs from 'fs';
import path from 'path';
import { spawn } from 'child_process';

class Orchestrator {
  constructor() {
    this.processes = {};
    this.logger = this.setupLogger();
    this.config = this.loadConfig();
  }

  setupLogger() {
    const logsDir = path.join(process.cwd(), 'logs', 'orchestrator');
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
    const logMessage = `[${timestamp}] [${level}] [orchestrator] ${message}`;
    console.log(logMessage);

    const logFile = path.join(process.cwd(), 'logs', 'orchestrator', 'orchestrator.log');
    fs.appendFileSync(logFile, logMessage + '\n');
  }

  loadConfig() {
    const configPath = path.join(process.cwd(), '.openclaw', 'agent-config.json');
    try {
      return JSON.parse(fs.readFileSync(configPath, 'utf8'));
    } catch (error) {
      this.logger.error(`Failed to load config: ${error.message}`);
      return {};
    }
  }

  startProcess(name, script, args = []) {
    this.logger.info(`Starting ${name}...`);

    const process = spawn('node', [script, ...args], {
      cwd: process.cwd(),
      stdio: ['ignore', 'pipe', 'pipe'],
      detached: true,
    });

    process.stdout.on('data', (data) => {
      const message = data.toString().trim();
      if (message) {
        this.logger.debug(`[${name}] ${message}`);
      }
    });

    process.stderr.on('data', (data) => {
      const message = data.toString().trim();
      if (message) {
        this.logger.error(`[${name}] ${message}`);
      }
    });

    process.on('error', (error) => {
      this.logger.error(`${name} error: ${error.message}`);
      // Restart the process
      setTimeout(() => this.startProcess(name, script, args), 5000);
    });

    process.on('exit', (code) => {
      this.logger.warn(`${name} exited with code ${code}`);
      // Restart the process
      setTimeout(() => this.startProcess(name, script, args), 5000);
    });

    this.processes[name] = process;
    this.logger.info(`${name} started successfully (PID: ${process.pid})`);
  }

  startAllServices() {
    this.logger.info('='.repeat(80));
    this.logger.info('NEO PULSE HUB - MASTER ORCHESTRATOR');
    this.logger.info('='.repeat(80));
    this.logger.info('Starting all AI automation services...');
    this.logger.info('='.repeat(80));

    // Start OpenClaw Agent
    if (this.config.agent?.enabled !== false) {
      this.startProcess('OpenClaw-Agent', 'openclaw-agent.js');
    }

    // Start Sync Manager
    this.startProcess('Sync-Manager', 'sync-manager.js');

    // Start Dashboard Server (if exists)
    if (fs.existsSync('server/_core/index.ts')) {
      this.startProcess('Dashboard-Server', 'npm', ['run', 'dev']);
    }

    this.logger.info('='.repeat(80));
    this.logger.info('All services started successfully!');
    this.logger.info('='.repeat(80));
    this.logger.info('System Status:');
    this.logger.info('  ✅ OpenClaw Agent - Autonomous task execution');
    this.logger.info('  ✅ Sync Manager - Repository and data synchronization');
    this.logger.info('  ✅ Dashboard - Real-time monitoring and control');
    this.logger.info('='.repeat(80));
  }

  getStatus() {
    this.logger.info('System Status Report:');
    this.logger.info('-'.repeat(80));

    for (const [name, process] of Object.entries(this.processes)) {
      const status = process.killed ? '❌ STOPPED' : '✅ RUNNING';
      this.logger.info(`${name}: ${status} (PID: ${process.pid})`);
    }

    this.logger.info('-'.repeat(80));
  }

  stopAll() {
    this.logger.info('Stopping all services...');

    for (const [name, process] of Object.entries(this.processes)) {
      try {
        process.kill('SIGTERM');
        this.logger.info(`${name} stopped`);
      } catch (error) {
        this.logger.error(`Failed to stop ${name}: ${error.message}`);
      }
    }

    this.logger.info('All services stopped');
  }

  start() {
    this.startAllServices();

    // Log status every 5 minutes
    setInterval(() => {
      this.getStatus();
    }, 5 * 60 * 1000);

    // Handle graceful shutdown
    process.on('SIGINT', () => {
      this.logger.info('Received SIGINT, shutting down gracefully...');
      this.stopAll();
      process.exit(0);
    });

    process.on('SIGTERM', () => {
      this.logger.info('Received SIGTERM, shutting down gracefully...');
      this.stopAll();
      process.exit(0);
    });
  }
}

// Start the orchestrator
const orchestrator = new Orchestrator();
orchestrator.start();
