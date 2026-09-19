from hashlib import sha256
from asyncio import (
    AbstractEventLoop, 
    get_running_loop
)
import secrets


async def generate_code() -> int:
    """Generate a 6-digit verification code.

    Returns:
        int: Random number between 100000 and 999999.
    """
    return secrets.randbelow(900000) + 100000


async def generate_token() -> str:
    """Generate a secure URL-safe random token.

    Returns:
        str: 32-byte URL-safe base64 encoded token.
    """
    return secrets.token_urlsafe(32)


async def hash_token(
    token: str | int
) -> str:
    """Hash a token using SHA256.

    Args:
        token: Token to hash (string or integer).

    Returns:
        str: SHA256 hex digest of the token.
    """
    loop: AbstractEventLoop = get_running_loop()
    token_str: str = str(token)
    
    return await loop.run_in_executor(
        None,
        lambda: sha256(token_str.encode("utf-8")).hexdigest()
    )