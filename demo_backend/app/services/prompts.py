# app/services/prompts.py

EMAIL_INFERENCE_PROMPT = """
You are an expert at understanding business emails in a debt collections context.

Summarize the MAIN INTENT of the email in 2-3 lines.
Focus on:
- What specific action or response does the sender want from ABC Collections?
- Are they requesting documents, claiming payment completion, or discussing payment arrangements?
- Is this a human business communication requiring attention, or automated/system content?

IMPORTANT: Only describe what is actually written in the email content. Do not infer or assume requests that are not explicitly stated.

Be concise and factual. No categories, no explanations—just the sender's core intent in plain language.

EMAIL:
"{email_body}"

SUMMARY:
"""

EMAIL_CLASSIFICATION_PROMPT = """
You are an expert email classifier working in a debt collections agency.

1. Carefully read the email content and provided inference.
2. Determine the correct classification based on intent, content, and business context.
3. Choose ONE of the 2 main business categories below, or MANUAL_REVIEW if neither fits clearly.
4. If you are uncertain about any classification, choose MANUAL_REVIEW.

CRITICAL BUSINESS RULE: "Paid means paid" - if someone claims payment was made (even with uncertainty), classify as CLAIMS_PAID.

Email Categories:
1. INVOICE_REQUEST (Requests for documents/invoices)
2. CLAIMS_PAID (Claims past payment completion)
3. MANUAL_REVIEW (Everything else: Disputes, Promises to pay, Complex issues)

Return ONLY valid JSON with category and reasoning keys. No extra text.
{{"category": "CATEGORY_NAME", "reasoning": "Brief explanation"}}

Input:
EMAIL:
"{email_body}"

INFERENCE:
"{email_inference}"
"""

MANUAL_VS_AUTONO_PROMPT = """
You are an expert email intent classifier.
Your task is to determine whether a given email that was initially marked as 'manual_review' is actually a personal AUTO_REPLY, a system-generated NO_REPLY, or a genuine MANUAL_REVIEW.

Categories:
1. AUTO_REPLY (Out of office, vacation, personal absence)
2. NO_REPLY (System notifications, ticket creations, newsletters)
3. MANUAL_REVIEW (Human emails requiring attention, disputes, questions)

Return ONLY valid JSON with category and reasoning keys. No extra text.
{{"category": "manual_review" | "auto_reply" | "no_reply", "reasoning": "brief explanation"}}

EMAIL CONTENT:
"{email_body}"
"""

# --- DOCUMENT PROMPT CONSTANTS (New) ---

DOCUMENT_PROMPTS = {
    "en": {
        "instructions": """You are an expert invoice data extractor. Extract key information from this English invoice text and return ONLY a valid JSON object.

CRITICAL: Identify the ISSUING company (sender) vs BILL-TO company (customer):
- ISSUING COMPANY: The business that SENT the invoice (appears at top, has logo, contact details)
- BILL-TO COMPANY: The customer receiving the invoice (appears after "Bill To:", "Ship To:", "Customer:")

Required JSON format:""",
        "json_instructions": "\nReturn ONLY the JSON object.\n\nInvoice text:\n",
        "logo_instruction": '\nLogo text extracted: "{logo_text}"\nUse this logo text to help identify the ISSUING company (sender).',
    },
    "fr": {
        "instructions": """Vous êtes un expert en extraction de données de factures. Extrayez les informations clés de ce texte de facture française et retournez UNIQUEMENT un objet JSON valide.

CRITIQUE: Identifiez l'entreprise ÉMETTRICE vs l'entreprise FACTURÉE:
- ENTREPRISE ÉMETTRICE: L'entreprise qui a ENVOYÉ la facture (apparaît en haut, a le logo, coordonnées)
- ENTREPRISE FACTURÉE: Le client qui reçoit la facture (apparaît après "Facturé à:", "Client:", "Destinataire:")

Format JSON requis:""",
        "json_instructions": "\nRetournez UNIQUEMENT l'objet JSON.\n\nTexte de la facture:\n",
        "logo_instruction": '\nTexte du logo extrait: "{logo_text}"\nUtilisez ce texte du logo pour identifier l\'entreprise ÉMETTRICE.',
    },
    "it": {
        "instructions": """Sei un esperto nell'estrazione di dati dalle fatture. Estrai le informazioni chiave da questo testo di fattura italiana e restituisci SOLO un oggetto JSON valido.

CRITICO: Identifica l'azienda EMITTENTE vs l'azienda FATTURATA:
- AZIENDA EMITTENTE: L'azienda che ha INVIATO la fattura (appare in alto, ha il logo, dettagli di contatto)
- AZIENDA FATTURATA: Il cliente che riceve la fattura (appare dopo "Fatturare a:", "Cliente:", "Destinatario:")

Formato JSON richiesto:""",
        "json_instructions": "\nRestituisci SOLO l'oggetto JSON.\n\nTesto della fattura:\n",
        "logo_instruction": '\nTesto del logo estratto: "{logo_text}"\nUsa questo testo del logo per identificare l\'azienda EMITTENTE.',
    },
    "es": {
        "instructions": """Eres un experto en extracción de datos de facturas. Extrae la información clave de este texto de factura española y devuelve SOLO un objeto JSON válido.

CRÍTICO: Identifica la empresa EMISORA vs la empresa FACTURADA:
- EMPRESA EMISORA: La empresa que ENVIÓ la factura (aparece arriba, tiene logo, datos de contacto)
- EMPRESA FACTURADA: El cliente que recibe la factura (aparece después de "Facturar a:", "Cliente:", "Destinatario:")

Formato JSON requerido:""",
        "json_instructions": "\nDevuelve SOLO el objeto JSON.\n\nTexto de la factura:\n",
        "logo_instruction": '\nTexto del logo extraído: "{logo_text}"\nUsa este texto del logo para identificar la empresa EMISORA.',
    },
}

DOCUMENT_JSON_SCHEMA = """
{
    "invoice_number": "exact invoice number found",
    "issuing_company": "company that SENT/ISSUED the invoice (NOT bill-to)", 
    "bill_to_company": "customer company receiving the invoice",
    "invoice_date": "YYYY-MM-DD format",
    "total_amount": "final total number only (float or int)",
    "currency": "currency symbol or code",
    "customer_po": "purchase order number if found (string or null)",
    "confidence_score": "high/medium/low",
    "language": "en"
}
"""