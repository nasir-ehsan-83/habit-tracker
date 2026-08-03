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
    try:
        new_user = User(
            **user.model_dump(exclude={"password"}),
            password = await hash_password(user.password)
        )
        saved_user = await new_user.insert()

        default_preference = UserPreference(owner_id = saved_user.id)
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
    response: Response,
    user_credential: OAuth2PasswordRequestForm
) -> Dict[str, Any]:
    try:
    
        user = await User.find_one(User.username == user_credential.username)

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

        access_token = await create_access_token(user_payload)
        refresh_token = await create_refresh_token(user_payload)

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
            #secure = True,
            #samesite = "lax"
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
    request: Request
) -> Dict[str, Any]:
    try:
    
        refresh_token = request.cookies.get("jwt")

        if not refresh_token:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Refresh token not found"
            )

        payload: Dict[str, Any] = await verify_refresh_token(refresh_token)
        saved_token = await redis_client.get(f"{REDIS_REFRESH_PREFIX}{payload['id']}")

        if isinstance(saved_token, bytes):
            saved_token = saved_token.decode("utf-8")

        if not saved_token or saved_token != refresh_token:
            
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "Token expired or blacklisted"
            )

        new_access_token = await create_access_token({
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
    request: Request
) -> Response:

    refresh_token = request.cookies.get("jwt")
    auth_header = request.headers.get("Authorization")
    response = Response(status_code = status.HTTP_204_NO_CONTENT)

    if refresh_token:
        try:
            payload = await verify_refresh_token(refresh_token)
            await redis_client.delete(f"{REDIS_REFRESH_PREFIX}{payload['id']}")
        
        except Exception:
            pass

    if auth_header and auth_header.startswith("Bearer "):
        try:
            access_token = auth_header.split(" ")[1]
           
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
    request: Request
) -> Response:
    try:
        refresh_token = request.cookies.get("jwt")
        auth_header = request.headers.get("Authorization")
        
        if not refresh_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        payload = await verify_refresh_token(refresh_token)
        user = await User.get(BeanieObjectId(payload["id"]))

        if not user:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "User not found"
            )

        if auth_header and auth_header.startswith("Bearer "):
            access_token = auth_header.split(" ")[1]
           
            await redis_client.set(
                name = f"{REDIS_BLACKLIST_PREFIX}{access_token}",
                value = "revoked",
                ex = 15 * 60
            )

        await redis_client.delete(f"{REDIS_REFRESH_PREFIX}{user.id}")
        await user.delete()

        response = Response(status_code = status.HTTP_204_NO_CONTENT)
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
    email: EmailStr
) -> Dict[str, str]:
    try:
        user = await User.find_one(User.email == email)

        if not user:
            return {
                "message": "Verification code sent successfully"
            }

        verify_code = await generate_code()
        hashed_code = await hash_token(verify_code)

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
    data: VerifyEmail
) -> str:
    try:
        user: User | None = await User.find_one(User.email == data.email)

        if not user:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "User not found"
            )
        
        saved_code = await redis_client.get(f"{REDIS_VERIFY_CODE_PREFIX}{data.email}")

        if isinstance(saved_code, bytes):
            saved_code = saved_code.decode("utf-8")

        hashed_input_code = await hash_token(data.verify_code)

        if not saved_code or saved_code != hashed_input_code:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "Token expired or blacklisted"
            )

        await redis_client.delete(f"{REDIS_VERIFY_CODE_PREFIX}{data.email}")

        verify_token = await generate_token()
        hashed_token = await hash_token(verify_token)

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
    data: ResetPassword
) -> User:
    try:
        user: User | None = await User.find_one(User.email == data.email) 

        if not user:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail =  "User not found"
            )
        
        saved_token = await redis_client.get(f"{REDIS_VERIFY_TOKEN_PREFIX}{data.email}")

        if isinstance(saved_token, bytes):
            saved_token = saved_token.decode("utf-8")

        hashed_input_token = await hash_token(data.verify_token)

        if not saved_token or saved_token != hashed_input_token:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "Token expired or blacklisted"
            )

        await redis_client.delete(f"{REDIS_VERIFY_TOKEN_PREFIX}{data.email}")
        await redis_client.delete(f"{REDIS_REFRESH_PREFIX}{user.id}")

        new_hashed_password = await hash_password(data.new_password)

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
