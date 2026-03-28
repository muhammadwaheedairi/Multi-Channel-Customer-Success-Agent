from fastapi import APIRouter, Request
from database.queries import get_ticket_by_id, update_ticket_status, get_conversation_messages, get_active_conversation
from core.exceptions import FTEException

router = APIRouter(prefix="/tickets", tags=["tickets"])

@router.get("/{ticket_id}")
async def get_ticket(ticket_id: str, request: Request):
    pool = request.app.state.pool
    ticket = await get_ticket_by_id(pool, ticket_id)
    if not ticket:
        raise FTEException("Ticket not found", status_code=404)
    return {
        "ticket_id": str(ticket["id"]),
        "status": ticket["status"],
        "channel": ticket["source_channel"],
        "category": ticket["category"],
        "priority": ticket["priority"],
        "created_at": str(ticket["created_at"])
    }

@router.patch("/{ticket_id}/status")
async def update_status(ticket_id: str, status: str, request: Request):
    allowed = ["open", "in_progress", "resolved", "escalated"]
    if status not in allowed:
        raise FTEException(f"Status must be one of: {allowed}")
    pool = request.app.state.pool
    ticket = await update_ticket_status(pool, ticket_id, status)
    if not ticket:
        raise FTEException("Ticket not found", status_code=404)
    return {"ticket_id": ticket_id, "status": ticket["status"]}

@router.get("/{ticket_id}/messages")
async def get_messages(ticket_id: str, request: Request):
    pool = request.app.state.pool
    ticket = await get_ticket_by_id(pool, ticket_id)
    if not ticket:
        raise FTEException("Ticket not found", status_code=404)
    conv = await get_active_conversation(pool, str(ticket["customer_id"]))
    if not conv:
        return {"messages": []}
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
