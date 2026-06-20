from pydantic import BaseModel, Field

from app.schemas.common import TimestampedModel
from app.schemas.speaker import SpeakerResponse


class GenerationRequest(BaseModel):
    speaker_id: str
    text: str = Field(min_length=1, max_length=2000)
    language: str = Field(pattern="^(zh|en|ja|ko|fr|de|es)$")
    voice_similarity: int = Field(default=80, ge=0, le=100)
    emotion: int = Field(default=50, ge=0, le=100)
    emotion_label: str = Field(default="Calm", pattern="^(Happy|Sad|Excited|Calm|Serious)$")
    speed: float = Field(default=1.0, ge=0.5, le=2.0)
    pitch: int = Field(default=0, ge=-12, le=12)
    stability: int = Field(default=75, ge=0, le=100)
    output_format: str = Field(default="wav", pattern="^(wav)$")


class GenerationResponse(TimestampedModel):
    id: str
    speaker: SpeakerResponse
    text: str
    language: str
    voice_similarity: int
    emotion: int
    emotion_label: str
    speed: float
    pitch: int
    stability: int
    output_format: str
    engine: str
    status: str
    audio_url: str
    meta: dict
