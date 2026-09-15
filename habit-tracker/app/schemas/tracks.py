from typing import (
    Any, 
    List
)
import datetime 
from beanie import BeanieObjectId
from pydantic import (
    BaseModel,
    ConfigDict, 
    Field,
    field_validator
)
from app.utils.enum import HabitStatus



class TrackCreate(BaseModel):
    """Request model for creating a track entry."""

    habit_id: BeanieObjectId = Field(
        ..., 
        description = "ID of the habit to track"
    )
    """Habit to track."""

    note: str | None = Field(
        default = None, 
        max_length = 500,
        description = "Optional note for the tracking entry"
    )
    """Optional note about the completion."""

    value: int = Field(
        default = 1, 
        ge = 0,
        description = "Value or progress amount for the habit"
    )
    """Numeric value for measurable habits."""

    date: datetime.date = Field(
        default_factory = lambda: datetime.datetime.now().date(),
        description = "Date of the tracking entry"
    )
    """Date of completion."""

    timestamp: int = Field(
        default_factory = lambda: int(datetime.datetime.now().timestamp()),
        description = "Unix timestamp of the tracking entry"
    )
    """Unix timestamp of completion."""

    status: HabitStatus = Field(
        default = HabitStatus.completed,
        description = "Status of the habit for this tracking entry"
    )
    """Completion status."""



class TrackOut(BaseModel):
    """Response model for track entry."""

    id:         str = Field(
        ..., 
        alias = "_id",
        description = "Unique identifier for the tracking entry"
    )
    """Track identifier."""

    habit_id:   BeanieObjectId = Field(
        ...,
        description = "ID of the tracked habit"
    )
    """Associated habit ID."""

    note:       str | None = Field(
        ...,
        description = "Optional note for the tracking entry"
    )
    """Optional note."""

    value:      int = Field(
        ...,
        description = "Value or progress amount for the habit"
    )
    """Tracked value."""

    date:       datetime.date = Field(
        ...,
        description = "Date of the tracking entry"
    )
    """Completion date."""

    timestamp:  int = Field(
        ...,
        description = "Unix timestamp of the tracking entry"
    )
    """Unix timestamp."""

    status:     HabitStatus = Field(
        ...,
        description = "Status of the habit for this tracking entry"
    )
    """Completion status."""

    created_at: datetime.datetime = Field(
        ...,
        description = "Timestamp when the tracking entry was created"
    )
    """Creation timestamp."""

    updated_at: datetime.datetime = Field(
        ...,
        description = "Timestamp when the tracking entry was last updated"
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



class TrackUpdate(BaseModel):
    """Request model for updating a track entry (all fields optional)."""

    note:       str | None = Field(
        default = None, 
        max_length = 500,
        description = "Updated note for the tracking entry"
    )
    """Updated note."""

    value:      int | None = Field(
        default = None, 
        ge = 0,
        description = "Updated value or progress amount"
    )
    """Updated value."""

    status:     HabitStatus | None = Field(
        default = None,
        description = "Updated status of the habit"
    )
    """Updated status."""





class MissedDaysResponse(BaseModel):
    """Response model for missed days."""

    missed_days:    List[datetime.date] = Field(
        ...,
        description = "List of dates where the habit was missed"
    )
    """List of missed dates."""

    habit_id:       BeanieObjectId | None = Field(
        default = None,
        description = "ID of the habit (optional)"
    )
    """Habit ID if filtered by habit."""