import os
from dotenv import load_dotenv

# Load environment variables from parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

class Config:
    """Application configuration"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.environ.get('DEBUG', 'True') == 'True'
    
    # Gmail SMTP Configuration
    GMAIL_USER = os.environ.get('GMAIL_USER')
    GMAIL_PASSWORD = os.environ.get('GMAIL_PASSWORD')
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    
    # Supabase Configuration
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    
    # JWT Configuration
    JWT_EXPIRY_DAYS = int(os.environ.get('JWT_EXPIRY_DAYS', 7))
    JWT_ALGORITHM = 'HS256'
    
    # OTP Configuration
    OTP_EXPIRY_MINUTES = 10
    MAX_OTP_ATTEMPTS = 3
    
    # API Keys
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    @staticmethod
    def validate_config():
        required_vars = ['GMAIL_USER', 'GMAIL_PASSWORD', 'SUPABASE_URL', 'SUPABASE_KEY', 'GEMINI_API_KEY']
        missing = [var for var in required_vars if not os.environ.get(var)]
        if missing:
            raise ValueError(f"Missing env variables: {', '.join(missing)}")