
API для определения вида и породы животных по фотографии или текстовому описанию с использованием локальной модели LLaVA через Ollama.

Возможности:
- Определение по фото (`POST /predict`) 
- Определение по текстовому описанию (`POST /predict/text`)
- Schema-Guided Reasoning (SGR) — структурированный вывод с объяснением 
- Локально
- Ответы в формате JSON

Запуск:
1. Клонировать репозиторий
2. Установить [Ollama](https://ollama.com)
3. Скачать модель: `ollama pull llava`
4. Создать виртуальное окружение
5. Запустить приложение uvicorn main:app --reload

Проект:
- main.py: Основное API (простой вывод) на 8080 порту
- main_sgr.py: API с Schema-Guided Reasoning (тут запросы только по фото) на 8081 порту
- requests_ollama.py: класс для работы с Ollama
- metrics.py: Сбор метрик
- test_runner.py: Запуск тестов
- iterative_tester.py: Итеративное тестирование

Эндпоинты
Метод: POST
Эндпоинт: /predict
Порт: 8000
Описание: Определение породы по фото

Метод: POST
Эндпоинт: /predict/text
Порт: 8000
Описание: Определение породы по текстовому описанию

Метод: GET
Эндпоинт: /status
Порт: 8000
Описание: Проверка статуса Ollama

Метод: GET
Эндпоинт: /metrics
Порт: 8000
Описание: Получение метрик производительности

Метод: POST
Эндпоинт: /predict
Порт: 8001
Описание: SGR режим с объяснением (только фото)


RAG

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

Агент:
Расположение:
 папка pet_hashtag_agent
 Реализована модель агента с загрушкой.
 Запуск: python run.py из папки /pet_hashtag_agent

Инструменты агента:

- identify_pet: определение породы по фото
- generate_hashtags: генерация хештегов
- get_user_stats: получение статистики пользователя

_____________________________________________________________________________________________
Развертывание
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

