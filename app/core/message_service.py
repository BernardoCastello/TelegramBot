from app.ai.openai_responder import OpenAIResponder


class MessageService:
    def __init__(self):
        self.ai_responder = OpenAIResponder()

    def process_message(self, message: str) -> str:
        try:
            return self.ai_responder.get_response(message)
        except Exception:
            return (
                "Tive um problema ao gerar a resposta agora 😕\n"
                "Pode tentar novamente em alguns instantes?"
            )
