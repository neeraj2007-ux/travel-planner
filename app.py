import os
from flask import Flask, request, jsonify
from flask_cors import CORS

from config import Config
from auth_service import AuthService
from email_service import EmailService
from database_service import DatabaseService
from ai_service import AIService


# ================= APP INIT =================

app = Flask(__name__)
app.config.from_object(Config)

CORS(
    app,
    supports_credentials=True,
    origins=[
        "https://neeraj2007-ux.github.io",
        "http://localhost:5500",
        "http://127.0.0.1:5500"
    ]
)


# ================= SERVICES =================

auth_service = AuthService()
email_service = EmailService()
db_service = DatabaseService()
ai_service = AIService()


# ================= HEALTH CHECK =================

@app.route("/")
def home():
    return jsonify({
        "status": "Backend Running",
        "message": "Travel Planner API is live"
    })


# ================= AUTH HELPER =================

def get_auth():
    token = request.headers.get('Authorization', '')
    token = token.split(' ')[1] if ' ' in token else ''
    return auth_service.verify_jwt_token(token)


# =================================================
# ================= API ROUTES ====================
# =================================================

@app.route("/api/send-otp", methods=["POST"])
def send_otp():
    email = request.json.get("email", "").lower().strip()

    if not email:
        return jsonify({"success": False, "message": "Email required"}), 400

    otp = auth_service.generate_otp()
    auth_service.store_otp(email, otp)

    if email_service.send_otp_email(email, otp):
        return jsonify({"success": True, "message": "OTP sent"})

    print(f"OTP for {email}: {otp}")
    return jsonify({"success": True, "message": "OTP generated"})


@app.route("/api/verify-otp", methods=["POST"])
def verify_otp():
    data = request.json
    email = data.get("email", "").lower().strip()
    otp = data.get("otp", "").strip()

    success, msg = auth_service.verify_otp(email, otp)

    if success:
        user = db_service.get_user_by_email(email)
        if not user:
            db_service.create_user(email)

        token = auth_service.generate_jwt_token(email)

        return jsonify({
            "success": True,
            "token": token,
            "user": {"email": email}
        })

    return jsonify({"success": False, "message": msg}), 400


@app.route("/api/generate-trip", methods=["POST"])
def generate_trip():
    success, user = get_auth()
    if not success:
        return jsonify({"success": False}), 401

    data = request.json

    result = ai_service.generate_itinerary(
        data["destination"],
        float(data["budget"]),
        int(data["members"]),
        int(data["days"]),
        data["from"],
        data["accommodation"],
        data.get("interests", [])
    )

    trip_data = {
        "user_email": user["email"],
        "destination": data["destination"],
        "budget": data["budget"],
        "members": data["members"],
        "days": data["days"],
        "itinerary": result["itinerary"].get("itinerary", []),
        "recommendations": result["itinerary"].get("recommendations", {}),
        "budget_breakdown": result["itinerary"].get("estimated_costs", {})
    }

    db_service.create_trip(trip_data)
    email_service.send_booking_confirmation(user["email"], trip_data)

    return jsonify({"success": True, "trip": trip_data})


@app.route("/api/my-trips", methods=["GET"])
def my_trips():
    success, user = get_auth()
    if not success:
        return jsonify({"success": False}), 401

    trips = db_service.get_user_trips(user["email"])
    return jsonify({"success": True, "trips": trips})


# ================= RUN SERVER =================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
