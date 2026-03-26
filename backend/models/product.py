from sqlalchemy import Column, ForeignKey, Index, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base
from models.base import TimestampMixin


class Product(TimestampMixin, Base):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("store_id", "shopify_id", name="uq_product_store_shopify"),
    )

    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id"), nullable=False, index=True)
    shopify_id = Column(String, nullable=False)
    title = Column(String, nullable=True)
    sku = Column(String, nullable=True)
    sku_cleaned = Column(String, nullable=True)
    variant_title = Column(String, nullable=True)
    variant_sku = Column(String, nullable=True)
    price = Column(Numeric(10, 2), nullable=True)
    image_url = Column(String, nullable=True)

    store = relationship("Store")
