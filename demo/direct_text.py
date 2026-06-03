"""
Обёртка для main.py: добавляет эндпоинт /predict/text_direct
(прямой вызов Ollama, без LiteLLM, для демонстрации)
"""
import json
import requests
from fastapi import APIRouter
from pydantic import BaseModel

OLLAMA_URL = "http://host.docker.internal:11434/api/generate"

router = APIRouter()

class TextQuery(BaseModel):
    description: str

@router.post("/predict/text_direct")
async def direct_predict_text(query: TextQuery):
    """Определение породы по текстовому описанию через прямой вызов Ollama"""
    prompt = (
        f"Based on this description of an animal, determine the animal type and breed.\n"
        f"Description: {query.description}\n\n"
        f"Respond in JSON format ONLY: {{\"animal\": \"type\", \"breed\": \"name\"}}"
    )
    try:
        r = requests.post(OLLAMA_URL, json={
            "model": "tinyllama",
            "prompt": prompt,
            "stream": False,
            "temperature": 0.1,
            "max_tokens": 100,
        }, timeout=60)
        if r.status_code == 200:
            text = r.json().get("response", "")
            if "{" in text and "}" in text:
                json_str = text[text.find("{"):text.rfind("}")+1]
                return json.loads(json_str)
            return {"raw": text}
        return {"error": f"Ollama error: {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}
