import csv
import io
from datetime import date
from typing import Generator, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from models import LineItem, Order, Payout, PayoutItem


ORDERS_COLUMNS = ["order_number", "customer_name", "customer_email", "status",
                  "financial_status", "fulfillment_status", "total_price", "created_at"]

ITEMS_COLUMNS = ["order_number", "title", "sku", "sku_cleaned",
                 "variant_title", "quantity", "unit_price", "total_price",
                 "discount_amount", "tax_amount", "refund_amount", "fulfillment_status"]

PAYOUTS_COLUMNS = ["payout_date", "payout_status", "gross_amount", "fee_amount", "net_amount"]


class CSVExporter:
    def export_orders(self, session: Session, store_id: UUID,
                      date_from: date, date_to: date) -> Generator[str, None, None]:
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(ORDERS_COLUMNS)
        yield buf.getvalue()
        buf.truncate(0)
        buf.seek(0)

        orders = (session.query(Order).filter(Order.store_id == store_id)
                  .order_by(Order.order_created_at.desc()).limit(50000).all())
        for o in orders:
            writer.writerow([
                o.order_number, o.customer_name, o.customer_email, o.status,
                o.financial_status.value if o.financial_status else "",
                o.fulfillment_status.value if o.fulfillment_status else "",
                str(o.total_price or ""), str(o.order_created_at or ""),
            ])
            yield buf.getvalue()
            buf.truncate(0)
            buf.seek(0)

    def export_items(self, session: Session, store_id: UUID,
                     date_from: date, date_to: date) -> Generator[str, None, None]:
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(ITEMS_COLUMNS)
        yield buf.getvalue()
        buf.truncate(0)
        buf.seek(0)

        items = (session.query(LineItem).join(Order)
                 .filter(Order.store_id == store_id).limit(50000).all())
        for li in items:
            writer.writerow([
                "", li.title, li.sku, li.sku_cleaned,
                li.variant_title, li.quantity, str(li.unit_price or ""),
                str(li.total_price or ""), str(li.discount_amount or ""),
                str(li.tax_amount or ""), str(li.refund_amount or ""),
                li.fulfillment_status,
            ])
            yield buf.getvalue()
            buf.truncate(0)
            buf.seek(0)
