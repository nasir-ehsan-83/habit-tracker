from datetime import (
    datetime,
    timezone
)
from beanie import (
    Document, 
    BeanieObjectId
)
from pymongo import (
    ASCENDING,
    IndexModel
)
from pydantic import Field



class Track(Document):

    user_id:        BeanieObjectId
    habit_id:       BeanieObjectId
    note:           str | None
    value:          int

    created_at:     datetime = Field(default_factory = lambda: datetime.now(timezone.utc))
    updated_at:     datetime = Field(default_factory = lambda: datetime.now(timezone.utc))


    class Settings:

        name = "tracks"

        indexes = [
            IndexModel(
                [
                    ("user_id", ASCENDING),
                    ("habit_id", ASCENDING)
                ],
                unique = True
            ),
        ]