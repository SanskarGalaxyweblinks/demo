# app/services/email_service.py
from __future__ import annotations

import re
import time
from typing import Any

# KYC-specific keyword categories
KYC_KEYWORDS = {
    "Onboarding": [
        "new account", "open account", "kyc", "verification", "onboard", 
        "customer application", "register", "signup", "identity verification",
        "documents attached", "driver license", "passport", "bank statement",
        "complete verification", "account opening", "new customer"
    ],
    "Dispute": [
        "dispute", "appeal", "rejected", "denied", "reconsider", "error",
        "incorrect", "wrong decision", "review again", "challenge",
        "complaint", "disagree", "unfair", "mistake", "resubmit"
    ],
    "Other": [
        "question", "information", "help", "support", "inquiry", "general",
        "how to", "what is", "can you", "please explain", "requirements"
    ]
}

PRIORITY_KEYWORDS = {
    "High": ["urgent", "immediately", "asap", "critical", "dispute", "rejected"],
    "Medium": ["soon", "follow up", "schedule", "review"],
}

SENTIMENT_KEYWORDS = {
    "Negative": ["unhappy", "disappointed", "frustrated", "angry", "upset"],
    "Positive": ["thank", "great", "appreciate", "happy", "excellent"],
}

def classify_email(subject: str, body: str, user: dict[str, Any] | None) -> dict[str, Any]:
    """
    Classify emails into KYC categories using keyword matching and rules.
    Simple, fast, and cost-effective approach for demo purposes.
    """
    start_time = time.time()
    
    # Combine subject and body for analysis
    content = f"{subject} {body}".lower()
    
    # Step 1: Determine KYC category
    category = "Other"  # Default
    category_confidence = 0.0
    
    for cat_name, keywords in KYC_KEYWORDS.items():
        matches = sum(1 for keyword in keywords if keyword in content)
        confidence = min(matches / len(keywords), 1.0)
        
        if confidence > category_confidence:
            category_confidence = confidence
            category = cat_name
    
    # Step 2: Determine priority
    priority = "Low"  # Default
    for level, keywords in PRIORITY_KEYWORDS.items():
        if any(keyword in content for keyword in keywords):
            priority = level
            break
    
    # Step 3: Determine sentiment
    sentiment = "Neutral"  # Default
    for sent, keywords in SENTIMENT_KEYWORDS.items():
        if any(keyword in content for keyword in keywords):
            sentiment = sent
            break
    
    # Step 4: Extract tags
    tags = set()
    if user:
        tags.add("authenticated")
    
    # Add specific tags based on content
    if re.search(r'\battach', content):
        tags.add("has_attachments")
    if any(doc in content for doc in ["license", "passport", "id", "invoice"]):
        tags.add("documents_mentioned")
    if "$" in content or "usd" in content or "amount" in content:
        tags.add("financial")
    if any(word in content for word in ["deadline", "expires", "urgent"]):
        tags.add("time_sensitive")
    
    # Step 5: Calculate overall confidence
    base_confidence = 0.7
    if category != "Other":
        base_confidence += 0.15  # Boost if we found a specific category
    if priority == "High":
        base_confidence += 0.1
    if len(tags) > 1:
        base_confidence += 0.05
    
    confidence = min(base_confidence, 0.98)
    
    processing_time = time.time() - start_time
    
    return {
        "category": category,
        "priority": priority,
        "sentiment": sentiment,
        "confidence": round(confidence, 2),
        "tags": sorted(list(tags)),
        "processing_time": round(processing_time, 2)
    }

# Legacy function name for compatibility
async def classify_email_chain(subject: str, body: str) -> dict:
    """
    Legacy wrapper function for backward compatibility.
    Calls the new classify_email function.
    """
    result = classify_email(subject, body, None)
    
    # Add legacy fields for compatibility
    return {
        "category": result["category"],
        "reasoning": f"Classified as {result['category']} based on keyword analysis and content patterns",
        "summary": f"Email content analyzed for KYC classification. Priority: {result['priority']}, Sentiment: {result['sentiment']}",
        "processing_time": result["processing_time"]
    }