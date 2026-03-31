from fastapi import APIRouter, Request, BackgroundTasks
from pydantic import BaseModel, EmailStr, field_validator
from database.connection import get_pool
from database.queries import (
    create_customer, create_ticket, create_conversation,
    save_message, get_ticket_by_id, get_conversation_messages
)
from agent.customer_success_agent import run_agent
from core.config import settings
import structlog
import os

logger = structlog.get_logger()
router = APIRouter(prefix="/support", tags=["support"])

class SupportFormInput(BaseModel):
    name: str
    email: EmailStr
    subject: str
    category: str = "general"
    priority: str = "medium"
    message: str

    @field_validator("name")
    @classmethod
    def name_valid(cls, v):
        if len(v.strip()) < 2:
            raise ValueError("Name must be at least 2 characters")
        return v.strip()

    @field_validator("message")
    @classmethod
    def message_valid(cls, v):
        if len(v.strip()) < 10:
            raise ValueError("Message must be at least 10 characters")
        return v.strip()

    @field_validator("category")
    @classmethod
    def category_valid(cls, v):
        allowed = ["general", "technical", "billing", "feedback", "bug_report"]
        if v not in allowed:
            raise ValueError(f"Category must be one of: {allowed}")
        return v

class SupportFormResponse(BaseModel):
    ticket_id: str
    message: str
    estimated_response_time: str

async def send_real_email(
    to_email: str,
    subject: str,
    body: str
) -> bool:
    """Send real email via Gmail API."""
    try:
        import base64
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from channels.gmail_auth import get_gmail_service

        service = get_gmail_service()
        if not service:
            logger.warning("gmail_not_configured")
            return False

        # Create email
        msg = MIMEMultipart("alternative")
        msg["to"] = to_email
        msg["subject"] = subject

        # Plain text version
        text_part = MIMEText(body, "plain")
        msg.attach(text_part)

        # Encode and send
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
        result = service.users().messages().send(
            userId="me",
            body={"raw": raw}
        ).execute()

        logger.info("email_sent_successfully",
                   to=to_email,
                   message_id=result["id"])
        return True

    except Exception as e:
        logger.error("email_send_failed", error=str(e), to=to_email)
        return False

async def process_with_agent(
    customer_id: str,
    ticket_id: str,
    subject: str,
    message: str,
    channel: str,
    email: str,
    name: str
):
    """Background task — agent processes the message."""
    os.environ["OPENAI_API_KEY"] = settings.openai_api_key

    try:
        logger.info("agent_processing_start",
                   ticket_id=ticket_id,
                   channel=channel)

        result = await run_agent(
            message=message,
            customer_id=customer_id,
            channel=channel,
            ticket_subject=subject
        )

        logger.info("agent_processing_done",
                   ticket_id=ticket_id,
                   success=result["success"])

        if result["success"]:
            # Send confirmation email to customer
            confirmation_body = f"""Dear {name},

Thank you for contacting TechCorp Support!

Your support request has been received and our AI agent has responded.

Track your ticket here:
http://localhost:3000/support/ticket/{ticket_id}

---
Ticket ID: {ticket_id}
Subject: {subject}

Our AI agent's response is available on your ticket page.

Best regards,
TechCorp AI Support Team"""

            sent = await send_real_email(
                to_email=email,
                subject=f"[TechCorp Support] Ticket #{ticket_id[:8]} — {subject}",
                body=confirmation_body
            )

            if sent:
                logger.info("confirmation_email_sent", to=email)
            else:
                logger.warning("confirmation_email_failed", to=email)

    except Exception as e:
        logger.error("agent_processing_failed",
                    ticket_id=ticket_id,
                    error=str(e))

@router.post("/submit", response_model=SupportFormResponse)
async def submit_form(
    payload: SupportFormInput,
    request: Request,
    background_tasks: BackgroundTasks
):
    pool = request.app.state.pool

    customer = await create_customer(pool, payload.email, payload.name)
    customer_id = str(customer["id"])

    conversation = await create_conversation(pool, customer_id, "web_form")
    conversation_id = str(conversation["id"])

    ticket = await create_ticket(
        pool, customer_id, "web_form",
        payload.category, payload.priority
    )
    ticket_id = str(ticket["id"])

    await save_message(
        pool, conversation_id,
        "web_form", "inbound", "customer",
        f"Subject: {payload.subject}\n\n{payload.message}"
    )

    background_tasks.add_task(
        process_with_agent,
        customer_id,
        ticket_id,
        payload.subject,
        payload.message,
        "web_form",
        payload.email,
        payload.name
    )

    logger.info("ticket_created", ticket_id=ticket_id, channel="web_form")

    return SupportFormResponse(
        ticket_id=ticket_id,
        message="Thank you! Our AI agent will respond shortly.",
        estimated_response_time="Within 5 minutes"
    )

@router.get("/ticket/{ticket_id}")
async def get_ticket(ticket_id: str, request: Request):
    pool = request.app.state.pool
    ticket = await get_ticket_by_id(pool, ticket_id)
    if not ticket:
        from core.exceptions import FTEException
        raise FTEException("Ticket not found", status_code=404)
    return {
        "ticket_id": ticket_id,
        "status": ticket["status"],
        "channel": ticket["source_channel"],
        "category": ticket["category"],
        "priority": ticket["priority"],
        "created_at": str(ticket["created_at"])
    }

@router.get("/ticket/{ticket_id}/messages")
async def get_ticket_messages(ticket_id: str, request: Request):
    pool = request.app.state.pool
    ticket = await get_ticket_by_id(pool, ticket_id)
    if not ticket:
        from core.exceptions import FTEException
        raise FTEException("Ticket not found", status_code=404)
    async with pool.acquire() as conn:
        conv = await conn.fetchrow(
            """SELECT id FROM conversations
               WHERE customer_id = $1
               ORDER BY started_at DESC LIMIT 1""",
            str(ticket["customer_id"])
        )
    if not conv:
        return {"ticket_id": ticket_id, "messages": []}
    messages = await get_conversation_messages(pool, str(conv["id"]))
    return {
        "ticket_id": ticket_id,
        "messages": [
            {
                "role": m["role"],
                "content": m["content"],
                "channel": m["channel"],
                "created_at": str(m["created_at"])
            }
            for m in messages
        ]
    }
