from datetime import (
    date,
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



class Streak(Document):
    """Streak tracking model for habit consistency."""

    owner_id:       BeanieObjectId
    """User who owns this streak."""

    habit_id:       BeanieObjectId
    """Habit associated with this streak."""

    current_streak: int = Field(default = 0, ge = 0)
    """Current consecutive days of habit completion."""

    longest_streak: int = Field(default = 0, ge = 0)
    """All-time best streak achieved."""

    start_date:     date | None = Field(default = None)
    """Date when the current streak started."""

    last_tracked:   date | None = Field(default = None)
    """Date of the last tracked completion."""

    status:         str = Field(default = "active")
    """Streak status: active, inactive."""

    created_at:     datetime = Field(default_factory = lambda: datetime.now(timezone.utc))
    """Creation timestamp."""

    updated_at:     datetime = Field(default_factory = lambda: datetime.now(timezone.utc))
    """Last update timestamp."""


    @before_event([Replace, Update])
    async def update_timestamp(self) -> None:
        """Update updated_at timestamp before save."""
        self.updated_at = datetime.now(timezone.utc)


    class Settings:
        """MongoDB collection configuration."""

        name = "streaks"

        indexes = [
            IndexModel(
                [
                    ("owner_id", ASCENDING),
                    ("habit_id", ASCENDING)
                ],
                unique = True
            ),
        ]