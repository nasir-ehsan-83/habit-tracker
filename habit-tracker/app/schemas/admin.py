from pydantic import BaseModel

class AppStatsOut(BaseModel):
    total_users:    int
    active_users:   int     
    total_habits:   int
    total_streaks:  int    
