#!/usr/bin/env node
/**
 * Simple Express server for handling email subscriptions
 * Stores emails in local JSON file and syncs with Google Sheets
 */

const express = require('express');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname)));

// Data directory
const DATA_DIR = path.join(__dirname, 'data');
const SUBSCRIBERS_FILE = path.join(DATA_DIR, 'subscribers.json');

// Ensure data directory exists
if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
}

// Initialize subscribers file
if (!fs.existsSync(SUBSCRIBERS_FILE)) {
    fs.writeFileSync(SUBSCRIBERS_FILE, JSON.stringify({ subscribers: [] }, null, 2));
}

/**
 * GET /api/subscribers - Get all subscribers
 */
app.get('/api/subscribers', (req, res) => {
    try {
        const data = JSON.parse(fs.readFileSync(SUBSCRIBERS_FILE, 'utf8'));
        res.json(data.subscribers);
    } catch (error) {
        console.error('Error reading subscribers:', error);
        res.status(500).json({ error: 'Failed to read subscribers' });
    }
});

/**
 * POST /api/subscribe - Add new subscriber
 */
app.post('/api/subscribe', (req, res) => {
    try {
        const { name, email, interests, timestamp } = req.body;

        // Validation
        if (!name || !email) {
            return res.status(400).json({ error: 'Name and email are required' });
        }

        // Email validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            return res.status(400).json({ error: 'Invalid email format' });
        }

        // Read existing subscribers
        const data = JSON.parse(fs.readFileSync(SUBSCRIBERS_FILE, 'utf8'));

        // Check for duplicate email
        const existingSubscriber = data.subscribers.find(s => s.email === email);
        if (existingSubscriber) {
            return res.status(409).json({ error: 'Email already subscribed' });
        }

        // Create new subscriber
        const subscriber = {
            id: Date.now().toString(),
            name: name.trim(),
            email: email.toLowerCase().trim(),
            interests: interests ? interests.trim() : '',
            timestamp: timestamp || new Date().toISOString(),
            status: 'active',
            source: 'website'
        };

        // Add to subscribers
        data.subscribers.push(subscriber);

        // Save to file
        fs.writeFileSync(SUBSCRIBERS_FILE, JSON.stringify(data, null, 2));

        console.log(`✅ New subscriber: ${email}`);

        // Sync with Google Sheets (async, don't wait)
        syncToGoogleSheets(subscriber).catch(err => {
            console.error('Error syncing to Google Sheets:', err);
        });

        res.status(201).json({
            success: true,
            message: 'Subscription successful',
            subscriber: subscriber
        });
    } catch (error) {
        console.error('Error adding subscriber:', error);
        res.status(500).json({ error: 'Failed to add subscriber' });
    }
});

/**
 * POST /api/export-to-sheets - Export all subscribers to Google Sheets
 */
app.post('/api/export-to-sheets', (req, res) => {
    try {
        const data = JSON.parse(fs.readFileSync(SUBSCRIBERS_FILE, 'utf8'));
        const subscribers = data.subscribers;

        if (subscribers.length === 0) {
            return res.status(400).json({ error: 'No subscribers to export' });
        }

        // Prepare CSV format for Google Sheets
        let csvContent = 'الاسم,البريد الإلكتروني,الاهتمامات,التاريخ,الحالة\n';
        
        subscribers.forEach(sub => {
            const row = [
                `"${sub.name}"`,
                `"${sub.email}"`,
                `"${sub.interests}"`,
                `"${sub.timestamp}"`,
                `"${sub.status}"`
            ].join(',');
            csvContent += row + '\n';
        });

        // Save CSV file
        const csvFile = path.join(DATA_DIR, `subscribers_${Date.now()}.csv`);
        fs.writeFileSync(csvFile, csvContent, 'utf8');

        console.log(`✅ Exported ${subscribers.length} subscribers to CSV`);

        res.json({
            success: true,
            message: `Exported ${subscribers.length} subscribers`,
            file: csvFile,
            count: subscribers.length
        });
    } catch (error) {
        console.error('Error exporting subscribers:', error);
        res.status(500).json({ error: 'Failed to export subscribers' });
    }
});

/**
 * Sync subscriber to Google Sheets
 */
async function syncToGoogleSheets(subscriber) {
    try {
        // Check if gws is available
        execSync('which gws', { stdio: 'ignore' });

        // Prepare row data
        const rowData = [
            subscriber.name,
            subscriber.email,
            subscriber.interests,
            subscriber.timestamp,
            subscriber.status
        ];

        // Append to Google Sheet (requires proper setup)
        // This is a placeholder - actual implementation depends on Google Sheets setup
        console.log('📊 Syncing to Google Sheets:', subscriber.email);

        // In production, you would use:
        // execSync(`gws append --sheet "NEO_PULSE_HUB_Subscribers" --values ${rowData.join(' ')}`);

    } catch (error) {
        // gws not available or error - just log it
        console.warn('⚠️ Could not sync to Google Sheets:', error.message);
    }
}

/**
 * Health check endpoint
 */
app.get('/api/health', (req, res) => {
    res.json({
        status: 'ok',
        timestamp: new Date().toISOString(),
        subscribers: (() => {
            try {
                const data = JSON.parse(fs.readFileSync(SUBSCRIBERS_FILE, 'utf8'));
                return data.subscribers.length;
            } catch {
                return 0;
            }
        })()
    });
});

/**
 * Error handling middleware
 */
app.use((err, req, res, next) => {
    console.error('Server error:', err);
    res.status(500).json({ error: 'Internal server error' });
});

/**
 * Start server
 */
app.listen(PORT, () => {
    console.log(`🚀 Subscription server running on port ${PORT}`);
    console.log(`📧 Subscribers file: ${SUBSCRIBERS_FILE}`);
});
