
from agent import SimpleAgent

agent = SimpleAgent()

result1 = agent.think_and_act("Определи породу этого пушистого рыжего кота")
print(f"Результат: {result1}\n")

result2 = agent.think_and_act("Сделай хештеги для моего питомца для Instagram")
print(f"Результат: {result2}\n")

result3 = agent.think_and_act("Покажи мою статистику")
print(f"Результат: {result3}\n")

result4 = agent.think_and_act("В чем смысл жизни?")
print(f"Результат: {result4}\n")
