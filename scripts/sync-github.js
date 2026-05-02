#!/usr/bin/env node

/**
 * GitHub Repository Sync for Neo Pulse Hub
 * Commits and pushes all automation changes to GitHub
 * Triggered after each automation cycle
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Configuration
const CONFIG = {
  repoDir: path.join(__dirname, '..'),
  logsDir: path.join(__dirname, '../logs'),
  gitUserName: 'Neo Pulse Hub Bot',
  gitUserEmail: 'bot@neopulsehub.com',
  commitMessagePrefix: '🤖 Auto-commit:',
};

// Ensure directories exist
function ensureDirectories() {
  if (!fs.existsSync(CONFIG.logsDir)) {
    fs.mkdirSync(CONFIG.logsDir, { recursive: true });
  }
}

// Execute shell command
function executeCommand(command, options = {}) {
  try {
    console.log(`[Git] Executing: ${command}`);
    const output = execSync(command, {
      cwd: CONFIG.repoDir,
      encoding: 'utf-8',
      ...options,
    });
    console.log(`[Git] Output: ${output.trim()}`);
    return { success: true, output };
  } catch (error) {
    console.error(`[Git] Error: ${error.message}`);
    return { success: false, error: error.message };
  }
}

// Configure git user
function configureGit() {
  console.log('[Git] Configuring git user...');
  executeCommand(`git config user.name "${CONFIG.gitUserName}"`);
  executeCommand(`git config user.email "${CONFIG.gitUserEmail}"`);
}

// Check git status
function checkGitStatus() {
  console.log('[Git] Checking repository status...');
  const result = executeCommand('git status --porcelain');

  if (!result.success) {
    throw new Error('Failed to check git status');
  }

  const changedFiles = result.output.trim().split('\n').filter(line => line.length > 0);
  console.log(`[Git] Found ${changedFiles.length} changed files`);

  return changedFiles;
}

// Stage changes
function stageChanges() {
  console.log('[Git] Staging changes...');
  const result = executeCommand('git add -A');

  if (!result.success) {
    throw new Error('Failed to stage changes');
  }

  return result;
}

// Generate commit message
function generateCommitMessage() {
  const timestamp = new Date().toISOString();
  const changes = [];

  // Check what was changed
  const productsDir = path.join(CONFIG.repoDir, 'products');
  const blogDir = path.join(CONFIG.repoDir, 'blog');

  if (fs.existsSync(productsDir)) {
    const productFiles = fs.readdirSync(productsDir).filter(f => f.endsWith('.json'));
    if (productFiles.length > 0) {
      changes.push(`${productFiles.length} products`);
    }
  }

  if (fs.existsSync(blogDir)) {
    const blogFiles = fs.readdirSync(blogDir).filter(f => f.endsWith('.md'));
    if (blogFiles.length > 0) {
      changes.push(`${blogFiles.length} blog posts`);
    }
  }

  const changesSummary = changes.length > 0 ? ` - ${changes.join(', ')}` : '';
  const message = `${CONFIG.commitMessagePrefix} Automation cycle${changesSummary} at ${timestamp}`;

  return message;
}

// Commit changes
function commitChanges() {
  console.log('[Git] Committing changes...');
  const commitMessage = generateCommitMessage();

  const result = executeCommand(`git commit -m "${commitMessage}"`);

  if (!result.success) {
    if (result.error.includes('nothing to commit')) {
      console.log('[Git] No changes to commit');
      return { success: true, message: 'No changes' };
    }
    throw new Error(`Failed to commit: ${result.error}`);
  }

  return result;
}

// Push changes to remote
function pushChanges() {
  console.log('[Git] Pushing changes to remote...');

  // Get current branch
  const branchResult = executeCommand('git rev-parse --abbrev-ref HEAD');
  if (!branchResult.success) {
    throw new Error('Failed to get current branch');
  }

  const branch = branchResult.output.trim();
  console.log(`[Git] Current branch: ${branch}`);

  // Push to remote
  const pushResult = executeCommand(`git push origin ${branch}`);

  if (!pushResult.success) {
    // Try to set upstream if it doesn't exist
    console.log('[Git] Attempting to set upstream...');
    const upstreamResult = executeCommand(`git push -u origin ${branch}`);
    if (!upstreamResult.success) {
      throw new Error(`Failed to push: ${upstreamResult.error}`);
    }
    return upstreamResult;
  }

  return pushResult;
}

// Get repository statistics
function getRepositoryStats() {
  const stats = {
    products: 0,
    blogs: 0,
    commits: 0,
  };

  const productsDir = path.join(CONFIG.repoDir, 'products');
  const blogDir = path.join(CONFIG.repoDir, 'blog');

  if (fs.existsSync(productsDir)) {
    stats.products = fs.readdirSync(productsDir).filter(f => f.endsWith('.json')).length;
  }

  if (fs.existsSync(blogDir)) {
    stats.blogs = fs.readdirSync(blogDir).filter(f => f.endsWith('.md')).length;
  }

  const commitsResult = executeCommand('git rev-list --count HEAD');
  if (commitsResult.success) {
    stats.commits = parseInt(commitsResult.output.trim(), 10);
  }

  return stats;
}

// Log execution
function logExecution(status, details) {
  const timestamp = new Date().toISOString();
  const logEntry = {
    timestamp,
    status,
    details,
  };

  const logFile = path.join(CONFIG.logsDir, `sync-github-${new Date().toISOString().split('T')[0]}.log`);
  const existingLogs = fs.existsSync(logFile) ? JSON.parse(fs.readFileSync(logFile, 'utf-8')) : [];
  existingLogs.push(logEntry);
  fs.writeFileSync(logFile, JSON.stringify(existingLogs, null, 2));

  console.log(`[Log] Execution logged: ${status}`);
}

// Main execution
async function main() {
  try {
    console.log('🔄 [GitHub] Starting repository synchronization...');
    ensureDirectories();

    // Configure git
    configureGit();

    // Check if we're in a git repository
    const isGitRepo = executeCommand('git rev-parse --is-inside-work-tree');
    if (!isGitRepo.success || isGitRepo.output.trim() !== 'true') {
      throw new Error('Not a git repository');
    }

    // Check status
    const changedFiles = checkGitStatus();

    if (changedFiles.length === 0) {
      console.log('[Git] No changes to sync');
      logExecution('success', {
        message: 'No changes to sync',
        timestamp: new Date().toISOString(),
      });
      return;
    }

    // Stage changes
    stageChanges();

    // Commit changes
    const commitResult = commitChanges();
    if (!commitResult.success && !commitResult.message) {
      throw new Error('Failed to commit changes');
    }

    // Push changes
    const pushResult = pushChanges();
    if (!pushResult.success) {
      throw new Error('Failed to push changes');
    }

    // Get statistics
    const stats = getRepositoryStats();

    const successMessage = `Successfully synced ${changedFiles.length} files to GitHub`;
    console.log(`✅ [Success] ${successMessage}`);
    logExecution('success', {
      filesChanged: changedFiles.length,
      stats,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('❌ [Error] GitHub synchronization failed:', error.message);
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

module.exports = { configureGit, checkGitStatus, stageChanges, commitChanges, pushChanges };
