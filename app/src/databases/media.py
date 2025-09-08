from sqlalchemy import BigInteger, Column, Integer

from src.core.database import Base


class Media(Base):
    __tablename__ = "media"
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    message_id = Column(BigInteger, nullable=False, index=True, unique=True)
