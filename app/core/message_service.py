import asyncio
import logging
import json

from app.ai.openai_responder import OpenAIResponder
from app.ai.prompts import RESUME_PROMPT
from app.ai.tool_registry import ToolRegistry

logger = logging.getLogger(__name__)

message_memory = 5


class MessageService:

    def __init__(self):
        self.ai_responder = OpenAIResponder()
        self.tool_registry = ToolRegistry()

    def process_message(
        self,
        message: str,
        chat_id: int = None,
        message_repo=None,
        conversation_repo=None
    ) -> str:

        try:
            messages = []

            # 🔹 Inclui resumo salvo
            if conversation_repo and chat_id is not None:
                summary = conversation_repo.get_summary(chat_id)
                if summary:
                    messages.append({
                        "role": "system",
                        "content": f"Resumo da conversa até agora:\n{summary}"
                    })

            # 🔹 Memória curta
            last_msgs = []
            if message_repo and chat_id is not None:
                last_msgs = message_repo.get_last_messages(
                    chat_id,
                    limit=message_memory
                )

            for msg in last_msgs:
                # 🔥 IGNORA mensagens de tool
                if msg.get("role") == "tool":
                    continue

                # 🔥 IGNORA assistant que contém tool_calls antigos
                if msg.get("tool_calls"):
                    continue

                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            

            # 🔹 Nova mensagem do usuário
            if not last_msgs or last_msgs[-1]["content"] != message:
                messages.append({
                    "role": "user",
                    "content": message
                })

            # 🔥 Primeira chamada ao modelo
            resposta = self.ai_responder.get_response(
                messages=messages,
                use_tools=True
            )

            # 🔁 LOOP MULTI-TOOL (agente real)
            while resposta["type"] == "tool_call":

                tool_result = self.tool_registry.execute(
                    resposta["name"],
                    resposta["arguments"]
                )

                # adiciona chamada da tool
                messages.append(resposta["original_message"])

                # adiciona retorno da tool
                messages.append({
                    "role": "tool",
                    "tool_call_id": resposta["tool_call_id"],
                    "content": json.dumps(tool_result)
                })

                # chama modelo novamente
                resposta = self.ai_responder.get_response(
                    messages=messages,
                    use_tools=False
                )

            # 🔹 Conteúdo final
            final_content = resposta["content"]

            # 🔹 Incrementa contador para summary
            if conversation_repo and chat_id is not None:

                conversation_repo.increment_message_count(chat_id)

                message_count = conversation_repo.get_message_count(chat_id) or 0

                if message_count >= message_memory:
                    print(f"🔄 Gerando resumo após {message_count} mensagens para chat_id {chat_id}")

                    asyncio.create_task(
                        self.summarize_and_persist(
                            chat_id,
                            message_repo,
                            conversation_repo
                        )
                    )

                    conversation_repo.reset_message_count(chat_id)

            return final_content

        except Exception:
            logger.exception("Erro ao processar mensagem")
            return (
                "Tive um problema ao gerar a resposta agora 😕\n"
                "Pode tentar novamente em alguns instantes?"
            )


    async def summarize_and_persist(
        self,
        chat_id: int,
        message_repo,
        conversation_repo,
        threshold: int = message_memory,
        keep_last: int = 3
    ):
        await asyncio.to_thread(
            self._summarize_blocking,
            chat_id,
            message_repo,
            conversation_repo,
            threshold,
            keep_last
        )

    def _summarize_blocking(
        self,
        chat_id: int,
        message_repo,
        conversation_repo,
        threshold: int,
        keep_last: int
    ):
        try:

            count = message_repo.count_messages(chat_id) if message_repo else 0

            if count < threshold:
                return

            msgs = (
                message_repo.get_messages_to_summarize(
                    chat_id,
                    keep_last=keep_last
                )
                if message_repo
                else []
            )

            if not msgs:
                return

            # 🔹 Prompt dedicado de resumo
            prompt_messages = [
                {"role": "system", "content": RESUME_PROMPT}
            ] + msgs

            # 🔥 Resumo NÃO usa tools
            summary_response = self.ai_responder.get_response(
                messages=prompt_messages,
                use_tools=False
            )

            summary_text = summary_response["content"]

            if conversation_repo:
                conversation_repo.append_summary(chat_id, summary_text)

            # Opcional: limpar mensagens antigas
            # if message_repo:
            #     message_repo.delete_messages(chat_id, keep_last=keep_last)

        except Exception:
            logger.exception("Erro ao sumarizar conversa")