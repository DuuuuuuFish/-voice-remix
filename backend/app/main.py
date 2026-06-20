from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.core.config import get_settings
from app.db.base import Base
from app.db.migrate import run_startup_migrations
from app.db.session import SessionLocal, engine
from app.services.model_manager import ensure_cosyvoice_model
from app.services.seed import seed_demo_data
from app.services.storage import LocalStorageService


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    storage = LocalStorageService()
    storage.ensure_directories()
    settings.cosyvoice_model_dir.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    run_startup_migrations()
    ensure_cosyvoice_model()
    with SessionLocal() as db:
        seed_demo_data(db)

    app.include_router(router, prefix=settings.api_prefix)
    app.mount(settings.public_media_prefix, StaticFiles(directory=Path(settings.storage_dir)), name="media")
    return app


app = create_app()
