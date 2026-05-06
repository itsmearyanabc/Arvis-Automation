from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json

app = FastAPI(title="Data Filtration Layer", description="Intercept raw JSON webhooks, clean data, and extract entities.")

class CleanedData(BaseModel):
    source: str
    event_type: str
    user_id: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    message_content: Optional[str]
    raw_payload: Dict[str, Any]

@app.post("/webhook/intercept")
async def intercept_webhook(request: Request):
    """
    Endpoint to receive raw webhooks, clean them, and route them to n8n.
    """
    try:
        payload = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")

    # Basic entity extraction and data cleaning logic
    extracted_data = CleanedData(
        source=payload.get("source", "unknown"),
        event_type=payload.get("event", "generic_event"),
        user_id=payload.get("user", {}).get("id") or payload.get("user_id"),
        contact_email=payload.get("email") or payload.get("contact", {}).get("email"),
        contact_phone=payload.get("phone") or payload.get("contact", {}).get("phone"),
        message_content=payload.get("message", {}).get("text") or payload.get("text"),
        raw_payload=payload
    )

    # TODO: In production, forward `extracted_data.dict()` to n8n Webhook URL.
    # n8n_webhook_url = "http://n8n:5678/webhook/your-webhook-id"
    # requests.post(n8n_webhook_url, json=extracted_data.dict())

    return {
        "status": "success",
        "message": "Data filtered and processed successfully.",
        "data": extracted_data.model_dump()
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
