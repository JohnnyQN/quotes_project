import express from 'express';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import db from '../db.js';
import dotenv from 'dotenv';

dotenv.config();
const router = express.Router();

// Helper: validate email format
const isValidEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

// ✅ Test route
router.get('/', (req, res) => {
  res.send("✅ Auth route is working");
});

// ✅ Register route
router.post('/register', async (req, res) => {
  const { name, email, password } = req.body;

  // Basic validation
  if (!name || !email || !password) {
    return res.status(400).json({ error: 'Name, email, and password are required' });
  }

  if (!isValidEmail(email)) {
    return res.status(400).json({ error: 'Invalid email format' });
  }

  if (password.length < 6) {
    return res.status(400).json({ error: 'Password must be at least 6 characters long' });
  }

  try {
    // Check if user already exists
    const userCheck = await db.query('SELECT * FROM users WHERE email = $1', [email]);
    if (userCheck.rows.length > 0) {
      return res.status(400).json({ error: 'User already exists' });
    }

    // Hash password & create user
    const hashedPassword = await bcrypt.hash(password, 10);
    const newUser = await db.query(
      `INSERT INTO users (name, email, password, created_at)
       VALUES ($1, $2, $3, NOW())
       RETURNING id, name, email`,
      [name, email, hashedPassword]
    );

    const token = jwt.sign({ userId: newUser.rows[0].id }, process.env.JWT_SECRET, {
      expiresIn: '1h'
    });

    res.status(201).json({ token });
  } catch (error) {
    console.error("❌ Registration error:", error);
    res.status(500).json({ error: 'Server error during registration' });
  }
});

// ✅ Login route
router.post('/login', async (req, res) => {
  const { email, password } = req.body;

  try {
    const user = await db.query('SELECT * FROM users WHERE email = $1', [email]);
    if (user.rows.length === 0) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const validPassword = await bcrypt.compare(password, user.rows[0].password);
    if (!validPassword) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const token = jwt.sign({ userId: user.rows[0].id }, process.env.JWT_SECRET, {
      expiresIn: '1h'
    });

    res.json({ token });
  } catch (error) {
    console.error("❌ Login error:", error);
    res.status(500).json({ error: 'Server error during login' });
  }
});

export default router;
