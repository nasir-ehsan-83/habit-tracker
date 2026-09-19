from contextlib import asynccontextmanager;
from fastapi import (
    FastAPI,
    Request,
    status
);
from fastapi.middleware.cors import CORSMiddleware;
from fastapi.responses import JSONResponse;
from slowapi.errors import RateLimitExceeded;

from app.utils import limiter;
from app.core import cors;
from app.db import init_db;
from app.routes import (
    auth, 
    habits, 
    users
);

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.

    Handles startup and shutdown events.
    - Startup: Initializes database connection.
    - Shutdown: Cleanup resources (if needed).
    """
    await init_db();
    yield

app: FastAPI = FastAPI(
    lifespan = lifespan
);
"""FastAPI application instance."""

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    **cors
);

# Rate limiter state
app.state.limiter = limiter;

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded errors.

    Returns a 429 Too Many Requests response with a user-friendly message.
    """
    return JSONResponse(
        status_code = status.HTTP_429_TOO_MANY_REQUESTS,
        content = {
            "detail": "Too many requests. Please try again later."
        }
    );

# Register routes
app.include_router(auth.router);
app.include_router(users.router);
app.include_router(habits.router);
