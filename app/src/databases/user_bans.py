from sqlalchemy import BigInteger, DateTime, text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class UserBan(Base):
	__tablename__ = "user_bans"
	__table_args__ = {
		"mysql_engine": "InnoDB",
		"mysql_charset": "utf8mb4",
		"mysql_collate": "utf8mb4_general_ci",
	}

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
	user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
	expiry: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
	created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))


