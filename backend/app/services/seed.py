from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import Speaker


def seed_demo_data(db: Session) -> None:
    settings = get_settings()
    if not settings.seed_demo_content:
        return
    speaker_exists = db.scalar(select(Speaker.id).limit(1))
    if speaker_exists:
        return
