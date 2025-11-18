from __future__ import annotations

import io
import random
from typing import Any

from fastapi import HTTPException, UploadFile, status

SUPPORTED_TYPES = {
    "application/pdf": "PDF",
    "application/msword": "DOC",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "DOCX",
    "image/jpeg": "Image",
    "image/png": "Image",
}


async def analyze_document(file: UploadFile, user: dict[str, Any] | None):
    if not file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File missing")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    file_type = SUPPORTED_TYPES.get(file.content_type, "Unknown")
    preview = preview_text(contents)

    entities = []
    if "invoice" in preview.lower():
        entities.append("Invoice Number")
    if "$" in preview or "usd" in preview.lower():
        entities.append("Amount")
    if "due" in preview.lower():
        entities.append("Due Date")
    if user:
        entities.append("User:" + user["email"])

    confidence = round(random.uniform(0.8, 0.97), 2)

    return {
        "document_type": file_type,
        "page_count": max(1, len(contents) // 2000),
        "entities": entities or ["General Metadata"],
        "detected_currency": "USD" if "$" in preview else None,
        "confidence": confidence,
        "preview": preview[:400],
    }


def preview_text(contents: bytes) -> str:
    try:
        text = contents.decode("utf-8")
    except UnicodeDecodeError:
        text = contents[:400].decode("latin-1", errors="ignore")

    output = io.StringIO()
    for line in text.splitlines():
        if not line.strip():
            continue
        output.write(line.strip())
        output.write("\n")
        if output.tell() > 600:
            break
    return output.getvalue().strip()


