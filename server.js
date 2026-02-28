// server.js
const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(bodyParser.json());

let otpStore = {};

// -------------------- Send OTP --------------------
app.post('/send-otp', (req, res) => {
  const { email } = req.body;
  if (!email) return res.status(400).json({ success: false, message: 'Email required' });

  const otp = Math.floor(100000 + Math.random() * 900000).toString();
  otpStore[email] = otp;
  console.log(`OTP for ${email}: ${otp}`); // For demo purposes

  res.json({ success: true, message: `OTP sent to ${email}` });
});

// -------------------- Verify OTP --------------------
app.post('/verify-otp', (req, res) => {
  const { email, otp } = req.body;
  if (!otpStore[email] || otpStore[email] !== otp) return res.json({ success: false, message: 'Invalid OTP' });

  delete otpStore[email];
  const token = 'mock-jwt-token-' + email;
  res.json({ success: true, token });
});

// -------------------- Generate Trip --------------------
app.post('/generate-trip', (req, res) => {
  const { destination, budget, members, days } = req.body;
  const trip = {
    destination,
    budget,
    members,
    days,
    itinerary: [
      { title: 'Day 1', activities: ['Visit landmark', 'Lunch at cafe'] },
      { title: 'Day 2', activities: ['Shopping', 'Dinner at local restaurant'] },
      { title: 'Day 3', activities: ['Museum visit', 'Return home'] }
    ]
  };
  res.json({ success: true, trip });
});

// -------------------- Health Check --------------------
app.get('/health', (req, res) => res.json({ status: 'ok' }));

app.listen(PORT, () => console.log(`Backend running on port ${PORT}`));