from openai import OpenAI
from app.infra.environment import OPENAI_API_KEY
from app.ai.prompts import SYSTEM_PROMPT
from app.ai.tools import RAG_TOOL_DEFINITION
import json


class OpenAIResponder:

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.system_prompt = SYSTEM_PROMPT

    def get_response(self, messages: list, use_tools: bool = True):

        sanitized_messages = []

        for msg in messages:
            new_msg = msg.copy()

            if "content" in new_msg and new_msg["content"] is None:
                new_msg["content"] = ""

            sanitized_messages.append(new_msg)

        final_messages = [
            {"role": "system", "content": self.system_prompt}
        ] + sanitized_messages

        request_params = {
            "model": "gpt-4o-mini",
            "messages": final_messages,
            "temperature": 0.3,
        }

        if use_tools:
            request_params["tools"] = [RAG_TOOL_DEFINITION]
            request_params["tool_choice"] = "auto"

        import json

        print("\n================ MENSAGENS ENVIADAS PARA OPENAI ================\n")
        print(json.dumps(final_messages, indent=2, ensure_ascii=False))
        print("\n===============================================================\n")

        response = self.client.chat.completions.create(**request_params)

        message = response.choices[0].message

        # 🔥 TOOL CALL
        if message.tool_calls:

            tool_call = message.tool_calls[0]

            assistant_message = {
                "role": "assistant",
                "content": "",  # 🔥 NUNCA pode ser None
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    }
                ]
            }

            return {
                "type": "tool_call",
                "tool_call_id": tool_call.id,
                "name": tool_call.function.name,
                "arguments": json.loads(tool_call.function.arguments),
                "original_message": assistant_message
            }

        # 🔹 RESPOSTA NORMAL
        return {
            "type": "text",
            "content": message.content or ""
        }