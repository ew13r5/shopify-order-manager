from sqlalchemy import Column, Date, Enum, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base
from models.base import TimestampMixin
from models.enums import PayoutStatus


class Payout(TimestampMixin, Base):
    __tablename__ = "payouts"
    __table_args__ = (
        UniqueConstraint("store_id", "shopify_payout_id", name="uq_payout_store_shopify"),
    )

    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id"), nullable=False)
    shopify_payout_id = Column(String, nullable=True)
    date = Column(Date, nullable=True)
    amount = Column(Numeric(10, 2), nullable=True)
    status = Column(Enum(PayoutStatus), nullable=True)

    store = relationship("Store")
    items = relationship("PayoutItem", back_populates="payout", cascade="all, delete-orphan")


class PayoutItem(TimestampMixin, Base):
    __tablename__ = "payout_items"

    payout_id = Column(UUID(as_uuid=True), ForeignKey("payouts.id"), nullable=False)
    line_item_id = Column(UUID(as_uuid=True), ForeignKey("line_items.id"), nullable=True)
    gross_amount = Column(Numeric(10, 2), nullable=True)
    fee_amount = Column(Numeric(10, 2), nullable=True)
    net_amount = Column(Numeric(10, 2), nullable=True)

    payout = relationship("Payout", back_populates="items")
    line_item = relationship("LineItem")
