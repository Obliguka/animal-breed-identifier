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
