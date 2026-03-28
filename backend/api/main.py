from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.logging import setup_logging
from core.exceptions import FTEException, fte_exception_handler, generic_exception_handler
from database.connection import create_pool, close_pool, get_pool
from api.routers.support_form import router as support_router
from api.routers.customers import router as customers_router
from api.routers.tickets import router as tickets_router
from api.routers.metrics import router as metrics_router
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
    version="1.0.0",
    lifespan=lifespan,
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

@app.get("/health")
async def health():
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.fetchval("SELECT 1")
    return {
        "status": "healthy",
        "env": settings.environment,
        "database": "connected"
    }
