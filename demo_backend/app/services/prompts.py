# demo_backend/app/services/prompts.py
"""
Optimized prompts for KYC AI processing using Groq API.
Contains system and user prompts for email classification and document analysis.
"""

# =============================================================================
# EMAIL CLASSIFICATION PROMPTS
# =============================================================================

EMAIL_CLASSIFICATION_SYSTEM_PROMPT = """
You are an expert AI system for KYC (Know Your Customer) email classification in the financial services industry. 
Your task is to analyze customer emails and classify them into specific categories for automated processing.

CLASSIFICATION CATEGORIES (REQUIRED - pick exactly one):
1. "Onboarding" - New customer account applications, KYC document submissions, identity verification requests, account opening requests
2. "Dispute" - Account verification disputes, rejection appeals, complaints about KYC process, requests for reconsideration
3. "Other" - General inquiries, questions about requirements, support requests, informational queries

PRIORITY LEVELS (REQUIRED - pick exactly one):
- "High" - Urgent requests, disputes, rejected applications, time-sensitive matters, complaints
- "Medium" - Standard applications, follow-ups, document resubmissions, routine inquiries  
- "Low" - General questions, informational requests, non-urgent support

SENTIMENT ANALYSIS (REQUIRED - pick exactly one):
- "Positive" - Appreciative, cooperative, satisfied, thankful tone
- "Negative" - Frustrated, angry, disappointed, complaint tone, dissatisfied
- "Neutral" - Professional, matter-of-fact, informational, business-like tone

EXTRACT RELEVANT TAGS from content (include any that apply):
- "documents_attached" if attachments mentioned
- "urgent_request" if urgency indicated  
- "new_customer" if first-time application
- "existing_customer" if ongoing relationship mentioned
- "compliance_issue" if regulatory concerns
- "technical_issue" if system/process problems
- "resubmission" if re-sending documents
- "deadline_mentioned" if time constraints noted
- "financial_documents" if bank statements, invoices mentioned
- "id_documents" if passport, license, ID mentioned

IMPORTANT: You must respond in valid JSON format only. Provide detailed reasoning for your classification decisions.
"""

EMAIL_CLASSIFICATION_USER_PROMPT = """
Analyze this customer email for KYC classification:

SUBJECT: {subject}

BODY: {body}

Respond with a JSON object containing exactly these fields:
{{
    "category": "Onboarding|Dispute|Other",
    "priority": "High|Medium|Low", 
    "sentiment": "Positive|Negative|Neutral",
    "confidence": 0.0-1.0,
    "tags": ["relevant", "tags", "here"],
    "reasoning": "Detailed explanation of classification decision including specific keywords and context that led to this classification"
}}

Focus on the customer's intent, urgency level, emotional tone, and any KYC-related keywords or phrases. 
Consider document attachments, deadlines, and compliance requirements when determining priority.
"""

# =============================================================================
# DOCUMENT ANALYSIS PROMPTS  
# =============================================================================

DOCUMENT_ANALYSIS_SYSTEM_PROMPT = """
You are an expert AI system for KYC document analysis. Your task is to extract critical information from identity documents and financial documents for customer onboarding and compliance.

DOCUMENT TYPES TO IDENTIFY (pick the most specific):
- "ID_Document" - Driver's licenses, passports, national IDs, state IDs, voter cards
- "Financial_Document" - Bank statements, invoices, receipts, tax documents, pay stubs
- "Proof_of_Address" - Utility bills, lease agreements, official correspondence with address
- "Business_Document" - Business licenses, incorporation papers, tax certificates
- "Other" - Any document that doesn't clearly fit the above categories

FOR ID DOCUMENTS, EXTRACT (use null if not found):
- Full name (first and last name)
- Date of birth (in YYYY-MM-DD format if possible)
- Document number (license number, passport number, etc.)
- Document type (Driver License, Passport, National ID, etc.)
- Issuing authority (DMV, State Department, etc.)
- Expiry date (in YYYY-MM-DD format if possible)  
- Address (if present on document)

FOR FINANCIAL DOCUMENTS, EXTRACT (use null if not found):
- Company/institution name
- Document number (invoice #, account #, statement #)
- Date (in YYYY-MM-DD format if possible)
- Amount/balance (numerical value)
- Currency (USD, EUR, GBP, etc.)
- Account holder name
- Account number (if applicable)

FOR PROOF OF ADDRESS, EXTRACT (use null if not found):
- Name on document
- Full address
- Document date (in YYYY-MM-DD format if possible)
- Issuing company/authority
- Service type (electricity, gas, internet, etc.)

IMPORTANT: You must respond in valid JSON format only. Extract actual data from the document text provided.
"""

DOCUMENT_ANALYSIS_USER_PROMPT = """
Analyze this document text for KYC data extraction:

DOCUMENT TEXT:
{document_text}

FILENAME: {filename}

Respond with a JSON object containing exactly these fields:
{{
    "document_type": "ID_Document|Financial_Document|Proof_of_Address|Business_Document|Other",
    "extracted_entities": ["Entity 1: Value 1", "Entity 2: Value 2", "..."],
    "structured_data": {{
        "field_name": "actual_extracted_value",
        "field_name2": "actual_extracted_value2"
    }},
    "confidence": 0.0-1.0,
    "summary": "Brief description of document content and what was extracted"
}}

Extract all relevant KYC information from the actual document text. Use null for fields that cannot be found.
Create extracted_entities as "Field: Value" pairs for easy reading.
Set confidence based on how clearly the information could be extracted from the text.
"""

# =============================================================================
# PROMPT TEMPLATES
# =============================================================================

def format_email_classification_prompt(subject: str, body: str) -> tuple[str, str]:
    """Format email classification prompts with actual content"""
    system_prompt = EMAIL_CLASSIFICATION_SYSTEM_PROMPT
    user_prompt = EMAIL_CLASSIFICATION_USER_PROMPT.format(
        subject=subject,
        body=body
    )
    return system_prompt, user_prompt

def format_document_analysis_prompt(document_text: str, filename: str) -> tuple[str, str]:
    """Format document analysis prompts with actual content"""
    system_prompt = DOCUMENT_ANALYSIS_SYSTEM_PROMPT
    user_prompt = DOCUMENT_ANALYSIS_USER_PROMPT.format(
        document_text=document_text,
        filename=filename
    )
    return system_prompt, user_prompt

# =============================================================================
# RESPONSE VALIDATION SCHEMAS
# =============================================================================

EMAIL_CLASSIFICATION_SCHEMA = {
    "category": ["Onboarding", "Dispute", "Other"],
    "priority": ["High", "Medium", "Low"],
    "sentiment": ["Positive", "Negative", "Neutral"],
    "confidence": {"type": "float", "min": 0.0, "max": 1.0},
    "tags": {"type": "list"},
    "reasoning": {"type": "string", "min_length": 10}
}

DOCUMENT_ANALYSIS_SCHEMA = {
    "document_type": ["ID_Document", "Financial_Document", "Proof_of_Address", "Business_Document", "Other"],
    "extracted_entities": {"type": "list"},
    "structured_data": {"type": "dict"},
    "confidence": {"type": "float", "min": 0.0, "max": 1.0},
    "summary": {"type": "string", "min_length": 10}
}

def validate_email_response(response_data: dict) -> bool:
    """Validate email classification response format"""
    try:
        # Check required fields exist
        required_fields = ["category", "priority", "sentiment", "confidence", "tags", "reasoning"]
        for field in required_fields:
            if field not in response_data:
                return False
        
        # Validate category
        if response_data["category"] not in EMAIL_CLASSIFICATION_SCHEMA["category"]:
            return False
        
        # Validate priority  
        if response_data["priority"] not in EMAIL_CLASSIFICATION_SCHEMA["priority"]:
            return False
        
        # Validate sentiment
        if response_data["sentiment"] not in EMAIL_CLASSIFICATION_SCHEMA["sentiment"]:
            return False
        
        # Validate confidence
        confidence = response_data["confidence"]
        if not isinstance(confidence, (int, float)) or confidence < 0.0 or confidence > 1.0:
            return False
        
        # Validate tags is list
        if not isinstance(response_data["tags"], list):
            return False
        
        # Validate reasoning has content
        if not isinstance(response_data["reasoning"], str) or len(response_data["reasoning"]) < 10:
            return False
        
        return True
        
    except Exception:
        return False

def validate_document_response(response_data: dict) -> bool:
    """Validate document analysis response format"""
    try:
        # Check required fields exist
        required_fields = ["document_type", "extracted_entities", "structured_data", "confidence", "summary"]
        for field in required_fields:
            if field not in response_data:
                return False
        
        # Validate document_type
        if response_data["document_type"] not in DOCUMENT_ANALYSIS_SCHEMA["document_type"]:
            return False
        
        # Validate extracted_entities is list
        if not isinstance(response_data["extracted_entities"], list):
            return False
        
        # Validate structured_data is dict
        if not isinstance(response_data["structured_data"], dict):
            return False
        
        # Validate confidence
        confidence = response_data["confidence"]
        if not isinstance(confidence, (int, float)) or confidence < 0.0 or confidence > 1.0:
            return False
        
        # Validate summary has content
        if not isinstance(response_data["summary"], str) or len(response_data["summary"]) < 10:
            return False
        
        return True
        
    except Exception:
        return False