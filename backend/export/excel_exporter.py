import io
from datetime import date
from uuid import UUID

from openpyxl import Workbook
from sqlalchemy.orm import Session

from models import LineItem, Order


class ExcelExporter:
    def export(self, session: Session, store_id: UUID, export_type: str,
               date_from: date, date_to: date) -> io.BytesIO:
        wb = Workbook()
        ws = wb.active
        ws.title = export_type.capitalize()

        if export_type == "orders":
            ws.append(["Order #", "Customer", "Status", "Total", "Date"])
            orders = (session.query(Order).filter(Order.store_id == store_id)
                      .limit(50000).all())
            for o in orders:
                ws.append([
                    o.order_number, o.customer_name,
                    o.financial_status.value if o.financial_status else "",
                    float(o.total_price or 0),
                    str(o.order_created_at or ""),
                ])

        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        return buf
