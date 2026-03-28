from fastapi import APIRouter, Request
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from database.connection import get_pool
from database.queries import create_customer, create_ticket, create_conversation, save_message, get_ticket_by_id, get_conversation_messages
import structlog

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

@router.post("/submit", response_model=SupportFormResponse)
async def submit_form(payload: SupportFormInput, request: Request):
    pool = request.app.state.pool

    # Get or create customer
    customer = await create_customer(pool, payload.email, payload.name)
    customer_id = str(customer["id"])

    # Create conversation
    conversation = await create_conversation(pool, customer_id, "web_form")
    conversation_id = str(conversation["id"])

    # Create ticket
    ticket = await create_ticket(
        pool, customer_id, "web_form",
        payload.category, payload.priority
    )
    ticket_id = str(ticket["id"])

    # Save message
    await save_message(
        pool, conversation_id,
        "web_form", "inbound", "customer",
        f"Subject: {payload.subject}\n\n{payload.message}"
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
