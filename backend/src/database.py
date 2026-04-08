# from sqlmodel import SQLModel, create_engine, Session
# from .models import *


# DATABASE_URL = "postgresql://postgres:passwordpg@localhost:5432/chatconwebsockets"
# engine = create_engine(DATABASE_URL)


# # Ignora tablas existentes, crea si faltan
# SQLModel.metadata.create_all(bind=engine)


# SessionLocal = Session(bind=engine, autoflush=False, autocommit=False)


# def get_session():
#     db = SessionLocal
#     try:
#         yield db
#     finally:
#         db.close()


from sqlmodel import SQLModel, create_engine, Session


DATABASE_URL = "postgresql://postgres:passwordpg@localhost:5432/chatconwebsockets"
engine = create_engine(DATABASE_URL)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:  # nueva sesión por cada request
        yield session
        # la sesión se cierra automáticamente al salir del bloque with
