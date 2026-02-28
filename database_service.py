"""
Database service for Supabase operations
"""
from supabase import create_client, Client
from config import Config
from datetime import datetime

class DatabaseService:
    """Handle all database operations with Supabase"""
    
    def __init__(self):
        self.supabase: Client = create_client(
            Config.SUPABASE_URL,
            Config.SUPABASE_KEY
        )
    
    # ============ USER OPERATIONS ============
    
    def get_user_by_email(self, email):
        """Get user by email"""
        try:
            response = self.supabase.table('users').select('*').eq('email', email).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting user: {str(e)}")
            return None
    
    def create_user(self, email):
        """Create new user"""
        try:
            user_data = {
                'email': email,
                'created_at': datetime.now().isoformat()
            }
            response = self.supabase.table('users').insert(user_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            return None
    
    def update_user_last_login(self, email):
        """Update user's last login timestamp"""
        try:
            self.supabase.table('users').update({
                'last_login': datetime.now().isoformat()
            }).eq('email', email).execute()
            return True
        except Exception as e:
            print(f"Error updating last login: {str(e)}")
            return False
    
    # ============ TRIP OPERATIONS ============
    
    def create_trip(self, trip_data):
        """Create new trip"""
        try:
            trip_data['created_at'] = datetime.now().isoformat()
            response = self.supabase.table('trips').insert(trip_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating trip: {str(e)}")
            return None
    
    def get_user_trips(self, email):
        """Get all trips for a user"""
        try:
            response = self.supabase.table('trips')\
                .select('*')\
                .eq('user_email', email)\
                .order('created_at', desc=True)\
                .execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting trips: {str(e)}")
            return []
    
    def get_trip_by_id(self, trip_id):
        """Get trip by ID"""
        try:
            response = self.supabase.table('trips').select('*').eq('id', trip_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting trip: {str(e)}")
            return None
    
    def update_trip(self, trip_id, updates):
        """Update trip information"""
        try:
            updates['updated_at'] = datetime.now().isoformat()
            self.supabase.table('trips').update(updates).eq('id', trip_id).execute()
            return True
        except Exception as e:
            print(f"Error updating trip: {str(e)}")
            return False
    
    def delete_trip(self, trip_id, user_email):
        """Delete a trip"""
        try:
            self.supabase.table('trips')\
                .delete()\
                .eq('id', trip_id)\
                .eq('user_email', user_email)\
                .execute()
            return True
        except Exception as e:
            print(f"Error deleting trip: {str(e)}")
            return False
    
    # ============ BOOKING OPERATIONS ============
    
    def create_booking(self, booking_data):
        """Create new booking"""
        try:
            booking_data['created_at'] = datetime.now().isoformat()
            booking_data['status'] = 'confirmed'
            response = self.supabase.table('bookings').insert(booking_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating booking: {str(e)}")
            return None
    
    def get_user_bookings(self, email):
        """Get all bookings for a user"""
        try:
            response = self.supabase.table('bookings')\
                .select('*')\
                .eq('user_email', email)\
                .order('created_at', desc=True)\
                .execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting bookings: {str(e)}")
            return []