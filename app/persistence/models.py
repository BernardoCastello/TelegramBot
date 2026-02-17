from sqlalchemy import Column, Integer, Text, String, TIMESTAMP, func, BigInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ConversationMessage(Base):
    __tablename__ = "conversation_messages"
    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger, index=True, nullable=False)
    role = Column(String(32), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )


class ConversationSummary(Base):
    __tablename__ = "conversation_summaries"
    chat_id = Column(BigInteger, primary_key=True, nullable=False)
    message_count = Column(Integer, nullable=False)
    summary = Column(Text)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )