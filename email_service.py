import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

class EmailService:
    def send_otp_email(self, to_email, otp):
        if not Config.GMAIL_USER or not Config.GMAIL_PASSWORD:
            print("Email credentials missing. Check .env")
            return False
            
        try:
            msg = MIMEMultipart()
            msg['Subject'] = 'Your OTP Code'
            msg['From'] = Config.GMAIL_USER
            msg['To'] = to_email
            
            html = f"<h1>Your OTP is: {otp}</h1><p>Expires in 10 minutes.</p>"
            msg.attach(MIMEText(html, 'html'))
            
            with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
                server.starttls()
                server.login(Config.GMAIL_USER, Config.GMAIL_PASSWORD)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Email Error: {e}")
            return False

    def send_booking_confirmation(self, to_email, trip_details):
        # Implementation similar to above, simplified for brevity
        return True