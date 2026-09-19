from typing import (
    Annotated, 
    List
)
from beanie import BeanieObjectId
from fastapi import (
    APIRouter, 
    Depends, 
    Path, 
    Query
)

from app.dependencies import (
    get_current_user, 
    required_role
)
from app.schemas import (
    UserAdminOut, 
    HabitAdminOut,
    AppStatsOut
)
from app.services.admin_service import (
    block_user_service,
    get_all_habits_service, 
    get_all_users_service, 
    get_user_service,
    get_app_stats_service
)
from app.models import (
    User,
    Habit
)
from app.utils.enum import HabitCategory




router: APIRouter = APIRouter(
    prefix = '/api/admin',
    tags = ["Admin"],
    dependencies = [
        Depends(get_current_user),
        Depends(required_role(["ADMIN"]))
    ]
)




@router.get(
    '/users',
    response_model = List[UserAdminOut],
    summary = "Retrieve all users",
    description = "Fetches a paginated list of all registered users with optional filtering by active status. Accessible only to administrators."
)
async def get_all_users_route(
    is_active:  Annotated[bool, Query(description = "Filter users by active status. If True, returns only active users.")] = True,
    page:       Annotated[int, Query(ge = 1, le = 100, description = "Page number for pagination (1-100).")] = 1,
    limit:      Annotated[int, Query(ge = 1, le = 100, description = "Number of users per page (1-100).")] = 10
) -> List[User]:
    
    """Retrieves a paginated list of all users with optional active status filtering.

    This endpoint provides administrative access to view all registered users
    in the system. Results can be filtered by active status and paginated
    for efficient data retrieval.

    **Response Codes:**
    - 200: Users retrieved successfully
    - 401: Unauthorized - Authentication required
    - 403: Forbidden - Admin privileges required
    - 500: Internal server error

    Args:
        is_active: Filter to include only active users. Defaults to True.
        page: Page number for pagination (starts from 1). Defaults to 1.
        limit: Maximum number of users to return per page. Defaults to 10.

    Returns:
        List[User]: A list of User objects matching the query criteria.

    Raises:
        HTTPException 401: If user is not authenticated.
        HTTPException 403: If user does not have admin role.
        HTTPException 500: If an internal server error occurs.
    """

    return await get_all_users_service(is_active, page, limit)





@router.get(
    '/users/{user_id}',
    response_model = UserAdminOut,
    summary = "Retrieve user by ID",
    description = "Fetches detailed information about a specific user by their unique identifier. Accessible only to administrators."
)
async def get_user_route(
    user_id:    Annotated[BeanieObjectId, Path(description = "The unique MongoDB ObjectId of the user to retrieve.")]
) -> User:
    
    """Retrieves detailed information about a specific user by their ID.

    This endpoint allows administrators to view all details of any user
    in the system using their unique MongoDB ObjectId.

    **Response Codes:**
    - 200: User found and returned successfully
    - 401: Unauthorized - Authentication required
    - 403: Forbidden - Admin privileges required
    - 404: User not found with the provided ID
    - 500: Internal server error

    Args:
        user_id: The MongoDB ObjectId of the user to retrieve (path parameter).

    Returns:
        User: The User object with all user details.

    Raises:
        HTTPException 401: If user is not authenticated.
        HTTPException 403: If user does not have admin role.
        HTTPException 404: If no user exists with the given ID.
        HTTPException 500: If an internal server error occurs.
    """

    return await get_user_service(user_id)




@router.patch(
    '/users/{user_id}/ban',
    response_model = UserAdminOut,
    summary = "Block a user",
    description = "Blocks a user account by setting their status to 'block'. Blocked users cannot access the application. Accessible only to administrators."
)
async def user_ban_route(
    user_id:    Annotated[BeanieObjectId, Path(description = "The unique MongoDB ObjectId of the user to block.")]
) -> User:
    
    """Blocks a user account by updating their status to "block".

    This administrative endpoint allows admins to deactivate a user's account,
    preventing them from accessing the application and its features. The user's
    status is updated to "block" in the database.

    **Response Codes:**
    - 200: User blocked successfully
    - 401: Unauthorized - Authentication required
    - 403: Forbidden - Admin privileges required
    - 404: User not found with the provided ID
    - 500: Internal server error

    Args:
        user_id: The MongoDB ObjectId of the user to block (path parameter).

    Returns:
        User: The updated User object with status set to "block".

    Raises:
        HTTPException 401: If user is not authenticated.
        HTTPException 403: If user does not have admin role.
        HTTPException 404: If no user exists with the given ID.
        HTTPException 500: If an internal server error occurs.
    """

    return await block_user_service(user_id)




@router.get(
    '/habits',
    response_model = List[HabitAdminOut],
    summary = "Retrieve all habits",
    description = "Fetches a paginated list of all habits with optional filtering by owner ID and category. Accessible only to administrators."
)
async def get_all_habits_route(
    owner_id:   Annotated[BeanieObjectId | None, Query(description =  "Filter habits by owner's user ID. If not provided, returns habits from all users.")] = None,
    category:   Annotated[HabitCategory | None, Query(description = "Filter habits by category (e.g., HEALTH, SPORT, STUDY).")] = None,
    page:       Annotated[int, Query(ge = 1, description = "Page number for pagination (starts from 1).")] = 1,
    limit:      Annotated[int, Query(ge = 1, description = "Number of habits per page.")] = 10,
) -> List[Habit]:
    
    """Retrieves a paginated list of all habits with optional filtering.

    This administrative endpoint provides access to view all habits in the
    system. Results can be filtered by owner ID, category, and paginated
    for efficient data retrieval. Habits are sorted by creation date ascending.

    **Response Codes:**
    - 200: Habits retrieved successfully
    - 401: Unauthorized - Authentication required
    - 403: Forbidden - Admin privileges required
    - 500: Internal server error

    Args:
        owner_id: Optional filter to retrieve habits belonging to a specific user.
        category: Optional filter to retrieve habits of a specific category.
        page: Page number for pagination (starts from 1). Defaults to 1.
        limit: Maximum number of habits to return per page. Defaults to 10.

    Returns:
        List[Habit]: A list of Habit objects matching the query criteria,
            sorted by creation date ascending.

    Raises:
        HTTPException 401: If user is not authenticated.
        HTTPException 403: If user does not have admin role.
        HTTPException 500: If an internal server error occurs.
    """

    return await get_all_habits_service(owner_id, category, page, limit)





@router.get(
    '/stats',
    response_model = AppStatsOut,
    summary = "Retrieve application statistics",
    description = "Retrieves comprehensive application statistics including user counts, habit totals, and streak information for the admin dashboard. Accessible only to administrators."
)
async def get_app_stats_route() -> AppStatsOut:
    """Retrieves comprehensive application statistics for the admin dashboard.

    This endpoint aggregates key metrics from the database to provide an
    overview of the application's current state, including total users,
    active users, habits, and streaks.

    **Response Codes:**
    - 200: Statistics retrieved successfully
    - 401: Unauthorized - Authentication required
    - 403: Forbidden - Admin privileges required
    - 500: Internal server error

    Returns:
        AppStatsOut: Application statistics containing:
            - total_users: Total number of registered users
            - active_users: Number of users with "active" status
            - total_habits: Total number of habits created
            - total_streaks: Total number of streaks recorded

    Raises:
        HTTPException 401: If user is not authenticated.
        HTTPException 403: If user does not have admin role.
        HTTPException 500: If an internal server error occurs.
    """
    return await get_app_stats_service()