from datetime import datetime

from pydantic import BaseModel


class ApiMessage(BaseModel):
    message: str


class TimestampedModel(BaseModel):
    created_at: datetime
    updated_at: datetime
