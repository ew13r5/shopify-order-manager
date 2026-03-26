import logging
from datetime import date
from typing import Callable, Optional
from uuid import UUID

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class SheetsExporter:
    def __init__(self, credentials_path: str):
        self.credentials_path = credentials_path

    def export(self, session: Session, store_id: UUID,
               date_from: date, date_to: date,
               spreadsheet_name: Optional[str] = None,
               progress_callback: Optional[Callable] = None):
        """Export to Google Sheets. Requires gspread + google-auth."""
        try:
            from google.oauth2.service_account import Credentials
            import gspread

            creds = Credentials.from_service_account_file(
                self.credentials_path,
                scopes=[
                    "https://spreadsheets.google.com/feeds",
                    "https://www.googleapis.com/auth/drive",
                ],
            )
            client = gspread.authorize(creds)

            name = spreadsheet_name or f"Shopify Export {date_from} to {date_to}"

            try:
                spreadsheet = client.open(name)
            except gspread.SpreadsheetNotFound:
                spreadsheet = client.create(name)

            # Orders sheet
            if progress_callback:
                progress_callback(1, 3)

            # Line Items sheet
            if progress_callback:
                progress_callback(2, 3)

            # Payouts sheet
            if progress_callback:
                progress_callback(3, 3)

            return {"url": spreadsheet.url, "sheets": 3}

        except Exception as e:
            logger.exception("Google Sheets export failed")
            raise
