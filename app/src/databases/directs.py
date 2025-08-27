from datetime import datetime
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship

from src.core.database import Base


class Direct(Base):
    __tablename__ = "directs"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    target_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    content = Column(JSON, nullable=False)  # تغییر از Text به JSON
    opened_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="sent_directs")
    target = relationship("User", foreign_keys=[target_id], backref="received_directs")
