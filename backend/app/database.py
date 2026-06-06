from sqlmodel import SQLModel, create_engine, Session
from .config import settings


engine = create_engine(settings.DATABASE_URL)


# Crea todas las tablas definidas en los modelos si no existen aún
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# Generador de sesión de base de datos para inyección de dependencias en FastAPI
# Retorna una sesión por cada request y la cierra automáticamente al terminar
def get_session():
    with Session(engine) as session:  # nueva sesión por cada request
        yield session
        # la sesión se cierra automáticamente al salir del bloque with
