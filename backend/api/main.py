from contextlib import asynccontextmanager
from fastapi import FastAPI
from core.config import settings
import structlog

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup", env=settings.environment)
    yield
    logger.info("shutdown")

app = FastAPI(
    title="Customer Success FTE API",
    version="1.0.0",
    lifespan=lifespan,
)

@app.get("/health")
async def health():
    return {"status": "healthy", "env": settings.environment}
