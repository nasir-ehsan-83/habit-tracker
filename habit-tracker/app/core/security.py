from passlib.context import CryptContext
from fastapi.concurrency import run_in_threadpool



password_context = CryptContext(
    schemes = ["bcrypt"], 
    deprecated = "auto"
)




async def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")[:72]

    password_truncated = password_bytes.decode(
        "utf-8", 
        errors="ignore"
    )

    return await run_in_threadpool(
        password_context.hash, 
        password_truncated
    )



async def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password:
        return False
    
    return await run_in_threadpool(
        password_context.verify,
        plain_password,
        hashed_password
    )