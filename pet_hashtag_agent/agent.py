
import json
from tools import *

class SimpleAgent:
    def __init__(self):
        self.tools = {
            "identify_pet": {"function": identify_pet, "input_model": PetInput},
            "generate_hashtags": {"function": generate_hashtags, "input_model": HashtagInput},
            "get_user_stats": {"function": get_user_stats, "input_model": StatsInput},
        }

    def think_and_act(self, user_request: str, user_id: str = "anonymous"):
        user_request_lower = user_request.lower()
        print(f"\n Агент получил запрос: '{user_request}'")

        if "определи" in user_request_lower or "порода" in user_request_lower:
            tool_name = "identify_pet"
            description = user_request.replace("определи", "").replace("породу", "").strip()
            input_data = PetInput(description=description if description else "животное на фото")

        elif "хештег" in user_request_lower or "hashtag" in user_request_lower:
            tool_name = "generate_hashtags"
            # В реальности здесь нужен был бы вызов identify_pet, но для простоты используем заглушку
            input_data = HashtagInput(animal="dog", breed="husky", platform="instagram")

        elif "статистик" in user_request_lower or "stats" in user_request_lower:
            tool_name = "get_user_stats"
            input_data = StatsInput(user_id=user_id)

        else:
            return self._human_escalation(user_request)

        print(f"Агент вызвал инструмент: '{tool_name}'")
        return self._execute_tool(tool_name, input_data)

    def _execute_tool(self, tool_name: str, input_data):
        tool = self.tools.get(tool_name)
        if not tool:
            return f"Ошибка: Инструмент '{tool_name}' не найден."

        result = tool["function"](input_data)
        return result

    def _human_escalation(self, user_request: str):
        print(" Агент НЕ понял запрос. (HITL).")
        return f"Я не понял ваш запрос: '{user_request}'."
