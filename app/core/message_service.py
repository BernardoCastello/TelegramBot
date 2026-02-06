import asyncio
from app.ai.openai_responder import OpenAIResponder

class MessageService:
    def __init__(self):
        self.ai_responder = OpenAIResponder()

    def process_message(self, message: str, chat_id: int = None, conversation_repo=None) -> str:
        try:
            messages = []

            # incluir resumo salvo como system
            if conversation_repo and chat_id is not None:
                summary = conversation_repo.get_summary(chat_id)
                if summary:
                    messages.append({
                        "role": "system",
                        "content": f"Resumo da conversa até agora:\n{summary}"
                    })

                # memória curta do BD: últimas 3 mensagens
                last_msgs = conversation_repo.get_last_messages(chat_id, limit=3)
                messages.extend(last_msgs)

            messages.append({"role": "user", "content": message})

            resposta = self.ai_responder.get_response(messages=messages)
            return resposta
        except Exception:
            return (
                "Tive um problema ao gerar a resposta agora 😕\n"
                "Pode tentar novamente em alguns instantes?"
            )

    # método async que roda em background e faz a sumarização (chama OpenAI via thread)
    async def summarize_and_persist(self, chat_id: int, conversation_repo, threshold: int = 20, keep_last: int = 3):
        # roda a versão bloqueante em thread para não travar o loop
        await asyncio.to_thread(self._summarize_blocking, chat_id, conversation_repo, threshold, keep_last)

    def _summarize_blocking(self, chat_id: int, conversation_repo, threshold: int, keep_last: int):
        try:
            count = conversation_repo.count_messages(chat_id)
            if count < threshold:
                return

            msgs = conversation_repo.get_messages_to_summarize(chat_id, keep_last=keep_last)
            if not msgs:
                return

            # montar prompt de sumarização
            system = {"role": "system", "content": "Resuma a conversa abaixo em 3-5 frases claras."}
            prompt_messages = [system] + msgs

            summary_text = self.ai_responder.get_response(messages=prompt_messages)

            conversation_repo.append_summary(chat_id, summary_text)

            # opcional: remover mensagens resumidas para manter short-memory pequena
            conversation_repo.delete_messages(chat_id, keep_last=keep_last)
        except Exception:
            # registre/exponha erro conforme necessário
            import logging
            logging.exception("Erro ao sumarizar conversa")