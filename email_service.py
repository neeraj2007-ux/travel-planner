"""
Email service for sending OTP via Gmail SMTP
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

class EmailService:
    """Handle email sending via Gmail SMTP"""
    
    def __init__(self):
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.gmail_user = Config.GMAIL_USER
        self.gmail_password = Config.GMAIL_PASSWORD
    
    def send_otp_email(self, to_email, otp):
        """
        Send OTP to user's email
        
        Args:
            to_email (str): Recipient email address
            otp (str): 6-digit OTP code
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Your Travel Planner OTP'
            msg['From'] = self.gmail_user
            msg['To'] = to_email
            
            # HTML email template
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
                    <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        <div style="text-align: center; margin-bottom: 30px;">
                            <h1 style="color: #667eea; margin: 0;">✈️ TravelBuddy</h1>
                            <p style="color: #666; margin: 5px 0;">AI Travel Planner for Students</p>
                        </div>
                        
                        <h2 style="color: #333; margin-bottom: 20px;">Your Login Code</h2>
                        
                        <p style="color: #555; font-size: 16px; line-height: 1.6;">
                            Use this code to complete your login:
                        </p>
                        
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; font-size: 36px; font-weight: bold; border-radius: 8px; margin: 25px 0; letter-spacing: 8px;">
                            {otp}
                        </div>
                        
                        <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 4px;">
                            <p style="margin: 0; color: #856404; font-size: 14px;">
                                ⚠️ This code will expire in <strong>10 minutes</strong>
                            </p>
                        </div>
                        
                        <p style="color: #666; font-size: 14px; line-height: 1.6;">
                            If you didn't request this code, please ignore this email. 
                            Your account security is important to us.
                        </p>
                        
                        <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 30px 0;">
                        
                        <p style="color: #999; font-size: 12px; text-align: center; margin: 0;">
                            TravelBuddy - Making student travel affordable and easy<br>
                            © 2024 TravelBuddy. All rights reserved.
                        </p>
                    </div>
                </body>
            </html>
            """
            
            # Attach HTML content
            part = MIMEText(html_content, 'html')
            msg.attach(part)
            
            # Connect to Gmail SMTP server and send
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.gmail_user, self.gmail_password)
            server.send_message(msg)
            server.quit()
            
            print(f"OTP email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
    
    def send_booking_confirmation(self, to_email, trip_details):
        """
        Send booking confirmation email
        
        Args:
            to_email (str): Recipient email address
            trip_details (dict): Trip information
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'Trip Booking Confirmed - {trip_details["destination"]}'
            msg['From'] = self.gmail_user
            msg['To'] = to_email
            
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
                    <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
                        <h1 style="color: #667eea;">🎉 Booking Confirmed!</h1>
                        <h2>Trip to {trip_details['destination']}</h2>
                        <p><strong>Duration:</strong> {trip_details['days']} days</p>
                        <p><strong>Travelers:</strong> {trip_details['members']} person(s)</p>
                        <p><strong>Total Budget:</strong> ₹{trip_details['budget']}</p>
                        <hr>
                        <p>Your trip plan is ready! Check your dashboard for full itinerary.</p>
                        <p style="color: #666; font-size: 12px;">TravelBuddy - AI Travel Planner</p>
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
            
            return True
            
        except Exception as e:
            print(f"Error sending confirmation email: {str(e)}")
            return False
