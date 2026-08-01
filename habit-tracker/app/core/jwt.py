from typing import (
    Any, 
    Dict
)
from fastapi import (
    HTTPException, 
    status
)
from beanie import BeanieObjectId
from fastapi.concurrency import run_in_threadpool
from datetime import (
    datetime, 
    timezone, 
    timedelta
)
from jose import (
    jwt, 
    JWTError, 
    ExpiredSignatureError
)

from app.schemas import TokenData
from app.config import (
    settings,
    logger
)



ACCESS_SECRET_KEY:  str = settings.ACCESS_SECRET_KEY
REFRESH_SECRET_KEY: str = settings.REFRESH_SECRET_KEY

ALGORITHM:  str = settings.ALGORITHM

ACCESS_TOKEN_EXPIRE_MINUTES:    int = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS:      int = settings.REFRESH_TOKEN_EXPIRE_DAYS




async def create_access_token(
    data: Dict[str, str | int | datetime]
) -> str:

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire, 
        "type": "access"
    })
    
    return await run_in_threadpool(
        jwt.encode, 
        to_encode, 
        ACCESS_SECRET_KEY, ALGORITHM
    )




async def verify_access_token(
    token: str, 
    credentials_exception: HTTPException
) -> TokenData:

    try:
        payload: Dict[str, Any] = await run_in_threadpool(
            jwt.decode, 
            token, 
            ACCESS_SECRET_KEY, 
            [ALGORITHM]
        )
        
        if payload.get("type") != "access":
            raise credentials_exception
        
        id:     BeanieObjectId | None = payload.get("id")
        role:   str | None = payload.get("role")
        
        if not id or not role:
            raise credentials_exception
        
        return TokenData(
            id  = id, 
            role = role
        )
    
    except ExpiredSignatureError:
        logger.warning("Access token expired")
        
        raise credentials_exception
    
    except JWTError as error:
        logger.error(f"JWT-Access-Token Error: {error}", exc_info = True)
        
        raise credentials_exception
    
    except Exception as error:
        logger.error(f"Unexpected Access Token Exception: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail = "Internal server error"
        )




async def create_refresh_token(
    data: Dict[str, str | int | datetime]
) -> str:

    to_encode:  Dict[str, str | int | datetime] = data.copy()
    expire:     datetime = datetime.now(timezone.utc) + timedelta(days = REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire, 
        "type": "refresh"
    })
    
    return await run_in_threadpool(
        jwt.encode, 
        to_encode, 
        REFRESH_SECRET_KEY, 
        ALGORITHM
    )



async def verify_refresh_token(
    token: str,
    credentials_exception: HTTPException = HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Invalid refresh token")
) -> Dict[str, Any]:
    
    try:
        payload: Dict[str, Any] = await run_in_threadpool(
            jwt.decode, 
            token, 
            REFRESH_SECRET_KEY, 
            [ALGORITHM]
        )
    
        if payload.get("type") != "refresh":
            raise credentials_exception
    
        return payload
    
    except ExpiredSignatureError:
        logger.warning("Refresh token expired")
        
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED, 
            detail = "Refresh token expired"
        )
    
    except JWTError as error:
        logger.error(f"JWT-Refresh-Token Error: {error}", exc_info = True)
        
        raise credentials_exception
    
    except Exception as error:
        logger.error(f"Unexpected Refresh-Token Exception: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail = "Internal server error"
        )
