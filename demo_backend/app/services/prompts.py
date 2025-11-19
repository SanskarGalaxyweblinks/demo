# ---------------------------------------------------------
# EMAIL INFERENCE PROMPT
# ---------------------------------------------------------

EMAIL_INFERENCE_PROMPT = """
You are an expert at understanding business emails in a debt collections context.

Summarize the MAIN INTENT of the email in 2-3 lines.
Focus on:
- What specific action or response does the sender want from ABC Collections?
- Are they requesting documents, claiming payment completion, or discussing payment arrangements?
- Is this a human business communication requiring attention, or automated/system content?

IMPORTANT: Only describe what is actually written in the email content. Do not infer.

Be concise and factual. No categories, no explanations.

EMAIL:
"{email_body}"

SUMMARY:
"""


# ---------------------------------------------------------
# EMAIL CLASSIFICATION PROMPT
# ---------------------------------------------------------

EMAIL_CLASSIFICATION_PROMPT = """
You are an expert email classifier working in a debt collections agency.

Follow these rules:
1. Classify only as: INVOICE_REQUEST, CLAIMS_PAID, MANUAL_REVIEW.
2. If sender claims ANY kind of past payment (even uncertain) → CLAIMS_PAID.
3. If sender requests ANY invoice/document → INVOICE_REQUEST.
4. Everything else → MANUAL_REVIEW.
5. When unsure → MANUAL_REVIEW.

Return ONLY JSON:
{"category": "CATEGORY_NAME", "reasoning": "Brief explanation"}

EMAIL:
"{email_body}"

INFERENCE:
"{email_inference}"
"""


# ---------------------------------------------------------
# MANUAL VS AUTO VS NO_REPLY PROMPT
# ---------------------------------------------------------

MANUAL_VS_AUTONO_PROMPT = """
You are an expert classifier.

Your task:
- AUTO_REPLY → Out of office, vacation, personal absence
- NO_REPLY → System messages, tickets, newsletters
- MANUAL_REVIEW → Human-written content that needs a response

Return ONLY JSON:
{"category": "auto_reply" | "no_reply" | "manual_review", "reasoning": "brief explanation"}

EMAIL CONTENT:
"{email_body}"
"""


# ---------------------------------------------------------
# DOCUMENT (INVOICE) PROMPTS
# ---------------------------------------------------------

DOCUMENT_PROMPTS = {
    "en": {
        "instructions": """You are an expert invoice data extractor. Extract key information from this invoice and return ONLY valid JSON.

CRITICAL:
- ISSUING COMPANY = company that SENT the invoice (top/header)
- BILL-TO COMPANY = customer receiving the invoice""",

        "json_instructions": "\nReturn ONLY the JSON object.\n\nInvoice Text:\n",
        "logo_instruction": '\nLogo text extracted: "{logo_text}"\nUse this to identify the issuing company.',
    },

    "fr": {
        "instructions": """Vous êtes un expert en extraction de données de factures.

CRITIQUE:
- ENTREPRISE ÉMETTRICE = celle qui ENVOIE la facture
- ENTREPRISE FACTURÉE = le client qui la reçoit""",

        "json_instructions": "\nRetournez UNIQUEMENT l'objet JSON.\n\nTexte de la facture:\n",
        "logo_instruction": '\nTexte du logo: "{logo_text}"\nAidez-vous-en pour identifier l\'entreprise émettrice.',
    },

    "it": {
        "instructions": """Sei un esperto nell'estrazione di dati da fatture.

CRITICO:
- AZIENDA EMITTENTE = chi invia la fattura
- AZIENDA FATTURATA = chi la riceve""",

        "json_instructions": "\nRestituisci SOLO l'oggetto JSON.\n\nTesto della fattura:\n",
        "logo_instruction": '\nTesto del logo: "{logo_text}"\nUsalo per identificare l\'azienda emittente.',
    },

    "es": {
        "instructions": """Eres un experto en extracción de datos de facturas.

CRÍTICO:
- EMPRESA EMISORA = quien envía la factura
- EMPRESA FACTURADA = el cliente""",

        "json_instructions": "\nDevuelve SOLO el objeto JSON.\n\nTexto de la factura:\n",
        "logo_instruction": '\nTexto del logo: "{logo_text}"\nUsa esto para identificar la empresa emisora.',
    },
}


# ---------------------------------------------------------
# JSON SCHEMA (CAMELCASE) — EXACTLY MATCHES PYDANTIC MODEL
# ---------------------------------------------------------

DOCUMENT_JSON_SCHEMA = """
{{
  "invoiceNumber": "exact invoice number found",
  "issuingCompany": "company that SENT/ISSUED the invoice",
  "billToCompany": "customer company receiving the invoice",
  "invoiceDate": "YYYY-MM-DD",
  "totalAmount": "final total number",
  "currency": "currency symbol or code",
  "customerPO": "purchase order number if found",
  "confidenceScore": "high/medium/low",
  "language": "<LANG>"
}}
"""
