from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class ReportCategory(Base):
	__tablename__ = "report_categories"

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
	subject: Mapped[str] = mapped_column(String(255), nullable=False)



