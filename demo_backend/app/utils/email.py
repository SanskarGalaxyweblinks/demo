import random
import string

def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))

async def send_verification_email(email_to: str, otp: str):
    # Integrate SendGrid, AWS SES, or SMTP here
    print(f"--- EMAIL SIMULATION ---")
    print(f"To: {email_to}")
    print(f"Subject: Verify your account")
    print(f"Code: {otp}")
    print(f"------------------------")

async def send_password_reset_email(email_to: str, link: str):
    print(f"--- EMAIL SIMULATION ---")
    print(f"To: {email_to}")
    print(f"Subject: Password Reset")
    print(f"Link: {link}")
    print(f"------------------------")