import json
import requests

def send_to_ollama(prompt, temperature=0.2, max_tokens=150, timeout=300, image_base64=None):
    
    payload = {
        "model": "llava",
        "prompt": prompt,
        "stream": False,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    if image_base64:
        payload["images"] = [image_base64]
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get("response", "")
            
            try:
                if "{" in answer and "}" in answer:
                    json_str = answer[answer.find("{"):answer.rfind("}")+1]
                    result_json = json.loads(json_str)
                    return result_json
                else:
                    return {
                        "animal": "не удалось определить",
                        "breed": "не удалось определить",
                        "raw_response": answer
                    }
            except json.JSONDecodeError:
                return {
                    "animal": "ошибка формата",
                    "breed": "ошибка формата",
                    "raw_response": answer
                }
        else:
            return {"error": f"Ошибка Ollama: {response.status_code}"}
            
    except requests.exceptions.ConnectionError:
        return {"error": "Не удалось подключиться к Ollama."}
    except requests.exceptions.Timeout:
        return {"error": "Превышен таймаут ожидания ответа от Ollama"}
    except Exception as e:
        return {"error": str(e)}