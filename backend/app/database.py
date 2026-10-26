import os
from collections.abc import Generator

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import Session, sessionmaker

if os.getenv("APP_ENV") == "production" and not (
    os.getenv("DATABASE_URL") or os.getenv("POSTGRES_PASSWORD")
):
    raise RuntimeError("Production database credentials are required")

DATABASE_URL = os.getenv("DATABASE_URL") or URL.create(
    "postgresql+psycopg",
    username=os.getenv("POSTGRES_USER", "apparel"),
    password=os.getenv("POSTGRES_PASSWORD", "apparel"),
    host=os.getenv("POSTGRES_HOST", "localhost"),
    database=os.getenv("POSTGRES_DB", "apparel"),
).render_as_string(hide_password=False)

engine = create_engine(DATABASE_URL, pool_pre_ping=True, hide_parameters=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    """Yield a session for request handlers and always close it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
