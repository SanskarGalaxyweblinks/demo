from __future__ import annotations

import random
import textwrap
from datetime import datetime
from typing import Any

TONE_PREFIX = {
    "professional": "Dear {name},",
    "casual": "Hi {name},",
    "friendly": "Hello {name},",
}


def generate_response(message: str, tone: str | None, user: dict[str, Any] | None):
    tone = (tone or "professional").lower()
    if tone not in TONE_PREFIX:
        tone = "professional"

    recipient = "Valued Customer"
    if "john" in message.lower():
        recipient = "John"
    if "team" in message.lower():
        recipient = "Team"

    prefix = TONE_PREFIX[tone].format(name=recipient)
    closing = "Best regards"
    if tone == "casual":
        closing = "Thanks"
    elif tone == "friendly":
        closing = "Warm regards"

    signature = "JupiterBrains Support"
    if user:
        signature = user["full_name"] or user["email"]

    body = textwrap.dedent(
        f"""
        {prefix}

        Thank you for contacting us. Our system received your message on {datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC")} and it is now in review.

        Key details we understood:
        • Primary intent: {infer_intent(message)}
        • Urgency: {detect_urgency(message)}

        We will follow up with any next steps shortly. If you have supporting documents, feel free to reply to this email and attach them for faster processing.

        {closing},
        {signature}
        """
    ).strip()

    tokens_used = len(message.split()) + 120
    latency_ms = random.randint(450, 1200)

    return {
        "response": body,
        "tone": tone,
        "tokens_used": tokens_used,
        "latency_ms": latency_ms,
    }


def infer_intent(message: str) -> str:
    lowered = message.lower()
    if any(word in lowered for word in ["refund", "return"]):
        return "Refund inquiry"
    if any(word in lowered for word in ["quote", "pricing", "plan"]):
        return "Pricing request"
    if any(word in lowered for word in ["error", "bug", "issue"]):
        return "Support ticket"
    return "General inquiry"


def detect_urgency(message: str) -> str:
    lowered = message.lower()
    if any(word in lowered for word in ["urgent", "asap", "immediately"]):
        return "High"
    if any(word in lowered for word in ["soon", "next week"]):
        return "Medium"
    return "Normal"


