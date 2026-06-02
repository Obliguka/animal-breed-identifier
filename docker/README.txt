Задание: Развернуть Langfuse + LiteLLM и интегрировать с системой

=== Структура ===

docker/             - Docker-compose файлы для развёртывания
  docker-compose.langfuse-full.yml   - Langfuse + Clickhouse + MinIO + Redis
  docker-compose-litellm.yml         - LiteLLM Proxy
  docker-compose-langfuse.yml        - Langfuse (упрощённый)
  litellm_config.yaml                - Конфиг моделей LiteLLM
  clickhouse-config/                 - Конфиг Clickhouse

code/               - Код системы с интеграцией
  main.py           - FastAPI сервер
  llm_client.py     - Клиент для LiteLLM + Langfuse трассировки + HTTP 402
  requests_ollama.py - Отправка запросов через LiteLLM
  metrics.py        - Метрики
  .env              - Ключи API

prompts/            - Промпты для моделей

=== Как запустить ===

1. Docker-сервисы:
   cd docker
   docker compose -f docker-compose.langfuse-full.yml up -d
   docker compose -f docker-compose-litellm.yml up -d

2. Langfuse: http://localhost:3000 (зарегистрироваться, создать проект)
3. LiteLLM: http://localhost:4000

4. Система:
   cd code
   pip install -r requirements.txt
   python main.py
   http://localhost:8000

=== Что реализовано ===

[1] Langfuse развёрнут через Docker Compose (+ Clickhouse, MinIO, Redis)
[2] Langfuse SDK интегрирован: трассировки с запросом, ответом, токенами, временем
[3] LiteLLM развёрнут через Docker Compose
[4] Подключена модель tinyllama через Ollama (локально)
[5] Создан виртуальный ключ с дневным бюджетом
[6] Система шлёт запросы через LiteLLM, а не напрямую
[7] При превышении бюджета возвращается HTTP 402
