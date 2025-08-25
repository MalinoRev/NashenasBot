from sqlalchemy import BigInteger, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from src.core.database import Base


class Direct(Base):
	__tablename__ = "directs"

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
	user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
	target_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
	content: Mapped[str] = mapped_column(String(1000), nullable=False)
	opened_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
	created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

	# Relationships
	user = relationship("User", foreign_keys=[user_id], back_populates="sent_directs")
	target = relationship("User", foreign_keys=[target_id], back_populates="received_directs")
