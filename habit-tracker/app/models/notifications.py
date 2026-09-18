from typing import List
from datetime import (
    datetime, 
    timezone
)
from pymongo import (
    ASCENDING, 
    IndexModel
)
from beanie import (
    Document, 
    BeanieObjectId, 
    before_event, 
    Replace, 
    Update
)
from pydantic import Field




class Notification(Document):
    """Notification schedule model for habit reminders."""

    owner_id:       BeanieObjectId  = Field(..., description = "User ID")
    """User who owns this notification."""

    habit_id:       BeanieObjectId  = Field(..., description = "Habit ID")
    """Habit associated with this notification."""

    time:           str             = Field(..., description = "Reminder time in HH:MM format")
    """Time of day to send notification (HH:MM)."""

    days:           List[int]       = Field(default = [0, 1, 2, 3, 4], description = "Days of week (0=Monday to 6=Sunday)")
    """Days of the week for recurring notifications (0=Monday, 6=Sunday)."""

    type:           str             = Field(default = "reminder", description = "Notification type")
    """Type of notification (reminder, summary, test)."""

    next_trigger:   datetime        = Field(..., description = "Next trigger time")
    """Next scheduled trigger timestamp."""

    is_active:      bool            = Field(default = True, description = "Whether schedule is active")
    """Active status of the notification schedule."""

    title:          str | None      = Field(default = None, description = "Notification title")
    """Optional notification title."""

    message:        str | None      = Field(default = None, description = "Notification message")
    """Optional notification message."""

    sent_at:        datetime | None = Field(default = None, description = "Sent timestamp")
    """Timestamp when notification was sent."""

    status:         str             = Field(default = "pending", description = "Delivery status (pending/delivered/failed)")
    """Current delivery status."""

    created_at:     datetime        = Field(default_factory = lambda: datetime.now(timezone.utc))
    """Creation timestamp."""

    updated_at:     datetime        = Field(default_factory = lambda: datetime.now(timezone.utc))
    """Last update timestamp."""

    @before_event([Replace, Update])
    async def update_timestamp(self) -> None:
        """Update updated_at timestamp before save."""
        self.updated_at = datetime.now(timezone.utc)

    class Settings:
        """MongoDB collection configuration."""

        name = "notifications"
        indexes = [
            IndexModel([("owner_id", ASCENDING), ("habit_id", ASCENDING)]),
            IndexModel([("next_trigger", ASCENDING)]),
            IndexModel([("is_active", ASCENDING)]),
            IndexModel([("owner_id", ASCENDING), ("is_active", ASCENDING)])
        ]




class NotificationSettings(Document):
    """User notification preferences."""

    owner_id:           BeanieObjectId      = Field(..., description="User ID")
    """User who owns these settings."""

    push_enabled:       bool                = Field(default = True, description = "Push notifications enabled")
    """Enable push notifications."""

    email_enabled:      bool                = Field(default = False, description = "Email notifications enabled")
    """Enable email notifications."""

    reminder_time:      str | None          = Field(default = None, description = "Default reminder time")
    """Default reminder time (HH:MM)."""

    reminder_days:      List[int] | None    = Field(default = None, description = "Default reminder days")
    """Default days for reminders (0=Monday, 6=Sunday)."""

    created_at:         datetime            = Field(default_factory = lambda: datetime.now(timezone.utc))
    """Creation timestamp."""

    updated_at:         datetime            = Field(default_factory = lambda: datetime.now(timezone.utc))
    """Last update timestamp."""

    @before_event([Replace, Update])
    async def update_timestamp(self) -> None:
        """Update updated_at timestamp before save."""
        self.updated_at = datetime.now(timezone.utc)

    class Settings:
        """MongoDB collection configuration."""

        name = "notification_settings"
        indexes = [
            IndexModel([("owner_id", ASCENDING)], unique = True)
        ]