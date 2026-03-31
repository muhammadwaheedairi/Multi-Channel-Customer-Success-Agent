import openai
import structlog
import os
import ssl

logger = structlog.get_logger()

async def generate_embedding(text: str) -> list[float]:
    """Generate OpenAI embedding for text."""
    try:
        client = openai.AsyncOpenAI(
            api_key=os.environ.get("OPENAI_API_KEY")
        )
        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input=text[:8000]
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error("embedding_failed", error=str(e))
        return []

def embedding_to_str(embedding: list[float]) -> str:
    """Convert embedding list to pgvector string format."""
    return f"[{','.join(map(str, embedding))}]"

def get_db_url():
    return os.environ.get(
        "DATABASE_URL",
        "postgresql://fte_user:fte_password@localhost:5432/fte_db"
    )

async def get_conn():
    import asyncpg
    url = get_db_url()
    if "neon.tech" in url:
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        return await asyncpg.connect(url, ssl=ssl_ctx)
    return await asyncpg.connect(url)

async def update_knowledge_base_embeddings():
    """Generate embeddings for all knowledge base entries."""
    conn = await get_conn()
    try:
        rows = await conn.fetch(
            "SELECT id, title, content FROM knowledge_base WHERE embedding IS NULL"
        )
        logger.info("updating_embeddings", count=len(rows))
        for row in rows:
            text = f"{row['title']}\n{row['content']}"
            embedding = await generate_embedding(text)
            if embedding:
                embedding_str = embedding_to_str(embedding)
                await conn.execute(
                    "UPDATE knowledge_base SET embedding = $1::vector WHERE id = $2",
                    embedding_str, row['id']
                )
                logger.info("embedding_updated", title=row['title'])
        logger.info("embeddings_complete")
    finally:
        await conn.close()
