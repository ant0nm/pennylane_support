from fastapi import FastAPI, Depends
from .config import get_settings
from contextlib import asynccontextmanager
from .database import get_session, engine
from sqlmodel import Session, text
from alembic.config import Config
from alembic import command
from .routers import challenges


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        print("Running migrations...")
        cfg = Config("alembic.ini")
        command.upgrade(cfg, "head")
        print("Ran migrations successfully!")
    except Exception as e:
        print(f"Migration failed: {e}")
        raise

    yield

    # Shutdown
    engine.dispose()


current_settings = get_settings()
app = FastAPI(
    title=current_settings.project_name,
    version=current_settings.project_version,
    description=(
        "API that powers PennyLane Support, a community-driven support conversations platform for "
        "PennyLane quantum computing challenges."
    ),
    lifespan=lifespan,
)

app.include_router(challenges.router)
