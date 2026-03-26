from typing import Optional
from uuid import UUID

from fastapi import Depends, Header, Query, Request
from sqlalchemy.orm import Session

from database import get_db
from models import Store
from providers import ProviderManager
from providers.base import DataProvider


def get_provider_manager(request: Request) -> ProviderManager:
    return request.app.state.provider_manager


def get_current_provider(
    db: Session = Depends(get_db),
    pm: ProviderManager = Depends(get_provider_manager),
) -> DataProvider:
    return pm.get_provider(session=db)


def get_store_id(
    store_id: Optional[str] = Query(None),
    x_store_id: Optional[str] = Header(None, alias="X-Store-Id"),
    db: Session = Depends(get_db),
) -> Optional[UUID]:
    sid = store_id or x_store_id
    if sid:
        return UUID(sid)
    first = db.query(Store).first()
    return first.id if first else None
