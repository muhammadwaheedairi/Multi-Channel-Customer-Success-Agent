from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from core.config import settings
from core.logging import setup_logging
from core.exceptions import FTEException, fte_exception_handler, generic_exception_handler
from database.connection import create_pool, close_pool, get_pool
from api.routers.support_form import router as support_router
from api.routers.customers import router as customers_router
from api.routers.tickets import router as tickets_router
from api.routers.metrics import router as metrics_router
from api.routers.conversations import router as conversations_router
from channels.whatsapp_handler import router as whatsapp_router
from channels.gmail_handler import router as gmail_router
import structlog

setup_logging()
logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await create_pool(settings.database_url)
    logger.info("startup", env=settings.environment)
    yield
    await close_pool()
    logger.info("shutdown")

app = FastAPI(
    title="Customer Success FTE API",
    description="""
## Digital FTE Factory — Customer Success Agent API

24/7 AI-powered customer support across **Web Form**, **WhatsApp**, and **Gmail**.

### Channels
- `POST /support/submit` — Web Form intake
- `POST /webhooks/whatsapp` — Twilio WhatsApp
- `POST /webhooks/gmail` — Gmail Pub/Sub

### Agent Tools
- `search_knowledge_base` — pgvector semantic search
- `create_ticket` — CRM ticket creation
- `get_customer_history` — Cross-channel history
- `escalate_to_human` — Human handoff
- `send_response` — Channel-aware reply

### Quick Test
```bash
curl -X POST /support/submit -d '{"name":"Test","email":"t@t.com",
"subject":"Help","category":"technical","message":"I need help with API"}'
```
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(FTEException, fte_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
app.include_router(support_router)
app.include_router(customers_router)
app.include_router(tickets_router)
app.include_router(metrics_router)
app.include_router(conversations_router)
app.include_router(whatsapp_router)
app.include_router(gmail_router)

@app.get("/health", tags=["system"])
async def health():
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.fetchval("SELECT 1")
    return {
        "status": "healthy",
        "env": settings.environment,
        "database": "connected",
        "channels": ["web_form", "whatsapp", "email"]
    }
