import os
from dotenv import load_dotenv

# Load .env from root directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key')
    DEBUG = os.environ.get('DEBUG', 'False') == 'True'
    
    # Email
    GMAIL_USER = os.environ.get('GMAIL_USER')
    GMAIL_PASSWORD = os.environ.get('GMAIL_PASSWORD')
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    
    # Supabase
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    
    # JWT & OTP
    JWT_EXPIRY_DAYS = 7
    JWT_ALGORITHM = 'HS256'
    OTP_EXPIRY_MINUTES = 10
    MAX_OTP_ATTEMPTS = 3
    
    # APIs
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

    @staticmethod
    def validate_config():
        # Only strict check in production
        if not Config.DEBUG:
            required = ['GMAIL_USER', 'GMAIL_PASSWORD', 'SUPABASE_URL', 'SUPABASE_KEY', 'GEMINI_API_KEY']
            missing = [r for r in required if not os.environ.get(r)]
            if missing: raise ValueError(f"Missing env vars: {missing}")