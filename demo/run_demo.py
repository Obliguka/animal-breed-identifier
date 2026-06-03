"""Точка входа для демо: основное API + прямой текстовый эндпоинт"""
import uvicorn
from main import app
from direct_text import router as direct_router

# Добавляем дополнительный эндпоинт
app.include_router(direct_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
