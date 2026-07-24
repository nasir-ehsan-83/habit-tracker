from typing import Any, Dict
from fastapi import (
    HTTPException,
    Request,
    Response,
    status
)
from fastapi.security import OAuth2PasswordRequestForm

from app.models.users import User
from app.core.security import verify
from app.config.logging_handler import logger
from app.core.jwt import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token
)


async def handle_login(
    response: Response, 
    user_credential: OAuth2PasswordRequestForm
) -> Dict[str, str]:

    try:
        # Get user from database
        user = await User.find_one(User.username == user_credential.username) # type: ignore

        # If user not found
        if not user:
            logger.warning(f"Login failed: Username '{user_credential.username}' not found.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        # If user found but is inactive or deleted
        if user.status != "active":
            logger.warning(f"Login forbidden: Account '{user_credential.username}' is inactive.")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Verify password 
        if not await verify(user_credential.password, user.password):
            logger.warning(f"Login failed: Incorrect password for user '{user_credential.username}'.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        # Create JWT access-token 
        access_token = await create_access_token({
            "id": str(user.id),
            "role": user.role
        })

        # Create JWT refresh-token
        refresh_token = await create_refresh_token({
            "id": str(user.id),
            "role": user.role
        })

        # Add refresh token to database
        await user.update({ # type: ignore
            "$set": {
                "refresh_token": refresh_token
            }
        })

        # Return refresh-token as cookie
        response.set_cookie(
            key="jwt",
            value=refresh_token,
            httponly = True,
            max_age = 7 * 24 * 60 * 60
            # secure = True, samesite = "lax"  <- Recommended for production security
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    except HTTPException:
        # Re-raise explicit HTTP exceptions to maintain intended API behavior
        raise
    except Exception as error:
        # Log unexpected system errors 
        logger.error(f"Unexpected Login Exception: {error}", exc_info = True)
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )


async def handle_refresh_token(request: Request) -> Dict[str, str]:
    try:
        # Get refresh-token from cookies
        refresh_token = request.cookies.get("jwt")

        # If refresh-token does not exist
        if not refresh_token:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Refresh token not found"
            )

        payload: Dict[str, Any] | HTTPException = await verify_refresh_token(refresh_token)

        # Get user from database
        user: User = await User.get(payload["id"]) # type: ignore

        # If user not found
        if not user:
            logger.warning(f"Refresh token used for non-existent user ID: {payload.get('id')}")
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "User not found"
            )

        # If user is inactive or deleted
        if user.status != "active":
            logger.warning(f"Refresh token blocked: User account '{user.username}' is inactive.")
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "User account is inactive"
            )

        # Verify refresh-token with user.refresh_token (Reuse detection)
        if user.refresh_token != refresh_token:
            logger.error(f"Potential Token Reuse Attack! Token mismatch for user: {user.username}")
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Invalid refresh token"
            )

        # Create new JWT access-token
        access_token = await create_access_token({
            "id": payload["id"], # type: ignore
            "role": payload["role"] # type: ignore
        })

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    except HTTPException:
        raise
    except Exception as error:
        logger.error(f"Unexpected Refresh Token Exception: {error}", exc_info = True)
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def handle_logout(request: Request) -> Response:
    
    refresh_token = request.cookies.get("jwt")
    response = Response(status_code = status.HTTP_204_NO_CONTENT)

    if not refresh_token:
        response.delete_cookie("jwt")
        return response

    try:
        payload = await verify_refresh_token(refresh_token)
        user = await User.get(payload["id"]) # type: ignore
        
        if user:
            await user.update({ # type: ignore
                "$set": {
                    "refresh_token": None
                }
            })

    except Exception as error:
        logger.error(f"Logout Exception: {error}", exc_info = True)

    # Cookie is deleted in all cases (even on DB error) to log out the user from front-end
    response.delete_cookie("jwt")
    return response
