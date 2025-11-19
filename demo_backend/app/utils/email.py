# demo_backend/app/utils/email.py
import os
import random
import string
import aiosmtplib
from email.message import EmailMessage

# --- Configuration Fetching ---
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")

def generate_otp(length=6):
    """Generates a random 6-digit OTP."""
    return ''.join(random.choices(string.digits, k=length))

async def send_email(to_email: str, subject: str, body: str):
    """Generic function to send an email."""
    if not SMTP_USER or not SMTP_PASS:
        print(f"⚠️ [EMAIL MOCK] To: {to_email} | Subject: {subject} | Body: {body}")
        print("   (Email not sent because SMTP_USER or SMTP_PASS is missing in .env)")
        return

    msg = EmailMessage()
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        await aiosmtplib.send(
            msg,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            start_tls=True,
            username=SMTP_USER,
            password=SMTP_PASS,
            validate_certs=False,  # CHANGED: Disable cert validation for local dev
        )
        print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# --- Functions called by auth.py ---

async def send_verification_email(email: str, otp: str):
    subject = "Your Verification Code"
    body = f"Your verification code for Jupiter AI is: {otp}"
    await send_email(email, subject, body)

async def send_password_reset_email(email: str, link: str):
    subject = "Reset Your Password"
    body = f"Click the link to reset your password: {link}\n\nIf you did not request this, please ignore this email."
    await send_email(email, subject, body)