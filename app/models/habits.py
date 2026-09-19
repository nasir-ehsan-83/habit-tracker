from datetime import (
    datetime, 
    timezone, 
    date, 
    time
)
from pydantic import (
    Field,
    field_serializer, 
    model_validator
)
from beanie import (
    Document, 
    BeanieObjectId
)
from pymongo import (
    ASCENDING, 
    IndexModel
)
from app.utils.enum import (
    HabitCategory, 
    HabitStatus
)



class Habit(Document):
    """Habit tracking model for users."""

    name:           str = Field(min_length = 1)
    """Habit name (e.g., "Morning Exercise")."""

    owner_id:       BeanieObjectId
    """User who owns this habit."""

    status:         HabitStatus = HabitStatus.pending
    """Current status: pending, active, archived, deleted."""

    category:       HabitCategory
    """Habit category (HEALTH, SPORT, STUDY, WORK)."""

    remind_time:    time
    """Reminder time (HH:MM:SS)."""

    start_date:     date
    """Tracking start date."""

    end_date:       date
    """Tracking end date."""

    created_at:     datetime = Field(default_factory = lambda: datetime.now(timezone.utc))
    """Creation timestamp."""

    updated_at:     datetime = Field(default_factory = lambda: datetime.now(timezone.utc))
    """Last update timestamp."""


    @field_serializer('remind_time')
    def serialize_time(self, remind_time: time) -> str:
        """Convert time to string format."""
        return remind_time.strftime("%H:%M:%S")


    @model_validator(mode = "after")
    def validate_dates(self) -> 'Habit':
        """Validate start_date and end_date constraints."""
        if self.end_date < self.start_date:
            raise ValueError("end_date cannot be before start_date")
        
        if self.start_date < date.today():
            raise ValueError("start_date cannot be before today")
            
        return self


    class Settings:
        """MongoDB collection configuration."""

        name = "habits"

        bson_encoders = {
            time: lambda t: t.strftime("%H:%M:%S")
        }

        indexes = [
            IndexModel(
                [("name", ASCENDING), ("owner_id", ASCENDING)],
                unique = True
            )
        ]