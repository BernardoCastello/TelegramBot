from app.persistence.postgres_repository import PostgresConversationRepository

if __name__ == "__main__":
    repo = PostgresConversationRepository()
    repo.enable_vector_extension()
    repo.create_tables()
    repo.create_vector_index()
    print("Banco Criado")
