import random
import string
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from ..config import settings

# Configure the connection using settings from config.py
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False  # Set to False for local dev to avoid SSL errors
)

def generate_otp(length: int = 6) -> str:
    """Generate a random numeric OTP."""
    return "".join(random.choices(string.digits, k=length))

async def send_verification_email(email_to: str, otp: str):
    """Sends a verification email with the OTP using HTML template."""
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 8px;">
                <h2 style="color: #2563eb; text-align: center;">Welcome to Jupiter Brains</h2>
                <p>Thank you for registering. Please use the following One-Time Password (OTP) to verify your email address:</p>
                
                <div style="background-color: #f3f4f6; padding: 15px; border-radius: 6px; text-align: center; margin: 20px 0;">
                    <h3 style="font-size: 24px; letter-spacing: 4px; margin: 0; color: #111;">{otp}</h3>
                </div>
                
                <p style="color: #666; font-size: 14px;">This OTP will expire in 10 minutes.</p>
                <p style="color: #666; font-size: 14px;">If you did not request this, please ignore this email.</p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="font-size: 12px; color: #999; text-align: center;">Jupiter Brains Inc.</p>
            </div>
        </body>
    </html>
    """
    
    message = MessageSchema(
        subject="Your Email Verification Code",
        recipients=[email_to],
        body=html_content,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)

async def send_password_reset_email(email_to: str, reset_link: str):
    """Sends a password reset email with a link."""
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 8px;">
                <h2 style="color: #dc2626; text-align: center;">Password Reset Request</h2>
                <p>You are receiving this email because a password reset was requested for your account.</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_link}" style="background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">Reset Password</a>
                </div>
                
                <p style="word-break: break-all; font-size: 13px; color: #666;">
                    Or copy this link: <br>
                    <a href="{reset_link}">{reset_link}</a>
                </p>
                
                <p style="color: #666; font-size: 14px;">This link will expire in 15 minutes.</p>
                <p style="color: #666; font-size: 14px;">If you did not request this, please ignore this email.</p>
            </div>
        </body>
    </html>
    """
    
    message = MessageSchema(
        subject="Your Password Reset Link",
        recipients=[email_to],
        body=html_content,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)