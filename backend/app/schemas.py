from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    description: str
    category: str
    configuration_options: dict[str, Any]
    prices: list["ProductPriceRead"]


class ProductPriceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    option_key: str
    option_value: str
    price_pence: int
    pair_price_pence: int | None


class PriceQuoteRequest(BaseModel):
    options: dict[str, str | int] = {}
    quantity: int = Field(default=1, ge=1)


class PriceQuoteRead(BaseModel):
    price_pence: int
    unit_price_pence: int
    pair_price_pence: int | None
    quantity: int
    total_price_pence: int
    currency: str = "GBP"
    demonstration_price: bool = True
    normalized_text: str | None = None


class OrderCreate(BaseModel):
    product_id: int
    options: dict[str, str | int] = {}
    quantity: int = Field(default=1, ge=1)
    customer_name: str = Field(min_length=1, max_length=200)
    customer_contact: str = Field(min_length=3, max_length=320)


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity: int
    total_price_pence: int
    status: str
    created_at: datetime
