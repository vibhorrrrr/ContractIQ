"""Health check endpoint — no auth required."""

import redis.asyncio as aioredis
from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import settings
from app.core.database import async_session

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """Check database and Redis connectivity."""
    db_status = "ok"
    redis_status = "ok"

    # Check DB
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    # Check Redis
    try:
        r = aioredis.from_url(settings.REDIS_URL)
        await r.ping()
        await r.aclose()
    except Exception:
        redis_status = "error"

    overall = "ok" if db_status == "ok" and redis_status == "ok" else "degraded"
    return {"status": overall, "db": db_status, "redis": redis_status}
