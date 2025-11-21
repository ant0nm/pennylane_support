from fastapi import FastAPI
from .config import get_settings

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World", "settings": get_settings()}
