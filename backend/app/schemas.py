from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class User (BaseModel):
    id_usuario: int
    email: EmailStr
    username: str
    fecha_de_nacimiento: date
    fecha_de_alta: date


class TipoSala (str,Enum):
    TEXTO = "texto"
    VOZ = "voz"


class TokenData(BaseModel):
    id_usuario: int | None = None


class UsuarioCreate(BaseModel):
    email: EmailStr = Field(min_length=8, max_length=25)
    username: str = Field(min_length= 3, max_length=16)
    contrasenha: str = Field(min_length=6, max_length=20)
    fecha_de_nacimiento: date


class UsuarioUpdate(BaseModel):
    username: str | None = None
    contrasenha: str | None = None
    fecha_de_nacimiento: str | None = None


class CanalCreate(BaseModel):
    nombre_canal: str
    contenido_principal: str


class CanalUpdate(BaseModel):
    nombre_canal: str | None = None
    creador: int
    contenido_principal: str | None = None


class SalaCreate(BaseModel):
    tipo: TipoSala
    nombre_sala: str  


class SalaUpdate(BaseModel):
    tipo: TipoSala | None = None
    nombre_sala: str | None = None


class MensajeWs(BaseModel):
    contenido: str = Field(min_length=1, max_length=4000)

class NotificacionResponse(BaseModel):
    id_notificacion: int
    contenido: str
    id_mensaje: int
    tipo: str
    fecha: datetime
    id_sala: Optional[int] = None
    id_canal: Optional[int] = None
    id_usuario_emisor: Optional[int] = None

class MarcarLeidasRequest(BaseModel):
    id_sala: Optional[int] = None
    id_usuario_emisor: Optional[int] = None