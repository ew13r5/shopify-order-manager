import logging

from tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="tasks.export_gsheets")
def export_gsheets_task(self, store_id: str, date_range: dict):
    """Export data to Google Sheets."""
    from database import SessionLocal
    from config import get_settings
    from uuid import UUID

    settings = get_settings()
    if not settings.GOOGLE_SERVICE_ACCOUNT_JSON:
        return {"error": "Google Sheets not configured"}

    session = SessionLocal()
    try:
        from export.sheets_exporter import SheetsExporter

        exporter = SheetsExporter(settings.GOOGLE_SERVICE_ACCOUNT_JSON)

        def progress_callback(current, total):
            self.update_state(
                state="PROGRESS",
                meta={"current": current, "total": total},
            )

        result = exporter.export(
            session, UUID(store_id),
            date_range.get("start"), date_range.get("end"),
            progress_callback=progress_callback,
        )
        return result
    finally:
        session.close()
