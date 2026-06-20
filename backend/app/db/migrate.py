from sqlalchemy import inspect, text

from app.db.session import engine


def run_startup_migrations() -> None:
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    if "uploads" in tables:
        columns = {column["name"] for column in inspector.get_columns("uploads")}
        with engine.begin() as connection:
            if "detected_language" not in columns:
                connection.execute(text("ALTER TABLE uploads ADD COLUMN detected_language VARCHAR(16)"))
            if "prompt_text" not in columns:
                connection.execute(text("ALTER TABLE uploads ADD COLUMN prompt_text TEXT"))
