"""
Authentication service for OTP generation and JWT tokens
"""
import random
import jwt
from datetime import datetime, timedelta
from config import Config

class AuthService:
    """Handle authentication operations"""
    
    def __init__(self):
        self.otp_storage = {}  # In production, use Redis
        self.secret_key = Config.SECRET_KEY
        self.jwt_algorithm = Config.JWT_ALGORITHM
        self.jwt_expiry_days = Config.JWT_EXPIRY_DAYS
    
    def generate_otp(self):
        """
        Generate a 6-digit OTP
        
        Returns:
            str: 6-digit OTP
        """
        return str(random.randint(100000, 999999))
    
    def store_otp(self, email, otp):
        """
        Store OTP with expiry time
        
        Args:
            email (str): User email
            otp (str): Generated OTP
        """
        expiry = datetime.now() + timedelta(minutes=Config.OTP_EXPIRY_MINUTES)
        self.otp_storage[email] = {
            'otp': otp,
            'expiry': expiry,
            'attempts': 0
        }
    
    def verify_otp(self, email, otp):
        """
        Verify OTP for an email
        
        Args:
            email (str): User email
            otp (str): OTP to verify
            
        Returns:
            tuple: (success: bool, message: str)
        """
        # Check if OTP exists
        if email not in self.otp_storage:
            return False, 'OTP not found or expired'
        
        stored_data = self.otp_storage[email]
        
        # Check expiry
        if datetime.now() > stored_data['expiry']:
            del self.otp_storage[email]
            return False, 'OTP expired'
        
        # Check max attempts
        if stored_data['attempts'] >= Config.MAX_OTP_ATTEMPTS:
            del self.otp_storage[email]
            return False, 'Too many attempts. Please request a new OTP'
        
        # Verify OTP
        if stored_data['otp'] == otp:
            # Remove OTP after successful verification
            del self.otp_storage[email]
            return True, 'OTP verified successfully'
        else:
            # Increment attempts
            stored_data['attempts'] += 1
            return False, 'Invalid OTP'
    
    def generate_jwt_token(self, email):
        """
        Generate JWT token for authenticated user
        
        Args:
            email (str): User email
            
        Returns:
            str: JWT token
        """
        payload = {
            'email': email,
            'exp': datetime.utcnow() + timedelta(days=self.jwt_expiry_days),
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.jwt_algorithm)
        return token
    
    def verify_jwt_token(self, token):
        """
        Verify JWT token
        
        Args:
            token (str): JWT token
            
        Returns:
            tuple: (success: bool, payload/message: dict/str)
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.jwt_algorithm])
            return True, payload
        except jwt.ExpiredSignatureError:
            return False, 'Token expired'
        except jwt.InvalidTokenError:
            return False, 'Invalid token'
    
    def clear_otp(self, email):
        """Remove OTP from storage"""
        if email in self.otp_storage:
            del self.otp_storage[email]
