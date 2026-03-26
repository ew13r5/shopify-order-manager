from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_db, get_store_id
from models import LineItem, Order
from services.sku_cleaner import has_hidden_chars

router = APIRouter(prefix="/api", tags=["line_items"])


@router.get("/line-items")
def list_line_items(
    sku: Optional[str] = None,
    product_id: Optional[str] = None,
    store_id: UUID = Depends(get_store_id),
    db: Session = Depends(get_db),
):
    query = db.query(LineItem).join(Order).filter(Order.store_id == store_id)
    if sku:
        query = query.filter(LineItem.sku_cleaned.ilike("%" + sku + "%"))
    if product_id:
        query = query.filter(LineItem.product_id == UUID(product_id))
    items = query.limit(100).all()
    return [
        {
            "id": str(li.id),
            "title": li.title,
            "sku": li.sku,
            "sku_cleaned": li.sku_cleaned,
            "has_hidden_chars": has_hidden_chars(li.sku),
            "variant_title": li.variant_title,
            "quantity": li.quantity,
            "unit_price": float(li.unit_price or 0),
            "total_price": float(li.total_price or 0),
            "discount_amount": float(li.discount_amount or 0),
            "tax_amount": float(li.tax_amount or 0),
            "fulfillment_status": li.fulfillment_status,
            "refund_amount": float(li.refund_amount or 0),
        }
        for li in items
    ]
