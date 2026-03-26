from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class AnalyticsSummaryResponse(BaseModel):
    total_orders: int = 0
    revenue: float = 0
    average_order_value: float = 0
    refund_rate: float = 0
    fulfillment_rate: float = 0
    comparison: Optional[Dict[str, Any]] = None

class ChartDataResponse(BaseModel):
    type: str
    data: List[Dict[str, Any]] = []
