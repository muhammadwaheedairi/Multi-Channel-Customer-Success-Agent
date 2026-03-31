import pytest
import asyncio
from database.connection import create_pool, close_pool
from database.queries import create_customer
from agent.customer_success_agent import run_agent

DATABASE_URL = "postgresql://fte_user:fte_password@localhost:5432/fte_db"

@pytest.fixture(scope="module")
async def pool():
    p = await create_pool(DATABASE_URL)
    yield p
    await close_pool()

@pytest.fixture(scope="module")
async def customer_id(pool):
    customer = await create_customer(pool, "agenttest@example.com", "Agent Test User")
    return str(customer["id"])

# ─── TEST CASES ───────────────────────────────────────────

@pytest.mark.asyncio
async def test_password_reset_email(customer_id):
    """Email: Password reset question should get helpful response."""
    result = await run_agent(
        message="I forgot my password and cannot login",
        customer_id=customer_id,
        channel="email",
        ticket_subject="Login Issue"
    )
    assert result["success"] is True
    assert result["output"] is not None
    print(f"\n✅ Email response:\n{result['output'][:200]}")

@pytest.mark.asyncio
async def test_whatsapp_short_response(customer_id):
    """WhatsApp: Response should be concise."""
    result = await run_agent(
        message="how do i add team members",
        customer_id=customer_id,
        channel="whatsapp",
        ticket_subject="Team Help"
    )
    assert result["success"] is True
    print(f"\n✅ WhatsApp response:\n{result['output'][:200]}")

@pytest.mark.asyncio
async def test_pricing_escalation(customer_id):
    """Pricing question MUST escalate."""
    result = await run_agent(
        message="How much does the enterprise plan cost?",
        customer_id=customer_id,
        channel="web_form",
        ticket_subject="Pricing"
    )
    assert result["success"] is True
    output_lower = result["output"].lower()
    assert any(word in output_lower for word in ["escalat", "human", "team", "pricing"])
    print(f"\n✅ Pricing escalation:\n{result['output'][:200]}")

@pytest.mark.asyncio
async def test_refund_escalation(customer_id):
    """Refund request MUST escalate."""
    result = await run_agent(
        message="I want a refund for last month",
        customer_id=customer_id,
        channel="email",
        ticket_subject="Refund"
    )
    assert result["success"] is True
    output_lower = result["output"].lower()
    assert any(word in output_lower for word in ["escalat", "human", "billing", "team"])
    print(f"\n✅ Refund escalation:\n{result['output'][:200]}")

@pytest.mark.asyncio
async def test_human_request_whatsapp(customer_id):
    """WhatsApp 'human' keyword MUST escalate."""
    result = await run_agent(
        message="human",
        customer_id=customer_id,
        channel="whatsapp",
        ticket_subject="Human Request"
    )
    assert result["success"] is True
    print(f"\n✅ Human request:\n{result['output'][:200]}")

@pytest.mark.asyncio
async def test_slack_integration_help(customer_id):
    """Technical question should search docs and respond."""
    result = await run_agent(
        message="How do I connect Slack to TechCorp?",
        customer_id=customer_id,
        channel="web_form",
        ticket_subject="Slack Integration"
    )
    assert result["success"] is True
    print(f"\n✅ Slack help:\n{result['output'][:200]}")
