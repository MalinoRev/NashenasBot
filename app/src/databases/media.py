from datetime import datetime
from sqlalchemy import BigInteger, Column, DateTime, Integer
from sqlalchemy.orm import relationship

from src.core.database import Base


class Media(Base):
    __tablename__ = "media"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    message_id = Column(BigInteger, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
