from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Payment(Base):
	__tablename__ = "payments"
	__table_args__ = {
		"mysql_engine": "InnoDB",
		"mysql_charset": "utf8mb4",
		"mysql_collate": "utf8mb4_general_ci",
	}

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
	user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
	price: Mapped[int] = mapped_column(Integer, nullable=False)
	product: Mapped[str] = mapped_column(String(255), nullable=False)
	authority: Mapped[str] = mapped_column(String(255), nullable=False)
	expired_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
	paid_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
	created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))


