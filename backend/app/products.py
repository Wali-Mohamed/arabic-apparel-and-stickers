from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import Product, ProductPrice
from app.personalization import normalize_and_validate_arabic_letter, normalize_and_validate_arabic_text
from app.schemas import PriceQuoteRead, PriceQuoteRequest, ProductRead
from app.telemetry import operation
from app.local_faults import reject_unavailable_pricing

router = APIRouter(prefix="/api/products", tags=["products"])

FONTS = {"Amiri", "Cairo", "Tajawal"}
HTV_COLOURS = {
    "Black": "#000000", "White": "#FFFFFF", "Yellow": "#FFEA00", "Light Blue": "#37C5D3", "Red": "#E52B24",
    "Grass Green": "#3AAF2A", "Pink": "#EB78B8", "Royal Blue": "#2F4A92", "Purple": "#5A3AA5", "Brown": "#4B2117",
    "Lake Blue": "#167D98", "Rose Gold": "#B9999F", "Dark Yellow": "#F18A00", "Rose Red": "#BF1831", "Aqua Blue": "#258FC6",
    "Dark Green": "#123D2D", "Green": "#078652", "Gold": "#D8BA39", "Silver": "#C8CDD0", "Orange": "#FF6413",
}
COLOURS = set(HTV_COLOURS.values())
TEXT_PRODUCTS = {
    "personalized-arabic-rectangular-tag",
    "personalized-arabic-htv-sticker",
    "be-seen-boys-sweater",
    "be-seen-mens-sweater",
}


@router.get("", response_model=list[ProductRead])
@operation("catalogue.lookup")
def list_products(db: Session = Depends(get_db)) -> list[Product]:
    return list(db.scalars(select(Product).options(selectinload(Product.prices)).order_by(Product.id)))


@router.get("/{product_id}", response_model=ProductRead)
@operation("product.lookup")
def get_product(product_id: int, db: Session = Depends(get_db)) -> Product:
    product = db.scalar(select(Product).options(selectinload(Product.prices)).where(Product.id == product_id))
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/{product_id}/price", response_model=PriceQuoteRead)
@operation("pricing.request")
def calculate_price(product_id: int, quote_request: PriceQuoteRequest, db: Session = Depends(get_db)) -> PriceQuoteRead:
    product = lookup_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    option_key, option_value, normalized_text = _price_option_for(product, quote_request.options)
    price = lookup_price(db, product.id, option_key, option_value)
    if price is None:
        raise HTTPException(status_code=400, detail="Unsupported product configuration")

    reject_unavailable_pricing()  # Only after product/options/price validation.
    total = calculate_total(price, quote_request.quantity)
    return PriceQuoteRead(
        price_pence=total,
        unit_price_pence=price.price_pence,
        pair_price_pence=price.pair_price_pence,
        quantity=quote_request.quantity,
        total_price_pence=total,
        normalized_text=normalized_text,
    )


@operation("product.lookup")
def lookup_product(db: Session, product_id: int) -> Product | None:
    return db.get(Product, product_id)


@operation("price.lookup")
def lookup_price(db: Session, product_id: int, option_key: str, option_value: str) -> ProductPrice | None:
    return db.scalar(
        select(ProductPrice).where(
            ProductPrice.product_id == product_id,
            ProductPrice.option_key == option_key,
            ProductPrice.option_value == option_value,
        )
    )


@operation("pricing.validate")
def _price_option_for(product: Product, options: dict[str, str | int]) -> tuple[str, str, str | None]:
    if product.slug == "personalized-arabic-htv-sticker":
        _require_allowed_options(options, {"text", "font", "size", "colour"})
        normalized_text = normalize_and_validate_arabic_text(options.get("text"))
        _validate_font(options.get("font"))
        if options.get("colour") not in COLOURS:
            raise HTTPException(status_code=422, detail="colour is not supported")
        size = str(options.get("size"))
        if size not in {"5x5", "9x4", "12x3"}:
            raise HTTPException(status_code=422, detail="size must be 5x5, 9x4, or 12x3")
        return "size", size, normalized_text

    if product.slug == "small-arabic-letter-tag":
        _require_allowed_options(options, {"text", "font"})
        normalized_text = normalize_and_validate_arabic_letter(options.get("text"))
        _validate_font(options.get("font"))
        return "standard", "standard", normalized_text

    if product.slug in TEXT_PRODUCTS:
        _require_allowed_options(options, {"text", "font"})
        normalized_text = normalize_and_validate_arabic_text(options.get("text"))
        _validate_font(options.get("font"))
        return "standard", "standard", normalized_text

    if product.slug == "small-be-seen-tag":
        _require_allowed_options(options, {"design"})
        if options.get("design", "be-seen") != "be-seen":
            raise HTTPException(status_code=422, detail="Small Be Seen tag uses the fixed Be Seen design")
        return "standard", "standard", None

    if product.slug in {"big-be-seen-tag", "be-seen-black-canvas-bag"}:
        _require_allowed_options(options, set())
        return "standard", "standard", None

    raise HTTPException(status_code=400, detail="Pricing is not configured for this product")


def _validate_font(font: object) -> None:
    if font not in FONTS:
        raise HTTPException(status_code=422, detail="font must be Amiri, Cairo, or Tajawal")


@operation("pricing.calculate")
def calculate_total(price: ProductPrice, quantity: int) -> int:
    pair_count, leftover = divmod(quantity, 2)
    return (
        pair_count * price.pair_price_pence + leftover * price.price_pence
        if price.pair_price_pence is not None
        else quantity * price.price_pence
    )


def _require_allowed_options(options: dict[str, str | int], allowed: set[str]) -> None:
    unsupported = set(options) - allowed
    if unsupported:
        raise HTTPException(status_code=422, detail=f"Unsupported options: {', '.join(sorted(unsupported))}")
