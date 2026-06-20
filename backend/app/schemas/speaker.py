from pydantic import BaseModel, Field

from app.schemas.common import TimestampedModel


class SpeakerCreateRequest(BaseModel):
    upload_id: str | None = None
    name: str = Field(min_length=2, max_length=255)
    favorite: bool = False
    base_speaker_id: str | None = None
    mix_with_speaker_id: str | None = None
    mix_ratio_primary: int = Field(default=70, ge=0, le=100)
    notes: str | None = None


class SpeakerUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    favorite: bool | None = None
    notes: str | None = None


class SpeakerResponse(TimestampedModel):
    id: str
    name: str
    favorite: bool
    upload_id: str | None
    engine: str
    voice_signature: dict
    notes: str | None
