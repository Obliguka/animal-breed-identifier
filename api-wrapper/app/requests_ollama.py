import json
from llm_client import LiteLLMClient, BudgetExceededError

def send_to_ollama(prompt, temperature=0.2, max_tokens=150, timeout=300, image_base64=None):
    client = LiteLLMClient()
    try:
        if image_base64:
            result, error = client.vision_completion(
                prompt=prompt, image_base64=image_base64, temperature=temperature, max_tokens=max_tokens
            )
        else:
            result, error = client.text_completion(
                prompt=prompt, temperature=temperature, max_tokens=max_tokens
            )
        if error and isinstance(error, BudgetExceededError):
            raise error
        if not result["success"]:
            return {"error": f"Ошибка LiteLLM: {result.get('error_message', 'Unknown')}"}
        answer = result["content"] or ""
        try:
            if "{" in answer and "}" in answer:
                json_str = answer[answer.find("{"):answer.rfind("}")+1]
                parsed = json.loads(json_str)
                return parsed
            else:
                return {"animal": "не удалось определить", "breed": "не удалось определить", "raw_response": answer}
        except json.JSONDecodeError:
            return {"animal": "ошибка формата", "breed": "ошибка формата", "raw_response": answer}
    except BudgetExceededError:
        raise
    except Exception as e:
        return {"error": f"Ошибка: {str(e)}"}
