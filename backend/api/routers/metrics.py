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

@router.get("/latency")
async def latency_metrics(request: Request):
    """Get average response latency per channel."""
    pool = request.app.state.pool
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT channel,
               AVG(latency_ms) as avg_latency,
               MIN(latency_ms) as min_latency,
               MAX(latency_ms) as max_latency,
               COUNT(*) as total_messages
               FROM messages
               WHERE direction = 'outbound'
               AND latency_ms IS NOT NULL
               GROUP BY channel"""
        )
    if not rows:
        return {"message": "No latency data yet"}
    return {
        row["channel"]: {
            "avg_ms": round(float(row["avg_latency"]), 2) if row["avg_latency"] else None,
            "min_ms": row["min_latency"],
            "max_ms": row["max_latency"],
            "total_messages": row["total_messages"]
        }
        for row in rows
    }

@router.get("/daily-report")
async def daily_report(request: Request):
    """Generate on-demand daily sentiment report."""
    from workers.daily_report import generate_daily_report
    report = await generate_daily_report()
    return report
