from typing import Annotated
from beanie import BeanieObjectId
from fastapi import (
    APIRouter, 
    Depends,
    Body,
    Path,
    Query
)

from app.dependencies import get_current_user
from app.schemas import (
    ScheduleCreate,
    ScheduleOut,
    TokenData,
    MessageOut,
    ScheduleUpdate,
    SettingsOut,
    SettingsUpdate,
    TestNotificationIn, 
    TestNotificationOut,
    NotificationHistoryOut
)
from app.services.notifications_service import (
    create_schedule_service,
    update_schedule_service,
    delete_schedule_service,
    get_settings_service,
    update_settings_service,
    send_test_notification_service,
    get_notification_history_service
)




router: APIRouter = APIRouter(
    prefix = '/api/notifications',
    tags = ["Notifications"],
    dependencies = [
        Depends(get_current_user)
    ]
)




@router.post(
    '/schedule',
    response_model = ScheduleOut,
    status_code = 201,
    summary = "Create notification schedule",
    description = "Creates a new notification schedule for the authenticated user with specified time, frequency, and ..."
)
async def create_schedule_route(
    current_user:       Annotated[TokenData, Depends(get_current_user)],
    schedule_in:        Annotated[ScheduleCreate, Body(description = "Schedule configuration details including time, frequency, and notification preferences.")]
) -> ScheduleOut:
    
    """Creates a new notification schedule for the authenticated user.

    This endpoint allows users to set up scheduled notifications for their
    habits, including daily reminders, weekly summaries, or custom schedules.

    **Response Codes:**
    - 201: Schedule created successfully
    - 400: Invalid schedule configuration
    - 401: Unauthorized - Authentication required
    - 500: Internal server error

    Args:
        current_user: The authenticated user's token data.
        schedule_in: Schedule configuration 

    Returns:
        ScheduleOut: The created schedule with all details 
    Raises:
        HTTPException 400: If schedule configuration is invalid.
        HTTPException 401: If user is not authenticated.
        HTTPException 500: If an internal server error occurs.
    """

    return await create_schedule_service(current_user.id, schedule_in)




@router.put(
    '/schedule/{schedule_id}',
    response_model = MessageOut,
    summary = "Update notification schedule",
    description = "Updates an existing notification schedule with new configuration parameters."
)
async def update_schedule_route(
    current_user:       Annotated[TokenData, Depends(get_current_user)],
    schedule_id:        Annotated[BeanieObjectId, Path(description = "The MongoDB ObjectId of the schedule to update.")],
    schedule_in:        Annotated[ScheduleUpdate, Body(description = "Updated schedule configuration fields.")]
) -> MessageOut:
    
    """Updates an existing notification schedule.

    This endpoint allows users to modify their notification schedules,
    including time, frequency, or enable/disable status.

    **Response Codes:**
    - 200: Schedule updated successfully
    - 400: Invalid update configuration
    - 401: Unauthorized - Authentication required
    - 403: Forbidden - User doesn't own this schedule
    - 404: Schedule not found
    - 500: Internal server error

    Args:
        current_user: The authenticated user's token data.
        schedule_id: The MongoDB ObjectId of the schedule to update.
        schedule_in: Updated schedule fields (all fields optional)

    Returns:
        MessageOut: Success message confirming the update.

    Raises:
        HTTPException 400: If update configuration is invalid.
        HTTPException 401: If user is not authenticated.
        HTTPException 403: If user doesn't own the schedule.
        HTTPException 404: If schedule doesn't exist.
        HTTPException 500: If an internal server error occurs.
    """

    return await update_schedule_service(current_user.id, schedule_id, schedule_in)




@router.delete(
    '/schedule/{schedule_id}',
    response_model = MessageOut,
    summary = "Delete notification schedule",
    description = "Permanently deletes an existing notification schedule by its unique identifier."
)
async def delete_schedule_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
    schedule_id:    Annotated[BeanieObjectId, Path(description = "The MongoDB ObjectId of the schedule to delete.")]
) -> MessageOut:
    
    """Permanently deletes a notification schedule.

    This endpoint removes a notification schedule from the system.
    This action cannot be undone.

    **Response Codes:**
    - 200: Schedule deleted successfully
    - 401: Unauthorized - Authentication required
    - 403: Forbidden - User doesn't own this schedule
    - 404: Schedule not found
    - 500: Internal server error

    Args:
        current_user: The authenticated user's token data.
        schedule_id: The MongoDB ObjectId of the schedule to delete.

    Returns:
        MessageOut: Success message confirming deletion.

    Raises:
        HTTPException 401: If user is not authenticated.
        HTTPException 403: If user doesn't own the schedule.
        HTTPException 404: If schedule doesn't exist.
        HTTPException 500: If an internal server error occurs.
    """

    return await delete_schedule_service(current_user.id, schedule_id)




@router.get(
    '/settings',
    response_model = SettingsOut,
    summary = "Retrieve notification settings",
    description = "Fetches the current notification settings and preferences for the authenticated user."
)
async def get_settings_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)]
) -> SettingsOut:
    
    """Retrieves the user's current notification settings.

    This endpoint returns all notification preferences including channels,
    quiet hours, and enabled notification types.

    **Response Codes:**
    - 200: Settings retrieved successfully
    - 401: Unauthorized - Authentication required
    - 404: Settings not found (defaults will be returned)
    - 500: Internal server error

    Args:
        current_user: The authenticated user's token data.

    Returns:
        SettingsOut: User's notification settings

    Raises:
        HTTPException 401: If user is not authenticated.
        HTTPException 500: If an internal server error occurs.
    """

    return await get_settings_service(current_user.id)




@router.put(
    '/settings',
    response_model = MessageOut,
    summary = "Update notification settings",
    description = "Updates the user's notification settings and preferences."
)
async def update_settings_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
    settings_in:    Annotated[SettingsUpdate, Body(description = "Updated notification settings fields.")]
) -> MessageOut:
    
    """Updates the user's notification settings.

    This endpoint allows users to customize their notification preferences
    including channels, quiet hours, and notification types.

    **Response Codes:**
    - 200: Settings updated successfully
    - 400: Invalid settings configuration
    - 401: Unauthorized - Authentication required
    - 500: Internal server error

    Args:
        current_user: The authenticated user's token data.
        settings_in: Updated settings fields (all optional)

    Returns:
        MessageOut: Success message confirming the update.

    Raises:
        HTTPException 400: If settings configuration is invalid.
        HTTPException 401: If user is not authenticated.
        HTTPException 500: If an internal server error occurs.
    """

    return await update_settings_service(current_user.id, settings_in)




@router.post(
    '/test',
    response_model = TestNotificationOut,
    summary = "Send test notification",
    description = "Sends a test notification to the user's configured channels to verify delivery."
)
async def send_test_notification_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
    test_in:        Annotated[TestNotificationIn, Body(description = "Test notification configuration including channel and message.")]
) -> TestNotificationOut:
    
    """Sends a test notification to verify user's notification setup.

    This endpoint allows users to test their notification channels
    (email, push, etc.) to ensure they are working correctly.

    **Response Codes:**
    - 200: Test notification sent successfully
    - 400: Invalid test configuration
    - 401: Unauthorized - Authentication required
    - 500: Internal server error

    Args:
        current_user: The authenticated user's token data.
        test_in: Test configuration
    Returns:
        TestNotificationOut: Test results 

    Raises:
        HTTPException 400: If test configuration is invalid.
        HTTPException 401: If user is not authenticated.
        HTTPException 500: If an internal server error occurs.
    """

    return await send_test_notification_service(current_user.id, test_in)




@router.get(
    '/history',
    response_model = NotificationHistoryOut,
    summary = "Retrieve notification history",
    description = "Fetches the user's notification history with pagination support."
)
async def get_notification_history_route(
    current_user:   Annotated[TokenData, Depends(get_current_user)],
    limit:          Annotated[int, Query(ge = 1, le = 100, description = "Maximum number of history records to return (1-100). Defaults to 20.")] = 20
) -> NotificationHistoryOut:
    
    """Retrieves the user's notification history.

    This endpoint returns a paginated list of past notifications sent to the user,
    including delivery status and timestamps.

    **Response Codes:**
    - 200: History retrieved successfully
    - 401: Unauthorized - Authentication required
    - 500: Internal server error

    Args:
        current_user: The authenticated user's token data.
        limit: Maximum number of history records to return (1-100). Defaults to 20.

    Returns:
        NotificationHistoryOut: Notification historys

    Raises:
        HTTPException 401: If user is not authenticated.
        HTTPException 500: If an internal server error occurs.
    """

    return await get_notification_history_service(current_user.id, limit)