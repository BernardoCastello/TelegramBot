from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoResultFound
from .models import Base, ConversationMessage, ConversationSummary
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
    
    def get_last_messages(self, chat_id: int, limit: int = 3):
        db = self.SessionLocal()
        try:
            rows = (
                db.query(ConversationMessage)
                .filter(ConversationMessage.chat_id == chat_id)
                .order_by(ConversationMessage.created_at.desc())
                .limit(limit)
                .all()
            )
            # retornar em ordem cronológica (antigo -> novo)
            return [{"role": r.role, "content": r.content} for r in reversed(rows)]
        finally:
            db.close()

    def get_summary(self, chat_id: int) -> str:
        db = self.SessionLocal()
        try:
            row = db.query(ConversationSummary).filter(ConversationSummary.chat_id == chat_id).one_or_none()
            return row.summary if row else ""
        finally:
            db.close()

    def append_summary(self, chat_id: int, summary: str):
        db = self.SessionLocal()
        try:
            existing = db.query(ConversationSummary).filter(ConversationSummary.chat_id == chat_id).one_or_none()
            if existing:
                existing.summary = (existing.summary + "\n" + summary) if existing.summary else summary
            else:
                existing = ConversationSummary(chat_id=chat_id, summary=summary)
                db.add(existing)
            db.commit()
            db.refresh(existing)
            return existing
        except Exception:
            logger.exception("Erro ao gravar summary")
            raise
        finally:
            db.close()

    def count_messages(self, chat_id: int) -> int:
        db = self.SessionLocal()
        try:
            return db.query(func.count(ConversationMessage.id)).filter(ConversationMessage.chat_id == chat_id).scalar() or 0
        finally:
            db.close()

    def get_messages_to_summarize(self, chat_id: int, keep_last: int = 2):
        db = self.SessionLocal()
        try:
            rows = (
                db.query(ConversationMessage)
                .filter(ConversationMessage.chat_id == chat_id)
                .order_by(ConversationMessage.created_at.asc())
                .all()
            )
            to_summarize = rows[:-keep_last] if len(rows) > keep_last else []
            return [{"role": r.role, "content": r.content} for r in to_summarize]
        finally:
            db.close()

    def delete_messages(self, chat_id: int, keep_last: int = 2):
        db = self.SessionLocal()
        try:
            rows = (
                db.query(ConversationMessage)
                .filter(ConversationMessage.chat_id == chat_id)
                .order_by(ConversationMessage.created_at.asc())
                .all()
            )
            if len(rows) <= keep_last:
                return 0
            to_delete = rows[:-keep_last]
            ids = [r.id for r in to_delete]
            db.query(ConversationMessage).filter(ConversationMessage.id.in_(ids)).delete(synchronize_session=False)
            db.commit()
            return len(ids)
        finally:
            db.close()

    