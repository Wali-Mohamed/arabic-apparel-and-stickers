import os
import subprocess
import sys

import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool, QueuePool

from app.db_config import database_url, engine_options
import migrate_neon


def test_local_defaults_and_special_password_preserve_docker_behavior():
    url = database_url(env={"POSTGRES_HOST": "postgres", "POSTGRES_PASSWORD": "synthetic%@/:"})
    assert url.drivername == "postgresql+psycopg"
    assert url.host == "postgres"
    assert url.password == "synthetic%@/:"
    assert "sslmode" not in url.query
    engine = create_engine(url, **engine_options(url, env={}))
    assert isinstance(engine.pool, QueuePool)
    engine.dispose()


@pytest.mark.parametrize("scheme", ["postgres", "postgresql", "postgresql+psycopg"])
def test_neon_ssl_query_parameters_and_pooled_driver_options(scheme):
    url = database_url(env={"DATABASE_URL": f"{scheme}://user:synthetic@ep-unit-pooler.region.neon.tech/db?sslmode=require&channel_binding=require"})
    assert url.drivername == "postgresql+psycopg"
    engine = create_engine(url, **engine_options(url, env={}))
    assert isinstance(engine.pool, NullPool)
    _, parameters = engine.dialect.create_connect_args(url)
    assert parameters["sslmode"] == "require"
    assert parameters["channel_binding"] == "require"
    assert engine_options(url, env={})["connect_args"]["prepare_threshold"] is None
    engine.dispose()


def test_neon_defaults_to_ssl_and_preserves_stronger_certificate_validation():
    base = "postgresql+psycopg://user:synthetic@ep-unit.region.neon.tech/db"
    assert database_url(env={"DATABASE_URL": base}).query["sslmode"] == "require"
    assert database_url(env={"DATABASE_URL": base + "?sslmode=verify-full"}).query["sslmode"] == "verify-full"
    for mode in ("disable", "allow", "prefer"):
        with pytest.raises(ValueError, match="SSL"):
            database_url(env={"DATABASE_URL": base + f"?sslmode={mode}"})


def test_direct_migration_url_is_separate_and_pooler_is_rejected():
    app = "postgresql+psycopg://user:synthetic@ep-unit-pooler.region.neon.tech/db"
    direct = app.replace("-pooler", "")
    assert database_url(migration=True, env={"DATABASE_URL": app, "MIGRATION_DATABASE_URL": direct}).host == "ep-unit.region.neon.tech"
    with pytest.raises(ValueError, match="direct"):
        database_url(migration=True, env={"MIGRATION_DATABASE_URL": app})
    with pytest.raises(ValueError, match="explicitly"):
        database_url(migration=True, env={"DATABASE_URL": direct})
    # Local Alembic remains compatible without any Neon-specific variable.
    assert database_url(migration=True, env={}).host == "localhost"


def test_vercel_uses_no_local_connection_pool_and_invalid_settings_hide_input():
    url = database_url(env={})
    assert engine_options(url, env={"VERCEL": "1"})["poolclass"] is NullPool
    with pytest.raises(ValueError, match="DATABASE_POOL_MODE"):
        engine_options(url, env={"DATABASE_POOL_MODE": "invalid"})
    with pytest.raises(ValueError) as error:
        database_url(env={"DATABASE_URL": "synthetic-secret-not-a-url"})
    assert "synthetic-secret" not in str(error.value)


def test_migration_plan_and_target_guards_never_create_an_engine(monkeypatch, capsys):
    monkeypatch.setenv("MIGRATION_DATABASE_URL", "postgresql+psycopg://user:synthetic@ep-unit.region.neon.tech/db?sslmode=require")
    engine_calls = []
    def forbidden_engine(*args, **kwargs):
        engine_calls.append(True)
        raise AssertionError("This check must not create a database engine")
    monkeypatch.setattr(migrate_neon, "create_engine", forbidden_engine)
    assert migrate_neon.main([]) == 0
    assert migrate_neon.main(["--apply"]) == 1
    assert migrate_neon.main(["--apply", "--expected-host", "wrong.invalid", "--expected-database", "db"]) == 1
    output = capsys.readouterr().out
    assert "No connection or migration performed" in output
    assert "synthetic" not in output
    assert "postgresql" not in output
    assert engine_calls == []


def test_vercel_entrypoint_loads_and_health_runs_without_database_connection():
    environment = os.environ.copy()
    environment.update({
        "APP_ENV": "production", "VERCEL": "1", "ALLOWED_HOSTS": "testserver",
        "PUBLIC_ORIGIN": "https://frontend.example.invalid",
        "DATABASE_URL": "postgresql+psycopg://user:synthetic@unreachable.example.invalid/db?sslmode=require",
    })
    code = """
import asgi
from fastapi.testclient import TestClient
from sqlalchemy.pool import NullPool
from app.database import engine
assert isinstance(engine.pool, NullPool)
with TestClient(asgi.app) as client:
    assert client.get('/health').status_code == 200
    assert client.get('/docs').status_code == 404
"""
    result = subprocess.run([sys.executable, "-c", code], env=environment, capture_output=True, text=True)
    # Avoid echoing a subprocess environment or driver exception into pytest logs.
    assert result.returncode == 0, "Offline Vercel entrypoint/health check failed"
