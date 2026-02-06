from app.persistence.postgres_repository import PostgresConversationRepository

if __name__ == "__main__":
    repo = PostgresConversationRepository()
    repo.create_tables()
    print("Tabelas criadas")