from passlib.context import CryptContext
from fastapi.concurrency import run_in_threadpool



password_context = CryptContext(
    schemes = ["bcrypt"], 
    deprecated = "auto"
)
"""Password hashing context using bcrypt algorithm.

Configured with bcrypt as the default scheme for secure password hashing.
Auto-deprecated schemes will be handled automatically.
"""




async def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt.

    Truncates the password to 72 bytes (bcrypt limit) and hashes it
    using the configured password context.

    Args:
        password: Plain-text password to hash.

    Returns:
        str: Bcrypt-hashed password string.
    """
    password_bytes: bytes = password.encode("utf-8")[:72]

    password_truncated: str = password_bytes.decode(
        "utf-8", 
        errors = "ignore"
    )

    return await run_in_threadpool(
        password_context.hash, 
        password_truncated
    )



async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a hashed password.

    Compares the plain password with the stored hash to authenticate users.

    Args:
        plain_password: Plain-text password to verify.
        hashed_password: Stored bcrypt hash to compare against.

    Returns:
        bool: True if password matches the hash, False otherwise.
            Also returns False if hashed_password is empty or None.
    """
    if not hashed_password:
        return False
    
    return await run_in_threadpool(
        password_context.verify,
        plain_password,
        hashed_password
    )