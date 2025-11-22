from fastapi import FastAPI, Depends
from .config import get_settings
from contextlib import contextmanager
from .database import get_session, engine
from sqlmodel import Session, text


@contextmanager
def lifespan(app: FastAPI):
    # Startup
    # cfg = Config("alembic.ini")
    # command.upgrade(cfg, "head")

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
    result = session.exec(text("SELECT version()")).first()
    return {"pg_version": str(result[0])}
