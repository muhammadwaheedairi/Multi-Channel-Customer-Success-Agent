import asyncio
import structlog
from kafka.client import FTEConsumer, FTEProducer
from kafka.topics import TOPICS
from database.connection import create_pool
from database.queries import create_customer, create_conversation, save_message
from agent.customer_success_agent import run_agent

logger = structlog.get_logger()
DATABASE_URL = "postgresql://fte_user:fte_password@localhost:5432/fte_db"

async def handle_message(topic: str, data: dict):
    """Process incoming ticket from any channel."""
    logger.info("processing_message", topic=topic, channel=data.get("channel"))
    pool = await create_pool(DATABASE_URL)
    try:
        channel = data.get("channel", "web_form")
        email = data.get("customer_email", "")
        name = data.get("customer_name", "Unknown")
        message = data.get("content", "")
        subject = data.get("subject", "Support Request")

        customer = await create_customer(pool, email, name)
        customer_id = str(customer["id"])

        conv = await create_conversation(pool, customer_id, channel)
        await save_message(
            pool, str(conv["id"]),
            channel, "inbound", "customer", message
        )

        result = await run_agent(
            message=message,
            customer_id=customer_id,
            channel=channel,
            ticket_subject=subject
        )
        logger.info("message_processed", success=result["success"])
    except Exception as e:
        logger.error("processing_failed", error=str(e))
    finally:
        await pool.close()

async def main():
    logger.info("worker_starting")
    consumer = FTEConsumer(
        topics=[TOPICS["tickets_incoming"]],
        group_id="fte-processor"
    )
    await consumer.start()
    logger.info("worker_ready", topic=TOPICS["tickets_incoming"])
    await consumer.consume(handle_message)

if __name__ == "__main__":
    asyncio.run(main())
