from supabase import create_client
from config import Config
from datetime import datetime, timezone


class DatabaseService:
    def __init__(self):
        self.supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

    # ---------- USERS ----------

    def create_user(self, email):
        self.supabase.table("users").insert({
            "email": email,
            "created_at": datetime.now(timezone.utc).isoformat()
        }).execute()

    def get_user_by_email(self, email):
        res = self.supabase.table("users").select("*").eq("email", email).execute()
        return res.data[0] if res.data else None

    # ---------- TRIPS ----------

    def create_trip(self, trip):
        self.supabase.table("trips").insert({
            "user_email": trip["user_email"],
            "destination": trip["destination"],
            "budget": trip["budget"],
            "members": trip["members"],
            "days": trip["days"],
            "from_location": trip["from_location"],
            "accommodation": trip["accommodation"],
            "interests": trip["interests"],
            "itinerary": trip["itinerary"],
            "recommendations": trip["recommendations"],
            "budget_breakdown": trip["budget_breakdown"],
            "created_at": datetime.now(timezone.utc).isoformat()
        }).execute()

    def get_user_trips(self, email):
        res = self.supabase.table("trips") \
            .select("*") \
            .eq("user_email", email) \
            .order("created_at", desc=True) \
            .execute()
        return res.data
