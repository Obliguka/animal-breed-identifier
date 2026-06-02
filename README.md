
API для определения вида и породы животных по фотографии или текстовому описанию с использованием локальной модели LLaVA через Ollama.

## Структура проекта

├── main.py # API (порт 8000) — быстрый режим, Langfuse + LiteLLM
├── RAG/
│ └── main_rag.py # API (порт 8001) — точный режим, RAG + BM25
├── pet_hashtag_agent/
│ ├── agent.py # Агент-заглушка (устаревшая версия)
│ ├── real_agent.py # Агент с ReAct-циклом и `<tool_call>`
│ └── tools.py # Инструменты агента
├── api-wrapper/ # Docker-обёртка для нагрузочного тестирования
├── docker/ # Docker-стек: Langfuse + ClickHouse + LiteLLM + Redis
├── fine-turning/ # LoRA-дообучение ELECTRA/BERT
├── prompts/ # Промпты для LLaVA
└── test_data/ # Тестовые фото (20 пород)

## Возможности

- **POST /predict** (порт 8000) — определение породы по фото (1 вызов LLaVA, ~20 с)
- **POST /predict/text** (порт 8000) — определение по текстовому описанию
- **POST /predict** (порт 8001) — определение с RAG + ретривером (2 вызова LLaVA, ~120 с), возвращает breed + confidence + reasoning
- **GET /metrics** (порт 8000) — метрики производительности
- **AI-агент** — ReAct-цикл на llama3.2-vision: LLM сама выбирает инструменты через `<tool_call>`
- **RAG-ретривер** — BM25-поиск по базе 20 пород (Recall@3 = 100%)
- **Fine-tuning** — LoRA-дообучение ELECTRA/BERT (эксперимент)
- **Мониторинг** — Langfuse (трассировка), LiteLLM (прокси), MetricsCollector (p95 latency)
- **Нагрузочное тестирование** — Docker + Locust

## Почему два API?

| Характеристика | Порт 8000 | Порт 8001 |
|---|---|---|
| Вызовов LLaVA | 1 | 2 (признаки → финальный) |
| Время ответа | ~15–30 с | ~60–180 с |
| RAG | нет | BM25 + контекст |
| Мониторинг | Langfuse, LiteLLM | нет |
| Возвращает | breed | breed + confidence + reasoning |
| Назначение | Быстрые интеграции, НТ | Точное определение (для агента) |

Запуск:
1. Клонировать репозиторий
2. Установить [Ollama](https://ollama.com)
3. Скачать модель: `ollama pull llava`
4. Создать виртуальное окружение
5. Запустить приложение uvicorn main:app --reload --port {port}

_____________________________________________________________________________________________

## RAG

Система использует RAG для улучшения точности определения породы:

- Модель LLaVA извлекает ключевые признаки из фото (форма ушей, тип шерсти, окрас, хвост)
- Ретривер ищет похожие породы в базе знаний по извлечённым признакам
- Найденные породы добавляются в промпт в качестве контекста
- Модель даёт финальный ответ, опираясь на этот контекст

Метрики ретривера на тестовом наборе (29 запросов):

Precision@3: 33.3%
Recall@3: 100.0%
MRR: 0.908
NDCG@3: 0.829
_____________________________________________________________________________________________

## Агент
Использует llama3.2-vision (10.7B) — в отличие от LLaVA, умеет корректно парсить `<tool_call>`.

Цикл: Thought → `<tool_call>` → Python (API) → результат → Thought → `<tool_call>` → финальный ответ.

Инструменты:

identify_pet() — определяет породу по фото через API на порту 8001
generate_hashtags(breed) — генерирует хештеги для породы
get_user_stats(user_id) — статистика пользователя
Максимум 6 итераций (защита от зацикливания)


Запуск агента:

python real_agent.py
Команды агента:

/photo photo/husky1.jpg — загрузить фото
/state — проверить статус
определи породу и сделай хештеги — запустить агента
/exit — выход
_____________________________________________________________________________________________
## fine-tuning

Расположение:
 папка fine-turning

Что делает
1	Загружает training_data.json (текстовые описания + порода)
2	Преобразует породы в числовые метки (label2id, id2label)
3	Создаёт датасет Hugging Face и разбивает на train (80%) и eval (20%)
4	Загружает модель и токенизатор
5	Настраивает LoRA (ранг 8, alpha 16, dropout 0.1)
6	Задаёт гиперпараметры обучения (5 эпох, batch size 4, lr 2e-4)
7	Обучает модель
8	Сохраняет LoRA-адаптер (не полную модель, а только малые веса)
_____________________________________________________________________________________________
## Развертывание для НТ
папка api-wrapper

Установлен докер
Установлен locust


0. запустить докер
1. Перейти в папку cd api-wrapper/
2. Запустим контейнер с проектом docker compose up --build
3. Запустить locustfile.py locust -f api-wrapper/app/locustfile.py --host http://localhost:8000
4. Открыть в браузере http://localhost:8089 и настроить кол-во юзеров и запустить НТ 



Проверка в терминале работы сервера curl:
1. Проверка Health Check
curl http://localhost:8000/health
Ответ: {"status":"ok"}

2. Информация о сервисе
curl http://localhost:8000/info
Ответ: {"input_type":"image","input_schema":{"type":"object","properties":{}},"output_schema":{"type":"object","properties":{"animal":{"type":"string","description":"Вид животного"},"breed":{"type":"string","description":"Порода"}}}}

3. Запрос с минимальным изображением(проверка,что запустилось приложение)
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d "{\"content\": [{\"type\": \"image\", \"image\": \"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==\"}]}"
Ответ: {"status":"success","result":{"animal":"unknown","breed":"unknown"},"error":null}

_____________________________________________________________________________________________
## Мониторинг
Langfuse (localhost:3000) — трассировка запросов: промпт, токены, время, ошибки
LiteLLM (localhost:4000) — прокси для единого API-формата, смена модели без правки кода, виртуальные ключи с бюджетом
MetricsCollector — total_requests, avg_latency_ms, p95_latency, error_rate

## Полный Docker-стек (мониторинг)
В папке docker/ лежит полный стек для продакшен-среды:

cd docker
docker compose up -d
Поднимает:

| Сервис | Порт | Назначение |
|---|---|---|
| Langfuse | 3000 | Трассировка запросов к LLM |
| ClickHouse | 8123 | База для хранения трейсов |
| PostgreSQL | 5433 | БД Langfuse |
| LiteLLM | 4000 | Прокси для API-запросов к LLM |
| MinIO | 9090 | S3-хранилище для артефактов |
| Redis | 6379 | Кэширование |
| ZooKeeper | 2181 | Координация ClickHouse |

### Остановка
cd docker
docker compose down

### Примечание
Langfuse при перезапуске без volumes потребует повторной регистрации (БД не сохраняется). Для постоянного хранения нужны persistent volumes (добавляются в docker-compose.yaml).