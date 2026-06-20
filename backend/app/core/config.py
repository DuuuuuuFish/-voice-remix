from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]
ROOT_DIR = BASE_DIR.parent
STORAGE_DIR = BASE_DIR / "storage"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(str(ROOT_DIR / ".env"), str(BASE_DIR / ".env")),
        env_file_encoding="utf-8",
        extra="ignore",
        protected_namespaces=("settings_",),
    )

    app_name: str = "AI Voice Clone Platform"
    app_env: Literal["development", "production", "test"] = "development"
    api_prefix: str = "/api"
    api_host: str = Field(default="0.0.0.0", validation_alias=AliasChoices("API_HOST", "api_host"))
    api_port: int = Field(default=8000, validation_alias=AliasChoices("API_PORT", "api_port"))
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"]
    )

    database_url: str = Field(
        default=f"sqlite:///{(STORAGE_DIR / 'voice_clone.db').as_posix()}",
        validation_alias=AliasChoices("DATABASE_URL", "database_url"),
    )
    storage_backend: Literal["local", "s3"] = "local"
    storage_dir: Path = Field(default=STORAGE_DIR, validation_alias=AliasChoices("STORAGE_PATH", "STORAGE_DIR", "storage_dir"))
    public_media_prefix: str = "/media"
    frontend_port: int = Field(default=3000, validation_alias=AliasChoices("FRONTEND_PORT", "frontend_port"))

    voice_engine: Literal["cosyvoice2", "xtts-v2"] = Field(default="cosyvoice2", validation_alias=AliasChoices("VOICE_ENGINE", "voice_engine"))
    max_upload_mb: int = Field(default=20, validation_alias=AliasChoices("MAX_UPLOAD_MB", "max_upload_mb"))
    max_reference_seconds: int = Field(default=30, validation_alias=AliasChoices("MAX_REFERENCE_SECONDS", "max_reference_seconds"))
    min_reference_seconds: int = Field(default=5, validation_alias=AliasChoices("MIN_REFERENCE_SECONDS", "min_reference_seconds"))
    default_language: str = "zh"
    cosyvoice_model_id: str = Field(default="iic/CosyVoice2-0.5B", validation_alias=AliasChoices("COSYVOICE_MODEL_ID", "cosyvoice_model_id"))
    cosyvoice_model_dir: Path = Field(
        default=BASE_DIR / "pretrained_models" / "CosyVoice2-0.5B",
        validation_alias=AliasChoices("MODEL_PATH", "COSYVOICE_MODEL_DIR", "cosyvoice_model_dir"),
    )
    cosyvoice_fp16: bool = True
    cosyvoice_load_jit: bool = False
    cosyvoice_load_trt: bool = False
    cosyvoice_load_vllm: bool = False
    cosyvoice_trt_concurrent: int = 1
    whisper_model_size: str = Field(default="small", validation_alias=AliasChoices("WHISPER_MODEL_SIZE", "whisper_model_size"))
    whisper_model_id: str = Field(default="Systran/faster-whisper-small", validation_alias=AliasChoices("WHISPER_MODEL_ID", "whisper_model_id"))
    whisper_model_dir: Path = Field(
        default=BASE_DIR / "pretrained_models" / "faster-whisper-small",
        validation_alias=AliasChoices("WHISPER_MODEL_PATH", "WHISPER_MODEL_DIR", "whisper_model_dir"),
    )
    model_source: Literal["modelscope", "huggingface"] = Field(default="modelscope", validation_alias=AliasChoices("MODEL_SOURCE", "model_source"))

    s3_endpoint: str | None = None
    s3_bucket: str | None = None
    s3_access_key: str | None = None
    s3_secret_key: str | None = None
    s3_region: str | None = None

    seed_demo_content: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
