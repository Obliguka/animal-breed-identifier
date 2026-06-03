# Animal Breed Identifier — план демонстрации (15 мин)

## 1. Docker-развёртывание (3 мин)

```powershell
cd animal-breed-identifier/demo
docker compose up -d
docker ps
```

Показать: 10 контейнеров Up. Объяснить: одна команда — и весь проект работает.

## 2. API жив (1 мин)

```powershell
python -c "import requests; print(requests.get('http://localhost:8000/metrics').json())"
```

Ответ: `{"error":"Нет данных"}` — сервер жив, просто ещё не было запросов.

## 3. Определение породы по тексту (3 мин)

```powershell
python -c "
import requests
r = requests.post('http://localhost:8000/predict/text_direct',
    json={'description': 'a fluffy white dog with a curled tail and smiling face'},
    timeout=60)
print(r.json())
"
```

Объяснить: описание отправляется в tinyllama через Ollama, модель определяет вид и породу.

## 4. Точный API (RAG, порт 8001) — 3 мин

```powershell
python -c "
import requests
r = requests.post('http://localhost:8001/predict',
    files={'file': open('../test_data/images/samoyed1.jpg', 'rb')},
    timeout=180)
print(r.json())
"
```

Если не хватает GPU — объяснить: LLaVA 7B требует 8GB VRAM, на машине 6GB.
На другой машине с нормальным GPU работает из коробки.

## 5. Вопрос — ответ (5 мин)

Куратор может спросить:
- Почему Docker, а не локально? → Воспроизводимость, изоляция
- А что с agent? → Есть в Docker, можно запустить `docker compose run --rm agent`
- А агент с картинками работает? → Требует llama3.2-vision (10.7B), нужен GPU
- Где лежит код? → github.com/Obliguka/animal-breed-identifier

---

**Главное:** куратор клонирует репу → делает `docker compose up -d` → всё работает. Воспроизводимость доказана ✅
