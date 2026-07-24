from datetime import (
    datetime, 
    timezone, 
    date, 
    time
)
from pydantic import (
    Field,
    field_serializer, 
    model_validator
)
from beanie import (
    Document, 
    BeanieObjectId
)
from pymongo import (
    ASCENDING, 
    IndexModel
)
from app.utils.enum import HabitStatus

class Habit(Document):
    name: str = Field(min_length=1)
    owner_id: BeanieObjectId
    status: HabitStatus = HabitStatus.pending
    
    remind_time: time
    start_date: date
    end_date: date
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_serializer('remind_time')
    def serialize_time(self, remind_time: time):
        return remind_time.strftime("%H:%M:%S")

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date cannot be before start_date")
        
        if self.start_date < date.today():
            raise ValueError("start_date cannot be before today")
            
        return self

    class Settings:
        name = "habits"
        
        bson_encoders = {  # type: ignore
            time: lambda t: t.strftime("%H:%M:%S")  # type: ignore
        }

        indexes = [
            IndexModel(
                [("name", ASCENDING), ("owner_id", ASCENDING)],
                unique=True
            )
        ]
