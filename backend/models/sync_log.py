from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship

from database import Base
from models.base import TimestampMixin
from models.enums import SyncStatus


class SyncLog(TimestampMixin, Base):
    __tablename__ = "sync_log"

    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id"), nullable=False)
    started_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)
    orders_synced = Column(Integer, default=0)
    errors = Column(JSON, nullable=True)
    status = Column(Enum(SyncStatus), nullable=False, default=SyncStatus.running)

    store = relationship("Store")
