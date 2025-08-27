from sqlalchemy import BigInteger, Column, Integer

from src.core.database import Base


class Media(Base):
    __tablename__ = "media"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    message_id = Column(BigInteger, nullable=False, index=True, unique=True)
