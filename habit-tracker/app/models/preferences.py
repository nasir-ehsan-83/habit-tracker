from datetime import (
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


class UserPreference(Document):

    owner_id:               BeanieObjectId
    theme:                  str = Field(default = "light", max_length = 20)
    language:               str = Field(default = "en", max_length = 10)
    timezone:               str = Field(default = "UTC", max_length = 50)
    start_of_week:          str = Field(default = "saturday", max_length = 20)
    notifications_enabled:  bool = Field(default = True)
    reminder_time:          str | None = Field(default = "20:00", max_length = 5)
    default_view:           str = Field(default = "daily", max_length = 20)

    created_at:             datetime = Field(default_factory = lambda: datetime.now(timezone.utc))
    updated_at:             datetime = Field(default_factory = lambda: datetime.now(timezone.utc))


    @before_event([Replace, Update])
    async def update_timestamp(self) -> None:
        self.updated_at = datetime.now(timezone.utc)


    class Settings:

        name = "user_preferences"

        indexes = [
            IndexModel(
                [
                    ("user_id", ASCENDING)
                ],
                unique = True
            ),
        ]
