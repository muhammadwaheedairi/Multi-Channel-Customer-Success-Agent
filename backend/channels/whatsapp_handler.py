from fastapi import APIRouter, Request, BackgroundTasks, Response, HTTPException
from database.connection import get_pool
from database.queries import create_customer, create_conversation, save_message
from agent.customer_success_agent import run_agent
import hmac
import hashlib
import os
import structlog

logger = structlog.get_logger()
router = APIRouter(prefix="/webhooks", tags=["webhooks"])

def validate_twilio_signature(request_url: str, params: dict, signature: str, auth_token: str) -> bool:
    """Validate Twilio webhook signature."""
    try:
        sorted_params = "".join(f"{k}{v}" for k, v in sorted(params.items()))
        s = request_url + sorted_params
        mac = hmac.new(auth_token.encode("utf-8"), s.encode("utf-8"), hashlib.sha1)
        computed = mac.digest()
        import base64
        expected = base64.b64encode(computed).decode("utf-8")
        return hmac.compare_digest(expected, signature)
    except Exception:
        return False

async def process_whatsapp_with_agent(customer_id: str, message: str, phone: str):
    try:
        result = await run_agent(
            message=message,
            customer_id=customer_id,
            channel="whatsapp",
            ticket_subject="WhatsApp Support"
        )
        logger.info("whatsapp_agent_done", customer_id=customer_id)
    except Exception as e:
        logger.error("whatsapp_agent_failed", error=str(e))

@router.post("/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """Handle incoming WhatsApp messages from Twilio."""
    try:
        form_data = await request.form()
        data = dict(form_data)

        # Twilio signature validation (production)
        auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        if auth_token:
            signature = request.headers.get("X-Twilio-Signature", "")
            url = str(request.url)
            if not validate_twilio_signature(url, data, signature, auth_token):
                logger.warning("twilio_signature_invalid")
                raise HTTPException(status_code=403, detail="Invalid Twilio signature")

        phone = data.get("From", "").replace("whatsapp:", "")
        message_body = data.get("Body", "").strip()
        profile_name = data.get("ProfileName", "WhatsApp User")

        logger.info("whatsapp_received", phone=phone[:6], message=message_body[:50])

        if not phone or not message_body:
            return Response(
                content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
                media_type="application/xml"
            )

        pool = request.app.state.pool

        async with pool.acquire() as conn:
            customer = await conn.fetchrow(
                """SELECT c.* FROM customers c
                   JOIN customer_identifiers ci ON ci.customer_id = c.id
                   WHERE ci.identifier_type = 'whatsapp'
                   AND ci.identifier_value = $1""",
                phone
            )
            if not customer:
                customer = await conn.fetchrow(
                    "INSERT INTO customers (phone, name) VALUES ($1, $2) RETURNING *",
                    phone, profile_name
                )
                await conn.execute(
                    """INSERT INTO customer_identifiers
                       (customer_id, identifier_type, identifier_value)
                       VALUES ($1, 'whatsapp', $2)""",
                    str(customer["id"]), phone
                )

        customer_id = str(customer["id"])
        conv = await create_conversation(pool, customer_id, "whatsapp")
        await save_message(
            pool, str(conv["id"]),
            "whatsapp", "inbound", "customer", message_body
        )

        background_tasks.add_task(
            process_whatsapp_with_agent,
            customer_id, message_body, phone
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("whatsapp_webhook_failed", error=str(e))

    return Response(
        content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
        media_type="application/xml"
    )

@router.post("/whatsapp/status")
async def whatsapp_status(request: Request):
    """Handle WhatsApp delivery status updates from Twilio."""
    try:
        form_data = await request.form()
        data = dict(form_data)

        message_sid = data.get("MessageSid")
        status = data.get("MessageStatus")

        logger.info("whatsapp_status_update", sid=message_sid, status=status)

        if message_sid and status:
            pool = request.app.state.pool
            async with pool.acquire() as conn:
                await conn.execute(
                    """UPDATE messages
                       SET delivery_status = $1
                       WHERE channel_message_id = $2""",
                    status, message_sid
                )

        return {"status": "received"}
    except Exception as e:
        logger.error("whatsapp_status_failed", error=str(e))
        return {"status": "error"}

@router.get("/whatsapp/test")
async def whatsapp_test(request: Request, background_tasks: BackgroundTasks):
    """Test endpoint — simulate WhatsApp message without Twilio."""
    pool = request.app.state.pool

    async with pool.acquire() as conn:
        existing = await conn.fetchrow(
            """SELECT c.* FROM customers c
               JOIN customer_identifiers ci ON ci.customer_id = c.id
               WHERE ci.identifier_type = 'whatsapp'
               AND ci.identifier_value = $1""",
            "+923001234567"
        )
        if existing:
            customer = existing
        else:
            customer = await conn.fetchrow(
                "INSERT INTO customers (phone, name) VALUES ($1, $2) RETURNING *",
                "+923001234567", "Test WhatsApp User"
            )
            await conn.execute(
                """INSERT INTO customer_identifiers
                   (customer_id, identifier_type, identifier_value)
                   VALUES ($1, 'whatsapp', $2)
                   ON CONFLICT DO NOTHING""",
                str(customer["id"]), "+923001234567"
            )

    customer_id = str(customer["id"])
    conv = await create_conversation(pool, customer_id, "whatsapp")
    await save_message(
        pool, str(conv["id"]),
        "whatsapp", "inbound", "customer",
        "how do i reset my password"
    )

    background_tasks.add_task(
        process_whatsapp_with_agent,
        customer_id,
        "how do i reset my password",
        "+923001234567"
    )

    return {
        "status": "processing",
        "customer_id": customer_id,
        "message": "WhatsApp test message sent to agent"
    }

def format_whatsapp_response(response: str, max_length: int = 1600) -> list[str]:
    """
    Split long WhatsApp responses into multiple messages.
    Twilio max is 1600 chars per message.
    """
    if len(response) <= max_length:
        return [response]

    messages = []
    while response:
        if len(response) <= max_length:
            messages.append(response)
            break
        # Find good break point
        break_point = response.rfind('. ', 0, max_length)
        if break_point == -1:
            break_point = response.rfind(' ', 0, max_length)
        if break_point == -1:
            break_point = max_length
        messages.append(response[:break_point + 1].strip())
        response = response[break_point + 1:].strip()

    return messages
