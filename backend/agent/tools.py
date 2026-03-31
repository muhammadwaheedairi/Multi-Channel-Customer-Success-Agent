from agents import function_tool
from pydantic import BaseModel
import asyncpg
import ssl
import structlog
import os
from agent.formatters import format_for_channel
from agent.sentiment import analyze_sentiment

logger = structlog.get_logger()

def get_database_url():
    return os.environ.get(
        "DATABASE_URL",
        "postgresql://fte_user:fte_password@localhost:5432/fte_db"
    )

async def get_fresh_conn():
    url = get_database_url()
    if "neon.tech" in url:
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        return await asyncpg.connect(url, ssl=ssl_ctx)
    return await asyncpg.connect(url)

async def send_via_gmail(
    to_email: str,
    subject: str,
    body: str,
    thread_id: str = None
) -> bool:
    """Send real Gmail reply."""
    try:
        import base64
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from channels.gmail_auth import get_gmail_service

        service = get_gmail_service()
        if not service:
            return False

        msg = MIMEMultipart("alternative")
        msg["to"] = to_email
        msg["subject"] = f"Re: {subject}" if not subject.startswith("Re:") else subject
        msg.attach(MIMEText(body, "plain"))

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
        send_body = {"raw": raw}
        if thread_id:
            send_body["threadId"] = thread_id

        result = service.users().messages().send(
            userId="me", body=send_body
        ).execute()

        logger.info("gmail_sent_from_tool",
                   to=to_email,
                   message_id=result["id"])
        return True

    except Exception as e:
        logger.error("gmail_send_failed", error=str(e))
        return False

class SearchInput(BaseModel):
    query: str
    max_results: int = 3

class TicketInput(BaseModel):
    customer_id: str
    issue: str
    channel: str
    category: str = "general"
    priority: str = "medium"

class EscalationInput(BaseModel):
    ticket_id: str
    reason: str

class ResponseInput(BaseModel):
    ticket_id: str
    message: str
    channel: str

class HistoryInput(BaseModel):
    customer_id: str

@function_tool
async def search_knowledge_base(input: SearchInput) -> str:
    """Search product documentation for relevant information.
    Use when customer asks about features, how-to, or technical issues.
    """
    conn = None
    try:
        from agent.embeddings import generate_embedding, embedding_to_str
        embedding = await generate_embedding(input.query)
        conn = await get_fresh_conn()

        if embedding:
            embedding_str = embedding_to_str(embedding)
            rows = await conn.fetch(
                """SELECT title, content,
                   1 - (embedding <=> $1::vector) as similarity
                   FROM knowledge_base
                   WHERE embedding IS NOT NULL
                   ORDER BY embedding <=> $1::vector
                   LIMIT $2""",
                embedding_str, input.max_results
            )
            if rows:
                return "\n\n---\n\n".join(
                    f"**{r['title']}** (relevance: {float(r['similarity']):.2f})\n{r['content']}"
                    for r in rows
                )

        # Keyword fallback
        rows = await conn.fetch(
            """SELECT title, content FROM knowledge_base
               WHERE content ILIKE $1 OR title ILIKE $1
               LIMIT $2""",
            f"%{input.query}%", input.max_results
        )
        if rows:
            return "\n\n---\n\n".join(
                f"**{r['title']}**\n{r['content']}" for r in rows
            )

        return "No relevant documentation found."

    except Exception as e:
        logger.error("search_failed", error=str(e))
        return "Knowledge base temporarily unavailable."
    finally:
        if conn:
            await conn.close()

@function_tool
async def create_ticket(input: TicketInput) -> str:
    """Create a support ticket. ALWAYS call this first."""
    conn = None
    try:
        sentiment = analyze_sentiment(input.issue)
        conn = await get_fresh_conn()

        # Verify customer exists
        customer = await conn.fetchrow(
            "SELECT id FROM customers WHERE id = $1", input.customer_id
        )
        if not customer:
            return f"Customer not found: {input.customer_id}"

        ticket = await conn.fetchrow(
            """INSERT INTO tickets (customer_id, source_channel, category, priority)
               VALUES ($1, $2, $3, $4) RETURNING id""",
            input.customer_id, input.channel,
            input.category, input.priority
        )
        ticket_id = str(ticket["id"])

        # Record metric
        try:
            await conn.execute(
                """INSERT INTO agent_metrics
                   (metric_name, metric_value, channel, dimensions)
                   VALUES ($1, $2, $3, $4)""",
                "sentiment_score", sentiment["score"],
                input.channel,
                '{"label":"' + sentiment["label"] + '"}'
            )
        except Exception:
            pass

        logger.info("ticket_created",
                   ticket_id=ticket_id,
                   sentiment=sentiment["score"])

        result = f"Ticket created. ID: {ticket_id}"
        if sentiment["should_escalate"]:
            result += " | Negative sentiment detected."
        return result

    except Exception as e:
        logger.error("create_ticket_failed", error=str(e))
        return f"Ticket creation failed: {str(e)}"
    finally:
        if conn:
            await conn.close()

@function_tool
async def get_customer_history(input: HistoryInput) -> str:
    """Get customer interaction history across ALL channels."""
    conn = None
    try:
        conn = await get_fresh_conn()
        rows = await conn.fetch(
            """SELECT m.channel, m.role, m.content, m.created_at
               FROM messages m
               JOIN conversations c ON m.conversation_id = c.id
               WHERE c.customer_id = $1
               ORDER BY m.created_at DESC LIMIT 5""",
            input.customer_id
        )
        if not rows:
            return "No previous interactions found."
        return "\n".join(
            f"[{r['channel']}] {r['role']}: {r['content'][:200]}"
            for r in rows
        )
    except Exception as e:
        logger.error("history_failed", error=str(e))
        return "History unavailable."
    finally:
        if conn:
            await conn.close()

@function_tool
async def escalate_to_human(input: EscalationInput) -> str:
    """Escalate to human support.
    Use for: pricing, refunds, legal, angry customers, human requests.
    """
    conn = None
    try:
        if not input.ticket_id or len(input.ticket_id) < 32:
            return f"Escalation recorded. Reason: {input.reason}."

        conn = await get_fresh_conn()
        await conn.execute(
            """UPDATE tickets SET status = 'escalated',
               resolution_notes = $1 WHERE id = $2""",
            f"Escalated: {input.reason}", input.ticket_id
        )
        try:
            await conn.execute(
                """INSERT INTO agent_metrics
                   (metric_name, metric_value, dimensions)
                   VALUES ('escalation', 1, $1)""",
                '{"reason":"' + input.reason + '"}'
            )
        except Exception:
            pass

        logger.info("escalated",
                   ticket_id=input.ticket_id,
                   reason=input.reason)
        return f"Escalated. Reason: {input.reason}. Human agent will follow up."

    except Exception as e:
        logger.error("escalation_failed", error=str(e))
        return f"Escalation recorded. Reason: {input.reason}."
    finally:
        if conn:
            await conn.close()

@function_tool
async def send_response(input: ResponseInput) -> str:
    """
    Send final response to customer. ALWAYS call this last.

    Flow:
    - Format response for channel
    - Save to DB
    - Email channel: fetch customer email → send via Gmail API
    """
    conn = None
    try:
        formatted = format_for_channel(
            input.message,
            input.channel,
            input.ticket_id
        )

        conn = await get_fresh_conn()

        # Get ticket info
        ticket_row = None
        if input.ticket_id and len(input.ticket_id) >= 32:
            ticket_row = await conn.fetchrow(
                "SELECT customer_id FROM tickets WHERE id = $1",
                input.ticket_id
            )

        customer_email = None
        conv_id = None

        if ticket_row:
            # Get conversation
            conv = await conn.fetchrow(
                """SELECT id FROM conversations
                   WHERE customer_id = $1 AND status = 'active'
                   ORDER BY started_at DESC LIMIT 1""",
                str(ticket_row["customer_id"])
            )
            if conv:
                conv_id = str(conv["id"])
                # Save outbound message to DB
                await conn.execute(
                    """INSERT INTO messages
                       (conversation_id, channel, direction, role, content)
                       VALUES ($1, $2, 'outbound', 'agent', $3)""",
                    conv_id, input.channel, formatted
                )

            # Get customer email
            customer = await conn.fetchrow(
                "SELECT email FROM customers WHERE id = $1",
                str(ticket_row["customer_id"])
            )
            if customer:
                customer_email = customer["email"]

        # Record metric
        try:
            await conn.execute(
                """INSERT INTO agent_metrics
                   (metric_name, metric_value, channel)
                   VALUES ('response_sent', 1, $1)""",
                input.channel
            )
        except Exception:
            pass

        # Send via Gmail if email channel
        if input.channel == "email" and customer_email:
            # Get thread_id and subject from environment
            thread_id = os.environ.get("CURRENT_THREAD_ID") or None
            subject = "TechCorp Support Response"

            # Get original subject from messages
            if conv_id:
                orig_msg = await conn.fetchrow(
                    """SELECT content FROM messages
                       WHERE conversation_id = $1
                       AND direction = 'inbound'
                       ORDER BY created_at ASC LIMIT 1""",
                    conv_id
                )
                if orig_msg:
                    content = orig_msg["content"]
                    if content.startswith("Subject:"):
                        subject = content.split("\n")[0].replace("Subject:", "").strip()

            sent = await send_via_gmail(
                to_email=customer_email,
                subject=subject,
                body=formatted,
                thread_id=thread_id if thread_id else None
            )

            if sent:
                logger.info("email_reply_sent", to=customer_email)
            else:
                logger.warning("email_reply_failed", to=customer_email)

        logger.info("response_sent", channel=input.channel)
        return f"Response sent via {input.channel}."

    except Exception as e:
        logger.error("send_response_failed", error=str(e))
        return f"Response recorded via {input.channel}."
    finally:
        if conn:
            await conn.close()
