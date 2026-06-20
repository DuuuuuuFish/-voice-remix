from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import UploadFile

from app.core.config import get_settings


class LocalStorageService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_dir = self.settings.storage_dir

    def ensure_directories(self) -> None:
        for folder in ("uploads", "generated", "voices"):
            (self.base_dir / folder).mkdir(parents=True, exist_ok=True)

    def save_upload(self, upload_file: UploadFile, target_path: Path) -> None:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with target_path.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)

    def media_url(self, absolute_path: Path) -> str:
        relative = absolute_path.relative_to(self.base_dir).as_posix()
        return f"{self.settings.public_media_prefix}/{relative}"
