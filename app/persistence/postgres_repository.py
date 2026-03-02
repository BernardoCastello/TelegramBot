from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoResultFound
from sqlalchemy.sql import text
from .models import Base, ConversationSummary
from .models import KnowledgeBase
from app.infra.environment import DATABASE_URL

import logging
logger = logging.getLogger(__name__)
from app.ai.embeddings import Embeddings

class PostgresConversationRepository:
    def __init__(self, database_url: str = None):
        url = database_url or DATABASE_URL
        if not url:
            raise RuntimeError("DATABASE_URL não configurado")
        self.engine = create_engine(url, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)

    def create_tables(self):
        Base.metadata.create_all(bind=self.engine)

    def enable_vector_extension(self):
        try:
            with self.engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                conn.commit()
        except Exception:
            logger.exception("Erro ao habilitar extensão pgvector")

    def create_vector_index(self):
        try:
            with self.engine.connect() as conn:
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS knowledge_base_embedding_idx
                    ON knowledge_base
                    USING ivfflat (embedding vector_cosine_ops)
                    WITH (lists = 100);
                """))
                conn.commit()
        except Exception:
            logger.exception("Erro ao criar índice vetorial")


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


    def increment_message_count(self, chat_id: int):
        db = self.SessionLocal()
        try:
            db.execute(
                text("""
                    INSERT INTO conversation_summaries (chat_id, message_count)
                    VALUES (:chat_id, 1)
                    ON CONFLICT (chat_id)
                    DO UPDATE
                    SET message_count = conversation_summaries.message_count + 1
                """),
                {"chat_id": chat_id}
            )
            db.commit()
        finally:
            db.close()


    def reset_message_count(self, chat_id: int):
        db = self.SessionLocal()
        try:
            db.execute(
                text("""
                    INSERT INTO conversation_summaries (chat_id, message_count)
                    VALUES (:chat_id, 0)
                    ON CONFLICT (chat_id)
                    DO UPDATE
                    SET message_count = 0
                """),
                {"chat_id": chat_id}
            )
            db.commit()
        finally:
            db.close()


    def get_message_count(self, chat_id: int) -> int:
        """Retorna o contador de mensagens para o chat."""
        db = self.SessionLocal()
        try:
            result = db.execute(
                text(
                    """
                    SELECT message_count
                    FROM conversation_summaries
                    WHERE chat_id = :chat_id
                    """
                ),
                {"chat_id": chat_id}
            ).fetchone()
            return result[0] if result else 0
        finally:
            db.close()

    def add_knowledge(self, titulo: str, texto: str, palavras_principais: list | None = None):
        """Gera embedding e insere um registro na tabela `knowledge_base`."""
        emb = Embeddings().generate_embedding(texto)
        db = self.SessionLocal()
        try:
            kb = KnowledgeBase(
                titulo=titulo,
                palavras_principais=palavras_principais or [],
                texto=texto,
                embedding=emb,
            )
            db.add(kb)
            db.commit()
            db.refresh(kb)
            return kb
        except Exception:
            logger.exception("Erro ao inserir conhecimento na base")
            raise
        finally:
            db.close()

    def _vector_literal(self, vector: list) -> str:
        """Converte lista de floats em literal SQL ARRAY[...] para uso em queries.

        Nota: o vetor é inserido diretamente no SQL porque o driver não faz bind
        automático para o tipo `vector` do pgvector aqui.
        """
        vals = ",".join((str(float(x)) for x in vector))
        return f"ARRAY[{vals}]"

    def search_knowledge(self, query: str, top_k: int = 5):
        """Busca os `top_k` documentos mais similares ao `query` usando pgvector.

        Retorna lista de dicionários com chaves: id, titulo, texto, palavras_principais.
        """
        emb = Embeddings().generate_embedding(query)
        vec_sql = self._vector_literal(emb)
        sql = f"""
            SELECT id, titulo, texto, palavras_principais
            FROM knowledge_base
            ORDER BY embedding <-> {vec_sql}::vector
            LIMIT :k
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql), {"k": top_k}).fetchall()
                records = []
                for row in result:
                    records.append({
                        "id": row[0],
                        "titulo": row[1],
                        "texto": row[2],
                        "palavras_principais": row[3],
                    })
                    #print(f"Chamou retrieval:{records}")
                return records
        except Exception:
            logger.exception("Erro ao buscar na knowledge_base")
            return []

    