import base64
import json
import requests
import re
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import uvicorn

from retriever import retriever

app = FastAPI(title="Animal Identifier with SGR + Retriever")

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llava"
TIMEOUT = 60

class BreedResult(BaseModel):
    animal: str
    breed: str
    confidence: float
    reasoning: str

def call_ollama(prompt: str, image_base64: str = None, max_tokens: int = 300) -> dict:
    """Универсальная функция вызова Ollama"""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "temperature": 0.1,
        "max_tokens": max_tokens
    }
    if image_base64:
        payload["images"] = [image_base64]
    
    response = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT)
    return response.json()

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()
    image_base64 = base64.b64encode(contents).decode("utf-8")
   
    feature_prompt = """Analyze this photo and describe the animal's key features in a single line:
- ears (floppy/pointed/folded)
- coat (short/long/fluffy/color)
- body (size/shape)
- tail (long/short/curled)
- special features

Example output: "pointed ears, thick coat, wolf-like face, blue eyes"
"""
    feature_response = call_ollama(feature_prompt, image_base64, max_tokens=100)
    features = feature_response.get("response", "").strip()
 
    similar_breeds_context = retriever.get_context_prompt(features, top_k=3)
  
    final_prompt = f"""You are a veterinary expert.

Extracted features from the photo: {features}

{similar_breeds_context}

Based on the features above, identify the most likely breed.
If unsure, use "unknown" for breed.

Respond ONLY with this JSON:
{{
    "animal": "dog or cat or other animal",
    "breed": "breed name",
    "confidence": 0.95,
    "reasoning": "why you think so"
}}

Use lowercase for breed names.
"""
    
    final_response = call_ollama(final_prompt, image_base64, max_tokens=300)
    answer = final_response.get("response", "")
    
  
    json_match = re.search(r'\{.*\}', answer, re.DOTALL)
    if not json_match:
        return {"error": "No JSON found", "raw_response": answer}
    
    try:
        data = json.loads(json_match.group())
        validated = BreedResult(**data)
        return validated.model_dump()
    except Exception as e:
        return {"error": str(e), "raw_response": answer}

@app.get("/")
async def root():
    return {
        "message": "Animal Identifier with SGR + Retriever",
        "endpoint": "/predict - POST with photo",
        "retriever": "Uses lexical search (BM25-like) to find similar breeds"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)