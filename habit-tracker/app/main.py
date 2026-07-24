from contextlib import asynccontextmanager
from fastapi import (
    FastAPI,
    Request,
    status
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.utils.limiter import limiter
from app.core.cors import cors
from app.db.database import init_db
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

# setup_offline_docs(app)

# add cors middleware
app.add_middleware(
    CORSMiddleware,
    **cors
)

# add rate-limit
app.state.limiter = limiter
# add handler for rate-limit
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code = status.HTTP_429_TOO_MANY_REQUESTS,
        content = {
            "detail": "Too many requests. Please try again later."
        }
    )

# add routes from app/routes/
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(habits.router)
