from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class City(Base):
	__tablename__ = "cities"
	__table_args__ = {
		"mysql_engine": "InnoDB",
		"mysql_charset": "utf8mb4",
		"mysql_collate": "utf8mb4_general_ci",
	}

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	state_id: Mapped[int] = mapped_column(Integer, ForeignKey("states.id"), nullable=False)
	city_name: Mapped[str] = mapped_column(String(255), nullable=False)


