"""No sockets: real SDK signals and API handlers using disposable SQLite."""
import json
from contextlib import contextmanager
import pytest
from fastapi.testclient import TestClient
from fastapi.routing import APIRoute
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import SpanKind
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import SimpleLogRecordProcessor, InMemoryLogRecordExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import InMemoryMetricReader
from sqlalchemy import select

from app import main
from app.telemetry import Telemetry
from app.database import get_db
from app.models import Order
from test_products import client  # Existing isolated SQLite fixture; no shared DB.


@pytest.fixture
def observed(client, monkeypatch):
    spans, logs, reader = InMemorySpanExporter(), InMemoryLogRecordExporter(), InMemoryMetricReader()
    resource = Resource({"service.name": "arabic-apparel-api"})
    traces, logger = TracerProvider(resource=resource), LoggerProvider(resource=resource)
    traces.add_span_processor(SimpleSpanProcessor(spans))
    logger.add_log_record_processor(SimpleLogRecordProcessor(logs))
    telemetry = Telemetry(traces, logger, MeterProvider(resource=resource, metric_readers=[reader]))
    monkeypatch.setattr(main, "configured_telemetry", lambda: telemetry)
    app = main.create_app()
    app.dependency_overrides[get_db] = main.app.dependency_overrides[get_db]
    with TestClient(app, raise_server_exceptions=False) as api:
        yield api, telemetry, spans, logs, reader, app


def journey(api):
    assert api.get("/api/products?secret=QUERY_SENTINEL", headers={
        "authorization": "Bearer TOKEN_SENTINEL", "cookie": "COOKIE_SENTINEL",
    }).status_code == 200
    options = {"text": "\u0633\u0644\u0627\u0645", "font": "Amiri"}
    assert api.post("/api/products/3/price", json={"options": options}).status_code == 200
    response = api.post("/api/orders", json={"product_id": 3, "options": options,
        "customer_name": "NAME_SENTINEL", "customer_contact": "CONTACT_SENTINEL@example.invalid"})
    assert response.status_code == 201
    assert api.post("/api/products/3/price", json={"options": {"text": "BODY_SENTINEL"}}).status_code == 422
    return response.json()["id"]


def test_correlation_metrics_and_privacy(observed, capsys):
    api, telemetry, spans, logs, reader, app = observed
    order_id = journey(api)
    with contextmanager(app.dependency_overrides[get_db])() as db:
        assert db.scalar(select(Order.id).where(Order.id == order_id)) == order_id
    finished = spans.get_finished_spans()
    records = logs.get_finished_logs()
    assert len(records) == 4
    assert len({r.log_record.trace_id for r in records}) == 4
    for record in records:
        log = record.log_record
        matching = [s for s in finished if s.context.span_id == log.span_id]
        assert len(matching) == 1
        assert matching[0].context.trace_id == log.trace_id != 0
        assert matching[0].kind == SpanKind.SERVER
        assert json.loads(log.body)["trace_id"] == format(log.trace_id, "032x")
    names = {s.name for s in finished}
    assert {"catalogue.lookup", "product.lookup", "price.lookup", "pricing.calculate", "order.create"} <= names
    data = reader.get_metrics_data()
    metrics = {m.name: m for r in data.resource_metrics for scope in r.scope_metrics for m in scope.metrics}
    assert sum(p.value for p in metrics["apparel.requests"].data.data_points) == 4
    assert sum(p.value for p in metrics["apparel.errors"].data.data_points) == 1
    assert sum(p.count for p in metrics["apparel.request.duration"].data.data_points) == 4
    exemplars = [e for p in metrics["apparel.request.duration"].data.data_points for e in p.exemplars]
    assert exemplars and all(e.trace_id in {s.context.trace_id for s in finished} for e in exemplars)
    exported = " ".join(s.to_json() for s in finished) + str(data) + str([r.to_json() for r in records]) + capsys.readouterr().out
    for secret in ["QUERY_SENTINEL", "TOKEN_SENTINEL", "COOKIE_SENTINEL", "NAME_SENTINEL",
                   "CONTACT_SENTINEL", "BODY_SENTINEL", "\u0633\u0644\u0627\u0645", "\\u0633\\u0644\\u0627\\u0645"]:
        assert secret not in exported
    assert all(not s.events for s in finished)  # No default exception payloads.


def test_telemetry_failure_does_not_break_committed_order(observed, monkeypatch):
    api, telemetry, spans, logs, reader, app = observed
    def fail(*args, **kwargs):
        raise RuntimeError("SECRET_EXPORT_FAILURE")
    monkeypatch.setattr(telemetry.logger, "emit", fail)
    monkeypatch.setattr(spans, "export", fail)
    order_id = journey(api)
    with contextmanager(app.dependency_overrides[get_db])() as db:
        assert db.get(Order, order_id).status == "new"


def test_unhandled_error_sanitized(observed):
    api, telemetry, spans, logs, reader, app = observed
    def fail():
        raise RuntimeError("EXCEPTION_SECRET")
    # Use an allowlisted route template to exercise a real 500 response.
    app.router.routes.insert(0, APIRoute('/api/products', fail, methods=['GET']))
    assert api.get('/api/products').status_code == 500
    assert json.loads(logs.get_finished_logs()[0].log_record.body)["status"] == "500"
    data = reader.get_metrics_data()
    errors = [p for r in data.resource_metrics for scope in r.scope_metrics for m in scope.metrics
              if m.name == "apparel.errors" for p in m.data.data_points]
    assert sum(p.value for p in errors if p.attributes["status"] == "500") == 1
    assert "EXCEPTION_SECRET" not in str([s.to_json() for s in spans.get_finished_spans()])
