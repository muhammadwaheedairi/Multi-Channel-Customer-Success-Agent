import asyncpg
from typing import Optional
import structlog

logger = structlog.get_logger()

# ─── CUSTOMERS ───────────────────────────────────────────

async def get_customer_by_email(pool: asyncpg.Pool, email: str):
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM customers WHERE email = $1", email
        )

async def create_customer(pool: asyncpg.Pool, email: str, name: str = "", phone: str = ""):
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            """INSERT INTO customers (email, name, phone)
               VALUES ($1, $2, $3)
               ON CONFLICT (email) DO UPDATE SET name = $2
               RETURNING *""",
            email, name, phone
        )

# ─── TICKETS ─────────────────────────────────────────────

async def create_ticket(
    pool: asyncpg.Pool,
    customer_id: str,
    source_channel: str,
    category: str = "general",
    priority: str = "medium"
):
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            """INSERT INTO tickets (customer_id, source_channel, category, priority)
               VALUES ($1, $2, $3, $4)
               RETURNING *""",
            customer_id, source_channel, category, priority
        )

async def get_ticket_by_id(pool: asyncpg.Pool, ticket_id: str):
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM tickets WHERE id = $1", ticket_id
        )

async def update_ticket_status(pool: asyncpg.Pool, ticket_id: str, status: str):
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            """UPDATE tickets SET status = $1
               WHERE id = $2 RETURNING *""",
            status, ticket_id
        )

# ─── CONVERSATIONS ────────────────────────────────────────

async def create_conversation(
    pool: asyncpg.Pool,
    customer_id: str,
    channel: str
):
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            """INSERT INTO conversations (customer_id, initial_channel)
               VALUES ($1, $2) RETURNING *""",
            customer_id, channel
        )

async def get_active_conversation(pool: asyncpg.Pool, customer_id: str):
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            """SELECT * FROM conversations
               WHERE customer_id = $1
               AND status = 'active'
               AND started_at > NOW() - INTERVAL '24 hours'
               ORDER BY started_at DESC LIMIT 1""",
            customer_id
        )

# ─── MESSAGES ────────────────────────────────────────────

async def save_message(
    pool: asyncpg.Pool,
    conversation_id: str,
    channel: str,
    direction: str,
    role: str,
    content: str,
    latency_ms: int = 0
):
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            """INSERT INTO messages
               (conversation_id, channel, direction, role, content, latency_ms)
               VALUES ($1, $2, $3, $4, $5, $6)
               RETURNING *""",
            conversation_id, channel, direction, role, content, latency_ms
        )

async def get_conversation_messages(pool: asyncpg.Pool, conversation_id: str):
    async with pool.acquire() as conn:
        return await conn.fetch(
            """SELECT * FROM messages
               WHERE conversation_id = $1
               ORDER BY created_at ASC""",
            conversation_id
        )

# ─── METRICS ─────────────────────────────────────────────

async def get_channel_metrics(pool: asyncpg.Pool):
    async with pool.acquire() as conn:
        return await conn.fetch(
            """SELECT
               initial_channel as channel,
               COUNT(*) as total_conversations,
               COUNT(*) FILTER (WHERE status = 'escalated') as escalations,
               AVG(sentiment_score) as avg_sentiment
               FROM conversations
               WHERE started_at > NOW() - INTERVAL '24 hours'
               GROUP BY initial_channel"""
        )

# ─── LATENCY TRACKING ────────────────────────────────

async def update_message_latency(
    pool: asyncpg.Pool,
    message_id: str,
    latency_ms: int
):
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE messages SET latency_ms = $1 WHERE id = $2",
            latency_ms, message_id
        )

async def get_avg_latency(pool: asyncpg.Pool, channel: str = None):
    async with pool.acquire() as conn:
        if channel:
            return await conn.fetchval(
                """SELECT AVG(latency_ms) FROM messages
                   WHERE direction = 'outbound'
                   AND channel = $1
                   AND latency_ms IS NOT NULL""",
                channel
            )
        return await conn.fetchval(
            """SELECT AVG(latency_ms) FROM messages
               WHERE direction = 'outbound'
               AND latency_ms IS NOT NULL"""
        )

async def record_agent_metric(
    pool: asyncpg.Pool,
    metric_name: str,
    metric_value: float,
    channel: str = None,
    dimensions: dict = None
):
    async with pool.acquire() as conn:
        await conn.execute(
            """INSERT INTO agent_metrics
               (metric_name, metric_value, channel, dimensions)
               VALUES ($1, $2, $3, $4)""",
            metric_name,
            metric_value,
            channel,
            json.dumps(dimensions or {})
        )
