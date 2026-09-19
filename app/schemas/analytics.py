from typing import (
    Dict, 
    List
)
from datetime import (
    date,
    datetime
)
from pydantic import (
    BaseModel, 
    Field
)




class BestHabitOut(BaseModel):
    """Best performing habit with streak count."""

    title:      str = Field(..., description = "Habit title")
    """Habit title."""

    streak:     int = Field(..., ge = 0, description = "Current streak count")
    """Current streak count."""




class DashboardOut(BaseModel):
    """Dashboard analytics response."""

    total_habits:       int                 = Field(..., ge = 0, description = "Total number of habits")
    """Total number of habits."""

    active_habits:      int                 = Field(..., ge = 0, description = "Number of active habits")
    """Number of active habits."""

    completion_rate:    float               = Field(..., ge = 0.0, le = 1.0, description = "Overall completion rate")
    """Overall completion rate (0.0 to 1.0)."""

    best_habit:         BestHabitOut | None = Field(default = None, description = "Best performing habit")
    """Best performing habit with streak count."""

    total_days_tracked: int                 = Field(..., ge = 0, description = "Total days tracked across all habits")
    """Total days tracked across all habits."""




class HeatmapOut(BaseModel):
    """Heatmap data for habit completions."""

    heatmap:    Dict[int, int]  = Field(
        default_factory = dict,
        description = "Dictionary with day as key and count as value"
    )
    """Dictionary mapping day to completion count."""

    year:       int             = Field(..., description = "Year of the heatmap")
    """Year of the heatmap."""

    month:      int | None      = Field(default = None, description = "Month of the heatmap if applicable")
    """Month of the heatmap (1-12) if applicable."""




class ProgressChartOut(BaseModel):
    """Progress chart data for a habit."""

    labels:         List[date]  = Field(default_factory = list, description = "List of dates for x-axis")
    """List of dates for x-axis."""

    values:         List[int]   = Field(default_factory = list, description = "List of values for y-axis")
    """List of values for y-axis (0 or 1)."""

    target_line:    int | None  = Field(default = None, description = "Target value line")
    """Target value line for comparison."""

    habit_title:    str         = Field(..., description = "Habit title")
    """Title of the habit."""

 


class DistributionOut(BaseModel):
    """Distribution of habit completions by time slots."""

    distribution:   Dict[str, int] = Field(
        default_factory = dict,
        description = "Time slots with count of completions"
    )
    """Time slots mapped to completion counts."""

    habit_title:    str = Field(..., description = "Habit title")
    """Title of the habit."""




class InsightsOut(BaseModel):
    """AI-generated insights for user."""

    insights:       List[str]   = Field(default_factory = list, description = "List of AI-generated insights")
    """List of AI-generated insights."""

    generated_at:   datetime    = Field(default_factory = lambda: datetime.now(), description = "Timestamp of insight generation")
    """Timestamp when insights were generated."""




class ExportOut(BaseModel):
    """Export data response with download URL."""

    download_url:   str         = Field(..., description = "URL to download the exported file")
    """URL to download the exported file."""

    format:         str         = Field(..., description = "Export format (json or csv)")
    """Export format (json or csv)."""

    expires_at:     datetime    = Field(..., description = "Expiration time of the download URL")
    """Expiration time of the download URL."""