from datetime import (
    datetime,
    date
)
from beanie import BeanieObjectId
from pydantic import BaseModel

class StreakResponse(BaseModel):
    habit_id:       BeanieObjectId
    streak_count:   int 
    start_date:     date 
    last_tracked:   date 
    status:         str 
    created_at:     datetime 
    updated_at:     datetime 
