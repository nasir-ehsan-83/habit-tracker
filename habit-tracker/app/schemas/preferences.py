from typing import Any
from datetime import datetime
from pydantic import (
    BaseModel,
    ConfigDict, 
    Field,
    field_validator
)




class PreferenceOut(BaseModel):

    id:                     str = Field(alias = "_id")
    theme:                  str
    language:               str
    timezone:               str
    start_of_week:          str
    notifications_enabled:  bool
    reminder_time:          str | None
    default_view:           str
    created_at:             datetime
    updated_at:             datetime

    model_config = ConfigDict(
        from_attributes = True, 
        populate_by_name = True
    )


    @field_validator("id", mode = "before")
    @classmethod
    def convert_objectid(cls, v: Any) -> str:
        return str(v)




class PreferenceUpdate(BaseModel):

    theme:                  str | None = Field(default = None, max_length = 20)
    language:               str | None = Field(default = None, max_length = 10)
    timezone:               str | None = Field(default = None, max_length = 50)
    start_of_week:          str | None = Field(default = None, max_length = 20)
    notifications_enabled:  bool | None = Field(default = None)
    reminder_time:          str | None = Field(default = None, max_length = 5)
    default_view:           str | None = Field(default = None, max_length = 20)
