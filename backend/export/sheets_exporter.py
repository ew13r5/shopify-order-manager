import logging
from typing import Optional
from uuid import UUID

import gspread
from google.oauth2.service_account import Credentials
from sqlalchemy.orm import Session, joinedload

from models import LineItem, Order, Payout, PayoutItem

logger = logging.getLogger(__name__)

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]


class SheetsExporter:
    def __init__(self, credentials_path: str):
        self.credentials_path = credentials_path
        self._client = None

    @property
    def client(self):
        if self._client is None:
            creds = Credentials.from_service_account_file(
                self.credentials_path, scopes=SCOPES
            )
            self._client = gspread.authorize(creds)
        return self._client

    def export(
        self,
        session: Session,
        store_id: UUID,
        spreadsheet_id: str,
    ) -> dict:
        """Export orders, line items, and payouts to 3 Google Sheets tabs."""

        spreadsheet = self.client.open_by_key(spreadsheet_id)

        # --- Sheet 1: Orders ---
        orders = (
            session.query(Order)
            .filter(Order.store_id == store_id)
            .options(joinedload(Order.line_items))
            .order_by(Order.order_created_at.desc())
            .all()
        )

        orders_header = ["Order #", "Date", "Customer", "Email", "Status", "Fulfillment", "Items", "Total"]
        orders_rows = []
        for o in orders:
            orders_rows.append([
                f"#{o.order_number}" if o.order_number else "",
                str(o.order_created_at.date()) if o.order_created_at else "",
                o.customer_name or "",
                o.customer_email or "",
                o.financial_status.value if o.financial_status else "",
                o.fulfillment_status.value if o.fulfillment_status else "",
                len(o.line_items) if o.line_items else 0,
                float(o.total_price) if o.total_price else 0,
            ])

        self._write_sheet(spreadsheet, "Orders", orders_header, orders_rows)
        orders_count = len(orders_rows)

        # --- Sheet 2: Line Items ---
        line_items = (
            session.query(LineItem)
            .join(Order, Order.id == LineItem.order_id)
            .filter(Order.store_id == store_id)
            .order_by(Order.order_created_at.desc())
            .all()
        )

        items_header = [
            "Order #", "Product", "SKU", "Variant", "Qty",
            "Unit Price", "Total", "Discount", "Tax", "Status", "Refund"
        ]
        items_rows = []
        for li in line_items:
            items_rows.append([
                f"#{li.order.order_number}" if li.order and li.order.order_number else "",
                li.title or "",
                li.sku_cleaned or li.sku or "",
                li.variant_title or "",
                li.quantity,
                float(li.unit_price) if li.unit_price else 0,
                float(li.total_price) if li.total_price else 0,
                float(li.discount_amount) if li.discount_amount else 0,
                float(li.tax_amount) if li.tax_amount else 0,
                li.fulfillment_status or "",
                float(li.refund_amount) if li.refund_amount else 0,
            ])

        self._write_sheet(spreadsheet, "Line Items", items_header, items_rows)
        items_count = len(items_rows)

        # --- Sheet 3: Payouts ---
        payout_items = (
            session.query(PayoutItem)
            .join(Payout, Payout.id == PayoutItem.payout_id)
            .filter(Payout.store_id == store_id)
            .options(
                joinedload(PayoutItem.payout),
                joinedload(PayoutItem.line_item),
            )
            .order_by(Payout.date.desc())
            .all()
        )

        payouts_header = [
            "Date", "Product", "SKU", "Qty", "Gross Revenue",
            "Shopify Fees", "Discounts", "Refunds", "Net Payout"
        ]
        payouts_rows = []
        for pi in payout_items:
            li = pi.line_item
            payouts_rows.append([
                str(pi.payout.date) if pi.payout and pi.payout.date else "",
                li.title if li else "",
                li.sku_cleaned or li.sku if li else "",
                li.quantity if li else 0,
                float(pi.gross_amount) if pi.gross_amount else 0,
                float(pi.fee_amount) if pi.fee_amount else 0,
                float(li.discount_amount) if li and li.discount_amount else 0,
                float(li.refund_amount) if li and li.refund_amount else 0,
                float(pi.net_amount) if pi.net_amount else 0,
            ])

        self._write_sheet(spreadsheet, "Payouts", payouts_header, payouts_rows)
        payouts_count = len(payouts_rows)

        return {
            "url": spreadsheet.url,
            "orders": orders_count,
            "line_items": items_count,
            "payouts": payouts_count,
        }

    def _write_sheet(self, spreadsheet, title: str, header: list, rows: list):
        """Write data to a sheet tab, creating it if needed. Clears existing data first."""
        try:
            worksheet = spreadsheet.worksheet(title)
            worksheet.clear()
        except gspread.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title=title, rows=len(rows) + 1, cols=len(header))

        # Batch update: header + all rows in one call
        all_data = [header] + rows
        worksheet.update(range_name="A1", values=all_data)
        logger.info("Sheet '%s': wrote %d rows", title, len(rows))
