from collections import defaultdict, deque

class ConversationMemory:
    def __init__(self, max_messages: int = 6):
        self.max_messages = max_messages
        self.short_memory = defaultdict(
            lambda: deque(maxlen=self.max_messages)
        )
        self.long_summary = defaultdict(str)

    def add_message(self, chat_id: int, role: str, content: str):
        self.short_memory[chat_id].append({
            "role": role,
            "content": content
        })

    def needs_summarization(self, chat_id: int) -> bool:
        return len(self.short_memory[chat_id]) >= self.max_messages

    def pop_old_messages(self, chat_id: int, keep_last: int = 3):
        messages = list(self.short_memory[chat_id])
        to_summarize = messages[:-keep_last]
        self.short_memory[chat_id].clear()

        for msg in messages[-keep_last:]:
            self.short_memory[chat_id].append(msg)

        return to_summarize

    def append_summary(self, chat_id: int, summary: str):
        if self.long_summary[chat_id]:
            self.long_summary[chat_id] += "\n" + summary
        else:
            self.long_summary[chat_id] = summary

    def get_context(self, chat_id: int):
        context = []

        if self.long_summary[chat_id]:
            context.append({
                "role": "system",
                "content": (
                    "Resumo da conversa até agora:\n"
                    f"{self.long_summary[chat_id]}"
                )
            })

        context.extend(self.short_memory[chat_id])
        return context

    def clear(self, chat_id: int):
        self.short_memory[chat_id].clear()
        self.long_summary[chat_id] = ""
