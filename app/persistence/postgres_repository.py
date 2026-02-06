from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, ConversationMessage
from app.infra.environment import DATABASE_URL

import logging
logger = logging.getLogger(__name__)

class PostgresConversationRepository:
    def __init__(self, database_url: str = None):
        url = database_url or DATABASE_URL
        if not url:
            raise RuntimeError("DATABASE_URL não configurado")
        self.engine = create_engine(url, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)

    def create_tables(self):
        Base.metadata.create_all(bind=self.engine)

    def add_message(self, chat_id: int, role: str, content: str):
        db = self.SessionLocal()
        try:
            msg = ConversationMessage(chat_id=chat_id, role=role, content=content)
            db.add(msg)
            db.commit()
            db.refresh(msg)
            return msg
        except Exception as e:
            logger.exception("Erro ao salvar mensagem no banco")
        finally:
            db.close()

    def get_messages(self, chat_id: int, limit: int = 50):
        db = self.SessionLocal()
        try:
            return (
                db.query(ConversationMessage)
                .filter(ConversationMessage.chat_id == chat_id)
                .order_by(ConversationMessage.created_at.desc())
                .limit(limit)
                .all()
            )
        finally:
            db.close()