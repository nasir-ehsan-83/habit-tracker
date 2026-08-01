from datetime import (
    date,
    datetime,
    timezone
)
from beanie import (
    Document, 
    BeanieObjectId,
    before_event,
    Replace,
    Update
)
from pymongo import (
    ASCENDING,
    DESCENDING,
    IndexModel
)
from pydantic import Field
from app.utils.enum import HabitStatus


class Track(Document):

    owner_id:       BeanieObjectId
    habit_id:       BeanieObjectId
    note:           str | None = Field(default = None, max_length = 500)
    value:          int = Field(default = 1, ge = 0)
    date:           date = Field(default_factory = lambda: datetime.now(timezone.utc).date())
    timestamp:      int = Field(default_factory = lambda: int(datetime.now(timezone.utc).timestamp()))
    status:         HabitStatus = Field(default =  HabitStatus.completed)

    created_at:     datetime = Field(default_factory = lambda: datetime.now(timezone.utc))
    updated_at:     datetime = Field(default_factory = lambda: datetime.now(timezone.utc))


    @before_event([Replace, Update])
    async def update_timestamp(self) -> None:
        self.updated_at = datetime.now(timezone.utc)


    class Settings:

        name = "tracks"

        indexes = [
            IndexModel(
                [
                    ("owner_id", ASCENDING),
                    ("habit_id", ASCENDING),
                    ("date", DESCENDING)
                ],
                unique = True
            ),
        ]
