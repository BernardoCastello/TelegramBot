from app.ai.tools import search_knowledge_tool


class ToolRegistry:

    def __init__(self):
        self._tools = {
            "search_knowledge": search_knowledge_tool
        }

    def execute(self, name: str, arguments: dict):
        if name not in self._tools:
            raise ValueError(f"Tool {name} não registrada")

        return self._tools[name](**arguments)