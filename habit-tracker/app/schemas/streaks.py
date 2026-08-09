from datetime import (
    datetime,
    date
)
from beanie import BeanieObjectId
from pydantic import BaseModel



class StreakResponse(BaseModel):
    owner_id:       BeanieObjectId
    habit_id:       BeanieObjectId
    status:         str 
    created_at:     datetime 
    updated_at:     datetime 



class CurrentStreakOut(StreakResponse):
    current_streak:     int
    start_date:         date | None = None
    last_tracked:       date | None = None



class BestStreakOut(StreakResponse):
    best_streak:    int