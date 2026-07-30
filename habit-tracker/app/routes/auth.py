from fastapi import (
    APIRouter, 
    Depends, 
    Request, 
    Response,
    Body
)
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from typing import Annotated

from app.schemas.token import Token
from app.models.users import User
from app.schemas.users import (
    UserCreate,
    UserPrivateOut
)
from app.utils.limiter import limiter
from app.services.auth_service import (
    handle_create_user,
    handle_login, 
    handle_refresh_token, 
    handle_logout
)

router = APIRouter(
    prefix = "/api/auth",
    tags = ["Authentication"]
)




@router.post(
    '/register', 
    response_model = UserPrivateOut
)
@limiter.limit('3/minute')
async def create_new_user(
    request: Request, 
    user_in: UserCreate = Body(...)
) -> User:
    
    return await handle_create_user(user_in)




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