from slowapi import Limiter
from slowapi.util import get_remote_address

limiter: Limiter = Limiter(
    key_func = get_remote_address
)
"""Rate limiter instance for API endpoints.

Uses client IP address as the rate limiting key.
Apply using @limiter.limit() decorator on routes.

Example:
    @router.get("/")
    @limiter.limit("5/minute")
    async def route(request: Request):
        return {"message": "Limited"}
"""