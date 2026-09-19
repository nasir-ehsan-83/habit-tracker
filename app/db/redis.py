from redis.asyncio import Redis

from app.config import settings

redis_client: Redis = Redis(
    host = settings.REDIS_HOST,
    port = settings.REDIS_PORT
)
from redis.asyncio import Redis

from app.config import settings

redis_client: Redis = Redis(
    host = settings.REDIS_HOST,
    port = settings.REDIS_PORT
)
"""Redis client instance for session management.

This asynchronous Redis client is configured using settings from the
application configuration() and is used for:
- Session storage
- Rate limiting
- Temporary data storage
"""