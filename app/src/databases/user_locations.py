from sqlalchemy import BigInteger, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class UserLocation(Base):
	__tablename__ = "user_locations"
	__table_args__ = {
		"mysql_engine": "InnoDB",
		"mysql_charset": "utf8mb4",
		"mysql_collate": "utf8mb4_general_ci",
	}

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
	user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
	location_x: Mapped[float] = mapped_column(Float, nullable=False)
	location_y: Mapped[float] = mapped_column(Float, nullable=False)


