# app/services/response_service.py
from __future__ import annotations

import random
import textwrap
from datetime import datetime
from typing import Any, Dict

# KYC-specific notification templates
NOTIFICATION_TEMPLATES = {
    "onboarding_received": {
        "subject": "KYC Application Received - {customer_name}",
        "template": """
        Dear {customer_name},

        Thank you for submitting your KYC application on {date}. We have successfully received your documents and begun the verification process.

        Documents received:
        {document_list}

        Your application reference: {reference_id}
        Expected processing time: 2-3 business days

        We will notify you once your verification is complete. If you have any questions, please reference your application ID in all correspondence.

        Best regards,
        JupiterBrains Compliance Team
        """
    },
    "verification_complete": {
        "subject": "KYC Verification Complete - {customer_name}",
        "template": """
        Dear {customer_name},

        Congratulations! Your KYC verification has been successfully completed on {date}.

        Your account is now fully activated and you can access all services.

        Account Details:
        • Customer ID: {customer_id}
        • Verification Level: Tier 1 Complete
        • Account Status: Active

        Welcome to JupiterBrains! 

        Best regards,
        JupiterBrains Customer Success Team
        """
    },
    "verification_failed": {
        "subject": "KYC Verification - Additional Information Required",
        "template": """
        Dear {customer_name},

        We have reviewed your KYC application submitted on {date}. Unfortunately, we need additional information to complete your verification.

        Issues identified:
        {issue_list}

        Next steps:
        • Please resubmit the requested documents
        • Ensure all documents are clear and unedited
        • Reference your application ID: {reference_id}

        Our team is available to assist you with any questions.

        Best regards,
        JupiterBrains Compliance Team
        """
    },
    "document_flagged": {
        "subject": "Document Review Required - {customer_name}",
        "template": """
        Dear {customer_name},

        During our automated document verification process, we have flagged some documents for manual review.

        This is a standard security procedure and does not necessarily indicate any issues with your application.

        What happens next:
        • Our compliance team will manually review your documents
        • You will receive an update within 5 business days
        • No action is required from you at this time

        Reference ID: {reference_id}

        Thank you for your patience.

        Best regards,
        JupiterBrains Security Team
        """
    }
}

async def send_customer_notification(
    customer_email: str,
    notification_type: str,
    context_data: Dict[str, Any],
    user: Any | None = None
) -> Dict[str, Any]:
    """
    Send automated notifications to customers during KYC process.
    
    Args:
        customer_email: Customer's email address
        notification_type: Type of notification (onboarding_received, verification_complete, etc.)
        context_data: Data to populate the template
        user: User who triggered the notification
    
    Returns:
        Dict with notification status and details
    """
    if notification_type not in NOTIFICATION_TEMPLATES:
        raise ValueError(f"Unknown notification type: {notification_type}")
    
    template_info = NOTIFICATION_TEMPLATES[notification_type]
    
    # Format the email content
    subject = template_info["subject"].format(**context_data)
    body = template_info["template"].format(**context_data).strip()
    
    # Simulate sending email (in real implementation, use actual email service)
    message_id = f"msg_{random.randint(100000, 999999)}"
    sent_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # Log the notification (in real implementation, save to database)
    print(f"Sending KYC notification: {notification_type} to {customer_email}")
    print(f"Subject: {subject}")
    
    return {
        "message_id": message_id,
        "sent_at": sent_at,
        "customer_email": customer_email,
        "notification_type": notification_type,
        "status": "sent"
    }

def generate_kyc_response(email_category: str, customer_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate automated responses based on KYC email classification.
    
    Args:
        email_category: Category from email classification (Onboarding/Dispute/Other)
        customer_data: Customer information and context
    
    Returns:
        Generated response and metadata
    """
    customer_name = customer_data.get("name", "Valued Customer")
    
    if email_category == "Onboarding":
        response = textwrap.dedent(f"""
        Dear {customer_name},
        
        Thank you for your interest in opening an account with JupiterBrains.
        
        To complete your KYC verification, please provide:
        • Government-issued photo ID (driver's license or passport)
        • Proof of address (utility bill or bank statement)
        • Completed application form
        
        You can submit these documents by replying to this email or through our secure portal.
        
        Processing time: 2-3 business days
        
        Best regards,
        JupiterBrains Onboarding Team
        """).strip()
        
    elif email_category == "Dispute":
        response = textwrap.dedent(f"""
        Dear {customer_name},
        
        We have received your dispute regarding your KYC verification decision.
        
        Our compliance team will review your case within 5 business days. We may request additional documentation to support your appeal.
        
        Please reference your case number in all future correspondence: DISP-{random.randint(10000, 99999)}
        
        We appreciate your patience during this review process.
        
        Best regards,
        JupiterBrains Compliance Team
        """).strip()
        
    else:  # Other
        response = textwrap.dedent(f"""
        Dear {customer_name},
        
        Thank you for contacting JupiterBrains.
        
        For KYC-related inquiries, please visit our help center or contact our dedicated KYC support team at kyc-support@jupiterbrains.com.
        
        For general questions, our customer service team will respond within 24 hours.
        
        Best regards,
        JupiterBrains Customer Service
        """).strip()
    
    return {
        "response": response,
        "category": email_category,
        "tokens_used": len(response.split()),
        "processing_time": round(random.uniform(0.1, 0.5), 2)
    }

# Legacy function for backward compatibility
def generate_response(message: str, tone: str | None, user: dict[str, Any] | None):
    """Legacy function - deprecated in favor of KYC-specific notifications"""
    return {
        "response": "This function has been replaced with KYC-specific notification system.",
        "tone": tone or "professional", 
        "tokens_used": 20,
        "latency_ms": 100,
        "deprecated": True
    }