# Escalation Rules

## MUST Escalate Immediately
- Pricing questions → reason: "pricing_inquiry"
- Refund requests → reason: "refund_request"
- Legal threats ("lawyer", "sue", "legal action") → reason: "legal_threat"
- Profanity or aggression → reason: "angry_customer"
- Customer types "human", "agent", "representative" → reason: "human_requested"

## Escalate After 2 Failed Searches
- Cannot find answer in knowledge base → reason: "no_answer_found"

## Never Escalate
- Password reset questions
- How-to questions covered in docs
- Bug reports (create ticket + acknowledge)
