from sqlalchemy import Column, Enum, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base
from models.base import TimestampMixin
from models.enums import AdjustmentType


class Adjustment(TimestampMixin, Base):
    __tablename__ = "adjustments"

    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id"), nullable=False)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=True)
    type = Column(Enum(AdjustmentType), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    reason = Column(Text, nullable=True)

    store = relationship("Store")
    order = relationship("Order", back_populates="adjustments")
