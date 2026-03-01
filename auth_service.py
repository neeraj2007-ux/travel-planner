import random
import jwt
from datetime import datetime, timedelta, timezone
from config import Config
from supabase import create_client


class AuthService:
    def __init__(self):
        self.secret_key = Config.SECRET_KEY
        self.supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

    def generate_otp(self):
        return str(random.randint(100000, 999999))

    def store_otp(self, email, otp):
        try:
            now = datetime.now(timezone.utc)
            expires = now + timedelta(minutes=Config.OTP_EXPIRY_MINUTES)

            data = {
                "email": email,
                "otp": otp,
                "attempts": 0,
                "created_at": now.isoformat(),
                "expires_at": expires.isoformat()
            }

            self.supabase.table("otp_codes").upsert(data).execute()
            print("✅ OTP stored")

        except Exception as e:
            print("❌ OTP Store Error:", e)

    def verify_otp(self, email, otp):
        try:
            res = self.supabase.table("otp_codes") \
                .select("*") \
                .eq("email", email) \
                .execute()

            if not res.data:
                return False, "OTP not found"

            record = res.data[0]

            if record["otp"] != otp:
                return False, "Invalid OTP"

            expires = datetime.fromisoformat(record["expires_at"])
            if expires < datetime.now(timezone.utc):
                return False, "OTP expired"

            self.supabase.table("otp_codes").delete().eq("email", email).execute()
            return True, "Success"

        except Exception as e:
            print("❌ OTP Verify Error:", e)
            return False, "Server error"

    def generate_jwt_token(self, email):
        payload = {
            "email": email,
            "exp": datetime.now(timezone.utc) + timedelta(days=Config.JWT_EXPIRY_DAYS)
        }
        return jwt.encode(payload, self.secret_key, algorithm=Config.JWT_ALGORITHM)

    def verify_jwt_token(self, token):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[Config.JWT_ALGORITHM])
            return True, payload
        except:
            return False, None
