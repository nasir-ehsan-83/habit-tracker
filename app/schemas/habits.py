from beanie import BeanieObjectId
from pydantic import (
    BaseModel, 
    ConfigDict, 
    Field,
    field_validator
)
from datetime import (
    date, 
    time
)

from app.utils.enum import (
    HabitStatus, 
    HabitCategory
)


class HabitBase(BaseModel):
    """Base habit model with common fields."""

    id: BeanieObjectId = Field(
        ..., 
        alias = "_id",
        description = "Unique identifier for the habit (MongoDB ObjectId)"
    )
    """Unique habit identifier."""

    name: str = Field(
        ..., 
        min_length = 3, 
        max_length = 50,
        description = "Habit name (3-50 characters)"
    )
    """Habit name (3-50 characters)."""

    category: HabitCategory = Field(
        ..., 
        description = "Category of the habit (e.g., Health, Education, Fitness)"
    )
    """Habit category (Health, Sport, Study, etc.)."""

    status: HabitStatus = Field(
        ..., 
        description = "Current status of the habit (Active, Paused, Completed, Archived)"
    )
    """Habit status: pending, completed, skipped, deleted, archived."""

    remind_time: time = Field(
        ..., 
        description = "Time of day to send reminder (HH:MM:SS format)"
    )
    """Reminder time (HH:MM:SS)."""

    start_date: date = Field(
        ..., 
        description = "Date when the habit starts"
    )
    """Start date of the habit."""

    end_date: date = Field(
        ..., 
        description = "Date when the habit ends (must be after start_date)"
    )
    """End date of the habit (must be after start_date)."""

    @field_validator("end_date")
    @classmethod 
    def validate_dates(cls, v: date, info) -> date:
        """Validate that end_date is after start_date."""
        if "start_date" in info.data:
            start = info.data["start_date"]
            if v <= start:
                raise ValueError("End date must be after start date")
        return v


class HabitCreate(HabitBase):
    """Request model for creating a habit."""


class HabitPrivateOut(HabitBase):
    """Response model for private habit data (user view)."""

    model_config = ConfigDict(
        from_attributes = True,
        populate_by_name = True
    )


class HabitAdminOut(HabitBase):
    """Response model for admin habit data (includes owner info)."""

    owner_id: BeanieObjectId = Field(
        ..., 
        description = "ID of the user who owns this habit"
    )
    """User who owns this habit."""

    created_at: date = Field(
        ..., 
        description = "Date when the habit was created"
    )
    """Creation date."""

    updated_at: date = Field(
        ..., 
        description = "Date when the habit was last updated"
    )
    """Last update date."""

    model_config = ConfigDict(
        from_attributes = True,
        populate_by_name = True
    )


class HabitUpdate(BaseModel):
    """Request model for updating a habit (all fields optional)."""

    name: str | None = Field(
        default = None,
        min_length = 3,
        max_length = 50,
        description = "Habit name (3-50 characters)"
    )
    """Updated habit name."""

    status: HabitStatus | None = Field(
        default = None,
        description = "Current status of the habit"
    )
    """Updated status."""

    remind_time: time | None = Field(
        default = None,
        description = "Time of day to send reminder"
    )
    """Updated reminder time."""

    start_date: date | None = Field(
        default = None,
        description = "Date when the habit starts"
    )
    """Updated start date."""

    end_date: date | None = Field(
        default = None,
        description = "Date when the habit ends"
    )
    """Updated end date."""

    @field_validator("end_date")
    @classmethod
    def validate_dates(cls, v: date | None, info) -> date | None:
        """Validate that end_date is after start_date (only if both provided)."""
        if v is not None and "start_date" in info.data:
            start = info.data["start_date"]
            if start is not None and v <= start:
                raise ValueError("End date must be after start date")
        return v