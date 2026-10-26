from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Order
from app.products import _price_option_for, calculate_total, lookup_product, lookup_price
from app.schemas import OrderCreate, OrderRead
from app.telemetry import operation

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("", response_model=OrderRead, status_code=201)
@operation("order.create")
def create_order(order_request: OrderCreate, db: Session = Depends(get_db)) -> Order:
    product = lookup_product(db, order_request.product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    option_key, option_value, normalized_text = _price_option_for(product, order_request.options)
    price = lookup_price(db, product.id, option_key, option_value)
    if price is None:
        raise HTTPException(status_code=400, detail="Unsupported product configuration")

    options = dict(order_request.options)
    if normalized_text is not None:
        options["text"] = normalized_text
    order = Order(
        product_id=product.id,
        customer_name=order_request.customer_name.strip(),
        customer_contact=order_request.customer_contact.strip(),
        options=options,
        quantity=order_request.quantity,
        total_price_pence=calculate_total(price, order_request.quantity),
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order
