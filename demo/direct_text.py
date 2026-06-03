"""
Эндпоинт /predict/text_direct:
- BM25-ретривер (база 20 пород) 
- tinyllama для финального ответа
"""
import json, re, requests
from fastapi import APIRouter
from pydantic import BaseModel

OLLAMA_URL = "http://host.docker.internal:11434/api/generate"
router = APIRouter()

class TextQuery(BaseModel):
    description: str

# База знаний: 20 пород
BREEDS_DB = [
    {"name": "siberian husky", "features": "pointed ears thick double coat wolf-like face often blue eyes", "animal": "dog"},
    {"name": "labrador", "features": "floppy ears short dense coat otter tail", "animal": "dog"},
    {"name": "german shepherd", "features": "pointed ears black tan coat strong build", "animal": "dog"},
    {"name": "corgi", "features": "short legs long body pointed ears fluffy coat", "animal": "dog"},
    {"name": "dachshund", "features": "very long body short legs floppy ears", "animal": "dog"},
    {"name": "bulldog", "features": "wrinkled face short legs pushed-in nose", "animal": "dog"},
    {"name": "doberman", "features": "sleek pointed ears black tan coat", "animal": "dog"},
    {"name": "rottweiler", "features": "muscular black with tan markings", "animal": "dog"},
    {"name": "samoyed", "features": "white fluffy coat smiling face curled tail", "animal": "dog"},
    {"name": "beagle", "features": "floppy ears short tricolor coat", "animal": "dog"},
    {"name": "shiba inu", "features": "fox-like pointed ears curled tail", "animal": "dog"},
    {"name": "alaskan malamute", "features": "large wolf-like thick coat curled tail", "animal": "dog"},
    {"name": "maine coon", "features": "very large long thick coat tufted ears bushy tail", "animal": "cat"},
    {"name": "siamese", "features": "slender short coat pointed color pattern blue eyes", "animal": "cat"},
    {"name": "persian", "features": "flat face very long fluffy coat", "animal": "cat"},
    {"name": "sphynx", "features": "hairless wrinkled skin large ears", "animal": "cat"},
    {"name": "british shorthair", "features": "round face dense short coat chunky build", "animal": "cat"},
    {"name": "scottish fold", "features": "folded ears round face", "animal": "cat"},
    {"name": "ragdoll", "features": "large blue eyes semi-long coat", "animal": "cat"},
    {"name": "russian blue", "features": "short blue-gray coat green eyes", "animal": "cat"},
]

def retrieve(query: str, top_k: int = 3) -> list:
    """BM25-поиск по описанию"""
    words = set(re.findall(r'\b[a-z]+\b', query.lower()))
    scores = []
    for b in BREEDS_DB:
        feat = set(re.findall(r'\b[a-z]+\b', b["features"].lower()))
        overlap = len(words & feat)
        for w in words:
            if w in b["features"]:
                overlap += 0.5
        scores.append((overlap, b))
    scores.sort(key=lambda x: -x[0])
    return [b for s, b in scores[:top_k] if s > 0]

@router.post("/predict/text_direct")
async def direct_predict_text(query: TextQuery):
    # 1. Ретривер ищет похожие породы
    matches = retrieve(query.description)
    
    # 2. Если ретривер что-то нашёл — возвращаем топ-результат
    if matches:
        return {
            "animal": matches[0]["animal"],
            "breed": matches[0]["name"],
            "confidence": "high",
            "matches": [m["name"] for m in matches]
        }
    
    # 3. Если ретривер не нашёл — пробуем tinyllama
    prompt = (
        f"Identify the animal from description: {query.description}\n"
        f"Respond JSON: {{\"animal\":\"type\",\"breed\":\"name\"}}"
    )
    try:
        r = requests.post(OLLAMA_URL, json={
            "model": "tinyllama",
            "prompt": prompt,
            "stream": False,
            "temperature": 0.1,
            "max_tokens": 80,
        }, timeout=60)
        if r.status_code == 200:
            text = r.json().get("response", "")
            if "{" in text and "}" in text:
                return json.loads(text[text.find("{"):text.rfind("}")+1])
            return {"raw": text}
        return {"error": f"Ollama error: {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}
