from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")

class PaginatedResponse(BaseModel):
    items: List[Any] = []
    total: int = 0
    page: int = 1
    per_page: int = 20
    has_next: bool = False

class ErrorResponse(BaseModel):
    error: str
    code: str
    detail: Optional[Any] = None

class ModeResponse(BaseModel):
    mode: str
    connection_status: str
    active_store: Optional[dict] = None
