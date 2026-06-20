from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import av
import librosa
import numpy as np
import soundfile as sf


def run_command(command: list[str]) -> None:
    process = subprocess.run(command, capture_output=True, text=True)
    if process.returncode != 0:
        raise RuntimeError(process.stderr.strip() or "Command execution failed")


def _has_command(name: str) -> bool:
    return shutil.which(name) is not None


def _requires_ffmpeg(source: Path) -> bool:
    return source.suffix.lower() in {".m4a", ".mp3"}


def _decode_with_pyav(source: Path, target_sr: int = 16000) -> np.ndarray:
    chunks: list[np.ndarray] = []
    with av.open(str(source)) as container:
        resampler = av.audio.resampler.AudioResampler(format="s16", layout="mono", rate=target_sr)
        for frame in container.decode(audio=0):
            resampled = resampler.resample(frame)
            if not isinstance(resampled, list):
                resampled = [resampled]
            for out_frame in resampled:
                if out_frame is None:
                    continue
                data = out_frame.to_ndarray()
                if data.ndim == 2:
                    data = data[0]
                chunks.append(data.astype(np.float32) / 32768.0)
    if not chunks:
        raise RuntimeError(f"Cannot decode audio file: {source.name}")
    return np.concatenate(chunks)


def probe_audio(path: Path) -> dict:
    info = sf.info(str(path))
    return {
        "duration_seconds": float(info.duration),
        "sample_rate": int(info.samplerate),
        "channels": int(info.channels),
    }


def normalize_audio(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)

    if _has_command("ffmpeg"):
        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(source),
            "-ac",
            "1",
            "-ar",
            "16000",
            "-c:a",
            "pcm_s16le",
            str(target),
        ]
        run_command(command)
        return

    if _requires_ffmpeg(source):
        audio = _decode_with_pyav(source, target_sr=16000)
        peak = float(np.max(np.abs(audio))) if len(audio) else 0.0
        if peak > 0:
            audio = 0.95 * (audio / peak)
        sf.write(str(target), audio, 16000, subtype="PCM_16")
        return

    # WAV fallback when ffmpeg is unavailable.
    audio, _ = librosa.load(str(source), sr=16000, mono=True)
    peak = float(np.max(np.abs(audio))) if len(audio) else 0.0
    if peak > 0:
        audio = 0.95 * (audio / peak)
    sf.write(str(target), audio, 16000, subtype="PCM_16")


def detect_vad_segments(path: Path, audio: np.ndarray | None = None, sr: int = 16000) -> list[dict]:
    if audio is None:
        audio, sr = librosa.load(path, sr=sr, mono=True)
    intervals = librosa.effects.split(audio, top_db=25)
    segments: list[dict] = []
    for start, end in intervals:
        segments.append({"start": round(start / sr, 3), "end": round(end / sr, 3)})
    return segments


def extract_speaker_features(path: Path, audio: np.ndarray | None = None, sr: int = 16000) -> dict:
    if audio is None:
        audio, sr = librosa.load(path, sr=sr, mono=True)

    centroid = librosa.feature.spectral_centroid(y=audio, sr=sr).mean()
    bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sr).mean()
    rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr).mean()
    zcr = librosa.feature.zero_crossing_rate(y=audio).mean()
    rms = librosa.feature.rms(y=audio).mean()

    try:
        f0 = librosa.yin(audio, fmin=60, fmax=400, sr=sr)
        f0 = f0[np.isfinite(f0)]
        pitch_hz = float(f0.mean()) if len(f0) else 180.0
    except Exception:
        pitch_hz = 180.0

    return {
        "pitch_hz": round(pitch_hz, 2),
        "brightness": round(float(centroid / 4000), 4),
        "bandwidth": round(float(bandwidth / 5000), 4),
        "rolloff": round(float(rolloff / 8000), 4),
        "energy": round(float(rms), 4),
        "zcr": round(float(zcr), 4),
    }


def build_voice_signature(features: dict) -> dict:
    pitch_hz = features.get("pitch_hz", 180.0)
    brightness = features.get("brightness", 0.5)
    speed_hint = max(0.82, min(1.18, 0.9 + features.get("energy", 0.1) * 1.8))
    return {
        "brightness": brightness,
        "pitch_hz": pitch_hz,
        "speed_hint": round(speed_hint, 2),
        "voice_family": "captured-reference",
    }


def merge_voice_signatures(primary: dict, secondary: dict, ratio_primary: int) -> dict:
    alpha = ratio_primary / 100
    merged: dict[str, float | str] = {}
    numeric_keys = {"brightness", "pitch_hz", "speed_hint"}
    for key in numeric_keys:
        first = float(primary.get(key, 0))
        second = float(secondary.get(key, 0))
        merged[key] = round(first * alpha + second * (1 - alpha), 3)
    merged["voice_family"] = f"mix-{ratio_primary}-{100 - ratio_primary}"
    return merged


def concat_audio_segments(segments: list[np.ndarray]) -> np.ndarray:
    if not segments:
        return np.zeros((1, 1), dtype=np.float32)
    prepared = []
    for segment in segments:
        if segment.ndim == 1:
            prepared.append(segment[np.newaxis, :].astype(np.float32))
        else:
            prepared.append(segment.astype(np.float32))
    return np.concatenate(prepared, axis=1)


def save_waveform(path: Path, waveform: np.ndarray, sample_rate: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if waveform.ndim == 2 and waveform.shape[0] == 1:
        data = waveform[0]
    elif waveform.ndim == 2:
        data = waveform.T
    else:
        data = waveform
    sf.write(path, data, sample_rate)
