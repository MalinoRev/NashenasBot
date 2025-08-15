from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class UserProfile(Base):
	__tablename__ = "user_profiles"
	__table_args__ = {
		"mysql_engine": "InnoDB",
		"mysql_charset": "utf8mb4",
		"mysql_collate": "utf8mb4_general_ci",
	}

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
	user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
	name: Mapped[str | None] = mapped_column(String(255), nullable=True)
	is_female: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
	age: Mapped[int | None] = mapped_column(Integer, nullable=True)
	state: Mapped[int | None] = mapped_column(Integer, ForeignKey("states.id"), nullable=True)
	city: Mapped[int | None] = mapped_column(Integer, ForeignKey("cities.id"), nullable=True)
	show_filter_message: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0")


