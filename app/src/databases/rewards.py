from sqlalchemy import BigInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Reward(Base):
	__tablename__ = "rewards"
	__table_args__ = {
		"mysql_engine": "InnoDB",
		"mysql_charset": "utf8mb4",
		"mysql_collate": "utf8mb4_general_ci",
	}

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
	invite_amount: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
	profile_amount: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")



