```markdown
# Animal Breed Identifier

API для определения вида и породы животных по фото или текстовому описанию.
Использует локальную модель LLaVA (Ollama) + RAG-ретривер + AI-агент.

## Структура проекта

├── main.py # API (порт 8000) — быстрый режим, Langfuse + LiteLLM
├── RAG/
│ └── main_rag.py # API (порт 8001) — более точный режим, RAG + ретривер
├── pet_hashtag_agent/
│ ├── agent.py # Агент-заглушка (ключевые слова)
│ └── real_agent.py # Агент с LLM (ReAct, <tool_call>)
├── api-wrapper/ # Docker-обёртка для нагрузочного тестирования
├── fine-turning/ # LoRA-адаптеры для ELECTRA
├── prompts/ # Текстовые промпты для LLaVA
└── test_data/ # Тестовые фото (20 пород)


## Возможности

- **POST /predict** (порт 8000) — определение породы по фото (1 вызов LLaVA, быстрый)
- **POST /predict/text** (порт 8000) — определение породы по текстовому описанию
- **POST /predict** (порт 8001) — определение с RAG + ретривером (2 вызова LLaVA, точный)
- **Real-агент** — ReAct-цикл: LLM сама выбирает инструменты через `<tool_call>`
- **RAG-ретривер** — BM25-поиск по базе 20 пород
- **Fine-tuning** — LoRA-дообучение ELECTRA для текстовой классификации
- **Мониторинг** — Langfuse (трассировка), LiteLLM (прокси), MetricsCollector (p95 latency)
- **Нагрузочное тестирование** — Docker + Locust

## Быстрый старт

### 1. Установка

```bash
git clone <repo>
cd animal-breed-identifier
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Запуск Ollama

```bash
ollama pull llava
ollama pull llama3.2-vision # для real_agent.py
```

### 3. Запуск API

**Быстрый режим (порт 8000), с мониторингом:**
```bash
uvicorn main:app --reload --port 8000
```

**Точный режим с RAG (порт 8001):**
```bash
uvicorn RAG.main_rag:app --reload --port 8001
```

### 4. Запуск агента

```bash
cd pet_hashtag_agent
python real_agent.py
```

Команды:
```
/photo photo/husky1.jpg — загрузить фото
/state — проверить статус фото
сделай хештеги — запустить агента
/exit — выход
```

## Эндпоинты

### Порт 8000 (main.py)

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/predict` | Определение породы по фото |
| POST | `/predict/text` | Определение породы по тексту |
| GET | `/metrics` | Статистика производительности |
| GET | `/status` | Статус Ollama |

Пример запроса:
```bash
curl -X POST http://localhost:8000/predict \
  -F "file=@photo/husky1.jpg"
```

### Порт 8001 (RAG/main_rag.py)

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/predict` | Определение с RAG + confidence + reasoning |

### Порт 8000 в Docker (api-wrapper)

```bash
cd api-wrapper
docker compose up --build
```

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/health` | Health check |
| GET | `/info` | Схема входных/выходных данных |
| POST | `/run` | Универсальный запрос |

см. api-wrapper/README.md

## Зачем два API?

|                Порт 8000          |         Порт 8001 |
| Вызовов LLaVA |     1             | 2 (признаки → финальный) |
| Время ответа  | ~15-30 с          | ~60-180 с |
| RAG           | нет               | BM25 + контекст |
| Дополнительно | Langfuse, LiteLLM | confidence, reasoning |

Порт 8000 — для быстрых интеграций.
Порт 8001 — когда важна точность и объяснение.

## RAG и ретривер

LLaVA извлекает ключевые признаки из фото → ретривер ищет похожие породы (BM25) → контекст добавляется в финальный промпт.

**Метрики ретривера (29 запросов):**

| Метрика     | Значение |
|-------------|----------|
| Recall@3    | 100%     |
| MRR         | 0.908    |
| NDCG@3      | 0.829    |
| Precision@3 | 33.3%    |

## Агент

`real_agent.py` реализует ReAct-цикл (Reasoning + Acting):

1. LLM получает запрос и сама решает, какой инструмент вызвать
2. Пишет `<tool_call>{"name": "...", "arguments": {...}}</tool_call>`
3. Python выполняет инструмент, возвращает результат
4. LLM анализирует результат — нужен ли следующий шаг
5. Когда цепочка выполнена — финальный ответ пользователю

**Инструменты агента:**
- `identify_pet()` — определение породы (через API на порту 8001)
- `generate_hashtags(breed)` — генерация хештегов
- `get_user_stats(user_id)` — статистика пользователя

## Fine-tuning

LoRA-дообучение ELECTRA на синтетических текстовых описаниях.
Подробнее: `fine-turning/README.md`

## Мониторинг

- **Langfuse** (порт 3000) — запись каждого запроса к LLM
- **LiteLLM** (порт 4000) — единый API-интерфейс для разных LLM
- **MetricsCollector** — среднее время, p95, успешность

## Нагрузочное тестирование

```bash
docker compose up --build -d # 1-й терминал: поднять контейнер
locust -f app/locustfile.py --host http://localhost:8000 # 2-й терминал
```
Открыть `http://localhost:8089`, настроить число пользователей, запустить тест.
```

---