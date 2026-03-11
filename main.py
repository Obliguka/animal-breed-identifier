import base64
import json
import requests
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import uvicorn
from requests_ollama import send_to_ollama

app = FastAPI(title="Animal Identifier with Ollama")

class TextQuery(BaseModel):
    description: str

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image_base64 = base64.b64encode(contents).decode("utf-8")
        
        prompt = open("prompts/prompt_photo.txt", "r", encoding="utf-8").read()
        
        return send_to_ollama(
            prompt=prompt, 
            image_base64=image_base64,
            temperature=0.75,
            max_tokens=250,
            timeout=300
        )       
    except Exception as e:
        return {"error": f"ошибка: {str(e)}"}


@app.post("/predict/text")
async def predict_text(query: TextQuery):
    try:
        template= open("prompts/prompt_text.txt", "r", encoding="utf-8").read()
        prompt_t = template.replace("{description}", query.description)

        #print(prompt_t)
        
        return send_to_ollama(
            prompt=prompt_t,
            temperature=0.2,
            max_tokens=150,
            timeout=60
        )  
        print(f"📦 РЕЗУЛЬТАТ ОТ send_to_ollama: {result}")      
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)