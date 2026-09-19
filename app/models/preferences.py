from datetime import (
    datetime,
    timezone
)
from beanie import (
    Document, 
    BeanieObjectId,
    before_event,
    Replace,
    Update
)
from pymongo import (
    ASCENDING,
    IndexModel
)
from pydantic import Field


class UserPreference(Document):
    """User preferences and application settings."""

    owner_id:               BeanieObjectId
    """User who owns these preferences."""

    theme:                  str = Field(default = "light", max_length = 20)
    """UI theme (light, dark, system)."""

    language:               str = Field(default = "en", max_length = 10)
    """Preferred language code (en, fa, etc.)."""

    timezone:               str = Field(default = "UTC", max_length = 50)
    """User timezone (e.g., UTC, Asia/Tehran)."""

    start_of_week:          str = Field(default = "saturday", max_length = 20)
    """First day of the week (saturday, sunday, monday)."""

    notifications_enabled:  bool = Field(default = True)
    """Enable/disable all notifications."""

    reminder_time:          str | None = Field(default = "20:00", max_length = 5)
    """Default reminder time (HH:MM)."""

    default_view:           str = Field(default = "daily", max_length = 20)
    """Default dashboard view (daily, weekly, monthly)."""

    created_at:             datetime = Field(default_factory = lambda: datetime.now(timezone.utc))
    """Creation timestamp."""

    updated_at:             datetime = Field(default_factory = lambda: datetime.now(timezone.utc))
    """Last update timestamp."""


    @before_event([Replace, Update])
    async def update_timestamp(self) -> None:
        """Update updated_at timestamp before save."""
        self.updated_at = datetime.now(timezone.utc)


    class Settings:
        """MongoDB collection configuration."""

        name = "user_preferences"

        indexes = [
            IndexModel(
                [("owner_id", ASCENDING)],
                unique = True
            ),
        ]