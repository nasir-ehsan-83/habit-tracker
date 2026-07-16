from datetime import datetime, timezone, timedelta
from typing import Dict
from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import HTTPException, status
from fastapi.concurrency import run_in_threadpool
from app.schemas.token import TokenData
from app.config.config import settings
from app.config.logging_handler import logger



ACCESS_SECRET_KEY = settings.ACCESS_SECRET_KEY
REFRESH_SECRET_KEY = settings.REFRESH_SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS



async def create_access_token(data: Dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    
    return await run_in_threadpool(jwt.encode, to_encode, ACCESS_SECRET_KEY, ALGORITHM)



async def verify_access_token(token: str, credentials_exception):
    try:
        payload = await run_in_threadpool(jwt.decode, token, ACCESS_SECRET_KEY, [ALGORITHM])
        
        if payload.get("type") != "access":
            raise credentials_exception
        
        id = payload.get("id")
        role = payload.get("role")
        
        if not id or not role:
            raise credentials_exception
        
        return TokenData(
            id = id, 
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



async def create_refresh_token(data: Dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days = REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    
    return await run_in_threadpool(jwt.encode, to_encode, REFRESH_SECRET_KEY, ALGORITHM)



async def verify_refresh_token(token: str):
    try:
        payload = await run_in_threadpool(jwt.decode, token, REFRESH_SECRET_KEY, [ALGORITHM])
    
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED, 
                detail = "Invalid refresh token"
            )
    
        return payload
    
    except ExpiredSignatureError:
        logger.warning("Refresh token expired")
        
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED, 
            detail = "Refresh token expired"
        )
    
    except JWTError as error:
        logger.error(f"JWT-Refresh-Token Error: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED, 
            detail = "Invalid refresh token"
        )
    
    except Exception as error:
        logger.error(f"Unexpected Refresh-Token Exception: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail = "Internal server error"
        )
