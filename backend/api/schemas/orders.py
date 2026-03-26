from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class LineItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: Optional[str] = None
    sku: Optional[str] = None
    sku_cleaned: Optional[str] = None
    has_hidden_chars: bool = False
    variant_title: Optional[str] = None
    quantity: int = 1
    unit_price: Optional[float] = None
    total_price: Optional[float] = None
    discount_amount: Optional[float] = 0
    tax_amount: Optional[float] = 0
    fulfillment_status: Optional[str] = None
    refund_amount: Optional[float] = 0

class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    order_number: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    status: Optional[str] = None
    financial_status: Optional[str] = None
    fulfillment_status: Optional[str] = None
    total_price: Optional[float] = None
    created_at: Optional[datetime] = None

class OrderDetailResponse(OrderResponse):
    line_items: List[LineItemResponse] = []
