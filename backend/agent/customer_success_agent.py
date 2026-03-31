from agents import Agent, Runner
from agent.prompts import SYSTEM_PROMPT
from agent.tools import (
    search_knowledge_base,
    create_ticket,
    get_customer_history,
    escalate_to_human,
    send_response,
)
import structlog
import os

logger = structlog.get_logger()

# Agent definition
customer_success_agent = Agent(
    name="Customer Success FTE",
    model="gpt-4o-mini",
    instructions=SYSTEM_PROMPT,
    tools=[
        create_ticket,
        get_customer_history,
        search_knowledge_base,
        escalate_to_human,
        send_response,
    ],
)

async def run_agent(
    message: str,
    customer_id: str,
    channel: str,
    ticket_subject: str = "Support Request"
) -> dict:
    """Run agent with customer message and return result."""
    try:
        context_message = f"""
=== MANDATORY CONTEXT ===
customer_id = "{customer_id}"
channel = "{channel}"
subject = "{ticket_subject}"

RULE: You MUST use customer_id="{customer_id}" when calling create_ticket.
Do NOT use "unknown" or any other value.

=== CUSTOMER MESSAGE ===
{message}
"""
        result = await Runner.run(
            customer_success_agent,
            context_message,
        )
        logger.info("agent_completed", customer_id=customer_id, channel=channel)
        return {
            "success": True,
            "output": result.final_output,
        }
    except Exception as e:
        logger.error("agent_failed", error=str(e))
        return {
            "success": False,
            "output": str(e),
        }
