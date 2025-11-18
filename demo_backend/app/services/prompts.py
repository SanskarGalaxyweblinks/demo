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