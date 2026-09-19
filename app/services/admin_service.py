from typing import (
    List, 
    Any, 
    Dict
)
from beanie import BeanieObjectId
from fastapi import (
    HTTPException,
    status
)

from app.utils import paginate
from app.config import logger
from app.models import (
    User, 
    Habit,
    Streak
)
from app.schemas import AppStatsOut




async def get_all_users_service(
    is_active:  bool = False, 
    page:       int = 1, 
    limit:      int = 10
) -> List[User]:
    
    """Retrieves a paginated list of all users with optional active status filtering.

    This administrative function provides access to view all registered users
    with pagination support. Admin access is required to retrieve this data.

    Args:
        is_active: If True, filters users to only those with an "active" status.
            Defaults to False.
        page: The page number for pagination, starting from 1. Defaults to 1.
        limit: The maximum number of users to return per page. Defaults to 10.

    Returns:
        A list of User objects matching the query criteria.

    Raises:
        HTTPException: If an internal server error occurs during database
            operations (status 500).
    """

    try:
        skip, limit_val = paginate(page, limit)
        
        query: Dict[str, Any] = {}

        if is_active:
            query["status"] = "active"

        return await User.find(query).skip(skip).limit(limit_val).to_list()
    
    except Exception as exc:
        logger.error(f"Unexpected error in get_all_users_service: {exc}", exc_info = True)
    
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def get_user_service(
    user_id:    BeanieObjectId
) -> User:
    
    """Retrieves a user by their unique identifier.

    This administrative function fetches a user document from the database
    using the provided ID. Admin access is required to view individual
    user details.

    Args:
        user_id: The MongoDB ObjectId of the user to retrieve.

    Returns:
        The User object corresponding to the provided ID.

    Raises:
        HTTPException: If the user is not found (status 404) or if an
            internal server error occurs (status 500).
    """

    try: 

        user: User | None = await User.get(user_id)

        if not user:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "User not found"
            )
        
        return user
    
    except HTTPException:
        raise
    
    except Exception as exc:
        logger.error(f"Unexpected error in get_user_service: {exc}", exc_info = True)

        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def block_user_service(
    user_id:    BeanieObjectId
) -> User:
    
    """Blocks a user by setting their status to "block".

    This administrative function allows an admin to deactivate a user account
    by updating their status. Blocked users will be unable to access the
    application.

    Args:
        user_id: The MongoDB ObjectId of the user to block.

    Returns:
        The updated User object with the status set to "block".

    Raises:
        HTTPException: If the user is not found (status 404) or if an
            internal server error occurs during the update operation
            (status 500).
    """

    try:
        user: User | None = await User.get(user_id)
        
        if not user:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "User not found"
            )
        
        await user.set({"status": "block"})

        return user
        
    except HTTPException:
        raise
        
    except Exception as exc:
        logger.error(f"Unexpected error in block_user_service: {exc}", exc_info = True)

        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )
    



async def get_all_habits_service(
    owner_id:   BeanieObjectId | None = None, 
    category:   str | None = None,
    page:       int = 1, 
    limit:      int = 10
) -> List[Habit]:
    
    """Retrieves a paginated list of all habits with optional filtering.

    This administrative function provides access to view all habits in the
    system with support for filtering by owner ID and category. Admin access
    is required to view all habits across all users.

    Args:
        owner_id: Optional filter to retrieve habits belonging to a specific
            user. Defaults to None.
        category: Optional filter to retrieve habits of a specific category.
            Defaults to None.
        page: The page number for pagination, starting from 1. Defaults to 1.
        limit: The maximum number of habits to return per page. Defaults to 10.

    Returns:
        A list of Habit objects matching the query criteria, sorted by
        creation date ascending.

    Raises:
        HTTPException: If an internal server error occurs during database
            operations (status 500).
    """

    try:
        skip, limit_val = paginate(page, limit)
        
        query: Dict[str, Any] = {}
        
        if owner_id is not None:
            query["owner_id"] = owner_id
        
        if category:
            query["category"] = category

        return await Habit.find(query).skip(skip).limit(limit_val).sort("+created_at").to_list()
    
    except HTTPException:
        raise
        
    except Exception as error:
        logger.error(f"Unexpected error in get_all_habits_service: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def get_app_stats_service() -> AppStatsOut:

    """Retrieves comprehensive application statistics for administrative dashboard.

    This administrative function aggregates key metrics from the database to
    provide an overview of the application's current state. Admin access is
    required to view these statistics.

    Returns:
        An AppStatsOut object containing the following statistics:
            - total_users: Total number of registered users.
            - active_users: Number of users with an "active" status.
            - total_habits: Total number of habits created.
            - total_streaks: Total number of streaks recorded.

    Raises:
        HTTPException: If an internal server error occurs during database
            aggregation operations (status 500).
    """

    try:

        total_users: int = await User.count()

        active_users: int = await User.find(User.status == "active" ).count()

        total_habits: int = await Habit.count()

        total_streaks: int = await Streak.count()

        return AppStatsOut(
            total_users = total_users,
            active_users = active_users,
            total_habits = total_habits,
            total_streaks = total_streaks
        )
    
    except HTTPException:
        raise
        
    except Exception as exc:
        logger.error(f"Unexpected error in get_app_stats_service: {exc}", exc_info = True)

        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )
    