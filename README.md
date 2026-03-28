
API для определения вида и породы животных по фотографии или текстовому описанию с использованием локальной модели LLaVA через Ollama.

Возможности:
- Определение по фото (`POST /predict`)
- Определение по текстовому описанию (`POST /predict/text`)
- Schema-Guided Reasoning (SGR)** — структурированный вывод с объяснением
- Локально
- Ответы в формате JSON

Запуск:
1. Клонировать репозиторий
2. Установить [Ollama](https://ollama.com)
3. Скачать модель: `ollama pull llava`
4. Создать виртуальное окружение
5. Запустить приложение uvicorn main:app --reload

Проект:
- main.py: Основное API (простой вывод) 
- main_sgr.py: API с Schema-Guided Reasoning (тут запросы только по фото)
- requests_ollama.py: класс для работы с Ollama
- metrics.py: Сбор метрик
- test_runner.py: Запуск тестов
- iterative_tester.py: Итеративное тестирование




