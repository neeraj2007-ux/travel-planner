import random
import jwt
from datetime import datetime, timedelta, timezone
from config import Config
from supabase import create_client

class AuthService:
    def __init__(self):
        self.secret_key = Config.SECRET_KEY
        # Initialize Supabase connection specifically for Auth
        self.supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

    def generate_otp(self):
        return str(random.randint(100000, 999999))

    def store_otp(self, email, otp):
        """Stores OTP in Supabase Database"""
        try:
            # Upsert: Update if exists, Insert if new
            data = {
                "email": email,
                "otp": otp,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            self.supabase.table('otps').upsert(data).execute()
            print(f"✅ OTP stored in DB for {email}")
        except Exception as e:
            print(f"❌ Error storing OTP: {e}")

    def verify_otp(self, email, otp):
        """Checks OTP against Supabase Database"""
        try:
            # 1. Fetch OTP from DB
            response = self.supabase.table('otps').select('*').eq('email', email).execute()
            
            if not response.data:
                return False, 'OTP not found. Please request a new one.'

            record = response.data[0]
            stored_otp = record['otp']
            created_at_str = record['created_at']

            # 2. Check Expiry (10 minutes)
            # Handle format: '2023-10-27T10:00:00+00:00'
            created_at = datetime.fromisoformat(created_at_str)
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            
            now = datetime.now(timezone.utc)
            
            # Calculate difference in minutes
            time_diff = (now - created_at).total_seconds() / 60

            if time_diff > Config.OTP_EXPIRY_MINUTES:
                return False, 'OTP has expired'

            # 3. Validate Code
            if stored_otp == otp:
                # Delete used OTP for security
                self.supabase.table('otps').delete().eq('email', email).execute()
                return True, 'Success'
            else:
                return False, 'Invalid OTP'

        except Exception as e:
            print(f"❌ Error verifying OTP: {e}")
            return False, 'Server error during verification'

    def generate_jwt_token(self, email):
        payload = {
            'email': email,
            'exp': datetime.now(timezone.utc) + timedelta(days=Config.JWT_EXPIRY_DAYS)
        }
        return jwt.encode(payload, self.secret_key, algorithm=Config.JWT_ALGORITHM)

    def verify_jwt_token(self, token):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[Config.JWT_ALGORITHM])
            return True, payload
        except:
            return False, 'Invalid Token'