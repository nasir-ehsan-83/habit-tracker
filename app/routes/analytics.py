from typing import Annotated
from datetime import date
from beanie import BeanieObjectId
from fastapi import (
    APIRouter, 
    Depends, 
    Query
)

from app.dependencies import get_current_user
from app.utils.enum import Timeframe
from app.schemas import (
    HeatmapOut, 
    ProgressChartOut,
    DashboardOut,
    DistributionOut,
    ExportOut, 
    InsightsOut
)
from app.services.analytics_service import (
    get_dashboard_service,
    get_distribution_service,
    export_data_service,
    get_heatmap_service,
    get_progress_chart_service,
    get_insights_service
)




router: APIRouter = APIRouter(
    prefix = '/api/analytics',
    tags = ["Analytics"],
    dependencies = [
        Depends(get_current_user)
    ]
)


@router.get(
    '/dashboard',
    response_model = DashboardOut,
    summary = "Retrieve dashboard analytics",
    description = "Fetches comprehensive dashboard analytics including key metrics, recent activities, and habits stats overview for the authenticated user."
)
async def get_dashboard_route(
    timeframe:      Annotated[Timeframe | None, Query(description = "Time period for analytics aggregation (e.g., DAY, WEEK, MONTH, YEAR). If not provided, uses default timeframe.")] = None
) -> DashboardOut:
    
    """Retrieves comprehensive dashboard analytics for the authenticated user.

    This endpoint aggregates key metrics and provides an overview of the user's
    performance, including habit completion rates, streaks, and recent activities.

    **Response Codes:**
    - 200: Dashboard data retrieved successfully
    - 401: Unauthorized - Authentication required
    - 500: Internal server error

    Args:
        timeframe: Optional time period for data collection (DAY, WEEK, MONTH, YEAR).

    Returns:
        DashboardOut: Dashboard analytics containing user's activities informations

    Raises:
        HTTPException 401: If user is not authenticated.
        HTTPException 500: If an internal server error occurs.
    """

    return await get_dashboard_service(timeframe)




@router.get(
    '/heatmap',
    response_model = HeatmapOut,
    summary = "Retrieve habit heatmap data",
    description = "Fetches heatmap data for habit completions over time, showing daily activity for the specified year and month."
)
async def get_heatmap_route(
    year:       Annotated[int, Query(ge = 2020, le = 2100, description = "Year for the heatmap data (2020-2100).")],
    month:      Annotated[int | None, Query(ge = 1, le = 12, description = "Month for the heatmap data (1-12). If not provided, returns data for the entire year.")] = None
) -> HeatmapOut:
    
    """Retrieves heatmap data showing habit completion over time.

    This endpoint provides visual representation of user's habit completion
    patterns, displaying daily activity levels for the specified time period.

    **Response Codes:**
    - 200: Heatmap data retrieved successfully
    - 401: Unauthorized - Authentication required
    - 500: Internal server error

    Args:
        year: The year for which to retrieve heatmap data (2020-2100).
        month: Optional month (1-12) for focused monthly view. If None, returns yearly data.

    Returns:
        HeatmapOut: Heatmap data containing: heatmap, year and month
        
    Raises:
        HTTPException 401: If user is not authenticated.
        HTTPException 500: If an internal server error occurs.
    """

    return await get_heatmap_service(year, month)




@router.get(
    '/progress-chart',
    response_model = ProgressChartOut,
    summary = "Retrieve habit progress chart",
    description = "Fetches progress chart data for a specific habit, showing completion trends over the specified period."
)
async def get_progress_chart_route(
    habit_id:   Annotated[BeanieObjectId, Query(description = "The unique MongoDB ObjectId of the habit to analyze.")],
    period:     Annotated[int, Query(ge = 1, le = 365, description = "Number of days to include in the progress chart (1-365). Defaults to 90.")] = 90
) -> ProgressChartOut:
    
    """Retrieves progress chart data for a specific habit over time.

    This endpoint provides trend analysis for a habit, showing completion
    patterns, streaks, and performance metrics over the specified period.

    **Response Codes:**
    - 200: Progress chart data retrieved successfully
    - 401: Unauthorized - Authentication required
    - 404: Habit not found or user doesn't have access
    - 500: Internal server error

    Args:
        habit_id: The MongoDB ObjectId of the habit to analyze.
        period: Number of days to include in the chart (1-365). Defaults to 90.

    Returns:
        ProgressChartOut: Progress chart data containing: labels, values, target_line and habit_title

    Raises:
        HTTPException 401: If user is not authenticated.
        HTTPException 404: If habit not found or doesn't belong to user.
        HTTPException 500: If an internal server error occurs.
    """

    return await get_progress_chart_service(habit_id, period)




@router.get(
    '/distribution',
    response_model = DistributionOut,
    summary = "Retrieve habit distribution",
    description = "Fetches distribution analytics for a specific habit, showing patterns across different categories, times, or completion statuses."
)
async def get_distribution_route(
    habit_id:   Annotated[BeanieObjectId, Query(description = "The unique MongoDB ObjectId of the habit to analyze.")]
) -> DistributionOut:
    
    """Retrieves distribution analytics for a specific habit.

    This endpoint provides insights into how habit completions are distributed
    across different dimensions such as time of day, day of week, or category.

    **Response Codes:**
    - 200: Distribution data retrieved successfully
    - 401: Unauthorized - Authentication required
    - 404: Habit not found or user doesn't have access
    - 500: Internal server error

    Args:
        habit_id: The MongoDB ObjectId of the habit to analyze.

    Returns:
        DistributionOut: Distribution data containing: distribution, habit_title
    Raises:
        HTTPException 401: If user is not authenticated.
        HTTPException 404: If habit not found or doesn't belong to user.
        HTTPException 500: If an internal server error occurs.
    """

    return await get_distribution_service(habit_id)




@router.get(
    '/insights',
    response_model = InsightsOut,
    summary = "Retrieve user insights",
    description = "Fetches personalized insights and recommendations based on the user's habit tracking patterns and performance."
)
async def get_insights_route() -> InsightsOut:
    
    """Retrieves personalized insights and recommendations for the user.

    This endpoint analyzes the user's habit tracking data to provide
    meaningful insights, patterns, and actionable recommendations for
    improving habit consistency and performance.

    **Response Codes:**
    - 200: Insights retrieved successfully
    - 401: Unauthorized - Authentication required
    - 500: Internal server error

    Returns:
        InsightsOut: Personalized insights containing: insights and generated_at

    Raises:
        HTTPException 401: If user is not authenticated.
        HTTPException 500: If an internal server error occurs.
    """

    return await get_insights_service()




@router.get(
    '/export',
    response_model = ExportOut,
    summary = "Export habit data",
    description = "Exports user's habit tracking data in JSON or CSV format, with optional date range filtering for the specified period."
)
async def export_data_route(
    format:         Annotated[str, Query(pattern = "^(json|csv)$", description = "Export format: 'json' or 'csv'.")] = "json",
    from_date:      Annotated[date | None, Query(description = "Start date for data export. If not provided, exports from the beginning.")] = None,
    to_date:        Annotated[date | None, Query(description = "End date for data export. If not provided, exports to the current date.")] = None
) -> ExportOut:
    
    """Exports the user's habit tracking data in the specified format.

    This endpoint allows users to download their habit data for backup,
    analysis, or migration purposes. Data can be filtered by date range
    and exported in JSON or CSV format.

    **Response Codes:**
    - 200: Data exported successfully
    - 401: Unauthorized - Authentication required
    - 400: Invalid date range or format
    - 500: Internal server error

    Args:
        format: Export format - either 'json' or 'csv'. Defaults to 'json'.
        from_date: Optional start date for data inclusion (YYYY-MM-DD).
        to_date: Optional end date for data inclusion (YYYY-MM-DD).

    Returns:
        ExportOut: Export data containing: download_url, format and expire_at

    Raises:
        HTTPException 401: If user is not authenticated.
        HTTPException 400: If date range is invalid or format is unsupported.
        HTTPException 500: If an internal server error occurs.
    """

    return await export_data_service(format, from_date, to_date)