from fastapi import FastAPI, Depends
from .config import get_settings
from contextlib import asynccontextmanager
from .database import get_session, engine
from sqlmodel import Session, text
from alembic.config import Config
from alembic import command


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


@app.get("/")
def root():
    current_settings = get_settings()
    return {
        "message": "Hello World",
        "settings": current_settings,
        "pg_connection_uri": current_settings.db_connection_url,
    }


@app.get("/test_db_connection/")
def test_db_connection(session: Session = Depends(get_session)):
    result = session.exec(text("SELECT VERSION(), CURRENT_CATALOG, CURRENT_USER;")).first()
    return {
        "pg_version": str(result[0]),
        "current_db": str(result[1]),
        "current_user": str(result[2]),
    }
