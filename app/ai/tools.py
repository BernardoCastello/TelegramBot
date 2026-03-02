from app.persistence.postgres_repository import PostgresConversationRepository


def search_knowledge_tool(query: str, top_k: int = 5):
    repo = PostgresConversationRepository()
    results = repo.search_knowledge(query, top_k=top_k)

    if not results:
        return {"results": [], "message": "Nenhum conhecimento relevante encontrado."}

    return {
        "results": results
    }


# Definição para o modelo
RAG_TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "search_knowledge",
        "description": "Busca informações sobre o Bernardo, como meios de contato.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Texto para buscar conhecimento relevante"
                },
                "top_k": {
                    "type": "integer",
                    "description": "Quantidade de resultados desejados",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    }
}