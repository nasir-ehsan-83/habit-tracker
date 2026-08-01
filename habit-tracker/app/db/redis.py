from redis.asyncio import Redis

from app.config import settings

redis_client: Redis = Redis(
    host = settings.REDIS_HOST,
    port = settings.REDIS_PORT
)