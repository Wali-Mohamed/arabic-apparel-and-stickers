import json
import pytest
from fastapi import HTTPException
from app import local_faults
from app.alert_webhook import sanitize
from test_products import client  # Isolated SQLite API fixture, never a shared DB.


SAFE = {"LOCAL_PRICE_FAULTS": "1", "LOCAL_OBSERVABILITY": "1",
        "DATABASE_URL": "postgresql+psycopg://demo:ephemeral_local_only@postgres/apparel_observability"}


@pytest.mark.parametrize("override", [{"LOCAL_PRICE_FAULTS": "0"}, {"LOCAL_OBSERVABILITY": "0"},
    {"VERCEL": "1"}, {"CI": "true"}, {"RUN_POSTGRES_INTEGRATION": "1"},
    {"DATABASE_URL": "postgresql+psycopg://demo:synthetic@postgres/real_database"},
    {"DATABASE_URL": "postgresql+psycopg://demo:synthetic@neon.example.invalid/apparel_observability"}])
def test_fault_disabled_outside_explicit_isolated_stack(override):
    assert not local_faults.local_fault_allowed({**SAFE, **override})
    assert not local_faults.local_fault_allowed({})


def test_marker_fault_and_recovery(monkeypatch, tmp_path):
    for key in ("VERCEL", "CI", "RUN_POSTGRES_INTEGRATION"):
        monkeypatch.delenv(key, raising=False)
    for key, value in SAFE.items():
        monkeypatch.setenv(key, value)
    marker = tmp_path / "fault"
    monkeypatch.setattr(local_faults, "PRICING_MARKER", marker)
    local_faults.reject_unavailable_pricing()
    try:
        marker.touch()
        with pytest.raises(HTTPException) as error:
            local_faults.reject_unavailable_pricing()
        assert error.value.status_code == 503
        monkeypatch.setenv("VERCEL", "1")
        local_faults.reject_unavailable_pricing()  # Even an armed marker cannot affect Vercel.
    finally:
        marker.unlink(missing_ok=True)
    local_faults.reject_unavailable_pricing()


def test_cleanup_after_script_failure(monkeypatch, tmp_path):
    monkeypatch.setattr(local_faults, "local_fault_allowed", lambda: True)
    marker = tmp_path / "marker"
    monkeypatch.setattr(local_faults, "PRICING_MARKER", marker)
    with pytest.raises(RuntimeError):
        with local_faults.pricing_fault():
            assert marker.is_file()
            raise RuntimeError("Simulated verification failure")
    assert not marker.exists()


def test_webhook_allowlist_excludes_all_untrusted_fields():
    payload = {"message": "SECRET_NAME", "alerts": [{"status": "firing",
        "labels": {"alertname": "PricingUnavailable", "customer": "SECRET_NAME"},
        "annotations": {"body": "SECRET_ARABIC_CONTACT_TOKEN"},
        "startsAt": "2026-10-27T01:00:00Z", "endsAt": "0001-01-01T00:00:00Z",
        "fingerprint": "1234567890abcdef"}]}
    result = sanitize(payload)
    assert len(result) == 1 and result[0]["state"] == "firing"
    assert set(result[0]) == {"alertname", "state", "starts_at", "ends_at", "fingerprint"}
    assert "SECRET" not in json.dumps(result)
    payload["alerts"][0]["status"] = "resolved"
    assert sanitize(payload)[0]["state"] == "resolved"
    payload["alerts"][0]["fingerprint"] = "SECRET_TOKEN"
    assert sanitize(payload) == []
    assert sanitize({"alerts": "not a list"}) == []


def test_real_pricing_validation_fault_and_ci_isolation(client, monkeypatch, tmp_path):
    for key in ("VERCEL", "CI", "RUN_POSTGRES_INTEGRATION"):
        monkeypatch.delenv(key, raising=False)
    for key, value in SAFE.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(local_faults, "PRICING_MARKER", tmp_path / "marker")
    valid = {"options": {"text": "\u0633\u0644\u0627\u0645", "font": "Amiri"}}
    with local_faults.pricing_fault():
        assert client.post('/api/products/3/price', json=valid).status_code == 503
        assert client.post('/api/products/3/price', json={"options": {"text": "INVALID"}}).status_code == 422
        assert client.get('/api/products').status_code == 200
        monkeypatch.setenv("CI", "true")
        assert client.post('/api/products/3/price', json=valid).status_code == 200
    assert client.post('/api/products/3/price', json=valid).json()["total_price_pence"] == 1200
