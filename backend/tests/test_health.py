from unittest.mock import MagicMock

import pytest

from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app import main

client = TestClient(main.app)


@pytest.mark.parametrize("path", ["/health", "/api/health"])
def test_health_endpoint(path) -> None:
    response = client.get(path)

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.parametrize("path", ["/health/db", "/api/health/db"])
def test_database_health_endpoint_returns_connected(monkeypatch, path) -> None:
    connection = MagicMock()
    database_engine = MagicMock()
    database_engine.connect.return_value.__enter__.return_value = connection
    monkeypatch.setattr(main, "engine", database_engine)

    response = client.get(path)

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}
    connection.execute.assert_called_once()


@pytest.mark.parametrize("path", ["/health/db", "/api/health/db"])
def test_database_health_endpoint_returns_service_unavailable(monkeypatch, path) -> None:
    database_engine = MagicMock()
    database_engine.connect.side_effect = SQLAlchemyError("database is unavailable")
    monkeypatch.setattr(main, "engine", database_engine)

    response = client.get(path)

    assert response.status_code == 503
    assert response.json() == {"detail": "Database unavailable"}
