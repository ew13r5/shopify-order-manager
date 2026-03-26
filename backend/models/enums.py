import enum


class FinancialStatus(str, enum.Enum):
    pending = "pending"
    authorized = "authorized"
    partially_paid = "partially_paid"
    paid = "paid"
    partially_refunded = "partially_refunded"
    refunded = "refunded"
    voided = "voided"


class FulfillmentStatus(str, enum.Enum):
    fulfilled = "fulfilled"
    unfulfilled = "unfulfilled"
    partial = "partial"
    restocked = "restocked"


class PayoutStatus(str, enum.Enum):
    scheduled = "scheduled"
    in_transit = "in_transit"
    paid = "paid"
    failed = "failed"
    cancelled = "cancelled"


class AdjustmentType(str, enum.Enum):
    refund = "refund"
    chargeback = "chargeback"
    correction = "correction"


class SyncStatus(str, enum.Enum):
    running = "running"
    completed = "completed"
    failed = "failed"


class DataMode(str, enum.Enum):
    shopify = "shopify"
    demo = "demo"
