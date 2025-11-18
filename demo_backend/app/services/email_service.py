from __future__ import annotations

import re
from typing import Any

KEYWORD_CATEGORIES = {
    "Billing": ["invoice", "payment", "billing", "overdue", "statement"],
    "Customer Support": ["issue", "support", "help", "problem", "bug", "error"],
    "Sales": ["quote", "pricing", "purchase", "order", "discount"],
    "Logistics": ["shipment", "delivery", "tracking", "warehouse"],
}

PRIORITY_RULES = {
    "High": ["urgent", "immediately", "asap", "critical"],
    "Medium": ["soon", "follow up", "schedule"],
}

SENTIMENT_RULES = {
    "Negative": ["unhappy", "disappointed", "frustrated"],
    "Positive": ["thank", "great", "appreciate", "happy"],
}


def classify_email(subject: str, body: str, user: dict[str, Any] | None) -> dict[str, Any]:
    content = f"{subject} {body}".lower()

    category = "General"
    for name, keywords in KEYWORD_CATEGORIES.items():
        if any(keyword in content for keyword in keywords):
            category = name
            break

    priority = "Low"
    for level, keywords in PRIORITY_RULES.items():
        if any(keyword in content for keyword in keywords):
            priority = level
            break
    sentiment = "Neutral"
    for label, keywords in SENTIMENT_RULES.items():
        if any(keyword in content for keyword in keywords):
            sentiment = label
            break

    tags = set()
    if user:
        tags.add("authenticated")
    if re.search(r"\bETA\b", content):
        tags.add("timeline")
    if "$" in content or "usd" in content:
        tags.add("finance")

    confidence = 0.65
    if priority == "High":
        confidence += 0.15
    if sentiment != "Neutral":
        confidence += 0.05
    confidence = min(confidence, 0.98)

    return {
        "category": category,
        "priority": priority,
        "sentiment": sentiment,
        "confidence": round(confidence, 2),
        "tags": sorted(tags),
    }


