import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config


class EmailService:
    def __init__(self):
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.gmail_user = Config.GMAIL_USER
        self.gmail_password = Config.GMAIL_PASSWORD

    # 🔥 SEND EMAIL IN BACKGROUND THREAD (CRITICAL FIX)
    def send_otp_email(self, to_email, otp):
        thread = threading.Thread(
            target=self._send_email_task,
            args=(to_email, otp),
            daemon=True
        )
        thread.start()
        return True

    def _send_email_task(self, to_email, otp):
        if not self.gmail_user or not self.gmail_password:
            print("❌ EMAIL CREDENTIALS MISSING")
            return False

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Your Travel Planner OTP'
            msg['From'] = self.gmail_user
            msg['To'] = to_email

            html_content = f"""
            <html>
            <body>
            <h2>Your OTP Code</h2>
            <h1>{otp}</h1>
            <p>Valid for 10 minutes</p>
            </body>
            </html>
            """

            msg.attach(MIMEText(html_content, 'html'))

            # 🔥 ADD TIMEOUT (CRITICAL)
            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10)
            server.starttls()
            server.login(self.gmail_user, self.gmail_password)
            server.send_message(msg)
            server.quit()

            print(f"✅ OTP sent to {to_email}")

        except Exception as e:
            print("❌ Email error:", str(e))
