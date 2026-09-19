from fastapi import (
    Depends, 
    HTTPException, 
    status
)
from fastapi.security import OAuth2PasswordBearer

from app.core import verify_access_token



oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "login")
"""OAuth2 password bearer token scheme.

Extracts the JWT token from the Authorization header.
The token URL points to the login endpoint.
"""



async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get the current authenticated user from the JWT token.

    Extracts and verifies the access token from the request,
    returning the user data if valid.

    Args:
        token: JWT access token from the Authorization header.

    Returns:
        TokenData: Decoded token data containing user ID and role.

    Raises:
        HTTPException 401: If token is invalid, expired, or missing.
    """
    credential_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Could not validate credentials",
        headers = {"WWW-Authenticate": "Bearer"}
    )

    return await verify_access_token(token, credential_exception)