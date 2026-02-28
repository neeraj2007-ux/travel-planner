import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

class EmailService:
    def __init__(self):
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.gmail_user = Config.GMAIL_USER
        self.gmail_password = Config.GMAIL_PASSWORD
    
    def send_otp_email(self, to_email, otp):
        if not self.gmail_user or not self.gmail_password:
            print("⚠️ EMAIL CREDENTIALS MISSING: Cannot send OTP email.")
            return False

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Your Travel Planner OTP'
            msg['From'] = self.gmail_user
            msg['To'] = to_email
            
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
                    <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
                        <h2 style="color: #333;">Your Login Code</h2>
                        <div style="background: #667eea; color: white; padding: 20px; text-align: center; font-size: 36px; font-weight: bold; border-radius: 8px; margin: 25px 0; letter-spacing: 8px;">
                            {otp}
                        </div>
                        <p>This code will expire in 10 minutes.</p>
                        <p style="color: #999; font-size: 12px;">TravelBuddy AI Planner</p>
                    </div>
                </body>
            </html>
            """
            
            part = MIMEText(html_content, 'html')
            msg.attach(part)
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.gmail_user, self.gmail_password)
            server.send_message(msg)
            server.quit()
            print(f"✅ OTP sent to {to_email}")
            return True
        except Exception as e:
            print(f"❌ Error sending email: {str(e)}")
            return False

    def send_booking_confirmation(self, to_email, trip):
        if not self.gmail_user: return False
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'Trip Plan: {trip["destination"]}'
            msg['From'] = self.gmail_user
            msg['To'] = to_email
            
            html = f"""
            <html><body>
                <h1>Trip to {trip['destination']}</h1>
                <p>Budget: ₹{trip['budget']}</p>
                <p>Your itinerary is saved in your dashboard.</p>
            </body></html>
            """
            msg.attach(MIMEText(html, 'html'))
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.gmail_user, self.gmail_password)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"❌ Error sending booking confirmation email: {e}")
            return False