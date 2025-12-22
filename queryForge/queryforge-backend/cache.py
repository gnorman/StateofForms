import json
import logging
import redis.asyncio as redis
from typing import Any, Optional
import os

logger = logging.getLogger(__name__)

redis_client: Optional[redis.Redis] = None


async def init_redis():
    """Initialize Redis connection on app startup"""
    global redis_client
    try:
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
        redis_client = await redis.from_url(redis_url, encoding="utf8", decode_responses=True)
        await redis_client.ping()
        logger.info(f"Redis connected successfully at {redis_url}")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {str(e)}")
        redis_client = None


async def close_redis():
    """Close Redis connection on app shutdown"""
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")


async def get_cache(key: str) -> Optional[Any]:
    """Get value from Redis cache"""
    if not redis_client:
        return None
    try:
        value = await redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        logger.warning(f"Cache GET error for key '{key}': {str(e)}")
        return None


async def set_cache(key: str, value: Any, ttl: int = 3600) -> bool:
    """Set value in Redis cache with TTL (default 1 hour)"""
    if not redis_client:
        return False
    try:
        await redis_client.setex(key, ttl, json.dumps(value, default=str))
        logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
        return True
    except Exception as e:
        logger.warning(f"Cache SET error for key '{key}': {str(e)}")
        return False


async def delete_cache(key: str) -> bool:
    """Delete value from Redis cache"""
    if not redis_client:
        return False
    try:
        await redis_client.delete(key)
        logger.debug(f"Cache DELETE: {key}")
        return True
    except Exception as e:
        logger.warning(f"Cache DELETE error for key '{key}': {str(e)}")
        return False


async def clear_cache_pattern(pattern: str) -> int:
    """Clear all cache entries matching a pattern (e.g., 'stock:*')"""
    if not redis_client:
        return 0
    try:
        keys = await redis_client.keys(pattern)
        if keys:
            await redis_client.delete(*keys)
            logger.debug(f"Cache CLEAR pattern '{pattern}': {len(keys)} keys deleted")
            return len(keys)
        return 0
    except Exception as e:
        logger.warning(f"Cache CLEAR pattern error '{pattern}': {str(e)}")
        return 0
