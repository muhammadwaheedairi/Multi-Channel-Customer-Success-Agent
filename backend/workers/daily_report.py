"""
Daily Sentiment Report Generator.
PDF requirement: "Generate daily reports on customer sentiment"
"""
import asyncio
import structlog
from datetime import datetime, timedelta
from database.connection import create_pool

logger = structlog.get_logger()
DATABASE_URL = "postgresql://fte_user:fte_password@localhost:5432/fte_db"

async def generate_daily_report() -> dict:
    """Generate daily sentiment and performance report."""
    pool = await create_pool(DATABASE_URL)
    try:
        yesterday = datetime.utcnow() - timedelta(days=1)

        async with pool.acquire() as conn:
            # Total tickets per channel
            channel_stats = await conn.fetch(
                """SELECT source_channel, COUNT(*) as total,
                   COUNT(*) FILTER (WHERE status = 'escalated') as escalated,
                   COUNT(*) FILTER (WHERE status = 'resolved') as resolved
                   FROM tickets
                   WHERE created_at > $1
                   GROUP BY source_channel""",
                yesterday
            )

            # Avg sentiment
            avg_sentiment = await conn.fetchval(
                """SELECT AVG(metric_value) FROM agent_metrics
                   WHERE metric_name = 'sentiment_score'
                   AND recorded_at > $1""",
                yesterday
            )

            # Total escalations
            total_escalations = await conn.fetchval(
                """SELECT COUNT(*) FROM agent_metrics
                   WHERE metric_name = 'escalation'
                   AND recorded_at > $1""",
                yesterday
            )

            # Avg latency
            avg_latency = await conn.fetchval(
                """SELECT AVG(latency_ms) FROM messages
                   WHERE direction = 'outbound'
                   AND created_at > $1""",
                yesterday
            )

        report = {
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "period": "last_24_hours",
            "sentiment": {
                "average_score": round(float(avg_sentiment), 2) if avg_sentiment else None,
                "label": "positive" if (avg_sentiment or 0) > 0.6
                         else "neutral" if (avg_sentiment or 0) > 0.4
                         else "negative"
            },
            "channels": {
                row["source_channel"]: {
                    "total": row["total"],
                    "escalated": row["escalated"],
                    "resolved": row["resolved"],
                    "escalation_rate": round(
                        row["escalated"] / max(row["total"], 1) * 100, 1
                    )
                }
                for row in channel_stats
            },
            "total_escalations": total_escalations,
            "avg_latency_ms": round(float(avg_latency), 0) if avg_latency else None,
            "status": "healthy" if (avg_sentiment or 0.5) > 0.4 else "needs_attention"
        }

        logger.info("daily_report_generated", date=report["date"])
        return report

    finally:
        await pool.close()

async def run_daily_scheduler():
    """Run report every 24 hours."""
    logger.info("daily_report_scheduler_started")
    while True:
        try:
            report = await generate_daily_report()
            logger.info("daily_report", **{
                k: v for k, v in report.items()
                if k != "channels"
            })
        except Exception as e:
            logger.error("daily_report_failed", error=str(e))
        # Wait 24 hours
        await asyncio.sleep(86400)

if __name__ == "__main__":
    asyncio.run(run_daily_scheduler())
