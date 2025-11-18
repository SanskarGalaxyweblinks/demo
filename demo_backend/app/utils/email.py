import os
import random
import string
import aiosmtplib
from email.message import EmailMessage

# --- Configuration ---
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "your-email@gmail.com")
SMTP_PASS = os.getenv("SMTP_PASS", "your-app-password")

# --- Helper Functions ---

def generate_otp(length=6):
    """Generates a random numeric OTP"""
    return ''.join(random.choices(string.digits, k=length))

async def send_verification_email(email: str, otp: str):
    """Sends the OTP verification email via SMTP"""
    msg = EmailMessage()
    msg["From"] = SMTP_USER
    msg["To"] = email
    msg["Subject"] = "Your verification code"
    msg.set_content(f"Use this code to finish logging in: {otp}")

    if not SMTP_USER or not SMTP_PASS:
        print(f"[MOCK EMAIL] To: {email}, OTP: {otp}")
        return

    await aiosmtplib.send(
        msg,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        start_tls=True,
        username=SMTP_USER,
        password=SMTP_PASS,
    )

async def send_password_reset_email(email: str, link: str):
    """Sends the password reset link via SMTP"""
    msg = EmailMessage()
    msg["From"] = SMTP_USER
    msg["To"] = email
    msg["Subject"] = "Reset Your Password"
    msg.set_content(f"Click the following link to reset your password: {link}")

    if not SMTP_USER or not SMTP_PASS:
        print(f"[MOCK EMAIL] To: {email}, Link: {link}")
        return

    await aiosmtplib.send(
        msg,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        start_tls=True,
        username=SMTP_USER,
        password=SMTP_PASS,
    )