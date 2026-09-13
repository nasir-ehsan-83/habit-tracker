from typing import Any
from datetime import datetime
from pydantic import (
    BaseModel,
    ConfigDict, 
    Field,
    field_validator
)


class PreferenceOut(BaseModel):
    """Response model for user preferences."""

    id: str = Field(
        ..., 
        alias = "_id",
        description = "Unique identifier for the user preferences (MongoDB ObjectId)"
    )
    """Unique preference identifier."""

    theme: str = Field(
        ..., 
        max_length = 20,
        description = "UI theme preference (e.g., light, dark, system)"
    )
    """UI theme (light, dark, system)."""

    language: str = Field(
        ..., 
        max_length = 10,
        description = "User's preferred language code (e.g., en, fa, fr)"
    )
    """Language code (en, fa, fr, etc.)."""

    timezone: str = Field(
        ..., 
        max_length = 50,
        description = "User's timezone (e.g., Asia/Tehran, UTC, America/New_York)"
    )
    """User timezone."""

    start_of_week: str = Field(
        ..., 
        max_length = 20,
        description = "First day of the week (e.g., monday, sunday)"
    )
    """First day of the week."""

    notifications_enabled: bool = Field(
        ..., 
        description = "Whether notifications are enabled for the user"
    )
    """Enable/disable notifications."""

    reminder_time: str | None = Field(
        default = None,
        max_length = 5,
        description = "Default reminder time in HH:MM format (24-hour)"
    )
    """Default reminder time (HH:MM)."""

    default_view: str = Field(
        ..., 
        max_length = 20,
        description = "Default view for the dashboard (e.g., daily, weekly, monthly)"
    )
    """Default dashboard view."""

    created_at: datetime = Field(
        ..., 
        description = "Timestamp when the preferences were created"
    )
    """Creation timestamp."""

    updated_at: datetime = Field(
        ..., 
        description = "Timestamp when the preferences were last updated"
    )
    """Last update timestamp."""

    model_config = ConfigDict(
        from_attributes = True, 
        populate_by_name = True
    )

    @field_validator("id", mode = "before")
    @classmethod
    def convert_objectid(cls, v: Any) -> str:
        """Convert ObjectId to string."""
        return str(v)


class PreferenceUpdate(BaseModel):
    """Request model for updating user preferences (all fields optional)."""

    theme: str | None = Field(
        default = None,
        max_length = 20,
        description = "UI theme preference (e.g., light, dark, system)"
    )
    """Updated UI theme."""

    language: str | None = Field(
        default = None,
        max_length = 10,
        description = "User's preferred language code (e.g., en, fa, fr)"
    )
    """Updated language code."""

    timezone: str | None = Field(
        default = None,
        max_length = 50,
        description = "User's timezone (e.g., Asia/Tehran, UTC, America/New_York)"
    )
    """Updated timezone."""

    start_of_week: str | None = Field(
        default = None,
        max_length = 20,
        description = "First day of the week (e.g., monday, sunday)"
    )
    """Updated first day of week."""

    notifications_enabled: bool | None = Field(
        default = None,
        description = "Whether notifications are enabled for the user"
    )
    """Updated notification setting."""

    reminder_time: str | None = Field(
        default = None,
        max_length = 5,
        description = "Default reminder time in HH:MM format (24-hour)"
    )
    """Updated reminder time (HH:MM)."""

    default_view: str | None = Field(
        default = None,
        max_length = 20,
        description = "Default view for the dashboard (e.g., daily, weekly, monthly)"
    )
    """Updated default view."""

    @field_validator("reminder_time")
    @classmethod
    def validate_reminder_time(cls, v: str | None) -> str | None:
        """Validate HH:MM format."""
        if v is not None:
            import re
            pattern = r"^([01]\d|2[0-3]):([0-5]\d)$"
            
            if not re.match(pattern, v):
                raise ValueError("reminder_time must be in HH:MM format (e.g., 14:30)")
        return v

    @field_validator("theme", "language", "timezone", "start_of_week", "default_view", check_fields = False)
    @classmethod
    def validate_not_empty(cls, v: str | None) -> str | None:
        """Ensure string fields are not empty."""
        if v is not None and len(v.strip()) == 0:
            raise ValueError('Field cannot be empty string')
        return v