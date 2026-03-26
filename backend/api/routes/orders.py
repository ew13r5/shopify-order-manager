from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.deps import get_current_provider, get_db, get_store_id
from providers.base import DataProvider, OrderFilters
from services.sku_cleaner import has_hidden_chars

router = APIRouter(prefix="/api", tags=["orders"])


@router.get("/orders")
def list_orders(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    fulfillment_status: Optional[str] = None,
    sku: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_dir: Optional[str] = None,
    store_id: UUID = Depends(get_store_id),
    provider: DataProvider = Depends(get_current_provider),
):
    filters = OrderFilters(
        page=page, per_page=per_page, search_query=search,
        status=status, fulfillment_status=fulfillment_status,
        sku=sku, sort_by=sort_by, sort_dir=sort_dir,
    )
    result = provider.get_orders(store_id, filters)
    items = []
    for o in result.items:
        items.append({
            "id": str(o.id),
            "order_number": o.order_number,
            "customer_name": o.customer_name,
            "customer_email": o.customer_email,
            "status": o.status,
            "financial_status": o.financial_status.value if o.financial_status else None,
            "fulfillment_status": o.fulfillment_status.value if o.fulfillment_status else None,
            "total_price": float(o.total_price) if o.total_price else None,
            "created_at": str(o.order_created_at) if o.order_created_at else None,
            "items_count": len(o.line_items) if o.line_items else 0,
        })
    return {"items": items, "total": result.total, "page": result.page,
            "per_page": result.per_page, "has_next": result.has_next}


@router.get("/orders/{order_id}")
def get_order_detail(
    order_id: str,
    store_id: UUID = Depends(get_store_id),
    provider: DataProvider = Depends(get_current_provider),
):
    order = provider.get_order_detail(store_id, UUID(order_id))
    if not order:
        raise HTTPException(404, detail="Order not found")
    line_items = []
    for li in order.line_items:
        line_items.append({
            "id": str(li.id), "title": li.title, "sku": li.sku,
            "sku_cleaned": li.sku_cleaned,
            "has_hidden_chars": has_hidden_chars(li.sku),
            "variant_title": li.variant_title, "quantity": li.quantity,
            "unit_price": float(li.unit_price) if li.unit_price else None,
            "total_price": float(li.total_price) if li.total_price else None,
            "discount_amount": float(li.discount_amount or 0),
            "tax_amount": float(li.tax_amount or 0),
            "fulfillment_status": li.fulfillment_status,
            "refund_amount": float(li.refund_amount or 0),
        })
    return {
        "id": str(order.id), "order_number": order.order_number,
        "customer_name": order.customer_name,
        "financial_status": order.financial_status.value if order.financial_status else None,
        "fulfillment_status": order.fulfillment_status.value if order.fulfillment_status else None,
        "total_price": float(order.total_price) if order.total_price else None,
        "created_at": str(order.order_created_at) if order.order_created_at else None,
        "line_items": line_items,
    }
