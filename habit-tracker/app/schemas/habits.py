from typing import Optional
from pydantic import (
    BaseModel, 
    ConfigDict, 
    Field
)
from datetime import date, time

from app.utils.enum import HabitStatus

class HabitBase(BaseModel):
    name: str = Field(
        min_length = 3, 
        max_length = 50
    )
    status: HabitStatus
    remind_time: time
    start_date: date
    end_date: date

class HabitCreate(HabitBase):
    pass

class HabitPrivateOut(HabitBase):
    pass

class HabitAdminOut(HabitBase):
    _id: int
    owner_id: int
    created_at: date
    updated_at: date

    model_config = ConfigDict(
        from_attributes = True, 
        populate_by_name = True
    )

class HabitUpdate(BaseModel):
    name: Optional[str] = Field(
        default = None, 
        min_lenght = 3, 
        max_length = 50
    )
    status: Optional[HabitStatus] = Field(default = None)
    remind_time: Optional[time] = Field(default = None)
    start_date: Optional[date] = Field(default = None)
    end_date: Optional[date] = Field(default = None)