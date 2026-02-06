# scripts/force_summarize.py
import asyncio
from app.persistence.postgres_repository import PostgresConversationRepository
from app.core.message_service import MessageService

repo = PostgresConversationRepository()
svc = MessageService()
chat_id = 12345  # substitua

# chama o summarizer assincronamente com threshold baixo
async def run():
    await svc.summarize_and_persist(chat_id, repo, threshold=1, keep_last=3)

asyncio.run(run())
print("Feito.")