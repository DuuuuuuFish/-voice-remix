from __future__ import annotations

import uuid
from pathlib import Path

import librosa
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import SessionLocal, get_db
from app.models import Generation, Speaker, Upload
from app.schemas.common import ApiMessage
from app.schemas.generation import GenerationRequest, GenerationResponse
from app.schemas.speaker import SpeakerCreateRequest, SpeakerResponse, SpeakerUpdateRequest
from app.schemas.upload import UploadResponse
from app.services.storage import LocalStorageService
from app.services.transcription import transcribe_reference_audio
from app.services.voice_engine import get_voice_engine
from app.utils.audio import (
    build_voice_signature,
    detect_vad_segments,
    extract_speaker_features,
    merge_voice_signatures,
    normalize_audio,
    probe_audio,
)


router = APIRouter()
settings = get_settings()
storage = LocalStorageService()


def run_upload_transcription(upload_id: str, normalized_path: str) -> None:
    try:
        transcription = transcribe_reference_audio(Path(normalized_path))
        with SessionLocal() as db:
            upload = db.get(Upload, upload_id)
            if not upload:
                return
            upload.detected_language = transcription["language"]
            upload.prompt_text = transcription["text"] or ""
            db.add(upload)
            db.commit()
    except Exception as exc:
        print(f"transcription failed for upload {upload_id}: {exc}")


def to_upload_response(item: Upload) -> UploadResponse:
    return UploadResponse(
        id=item.id,
        original_filename=item.original_filename,
        content_type=item.content_type,
        size_bytes=item.size_bytes,
        duration_seconds=item.duration_seconds,
        sample_rate=item.sample_rate,
        channels=item.channels,
        denoised=item.denoised,
        vad_segments=item.vad_segments,
        speaker_features=item.speaker_features,
        detected_language=item.detected_language,
        prompt_text=item.prompt_text,
        normalized_media_url=storage.media_url(Path(item.normalized_path)),
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def to_speaker_response(item: Speaker) -> SpeakerResponse:
    return SpeakerResponse(
        id=item.id,
        name=item.name,
        favorite=item.favorite,
        upload_id=item.upload_id,
        engine=item.engine,
        voice_signature=item.voice_signature,
        notes=item.notes,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def to_generation_response(item: Generation, speaker: Speaker) -> GenerationResponse:
    return GenerationResponse(
        id=item.id,
        speaker=to_speaker_response(speaker),
        text=item.text,
        language=item.language,
        voice_similarity=item.voice_similarity,
        emotion=item.emotion,
        emotion_label=item.emotion_label,
        speed=item.speed,
        pitch=item.pitch,
        stability=item.stability,
        output_format=item.output_format,
        engine=item.engine,
        status=item.status,
        audio_url=storage.media_url(Path(item.audio_path)),
        meta=item.meta,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.get("/health", response_model=ApiMessage)
def healthcheck() -> ApiMessage:
    return ApiMessage(message="ok")


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_reference(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> UploadResponse:
    print("upload received", flush=True)
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".wav", ".mp3", ".m4a"}:
        raise HTTPException(status_code=400, detail="仅支持 wav、mp3、m4a 格式。")

    content = await file.read()
    size_bytes = len(content)
    if size_bytes > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"文件超过 {settings.max_upload_mb}MB 限制。")

    file.file.seek(0)
    upload_id = str(uuid.uuid4())
    original_path = settings.storage_dir / "uploads" / f"{upload_id}{suffix}"
    normalized_path = settings.storage_dir / "uploads" / f"{upload_id}-normalized.wav"
    storage.save_upload(file, original_path)
    print("file saved", flush=True)
    print("normalizing audio", flush=True)
    try:
        normalize_audio(original_path, normalized_path)
    except Exception as e:
        print("audio decode failed", e, flush=True)
        raise HTTPException(status_code=400, detail=str(e)) from e
    print("audio normalized", flush=True)

    metadata = probe_audio(normalized_path)
    if metadata["duration_seconds"] < settings.min_reference_seconds:
        raise HTTPException(status_code=400, detail=f"参考音频长度不能少于 {settings.min_reference_seconds} 秒。")
    if metadata["duration_seconds"] > settings.max_reference_seconds:
        raise HTTPException(status_code=400, detail=f"参考音频长度不能超过 {settings.max_reference_seconds} 秒。")

    normalized_audio, normalized_sr = librosa.load(str(normalized_path), sr=22050, mono=True)
    vad_segments = detect_vad_segments(normalized_path, audio=normalized_audio, sr=normalized_sr)
    features = extract_speaker_features(normalized_path, audio=normalized_audio, sr=normalized_sr)
    print("speaker feature extracted", flush=True)

    upload = Upload(
        id=upload_id,
        original_filename=file.filename or original_path.name,
        content_type=file.content_type or "application/octet-stream",
        size_bytes=size_bytes,
        duration_seconds=metadata["duration_seconds"],
        sample_rate=metadata["sample_rate"],
        channels=metadata["channels"],
        original_path=str(original_path),
        normalized_path=str(normalized_path),
        denoised=True,
        vad_segments=vad_segments,
        speaker_features=features,
        detected_language=None,
        prompt_text="",
    )
    db.add(upload)
    db.commit()
    db.refresh(upload)
    background_tasks.add_task(run_upload_transcription, upload.id, str(normalized_path))
    print("upload completed", flush=True)
    return to_upload_response(upload)


@router.post("/clone", response_model=SpeakerResponse, status_code=status.HTTP_201_CREATED)
def create_speaker(request: SpeakerCreateRequest, db: Session = Depends(get_db)) -> SpeakerResponse:
    signature: dict
    upload_id: str | None = request.upload_id

    if request.base_speaker_id:
        base = db.get(Speaker, request.base_speaker_id)
        if not base:
            raise HTTPException(status_code=404, detail="未找到基础音色。")
        signature = dict(base.voice_signature)
        upload_id = base.upload_id
    elif request.upload_id:
        upload = db.get(Upload, request.upload_id)
        if not upload:
            raise HTTPException(status_code=404, detail="未找到上传记录。")
        signature = build_voice_signature(upload.speaker_features)
    else:
        raise HTTPException(status_code=400, detail="必须提供 upload_id 或 base_speaker_id。")

    if request.mix_with_speaker_id:
        secondary = db.get(Speaker, request.mix_with_speaker_id)
        if not secondary:
            raise HTTPException(status_code=404, detail="未找到要混合的第二音色。")
        signature = merge_voice_signatures(signature, secondary.voice_signature, request.mix_ratio_primary)

    speaker = Speaker(
        name=request.name,
        favorite=request.favorite,
        upload_id=upload_id,
        engine=settings.voice_engine,
        voice_signature=signature,
        notes=request.notes,
    )
    db.add(speaker)
    db.commit()
    db.refresh(speaker)
    return to_speaker_response(speaker)


@router.get("/speakers", response_model=list[SpeakerResponse])
def list_speakers(db: Session = Depends(get_db)) -> list[SpeakerResponse]:
    items = db.scalars(select(Speaker).order_by(desc(Speaker.favorite), desc(Speaker.created_at))).all()
    return [to_speaker_response(item) for item in items]


@router.patch("/speakers/{speaker_id}", response_model=SpeakerResponse)
def update_speaker(speaker_id: str, request: SpeakerUpdateRequest, db: Session = Depends(get_db)) -> SpeakerResponse:
    speaker = db.get(Speaker, speaker_id)
    if not speaker:
        raise HTTPException(status_code=404, detail="未找到音色。")
    payload = request.model_dump(exclude_none=True)
    for key, value in payload.items():
        setattr(speaker, key, value)
    db.add(speaker)
    db.commit()
    db.refresh(speaker)
    return to_speaker_response(speaker)


@router.delete("/speakers/{speaker_id}", response_model=ApiMessage)
def delete_speaker(speaker_id: str, db: Session = Depends(get_db)) -> ApiMessage:
    speaker = db.get(Speaker, speaker_id)
    if not speaker:
        raise HTTPException(status_code=404, detail="未找到音色。")
    for generation in speaker.generations:
        Path(generation.audio_path).unlink(missing_ok=True)
    db.delete(speaker)
    db.commit()
    return ApiMessage(message="Speaker deleted.")


@router.post("/generate", response_model=GenerationResponse, status_code=status.HTTP_201_CREATED)
def generate_audio(request: GenerationRequest, db: Session = Depends(get_db)) -> GenerationResponse:
    speaker = db.get(Speaker, request.speaker_id)
    if not speaker:
        raise HTTPException(status_code=404, detail="未找到音色。")

    output_name = f"{uuid.uuid4()}.{request.output_format}"
    output_path = settings.storage_dir / "generated" / output_name
    engine = get_voice_engine()
    try:
        upload = speaker.upload if speaker.upload_id else None
        render = engine.render(
            text=request.text,
            language=request.language,
            output_path=output_path,
            voice_signature=speaker.voice_signature,
            prompt_path=Path(upload.normalized_path) if upload else None,
            prompt_text=upload.prompt_text if upload else None,
            prompt_language=upload.detected_language if upload else None,
            speed=request.speed,
            pitch=request.pitch,
            emotion=request.emotion,
            emotion_label=request.emotion_label,
            voice_similarity=request.voice_similarity,
            stability=request.stability,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    generation = Generation(
        speaker_id=speaker.id,
        text=request.text,
        language=request.language,
        voice_similarity=request.voice_similarity,
        emotion=request.emotion,
        emotion_label=request.emotion_label,
        speed=request.speed,
        pitch=request.pitch,
        stability=request.stability,
        output_format=request.output_format,
        engine=engine.name,
        status="completed",
        audio_path=str(render.output_path),
        meta=render.metadata,
    )
    db.add(generation)
    db.commit()
    db.refresh(generation)
    return to_generation_response(generation, speaker)


@router.get("/generate/stream/{generation_id}")
def stream_generation(generation_id: str, db: Session = Depends(get_db)) -> StreamingResponse:
    generation = db.get(Generation, generation_id)
    if not generation:
        raise HTTPException(status_code=404, detail="未找到生成记录。")
    path = Path(generation.audio_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="音频文件不存在。")

    def iterfile():
        with path.open("rb") as handle:
            while chunk := handle.read(8192):
                yield chunk

    media_type = "audio/mpeg" if path.suffix == ".mp3" else "audio/wav"
    return StreamingResponse(iterfile(), media_type=media_type)


@router.get("/history", response_model=list[GenerationResponse])
def get_history(db: Session = Depends(get_db)) -> list[GenerationResponse]:
    rows = db.execute(
        select(Generation, Speaker).join(Speaker, Generation.speaker_id == Speaker.id).order_by(desc(Generation.created_at))
    ).all()
    return [to_generation_response(generation, speaker) for generation, speaker in rows]


@router.get("/history/{generation_id}/download")
def download_history_audio(generation_id: str, db: Session = Depends(get_db)) -> FileResponse:
    generation = db.get(Generation, generation_id)
    if not generation:
        raise HTTPException(status_code=404, detail="未找到历史记录。")
    path = Path(generation.audio_path)
    return FileResponse(path, media_type="application/octet-stream", filename=path.name)


@router.post("/history/{generation_id}/regenerate", response_model=GenerationResponse, status_code=status.HTTP_201_CREATED)
def regenerate_history(generation_id: str, db: Session = Depends(get_db)) -> GenerationResponse:
    previous = db.get(Generation, generation_id)
    if not previous:
        raise HTTPException(status_code=404, detail="未找到历史记录。")
    request = GenerationRequest(
        speaker_id=previous.speaker_id,
        text=previous.text,
        language=previous.language,
        voice_similarity=previous.voice_similarity,
        emotion=previous.emotion,
        emotion_label=previous.emotion_label,
        speed=previous.speed,
        pitch=previous.pitch,
        stability=previous.stability,
        output_format=previous.output_format,
    )
    return generate_audio(request, db)


@router.delete("/history/{generation_id}", response_model=ApiMessage)
def delete_history(generation_id: str, db: Session = Depends(get_db)) -> ApiMessage:
    generation = db.get(Generation, generation_id)
    if not generation:
        raise HTTPException(status_code=404, detail="未找到历史记录。")
    path = Path(generation.audio_path)
    db.delete(generation)
    db.commit()
    path.unlink(missing_ok=True)
    return ApiMessage(message="History deleted.")
