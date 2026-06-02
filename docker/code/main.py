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
