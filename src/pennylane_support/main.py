from fastapi import FastAPI
from .config import get_settings

settings = get_settings()
app = FastAPI(
    title=settings.project_name,
    version=settings.project_version,
    description=(
        "API that powers PennyLane Support, a community-driven support conversations platform for "
        "PennyLane quantum computing challenges."
    ),
)


@app.get("/")
async def root():
    current_settings = get_settings()
    return {
        "message": "Hello World",
        "settings": current_settings,
        "pg_connection_uri": current_settings.db_connection_url,
    }
