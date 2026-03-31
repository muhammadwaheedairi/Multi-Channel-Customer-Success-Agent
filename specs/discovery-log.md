# Discovery Log — Customer Success FTE

## Date: March 2026
## Stage: Incubation Phase

---

## Exercise 1.1 — Initial Exploration

### Channel Patterns Discovered
- **Email**: Longer messages, formal tone, customers expect detailed responses
- **WhatsApp**: Short, casual, emoji acceptable, max 300 chars preferred
- **Web Form**: Semi-formal, structured, customers provide more context upfront

### Ticket Categories Found (from sample-tickets.json)
1. Authentication issues (password reset, 2FA) — 30% of tickets
2. Integration problems (Slack, Google) — 20%
3. Billing/refund requests — 15% → MUST escalate
4. Pricing inquiries — 10% → MUST escalate
5. General how-to questions — 25%

### Key Patterns
- Angry customers always use CAPS or exclamation marks
- WhatsApp "human" keyword = immediate escalation needed
- Pricing questions NEVER answered by AI
- Refund requests ALWAYS need human agent

---

## Exercise 1.2 — Core Loop Prototype

### What Worked
- Simple keyword search in product-docs.md effective for common queries
- Channel metadata normalization before agent processing
- Response formatting per channel (email vs chat)

### What Failed Initially
- Agent tried to answer pricing questions → Fixed with hard constraint
- WhatsApp responses too long → Fixed with 300 char limit
- Empty messages caused crashes → Added validation

### Iteration Log
1. v1: Basic search + respond (no channel awareness)
2. v2: Added channel-specific formatting
3. v3: Added escalation rules
4. v4: Added conversation memory via DB

---

## Exercise 1.3 — Memory & State

### Decisions Made
- PostgreSQL for persistent conversation state (not in-memory)
- customer_identifiers table for cross-channel matching
- Email as primary identifier, phone for WhatsApp
- 24-hour active conversation window

### Sentiment Tracking
- Planned: DECIMAL(3,2) sentiment_score in conversations table
- Trigger: sentiment < 0.3 → escalate_to_human
- Tool: OpenAI response analysis

---

## Exercise 1.4 — MCP Tools → Production Tools

### Tools Defined
| Tool | MCP Version | Production Version |
|------|------------|-------------------|
| search_knowledge_base | String matching | pgvector semantic search |
| create_ticket | In-memory | PostgreSQL asyncpg |
| get_customer_history | Session only | Cross-channel DB query |
| escalate_to_human | Print statement | DB update + Kafka event |
| send_response | Console output | Channel-aware formatter |

---

## Exercise 1.5 — Edge Cases Found

| # | Edge Case | Channel | Handling |
|---|-----------|---------|----------|
| 1 | Empty message | All | Return clarification request |
| 2 | Pricing question | All | Immediate escalation |
| 3 | Refund request | All | Immediate escalation |
| 4 | "human" keyword | WhatsApp | Immediate escalation |
| 5 | Legal threat | All | Immediate escalation |
| 6 | Angry customer (CAPS) | All | Escalate with empathy |
| 7 | Unknown product feature | All | Escalate after 2 searches |
| 8 | Very long message | WhatsApp | Truncate response to 300 chars |
| 9 | Duplicate ticket | All | Check active conversation first |
| 10 | Cross-channel same customer | All | Unified customer_id lookup |

---

## Performance Baseline (Prototype)
- Average response time: ~10-15 seconds (OpenAI API latency)
- Accuracy on test set: 6/6 (100%) edge cases handled
- Escalation rate: ~50% (pricing + refund + human requests)
- Cross-channel identification: 100% (email-based lookup)
