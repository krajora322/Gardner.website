const express = require('express');
const mysql = require('mysql2');
const cors = require('cors');
require('dotenv').config();

const app = express();
app.use(cors());
app.use(express.json());

// Database connection
const db = mysql.createConnection({
    host: 'localhost',
    user: 'root', // Update with your MySQL username
    password: 'password', // Update with your MySQL password
    database: 'gardening_db'
});

// Connect to database
db.connect((err) => {
    if (err) {
        console.error('Error connecting to database:', err);
        return;
    }
    console.log('Connected to MySQL database');
});

// User registration endpoint
app.post('/api/users/register', (req, res) => {
    const { name, email, password } = req.body;
    
    const query = 'INSERT INTO users (name, email, password) VALUES (?, ?, ?)';
    db.query(query, [name, email, password], (err, result) => {
        if (err) {
            res.status(500).json({ error: 'Error registering user' });
            return;
        }
        res.status(201).json({ message: 'User registered successfully' });
    });
});

// Gardener listing endpoint
app.get('/api/gardeners', (req, res) => {
    const query = 'SELECT * FROM gardeners';
    db.query(query, (err, results) => {
        if (err) {
            res.status(500).json({ error: 'Error fetching gardeners' });
            return;
        }
        res.json(results);
    });
});

// Booking creation endpoint
app.post('/api/bookings', (req, res) => {
    const { user_id, gardener_id, service_type, booking_date, booking_time } = req.body;
    
    const query = 'INSERT INTO bookings (user_id, gardener_id, service_type, booking_date, booking_time) VALUES (?, ?, ?, ?, ?)';
    db.query(query, [user_id, gardener_id, service_type, booking_date, booking_time], (err, result) => {
        if (err) {
            res.status(500).json({ error: 'Error creating booking' });
            return;
        }
        res.status(201).json({ message: 'Booking created successfully' });
    });
});

// Get user bookings endpoint
app.get('/api/bookings/:userId', (req, res) => {
    const userId = req.params.userId;
    
    const query = `
        SELECT b.*, g.name as gardener_name 
        FROM bookings b
        JOIN gardeners g ON b.gardener_id = g.id
        WHERE b.user_id = ?
    `;
    
    db.query(query, [userId], (err, results) => {
        if (err) {
            res.status(500).json({ error: 'Error fetching bookings' });
            return;
        }
        res.json(results);
    });
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
