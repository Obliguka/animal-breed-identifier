import base64
import json
import requests
import re
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import uvicorn

from sgr.prompts import SGR_PROMPT

app = FastAPI(title="Animal Identifier with SGR")

class BreedResult(BaseModel):
    animal: str
    breed: str
    confidence: float
    reasoning: str

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()
    image_base64 = base64.b64encode(contents).decode("utf-8")
    
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llava",
            "prompt": SGR_PROMPT,
            "stream": False,
            "images": [image_base64],
            "temperature": 0.1,
            "max_tokens": 300
        },
        timeout=60
    )

    answer = response.json().get("response", "")
    
    json_match = re.search(r'\{.*\}', answer, re.DOTALL)
    if not json_match:
        return {"error": "No JSON found", "raw_response": answer}
    
    try:
        data = json.loads(json_match.group())
        validated = BreedResult(**data)
        return validated.model_dump()
    except Exception as e:
        return {"error": str(e), "raw_response": answer}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)