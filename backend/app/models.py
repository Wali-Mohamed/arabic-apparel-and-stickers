from typing import Any

from sqlalchemy import ForeignKey, Integer, JSON, String, Text, UniqueConstraint
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
    product: Mapped[Product] = relationship(back_populates="prices")
