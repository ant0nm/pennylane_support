from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session
from .config import get_settings

settings = get_settings()
engine = create_engine(settings.db_connection_url, echo=False)
SessionLocal = sessionmaker(engine, class_=Session, expire_on_commit=False)


def get_session():
    with SessionLocal() as session:
        yield session
