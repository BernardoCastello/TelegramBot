from sqlalchemy import Column, Integer, Text, String, TIMESTAMP, func, BigInteger
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from pgvector.sqlalchemy import Vector

Base = declarative_base()


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


class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"

    id = Column(Integer, primary_key=True)
    titulo = Column(Text, nullable=False)
    palavras_principais = Column(ARRAY(Text))
    texto = Column(Text, nullable=False)
    embedding = Column(Vector(1536))