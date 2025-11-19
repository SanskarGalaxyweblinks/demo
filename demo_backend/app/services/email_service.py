# app/services/email_service.py
from __future__ import annotations

import os
import json
import time
from typing import Any, Dict
from groq import Groq

# Initialize Groq client
def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")
    return Groq(api_key=api_key)

# Advanced prompts for KYC email classification
EMAIL_CLASSIFICATION_SYSTEM_PROMPT = """
You are an expert AI system for KYC (Know Your Customer) email classification in the financial services industry. 
Your task is to analyze customer emails and classify them into specific categories for automated processing.

CLASSIFICATION CATEGORIES:
1. "Onboarding" - New customer account applications, KYC document submissions, identity verification requests
2. "Dispute" - Account verification disputes, rejection appeals, complaint about KYC process
3. "Other" - General inquiries, questions about requirements, support requests

PRIORITY LEVELS:
- "High" - Urgent requests, disputes, rejected applications, time-sensitive matters
- "Medium" - Standard applications, follow-ups, document resubmissions  
- "Low" - General questions, informational requests

SENTIMENT ANALYSIS:
- "Positive" - Appreciative, cooperative, satisfied tone
- "Negative" - Frustrated, angry, disappointed, complaint tone
- "Neutral" - Professional, matter-of-fact, informational tone

EXTRACT RELEVANT TAGS from content such as:
- "documents_attached" if attachments mentioned
- "urgent_request" if urgency indicated
- "new_customer" if first-time application
- "existing_customer" if ongoing relationship
- "compliance_issue" if regulatory concerns
- "technical_issue" if system/process problems

You must respond in valid JSON format only. Provide detailed reasoning for your classification.
"""

EMAIL_CLASSIFICATION_USER_PROMPT = """
Analyze this customer email for KYC classification:

SUBJECT: {subject}

BODY: {body}

Respond with a JSON object containing:
{{
    "category": "Onboarding|Dispute|Other",
    "priority": "High|Medium|Low", 
    "sentiment": "Positive|Negative|Neutral",
    "confidence": 0.0-1.0,
    "tags": ["relevant", "tags", "here"],
    "reasoning": "Detailed explanation of classification decision"
}}

Focus on the customer's intent, urgency, emotional tone, and any KYC-related keywords or phrases.
"""

def classify_email(subject: str, body: str, user: Dict[str, Any] | None) -> Dict[str, Any]:
    """
    Classify emails into KYC categories using Groq API for real AI analysis.
    """
    start_time = time.time()
    
    try:
        # Initialize Groq client
        client = get_groq_client()
        
        # Format the prompt with actual email content
        user_prompt = EMAIL_CLASSIFICATION_USER_PROMPT.format(
            subject=subject,
            body=body
        )
        
        # Call Groq API
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": EMAIL_CLASSIFICATION_SYSTEM_PROMPT
                },
                {
                    "role": "user", 
                    "content": user_prompt
                }
            ],
            model="llama-3.1-20b-versatile",  # Use the most capable model
            temperature=0.1,  # Low temperature for consistent classification
            max_tokens=500,
            response_format={"type": "json_object"}  # Ensure JSON response
        )
        
        # Parse the response
        response_content = chat_completion.choices[0].message.content
        ai_result = json.loads(response_content)
        
        # Add additional context tags
        additional_tags = []
        content = f"{subject} {body}".lower()
        
        if user:
            additional_tags.append("authenticated_user")
        if any(word in content for word in ["attach", "attached", "document", "file"]):
            additional_tags.append("documents_mentioned")
        if any(word in content for word in ["asap", "urgent", "immediately", "emergency"]):
            additional_tags.append("urgent_request")
        if any(word in content for word in ["new", "first", "initial", "opening"]):
            additional_tags.append("new_customer")
        
        # Merge AI tags with additional context tags
        all_tags = list(set(ai_result.get("tags", []) + additional_tags))
        
        processing_time = time.time() - start_time
        
        return {
            "category": ai_result.get("category", "Other"),
            "priority": ai_result.get("priority", "Medium"),
            "sentiment": ai_result.get("sentiment", "Neutral"),
            "confidence": float(ai_result.get("confidence", 0.85)),
            "tags": sorted(all_tags),
            "reasoning": ai_result.get("reasoning", "AI classification completed"),
            "processing_time": round(processing_time, 2)
        }
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        return _fallback_classification(subject, body, user)
    except Exception as e:
        print(f"Groq API error: {e}")
        return _fallback_classification(subject, body, user)

def _fallback_classification(subject: str, body: str, user: Any) -> Dict[str, Any]:
    """
    Fallback classification using keyword matching if Groq API fails.
    """
    print("[EMAIL] Using fallback classification due to API error")
    
    content = f"{subject} {body}".lower()
    
    # Simple keyword-based classification
    if any(word in content for word in ["kyc", "onboard", "verification", "application", "new account"]):
        category = "Onboarding"
        priority = "High" if any(word in content for word in ["urgent", "asap"]) else "Medium"
    elif any(word in content for word in ["dispute", "appeal", "rejected", "complaint", "error"]):
        category = "Dispute" 
        priority = "High"
    else:
        category = "Other"
        priority = "Low"
    
    sentiment = "Negative" if any(word in content for word in ["angry", "frustrated", "upset"]) else "Neutral"
    
    tags = ["fallback_classification"]
    if user:
        tags.append("authenticated_user")
    
    return {
        "category": category,
        "priority": priority,
        "sentiment": sentiment,
        "confidence": 0.75,
        "tags": tags,
        "reasoning": "Classified using fallback keyword analysis due to API unavailability",
        "processing_time": 0.1
    }

# Legacy function for backward compatibility
async def classify_email_chain(subject: str, body: str) -> Dict[str, Any]:
    """
    Legacy wrapper function for backward compatibility.
    """
    result = classify_email(subject, body, None)
    
    return {
        "category": result["category"],
        "reasoning": result["reasoning"],
        "summary": f"Email classified as {result['category']} with {result['confidence']:.1%} confidence",
        "processing_time": result["processing_time"]
    }