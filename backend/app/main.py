from contextlib import asynccontextmanager

from fastapi import FastAPI

from .routers import auth, channels, friends, messages, notifications, rooms, users, ws
from .database import create_db_and_tables
from .config import ALLOWED_ORIGINS
from fastapi.middleware.cors import CORSMiddleware


# Crea las tablas al arrancar y cede el control a FastAPI durante la vida de la app
@asynccontextmanager
async def lifespan(_app: FastAPI):
    create_db_and_tables()  # se ejecuta al arrancar
    yield


app = FastAPI(title="Nexus API", version="1.0", lifespan=lifespan)


# CORS: solo se permiten los orígenes del frontend definidos en config
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(channels.router)
app.include_router(rooms.router)
app.include_router(messages.router)
app.include_router(friends.router)
app.include_router(notifications.router)
app.include_router(ws.router)
