import asyncio
import logging
from app.ai.openai_responder import OpenAIResponder
from app.ai.prompts import RESUME_PROMPT

logger = logging.getLogger(__name__)

message_memory = 3

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

                # memória curta do BD: últimas mensagens
                last_msgs = conversation_repo.get_last_messages(chat_id, limit=message_memory)
                messages.extend(last_msgs)

            messages.append({"role": "user", "content": message})

            resposta = self.ai_responder.get_response(messages=messages)

            # Incrementa o contador de mensagens
            conversation_repo.increment_message_count(chat_id)
            # Verifica se é hora de gerar o resumo
            message_count = conversation_repo.get_message_count(chat_id) or 0
            if message_count >= message_memory:
                print(f"🔄 Gerando resumo após {message_count} mensagens para chat_id {chat_id}")
                asyncio.create_task(self.summarize_and_persist(chat_id, conversation_repo))
                conversation_repo.reset_message_count(chat_id)

            return resposta
        except Exception as e:
            logger.exception("Erro ao processar mensagem")
            return (
                "Tive um problema ao gerar a resposta agora 😕\n"
                "Pode tentar novamente em alguns instantes?"
            )

    async def summarize_and_persist(self, chat_id: int, conversation_repo, threshold: int = message_memory, keep_last: int = 3):
        await asyncio.to_thread(self._summarize_blocking, chat_id, conversation_repo, threshold, keep_last)

    def _summarize_blocking(self, chat_id: int, conversation_repo, threshold: int, keep_last: int):
        print("-=-=-=-==-="*10)
        print("AKI FOI FEITO UM RESUMO!!!!!")
        try:
            count = conversation_repo.count_messages(chat_id)
            if count < threshold:
                return

            msgs = conversation_repo.get_messages_to_summarize(chat_id, keep_last=keep_last)
            if not msgs:
                return

            system = {"role": "system", "content":  RESUME_PROMPT}
            prompt_messages = [system] + msgs

            summary_text = self.ai_responder.get_response(messages=prompt_messages)

            conversation_repo.append_summary(chat_id, summary_text)
            #conversation_repo.delete_messages(chat_id, keep_last=keep_last)
        except Exception:
            logging.exception("Erro ao sumarizar conversa")