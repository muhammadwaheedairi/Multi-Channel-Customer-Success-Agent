import asyncio
import structlog
from kafka.client import FTEProducer
from kafka.topics import TOPICS
from database.connection import create_pool

logger = structlog.get_logger()
DATABASE_URL = "postgresql://fte_user:fte_password@localhost:5432/fte_db"

async def publish_metrics():
    """Collect DB metrics and publish to Kafka every 60 seconds."""
    producer = FTEProducer()
    await producer.start()
    pool = await create_pool(DATABASE_URL)

    logger.info("metrics_collector_started")

    while True:
        try:
            async with pool.acquire() as conn:
                total = await conn.fetchval("SELECT COUNT(*) FROM tickets")
                open_t = await conn.fetchval(
                    "SELECT COUNT(*) FROM tickets WHERE status = 'open'"
                )
                escalated = await conn.fetchval(
                    "SELECT COUNT(*) FROM tickets WHERE status = 'escalated'"
                )
                customers = await conn.fetchval("SELECT COUNT(*) FROM customers")
                channels = await conn.fetch(
                    """SELECT initial_channel, COUNT(*) as count
                       FROM conversations
                       WHERE started_at > NOW() - INTERVAL '1 hour'
                       GROUP BY initial_channel"""
                )

            metrics = {
                "event_type": "system_metrics",
                "total_tickets": total,
                "open_tickets": open_t,
                "escalated_tickets": escalated,
                "total_customers": customers,
                "channel_counts": {r["initial_channel"]: r["count"] for r in channels}
            }

            await producer.publish(TOPICS["metrics"], metrics)
            logger.info("metrics_published", total_tickets=total)

        except Exception as e:
            logger.error("metrics_collection_failed", error=str(e))

        await asyncio.sleep(60)

async def main():
    await publish_metrics()

if __name__ == "__main__":
    asyncio.run(main())
