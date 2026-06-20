from __future__ import annotations

import argparse
from pathlib import Path


def download_from_modelscope(model_id: str, target_dir: Path) -> None:
    from modelscope import snapshot_download

    snapshot_download(model_id, local_dir=str(target_dir))


def download_from_huggingface(model_id: str, target_dir: Path) -> None:
    from huggingface_hub import snapshot_download

    snapshot_download(repo_id=model_id, local_dir=str(target_dir))


def download_whisper_from_huggingface(model_id: str, target_dir: Path) -> None:
    from huggingface_hub import snapshot_download

    snapshot_download(repo_id=model_id, local_dir=str(target_dir))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=["modelscope", "huggingface"], default="modelscope")
    parser.add_argument("--model-id", default="iic/CosyVoice2-0.5B")
    parser.add_argument("--hf-model-id", default="FunAudioLLM/CosyVoice2-0.5B")
    parser.add_argument("--target-dir", default="/app/pretrained_models/CosyVoice2-0.5B")
    parser.add_argument("--download-whisper", action="store_true")
    parser.add_argument("--whisper-model-id", default="Systran/faster-whisper-small")
    parser.add_argument("--whisper-target-dir", default="/app/pretrained_models/faster-whisper-small")
    args = parser.parse_args()

    target_dir = Path(args.target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    marker = target_dir / "cosyvoice2.yaml"
    if marker.exists():
        print(f"Model already exists at {target_dir}")
        return

    if args.source == "modelscope":
        download_from_modelscope(args.model_id, target_dir)
    else:
        download_from_huggingface(args.hf_model_id, target_dir)
    print(f"Model downloaded to {target_dir}")

    if args.download_whisper:
        whisper_dir = Path(args.whisper_target_dir)
        whisper_dir.mkdir(parents=True, exist_ok=True)
        whisper_marker = whisper_dir / "model.bin"
        if not whisper_marker.exists():
            download_whisper_from_huggingface(args.whisper_model_id, whisper_dir)
        print(f"Whisper model prepared at {whisper_dir}")


if __name__ == "__main__":
    main()
