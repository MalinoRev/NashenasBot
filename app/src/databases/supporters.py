from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class Supporter(Base):
	__tablename__ = "supporters"
	__table_args__ = {
		"mysql_engine": "InnoDB",
		"mysql_charset": "utf8mb4",
		"mysql_collate": "utf8mb4_general_ci",
	}

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
	user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)

	# Relationship
	user: Mapped["User"] = relationship("User", back_populates="supporters")
