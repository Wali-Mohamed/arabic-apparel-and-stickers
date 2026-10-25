from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import app
from app.models import Base, Product, ProductPrice

CATALOGUE = [
    ("small-be-seen-tag", [("standard", "standard", 500, None)]),
    ("big-be-seen-tag", [("standard", "standard", 1000, None)]),
    ("personalized-arabic-rectangular-tag", [("standard", "standard", 1200, None)]),
    ("small-arabic-letter-tag", [("standard", "standard", 500, 850)]),
    ("personalized-arabic-htv-sticker", [("size", "5x5", 500, None), ("size", "9x4", 900, None), ("size", "12x3", 1200, None)]),
    ("be-seen-boys-sweater", [("standard", "standard", 1500, 2500)]),
    ("be-seen-mens-sweater", [("standard", "standard", 3000, 5000)]),
    ("be-seen-black-canvas-bag", [("standard", "standard", 2000, None)]),
]


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    session_factory = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    with session_factory() as session:
        for slug, prices in CATALOGUE:
            product = Product(slug=slug, name=slug, description="Test product.", category="Test", configuration_options={})
            session.add(product)
            session.flush()
            session.add_all(ProductPrice(product_id=product.id, option_key=key, option_value=value, price_pence=price, pair_price_pence=pair) for key, value, price, pair in prices)
        session.commit()

    def override_get_db() -> Generator[Session, None, None]:
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)


def quote(client: TestClient, product_id: int, options: dict[str, str | int], quantity: int = 1) -> dict:
    response = client.post(f"/api/products/{product_id}/price", json={"options": options, "quantity": quantity})
    assert response.status_code == 200, response.text
    return response.json()


def test_list_has_only_final_catalogue(client: TestClient) -> None:
    response = client.get("/api/products")
    assert response.status_code == 200
    assert [product["slug"] for product in response.json()] == [slug for slug, _ in CATALOGUE]
    assert "high-visibility-tags" not in {product["slug"] for product in response.json()}
    assert "personalized-arabic-htv-stickers" not in {product["slug"] for product in response.json()}


@pytest.mark.parametrize(("product_id", "options", "expected"), [
    (1, {"design": "be-seen"}, 500), (2, {}, 1000),
    (3, {"text": "\u0645\u062d\u0645\u062f \u0627\u0644\u0639\u0644\u064a", "font": "Amiri"}, 1200),
    (4, {"text": "\u0628\u0650", "font": "Cairo"}, 500),
    (5, {"text": "\u0639\u0644\u064a", "font": "Tajawal", "size": "5x5", "colour": "#FFEA00"}, 500),
    (5, {"text": "\u0639\u0644\u064a", "font": "Tajawal", "size": "9x4", "colour": "#F18A00"}, 900),
    (5, {"text": "\u0639\u0644\u064a", "font": "Tajawal", "size": "12x3", "colour": "#000000"}, 1200),
    (6, {"text": "\u0639\u0644\u064a", "font": "Amiri"}, 1500),
    (7, {"text": "\u0639\u0644\u064a", "font": "Amiri"}, 3000), (8, {}, 2000),
])
def test_each_product_price(client: TestClient, product_id: int, options: dict[str, str | int], expected: int) -> None:
    result = quote(client, product_id, options)
    assert result["price_pence"] == expected
    assert result["total_price_pence"] == expected
    assert result["unit_price_pence"] == expected


@pytest.mark.parametrize(("product_id", "options", "quantity", "expected"), [
    (4, {"text": "\u0628", "font": "Amiri"}, 2, 850), (4, {"text": "\u0628", "font": "Amiri"}, 5, 2200),
    (6, {"text": "\u0639\u0644\u064a", "font": "Cairo"}, 2, 2500), (6, {"text": "\u0639\u0644\u064a", "font": "Cairo"}, 3, 4000),
    (7, {"text": "\u0639\u0644\u064a", "font": "Tajawal"}, 2, 5000), (7, {"text": "\u0639\u0644\u064a", "font": "Tajawal"}, 5, 13000), (2, {}, 3, 3000),
])
def test_bundle_prices_apply_to_each_complete_pair(client: TestClient, product_id: int, options: dict[str, str | int], quantity: int, expected: int) -> None:
    result = quote(client, product_id, options, quantity)
    assert result["quantity"] == quantity
    assert result["price_pence"] == expected


@pytest.mark.parametrize(("product_id", "options"), [
    (5, {"text": "\u0639\u0644\u064a", "font": "Amiri", "width_cm": 10, "colour": "#FFEA00"}),
    (5, {"text": "\u0639\u0644\u064a", "font": "Amiri", "size": "10", "colour": "#FFEA00"}),
    (4, {"text": "\u0628\u062a", "font": "Amiri"}), (1, {"design": "diamond"}), (8, {"text": "\u0639\u0644\u064a"}),
])
def test_invalid_or_discontinued_options_are_rejected(client: TestClient, product_id: int, options: dict[str, str | int]) -> None:
    response = client.post(f"/api/products/{product_id}/price", json={"options": options})
    assert response.status_code == 422


def test_rejects_invalid_quantity(client: TestClient) -> None:
    response = client.post("/api/products/2/price", json={"options": {}, "quantity": 0})
    assert response.status_code == 422


def test_order_request_stores_server_calculated_total(client: TestClient) -> None:
    response = client.post(
        "/api/orders",
        json={
            "product_id": 4,
            "options": {"text": "\u0628", "font": "Amiri"},
            "quantity": 2,
            "customer_name": "Test customer",
            "customer_contact": "test@example.com",
        },
    )
    assert response.status_code == 201
    assert response.json()["total_price_pence"] == 850
    assert response.json()["status"] == "new"
