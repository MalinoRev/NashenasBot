from sqlalchemy import BigInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Price(Base):
	__tablename__ = "prices"
	__table_args__ = {
		"mysql_engine": "InnoDB",
		"mysql_charset": "utf8mb4",
		"mysql_collate": "utf8mb4_general_ci",
	}

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
	amount: Mapped[int] = mapped_column(Integer, nullable=False)
	price: Mapped[int] = mapped_column(Integer, nullable=False)



