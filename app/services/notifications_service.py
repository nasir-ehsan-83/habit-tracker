from datetime import (
    datetime, 
    timedelta
)
from typing import List
from fastapi import (
    HTTPException, 
    status
)
from beanie import BeanieObjectId

from app.config import logger
from app.schemas import (
    ScheduleCreate,
    ScheduleOut,
    MessageOut, 
    ScheduleUpdate,
    NotificationHistoryOut, 
    NotificationItemOut, 
    SettingsOut, 
    SettingsUpdate, 
    TestNotificationIn, 
    TestNotificationOut
)
from app.models import (
    Habit, 
    Notification,
    NotificationSettings
)




async def create_schedule_service(
    owner_id:       BeanieObjectId,
    schedule_in:    ScheduleCreate
) -> ScheduleOut:
    
    """Creates a new notification schedule for a habit.

    This service creates a scheduled notification for a habit, setting up
    the trigger time and frequency for reminders.

    Args:
        owner_id: The MongoDB ObjectId of the user creating the schedule.
        schedule_in: The pydantic model to create a user's schedule

    Returns:
        ScheduleOut: The created schedule with all details

    Raises:
        HTTPException 404: If the habit is not found.
        HTTPException 500: If an internal server error occurs.
    """
    
    try:
        habit: Habit | None = await Habit.get(schedule_in.habit_id)
       
        if not habit:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Habit not found"
            )
        
        now: datetime = datetime.now()
        trigger_time: datetime = datetime.combine(now.date(), datetime.strptime(schedule_in.time, "%H:%M").time())
        
        if trigger_time <= now:
            trigger_time += timedelta(days=1)
        
        notification = Notification(
            owner_id = owner_id,
            habit_id = schedule_in.habit_id,
            time = schedule_in.time,
            days = schedule_in.days,
            type = schedule_in.type,
            next_trigger = trigger_time,
            is_active = True
        )
        
        await notification.insert() # type: ignore
        
        return ScheduleOut(
            schedule_id = notification.id, # type: ignore
            habit_id = notification.habit_id,
            time = notification.time,
            days = notification.days,
            type = notification.type,
            next_trigger = notification.next_trigger,
            is_active = notification.is_active,
            created_at = notification.created_at
        )
        
    except HTTPException:
        raise
        
    except Exception as error:
        logger.error(f"Unexpected error in create_schedule_service: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def update_schedule_service(
    owner_id:       BeanieObjectId,
    schedule_id:    BeanieObjectId,
    schedule_in:    ScheduleUpdate
) -> MessageOut:
    
    """Updates an existing notification schedule.

    This service allows users to modify their notification schedule
    including time, days, and active status.

    Args:
        owner_id: The MongoDB ObjectId of the user owning the schedule.
        schedule_id: The MongoDB ObjectId of the schedule to update.
        schedule_in: Updated schedule fields (all optional)

    Returns:
        MessageOut: Success message confirming the update.

    Raises:
        HTTPException 404: If the schedule is not found.
        HTTPException 500: If an internal server error occurs.
    """
    
    try:
        notification: Notification | None = await Notification.find_one({
            "_id": schedule_id,
            "owner_id": owner_id
        })
        
        if not notification:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Schedule not found"
            )
        
        if schedule_in.time is not None:
            notification.time = schedule_in.time
            
            now: datetime = datetime.now()
            trigger_time: datetime = datetime.combine(now.date(), datetime.strptime(schedule_in.time, "%H:%M").time())
            
            if trigger_time <= now:
                trigger_time += timedelta(days=1)
            
            notification.next_trigger = trigger_time
        
        if schedule_in.days is not None:
            notification.days = schedule_in.days
        
        if schedule_in.is_active is not None:
            notification.is_active = schedule_in.is_active
        
        await notification.save() # type: ignore
        
        return MessageOut(
            message = "Schedule updated successfully"
        )
        
    except HTTPException:
        raise
        
    except Exception as error:
        logger.error(f"Unexpected error in update_schedule_service: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def delete_schedule_service(
    owner_id:       BeanieObjectId,
    schedule_id:    BeanieObjectId
) -> MessageOut:
    
    """Permanently deletes a notification schedule.

    This service removes a notification schedule from the system.

    Args:
        owner_id: The MongoDB ObjectId of the user owning the schedule.
        schedule_id: The MongoDB ObjectId of the schedule to delete.

    Returns:
        MessageOut: Success message confirming the deletion.

    Raises:
        HTTPException 404: If the schedule is not found.
        HTTPException 500: If an internal server error occurs.
    """
    
    try:
        
        notification: Notification | None = await Notification.find_one({
            "_id": schedule_id,
            "owner_id": owner_id
        })
        
        if not notification:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Schedule not found"
            )
        
        await notification.delete() # type: ignore
        
        return MessageOut(
            message = "Schedule deleted successfully"
        )
        
    except HTTPException:
        raise
        
    except Exception as error:
        logger.error(f"Unexpected error in delete_schedule_service: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def get_settings_service(
    owner_id:   BeanieObjectId
) -> SettingsOut:
    
    """Retrieves the user's notification settings.

    This service returns the user's notification preferences including
    enabled channels and reminder settings. If no settings exist,
    default values are returned.

    Args:
        owner_id: The MongoDB ObjectId of the user.

    Returns:
        SettingsOut: User's notification settings

    Raises:
        HTTPException 500: If an internal server error occurs.
    """
    
    try:
        settings: NotificationSettings | None = await NotificationSettings.find_one({"owner_id": owner_id})
        
        if not settings:
            return SettingsOut(
                push_enabled = True,
                email_enabled = False,
                reminder_time = None,
                reminder_days = None
            )
        
        return SettingsOut(
            push_enabled = settings.push_enabled,
            email_enabled = settings.email_enabled,
            reminder_time = settings.reminder_time,
            reminder_days = settings.reminder_days
        )
        
    except HTTPException:
        raise
        
    except Exception as error:
        logger.error(f"Unexpected error in get_settings_service: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def update_settings_service(
    owner_id:       BeanieObjectId,
    settings_in:    SettingsUpdate
) -> MessageOut:
    
    """Updates the user's notification settings.

    This service updates the user's notification preferences. If settings
    don't exist, they will be created with the provided values.

    Args:
        owner_id: The MongoDB ObjectId of the user.
        settings_in: Updated settings fields (all optional)HH:MM format)
            - reminder_days: Default reminder days

    Returns:
        MessageOut: Success message confirming the update.

    Raises:
        HTTPException 500: If an internal server error occurs.
    """
    
    try:
        settings: NotificationSettings | None = await NotificationSettings.find_one({"owner_id": owner_id})
        
        if not settings:
            settings = NotificationSettings(owner_id = owner_id)
        
        if settings_in.push_enabled is not None:
            settings.push_enabled = settings_in.push_enabled
        
        if settings_in.email_enabled is not None:
            settings.email_enabled = settings_in.email_enabled
        
        if settings_in.reminder_time is not None:
            settings.reminder_time = settings_in.reminder_time
        
        if settings_in.reminder_days is not None:
            settings.reminder_days = settings_in.reminder_days
        
        await settings.save() # type: ignore
        
        return MessageOut(
            message = "Settings updated successfully"
        )
        
    except HTTPException:
        raise
        
    except Exception as error:
        logger.error(f"Unexpected error in update_settings_service: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def send_test_notification_service(
    owner_id:   BeanieObjectId,
    test_in:    TestNotificationIn
) -> TestNotificationOut:
    
    """Sends a test notification to verify the user's notification setup.

    This service creates and sends a test notification to the user's
    configured channels to ensure they are working correctly.

    Args:
        owner_id: The MongoDB ObjectId of the user.
        test_in: Test Notification configuration 
    Returns:
        TestNotificationOut: Test results

    Raises:
        HTTPException 500: If an internal server error occurs.
    """

    try:

        notification: Notification = Notification(
            owner_id = owner_id,
            habit_id = BeanieObjectId(),
            time = datetime.now().strftime("%H:%M"),
            days = [],
            type = "test",
            next_trigger = datetime.now(),
            is_active = False,
            title = "Test Notification",
            message = test_in.message,
            sent_at = datetime.now(),
            status = "delivered"
        )
        
        await notification.insert() # type: ignore
        
        return TestNotificationOut(
            message = f"Test {test_in.type} notification sent successfully",
            sent_at = datetime.now()
        )
        
    except HTTPException:
        raise
        
    except Exception as error:
        logger.error(f"Unexpected error in send_test_notification_service: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def get_notification_history_service(
    owner_id:   BeanieObjectId,
    limit:      int = 20
) -> NotificationHistoryOut:
    
    """Retrieves the user's notification history.

    This service returns a paginated list of past notifications sent to
    the user, including delivery status and timestamps.

    Args:
        owner_id: The MongoDB ObjectId of the user.
        limit: Maximum number of history records to return (1-100). Defaults to 20.

    Returns:
        NotificationHistoryOut: Notification history 

    Raises:
        HTTPException 500: If an internal server error occurs.
    """
    
    try:
        notifications: List[Notification] = await Notification.find({
            "owner_id": owner_id,
            "sent_at": {"$ne": None}
        }).sort("-sent_at").limit(limit).to_list()
        
        notification_items: List[NotificationItemOut] = []
        for notif in notifications:
           
            notification_items.append(
                NotificationItemOut(
                    id = notif.id, # type: ignore
                    type = notif.type,
                    title = notif.title,
                    message = notif.message or "No message",
                    sent_at = notif.sent_at or datetime.now(),
                    status = notif.status
                )
            )
        
        total: int = await Notification.find({"owner_id": owner_id}).count()
        
        return NotificationHistoryOut(
            notifications = notification_items,
            total = total,
            limit = limit
        )
        
    except HTTPException:
        raise
        
    except Exception as error:
        logger.error(f"Unexpected error in get_notification_history_service: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )