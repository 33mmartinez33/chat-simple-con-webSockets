from sqlmodel import SQLModel, create_engine, Session
from .config import settings


engine = create_engine(settings.DATABASE_URL)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:  # nueva sesión por cada request
        yield session
        # la sesión se cierra automáticamente al salir del bloque with
