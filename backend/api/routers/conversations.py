from fastapi import APIRouter, Request
from database.queries import get_conversation_messages
from core.exceptions import FTEException

router = APIRouter(prefix="/conversations", tags=["conversations"])

@router.get("/{conversation_id}")
async def get_conversation(conversation_id: str, request: Request):
    pool = request.app.state.pool
    messages = await get_conversation_messages(pool, conversation_id)
    if not messages:
        raise FTEException("Conversation not found", status_code=404)
    return {
        "conversation_id": conversation_id,
        "messages": [
            {
                "role": m["role"],
                "content": m["content"],
                "channel": m["channel"],
                "direction": m["direction"],
                "created_at": str(m["created_at"])
            }
            for m in messages
        ]
    }
