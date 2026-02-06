# scripts/check_and_summarize.py
from app.persistence.postgres_repository import PostgresConversationRepository
from app.ai.openai_responder import OpenAIResponder

repo = PostgresConversationRepository()
chat_id = 12345  # substitua pelo chat_id que você estiver testando

print("count_messages:", repo.count_messages(chat_id))
msgs = repo.get_messages_to_summarize(chat_id, keep_last=3)
print("messages to summarize (count):", len(msgs))
for m in msgs[:5]:
    print(m)

# TESTE: gravar um summary de teste sem chamar a OpenAI
test_summary = "Resumo de teste: este é um resumo criado manualmente."
saved = repo.append_summary(chat_id, test_summary)
print("Summary salvo id:", saved.id, "chat_id:", saved.chat_id)