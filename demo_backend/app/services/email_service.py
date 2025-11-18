# app/services/email_service.py
import json
import time
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from .prompts import EMAIL_INFERENCE_PROMPT, EMAIL_CLASSIFICATION_PROMPT, MANUAL_VS_AUTONO_PROMPT

# Initialize LLM
# Llama3-70b is recommended for this level of reasoning
llm = ChatGroq(
    temperature=0,
    model_name="openai/gpt-oss-20b",
    api_key=os.environ.get("GROQ_API_KEY") # Or access via settings.groq_api_key
)

async def classify_email_chain(subject: str, body: str) -> dict:
    start_time = time.time()
    
    # Combine Subject and Body for context
    full_email_content = f"Subject: {subject}\n\nBody:\n{body}"

    # --- STEP 1: INFERENCE (Summarization) ---
    inference_chain = (
        ChatPromptTemplate.from_template(EMAIL_INFERENCE_PROMPT) 
        | llm 
        | StrOutputParser()
    )
    
    summary = await inference_chain.ainvoke({"email_body": full_email_content})

    # --- STEP 2: BUSINESS CLASSIFICATION ---
    classification_chain = (
        ChatPromptTemplate.from_template(EMAIL_CLASSIFICATION_PROMPT)
        | llm
        | JsonOutputParser() # Ensures we get a dict back
    )

    initial_result = await classification_chain.ainvoke({
        "email_body": full_email_content,
        "email_inference": summary
    })

    final_category = initial_result.get("category")
    final_reasoning = initial_result.get("reasoning")

    # --- STEP 3: REFINEMENT (If Manual Review) ---
    # Only run this if the first pass returned MANUAL_REVIEW
    if final_category == "MANUAL_REVIEW":
        refinement_chain = (
            ChatPromptTemplate.from_template(MANUAL_VS_AUTONO_PROMPT)
            | llm
            | JsonOutputParser()
        )
        
        refined_result = await refinement_chain.ainvoke({
            "email_body": full_email_content
        })
        
        # Update category and reasoning based on the deeper analysis
        final_category = refined_result.get("category").upper() # Ensure uppercase
        final_reasoning = f"{final_reasoning} -> Refined: {refined_result.get('reasoning')}"

    execution_time = time.time() - start_time

    return {
        "category": final_category,
        "reasoning": final_reasoning,
        "summary": summary.strip(),
        "processing_time": round(execution_time, 2)
    }