from sqlalchemy import BigInteger, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class BotSetting(Base):
	__tablename__ = "bot_settings"
	__table_args__ = {
		"mysql_engine": "InnoDB",
		"mysql_charset": "utf8mb4",
		"mysql_collate": "utf8mb4_general_ci",
	}

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
	bot_name: Mapped[str] = mapped_column(String(255), nullable=False, server_default="NashenasBot")
	bot_support_username: Mapped[str] = mapped_column(String(255), nullable=True)
	bot_channel: Mapped[str] = mapped_column(String(255), nullable=True)
	cache_channel_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
	maintenance_mode: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0")


