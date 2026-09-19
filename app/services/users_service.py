from typing import (
    Any,
    Dict,
    List, 
    Tuple
)
from fastapi import (
    HTTPException, 
    status
)
from datetime import (
    datetime, 
    timezone
)
from beanie import BeanieObjectId

from app.core import hash_password
from app.config import logger 
from app.models import (
    User,
    Habit,
    UserPreference
)
from app.schemas import (
    UserUpdate,
    PreferenceUpdate    
)
from app.services.habits_service import get_all_habits_service



async def get_user_service(
    id: BeanieObjectId
) -> User:
    
    """Retrieves a user by their unique identifier.

    This service fetches a user document from the database using the
    provided ID. Only active users (status = "active") are returned.

    Args:
        id: The MongoDB ObjectId of the user to retrieve.

    Returns:
        User: The User object with all user details.

    Raises:
        HTTPException 404: If user is not found or not active.
        HTTPException 500: If an internal server error occurs.
    """
    
    try:

        user: User | None = await User.find_one(
            User.id == BeanieObjectId(id),
            User.status == "active"
        )

        if not user:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND, 
                detail = "User not found"
            )
        
        return user
    
    except HTTPException:
        raise
    
    except Exception as error:
        logger.error(f"Unexpected error in get_user: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def update_user_service(
    id:     BeanieObjectId, 
    data:   UserUpdate
) -> User:
    
    """Updates a user's profile information.

    This service allows users to update their profile details such as
    username, full name, password, or other editable fields.

    Args:
        id: The MongoDB ObjectId of the user to update.
        data: Updated user fields(all optional)

    Returns:
        User: The updated User object with all fields.

    Raises:
        HTTPException 404: If user is not found or not active.
        HTTPException 500: If an internal server error occurs.

    Note:
        Passwords are automatically hashed before storage for security.
    """
    
    try:
        user: User | None = await User.find_one(
            User.id == BeanieObjectId(id),
            User.status == "active"
        )

        if not user:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "User not found"
            )
        
        update_data: Dict[str, Any] = data.model_dump(
            exclude_unset = True, 
            exclude_none = True
        )
        
        if "password" in update_data:
            update_data["password"] = await hash_password(update_data["password"])

        update_data["updated_at"] = datetime.now(timezone.utc)

        await user.set({ 
            **update_data
        })
        
        await user.sync()
        return user
    
    except HTTPException:
        raise
    
    except Exception as error:
        logger.error(f"Unexpected error in update_user: {error}", exc_info = True)
    
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def update_avatar_service(
    id:     BeanieObjectId,
    url:    str
) -> User:
    
    """Updates a user's avatar/profile picture URL.

    This service allows users to change their profile picture by providing
    a new image URL.

    Args:
        id: The MongoDB ObjectId of the user.
        url: The new avatar image URL (must be a valid URL).

    Returns:
        User: The updated User object with new avatar URL.

    Raises:
        HTTPException 404: If user is not found or not active.
        HTTPException 500: If an internal server error occurs.

    Note:
        The URL should point to a valid image resource. No validation
        of the URL format or image availability is performed.
    """

    try:

        user: User | None = await User.find_one(
            User.id == BeanieObjectId(id),
            User.status == "active"
        )

        if not user:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "User not found"
            )
        
        await user.set({
            "vavatar": url
        })
        await user.sync()

        return user

    except HTTPException:
        raise
    
    except Exception as error:
        logger.error(f"Unexpected error in update_avatar: {error}", exc_info = True)
    
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )
    


    
async def get_stats_service(
    id:     BeanieObjectId
) -> Tuple[User, List[Habit]]:
    
    """Retrieves comprehensive user statistics and habit data.

    This service returns both user information and all associated habits,
    providing a complete overview of the user's activity and progress.

    Args:
        id: The MongoDB ObjectId of the user.

    Returns:
        Tuple[User, List[Habit]]

    Raises:
        HTTPException 404: If user is not found or not active.
        HTTPException 500: If an internal server error occurs.

    Note:
        This service uses get_all_habits_service to retrieve habits,
        which includes pagination and filtering capabilities.
    """
    
    try:
        user: User | None = await User.find_one(
            User.id == BeanieObjectId(id),
            User.status == "active"
        )

        if not user:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "User not found"
            )
        
        habits: List[Habit] = await get_all_habits_service(id)

        return user, habits
    

    except HTTPException:
        raise
    
    except Exception as error:
        logger.error(f"Unexpected error in get_stats: {error}", exc_info = True)
    
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def get_preference_service(
    owner_id: BeanieObjectId
) -> UserPreference:
    
    """Retrieves the user's preferences and settings.

    This service returns all user preferences including notification
    settings, theme preferences, and application configurations.

    Args:
        owner_id: The MongoDB ObjectId of the user.

    Returns:
        UserPreference: User preferences

    Raises:
        HTTPException 404: If no preferences are found for the user.
        HTTPException 500: If an internal server error occurs.
    """
    
    try:
        preference: UserPreference | None = await UserPreference.find_one(UserPreference.owner_id == owner_id)

        if not preference:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "User preferences not found"
            )

        return preference

    except HTTPException:
        raise

    except Exception as error:
        logger.error(f"Unexpected error in get_preference: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )
        



async def update_preference_service(
    user_id: BeanieObjectId,
    preference_data: PreferenceUpdate
) -> UserPreference:
    
    """Updates the user's preferences and settings.

    This service allows users to customize their application experience
    by updating preferences.

    Args:
        user_id: The MongoDB ObjectId of the user.
        preference_data: Updated preference fields (all optional)

    Returns:
        UserPreference: The updated user preferences.

    Raises:
        HTTPException 404: If no preferences are found for the user.
        HTTPException 500: If an internal server error occurs.

    Note:
        If preferences don't exist, consider creating them instead of
        raising an exception. This could be implemented as an upsert operation.
    """
    
    try:
        preference: UserPreference | None = await UserPreference.find_one(UserPreference.owner_id == user_id)

        if not preference:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "User preferences not found"
            )

        update_dict: Dict[str, Any] = preference_data.model_dump(exclude_unset = True)

        await preference.set(update_dict)

        return preference

    except HTTPException:
        raise

    except Exception as error:
        logger.error(f"Unexpected error in update_preference: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )