"""Connection configuration only: parsing this module never opens a socket."""
import os
from collections.abc import Mapping
from typing import Any

from sqlalchemy import URL
from sqlalchemy.engine import make_url
from sqlalchemy.pool import NullPool


def is_neon(url: URL) -> bool:
    return (url.host or "").lower().endswith(".neon.tech")


def is_pooled(url: URL) -> bool:
    return (url.host or "").split(".")[0].endswith("-pooler")


def database_url(*, migration: bool = False, env: Mapping[str, str] | None = None) -> URL:
    settings = os.environ if env is None else env
    raw = settings.get("MIGRATION_DATABASE_URL") if migration else None
    raw = raw or settings.get("DATABASE_URL")
    if raw:
        try:
            url = make_url(raw)
        except Exception:
            # URL parse errors may embed credentials; never include raw input.
            raise ValueError("Invalid database URL configuration") from None
        if url.drivername in {"postgres", "postgresql"}:
            url = url.set(drivername="postgresql+psycopg")
        if url.drivername != "postgresql+psycopg":
            raise ValueError("Database URL must use the PostgreSQL psycopg driver")
    else:
        if settings.get("APP_ENV") == "production" and not settings.get("POSTGRES_PASSWORD"):
            raise ValueError("Production database credentials are required")
        url = URL.create(
            "postgresql+psycopg", username=settings.get("POSTGRES_USER", "apparel"),
            password=settings.get("POSTGRES_PASSWORD", "apparel"),
            host=settings.get("POSTGRES_HOST", "localhost"),
            database=settings.get("POSTGRES_DB", "apparel"),
        )
    if is_neon(url) or settings.get("DATABASE_SSL_REQUIRED") == "1":
        sslmode = url.query.get("sslmode", "require")
        if sslmode not in {"require", "verify-ca", "verify-full"}:
            raise ValueError("Remote database SSL must not be disabled or downgraded")
        url = url.update_query_dict({"sslmode": sslmode})
    if migration and is_pooled(url):
        raise ValueError("Migrations require a direct connection, not a pooler endpoint")
    if migration and is_neon(url) and not settings.get("MIGRATION_DATABASE_URL"):
        raise ValueError("Set MIGRATION_DATABASE_URL explicitly for Neon migrations")
    return url


def engine_options(url: URL, env: Mapping[str, str] | None = None) -> dict[str, Any]:
    settings = os.environ if env is None else env
    mode = settings.get("DATABASE_POOL_MODE", "null" if settings.get("VERCEL") == "1" or is_pooled(url) else "queue")
    if mode not in {"null", "queue"}:
        raise ValueError("DATABASE_POOL_MODE must be null or queue")
    options: dict[str, Any] = {"pool_pre_ping": True, "hide_parameters": True}
    if mode == "null":
        options["poolclass"] = NullPool
    if is_neon(url) or settings.get("VERCEL") == "1":
        options["connect_args"] = {"connect_timeout": 10}
    if is_pooled(url):
        # Conservative for the pinned psycopg/libpq versions under transaction
        # pooling. Neon supports protocol prepared statements, but we do not
        # depend on session state or automatic server-side preparation here.
        options.setdefault("connect_args", {})["prepare_threshold"] = None
    return options
