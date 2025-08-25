from sqlalchemy import BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from src.core.database import Base


class ChatRequest(Base):
	__tablename__ = "chat_requests"

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
	user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
	target_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
	accepted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
	rejected_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
	created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

	# Relationships
	user = relationship("User", foreign_keys=[user_id], back_populates="sent_chat_requests")
	target = relationship("User", foreign_keys=[target_id], back_populates="received_chat_requests")
