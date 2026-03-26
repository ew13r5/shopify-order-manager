from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class PayoutItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    line_item_id: Optional[str] = None
    gross_amount: Optional[float] = None
    fee_amount: Optional[float] = None
    net_amount: Optional[float] = None

class PayoutResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    date: Optional[date] = None
    amount: Optional[float] = None
    status: Optional[str] = None
    items: List[PayoutItemResponse] = []

class AdjustmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    order_id: Optional[str] = None
    type: Optional[str] = None
    amount: Optional[float] = None
    reason: Optional[str] = None
    created_at: Optional[datetime] = None
