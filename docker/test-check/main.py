"""
Тестовый проект: LLM через LiteLLM + Langfuse трассировки.

Использует tinyllama (маленькая модель, работает на CPU).
Для тестирования интеграции Langfuse + LiteLLM + бюджет.

Запуск:
    python main.py
    curl http://localhost:8001/predict/text -H "Content-Type: application/json" \
        -d '{"description": "пушистая кошка"}'
"""

import sys
import os

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "integration"))
from llm_client import (
    trace_text_call,
    BudgetExceededError,
    create_fastapi_budget_handler,
)
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

app = FastAPI(title="Test: TinyLLM + Langfuse + LiteLLM + Budget")

app.add_exception_handler(BudgetExceededError, create_fastapi_budget_handler())


class TextQuery(BaseModel):
    description: str


@app.post("/predict/text")
async def predict_text(query: TextQuery):
    prompt = f"""Определи животное по описанию. Ответь строго в формате JSON:
{{
    "animal": "тип животного",
    "description": "краткое описание"
}}

Описание: {query.description}
"""
    try:
        result = trace_text_call(
            prompt=prompt,
            metadata={
                "description_length": len(query.description),
                "model": "tinyllama",
                "endpoint": "/predict/text",
            },
        )
        return JSONResponse(
            content={
                "status": "ok",
                "result": result.get("content", ""),
                "tokens": {
                    "input": result.get("input_tokens", 0),
                    "output": result.get("output_tokens", 0),
                },
                "elapsed_seconds": result.get("elapsed_seconds", 0),
            }
        )
    except BudgetExceededError:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "error": str(e)},
        )


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
