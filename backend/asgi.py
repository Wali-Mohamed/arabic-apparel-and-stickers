"""Vercel backend service entrypoint; repository root owns public routing."""
import os

os.environ.setdefault("APP_ENV", "production")

# No connect/migrate/seed operation on import or request startup.
from app.main import app  # noqa: E402, F401
