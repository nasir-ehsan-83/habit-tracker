from datetime import datetime
from beanie import BeanieObjectId
from pydantic import (
    BaseModel,
    ConfigDict, 
    Field,
    field_validator
)




class TrackCreate(BaseModel):
    
    habit_id:   BeanieObjectId
    note:       str | None
    value:      int




class TrackOut(TrackCreate):

    id:         BeanieObjectId = Field(alias = "_id")

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes = True, 
        populate_by_name = True
    )

    
    @field_validator("id", mode = "before")
    @classmethod
    def convert_objectid(cls, v: BeanieObjectId):
        return str(v) 
    



class TrackUpdate(BaseModel):

    note:       str | None
    value:      datetime | None