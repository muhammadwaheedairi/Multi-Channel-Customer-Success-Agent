from fastapi import APIRouter, Request
from database.queries import get_channel_metrics

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.get("/channels")
async def channel_metrics(request: Request):
    pool = request.app.state.pool
    rows = await get_channel_metrics(pool)
    return {
        row["channel"]: {
            "total_conversations": row["total_conversations"],
            "escalations": row["escalations"],
            "avg_sentiment": float(row["avg_sentiment"]) if row["avg_sentiment"] else None
        }
        for row in rows
    }

@router.get("/summary")
async def summary(request: Request):
    pool = request.app.state.pool
    async with pool.acquire() as conn:
        total_tickets = await conn.fetchval("SELECT COUNT(*) FROM tickets")
        open_tickets = await conn.fetchval("SELECT COUNT(*) FROM tickets WHERE status = 'open'")
        total_customers = await conn.fetchval("SELECT COUNT(*) FROM customers")
        resolved = await conn.fetchval("SELECT COUNT(*) FROM tickets WHERE status = 'resolved'")
    return {
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "resolved_tickets": resolved,
        "total_customers": total_customers,
    }
