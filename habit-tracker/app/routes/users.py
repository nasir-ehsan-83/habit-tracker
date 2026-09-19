from typing import (
    Annotated, 
    List, 
    Tuple
)
from fastapi import (
    APIRouter,
    Body, 
    Depends,
)

from app.dependencies import (
    get_current_user,
    required_role
)
from app.models import (
    User, 
    Habit,
    UserPreference
)
from app.schemas import (
    UserPrivateOut,
    UserUpdate,
    TokenData,
    PreferenceOut,
    PreferenceUpdate
)
from app.services.users_service import (
    get_user_service,
    update_avatar_service, 
    update_user_service,
    get_stats_service,
    get_preference_service,
    update_preference_service
)




router = APIRouter(
    prefix = '/api/users',
    tags = ['User'],
    dependencies = [
        Depends(required_role(["ADMIN", "USER"]))
    ]
)




@router.get(
    '/me', 
    response_model = UserPrivateOut,
    summary = "Retrieve current user profile",
    description = "Fetches the complete profile information of the currently authenticated user."
)
async def get_user_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
) -> User:

    """Retrieves the complete profile of the authenticated user.

    This endpoint returns all private user information including email,
    preferences, and account status for the currently logged-in user.

    **Response Codes:**
    - 200: User profile retrieved successfully
    - 401: Unauthorized - Authentication required
    - 403: Forbidden - Insufficient permissions
    - 500: Internal server error

    Args:
        current_user: The authenticated user's token data.

    Returns:
        UserPrivateOut: Complete user profile information

    Raises:
        HTTPException 401: If user is not authenticated.
        HTTPException 403: If user doesn't have required role.
        HTTPException 500: If an internal server error occurs.
    """

    return await get_user_service(current_user.id)




@router.patch(
    '/me', 
    response_model = UserPrivateOut,
    summary = "Update current user profile",
    description = "Updates the profile information of the currently authenticated user."
)
async def update_user_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
    user_data:      Annotated[UserUpdate, Body(description = "Updated user profile fields (all fields optional).")]
) -> User :

    """Updates the authenticated user's profile information.

    This endpoint allows users to update their profile details such as
    username, full name, or other editable fields.

    **Response Codes:**
    - 200: User profile updated successfully
    - 400: Invalid update data
    - 401: Unauthorized - Authentication required
    - 403: Forbidden - Insufficient permissions
    - 500: Internal server error

    Args:
        current_user: The authenticated user's token data.
        user_data: Updated user fields (all optional)

    Returns:
        UserPrivateOut: Updated user profile with all fields.

    Raises:
        HTTPException 400: If update data is invalid.
        HTTPException 401: If user is not authenticated.
        HTTPException 403: If user doesn't have required role.
        HTTPException 500: If an internal server error occurs.
    """

    return await update_user_service(current_user.id, user_data)



@router.patch(
    '/me/avatar',
    response_model = UserPrivateOut,
    summary = "Update user avatar",
    description = "Updates the avatar URL for the currently authenticated user's profile picture."
)
async def update_user_avatar_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
    new_url:        str = Body(..., description = "The new URL for the user's avatar image.", embed = True)
) -> User:
    
    """Updates the user's avatar/profile picture URL.

    This endpoint allows users to change their profile picture by providing
    a new image URL. The URL should point to a valid image resource.

    **Response Codes:**
    - 200: Avatar updated successfully
    - 400: Invalid URL format
    - 401: Unauthorized - Authentication required
    - 403: Forbidden - Insufficient permissions
    - 500: Internal server error

    Args:
        current_user: The authenticated user's token data.
        new_url: The new avatar image URL (must be a valid URL).

    Returns:
        UserPrivateOut: Updated user profile with new avatar URL.

    Raises:
        HTTPException 400: If URL is invalid or malformed.
        HTTPException 401: If user is not authenticated.
        HTTPException 403: If user doesn't have required role.
        HTTPException 500: If an internal server error occurs.
    """

    return await update_avatar_service(current_user.id, new_url)




@router.get(
    '/me/stats',
    response_model = Tuple[User, List[Habit]],
    summary = "Retrieve user statistics",
    description = "Fetches comprehensive statistics including user details and their habit data."
)
async def get_user_stats_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
) -> Tuple[User, List[Habit]]:
    
    """Retrieves comprehensive user statistics and habit data.

    This endpoint returns both user information and all associated habits,
    providing a complete overview of the user's activity and progress.

    **Response Codes:**
    - 200: Statistics retrieved successfully
    - 401: Unauthorized - Authentication required
    - 403: Forbidden - Insufficient permissions
    - 500: Internal server error

    Args:
        current_user: The authenticated user's token data.

    Returns:
        Tuple[User, List[Habit]]

    Raises:
        HTTPException 401: If user is not authenticated.
        HTTPException 403: If user doesn't have required role.
        HTTPException 500: If an internal server error occurs.
    """

    return await get_stats_service(current_user.id)




@router.get(
    '/preference',
    response_model = PreferenceOut,
    summary = "Retrieve user preferences",
    description = "Fetches the current user's preferences and settings."
)
async def get_user_preference_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)]
) -> UserPreference:

    """Retrieves the user's current preferences and settings.

    This endpoint returns all user preferences including  theme preferences, 
    and application configurations.

    **Response Codes:**
    - 200: Preferences retrieved successfully
    - 401: Unauthorized - Authentication required
    - 403: Forbidden - Insufficient permissions
    - 404: Preferences not found (defaults will be returned)
    - 500: Internal server error

    Args:
        current_user: The authenticated user's token data.

    Returns:
        PreferenceOut: User preferences

    Raises:
        HTTPException 401: If user is not authenticated.
        HTTPException 403: If user doesn't have required role.
        HTTPException 500: If an internal server error occurs.
    """

    return await get_preference_service(current_user.id)




@router.put(
    '/preference',
    response_model = PreferenceOut,
    summary = "Create or update user preferences",
    description = "Creates or updates the user's preferences and settings. If preferences don't exist, they will be created."
)
async def create_or_update_user_preference_route(
    current_user:       Annotated[TokenData, Depends(get_current_user)],
    preference_data:    Annotated[PreferenceUpdate, Body(description = "Updated preference settings (all fields optional).")]
) -> UserPreference:

    """Creates or updates the user's preferences.

    This endpoint allows users to customize their application experience
    by updating preferences. If preferences don't exist, they will be
    created with the provided values.

    **Response Codes:**
    - 200: Preferences updated successfully
    - 201: Preferences created successfully
    - 400: Invalid preference data
    - 401: Unauthorized - Authentication required
    - 403: Forbidden - Insufficient permissions
    - 500: Internal server error

    Args:
        current_user: The authenticated user's token data.
        preference_data: Updated preference fields (all optional)

    Returns:
        PreferenceOut: Updated or created user preferences.

    Raises:
        HTTPException 400: If preference data is invalid.
        HTTPException 401: If user is not authenticated.
        HTTPException 403: If user doesn't have required role.
        HTTPException 500: If an internal server error occurs.
    """

    return await update_preference_service(current_user.id, preference_data)