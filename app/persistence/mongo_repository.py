from pymongo import MongoClient, ASCENDING
from datetime import datetime
from typing import List, Dict, Any
from app.infra.environment import MONGODB_URI
import logging

logger = logging.getLogger(__name__)


class MongoConversationRepository:
    def __init__(self, uri: str = None, db_name: str = "telegrambot"):
        uri = uri or MONGODB_URI
        if not uri:
            raise RuntimeError("MONGODB_URI não configurado")
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db["conversation_messages"]
        # ensure index on chat_id
        try:
            self.collection.create_index([("chat_id", ASCENDING)], unique=True)
        except Exception:
            logger.exception("Erro ao criar índice no MongoDB")

    def add_message(self, chat_id: int, role: str, content: str) -> Dict[str, Any]:
        msg = {"role": role, "content": content, "created_at": datetime.utcnow()}
        try:
            res = self.collection.update_one(
                {"chat_id": int(chat_id)},
                {
                    "$push": {"messages": msg},
                    "$setOnInsert": {"created_at": datetime.utcnow()}
                },
                upsert=True,
            )
            # return the pushed message for convenience
            return msg
        except Exception:
            logger.exception("Erro ao inserir mensagem no MongoDB")

    def get_last_messages(self, chat_id: int, limit: int = 3) -> List[Dict[str, str]]:
        try:
            doc = self.collection.find_one({"chat_id": int(chat_id)}, {"messages": {"$slice": -limit}})
            if not doc or "messages" not in doc:
                return []
            # Projection with $slice (negative) returns last N elements in chronological order
            return [{"role": m["role"], "content": m["content"]} for m in doc["messages"]]
        except Exception:
            logger.exception("Erro ao buscar últimas mensagens do MongoDB")
            return []

    def count_messages(self, chat_id: int) -> int:
        try:
            doc = self.collection.find_one({"chat_id": int(chat_id)}, {"messages": 1})
            if not doc or "messages" not in doc:
                return 0
            return len(doc["messages"])
        except Exception:
            logger.exception("Erro ao contar mensagens no MongoDB")
            return 0

    def get_messages_to_summarize(self, chat_id: int, keep_last: int = 2) -> List[Dict[str, str]]:
        try:
            doc = self.collection.find_one({"chat_id": int(chat_id)}, {"messages": 1})
            if not doc or "messages" not in doc:
                return []
            msgs = doc["messages"]
            to_summarize = msgs[:-keep_last] if len(msgs) > keep_last else []
            return [{"role": m["role"], "content": m["content"]} for m in to_summarize]
        except Exception:
            logger.exception("Erro ao montar lista para sumarizar no MongoDB")
            return []

    def delete_messages(self, chat_id: int, keep_last: int = 2) -> int:
        try:
            doc = self.collection.find_one({"chat_id": int(chat_id)}, {"messages": 1})
            if not doc or "messages" not in doc:
                return 0
            msgs = doc["messages"]
            if len(msgs) <= keep_last:
                return 0
            remaining = msgs[-keep_last:]
            res = self.collection.update_one({"chat_id": int(chat_id)}, {"$set": {"messages": remaining}})
            # quantidade removida
            return len(msgs) - len(remaining)
        except Exception:
            logger.exception("Erro ao deletar mensagens no MongoDB")
            return 0
