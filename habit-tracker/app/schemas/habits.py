from beanie import BeanieObjectId
from pydantic import (
    BaseModel, 
    ConfigDict, 
    Field
)
from datetime import (
    date, 
    time
)

from app.utils.enum import (
    HabitStatus, 
    HabitCategory
)




class HabitBase(BaseModel):
    
    name:           str = Field(
        min_length = 3, 
        max_length = 50
    )
    
    category:       HabitCategory
    status:         HabitStatus
    remind_time:    time
    start_date:     date
    end_date:       date




class HabitCreate(HabitBase):
    pass




class HabitPrivateOut(HabitBase):
    pass




class HabitAdminOut(HabitBase):

    _id:            BeanieObjectId
    owner_id:       BeanieObjectId
    created_at:     date
    updated_at:     date

    
    model_config = ConfigDict(
        from_attributes = True, 
        populate_by_name = True
    )




class HabitUpdate(BaseModel):
    
    name:           str | None = Field(
        default = None, 
        min_length = 3,
        max_length = 50
    )
    
    status:         HabitStatus | None  = Field(default = None)
    remind_time:    time | None         = Field(default = None)
    start_date:     date | None         = Field(default = None)
    end_date:       date | None         = Field(default = None)