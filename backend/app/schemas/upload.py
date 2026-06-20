from pydantic import BaseModel

from app.schemas.common import TimestampedModel


class UploadResponse(TimestampedModel):
    id: str
    original_filename: str
    content_type: str
    size_bytes: int
    duration_seconds: float
    sample_rate: int
    channels: int
    denoised: bool
    vad_segments: list[dict]
    speaker_features: dict
    detected_language: str | None
    prompt_text: str | None
    normalized_media_url: str
