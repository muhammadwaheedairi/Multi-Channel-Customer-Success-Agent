import asyncpg
import ssl
import structlog

logger = structlog.get_logger()
_pool = None

async def create_pool(database_url: str) -> asyncpg.Pool:
    global _pool

    # Neon requires SSL
    if "neon.tech" in database_url:
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        _pool = await asyncpg.create_pool(
            dsn=database_url,
            min_size=2,
            max_size=10,
            command_timeout=60,
            ssl=ssl_ctx,
        )
    else:
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
