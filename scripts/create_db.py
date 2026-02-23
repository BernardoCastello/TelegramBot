from app.persistence.postgres_repository import PostgresConversationRepository
from app.persistence.mongo_repository import MongoConversationRepository


if __name__ == "__main__":
    try:
        repo = PostgresConversationRepository()
        repo.enable_vector_extension()
        repo.create_tables()
        repo.create_vector_index()
        print("Postgres: tabelas e índices criados")
    except Exception as e:
        print(f"Aviso: não foi possível inicializar Postegres:\n {e}")

    # Inicializa MongoDB (cria coleção e índices)
    try:
        mongo_repo = MongoConversationRepository()
        print("MongoDB: coleção/índices verificados/criados")
    except Exception as e:
        print(f"Aviso: não foi possível inicializar MongoDB:\n {e}")

    print("Banco Criado")
