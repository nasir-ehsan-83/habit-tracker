from fastapi import (
    APIRouter, 
    Depends, 
    Request, 
    Response
)
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from typing import Annotated

from app.schemas.token import Token
from app.utils.limiter import limiter
from app.services.auth_service import (
    handle_login, 
    handle_refresh_token, 
    handle_logout
)

router = APIRouter(
    prefix = "/api/auth",
    tags = ["Authentication"]
)

@router.post(
    '/login', 
    response_model = Token
)
@limiter.limit('5/minute')
async def login(
    request: Request, 
    response: Response, 
    user_credential: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    
    return await handle_login(response, user_credential)




@router.get(
    '/refresh', 
    response_model = Token
)
@limiter.limit('5/minute')
async def refresh(
    request: Request
):
    
    return await handle_refresh_token(request)



@router.get('/logout')
async def logout(
    request: Request
):

    return await handle_logout(request)