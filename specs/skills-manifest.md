# Agent Skills Manifest — Customer Success FTE

## Skill 1: Knowledge Retrieval
- **When**: Customer asks product questions
- **Tool**: `search_knowledge_base`
- **Input**: query text, max_results
- **Output**: Relevant documentation snippets
- **Fallback**: "No docs found" → escalate after 2 attempts

## Skill 2: Ticket Management
- **When**: Every conversation start (MANDATORY)
- **Tool**: `create_ticket`
- **Input**: customer_id, issue, channel, category, priority
- **Output**: ticket_id for reference

## Skill 3: Customer History
- **When**: After ticket creation, before responding
- **Tool**: `get_customer_history`
- **Input**: customer_id
- **Output**: Last 5 messages across ALL channels

## Skill 4: Escalation Decision
- **When**: Pricing/refund/legal/angry/human request detected
- **Tool**: `escalate_to_human`
- **Input**: ticket_id, reason, urgency
- **Output**: Confirmation + human agent notified

## Skill 5: Channel Adaptation
- **When**: Before every send_response call
- **Tool**: `send_response` (with built-in formatter)
- **Input**: ticket_id, message, channel
- **Output**: Formatted response for email/whatsapp/web_form

## Skill 6: Customer Identification
- **When**: Every incoming message
- **Logic**: Email → customers.email lookup
           Phone → customer_identifiers WHERE type='whatsapp'
- **Output**: unified customer_id, merged history
