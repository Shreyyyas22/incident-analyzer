import time
from fastapi import HTTPException, status
import redis.asyncio as redis
from app.config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

RATE_LIMIT_MAX_REQUESTS = 1000
RATE_LIMIT_WINDOW_SECONDS = 60

async def check_rate_limit(service_id: str):
    """
    Sliding window rate limiter using Redis ZSET.
    """
    key = f"rate_limit:{service_id}"
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW_SECONDS

    async with redis_client.pipeline(transaction=True) as pipe:
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zadd(key, {str(now): now})
        pipe.zcard(key)
        pipe.expire(key, RATE_LIMIT_WINDOW_SECONDS)
        
        _, _, request_count, _ = await pipe.execute()

    if request_count > RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum 1000 requests per minute."
        )
