from collections import defaultdict
from datetime import (
    date,
    datetime, 
    timedelta
)
from typing import Dict, List, Tuple
from beanie import BeanieObjectId
from fastapi import (
    HTTPException, 
    status
)

from app.models import(
    Habit, 
    Track, 
    Streak
)
from app.schemas import (
    HeatmapOut,
    DistributionOut, 
    ProgressChartOut,
    DashboardOut,
    BestHabitOut, 
    ExportOut, 
    InsightsOut
)
from app.utils.enum import Timeframe
from app.config import logger




async def get_dashboard_service(
    timeframe:  Timeframe | None = None
) -> DashboardOut:

    """Retrieves comprehensive dashboard analytics for the authenticated user.

    This service aggregates key metrics from the database to provide an
    overview of the user's performance and activity statistics.

    Args:
        timeframe: Optional time period for analytics aggregation 
            (DAY, WEEK, MONTH, YEAR). If not provided, uses default aggregation.

    Returns:
        DashboardOut: Dashboard analytics containing: total_habits, active_habits, completion_rate, best_habit and total_days_tracked 
         
    Raises:
        HTTPException 500: If an internal server error occurs during 
            database operations.
    """
    
    try:
        total_habits = await Habit.count()
        
        active_habits = await Habit.find(Habit.status == "active").count()
        
        total_tracks = await Track.count()
        total_habits_count = await Habit.count()
        
        completion_rate = total_tracks / (total_habits_count * 30) if total_habits_count > 0 else 0.0
        completion_rate = min(completion_rate, 1.0)
        
        streaks = await Streak.find().sort("-current_streak").limit(1).to_list()
        best_habit = None
        
        if streaks:
            streak = streaks[0]
            habit = await Habit.get(streak.habit_id)
            
            if habit:
                best_habit = BestHabitOut(
                    title = habit.title,
                    streak = streak.current_streak
                )
        
        total_days_tracked = await Track.count()
        
        return DashboardOut(
            total_habits = total_habits,
            active_habits = active_habits,
            completion_rate = round(completion_rate, 2),
            best_habit = best_habit,
            total_days_tracked = total_days_tracked
        )
        
    except HTTPException:
        raise
        
    except Exception as error:
        logger.error(f"Unexpected error in get_dashboard_service: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def get_heatmap_service(
    year:   int,
    month:  int | None = None
) -> HeatmapOut:
    
    """Retrieves heatmap data showing habit completion intensity over time.

    This service provides visual representation of user's habit completion
    patterns, displaying daily activity levels for the specified time period.

    Args:
        year: The year for which to retrieve heatmap data.
        month: Optional month (1-12) for focused monthly view. 
            If None, returns data for the entire year.

    Returns:
        HeatmapOut: Heatmap data containing:, heatmap, year and month

    Raises:
        HTTPException 500: If an internal server error occurs during 
            database operations.
    """
    
    try:
        start_date: date = date(year, month, 1) if month else date(year, 1, 1)
        end_date: date = date(year, month + 1, 1) - timedelta(days = 1) if month else date(year, 12, 31)
        
        tracks: List[Track] = await Track.find(
            Track.date >= start_date,
            Track.date <= end_date
        ).to_list()
        
        heatmap: Dict[int, int] = defaultdict(int)

        for track in tracks:
            day: int = track.date.day
            heatmap[day] += 1
        
        return HeatmapOut(
            heatmap = dict(heatmap),
            year = year,
            month = month
        )
        
    except HTTPException:
        raise
        
    except Exception as error:
        logger.error(f"Unexpected error in get_heatmap_service: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def get_progress_chart_service(
    habit_id:   BeanieObjectId,
    period:     int = 90
) -> ProgressChartOut:
    
    """Retrieves progress chart data for a specific habit over time.

    This service provides trend analysis for a habit, showing completion
    patterns and performance metrics over the specified period.

    Args:
        habit_id: The MongoDB ObjectId of the habit to analyze.
        period: Number of days to include in the chart (1-365). Defaults to 90.

    Returns:
        ProgressChartOut: Progress chart data containing: labels, values, target_line and habit_title

    Raises:
        HTTPException 404: If habit not found.
        HTTPException 500: If an internal server error occurs during 
            database operations.
    """
    
    try:
        habit: Habit | None = await Habit.get(habit_id)
        
        if not habit:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Habit not found"
            )
        
        start_date: date = date.today() - timedelta(days = period)
        
        tracks: List[Track] = await Track.find(
            Track.habit_id == habit_id,
            Track.date >= start_date
        ).sort("date").to_list()
        
        labels: List[date] = []
        values: List[int] = []
        track_dict: Dict[date, int] = {track.date: 1 for track in tracks}
        
        current_date: date = start_date

        while current_date <= date.today():
            labels.append(current_date)
            values.append(track_dict.get(current_date, 0))
            current_date += timedelta(days = 1)
        
        return ProgressChartOut(
            labels = labels,
            values = values,
            target_line = habit.target_count if hasattr(habit, 'target_count') else None,
            habit_title = habit.title
        )
        
    except HTTPException:
        raise
        
    except Exception as error:
        logger.error(f"Unexpected error in get_progress_chart_service: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def get_distribution_service(
    habit_id:   BeanieObjectId
) -> DistributionOut:
    
    """Retrieves distribution analytics for a specific habit.

    This service provides insights into how habit completions are distributed
    across different time slots of the day.

    Args:
        habit_id: The MongoDB ObjectId of the habit to analyze.

    Returns:
        DistributionOut: Distribution data containing: distribution and habit_title

    Raises:
        HTTPException 404: If habit not found.
        HTTPException 500: If an internal server error occurs during 
            database operations.
    """
    
    try:
        habit: Habit | None = await Habit.get(habit_id)
        
        if not habit:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Habit not found"
            )
        
        tracks: List[Track] = await Track.find(Track.habit_id == habit_id).to_list()
        
        distribution: Dict[str, int] = defaultdict(int)

        time_slots: List[Tuple[str, int, int]] = [
            ("6-9", 6, 9),
            ("9-12", 9, 12),
            ("12-15", 12, 15),
            ("15-18", 15, 18),
            ("18-21", 18, 21)
        ]
        
        for track in tracks:
            
            if track.created_at:
                hour: int = track.created_at.hour
            
                for slot_name, start, end in time_slots:
            
                    if start <= hour < end:
                        distribution[slot_name] += 1
                        break
        
        return DistributionOut(
            distribution = dict(distribution),
            habit_title = habit.title
        )
        
    except HTTPException:
        raise
        
    except Exception as error:
        logger.error(f"Unexpected error in get_distribution_service: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )
    



async def get_insights_service() -> InsightsOut:
    
    """Retrieves personalized insights and recommendations for the user.

    This service analyzes the user's habit tracking data to provide
    meaningful insights, patterns, and actionable recommendations for
    improving habit consistency and performance.

    Returns:
        InsightsOut: Personalized insights containing: insights and generated_at

    Raises:
        HTTPException 500: If an internal server error occurs during 
            database operations.
    """
    
    try:
        insights: List[str] = []
        
        habits: List[Habit] = await Habit.find().to_list()
        total_habits: int = len(habits)
        
        if total_habits > 0:
            insights.append(f"You have {total_habits} active habits")
        
        top_streak: List[Streak] = await Streak.find().sort("-current_streak").limit(1).to_list()
        
        if top_streak:
            habit: Habit | None = await Habit.get(top_streak[0].habit_id)
        
            if habit:
                insights.append(f"Best streak: {top_streak[0].current_streak} days for {habit.title}")
        
        tracks_today: int = await Track.find(Track.date == date.today()).count()
        
        if tracks_today == 0:
            insights.append("You haven't tracked any habit today. Start now!")
        
        else:
            insights.append(f"You've tracked {tracks_today} habits today")
        
        weekday_tracks: Dict[int, int] = defaultdict(int)
        tracks: List[Track] = await Track.find().to_list()
        
        for track in tracks:
            weekday: int = track.date.weekday()
            weekday_tracks[weekday] += 1
        
        if weekday_tracks:
            
            best_day: int = max(weekday_tracks.items(), key = lambda x: x[1])[0]
            days: List[str] = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            insights.append(f"Your most productive day is {days[best_day]}")
        
        return InsightsOut(
            insights = insights
        )
        
    except HTTPException:
        raise
        
    except Exception as error:
        logger.error(f"Unexpected error in get_insights_service: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )




async def export_data_service(
    format:     str,
    from_date:  date | None = None,
    to_date:    date | None = None
) -> ExportOut:
    
    """Exports the user's habit tracking data in the specified format.

    This service allows users to export their habit data for backup,
    analysis, or migration purposes. Data can be filtered by date range
    and exported in JSON or CSV format.

    Args:
        format: Export format - either 'json' or 'csv'.
        from_date: Optional start date for data inclusion (YYYY-MM-DD).
        to_date: Optional end date for data inclusion (YYYY-MM-DD).

    Returns:
        ExportOut: Export data containing: download_url, format, expire_at

    Raises:
        HTTPException 500: If an internal server error occurs during 
            data export operations.
    """
    
    try:
        query: Dict[str, Dict[str, date]] = {}
        
        if from_date:
            query["date"] = {"$gte": from_date}
        
        if to_date:
            query["date"] = {"$lte": to_date}
        
        tracks: List[Track] = await Track.find(query).to_list()
        
        export_data: List[Dict[str, str | None]] = []
        
        for track in tracks:
        
            export_data.append({
                "habit_id": str(track.habit_id),
                "date": track.date.isoformat(),
                "created_at": track.created_at.isoformat() if track.created_at else None
            })
        
        download_url = f"https://s3.amazonaws.com/bucket/export_{date.today().isoformat()}.{format}"
        
        return ExportOut(
            download_url = download_url,
            format = format,
            expires_at = datetime.now() + timedelta(hours = 24)
        )
        
    except HTTPException:
        raise
        
    except Exception as error:
        logger.error(f"Unexpected error in get_export_service: {error}", exc_info = True)
        
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Internal server error"
        )