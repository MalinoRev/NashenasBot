from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class RequestedChannel(Base):
	__tablename__ = "requested_channels"
	__table_args__ = {
		"mysql_engine": "InnoDB",
		"mysql_charset": "utf8mb4",
		"mysql_collate": "utf8mb4_general_ci",
	}

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	channel_id: Mapped[str] = mapped_column(String(255), nullable=False)
