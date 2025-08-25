from sqlalchemy import BigInteger, Boolean, DateTime, Float, ForeignKey, Integer, text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class ChatQueue(Base):
	__tablename__ = "chat_queue"
	__table_args__ = {
		"mysql_engine": "InnoDB",
		"mysql_charset": "utf8mb4",
		"mysql_collate": "utf8mb4_general_ci",
	}

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
	user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
	user_location_x: Mapped[float | None] = mapped_column(Float, nullable=True)
	user_location_y: Mapped[float | None] = mapped_column(Float, nullable=True)
	user_state_id: Mapped[int] = mapped_column(Integer, ForeignKey("states.id"), nullable=False)
	user_city_id: Mapped[int] = mapped_column(Integer, ForeignKey("cities.id"), nullable=False)
	user_age: Mapped[int] = mapped_column(Integer, nullable=False)
	message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
	user_is_boy: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0")
	user_is_girl: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0")
	filter_age_range_from: Mapped[int | None] = mapped_column(Integer, nullable=True)
	filter_age_range_until: Mapped[int | None] = mapped_column(Integer, nullable=True)
	filter_location_distance: Mapped[int | None] = mapped_column(Integer, nullable=True)
	filter_only_boy: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0")
	filter_only_girl: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0")
	filter_only_state: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0")
	filter_only_city: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0")
	created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))



