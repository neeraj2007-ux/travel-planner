from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from config import Config
from auth_service import AuthService
from email_service import EmailService
from database_service import DatabaseService
from ai_service import AIService
import os

# Initialize App
# FIXED: Static folder points to ../frontend so localhost:5000 serves the UI
app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.config.from_object(Config)

# FIXED: Allow CORS from all origins for development
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Services
auth_service = AuthService()
email_service = EmailService()
db_service = DatabaseService()
ai_service = AIService()

# --- Auth Helper ---
def verify_request_auth():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token: return False, 'No token'
    return auth_service.verify_jwt_token(token)

# --- Routes ---
@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../frontend', path)

@app.route('/api/send-otp', methods=['POST'])
def send_otp():
    email = request.json.get('email')
    otp = auth_service.generate_otp()
    auth_service.store_otp(email, otp)
    # If email service isn't configured, print OTP to console for testing
    if not Config.GMAIL_USER:
        print(f"DEV MODE OTP: {otp}")
        return jsonify({'success': True, 'message': 'OTP sent (Dev mode: Check console)'})
    
    if email_service.send_otp_email(email, otp):
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Email failed'}), 500

@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    success, msg = auth_service.verify_otp(data['email'], data['otp'])
    if success:
        user = db_service.get_user_by_email(data['email'])
        if not user: db_service.create_user(data['email'])
        token = auth_service.generate_jwt_token(data['email'])
        return jsonify({'success': True, 'token': token, 'user': {'email': data['email']}})
    return jsonify({'success': False, 'message': msg}), 400

@app.route('/api/generate-trip', methods=['POST'])
def generate_trip():
    success, result = verify_request_auth()
    if not success: return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    email = result['email']
    
    data = request.json
    try:
        trip_res = ai_service.generate_itinerary(
            data['destination'], float(data['budget']), int(data['members']),
            int(data['days']), data['from'], data['accommodation'], data.get('interests', [])
        )
        
        full_trip_data = {
            'user_email': email,
            'destination': data['destination'],
            'budget': float(data['budget']),
            'members': int(data['members']),
            'days': int(data['days']),
            'itinerary': trip_res['itinerary'].get('itinerary', []),
            'recommendations': trip_res['itinerary'].get('recommendations', {}),
            'budget_breakdown': trip_res['itinerary'].get('estimated_costs', {})
        }
        
        saved_trip = db_service.create_trip(full_trip_data)
        return jsonify({'success': True, 'trip': full_trip_data})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/my-trips', methods=['GET'])
def get_my_trips():
    success, result = verify_request_auth()
    if not success: return jsonify({'success': False}), 401
    trips = db_service.get_user_trips(result['email'])
    return jsonify({'success': True, 'trips': trips})

@app.route('/api/health')
def health():
    return jsonify({'success': True, 'status': 'ok'})

if __name__ == '__main__':
    try:
        Config.validate_config()
        print("Starting Flask Server on http://127.0.0.1:5000")
        app.run(debug=True, port=5000)
    except Exception as e:
        print(f"Config Error: {e}")