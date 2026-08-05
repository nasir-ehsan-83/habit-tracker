from contextlib import asynccontextmanager
from fastapi import (
    FastAPI,
    Request,
    status
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.utils import limiter
from app.core import cors
from app.db import init_db
from app.routes import (
    auth, 
    habits, 
    users
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db() 
    yield

app = FastAPI(
    lifespan = lifespan
)

app.add_middleware(
    CORSMiddleware,
    **cors
)

app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code = status.HTTP_429_TOO_MANY_REQUESTS,
        content = {
            "detail": "Too many requests. Please try again later."
        }
    )

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(habits.router)
