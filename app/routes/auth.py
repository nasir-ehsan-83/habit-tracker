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
    status_code = status.HTTP_201_CREATED,
    summary = "Register a new user",
    description = "Creates a new user account with the provided credentials."
)
@limiter.limit('3/minute')
async def create_user_route(
    request:    Request,
    response:   Response,
    user_in:    Annotated[UserCreate, Body(..., description = "User registration data including email, password, ...")]
) -> User:
    
    """Registers a new user account.

    This endpoint handles user registration by validating the provided
    credentials, checking for duplicate emails, and creating a new user
    record in the database. Rate limiting is applied to prevent abuse.

    **Response Codes:**
    - 201: User created successfully
    - 400: Validation error (invalid email, weak password, etc.)
    - 409: Email already registered
    - 429: Too many requests (rate limit exceeded)
    - 500: Internal server error

    Args:
        request: The FastAPI request object.
        response: The FastAPI response object.
        user_in: User registration data containing email, password, and full name.

    Returns:
        User: The created user object with private information.

    Raises:
        HTTPException 400: If validation fails.
        HTTPException 409: If email already exists.
        HTTPException 429: If rate limit exceeded.
        HTTPException 500: If an internal server error occurs.
    """

    return await create_user_service(user_in)




@router.post(
    '/login',
    response_model = Token,
    summary = "Authenticate user",
    description = "Authenticates a user with email and password. Returns JWT access and refresh tokens upon successful authentication."
)
@limiter.limit('5/minute')
async def login_route(
    request:            Request,
    response:           Response,
    user_credential:    Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Dict[str, Any]:
    
    """Authenticates a user and returns access tokens.

    This endpoint validates user credentials and issues JWT access and
    refresh tokens. Tokens are set as HTTP-only cookies for enhanced security.
    Rate limiting is applied to prevent brute force attacks.

    **Response Codes:**
    - 200: Login successful, tokens returned
    - 400: Invalid credentials format
    - 401: Invalid username or password
    - 429: Too many login attempts
    - 500: Internal server error

    Args:
        request: The FastAPI request object.
        response: The FastAPI response object (cookies set here).
        user_credential: User credentials in OAuth2 password flow format.

    Returns:
        Dict[str, Any]: Access and refresh tokens along with token type.

    Raises:
        HTTPException 400: If credentials format is invalid.
        HTTPException 401: If authentication fails.
        HTTPException 429: If rate limit exceeded.
        HTTPException 500: If an internal server error occurs.
    """

    return await login_service(response, user_credential)




@router.get(
    '/refresh',
    response_model = Token,
    summary = "Refresh access token",
    description = "Generates a new access token using a valid refresh token. The refresh token must be present in cookies."
)
@limiter.limit('5/minute')
async def refresh_token_route(
    request:        Request,
    response:       Response,
    current_user:   Annotated[TokenData, Depends(get_current_user)]
) -> Dict[str, Any]:
    
    """Refreshes the access token.

    This endpoint generates a new access token using the refresh token
    stored in cookies. The user must be authenticated with a valid refresh
    token.

    **Response Codes:**
    - 200: New access token generated
    - 401: Invalid or expired refresh token
    - 429: Too many requests
    - 500: Internal server error

    Args:
        request: The FastAPI request object.
        response: The FastAPI response object.
        current_user: The authenticated user's token data.

    Returns:
        Dict[str, Any]: New access token and refresh token.

    Raises:
        HTTPException 401: If refresh token is invalid or expired.
        HTTPException 429: If rate limit exceeded.
        HTTPException 500: If an internal server error occurs.
    """

    return await refresh_token_service(request)




@router.get(
    '/logout',
    status_code = status.HTTP_200_OK,
    summary = "Logout user",
    description = "Logs out the currently authenticated user by clearing authentication cookies and invalidating the session."
)
async def logout_route(
    request:        Request,
    response:       Response,
    current_user:   Annotated[TokenData, Depends(get_current_user)]
):
    
    """Logs out the authenticated user.

    This endpoint clears the authentication cookies and performs any
    necessary session cleanup. The user must be authenticated.

    **Response Codes:**
    - 200: Logout successful
    - 401: User not authenticated
    - 500: Internal server error

    Args:
        request: The FastAPI request object.
        response: The FastAPI response object (cookies cleared here).
        current_user: The authenticated user's token data.

    Returns:
        Dict: Success message indicating logout.

    Raises:
        HTTPException 401: If user is not authenticated.
        HTTPException 500: If an internal server error occurs.
    """

    return await logout_service(request)




@router.delete(
    '/delete-account',
    status_code = status.HTTP_204_NO_CONTENT,
    summary = "Delete user account",
    description = "Permanently deletes the currently authenticated user's account and all associated data."
)
async def delete_account_route(
    request:        Request,
    response:       Response,
    current_user:   Annotated[TokenData, Depends(get_current_user)]
) -> Response:
    
    """Permanently deletes the user's account.

    This endpoint removes the authenticated user's account and all
    associated data from the database. The user must be authenticated.

    **Response Codes:**
    - 204: Account deleted successfully (no content)
    - 401: User not authenticated
    - 404: User not found
    - 500: Internal server error

    Args:
        request: The FastAPI request object.
        response: The FastAPI response object.
        current_user: The authenticated user's token data.

    Raises:
        HTTPException 401: If user is not authenticated.
        HTTPException 404: If user not found.
        HTTPException 500: If an internal server error occurs.
    """

    await delete_account_service(request)
    return Response(status_code = status.HTTP_204_NO_CONTENT)




@router.post(
    '/forget-password',
    response_model = Dict[str, str],
    summary = "Request password reset",
    description = "Sends a password reset link to the user's registered email address."
)
async def forget_password_route(
    email:  Annotated[EmailStr, Body(..., description = "Registered email address of the user")]
) -> Dict[str, str]:
    
    """Initiates the password reset process.

    This endpoint sends a password reset link to the user's email address
    if the email exists in the system. For security, the response is the
    same regardless of whether the email exists.

    **Response Codes:**
    - 200: Reset link sent (if email exists)
    - 400: Invalid email format
    - 500: Internal server error

    Args:
        email: The registered email address of the user.

    Returns:
        Dict[str, str]: Success message indicating the reset link was sent.

    Raises:
        HTTPException 400: If email format is invalid.
        HTTPException 500: If an internal server error occurs.
    """

    return await forget_password_service(email)




@router.post(
    '/verify-email',
    response_model = str,
    summary = "Verify email address",
    description = "Verifies the user's email address using a verification token sent to their email."
)
async def verify_email_route(
    data:   Annotated[VerifyEmail, Body(..., description = "Verification token data")]
) -> str:
    
    """Verifies the user's email address.

    This endpoint validates the email verification token and marks the
    user's email as verified in the database.

    **Response Codes:**
    - 200: Email verified successfully
    - 400: Invalid verification token
    - 404: User not found
    - 500: Internal server error

    Args:
        data: Verification token containing the user's email and verification code.

    Returns:
        str: Success message indicating email was verified.

    Raises:
        HTTPException 400: If verification token is invalid.
        HTTPException 404: If user not found.
        HTTPException 500: If an internal server error occurs.
    """

    return await verify_email_service(data)




@router.post(
    '/reset-password',
    response_model = UserPrivateOut,
    summary = "Reset password",
    description = "Resets the user's password using a valid reset token."
)
async def reset_password_route(
    data:   Annotated[ResetPassword, Body(..., description = "Reset token and new password")]
) -> User:
    
    """Resets the user's password.

    This endpoint validates the reset token and updates the user's password
    if the token is valid and hasn't expired.

    **Response Codes:**
    - 200: Password reset successfully
    - 400: Invalid reset token or weak password
    - 404: User not found
    - 500: Internal server error

    Args:
        data: Reset token and new password.

    Returns:
        User: The updated user object with private information.

    Raises:
        HTTPException 400: If reset token is invalid or password is weak.
        HTTPException 404: If user not found.
        HTTPException 500: If an internal server error occurs.
    """

    return await reset_password_service(data)