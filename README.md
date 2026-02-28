# 🌍 AI Travel Planner for Students

A budget-friendly travel planning web application designed specifically for students. Plan your trips intelligently with AI-powered itinerary generation, email-OTP authentication, and comprehensive budget management.

## 📋 Features

- ✈️ **Budget-Based Planning**: Input your total budget and get optimized allocation
- 🗺️ **AI-Powered Itineraries**: Day-wise travel plans tailored to your preferences
- 🔐 **Secure Authentication**: Email + OTP login (no passwords needed)
- 💰 **Smart Budget Breakdown**: Automatic allocation across categories
- 🎓 **Student-Friendly**: Designed for budget-conscious travelers
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile

## 🏗️ Project Structure

```
travel-planner/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── config.py              # Configuration management
│   ├── auth_service.py        # OTP and JWT authentication
│   ├── email_service.py       # Gmail SMTP email sending
│   ├── database_service.py    # Supabase database operations
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── index.html            # Main HTML page
│   ├── style.css             # Styling
│   └── script.js             # JavaScript API integration
└── .env.example              # Environment variables template
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Gmail account with App Password enabled
- Supabase account and project

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd travel-planner
```

### 2. Set Up Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Copy .env.example to .env
cp ../.env.example .env

# Edit .env with your credentials
nano .env  # or use any text editor
```

### 3. Configure Environment Variables

Edit `.env` file with your credentials:

```env
# Gmail SMTP
GMAIL_USER=your-email@gmail.com
GMAIL_PASSWORD=your-app-password

# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-supabase-key

# Security
SECRET_KEY=your-random-secret-key
```

#### Getting Gmail App Password:

1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Go to https://myaccount.google.com/apppasswords
4. Create app password for "Mail"
5. Copy the 16-character password

#### Getting Supabase Credentials:

1. Go to https://app.supabase.com
2. Create a new project
3. Go to Settings > API
4. Copy "Project URL" and "anon/public" key

### 4. Set Up Database

Create these tables in Supabase:

#### Users Table

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

#### Trips Table

```sql
CREATE TABLE trips (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    destination VARCHAR(255) NOT NULL,
    budget DECIMAL(10, 2) NOT NULL,
    members INTEGER NOT NULL,
    days INTEGER NOT NULL,
    from_location VARCHAR(255),
    accommodation VARCHAR(100),
    interests VARCHAR(100),
    budget_breakdown JSONB,
    itinerary JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (user_email) REFERENCES users(email)
);
```

#### Bookings Table (Optional)

```sql
CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    trip_id INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'confirmed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_email) REFERENCES users(email),
    FOREIGN KEY (trip_id) REFERENCES trips(id)
);
```

### 5. Run the Application

```bash
# From backend directory
python app.py
```

The server will start at `http://localhost:5000`

### 6. Access the Application

Open your browser and go to:
```
http://localhost:5000
```

## 📁 File Descriptions

### Backend Files

**app.py**
- Main Flask application
- API routes and endpoints
- Request handling and error management

**config.py**
- Centralized configuration
- Environment variable management
- Configuration validation

**auth_service.py**
- OTP generation and verification
- JWT token creation and validation
- Session management

**email_service.py**
- Gmail SMTP integration
- OTP email sending
- Booking confirmation emails

**database_service.py**
- Supabase database operations
- CRUD operations for users, trips, bookings
- Data validation and error handling

### Frontend Files

**index.html**
- Main webpage structure
- Trip planning form
- Authentication modal
- Destination showcase

**style.css**
- Responsive design
- Modern UI styling
- Gradient backgrounds
- Card layouts

**script.js**
- API integration
- Form handling
- OTP verification
- Trip plan display

## 🔑 API Endpoints

### Authentication

- `POST /api/send-otp` - Send OTP to email
- `POST /api/verify-otp` - Verify OTP and login

### Trip Management

- `POST /api/generate-trip` - Generate trip plan (auth required)
- `GET /api/my-trips` - Get user's trips (auth required)
- `GET /api/trips/:id` - Get specific trip (auth required)
- `DELETE /api/trips/:id` - Delete trip (auth required)

### Health Check

- `GET /api/health` - Server health status

## 🔒 Security Features

- JWT-based authentication
- Secure OTP via email
- Token expiry (30 days)
- Rate limiting on OTP attempts
- Secure password storage (never stored)
- CORS protection

## 💻 Technology Stack

### Backend
- **Python 3.8+**
- **Flask** - Web framework
- **Flask-CORS** - Cross-origin resource sharing
- **PyJWT** - JWT token handling
- **Supabase** - PostgreSQL database
- **Gmail SMTP** - Email service

### Frontend
- **HTML5**
- **CSS3** (Responsive Design)
- **JavaScript** (ES6+)
- **Fetch API** - HTTP requests

### Deployment
- **GitHub Pages** - Frontend hosting
- **Heroku/Railway/PythonAnywhere** - Backend hosting
- **Supabase** - Database hosting

## 📦 Deployment

### Deploy Backend (Heroku Example)

```bash
# Install Heroku CLI
# Login to Heroku
heroku login

# Create new app
heroku create your-app-name

# Add environment variables
heroku config:set GMAIL_USER=your-email@gmail.com
heroku config:set GMAIL_PASSWORD=your-app-password
heroku config:set SUPABASE_URL=your-url
heroku config:set SUPABASE_KEY=your-key
heroku config:set SECRET_KEY=your-secret

# Deploy
git push heroku main
```

### Deploy Frontend (GitHub Pages)

```bash
# Push frontend folder to gh-pages branch
git subtree push --prefix frontend origin gh-pages
```

## 🐛 Troubleshooting

### Email not sending
- Check Gmail App Password is correct
- Ensure 2FA is enabled on Gmail
- Check SMTP settings in config.py

### Database connection failed
- Verify Supabase URL and key
- Check if tables are created
- Ensure Supabase project is active

### OTP not working
- Check OTP hasn't expired (10 min)
- Verify email address is correct
- Check server logs for errors

## 📝 TODO / Future Enhancements

- [ ] Google Maps API integration
- [ ] Real-time flight/hotel booking
- [ ] AI-powered itinerary (Claude API)
- [ ] Social features (group planning)
- [ ] Payment gateway integration
- [ ] Mobile app (React Native)
- [ ] Multi-language support

## 👥 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

MIT License - feel free to use for your projects!

## 📧 Support

For issues and questions:
- Create an issue on GitHub
- Email: your-email@example.com

## 🎓 Built For Students, By Students

This project was created to make travel planning accessible and affordable for students worldwide.

---

**Happy Traveling! ✈️🌏**
