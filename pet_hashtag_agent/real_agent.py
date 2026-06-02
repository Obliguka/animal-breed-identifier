"""
Real Agent for Animal Breed Identifier
LLM сама выбирает инструменты и аргументы через <tool_call>.
Фото обрабатывается внешним API (порт 8001), LLM решает когда что вызывать.
"""

import json
import re
import base64
import requests
from typing import Dict, Any, List, Optional

# ============================================
# КОНФИГУРАЦИЯ
# ============================================

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3.2-vision"
MAX_ITERATIONS = 6
OLLAMA_TIMEOUT = 30    # текстовые запросы к Ollama
API_TIMEOUT = 180      # внешний API делает 2 vision-вызова

API_BASE_URL = "http://localhost:8001"

# ============================================
# РАЗДЕЛЯЕМОЕ СОСТОЯНИЕ (текущее фото)
# ============================================

_CURRENT_PHOTO_BASE64: Optional[str] = None

def set_current_photo(b64: Optional[str]) -> None:
    global _CURRENT_PHOTO_BASE64
    _CURRENT_PHOTO_BASE64 = b64

def get_current_photo() -> Optional[str]:
    return _CURRENT_PHOTO_BASE64

def photo_loaded() -> bool:
    return _CURRENT_PHOTO_BASE64 is not None

# ============================================
# ИНСТРУМЕНТЫ
# ============================================

def identify_pet() -> Dict[str, str]:
    """Определяет породу по загруженному фото (внешний API)."""
    photo_b64 = get_current_photo()
    if not photo_b64:
        return {"error": "Нет загруженного фото. Используй /photo <путь> сначала."}
    try:
        resp = requests.post(
            f"{API_BASE_URL}/predict",
            files={"file": base64.b64decode(photo_b64)},
            timeout=API_TIMEOUT
        )
        if resp.status_code == 200:
            return resp.json()
        else:
            return {"error": f"Ошибка API: {resp.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def generate_hashtags(breed: str) -> List[str]:
    """Генерирует хештеги для породы.

    Args:
        breed: порода (например, "siberian husky")
    """
    tag = breed.lower().replace(" ", "").replace("-", "")
    breed_key = breed.lower()

    hashtags = [f"#{tag}"]

    dog_breeds = [
        "husky", "labrador", "german shepherd", "corgi", "dachshund",
        "bulldog", "samoyed", "beagle", "shiba inu", "rottweiler",
        "siberian husky", "golden retriever", "poodle", "chihuahua",
        "malamute", "alaskan malamute",
    ]
    cat_breeds = [
        "maine coon", "siamese", "persian", "sphynx", "british shorthair",
        "scottish fold", "ragdoll", "siberian", "russian blue", "bengal",
    ]

    if breed_key in dog_breeds:
        hashtags.extend(["#dog", "#собака"])
    elif breed_key in cat_breeds:
        hashtags.extend(["#cat", "#кошка"])
    else:
        hashtags.extend(["#pet", "#питомец"])

    hashtags.extend(["#petlover", "#cute", f"#{tag}love"])
    return hashtags


def get_user_stats(user_id: str = "default") -> Dict[str, Any]:
    """Статистика пользователя.

    Args:
        user_id: идентификатор пользователя
    """
    return {
        "user_id": user_id,
        "total_requests": 42,
        "top_breeds": ["хаски", "мейн-кун", "корги"],
        "avg_latency_ms": 8350
    }


TOOLS = {
    "identify_pet": identify_pet,
    "generate_hashtags": generate_hashtags,
    "get_user_stats": get_user_stats,
}

# ============================================
# СИСТЕМНЫЙ ПРОМПТ (не f-string, чтобы не путаться с { })
# ============================================

TOOLS_DESC = (
    '1. identify_pet()\n'
    '   Описание: определяет породу и вид животного по загруженному фото\n'
    '   Аргументы: не требует (фото берётся из сессии)\n'
    '   Возвращает: {"animal": "dog", "breed": "siberian husky", "confidence": 0.95}\n'
    '\n'
    '2. generate_hashtags(breed: str) -> list[str]\n'
    '   Описание: генерирует хештеги для породы\n'
    '   Аргументы: breed — название породы (например, "siberian husky")\n'
    '   Возвращает: ["#siberianhusky", "#dog", "#собака", ...]\n'
    '\n'
    '3. get_user_stats(user_id: str = "default") -> dict\n'
    '   Описание: статистика пользователя\n'
    '   Аргументы: user_id — опционально\n'
    '   Возвращает: {"total_requests": 42, "top_breeds": [...], ...}\n'
)

SYSTEM_PROMPT = (
    'Ты — AI-агент для генерации хештегов питомцам.\n'
    '\n'
    'Фото загружается командой /photo. Ты НЕ видишь фото.\n'
    'Для распознавания породы вызывай identify_pet() — он пошлёт фото во внешний API.\n'
    '\n'
    'Доступные инструменты:\n'
    + TOOLS_DESC +
    '\n'
    'АЛГОРИТМ РАБОТЫ:\n'
    '1. Прочитай запрос пользователя\n'
    '2. Определи, какая цепочка вызовов нужна\n'
    '3. Вызывай ОДИН инструмент за раз через <tool_call>\n'
    '4. Получив результат, реши: нужен ли следующий вызов\n'
    '5. Когда все шаги цепочки выполнены — дай ответ БЕЗ <tool_call>\n'
    '\n'
    'ЦЕПОЧКИ ВЫЗОВОВ (выполняй ПОЛНОСТЬЮ, шаг за шагом):\n'
    '\n'
    '[Цепочка А] "Определи породу" + фото:\n'
    '   Шаг 1: identify_pet()\n'
    '   Шаг 2: ответь пользователю — какая порода\n'
    '\n'
    '[Цепочка Б] "Сделай хештеги" + фото:\n'
    '   Шаг 1: identify_pet()\n'
    '   Шаг 2: из "breed" вызови generate_hashtags(breed="...")\n'
    '   Шаг 3: покажи хештеги\n'
    '\n'
    '[Цепочка В] "Определи породу и сделай хештеги" + фото:\n'
    '   Шаг 1: identify_pet()\n'
    '   Шаг 2: generate_hashtags(breed=...)\n'
    '   Шаг 3: ответь: порода + хештеги\n'
    '\n'
    '[Цепочка Г] "Покажи статистику":\n'
    '   Шаг 1: get_user_stats()\n'
    '   Шаг 2: ответь со статистикой\n'
    '\n'
    '[Цепочка Д] Вопрос без фото:\n'
    '   → просто ответь без вызова инструментов\n'
    '\n'
    'ПРИМЕР полного цикла (цепочка В):\n'
    '> Запрос: "Определи породу и сделай хештеги"\n'
    '> Итерация 1: <tool_call>{"name": "identify_pet", "arguments": {}}</tool_call>\n'
    '  ← Результат: {"animal": "dog", "breed": "siberian husky"}\n'
    '> Итерация 2: <tool_call>{"name": "generate_hashtags", "arguments": {"breed": "siberian husky"}}</tool_call>\n'
    '  ← Результат: ["#siberianhusky", "#dog", ...]\n'
    '> Итерация 3: финальный ответ пользователю (без tool_call)\n'
    '\n'
    'ВАЖНО:\n'
    '- После каждого tool_call ты получаешь результат. Проанализируй его.\n'
    '- Если остались шаги → вызови следующий инструмент\n'
    '- Если все шаги сделаны → финальный ответ\n'
    '- Если identify_pet() вернул ошибку — объясни пользователю\n'
    '- Если фото не загружено — скажи загрузить через /photo\n'
    '\n'
    'ФОРМАТ ВЫЗОВА:\n'
    '<tool_call>{"name": "generate_hashtags", "arguments": {"breed": "siberian husky"}}</tool_call>\n'
    '\n'
    'Отвечай на русском. Будь дружелюбным.'
)


def parse_tool_calls(text: str) -> List[Dict[str, Any]]:
    """Извлекает <tool_call>...</tool_call> из ответа."""
    calls = []
    for m in re.findall(r'<tool_call>(.*?)</tool_call>', text, re.DOTALL):
        try:
            calls.append(json.loads(m.strip()))
        except json.JSONDecodeError:
            pass
    return calls


def execute_tool(name: str, args: Dict[str, Any]) -> Any:
    """Выполняет инструмент."""
    if name not in TOOLS:
        return {"error": f"Неизвестный инструмент: {name}"}
    try:
        print(f"  [exec] {name}({args})")
        return TOOLS[name](**args)
    except TypeError as e:
        return {"error": f"Неверные аргументы для {name}: {e}"}
    except Exception as e:
        return {"error": str(e)}


def call_ollama(messages: list) -> str:
    """Запрос к Ollama /api/chat."""
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "temperature": 0.2,
        "max_tokens": 1200,
    }
    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=OLLAMA_TIMEOUT)
        if r.status_code == 200:
            return r.json().get("message", {}).get("content", "")
        return f"[Ошибка Ollama: {r.status_code}]"
    except Exception as e:
        return f"[Ошибка Ollama: {e}]"


def run_agent(user_request: str) -> str:
    """Запускает агента: LLM выбирает инструменты через <tool_call>."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    # --- ВАЖНО: сообщаем модели о статусе фото ---
    if photo_loaded():
        messages.append({
            "role": "user",
            "content": f"[СИСТЕМА: Фото уже загружено! Можешь вызывать identify_pet() для определения породы.]"
        })

    messages.append({"role": "user", "content": user_request})

    for i in range(MAX_ITERATIONS):
        print(f"\n--- Итерация {i + 1}/{MAX_ITERATIONS} ---")
        resp = call_ollama(messages)
        print(f"  [LLM] {resp[:350]}")

        messages.append({"role": "assistant", "content": resp})

        calls = parse_tool_calls(resp)
        if not calls:
            print("  [*] Готово (нет вызовов)")
            return resp

        # Берём ТОЛЬКО первый вызов, остальные игнорируем
        # (LLM иногда пишет всю цепочку в одном ответе, но реальный результат мы дадим сами)
        c = calls[0]
        name = c.get("name", "")
        args = c.get("arguments", {})
        result = execute_tool(name, args)
        text = json.dumps(result, ensure_ascii=False, indent=2)
        print(f"  [result] {name} -> {text[:300]}")
        messages.append({
            "role": "user",
            "content": f"[РЕЗУЛЬТАТ {name}]: {text}"
        })

    return "Агент не завершил цепочку за отведённое число итераций."


def load_photo_to_base64(path: str) -> str:
    """Загружает фото в base64."""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def interactive_mode():
    """Интерактивный режим."""
    print("\n" + "=" * 60)
    print("  REAL AGENT — хештеги для питомцев")
    print(f"  Модель: {OLLAMA_MODEL} | API: {API_BASE_URL}/predict")
    print("=" * 60)
    print("  /photo <путь>  — загрузить фото")
    print("  /state         — статус фото")
    print("  /exit          — выход")
    print("=" * 60)

    while True:
        try:
            inp = input("\nВы: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nПока!")
            break

        if inp == "/exit":
            print("Пока!")
            break
        if inp == "/state":
            print("Фото загружено" if photo_loaded() else "Фото не загружено")
            continue
        if inp.startswith("/photo "):
            path = inp[7:].strip()
            try:
                set_current_photo(load_photo_to_base64(path))
                print(f"OK: {path}")
            except Exception as e:
                print(f"Ошибка: {e}")
            continue
        if inp:
            print("\nДумаю...")
            print(f"\nАгент:\n{run_agent(inp)}")


if __name__ == "__main__":
    print("Запуск REAL AGENT...")
    interactive_mode()
