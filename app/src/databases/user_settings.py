from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class UserSetting(Base):
	__tablename__ = "user_settings"
	__table_args__ = {
		"mysql_engine": "InnoDB",
		"mysql_charset": "utf8mb4",
		"mysql_collate": "utf8mb4_general_ci",
	}

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
	user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
	silented_until: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
	profile_visit_alarm: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0")
	profile_like_alarm: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0")
	can_get_likes: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="1")


