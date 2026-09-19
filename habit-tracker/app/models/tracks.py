import datetime
from beanie import (
    Document, 
    BeanieObjectId,
    before_event,
    Replace,
    Update
)
from pymongo import (
    ASCENDING,
    DESCENDING,
    IndexModel
)
from pydantic import Field
from app.utils.enum import HabitStatus


class Track(Document):
    """Track record for habit completion."""

    owner_id:       BeanieObjectId
    """User who owns this track."""

    habit_id:       BeanieObjectId
    """Habit being tracked."""

    note:           str | None = Field(default = None, max_length = 500)
    """Optional note about the completion."""

    value:          int = Field(default = 1, ge = 0)
    """Numeric value for measurable habits (e.g., minutes, count)."""

    date:           datetime.date = Field(default_factory = lambda: datetime.datetime.now(datetime.timezone.utc).date())
    """Date of the tracked completion."""

    timestamp:      int = Field(default_factory = lambda: int(datetime.datetime.now(datetime.timezone.utc).timestamp()))
    """Unix timestamp of the tracked completion."""

    status:         HabitStatus = Field(default = HabitStatus.completed)
    """Completion status: completed, skipped, failed."""

    created_at:     datetime.datetime = Field(default_factory = lambda: datetime.datetime.now(datetime.timezone.utc))
    """Creation timestamp."""

    updated_at:     datetime.datetime = Field(default_factory = lambda: datetime.datetime.now(datetime.timezone.utc))
    """Last update timestamp."""


    @before_event([Replace, Update])
    async def update_timestamp(self) -> None:
        """Update updated_at timestamp before save."""
        self.updated_at = datetime.datetime.now(datetime.timezone.utc)


    class Settings:
        """MongoDB collection configuration."""

        name = "tracks"

        indexes = [
            IndexModel(
                [
                    ("owner_id", ASCENDING),
                    ("habit_id", ASCENDING),
                    ("date", DESCENDING)
                ],
                unique = True
            ),
        ]