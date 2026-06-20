from __future__ import annotations

import sys
from pathlib import Path
from threading import Lock
from typing import Any

from app.core.config import get_settings


_model_lock = Lock()
_model_instance: Any | None = None


def ensure_cosyvoice_model() -> Any:
    global _model_instance
    if _model_instance is not None:
        return _model_instance

    with _model_lock:
        if _model_instance is not None:
            return _model_instance

        settings = get_settings()
        cosyvoice_root = Path(__file__).resolve().parents[2] / "third_party" / "CosyVoice"
        matcha_root = Path(__file__).resolve().parents[2] / "third_party" / "Matcha-TTS"
        whisper_root = Path(__file__).resolve().parents[2] / "third_party" / "whisper"
        if cosyvoice_root.exists() and str(cosyvoice_root) not in sys.path:
            sys.path.insert(0, str(cosyvoice_root))
        if matcha_root.exists() and str(matcha_root) not in sys.path:
            sys.path.insert(0, str(matcha_root))
        if whisper_root.exists() and str(whisper_root) not in sys.path:
            sys.path.insert(0, str(whisper_root))

        from cosyvoice.cli.cosyvoice import AutoModel

        model = AutoModel(
            model_dir=str(settings.cosyvoice_model_dir),
            load_jit=settings.cosyvoice_load_jit,
            load_trt=settings.cosyvoice_load_trt,
            load_vllm=settings.cosyvoice_load_vllm,
            fp16=settings.cosyvoice_fp16,
            trt_concurrent=settings.cosyvoice_trt_concurrent,
        )
        _model_instance = model
        return model


def cosyvoice_sample_rate() -> int:
    return int(ensure_cosyvoice_model().sample_rate)


def cosyvoice_model_dir() -> Path:
    return get_settings().cosyvoice_model_dir
