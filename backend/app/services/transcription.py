from __future__ import annotations

from pathlib import Path

from faster_whisper import WhisperModel
from huggingface_hub import snapshot_download

from app.core.config import get_settings


SUPPORTED_UPLOAD_LANGUAGES = {"zh", "en", "ja", "ko", "fr", "de", "es"}
_whisper_model: WhisperModel | None = None


def _get_model() -> WhisperModel:
    global _whisper_model
    if _whisper_model is None:
        settings = get_settings()
        model_dir = settings.whisper_model_dir
        model_dir.mkdir(parents=True, exist_ok=True)
        if not (model_dir / "model.bin").exists():
            snapshot_download(repo_id=settings.whisper_model_id, local_dir=str(model_dir))
        _whisper_model = WhisperModel(str(model_dir), device="cpu", compute_type="int8")
    return _whisper_model


def transcribe_reference_audio(path: Path) -> dict:
    try:
        model = _get_model()
        segments, info = model.transcribe(str(path), language=None, vad_filter=True)
        text = " ".join(segment.text.strip() for segment in segments).strip()
        language = info.language
    except Exception:
        return {
            "language": None,
            "text": "",
            "segments": [],
        }

    if language not in SUPPORTED_UPLOAD_LANGUAGES:
        language = "zh" if language in {"yue", "zh-cn", "zh-tw"} else (language or "zh")
    return {
        "language": language,
        "text": text,
        "segments": [],
    }
