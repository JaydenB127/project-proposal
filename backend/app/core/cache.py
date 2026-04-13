import json
import logging
from typing import Optional, Any
import redis.asyncio as aioredis
from app.core.config import settings

logger = logging.getLogger(__name__)
_redis: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _redis


async def cache_get(key: str) -> Optional[Any]:
    try:
        r = await get_redis()
        val = await r.get(key)
        return json.loads(val) if val else None
    except Exception as e:
        logger.warning(f"Cache GET failed for {key}: {e}")
        return None


async def cache_set(key: str, value: Any, ttl: int = None) -> None:
    try:
        r = await get_redis()
        ttl = ttl or settings.cache_ttl
        await r.setex(key, ttl, json.dumps(value, default=str))
    except Exception as e:
        logger.warning(f"Cache SET failed for {key}: {e}")


async def cache_delete_pattern(pattern: str) -> None:
    try:
        r = await get_redis()
        keys = await r.keys(pattern)
        if keys:
            await r.delete(*keys)
    except Exception as e:
        logger.warning(f"Cache DELETE failed for {pattern}: {e}")
