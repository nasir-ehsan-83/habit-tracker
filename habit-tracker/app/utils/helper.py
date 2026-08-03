from hashlib import sha256
import asyncio
import secrets


async def generate_code() -> int:
    return secrets.randbelow(900000) + 100000


async def generate_token() -> str:
    return secrets.token_urlsafe(32)


async def hash_token(
    token: str | int
) -> str:
    loop = asyncio.get_running_loop()
    token_str = str(token)
    
    return await loop.run_in_executor(
        None,
        lambda: sha256(token_str.encode("utf-8")).hexdigest()
    )
