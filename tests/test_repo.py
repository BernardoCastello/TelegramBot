from app.persistence.postgres_repository import PostgresConversationRepository

repo = PostgresConversationRepository()
repo.create_tables()
msg = repo.add_message(12345, "user", "mensagem de teste")
print("Salvo:", msg.id, msg.chat_id, msg.role)
rows = repo.get_messages(12345, limit=10)
print("Encontrado:", len(rows))