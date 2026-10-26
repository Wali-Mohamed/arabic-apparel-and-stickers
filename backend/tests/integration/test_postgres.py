"""Opt-in tests for an isolated, Alembic-migrated PostgreSQL database."""
import os

import pytest
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from fastapi.testclient import TestClient
from sqlalchemy import select

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_POSTGRES_INTEGRATION") != "1",
    reason="Requires an isolated migrated PostgreSQL database; see docs/CI_CD.md",
)


def test_migrated_catalogue_quote_and_order_persistence() -> None:
    from app.database import SessionLocal, engine
    from app.main import app
    from app.models import Order

    assert engine.dialect.name == "postgresql"
    assert engine.url.database == "apparel_ci", "Use the dedicated disposable test database"
    assert not app.dependency_overrides
    with engine.connect() as connection:
        assert MigrationContext.configure(connection).get_current_revision() == (
            ScriptDirectory.from_config(Config("alembic.ini")).get_current_head()
        )
    order_id = None
    try:
        with TestClient(app) as client:
            assert client.get("/health/db").json()["database"] == "connected"
            response = client.get("/api/products")
            assert response.status_code == 200
            products = response.json()
            assert len(products) == 8
            product = next(p for p in products if p["slug"] == "small-arabic-letter-tag")
            options = {"text": "\u0628", "font": "Amiri"}
            quote = client.post(f'/api/products/{product["id"]}/price', json={
                "options": options, "quantity": 3,
            })
            assert quote.status_code == 200
            assert quote.json()["total_price_pence"] == 1350
            invalid = client.post(f'/api/products/{product["id"]}/price', json={
                "options": {"text": "Latin", "font": "Amiri"}, "quantity": 1,
            })
            assert invalid.status_code == 422
            order_response = client.post("/api/orders", json={
                "product_id": product["id"], "options": options, "quantity": 3,
                "customer_name": "CI synthetic customer", "customer_contact": "ci@example.invalid",
            })
            assert order_response.status_code == 201
            order_id = order_response.json()["id"]
        # Separate session after the HTTP client closes proves a database commit.
        with SessionLocal() as session:
            order = session.scalar(select(Order).where(Order.id == order_id))
            assert order is not None
            assert order.total_price_pence == 1350
            assert order.status == "new"
            assert order.options == options
    finally:
        if order_id is not None:
            with SessionLocal() as session:
                order = session.get(Order, order_id)
                if order is not None:
                    session.delete(order)
                    session.commit()
