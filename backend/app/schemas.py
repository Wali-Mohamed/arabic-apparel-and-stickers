from typing import Any

from pydantic import BaseModel, ConfigDict


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


class PriceQuoteRequest(BaseModel):
    options: dict[str, str | int] = {}


class PriceQuoteRead(BaseModel):
    price_pence: int
    currency: str = "GBP"
    demonstration_price: bool = True
