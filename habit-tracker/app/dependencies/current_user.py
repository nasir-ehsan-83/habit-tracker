from fastapi import (
    Depends, 
    HTTPException, 
    status
)
from fastapi.security import OAuth2PasswordBearer

from app.core import verify_access_token



oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "login")



async def get_current_user(token: str = Depends(oauth2_scheme)):

    credential_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Could not validate credentials",
        headers = {"WWW-Authenticate": "Bearer"}
    )

    return await verify_access_token(token,credential_exception)
""" 
    # get user from database
    user = await User.get(token_data.id)

    if not user:
        raise credential_exception

    # if user is deleted or inactive
    if user.status != "active":
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "User account is inactive"
        )

    return user 
"""