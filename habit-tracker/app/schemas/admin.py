from pydantic import BaseModel, Field, field_validator


class AppStatsOut(BaseModel):
    """Application statistics response for admin dashboard."""

    total_users:    int = Field(..., description = "Total number of registered users", ge = 0)
    """Total number of registered users."""

    active_users:   int = Field(..., description = "Number of active users (logged in within last 7 days)", ge = 0)
    """Number of active users (logged in within last 7 days)."""

    total_habits:   int = Field(..., description = "Total number of habits created by all users", ge = 0)
    """Total number of habits created by all users."""

    total_streaks:  int = Field(..., description = "Total number of active streaks across all users", ge = 0)
    """Total number of active streaks across all users."""

    @field_validator("total_users", "active_users", "total_habits", "total_streaks")
    @classmethod
    def validate_non_negative(cls, v: int) -> int:
        """Ensure all values are non-negative."""
        if v < 0:
            raise ValueError("Value must be non-negative")
        return v