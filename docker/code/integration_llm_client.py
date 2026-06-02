import os
import time
import logging
from pathlib import Path
from typing import Optional

from openai import OpenAI
from dotenv import load_dotenv
from langfuse import get_client, Langfuse

_env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("llm_client")

LITELLM_URL = os.getenv("LITELLM_PROXY_URL", "http://localhost:4000")
LITELLM_API_KEY = os.getenv("LITELLM_MASTER_KEY", "sk-master-key-123")
DEFAULT_MODEL = "tinyllama"

_langfuse_instance = None

def _get_langfuse() -> Langfuse:
    global _langfuse_instance
    if _langfuse_instance is None:
        _langfuse_instance = get_client()
    return _langfuse_instance


class LiteLLMClient:
    def __init__(self):
        self.client = OpenAI(
            base_url=f"{LITELLM_URL}/v1",
            api_key=LITELLM_API_KEY,
        )

    def chat_completion(self, messages, model=DEFAULT_MODEL, temperature=0.7, max_tokens=1024, **kwargs):
        start_time = time.time()
        try:
            response = self.client.chat.completions.create(
                model=model, messages=messages, temperature=temperature, max_tokens=max_tokens, **kwargs,
            )
            elapsed = time.time() - start_time
            return {
                "success": True,
                "model": model,
                "content": response.choices[0].message.content,
                "input_tokens": response.usage.prompt_tokens if response.usage else 0,
                "output_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
                "elapsed_seconds": round(elapsed, 3),
            }, None
        except Exception as e:
            elapsed = time.time() - start_time
            error_msg = str(e)
            if "402" in error_msg or "insufficient_balance" in error_msg.lower() or "budget_exceeded" in error_msg.lower() or "budget has been exceeded" in error_msg.lower():
                return {
                    "success": False,
                    "model": model,
                    "error": "budget_exceeded",
                    "error_message": "Дневной лимит бюджета исчерпан (HTTP 402)",
                    "elapsed_seconds": round(elapsed, 3),
                }, BudgetExceededError("Дневной лимит бюджета исчерпан")
            return {
                "success": False,
                "model": model,
                "error": "api_error",
                "error_message": error_msg,
                "elapsed_seconds": round(elapsed, 3),
            }, None

    def vision_completion(self, prompt, image_base64, model="llava", temperature=0.75, max_tokens=250):
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}},
                ],
            }
        ]
        return self.chat_completion(messages=messages, model=model, temperature=temperature, max_tokens=max_tokens)

    def text_completion(self, prompt, model=DEFAULT_MODEL, temperature=0.2, max_tokens=150):
        messages = [{"role": "user", "content": prompt}]
        return self.chat_completion(messages=messages, model=model, temperature=temperature, max_tokens=max_tokens)


class BudgetExceededError(Exception):
    http_status = 402


def trace_vision_call(prompt, image_base64, metadata=None, model="llava"):
    client = LiteLLMClient()
    with _get_langfuse().start_as_current_observation(
        as_type="span", name="vision_predict",
        input={"prompt": prompt, "image_size": len(image_base64)},
        metadata=metadata or {},
    ) as trace_span:
        try:
            with _get_langfuse().start_as_current_observation(
                as_type="generation", name=f"llm_call_{model}_vision",
                model=model, input=prompt,
            ) as generation:
                result, error = client.vision_completion(prompt=prompt, image_base64=image_base64, model=model)
                if error and isinstance(error, BudgetExceededError):
                    generation.update(output=None, level="ERROR", status_message=str(error))
                    trace_span.update(output={"error": str(error), "http_status": 402})
                    raise error
                if not result["success"]:
                    generation.update(output=None, level="ERROR", status_message=result.get("error_message", ""))
                    trace_span.update(output=result)
                    return result
                generation.update(
                    output=result["content"],
                    usage={"input": result["input_tokens"], "output": result["output_tokens"]},
                )
            trace_span.update(
                output=result["content"],
                metadata={"elapsed_seconds": result["elapsed_seconds"], "input_tokens": result["input_tokens"], "output_tokens": result["output_tokens"]},
            )
            return result
        except BudgetExceededError:
            raise
        except Exception as e:
            trace_span.update(level="ERROR", status_message=str(e))
            raise


def trace_text_call(prompt, metadata=None, model=DEFAULT_MODEL):
    client = LiteLLMClient()
    with _get_langfuse().start_as_current_observation(
        as_type="span", name="text_predict",
        input={"prompt": prompt},
        metadata=metadata or {},
    ) as trace_span:
        try:
            with _get_langfuse().start_as_current_observation(
                as_type="generation", name=f"llm_call_{model}_text",
                model=model, input=prompt,
            ) as generation:
                result, error = client.text_completion(prompt=prompt, model=model)
                if error and isinstance(error, BudgetExceededError):
                    generation.update(output=None, level="ERROR", status_message=str(error))
                    trace_span.update(output={"error": str(error), "http_status": 402})
                    raise error
                if not result["success"]:
                    generation.update(output=None, level="ERROR", status_message=result.get("error_message", ""))
                    trace_span.update(output=result)
                    return result
                generation.update(
                    output=result["content"],
                    usage={"input": result["input_tokens"], "output": result["output_tokens"]},
                )
            trace_span.update(
                output=result["content"],
                metadata={"elapsed_seconds": result["elapsed_seconds"], "input_tokens": result["input_tokens"], "output_tokens": result["output_tokens"]},
            )
            return result
        except BudgetExceededError:
            raise
        except Exception as e:
            trace_span.update(level="ERROR", status_message=str(e))
            raise


def create_fastapi_budget_handler():
    from fastapi.responses import JSONResponse
    from fastapi import Request
    async def handler(request: Request, exc: BudgetExceededError):
        return JSONResponse(status_code=402, content={
            "error": "budget_exceeded", "message": str(exc), "http_status": 402,
        })
    return handler
