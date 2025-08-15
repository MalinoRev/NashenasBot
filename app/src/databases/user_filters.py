from sqlalchemy import BigInteger, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class UserFilter(Base):
	__tablename__ = "user_filters"
	__table_args__ = {
		"mysql_engine": "InnoDB",
		"mysql_charset": "utf8mb4",
		"mysql_collate": "utf8mb4_general_ci",
	}

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
	user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
	only_males: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
	only_females: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
	same_state: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
	distance_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
	age_from: Mapped[int | None] = mapped_column(Integer, nullable=True)
	age_until: Mapped[int | None] = mapped_column(Integer, nullable=True)


