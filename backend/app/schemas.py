from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# Schema de datos públicos del usuario autenticado (no incluye contraseña)
class User(BaseModel):
    id_usuario: int
    email: EmailStr
    username: str
    fecha_de_nacimiento: date
    fecha_de_alta: date


# Enum de tipos de sala (duplicado de models para uso en schemas sin importar SQLModel)
class TipoSala(str, Enum):
    TEXTO = "texto"
    VOZ = "voz"


# Payload que se extrae del JWT para identificar al usuario
class TokenData(BaseModel):
    id_usuario: int | None = None


# Datos necesarios para registrar un nuevo usuario
class UsuarioCreate(BaseModel):
    email: EmailStr = Field(min_length=8, max_length=25)
    username: str = Field(min_length=3, max_length=16)
    contrasenha: str = Field(min_length=6, max_length=20)
    fecha_de_nacimiento: date


# Campos actualizables del perfil. Todos son opcionales para permitir PATCH parcial
class UsuarioUpdate(BaseModel):
    username: str | None = None
    contrasenha: str | None = None
    fecha_de_nacimiento: str | None = None


# Datos requeridos para crear un canal
class CanalCreate(BaseModel):
    nombre_canal: str
    contenido_principal: str


# Campos actualizables de un canal. creador es obligatorio para validar permisos
class CanalUpdate(BaseModel):
    nombre_canal: str | None = None
    creador: int
    contenido_principal: str | None = None


# Datos para crear una sala dentro de un canal
class SalaCreate(BaseModel):
    tipo: TipoSala
    nombre_sala: str


# Campos actualizables de una sala
class SalaUpdate(BaseModel):
    tipo: TipoSala | None = None
    nombre_sala: str | None = None


# Payload de un mensaje enviado por WebSocket
class MensajeWs(BaseModel):
    contenido: str = Field(min_length=1, max_length=4000)


# Respuesta con los datos de una notificación no leída
# tipo puede ser "sala" (mensaje de canal) o "dm" (mensaje directo)
class NotificacionResponse(BaseModel):
    id_notificacion: int
    contenido: str
    id_mensaje: int
    tipo: str
    fecha: datetime
    id_sala: Optional[int] = None           # Presente si tipo == "sala"
    id_canal: Optional[int] = None          # Presente si tipo == "sala"
    id_usuario_emisor: Optional[int] = None # Presente si tipo == "dm"


# Filtro para marcar notificaciones como leídas: por sala o por emisor en DM
class MarcarLeidasRequest(BaseModel):
    id_sala: Optional[int] = None
    id_usuario_emisor: Optional[int] = None
