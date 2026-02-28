"""
Main Flask Application
Travel Planner Backend API
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime

# Import services
from config import Config
from auth_service import AuthService
from email_service import EmailService
from database_service import DatabaseService
from ai_service import AIService

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend')
CORS(app)  # In production, restrict origins: origins=["https://your-frontend.com"]

# Load configuration
app.config.from_object(Config)

# Initialize services
auth_service = AuthService()
email_service = EmailService()
db_service = DatabaseService()
ai_service = AIService()

# ==================== UTILITY FUNCTIONS ====================

def get_auth_token():
    """Extract auth token from request header"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    return auth_header.split(' ')[1]

def verify_request_auth():
    """
    Verify authentication token from request
    Returns:
        tuple: (success: bool, email/error: str)
    """
    token = get_auth_token()
    if not token:
        return False, 'Authentication required'

    success, result = auth_service.verify_jwt_token(token)
    if not success:
        return False, result

    return True, result['email']

# ==================== FRONTEND ROUTES ====================

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('../frontend', path)

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/api/send-otp', methods=['POST'])
def send_otp():
    try:
        data = request.get_json()
        email = data.get('email')
        if not email:
            return jsonify({'success': False, 'message': 'Email is required'}), 400

        otp = auth_service.generate_otp()
        auth_service.store_otp(email, otp)

        if email_service.send_otp_email(email, otp):
            return jsonify({'success': True, 'message': 'OTP sent successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to send OTP. Please try again.'}), 500

    except Exception as e:
        print(f"Error in send_otp: {str(e)}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    try:
        data = request.get_json()
        email = data.get('email')
        otp = data.get('otp')
        if not email or not otp:
            return jsonify({'success': False, 'message': 'Email and OTP are required'}), 400

        success, message = auth_service.verify_otp(email, otp)
        if not success:
            return jsonify({'success': False, 'message': message}), 400

        user = db_service.get_user_by_email(email)
        if not user:
            user = db_service.create_user(email)

        db_service.update_user_last_login(email)
        token = auth_service.generate_jwt_token(email)

        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': token,
            'user': {'email': email}
        })

    except Exception as e:
        print(f"Error in verify_otp: {str(e)}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

# ==================== TRIP PLANNING ROUTES ====================

@app.route('/api/generate-trip', methods=['POST'])
def generate_trip():
    """Generate trip plan based on user input"""
    try:
        auth_success, email_or_error = verify_request_auth()
        if not auth_success:
            return jsonify({'success': False, 'message': email_or_error}), 401

        email = email_or_error
        data = request.get_json()

        # Extract trip parameters safely
        try:
            destination = data.get('destination')
            budget = float(data.get('budget'))
            members = int(data.get('members'))
            days = int(data.get('days'))
            from_location = data.get('from')
            accommodation = data.get('accommodation')
            interests = data.get('interests', [])
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Budget, members, and days must be numbers'}), 400

        if not isinstance(interests, list):
            interests = [interests]

        if not all([destination, budget, members, days, from_location]):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400

        per_person_budget = budget / members
        budget_breakdown = {
            'transportation': round(budget * 0.30, 2),
            'accommodation': round(budget * 0.35, 2),
            'food': round(budget * 0.20, 2),
            'activities': round(budget * 0.10, 2),
            'miscellaneous': round(budget * 0.05, 2)
        }

        ai_result = ai_service.generate_itinerary(
            destination=destination,
            budget=budget,
            members=members,
            days=days,
            from_location=from_location,
            accommodation=accommodation,
            interests=interests
        )

        # Safe extraction
        itinerary_data = ai_result.get('itinerary', {})
        itinerary = itinerary_data.get('itinerary', [])
        recommendations = itinerary_data.get('recommendations', {})
        estimated_costs = itinerary_data.get('estimated_costs', budget_breakdown)

        trip_data = {
            'user_email': email,
            'destination': destination,
            'budget': budget,
            'members': members,
            'days': days,
            'from_location': from_location,
            'accommodation': accommodation,
            'interests': interests,
            'budget_breakdown': estimated_costs,
            'itinerary': itinerary,
            'recommendations': recommendations
        }

        saved_trip = db_service.create_trip(trip_data)

        if saved_trip:
            # Send confirmation email
            email_service.send_booking_confirmation(email, trip_data)

            return jsonify({
                'success': True,
                'message': 'Trip plan generated successfully',
                'trip': {
                    'id': saved_trip.get('id'),
                    'destination': destination,
                    'budget': budget,
                    'per_person_budget': per_person_budget,
                    'members': members,
                    'days': days,
                    'budget_breakdown': estimated_costs,
                    'itinerary': itinerary,
                    'recommendations': recommendations
                }
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to save trip'}), 500

    except Exception as e:
        print(f"Error in generate_trip: {str(e)}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

@app.route('/api/my-trips', methods=['GET'])
def get_my_trips():
    try:
        auth_success, email_or_error = verify_request_auth()
        if not auth_success:
            return jsonify({'success': False, 'message': email_or_error}), 401

        email = email_or_error
        trips = db_service.get_user_trips(email)

        return jsonify({'success': True, 'trips': trips})

    except Exception as e:
        print(f"Error in get_my_trips: {str(e)}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

@app.route('/api/trips/<int:trip_id>', methods=['GET'])
def get_trip(trip_id):
    try:
        auth_success, email_or_error = verify_request_auth()
        if not auth_success:
            return jsonify({'success': False, 'message': email_or_error}), 401

        email = email_or_error
        trip = db_service.get_trip_by_id(trip_id)

        if not trip:
            return jsonify({'success': False, 'message': 'Trip not found'}), 404

        if trip['user_email'] != email:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403

        return jsonify({'success': True, 'trip': trip})

    except Exception as e:
        print(f"Error in get_trip: {str(e)}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

@app.route('/api/trips/<int:trip_id>', methods=['DELETE'])
def delete_trip(trip_id):
    try:
        auth_success, email_or_error = verify_request_auth()
        if not auth_success:
            return jsonify({'success': False, 'message': email_or_error}), 401

        email = email_or_error
        success = db_service.delete_trip(trip_id, email)

        if success:
            return jsonify({'success': True, 'message': 'Trip deleted successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to delete trip'}), 500

    except Exception as e:
        print(f"Error in delete_trip: {str(e)}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'success': True, 'message': 'Server is running', 'timestamp': datetime.now().isoformat()})

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'message': 'Internal server error'}), 500

# ==================== RUN APPLICATION ====================

if __name__ == '__main__':
    try:
        Config.validate_config()
        print("✅ Configuration validated successfully")
    except ValueError as e:
        print(f"❌ Configuration error: {str(e)}. Please check your .env file")
        exit(1)

    print("🚀 Starting Travel Planner API...")
    print(f"📧 Email service: {Config.GMAIL_USER}")
    print(f"🗄️  Database: Supabase configured")

    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)