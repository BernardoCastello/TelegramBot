from sqlalchemy import Column, Integer, Text, String, TIMESTAMP, func, BigInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ConversationMessage(Base):
    __tablename__ = "conversation_messages"
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(BigInteger, index=True)
    role = Column(String(32))
    content = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())