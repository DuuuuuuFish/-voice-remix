from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
import torchaudio

from app.core.config import get_settings
from app.services.model_manager import ensure_cosyvoice_model
from app.utils.audio import concat_audio_segments, save_waveform


LANGUAGE_TOKEN = {
    "zh": "<|zh|>",
    "en": "<|en|>",
    "ja": "<|ja|>",
    "ko": "<|ko|>",
    "fr": "<|fr|>",
    "de": "<|de|>",
    "es": "<|es|>",
}


@dataclass
class VoiceRenderResult:
    output_path: Path
    metadata: dict


class BaseVoiceEngine:
    name = "base"

    def render(
        self,
        *,
        text: str,
        language: str,
        output_path: Path,
        voice_signature: dict,
        prompt_path: Path | None,
        prompt_text: str | None,
        prompt_language: str | None,
        speed: float,
        pitch: int,
        emotion: int,
        emotion_label: str,
        voice_similarity: int,
        stability: int,
    ) -> VoiceRenderResult:
        raise NotImplementedError


class XTTSVoiceEngine(BaseVoiceEngine):
    name = "xtts-v2"

    def render(self, **kwargs) -> VoiceRenderResult:  # type: ignore[override]
        raise RuntimeError("XTTS-v2 is not enabled in this build. Use VOICE_ENGINE=cosyvoice2.")


class CosyVoice2Engine(BaseVoiceEngine):
    name = "cosyvoice2"

    def _split_user_segments(self, text: str) -> list[str]:
        # Users can force sentence boundaries with line breaks.
        segments = [segment.strip() for segment in text.splitlines() if segment.strip()]
        return segments or [text.strip()]

    def _build_target_text(self, text: str, language: str, prompt_language: str | None) -> tuple[str, str]:
        cross_lingual = prompt_language is not None and prompt_language != language
        if cross_lingual:
            return f"{LANGUAGE_TOKEN[language]}{text}", "cross_lingual"
        return text, "zero_shot"

    def render(
        self,
        *,
        text: str,
        language: str,
        output_path: Path,
        voice_signature: dict,
        prompt_path: Path | None,
        prompt_text: str | None,
        prompt_language: str | None,
        speed: float,
        pitch: int,
        emotion: int,
        emotion_label: str,
        voice_similarity: int,
        stability: int,
    ) -> VoiceRenderResult:
        if prompt_path is None or not prompt_path.exists():
            raise RuntimeError("Prompt audio is required for CosyVoice2 zero-shot cloning.")

        model = ensure_cosyvoice_model()
        text_segments = self._split_user_segments(text)
        mode = "cross_lingual" if not prompt_text else self._build_target_text(text_segments[0], language, prompt_language)[1]
        speed_value = max(0.5, min(2.0, speed))

        segments: list[np.ndarray] = []
        for raw_text in text_segments:
            target_text, segment_mode = self._build_target_text(raw_text, language, prompt_language)
            if not prompt_text:
                target_text = f"{LANGUAGE_TOKEN[language]}{raw_text}"
                segment_mode = "cross_lingual"

            if segment_mode == "cross_lingual":
                output_iter = model.inference_cross_lingual(
                    target_text,
                    str(prompt_path),
                    stream=False,
                    speed=speed_value,
                    text_frontend=False,
                )
            else:
                output_iter = model.inference_zero_shot(
                    target_text,
                    prompt_text,
                    str(prompt_path),
                    stream=False,
                    speed=speed_value,
                    text_frontend=False,
                )

            for item in output_iter:
                speech = item["tts_speech"]
                if isinstance(speech, torch.Tensor):
                    segments.append(speech.detach().cpu().numpy())
                else:
                    segments.append(np.asarray(speech))

        waveform = concat_audio_segments(segments)
        save_waveform(output_path, waveform, int(model.sample_rate))
        duration_seconds = round(waveform.shape[-1] / int(model.sample_rate), 3)
        return VoiceRenderResult(
            output_path=output_path,
            metadata={
                "mode": mode,
                "sample_rate": int(model.sample_rate),
                "duration_seconds": duration_seconds,
                "speed": speed_value,
                "prompt_language": prompt_language,
                "target_language": language,
                "emotion_label": emotion_label,
                "voice_similarity": voice_similarity,
                "stability": stability,
                "pitch": pitch,
                "emotion": emotion,
                "segment_count": len(text_segments),
            },
        )


def get_voice_engine() -> BaseVoiceEngine:
    engine_name = get_settings().voice_engine
    if engine_name == "xtts-v2":
        return XTTSVoiceEngine()
    return CosyVoice2Engine()
