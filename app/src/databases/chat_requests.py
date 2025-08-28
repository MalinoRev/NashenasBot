from datetime import datetime
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from src.core.database import Base


class ChatRequest(Base):
    __tablename__ = 'chat_requests'

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False, index=True)
    target_id = Column(BigInteger, ForeignKey('users.id'), nullable=False, index=True)
    accepted_at = Column(DateTime, nullable=True)
    rejected_at = Column(DateTime, nullable=True)
    canceled_at = Column(DateTime, nullable=True)
    request_message_id = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship('User', foreign_keys=[user_id], backref='sent_chat_requests')
    target = relationship('User', foreign_keys=[target_id], backref='received_chat_requests')
