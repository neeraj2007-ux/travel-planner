import random
import jwt
from datetime import datetime, timedelta
from config import Config

class AuthService:
    def __init__(self):
        if not hasattr(self, 'otp_storage'):
            self.otp_storage = {}
        self.secret_key = Config.SECRET_KEY

    def generate_otp(self):
        return str(random.randint(100000, 999999))

    def store_otp(self, email, otp):
        expiry = datetime.utcnow() + timedelta(minutes=Config.OTP_EXPIRY_MINUTES)
        self.otp_storage[email] = {'otp': otp, 'expiry': expiry, 'attempts': 0}
        print(f"DEBUG OTP for {email}: {otp}") # Remove in production

    def verify_otp(self, email, otp):
        if email not in self.otp_storage: return False, 'OTP expired or not found'
        record = self.otp_storage[email]
        if datetime.utcnow() > record['expiry']:
            del self.otp_storage[email]
            return False, 'OTP expired'
        if record['otp'] == otp:
            del self.otp_storage[email]
            return True, 'Success'
        return False, 'Invalid OTP'

    def generate_jwt_token(self, email):
        payload = {
            'email': email,
            'exp': datetime.utcnow() + timedelta(days=Config.JWT_EXPIRY_DAYS)
        }
        return jwt.encode(payload, self.secret_key, algorithm=Config.JWT_ALGORITHM)

    def verify_jwt_token(self, token):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[Config.JWT_ALGORITHM])
            return True, payload
        except:
            return False, 'Invalid Token'