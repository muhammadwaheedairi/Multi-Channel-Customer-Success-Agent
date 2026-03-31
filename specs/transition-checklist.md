# Transition Checklist: General Agent → Custom Agent

## Status: COMPLETE ✅

---

## 1. Discovered Requirements
- [x] Multi-channel support (email, whatsapp, web_form)
- [x] Channel-aware response formatting
- [x] Unified customer identity across channels
- [x] Escalation rules (pricing, refund, legal, angry, human)
- [x] Conversation history persistence (PostgreSQL)
- [x] Ticket lifecycle management
- [x] Knowledge base search
- [x] Background task processing

## 2. Working System Prompt
Extracted to: `agent/prompts.py` → `SYSTEM_PROMPT`

Key additions from incubation:
- Strict workflow order (create_ticket FIRST)
- Channel-specific instructions
- Hard constraints (never pricing, never refund)
- Escalation triggers with reason codes

## 3. Edge Cases → Test Cases

| Edge Case | Test | Status |
|-----------|------|--------|
| Password reset (email) | test_password_reset_email | ✅ PASS |
| Short response (WhatsApp) | test_whatsapp_short_response | ✅ PASS |
| Pricing escalation | test_pricing_escalation | ✅ PASS |
| Refund escalation | test_refund_escalation | ✅ PASS |
| Human request (WhatsApp) | test_human_request_whatsapp | ✅ PASS |
| Technical help (Slack) | test_slack_integration_help | ✅ PASS |

## 4. Code Mapping

| Incubation | Production |
|-----------|------------|
| MCP server tools | `@function_tool` in `agent/tools.py` |
| In-memory state | PostgreSQL via asyncpg |
| Print statements | structlog JSON logging |
| Manual testing | pytest-asyncio test suite |
| Direct API calls | FastAPI routers + background tasks |
| Single channel | 3 channel handlers |

## 5. Performance Baseline
- Response time: ~10-15s (OpenAI gpt-4o-mini)
- Test accuracy: 6/6 (100%)
- Channels tested: 3/3
- Escalation working: ✅

## 6. Production Checklist
- [x] Database schema — 7 tables
- [x] Kafka topics — 7 topics defined
- [x] Channel handlers — gmail, whatsapp, web_form
- [x] Kubernetes manifests — 6 files
- [x] Docker images — built and tested
- [x] Error handling — try/catch in all tools
- [x] Pydantic v2 validation — all inputs
- [x] Environment variables — .env + pydantic-settings

## 7. Response Patterns Discovered

### Email Pattern (Worked Best)
```
Dear {name},

[Empathy line if frustrated]
[Direct answer in 2-3 sentences]
[Step by step if needed]

Best regards,
TechCorp AI Support
---
Ticket: {ticket_id}
```

### WhatsApp Pattern (Worked Best)
```
[Direct answer max 2 sentences] ✅
📱 Type 'human' for live support.
```

### Web Form Pattern (Worked Best)
```
[Answer with numbered steps if needed]

---
Need more help? Reply to this message.
```

## 8. MCP → Production Tool Comparison

| Aspect | MCP (Incubation) | OpenAI SDK (Production) |
|--------|-----------------|------------------------|
| Input validation | None | Pydantic v2 BaseModel |
| Error handling | Crashes | try/catch + fallback |
| Database | In-memory | asyncpg fresh connections |
| Search | String matching | pgvector semantic search |
| Logging | print() | structlog JSON |
| Channel format | Single | Email/WhatsApp/Web aware |
