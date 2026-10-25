from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import Product, ProductPrice
from app.schemas import PriceQuoteRead, PriceQuoteRequest, ProductRead

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=list[ProductRead])
def list_products(db: Session = Depends(get_db)) -> list[Product]:
    statement = select(Product).options(selectinload(Product.prices)).order_by(Product.id)
    return list(db.scalars(statement))


@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: int, db: Session = Depends(get_db)) -> Product:
    statement = select(Product).options(selectinload(Product.prices)).where(Product.id == product_id)
    product = db.scalar(statement)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/{product_id}/price", response_model=PriceQuoteRead)
def calculate_price(
    product_id: int, quote_request: PriceQuoteRequest, db: Session = Depends(get_db)
) -> PriceQuoteRead:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    option_key, option_value = _price_option_for(product, quote_request.options)
    statement = select(ProductPrice).where(
        ProductPrice.product_id == product.id,
        ProductPrice.option_key == option_key,
        ProductPrice.option_value == option_value,
    )
    price = db.scalar(statement)
    if price is None:
        raise HTTPException(status_code=400, detail="Unsupported product configuration")

    return PriceQuoteRead(price_pence=price.price_pence)


def _price_option_for(product: Product, options: dict[str, str | int]) -> tuple[str, str]:
    if product.slug == "personalized-arabic-htv-stickers":
        width_cm = options.get("width_cm")
        if width_cm is None:
            raise HTTPException(status_code=400, detail="width_cm is required")
        return "width_cm", str(width_cm)

    if product.slug == "high-visibility-tags":
        if options.get("design") == "b-series":
            return "design", "b-series"
        shape = options.get("shape")
        if shape is None:
            raise HTTPException(status_code=400, detail="shape or B-Series design is required")
        return "shape", str(shape)

    if product.slug == "be-seen-sweater":
        return "standard", "standard"

    raise HTTPException(status_code=400, detail="Pricing is not configured for this product")
