const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const { GroqClient } = require('groq-sdk');

const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());

// Initialize Groq API client
const groqClient = new GroqClient({
    projectId: 'your_project_id',
    dataset: 'your_dataset'
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ status: 'healthy' });
});

// Chat endpoint
app.post('/chat', async (req, res) => {
    const { message } = req.body;
    const response = await groqClient.chat(message);
    res.json(response);
});

// Recommendations endpoint
app.get('/recommendations', async (req, res) => {
    const recommendations = await groqClient.getRecommendations();
    res.json(recommendations);
});

// Orders endpoint
app.post('/orders', async (req, res) => {
    const orderData = req.body;
    const result = await groqClient.createOrder(orderData);
    res.json(result);
});

// Newsletter subscription endpoint
app.post('/subscribe', async (req, res) => {
    const { email } = req.body;
    const result = await groqClient.subscribeToNewsletter(email);
    res.json(result);
});

// Analytics endpoint
app.get('/analytics', async (req, res) => {
    const analyticsData = await groqClient.getAnalytics();
    res.json(analyticsData);
});

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});