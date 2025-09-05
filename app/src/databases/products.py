from sqlalchemy import BigInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Product(Base):
	__tablename__ = "products"
	__table_args__ = {
		"mysql_engine": "InnoDB",
		"mysql_charset": "utf8mb4",
		"mysql_collate": "utf8mb4_general_ci",
	}

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
	unban_price: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
	delete_account_price: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
	vip_rank_price: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
	# Number of days for VIP validity
	vip_rank_time: Mapped[int] = mapped_column(Integer, nullable=False, server_default="30")




