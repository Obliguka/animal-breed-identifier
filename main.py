import base64
import json
import requests
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import uvicorn
from requests_ollama import send_to_ollama
from llm_client import trace_vision_call, trace_text_call, BudgetExceededError, create_fastapi_budget_handler
import time
from metrics import MetricsCollector

# Вспомогательный клиент для прямого вызова Ollama
OLLAMA_VISION_URL = "http://localhost:11434/api/generate"

def call_ollama_direct(prompt: str, image_base64: str) -> dict:
    """Вызов LLaVA напрямую через /api/generate (как в RAG/main_rag.py)"""
    payload = {
        "model": "llava",
        "prompt": prompt,
        "stream": False,
        "temperature": 0.2,
        "max_tokens": 250,
        "images": [image_base64]
    }
    try:
        r = requests.post(OLLAMA_VISION_URL, json=payload, timeout=180)
        if r.status_code == 200:
            text = r.json().get("response", "")
            # Пытаемся извлечь JSON из ответа
            if "{" in text and "}" in text:
                json_str = text[text.find("{"):text.rfind("}")+1]
                return json.loads(json_str)
            return {"raw": text}
        return {"error": f"Ollama error: {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}

print("Начало")
metrics = MetricsCollector()

app = FastAPI(title="Animal Identifier with Ollama + Langfuse + LiteLLM")
app.add_exception_handler(BudgetExceededError, create_fastapi_budget_handler())

class TextQuery(BaseModel):
    description: str

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    start_time = time.time()
    endpoint = "/predict"
    try:
        contents = await file.read()
        image_base64 = base64.b64encode(contents).decode("utf-8")
        prompt = open("prompts/prompt_photo.txt", "r", encoding="utf-8").read()
        result = trace_vision_call(
            prompt=prompt,
            image_base64=image_base64,
            metadata={"file_size": len(contents), "endpoint": endpoint},
        )
        latency_ms = (time.time() - start_time) * 1000
        metrics.log_request(endpoint=endpoint, status="success", latency_ms=latency_ms, metadata={"file_size": len(contents)})
        return result
    except BudgetExceededError:
        raise
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        metrics.log_request(endpoint=endpoint, status="error", latency_ms=latency_ms, error=str(e))
        return {"error": str(e)}

@app.post("/predict_direct")
async def predict_direct(file: UploadFile = File(...)):
    """Определение породы через прямой вызов Ollama + трейс в Langfuse"""
    start_time = time.time()
    try:
        contents = await file.read()
        image_base64 = base64.b64encode(contents).decode("utf-8")
        prompt = open("prompts/prompt_photo.txt", "r", encoding="utf-8").read()
        
        # Вызываем LLaVA напрямую
        result = call_ollama_direct(prompt, image_base64)
        
        # Постить трейс в Langfuse через REST API (для v2)
        try:
            import uuid, os
            from dotenv import load_dotenv
            load_dotenv()
            lf_pk = os.getenv("LANGFUSE_PUBLIC_KEY", "")
            lf_sk = os.getenv("LANGFUSE_SECRET_KEY", "")
            if lf_pk and lf_sk:
                trace_data = {
                    "name": "agent_predict",
                    "input": {"file_size": len(contents), "prompt": prompt[:100]},
                    "output": result,
                    "metadata": {"latency_ms": (time.time() - start_time) * 1000}
                }
                requests.post("http://localhost:3000/api/public/traces",
                    auth=(lf_pk, lf_sk), json=trace_data, timeout=5)
        except Exception:
            pass
        
        latency_ms = (time.time() - start_time) * 1000
        metrics.log_request(endpoint="/predict_direct", status="success", latency_ms=latency_ms)
        return result
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        metrics.log_request(endpoint="/predict_direct", status="error", latency_ms=latency_ms, error=str(e))
        return {"error": str(e)}

@app.post("/predict/text")
async def predict_text(query: TextQuery):
    start_time = time.time()
    endpoint = "/predict/text"
    try:
        template = open("prompts/prompt_text.txt", "r", encoding="utf-8").read()
        prompt_t = template.replace("{description}", query.description)
        result = trace_text_call(
            prompt=prompt_t,
            metadata={"description_length": len(query.description), "endpoint": endpoint},
        )
        latency_ms = (time.time() - start_time) * 1000
        metrics.log_request(endpoint=endpoint, status="success", latency_ms=latency_ms, metadata={"description_length": len(query.description)})
        return result
    except BudgetExceededError:
        raise
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        metrics.log_request(endpoint=endpoint, status="error", latency_ms=latency_ms, error=str(e))
        return {"error": str(e)}

@app.get("/metrics")
async def get_metrics():
    return metrics.get_stats()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
