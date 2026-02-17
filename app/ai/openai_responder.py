from openai import OpenAI
from app.infra.environment import OPENAI_API_KEY
from app.ai.prompts import SYSTEM_PROMPT

class OpenAIResponder:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.system_prompt = SYSTEM_PROMPT

    def get_response(self, user_message: str = None, messages: list = None) -> str:
        if messages is None:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_message}
            ]
        else:
            # Remover mensagens duplicadas
            unique_messages = []
            seen = set()
            for msg in messages:
                msg_content = (msg["role"], msg["content"])
                if msg_content not in seen:
                    unique_messages.append(msg)
                    seen.add(msg_content)
            messages = [{"role": "system", "content": self.system_prompt}] + unique_messages

        print(messages)

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.4,
            max_tokens=300
        )

        return response.choices[0].message.content
