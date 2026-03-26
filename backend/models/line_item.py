from sqlalchemy import Column, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base
from models.base import TimestampMixin


class LineItem(TimestampMixin, Base):
    __tablename__ = "line_items"
    __table_args__ = (
        Index("ix_line_items_sku_cleaned", "sku_cleaned"),
    )

    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True)
    shopify_id = Column(String, nullable=True)
    title = Column(String, nullable=True)
    sku = Column(String, nullable=True)
    sku_cleaned = Column(String, nullable=True)
    variant_title = Column(String, nullable=True)
    variant_sku = Column(String, nullable=True)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(10, 2), nullable=True)
    total_price = Column(Numeric(10, 2), nullable=True)
    discount_amount = Column(Numeric(10, 2), default=0)
    tax_amount = Column(Numeric(10, 2), default=0)
    fulfillment_status = Column(String, nullable=True)
    refund_amount = Column(Numeric(10, 2), default=0)

    order = relationship("Order", back_populates="line_items")
    product = relationship("Product")
