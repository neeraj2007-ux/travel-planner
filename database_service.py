from supabase import create_client
from config import Config
from datetime import datetime

class DatabaseService:
    def __init__(self):
        self.supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    def get_user_by_email(self, email):
        try:
            res = self.supabase.table('users').select('*').eq('email', email).execute()
            return res.data[0] if res.data else None
        except: return None
    
    def create_user(self, email):
        try:
            res = self.supabase.table('users').insert({'email': email}).execute()
            return res.data[0] if res.data else None
        except: return None
    
    def create_trip(self, trip_data):
        try:
            res = self.supabase.table('trips').insert(trip_data).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            print(f"DB Error: {e}")
            return None
    
    def get_user_trips(self, email):
        try:
            res = self.supabase.table('trips').select('*').eq('user_email', email).order('created_at', desc=True).execute()
            return res.data if res.data else []
        except: return []