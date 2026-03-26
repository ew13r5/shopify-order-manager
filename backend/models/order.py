from sqlalchemy import Column, DateTime, Enum, ForeignKey, Index, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base
from models.base import TimestampMixin
from models.enums import FinancialStatus, FulfillmentStatus


class Order(TimestampMixin, Base):
    __tablename__ = "orders"
    __table_args__ = (
        UniqueConstraint("store_id", "shopify_id", name="uq_order_store_shopify"),
        Index("ix_orders_order_created_at", "order_created_at"),
    )

    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id"), nullable=False, index=True)
    shopify_id = Column(String, nullable=False)
    order_number = Column(String, nullable=True)
    customer_name = Column(String, nullable=True)
    customer_email = Column(String, nullable=True)
    status = Column(String, nullable=True)
    financial_status = Column(Enum(FinancialStatus), nullable=True)
    fulfillment_status = Column(Enum(FulfillmentStatus), nullable=True)
    total_price = Column(Numeric(10, 2), nullable=True)
    order_created_at = Column(DateTime(timezone=True), nullable=True)
    order_updated_at = Column(DateTime(timezone=True), nullable=True)

    store = relationship("Store")
    line_items = relationship("LineItem", back_populates="order", cascade="all, delete-orphan")
    adjustments = relationship("Adjustment", back_populates="order")
