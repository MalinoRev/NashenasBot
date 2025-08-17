from sqlalchemy import BigInteger, DateTime, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Like(Base):
	__tablename__ = "likes"
	__table_args__ = {
		"mysql_engine": "InnoDB",
		"mysql_charset": "utf8mb4",
		"mysql_collate": "utf8mb4_general_ci",
	}

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
	user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
	target_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
	created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))



