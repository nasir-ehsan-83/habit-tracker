from pymongo.errors import DuplicateKeyError
from typing import (
    Any, 
    Dict
)
from fastapi import (
    HTTPException,
    Request,
    Response,
    status
)
from fastapi.security import OAuth2PasswordRequestForm

from app.models.users import User
from app.schemas.users import UserCreate
from app.core.security import (
    verify,
    hash
)
from app.config.logging_handler import logger
from app.core.jwt import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token
)




async def handle_create_user(user: UserCreate) -> User:
    try:
        
        if await User.find_one(User.email == user.email):
            
            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT,
                detail = "Email exists"
            )
        
        if await User.find_one(User.username == user.username):
            
            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT, 
                detail = "Username exists"
            )
        
        new_user = User(
            **user.model_dump(exclude = {"password"}),
            password = await hash(user.password)
        )

        return await new_user.insert()
    
    except HTTPException:
        raise
    
    except DuplicateKeyError as error:
        logger.error(f"Duplicate Key Error while registering user: {error}", exc_info = True)
    
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = "Data conflict: The provided credentials are already in use."
        )
    
    except Exception as error:
        logger.error(f"Unexpected error in create_user: {error}", exc_info = True)
    
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )





async def handle_login(
    response: Response, 
    user_credential: OAuth2PasswordRequestForm
) -> Dict[str, str]:

    try:
        
        user = await User.find_one(User.username == user_credential.username) # type: ignore

        if not user:
            logger.warning(f"Login failed: Username '{user_credential.username}' not found.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        if user.status != "active":
            logger.warning(f"Login forbidden: Account '{user_credential.username}' is inactive.")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        if not await verify(user_credential.password, user.password):
            logger.warning(f"Login failed: Incorrect password for user '{user_credential.username}'.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        access_token = await create_access_token({
            "id": str(user.id),
            "role": user.role
        })

        refresh_token = await create_refresh_token({
            "id": str(user.id),
            "role": user.role
        })

        await user.update({ 
            "$set": {
                "refresh_token": refresh_token
            }
        })

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
        raise

    except Exception as error:

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
