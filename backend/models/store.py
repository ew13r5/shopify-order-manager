from typing import Optional

from cryptography.fernet import Fernet
from sqlalchemy import Boolean, Column, Enum, LargeBinary, String

from database import Base
from models.base import TimestampMixin
from models.enums import DataMode


class Store(TimestampMixin, Base):
    __tablename__ = "stores"

    name = Column(String, nullable=False)
    shopify_domain = Column(String, nullable=True)
    access_token_encrypted = Column(LargeBinary, nullable=True)
    is_demo = Column(Boolean, default=False, nullable=False)
    data_mode = Column(Enum(DataMode), nullable=False, default=DataMode.demo)

    @property
    def access_token(self) -> Optional[str]:
        if self.access_token_encrypted is None:
            return None
        from config import get_settings

        settings = get_settings()
        if not settings.ENCRYPTION_KEY:
            return None
        f = Fernet(settings.ENCRYPTION_KEY.encode())
        return f.decrypt(self.access_token_encrypted).decode()

    @access_token.setter
    def access_token(self, value: Optional[str]):
        if value is None:
            self.access_token_encrypted = None
            return
        from config import get_settings

        settings = get_settings()
        if not settings.ENCRYPTION_KEY:
            raise ValueError("ENCRYPTION_KEY must be set to encrypt tokens")
        f = Fernet(settings.ENCRYPTION_KEY.encode())
        self.access_token_encrypted = f.encrypt(value.encode())
