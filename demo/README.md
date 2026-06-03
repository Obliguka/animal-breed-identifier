# Animal Breed Identifier — развёртывание через Docker

## Требования

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Ollama](https://ollama.com) с моделями:

```bash
ollama pull llava           # для API
ollama pull llama3.2-vision  # для агента (опционально)
```

## Быстрый старт

```bash
# 1. Перейти в папку demo
cd animal-breed-identifier/demo

# 2. Запустить всё
docker compose up -d

# 3. Проверить, что API работает
curl http://localhost:8000/metrics
# → {"total_requests": 0, ...}

# 4. (опционально) Зарегистрироваться в Langfuse
#    Открой http://localhost:3000
#    Зарегистрируйся → создай проект → получи API-ключи
#    Положи их в .env (скопируй из .env.example)
#    Перезапусти: docker compose restart api8000

# 5. Агент — в отдельном терминале
docker compose run --rm agent
```

## Что поднимается

| Сервис | Порт | Описание |
|--------|------|----------|
| **api8000** | 8000 | Быстрый API (1 вызов LLaVA) |
| **api8001** | 8001 | Точный API + RAG + BM25 (2 вызова LLaVA) |
| **agent** | — | CLI агент с ReAct-циклом (запуск: `docker compose run --rm agent`) |
| **Langfuse** | 3000 | Трассировка запросов к LLM |
| **LiteLLM** | 4000 | Прокси для единого API-формата |
| **ClickHouse** | 8123 | Хранение трейсов Langfuse |
| **PostgreSQL** | 5433 | БД Langfuse + LiteLLM |

## Проверка работы

### API (порт 8000) — быстрый режим

```bash
# Проверка (эндпоинта /health нет, используем /metrics)
curl http://localhost:8000/metrics

# Определить породу по фото (прямой вызов Ollama, без Langfuse)
curl -X POST http://localhost:8000/predict_direct \
  -F "file=@../test_data/images/husky1.jpg"

# Определить породу через LiteLLM + Langfuse (если настроен Langfuse)
curl -X POST http://localhost:8000/predict \
  -F "file=@../test_data/images/husky1.jpg"

# Метрики
curl http://localhost:8000/metrics
```

### API + RAG (порт 8001) — точный режим

```bash
curl -X POST http://localhost:8001/predict \
  -F "file=@../test_data/images/husky1.jpg"
# → {"animal": "dog", "breed": "siberian husky", "confidence": 0.97, ...}
```

### AI-агент

```bash
docker compose run --rm agent
```

Внутри агента:

```
Вы: /photo test_data/images/husky1.jpg
Вы: определи породу и сделай хештеги
```

## Остановка

```bash
# Остановить всё
docker compose down

# Остановить + удалить volumes (стерёт данные Langfuse)
docker compose down -v
```

## Как это устроено

- **Ollama** не завёрнута в Docker — она работает на хосте. Контейнеры стучатся к ней через `host.docker.internal:11434`
- **Исходный код** не модифицируется — при сборке Dockerfile заменяет `localhost:11434` на `host.docker.internal:11434` через `sed`
- **Langfuse** требует регистрации после первого запуска. Если не заполнен `.env`, трейсинг не работает, но API продолжает отвечать

## Структура demo/

```
demo/
├── docker-compose.yaml      # Главный файл
├── Dockerfile.api8000        # Сборка быстрого API
├── Dockerfile.api8001        # Сборка точного API
├── Dockerfile.agent          # Сборка агента
├── litellm_config.yaml       # Конфиг LiteLLM
├── .env.example              # Шаблон переменных
└── README.md                 # Эта инструкция
```
