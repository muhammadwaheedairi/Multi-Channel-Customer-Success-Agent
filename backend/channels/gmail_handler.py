from fastapi import APIRouter, Request, BackgroundTasks
from database.queries import create_customer, create_conversation, save_message
from agent.customer_success_agent import run_agent
from core.config import settings
import base64
import json
import re
import structlog
import os

logger = structlog.get_logger()
router = APIRouter(prefix="/webhooks", tags=["webhooks"])

# ─── CRITICAL: Store LAST history_id in file (DB mein better hoga production mein)
HISTORY_ID_FILE = "../context/last_history_id.txt"

def save_history_id(history_id: str):
    """Save history_id for next request."""
    with open(HISTORY_ID_FILE, "w") as f:
        f.write(str(history_id))
    logger.info("history_id_saved", history_id=history_id)

def load_history_id() -> str | None:
    """Load previously saved history_id."""
    try:
        if os.path.exists(HISTORY_ID_FILE):
            with open(HISTORY_ID_FILE, "r") as f:
                hid = f.read().strip()
                if hid:
                    return hid
    except Exception:
        pass
    return None

# ─── GMAIL SERVICE ───────────────────────────────────

def get_gmail_service():
    try:
        from channels.gmail_auth import get_gmail_service as _get
        return _get()
    except Exception as e:
        logger.error("gmail_service_failed", error=str(e))
        return None

# ─── EMAIL PARSING ────────────────────────────────────

def extract_email_address(from_header: str) -> str:
    match = re.search(r'<(.+?)>', from_header)
    return match.group(1).strip() if match else from_header.strip()

def extract_name(from_header: str) -> str:
    if "<" in from_header:
        return from_header.split("<")[0].strip().strip('"').strip("'")
    return from_header.strip()

def extract_body(payload: dict) -> str:
    """Extract plain text body — handles all Gmail payload structures."""
    try:
        # Direct body
        data = payload.get("body", {}).get("data", "")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

        # Parts
        for part in payload.get("parts", []):
            if part.get("mimeType") == "text/plain":
                data = part.get("body", {}).get("data", "")
                if data:
                    return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
            # Nested parts
            for subpart in part.get("parts", []):
                if subpart.get("mimeType") == "text/plain":
                    data = subpart.get("body", {}).get("data", "")
                    if data:
                        return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
    except Exception as e:
        logger.error("body_extract_failed", error=str(e))
    return ""

def get_message_details(service, message_id: str) -> dict | None:
    """Fetch full message — skip SENT/DRAFT/own emails."""
    try:
        msg = service.users().messages().get(
            userId="me",
            id=message_id,
            format="full"
        ).execute()

        label_ids = msg.get("labelIds", [])
        if "INBOX" not in label_ids:
            return None
        if "SENT" in label_ids or "DRAFT" in label_ids:
            return None

        headers = {
            h["name"].lower(): h["value"]
            for h in msg["payload"]["headers"]
        }

        from_header = headers.get("from", "")
        from_email = extract_email_address(from_header)

        # Skip own emails
        if "m128waheed@gmail.com" in from_email.lower():
            return None

        body = extract_body(msg["payload"])
        if not body.strip():
            return None

        return {
            "message_id": message_id,
            "thread_id": msg.get("threadId"),
            "from_email": from_email,
            "from_name": extract_name(from_header),
            "subject": headers.get("subject", "Support Request"),
            "body": body[:3000].strip(),
        }
    except Exception as e:
        logger.error("get_message_failed", error=str(e))
        return None

def fetch_new_emails(old_history_id: str) -> tuple[list, str]:
    """
    KEY FIX: Use OLD history_id to fetch — NOT the new one from Pub/Sub.
    Returns (emails, new_history_id_to_save)
    """
    try:
        service = get_gmail_service()
        if not service:
            return [], old_history_id

        logger.info("fetching_from_old_history_id",
                   old_history_id=old_history_id)

        history_response = service.users().history().list(
            userId="me",
            startHistoryId=old_history_id,
            historyTypes=["messageAdded"],
            labelId="INBOX"
        ).execute()

        new_history_id = history_response.get("historyId", old_history_id)
        logger.info("history_fetched",
                   has_history="history" in history_response,
                   new_history_id=new_history_id,
                   records=len(history_response.get("history", [])))

        # Collect message IDs
        message_ids_seen = set()
        message_ids = []

        for record in history_response.get("history", []):
            for msg_added in record.get("messagesAdded", []):
                mid = msg_added["message"]["id"]
                if mid not in message_ids_seen:
                    message_ids_seen.add(mid)
                    message_ids.append(mid)

        logger.info("message_ids_collected", count=len(message_ids))

        # Fetch full details
        emails = []
        for message_id in message_ids:
            details = get_message_details(service, message_id)
            if details:
                emails.append(details)
                logger.info("email_accepted",
                           from_email=details["from_email"],
                           subject=details["subject"])

        return emails, new_history_id

    except Exception as e:
        error_str = str(e)
        if "404" in error_str:
            logger.error("history_id_expired_need_full_sync",
                        old_history_id=old_history_id)
            # Get fresh history_id
            try:
                service = get_gmail_service()
                profile = service.users().getProfile(userId="me").execute()
                fresh_id = profile.get("historyId", old_history_id)
                save_history_id(fresh_id)
                logger.info("fresh_history_id_saved", history_id=fresh_id)
            except Exception:
                pass
        else:
            logger.error("fetch_history_failed", error=error_str)
        return [], old_history_id

# ─── GMAIL SEND ───────────────────────────────────────

async def send_gmail_reply(
    to_email: str,
    subject: str,
    body: str,
    thread_id: str = None
) -> bool:
    try:
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        service = get_gmail_service()
        if not service:
            return False

        msg = MIMEMultipart("alternative")
        msg["to"] = to_email
        msg["subject"] = (
            f"Re: {subject}"
            if not subject.lower().startswith("re:")
            else subject
        )
        msg.attach(MIMEText(body, "plain"))

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
        send_body = {"raw": raw}
        if thread_id:
            send_body["threadId"] = thread_id

        result = service.users().messages().send(
            userId="me", body=send_body
        ).execute()

        logger.info("gmail_reply_sent",
                   to=to_email,
                   message_id=result["id"])
        return True
    except Exception as e:
        logger.error("gmail_reply_failed", error=str(e))
        return False

# ─── AGENT PROCESSING ─────────────────────────────────

async def process_email_with_agent(
    customer_id: str,
    subject: str,
    message: str,
    from_email: str,
    thread_id: str
):
    os.environ["OPENAI_API_KEY"] = settings.openai_api_key
    os.environ["CURRENT_THREAD_ID"] = thread_id or ""
    os.environ["CURRENT_CUSTOMER_EMAIL"] = from_email

    try:
        logger.info("email_agent_start",
                   from_email=from_email,
                   subject=subject)

        result = await run_agent(
            message=message,
            customer_id=customer_id,
            channel="email",
            ticket_subject=subject
        )

        logger.info("email_agent_done",
                   from_email=from_email,
                   success=result["success"])

        # Send reply
        if result["success"] and result.get("output"):
            await send_gmail_reply(
                to_email=from_email,
                subject=subject,
                body=result["output"],
                thread_id=thread_id
            )
    except Exception as e:
        logger.error("email_agent_failed", error=str(e))

# ─── WEBHOOK ──────────────────────────────────────────

@router.post("/gmail")
async def gmail_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Gmail Pub/Sub webhook.

    CRITICAL FIX: Pub/Sub history_id = NEW state (always empty if used directly)
    Solution: Use SAVED old history_id to fetch changes, save new one for next time.
    """
    try:
        body = await request.json()
        pubsub_message = body.get("message", {})

        if not pubsub_message:
            return {"status": "no_message"}

        data_b64 = pubsub_message.get("data", "")
        if not data_b64:
            return {"status": "no_data"}

        decoded = json.loads(
            base64.b64decode(data_b64).decode("utf-8")
        )

        new_history_id = decoded.get("historyId")
        email_address = decoded.get("emailAddress")

        logger.info("pubsub_received",
                   new_history_id=new_history_id,
                   email=email_address)

        # Load OLD history_id (this is what we fetch FROM)
        old_history_id = load_history_id()

        if not old_history_id:
            # First time — save new_history_id and wait for next notification
            logger.info("first_run_saving_history_id",
                       history_id=new_history_id)
            save_history_id(str(new_history_id))
            return {"status": "initialized", "history_id": new_history_id}

        logger.info("fetching_emails",
                   old_history_id=old_history_id,
                   new_history_id=new_history_id)

        # Fetch using OLD history_id
        new_emails, updated_history_id = fetch_new_emails(old_history_id)

        # Save updated history_id for next time
        save_history_id(str(updated_history_id))

        logger.info("emails_found", count=len(new_emails))

        if not new_emails:
            return {"status": "no_new_emails"}

        pool = request.app.state.pool

        for email_data in new_emails:
            customer = await create_customer(
                pool,
                email_data["from_email"],
                email_data["from_name"]
            )
            customer_id = str(customer["id"])

            conv = await create_conversation(pool, customer_id, "email")
            await save_message(
                pool, str(conv["id"]),
                "email", "inbound", "customer",
                f"Subject: {email_data['subject']}\n\n{email_data['body']}"
            )

            logger.info("email_queued_for_agent",
                       from_email=email_data["from_email"],
                       subject=email_data["subject"])

            background_tasks.add_task(
                process_email_with_agent,
                customer_id,
                email_data["subject"],
                email_data["body"],
                email_data["from_email"],
                email_data["thread_id"] or ""
            )

        return {
            "status": "processing",
            "emails_queued": len(new_emails)
        }

    except Exception as e:
        logger.error("gmail_webhook_error", error=str(e))
        return {"status": "error", "detail": str(e)}

# ─── STATUS & TEST ────────────────────────────────────

@router.get("/gmail/status")
async def gmail_status():
    token_exists = os.path.exists("../context/token.json")
    creds_exists = os.path.exists("../context/credentials.json")
    saved_id = load_history_id()
    return {
        "credentials_file": creds_exists,
        "token_file": token_exists,
        "status": "ready" if token_exists else "needs_auth",
        "saved_history_id": saved_id,
        "webhook_url": "https://quintic-ozonic-mardell.ngrok-free.dev/webhooks/gmail"
    }

@router.get("/gmail/test")
async def gmail_test(request: Request, background_tasks: BackgroundTasks):
    """Simulate incoming email from muhammadwaheed128@gmail.com."""
    pool = request.app.state.pool

    test_email = {
        "from_email": "muhammadwaheed128@gmail.com",
        "from_name": "Muhammad Waheed",
        "subject": "2FA reset issue",
        "body": "Hi, I changed my phone and cannot login because 2FA is not working. How do I reset it?",
        "thread_id": ""
    }

    customer = await create_customer(
        pool, test_email["from_email"], test_email["from_name"]
    )
    customer_id = str(customer["id"])

    conv = await create_conversation(pool, customer_id, "email")
    await save_message(
        pool, str(conv["id"]),
        "email", "inbound", "customer",
        f"Subject: {test_email['subject']}\n\n{test_email['body']}"
    )

    background_tasks.add_task(
        process_email_with_agent,
        customer_id,
        test_email["subject"],
        test_email["body"],
        test_email["from_email"],
        test_email["thread_id"]
    )

    return {
        "status": "processing",
        "from": test_email["from_email"],
        "note": "Reply will be sent to muhammadwaheed128@gmail.com"
    }

@router.post("/gmail/init-history")
async def init_history():
    """
    Call this ONCE to initialize history_id from Gmail profile.
    Run before sending test email.
    """
    try:
        service = get_gmail_service()
        profile = service.users().getProfile(userId="me").execute()
        history_id = profile.get("historyId")
        save_history_id(str(history_id))
        return {
            "status": "initialized",
            "history_id": history_id,
            "message": "Now send a test email to m128waheed@gmail.com"
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}
