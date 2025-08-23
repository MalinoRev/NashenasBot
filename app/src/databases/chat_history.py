from sqlalchemy import BigInteger, DateTime, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class ChatHistory(Base):
	__tablename__ = "chat_history"
	__table_args__ = {
		"mysql_engine": "InnoDB",
		"mysql_charset": "utf8mb4",
		"mysql_collate": "utf8mb4_general_ci",
	}

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
	user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
	target_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
	chat_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("chats.id"), nullable=False)
	received_message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
	sent_message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
	created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))



