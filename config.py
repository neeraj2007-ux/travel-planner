"""
Configuration file for Travel Planner Application
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-secret-key')
    DEBUG = os.environ.get('DEBUG', 'False') == 'True'
    
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
    JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')
    
    # OTP Configuration
    OTP_EXPIRY_MINUTES = 10
    MAX_OTP_ATTEMPTS = 3
    
    # API Keys
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
    CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY')
    
    @staticmethod
    def validate_config():
        """Validate that all required configuration is present"""
        required_vars = [
            'GMAIL_USER',
            'GMAIL_PASSWORD',
            'SUPABASE_URL',
            'SUPABASE_KEY',
            'SECRET_KEY',
            'GOOGLE_MAPS_API_KEY'
        ]
        
        missing = []
        for var in required_vars:
            if not os.environ.get(var):
                missing.append(var)
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        return True