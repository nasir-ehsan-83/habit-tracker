from typing import (
    Any, 
    Dict
)
from beanie import BeanieObjectId
from fastapi import (
    HTTPException, 
    Request, 
    Response, 
    status
)
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from pymongo.errors import DuplicateKeyError

from app.config import logger
from app.core import (
    hash_password, 
    verify_password,
    create_access_token, 
    create_refresh_token, 
    verify_refresh_token
)
from app.utils import (
    generate_code,
    generate_token,
    hash_token,
    send_email
)
from app.db import redis_client
from app.models import (
    User,
    UserPreference
)
from app.schemas import (
    UserCreate,
    VerifyEmail,
    ResetPassword
)




REDIS_REFRESH_PREFIX = "auth:refresh-token:"
REDIS_BLACKLIST_PREFIX = "auth:blacklist:"

REDIS_VERIFY_CODE_PREFIX = "auth:verify-code:"
REDIS_VERIFY_TOKEN_PREFIX = "auth:verify-token:"



async def create_user_service(
    user: UserCreate
) -> User:
    
    """Registers a new user account.

    Creates a new user with the provided credentials, hashes the password,
    and sets up default user preferences. Performs duplicate email check
    before creation.

    Args:
        user: User registration data including email, username, and password.

    Returns:
        User: The created user object with all fields populated.

    Raises:
        HTTPException 409: If username or email already exists.
        HTTPException 500: If an internal server error occurs.
    """

    try:
        new_user: User = User(
            **user.model_dump(exclude = {"password"}),
            password = await hash_password(user.password)
        )
        saved_user: User = await new_user.insert()

        default_preference: UserPreference = UserPreference(owner_id = saved_user.id) # type: ignore
        await default_preference.insert()

        return saved_user

    except DuplicateKeyError:
        
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = "Data conflict: Username or Email already exists."
        )

    except Exception as error:
        logger.error(f"Unexpected error in create_user_service: {error}", exc_info = True)

        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def login_service(
    response:           Response,
    user_credential:    OAuth2PasswordRequestForm
) -> Dict[str, Any]:
    
    """Authenticates a user and returns access tokens.

    Validates user credentials, checks account status, and generates JWT
    access and refresh tokens. Sets refresh token as HTTP-only cookie.

    Args:
        response: FastAPI response object for setting cookies.
        user_credential: User credentials in OAuth2 password flow format.

    Returns:
        Dict[str, Any]: Contains access_token, token_type, and user payload.

    Raises:
        HTTPException 401: If credentials are invalid.
        HTTPException 403: If user account is inactive.
        HTTPException 500: If an internal server error occurs.
    """

    try:
        user: User | None = await User.find_one(User.username == user_credential.username)

        if not user or not await verify_password(user_credential.password, user.password):
            
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Invalid credentials"
            )

        if user.status != "active":
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "User account is inactive"
            )

        user_payload: Dict[str, Any] = {
            "id": str(user.id),
            "role": user.role
        }

        access_token: str= await create_access_token(user_payload)
        refresh_token: str = await create_refresh_token(user_payload)

        await redis_client.set(
            name = f"{REDIS_REFRESH_PREFIX}{user.id}",
            value = refresh_token,
            ex = 7 * 24 * 60 * 60
        )

        response.set_cookie(
            key = "jwt",
            value = refresh_token,
            httponly = True,
            max_age = 7 * 24 * 60 * 60,
            # secure=True,
            # samesite="lax"
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_payload
        }

    except HTTPException:
        raise

    except Exception as error:
        logger.error(f"Unexpected error in login_service: {error}", exc_info = True)

        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def refresh_token_service(
    request:    Request
) -> Dict[str, Any]:
    
    """Refreshes the access token.

    Validates the refresh token from cookies and generates a new access
    token if the refresh token is valid and matches the stored one.

    Args:
        request: FastAPI request object containing cookies.

    Returns:
        Dict[str, Any]: Contains new access_token, token_type, and user payload.

    Raises:
        HTTPException 401: If refresh token is not found.
        HTTPException 403: If token expired or blacklisted.
        HTTPException 500: If an internal server error occurs.
    """

    try:
        refresh_token: str | None = request.cookies.get("jwt")

        if not refresh_token:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Refresh token not found"
            )

        payload: Dict[str, Any] = await verify_refresh_token(refresh_token)
        saved_token: bytes | None = await redis_client.get(f"{REDIS_REFRESH_PREFIX}{payload['id']}")

        if isinstance(saved_token, bytes):
            saved_token = saved_token.decode("utf-8") # type: ignore

        if not saved_token or saved_token != refresh_token:
           
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "Token expired or blacklisted"
            )

        new_access_token: str = await create_access_token({
            "id": payload["id"],
            "role": payload["role"]
        })

        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "user": payload
        }

    except HTTPException:
        raise

    except Exception as error:
        logger.error(f"Unexpected error in refresh_token_service: {error}", exc_info = True)
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def logout_service(
    request:    Request
) -> Response:
    
    """Logs out the authenticated user.

    Clears the refresh token from Redis, blacklists the access token,
    and removes the JWT cookie.

    Args:
        request: FastAPI request object containing cookies and headers.

    Returns:
        Response: Response with cleared cookies.
    """

    refresh_token: str | None = request.cookies.get("jwt")
    auth_header: str | None = request.headers.get("Authorization")
    response: Response = Response(status_code=status.HTTP_204_NO_CONTENT)

    if refresh_token:
        try:
            payload: Dict[str, Any] = await verify_refresh_token(refresh_token)
            await redis_client.delete(f"{REDIS_REFRESH_PREFIX}{payload['id']}")
        
        except Exception:
            pass

    if auth_header and auth_header.startswith("Bearer "):
        try:
            access_token: str = auth_header.split(" ")[1]
            
            await redis_client.set(
                name = f"{REDIS_BLACKLIST_PREFIX}{access_token}",
                value = "revoked",
                ex = 15 * 60
            )
        except Exception:
            pass

    response.delete_cookie("jwt")
    return response




async def delete_account_service(
    request:    Request
) -> Response:
    
    """Permanently deletes the user's account.

    Removes the user from the database along with their refresh token,
    blacklists the access token, and clears authentication cookies.

    Args:
        request: FastAPI request object containing cookies and headers.

    Returns:
        Response: Empty response with status 204.

    Raises:
        HTTPException 401: If refresh token is not found.
        HTTPException 404: If user not found.
        HTTPException 500: If an internal server error occurs.
    """

    try:
        refresh_token: str | None = request.cookies.get("jwt")
        auth_header: str | None = request.headers.get("Authorization")

        if not refresh_token:
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED)

        payload: Dict[str, Any] = await verify_refresh_token(refresh_token)
        user: User | None = await User.get(BeanieObjectId(payload["id"]))

        if not user:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "User not found"
            )

        if auth_header and auth_header.startswith("Bearer "):
            access_token: str = auth_header.split(" ")[1]
            
            await redis_client.set(
                name = f"{REDIS_BLACKLIST_PREFIX}{access_token}",
                value = "revoked",
                ex = 15 * 60
            )

        await redis_client.delete(f"{REDIS_REFRESH_PREFIX}{user.id}")
        await user.delete()

        response: Response = Response(status_code = status.HTTP_204_NO_CONTENT)
        response.delete_cookie("jwt")

        return response

    except HTTPException:
        raise

    except Exception as error:
        logger.error(f"Unexpected error in delete_account_service: {error}", exc_info = True)

        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def forget_password_service(
    email:  EmailStr
) -> Dict[str, str]:
    
    """Initiates the password reset process.

    Sends a verification code to the user's email address. The response
    is the same regardless of whether the email exists for security.

    Args:
        email: The registered email address of the user.

    Returns:
        Dict[str, str]: Success message indicating code was sent.

    Raises:
        HTTPException 500: If an internal server error occurs.
    """

    try:
        user: User | None = await User.find_one(User.email == email)

        if not user:
            return {
                "message": "Verification code sent successfully"
            }

        verify_code: int = await generate_code()
        hashed_code: str = await hash_token(verify_code)

        await redis_client.set(
            name = f"{REDIS_VERIFY_CODE_PREFIX}{email}",
            value = hashed_code,
            ex = 5 * 60
        )

        await send_email(email, verify_code)

        return {
            "message": "Verification code sent successfully"
        }

    except HTTPException:
        raise

    except Exception as error:
        logger.error(f"Unexpected error in forget_password_service: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def verify_email_service(
    data:   VerifyEmail
) -> str:
    
    """Verifies the user's email address.

    Validates the verification code stored in Redis and generates a
    reset token if verification is successful.

    Args:
        data: Email and verification code.

    Returns:
        str: Verification token for password reset.

    Raises:
        HTTPException 404: If user not found.
        HTTPException 403: If token expired or invalid.
        HTTPException 500: If an internal server error occurs.
    """

    try:
        user: User | None = await User.find_one(User.email == data.email)

        if not user:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "User not found"
            )

        saved_code: str | None = await redis_client.get(f"{REDIS_VERIFY_CODE_PREFIX}{data.email}")

        if isinstance(saved_code, bytes):
            saved_code = saved_code.decode("utf-8")

        hashed_input_code: str = await hash_token(data.verify_code)

        if not saved_code or saved_code != hashed_input_code:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "Token expired or blacklisted"
            )

        await redis_client.delete(f"{REDIS_VERIFY_CODE_PREFIX}{data.email}")

        verify_token: str = await generate_token()
        hashed_token: str = await hash_token(verify_token)

        await redis_client.set(
            name = f"{REDIS_VERIFY_TOKEN_PREFIX}{data.email}",
            value = hashed_token,
            ex = 5 * 60
        )

        return verify_token

    except HTTPException:
        raise

    except Exception as error:
        logger.error(f"Unexpected error in verify_email_service: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def reset_password_service(
    data:   ResetPassword
) -> User:
    
    """Resets the user's password.

    Validates the reset token, updates the user's password with a new
    hashed version, and clears existing sessions.

    Args:
        data: Email, verification token, and new password.

    Returns:
        User: The updated user object.

    Raises:
        HTTPException 404: If user not found.
        HTTPException 403: If token expired or invalid.
        HTTPException 500: If an internal server error occurs.
    """

    try:
        user: User | None = await User.find_one(User.email == data.email)

        if not user:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "User not found"
            )

        saved_token: str | None = await redis_client.get(f"{REDIS_VERIFY_TOKEN_PREFIX}{data.email}")

        if isinstance(saved_token, bytes):
            saved_token = saved_token.decode("utf-8")

        hashed_input_token: str = await hash_token(data.verify_token)

        if not saved_token or saved_token != hashed_input_token:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "Token expired or blacklisted"
            )

        await redis_client.delete(f"{REDIS_VERIFY_TOKEN_PREFIX}{data.email}")
        await redis_client.delete(f"{REDIS_REFRESH_PREFIX}{user.id}")

        new_hashed_password: str = await hash_password(data.new_password)

        await user.set({
            "password": new_hashed_password
        })
        await user.sync()

        return user

    except HTTPException:
        raise

    except Exception as error:
        logger.error(f"Unexpected error in reset_password_service: {error}", exc_info = True)
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )