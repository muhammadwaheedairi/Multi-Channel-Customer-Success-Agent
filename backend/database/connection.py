import asyncpg
import structlog

logger = structlog.get_logger()
_pool = None

async def create_pool(database_url: str) -> asyncpg.Pool:
    global _pool
    _pool = await asyncpg.create_pool(
        dsn=database_url,
        min_size=5,
        max_size=20,
        command_timeout=60,
    )
    logger.info("db_pool_created")
    return _pool

async def get_pool() -> asyncpg.Pool:
    return _pool

async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        logger.info("db_pool_closed")
