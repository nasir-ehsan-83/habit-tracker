from typing import (
    Any, 
    List
)
from datetime import (
    date, 
    datetime
)
from beanie import BeanieObjectId
from pydantic import (
    BaseModel,
    ConfigDict, 
    Field,
    field_validator
)
from app.utils.enum import HabitStatus



class TrackCreate(BaseModel):
    
    habit_id:   BeanieObjectId
    note:       str | None = Field(default = None, max_length = 500)
    value:      int = Field(default = 1, ge = 0)
    date:       date = Field(default_factory = lambda: datetime.now().date())
    timestamp:  int = Field(default_factory = lambda: int(datetime.now().timestamp()))
    status:     HabitStatus = Field(default = HabitStatus.completed)



class TrackOut(BaseModel):

    id:         str = Field(alias = "_id")
    habit_id:   BeanieObjectId
    note:       str | None
    value:      int
    date:       date
    timestamp:  int
    status:     HabitStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes = True, 
        populate_by_name = True
    )

    
    @field_validator("id", mode = "before")
    @classmethod
    def convert_objectid(cls, v: Any) -> str:
        return str(v) 
    



class TrackUpdate(BaseModel):

    note:       str | None = Field(default = None, max_length = 500)
    value:      int | None = Field(default = None, ge = 0)
    status:     HabitStatus | None = Field(default = None)





class MissedDaysResponse(BaseModel):
    missed_days:    List[date]
    habit_id:       BeanieObjectId | None = None