from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import app
from app.models import Base, Product, ProductPrice


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    with session_factory() as session:
        sticker = Product(
            slug="personalized-arabic-htv-stickers",
            name="Personalized Arabic HTV Stickers",
            description="A test product.",
            category="HTV Stickers",
            configuration_options={"fonts": ["Amiri"]},
        )
        tag = Product(
            slug="high-visibility-tags",
            name="High-Visibility Tags",
            description="A test tag.",
            category="High-Visibility Tags",
            configuration_options={"shapes": ["diamond", "rectangle"]},
        )
        sweater = Product(
            slug="be-seen-sweater",
            name="Be Seen Sweater",
            description="A test sweater.",
            category="Apparel",
            configuration_options={"colour": "black"},
        )
        session.add_all([sticker, tag, sweater])
        session.flush()
        session.add_all(
            [
                ProductPrice(product_id=sticker.id, option_key="width_cm", option_value="10", price_pence=499),
                ProductPrice(product_id=sticker.id, option_key="width_cm", option_value="15", price_pence=699),
                ProductPrice(product_id=sticker.id, option_key="width_cm", option_value="20", price_pence=899),
                ProductPrice(product_id=tag.id, option_key="shape", option_value="diamond", price_pence=599),
                ProductPrice(product_id=tag.id, option_key="shape", option_value="rectangle", price_pence=699),
                ProductPrice(product_id=tag.id, option_key="design", option_value="b-series", price_pence=599),
                ProductPrice(product_id=sweater.id, option_key="standard", option_value="standard", price_pence=2499),
            ]
        )
        session.commit()

    def override_get_db() -> Generator[Session, None, None]:
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)


def test_list_products(client: TestClient) -> None:
    response = client.get("/api/products")

    assert response.status_code == 200
    assert response.json()[0]["slug"] == "personalized-arabic-htv-stickers"
    assert response.json()[0]["configuration_options"] == {"fonts": ["Amiri"]}
    assert response.json()[0]["prices"][0]["price_pence"] == 499


def test_get_product(client: TestClient) -> None:
    response = client.get("/api/products/1")

    assert response.status_code == 200
    assert response.json()["name"] == "Personalized Arabic HTV Stickers"


def test_get_missing_product_returns_not_found(client: TestClient) -> None:
    response = client.get("/api/products/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}


@pytest.mark.parametrize(
    ("product_id", "options", "price_pence"),
    [
        (1, {"width_cm": 10}, 499),
        (1, {"width_cm": 15}, 699),
        (1, {"width_cm": 20}, 899),
        (2, {"shape": "diamond"}, 599),
        (2, {"shape": "rectangle"}, 699),
        (2, {"design": "b-series"}, 599),
        (3, {}, 2499),
    ],
)
def test_calculate_demo_price(client: TestClient, product_id: int, options: dict[str, str | int], price_pence: int) -> None:
    response = client.post(f"/api/products/{product_id}/price", json={"options": options})

    assert response.status_code == 200
    assert response.json() == {
        "price_pence": price_pence,
        "currency": "GBP",
        "demonstration_price": True,
    }


def test_calculate_price_rejects_unsupported_option(client: TestClient) -> None:
    response = client.post("/api/products/1/price", json={"options": {"width_cm": 99}})

    assert response.status_code == 400
    assert response.json() == {"detail": "Unsupported product configuration"}
