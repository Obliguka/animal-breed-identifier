from schemas import RunRequest, RunResponse  
from service import get_service               
from fastapi import FastAPI, HTTPException
app = FastAPI(title="API Wrapper for Animal Breed Identifier")

service = get_service()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/info")
async def info():
    return service.get_info().model_dump()


@app.post("/run")
async def run(request: RunRequest):
    try:
        response = service.run(request)
        return response.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))