"""
Sentiment Analysis Skill.
PDF Exercise 1.5 — Skill 2: Sentiment Analysis
- When to use: Every customer message
- Inputs: message text
- Outputs: sentiment score, confidence
"""
import re
import structlog

logger = structlog.get_logger()

# Negative keywords
NEGATIVE_KEYWORDS = [
    "terrible", "horrible", "awful", "worst", "hate", "useless",
    "broken", "ridiculous", "frustrated", "angry", "furious",
    "disappointed", "unacceptable", "pathetic", "scam", "fraud",
    "lawsuit", "lawyer", "sue", "legal", "refund", "cancel",
    "never again", "waste", "stupid", "idiot", "damn", "hell"
]

# Positive keywords
POSITIVE_KEYWORDS = [
    "great", "excellent", "amazing", "wonderful", "fantastic",
    "helpful", "perfect", "love", "awesome", "thank", "thanks",
    "appreciate", "good", "nice", "pleased", "happy", "satisfied"
]

def analyze_sentiment(text: str) -> dict:
    """
    Analyze sentiment of customer message.
    Returns score 0.0 (very negative) to 1.0 (very positive).
    PDF Skill 2: Sentiment Analysis
    """
    text_lower = text.lower()

    # Count caps — anger indicator
    caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
    exclamation_count = text.count('!')
    question_count = text.count('?')

    # Score negative keywords
    negative_count = sum(1 for kw in NEGATIVE_KEYWORDS if kw in text_lower)
    positive_count = sum(1 for kw in POSITIVE_KEYWORDS if kw in text_lower)

    # Base score 0.5 (neutral)
    score = 0.5

    # Adjust for keywords
    score -= negative_count * 0.1
    score += positive_count * 0.1

    # Adjust for caps (anger)
    if caps_ratio > 0.3:
        score -= 0.2

    # Adjust for exclamations (frustration)
    if exclamation_count > 2:
        score -= 0.1

    # Clamp between 0 and 1
    score = max(0.0, min(1.0, score))

    # Determine label
    if score < 0.3:
        label = "negative"
        should_escalate = True
    elif score < 0.5:
        label = "slightly_negative"
        should_escalate = False
    elif score < 0.7:
        label = "neutral"
        should_escalate = False
    else:
        label = "positive"
        should_escalate = False

    result = {
        "score": round(score, 2),
        "label": label,
        "should_escalate": should_escalate,
        "indicators": {
            "caps_ratio": round(caps_ratio, 2),
            "exclamations": exclamation_count,
            "negative_keywords": negative_count,
            "positive_keywords": positive_count,
        }
    }

    logger.info("sentiment_analyzed",
               score=result["score"],
               label=result["label"])
    return result

async def save_sentiment_to_db(
    pool,
    conversation_id: str,
    score: float
):
    """Save sentiment score to conversations table."""
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                """UPDATE conversations
                   SET sentiment_score = $1
                   WHERE id = $2""",
                score, conversation_id
            )
    except Exception as e:
        logger.error("sentiment_save_failed", error=str(e))
