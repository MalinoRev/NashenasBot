from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class User(Base):
	__tablename__ = "users"
	__table_args__ = {
		"mysql_engine": "InnoDB",
		"mysql_charset": "utf8mb4",
		"mysql_collate": "utf8mb4_general_ci",
	}

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
	user_id: Mapped[int | None] = mapped_column(BigInteger, unique=True, nullable=False)
	tg_name: Mapped[str | None] = mapped_column(String(255), nullable=False)
	credit: Mapped[int] = mapped_column(BigInteger, nullable=False, server_default="0")
	chat_counter: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
	unique_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=False)
	referral_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=False)
	referraled_by: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
	last_activity: Mapped[DateTime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
	step: Mapped[str | None] = mapped_column(String(255), nullable=False)
	created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
	can_get_likes: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="1")

	# Relationships
	sent_directs = relationship("Direct", foreign_keys="Direct.user_id", back_populates="user")
	received_directs = relationship("Direct", foreign_keys="Direct.target_id", back_populates="target")
	sent_chat_requests = relationship("ChatRequest", foreign_keys="ChatRequest.user_id", back_populates="user")
	received_chat_requests = relationship("ChatRequest", foreign_keys="ChatRequest.target_id", back_populates="target")


