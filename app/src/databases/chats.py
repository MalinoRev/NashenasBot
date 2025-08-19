from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Chat(Base):
	__tablename__ = "chats"
	__table_args__ = {
		"mysql_engine": "InnoDB",
		"mysql_charset": "utf8mb4",
		"mysql_collate": "utf8mb4_general_ci",
	}

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
	user1_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
	user2_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
	secure_chat: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0")
	ended_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
	created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))


