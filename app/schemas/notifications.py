from datetime import datetime
from typing import List
from pydantic import (
    BaseModel, 
    Field, 
    field_validator
)
from beanie import BeanieObjectId




class ScheduleCreate(BaseModel):
    """Request model for creating a notification schedule."""

    habit_id:   BeanieObjectId  = Field(..., description = "Habit ID to set reminder for")
    """Habit to associate with this schedule."""

    time:       str             = Field(..., description = "Reminder time in HH:MM format", pattern = r"^([01]\d|2[0-3]):([0-5]\d)$")
    """Reminder time (HH:MM format)."""

    days:       List[int]       = Field(..., description = "Days of week (0=Monday to 6=Sunday)", min_length = 1, max_length = 7)
    """Days of week (0=Monday, 6=Sunday)."""

    type:       str             = Field(default = "reminder", description = "Notification type")
    """Notification type (reminder, summary, etc.)."""

    @field_validator('days')
    @classmethod
    def validate_days(cls, v: List[int]) -> List[int]:
        """Validate and deduplicate days."""
        for day in v:
            if not 0 <= day <= 6:
                raise ValueError('Days must be between 0 (Monday) and 6 (Sunday)')

        return sorted(set(v))



class ScheduleOut(BaseModel):
    """Response model for notification schedule."""

    schedule_id:    BeanieObjectId  = Field(..., description = "Schedule ID")
    """Unique schedule identifier."""

    habit_id:       BeanieObjectId  = Field(..., description = "Habit ID")
    """Associated habit ID."""

    time:           str             = Field(..., description = "Reminder time")
    """Reminder time (HH:MM)."""

    days:           List[int]       = Field(..., description = "Days of week")
    """Days of week (0=Monday, 6=Sunday)."""

    type:           str             = Field(..., description = "Notification type")
    """Notification type."""

    next_trigger:   datetime        = Field(..., description = "Next trigger time")
    """Next scheduled trigger timestamp."""

    is_active:      bool            = Field(default = True, description = "Whether schedule is active")
    """Active status."""

    created_at:     datetime        = Field(..., description = "Creation timestamp")
    """Creation timestamp."""


class ScheduleUpdate(BaseModel):
    """Request model for updating a notification schedule."""

    time:       str | None          = Field(default = None, description = "New reminder time", pattern = r"^([01]\d|2[0-3]):([0-5]\d)$")
    """Updated reminder time (HH:MM)."""

    days:       List[int] | None    = Field(default = None, description = "New days of week")
    """Updated days of week."""

    is_active:  bool | None         = Field(default = None, description = "Activate or deactivate schedule")
    """Updated active status."""

    @field_validator('days')
    @classmethod
    def validate_days(cls, v: List[int] | None) -> List[int] | None:
        """Validate and deduplicate days."""
        if v is not None:
            for day in v:
                if not 0 <= day <= 6:
                    raise ValueError('Days must be between 0 (Monday) and 6 (Sunday)')
            return sorted(set(v))
        return v


class SettingsOut(BaseModel):
    """Response model for notification settings."""

    push_enabled:       bool                = Field(default = True, description = "Push notifications enabled")
    """Enable push notifications."""

    email_enabled:      bool                = Field(default = False, description = "Email notifications enabled")
    """Enable email notifications."""

    reminder_time:      str | None          = Field(default = None, description = "Default reminder time", pattern = r"^([01]\d|2[0-3]):([0-5]\d)$")
    """Default reminder time (HH:MM)."""

    reminder_days:      List[int] | None    = Field(default = None, description = "Default reminder days")
    """Default days for reminders."""


class SettingsUpdate(BaseModel):
    """Request model for updating notification settings."""

    push_enabled:       bool | None         = Field(default = None, description = "Enable push notifications")
    """Updated push notification setting."""

    email_enabled:      bool | None         = Field(default = None, description = "Enable email notifications")
    """Updated email notification setting."""

    reminder_time:      str | None          = Field(default = None, description = "Default reminder time", pattern = r"^([01]\d|2[0-3]):([0-5]\d)$")
    """Updated default reminder time."""

    reminder_days:      List[int] | None    = Field(default = None, description = "Default reminder days")
    """Updated default reminder days."""

    @field_validator('reminder_days')
    @classmethod
    def validate_days(cls, v: List[int] | None) -> List[int] | None:
        """Validate and deduplicate days."""
        if v is not None:
            for day in v:
                if not 0 <= day <= 6:
                    raise ValueError('Days must be between 0 (Monday) and 6 (Sunday)')
            return sorted(set(v))
        return v


class TestNotificationIn(BaseModel):
    """Request model for sending test notification."""

    type:       str = Field(..., description = "Notification type (push/email)")
    """Notification type to test."""

    message:    str = Field(..., description = "Test message", min_length = 1)
    """Test message content."""


class TestNotificationOut(BaseModel):
    """Response model for test notification."""

    message:    str         = Field(..., description = "Status message")
    """Status message."""

    sent_at:    datetime    = Field(..., description = "Sent timestamp")
    """Timestamp when test was sent."""


class NotificationItemOut(BaseModel):
    """Individual notification history item."""

    id:         BeanieObjectId  = Field(..., description = "Notification ID")
    """Notification identifier."""

    type:       str             = Field(..., description = "Notification type")
    """Type of notification."""

    title:      str | None      = Field(default = None, description = "Notification title")
    """Notification title."""

    message:    str             = Field(..., description = "Notification message")
    """Notification content."""

    sent_at:    datetime        = Field(..., description = "Sent timestamp")
    """When notification was sent."""

    status:     str             = Field(..., description = "Delivery status (delivered/failed/pending)")
    """Delivery status."""


class NotificationHistoryOut(BaseModel):
    """Response model for notification history."""

    notifications: List[NotificationItemOut] = Field(default_factory = list, description = "List of notifications")
    """List of notification items."""

    total:      int = Field(..., description = "Total count")
    """Total number of notifications."""

    limit:      int = Field(..., description = "Requested limit")
    """Requested limit."""


class MessageOut(BaseModel):
    """Generic message response."""

    message:    str = Field(..., description = "Response message")
    """Response message."""