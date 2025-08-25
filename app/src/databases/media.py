from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Media(Base):
	__tablename__ = "media"

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
	message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
