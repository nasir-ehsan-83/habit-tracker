from fastapi import (
    APIRouter, 
    Depends, 
    Request, 
    Response,
    Body,
    status
)
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from typing import (
    Annotated, 
    Any, 
    Dict
)

from pydantic import EmailStr

from app.utils import limiter
from app.dependencies import get_current_user 
from app.schemas import (
    UserCreate,
    UserPrivateOut,
    Token, 
    TokenData,
    VerifyEmail,
    ResetPassword
)
from app.models import User
from app.services.auth_service import (
    create_user_service,
    delete_account_service,
    forget_password_service,
    login_service, 
    logout_service,
    refresh_token_service, 
    reset_password_service,
    verify_email_service
)




router = APIRouter(
    prefix = "/api/auth",
    tags = ["Auth"]
)




@router.post(
    '/register', 
    response_model = UserPrivateOut,
    status_code = status.HTTP_201_CREATED
)
@limiter.limit('3/minute')
async def create_user_route(
    request:    Request, 
    response:   Response, 
    user_in:    Annotated[UserCreate, Body(...)]
) -> User:

    return await create_user_service(user_in)




@router.post(
    '/login', 
    response_model = Token
)
@limiter.limit('5/minute')
async def login_route(
    request:            Request, 
    response:           Response, 
    user_credential:    Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Dict[str, Any]:

    return await login_service(response, user_credential)




@router.get(
    '/refresh', 
    response_model = Token
)
@limiter.limit('5/minute')
async def refresh_token_route(
    request:        Request,
    response:       Response,
    current_user:   Annotated[TokenData, Depends(get_current_user)]
) -> Dict[str, Any]:

    return await refresh_token_service(request)


@router.get(
    '/logout',
    status_code = status.HTTP_200_OK
)
async def logout_route(
    request:        Request,
    response:       Response,
    current_user:   Annotated[TokenData, Depends(get_current_user)]
):

    return await logout_service(request)




@router.delete(
    '/delete-account',
    status_code = status.HTTP_204_NO_CONTENT
)
async def delete_account_route(
    request:        Request,
    response:       Response,
    current_user:   Annotated[TokenData, Depends(get_current_user)]
):
    await delete_account_service(request)
    return Response(status_code = status.HTTP_204_NO_CONTENT)



@router.post(
    '/forget-password',
    response_model = Dict[str, str]
)
async def forget_password_route(
    email:  Annotated[EmailStr, Body(...)]
) -> Dict[str, str]:
    
    return await forget_password_service(email)




@router.post(
    '/verify-email',
    response_model = str
)
async def verify_email_route(
    data:   Annotated[VerifyEmail, Body(...)]
) -> str:
    
    return await verify_email_service(data)
