import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class Upload(Base, TimestampMixin):
    __tablename__ = "uploads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    sample_rate: Mapped[int] = mapped_column(Integer, nullable=False)
    channels: Mapped[int] = mapped_column(Integer, nullable=False)
    original_path: Mapped[str] = mapped_column(String(500), nullable=False)
    normalized_path: Mapped[str] = mapped_column(String(500), nullable=False)
    denoised: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    vad_segments: Mapped[list[dict]] = mapped_column(JSON, default=list, nullable=False)
    speaker_features: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    detected_language: Mapped[str | None] = mapped_column(String(16), nullable=True)
    prompt_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    speakers: Mapped[list["Speaker"]] = relationship(back_populates="upload")


class Speaker(Base, TimestampMixin):
    __tablename__ = "speakers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    favorite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    upload_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("uploads.id"), nullable=True)
    engine: Mapped[str] = mapped_column(String(50), default="cosyvoice2", nullable=False)
    voice_signature: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    upload: Mapped[Upload | None] = relationship(back_populates="speakers")
    generations: Mapped[list["Generation"]] = relationship(
        back_populates="speaker", cascade="all, delete-orphan"
    )


class Generation(Base, TimestampMixin):
    __tablename__ = "generations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    speaker_id: Mapped[str] = mapped_column(String(36), ForeignKey("speakers.id"), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(16), nullable=False)
    voice_similarity: Mapped[int] = mapped_column(Integer, default=80, nullable=False)
    emotion: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    emotion_label: Mapped[str] = mapped_column(String(32), default="Calm", nullable=False)
    speed: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    pitch: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    stability: Mapped[int] = mapped_column(Integer, default=75, nullable=False)
    output_format: Mapped[str] = mapped_column(String(10), default="wav", nullable=False)
    engine: Mapped[str] = mapped_column(String(50), default="cosyvoice2", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="completed", nullable=False)
    audio_path: Mapped[str] = mapped_column(String(500), nullable=False)
    meta: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    speaker: Mapped[Speaker] = relationship(back_populates="generations")
