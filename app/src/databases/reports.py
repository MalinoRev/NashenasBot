from sqlalchemy import BigInteger, DateTime, ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Report(Base):
	__tablename__ = "reports"
	__table_args__ = {
		"mysql_engine": "InnoDB",
		"mysql_charset": "utf8mb4",
		"mysql_collate": "utf8mb4_unicode_ci",
	}

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
	category_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("report_categories.id"), nullable=True)
	user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
	target_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
	admin_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("admins.id"), nullable=True)
	reason: Mapped[str] = mapped_column(String(255), nullable=False)
	approved_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
	rejected_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
	created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))



