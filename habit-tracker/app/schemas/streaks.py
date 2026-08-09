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
    start_date:         date 
    last_tracked:       date 



class BestStreakOut(StreakResponse):
    best_streak:    int