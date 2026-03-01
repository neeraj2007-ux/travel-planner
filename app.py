import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from config import Config
from auth_service import AuthService
from email_service import EmailService
from database_service import DatabaseService
from ai_service import AIService

# Correct frontend path (important for Render)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, '../frontend')

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
app.config.from_object(Config)

# ✅ FIX 1 — Enable CORS for ALL routes
CORS(app, origins="*")

auth_service = AuthService()
email_service = EmailService()
db_service = DatabaseService()
ai_service = AIService()


def get_auth():
    token = request.headers.get('Authorization', '')
    token = token.split(' ')[1] if ' ' in token else ''
    return auth_service.verify_jwt_token(token)


# ================= FRONTEND ROUTES =================

@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(FRONTEND_DIR, path)


# ================= API ROUTES =================

@app.route('/api/send-otp', methods=['POST'])
def send_otp():
    raw_email = request.json.get('email', '')
    email = raw_email.lower().strip()

    if not email:
        return jsonify({'success': False, 'message': 'Email required'}), 400

    otp = auth_service.generate_otp()
    auth_service.store_otp(email, otp)

    if email_service.send_otp_email(email, otp):
        return jsonify({'success': True, 'message': 'OTP sent'})

    print(f"⚠️ OTP for {email}: {otp}")
    return jsonify({'success': True, 'message': 'OTP generated'})


@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    email = data.get('email', '').lower().strip()
    otp = data.get('otp', '').strip()

    success, msg = auth_service.verify_otp(email, otp)

    if success:
        user = db_service.get_user_by_email(email)
        if not user:
            db_service.create_user(email)

        token = auth_service.generate_jwt_token(email)
        return jsonify({'success': True, 'token': token, 'user': {'email': email}})

    return jsonify({'success': False, 'message': msg}), 400


@app.route('/api/generate-trip', methods=['POST'])
def generate_trip():
    success, user = get_auth()
    if not success:
        return jsonify({'success': False}), 401

    d = request.json

    result = ai_service.generate_itinerary(
        d['destination'], float(d['budget']), int(d['members']),
        int(d['days']), d['from'], d['accommodation'], d.get('interests', [])
    )

    trip_data = {
        'user_email': user['email'],
        'destination': d['destination'],
        'budget': d['budget'],
        'members': d['members'],
        'days': d['days'],
        'itinerary': result['itinerary'].get('itinerary', []),
        'recommendations': result['itinerary'].get('recommendations', {}),
        'budget_breakdown': result['itinerary'].get('estimated_costs', {})
    }

    db_service.create_trip(trip_data)
    email_service.send_booking_confirmation(user['email'], trip_data)

    return jsonify({'success': True, 'trip': trip_data})


@app.route('/api/my-trips', methods=['GET'])
def my_trips():
    success, user = get_auth()
    if not success:
        return jsonify({'success': False}), 401

    trips = db_service.get_user_trips(user['email'])
    return jsonify({'success': True, 'trips': trips})


# ================= RUN SERVER =================

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # REQUIRED for Render
    app.run(host='0.0.0.0', port=port)
