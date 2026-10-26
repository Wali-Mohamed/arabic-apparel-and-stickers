from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db_config import database_url, engine_options

connection_url = database_url()
DATABASE_URL = connection_url.render_as_string(hide_password=False)

engine = create_engine(connection_url, **engine_options(connection_url))
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    """Yield a session for request handlers and always close it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
