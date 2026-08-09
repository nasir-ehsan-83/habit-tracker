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
    IndexModel
)
from pydantic import Field



class Streak(Document):

    owner_id:       BeanieObjectId
    habit_id:       BeanieObjectId
    current_streak: int = Field(default = 0, ge = 0)
    longest_streak: int = Field(default = 0, ge = 0)
    start_date:     date | None = Field(default = None)
    last_tracked:   date | None = Field(default = None)
    status:         str = Field(default = "active")

    created_at:     datetime = Field(default_factory = lambda: datetime.now(timezone.utc))
    updated_at:     datetime = Field(default_factory = lambda: datetime.now(timezone.utc))


    @before_event([Replace, Update])
    async def update_timestamp(self) -> None:
        self.updated_at = datetime.now(timezone.utc)


    class Settings:

        name = "streaks"

        indexes = [
            IndexModel(
                [
                    ("owner_id", ASCENDING),
                    ("habit_id", ASCENDING)
                ],
                unique = True
            ),
        ]
