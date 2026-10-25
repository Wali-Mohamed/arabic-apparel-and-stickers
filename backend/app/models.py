from typing import Any

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(100), index=True)
    configuration_options: Mapped[dict[str, Any]] = mapped_column(JSON)
    prices: Mapped[list["ProductPrice"]] = relationship(
        back_populates="product", cascade="all, delete-orphan", lazy="selectin"
    )


class ProductPrice(Base):
    __tablename__ = "product_prices"
    __table_args__ = (UniqueConstraint("product_id", "option_key", "option_value"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
    option_key: Mapped[str] = mapped_column(String(50))
    option_value: Mapped[str] = mapped_column(String(100))
    price_pence: Mapped[int] = mapped_column(Integer)
    pair_price_pence: Mapped[int | None] = mapped_column(Integer, nullable=True)
    product: Mapped[Product] = relationship(back_populates="prices")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    customer_name: Mapped[str] = mapped_column(String(200))
    customer_contact: Mapped[str] = mapped_column(String(320))
    options: Mapped[dict[str, Any]] = mapped_column(JSON)
    quantity: Mapped[int] = mapped_column(Integer)
    total_price_pence: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(30), default="new")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
