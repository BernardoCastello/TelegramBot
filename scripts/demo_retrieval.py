from app.persistence.postgres_repository import PostgresConversationRepository


def main():
    repo = PostgresConversationRepository()
    # cria tabelas e extensões (execute uma vez em ambiente de dev)
    #repo.create_tables()
    #repo.enable_vector_extension()
    #repo.create_vector_index()

    print("Inserindo documento de exemplo...")
    kb = repo.add_knowledge(
        titulo="Formas de contato",
        texto="""Os meios de contado do Bernardo são:
        email: becastellosilva@gmail.com
        linkedin: https://www.linkedin.com/in/bernardo-castello-silva
        whatsapp: +55 53 981443623""",
        palavras_principais=["exemplo", "embeddings", "recuperação"],
    )
    print("Inserido ID:", getattr(kb, "id", None))

    print("Buscando por 'contato'...")
    results = repo.search_knowledge("contato", top_k=5)
    for r in results:
        print("-", r["id"], r["titulo"])


if __name__ == "__main__":
    main()
