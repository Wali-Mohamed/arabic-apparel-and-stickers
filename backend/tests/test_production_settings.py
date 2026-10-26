import pytest
from fastapi.testclient import TestClient

from app.main import create_app


def production_app(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("ALLOWED_HOSTS", "testserver,127.0.0.1")
    monkeypatch.setenv("PUBLIC_ORIGIN", "https://shop.example.invalid")
    return create_app()


def test_production_host_origin_and_docs(monkeypatch):
    with TestClient(production_app(monkeypatch)) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/health", headers={"host": "evil.example.invalid"}).status_code == 400
        assert client.get("/docs").status_code == 404
        assert client.get("/openapi.json").status_code == 404
        assert client.post("/api/orders", headers={"origin": "https://evil.example.invalid"}, json={}).status_code == 403
        response = client.options("/api/orders", headers={
            "origin": "https://shop.example.invalid", "access-control-request-method": "POST",
            "access-control-request-headers": "content-type",
        })
        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == "https://shop.example.invalid"


def test_production_settings_fail_closed(monkeypatch):
    production_app(monkeypatch)
    monkeypatch.setenv("ALLOWED_HOSTS", "*")
    with pytest.raises(RuntimeError, match="trusted hosts"):
        create_app()
    monkeypatch.setenv("ALLOWED_HOSTS", "testserver")
    monkeypatch.setenv("PUBLIC_ORIGIN", "http://public.example.invalid")
    with pytest.raises(RuntimeError, match="HTTPS"):
        create_app()
