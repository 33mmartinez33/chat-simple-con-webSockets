from datetime import date
from enum import Enum

from pydantic import BaseModel, EmailStr


class User (BaseModel):
    id_usuario: int
    email: EmailStr
    username: str
    fecha_de_nacimiento: date
    fecha_de_alta: date



class tipoSala (str,Enum):
    TEXTO = "texto"
    VOZ = "voz"



class TokenData(BaseModel):
    id_usuario: int | None = None



class UsuarioCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    fecha_de_nacimiento: date


class UsuarioUpdate(BaseModel):
    username: str | None = None
    contraseña: str | None = None
    fecha_de_nacimiento: str | None = None


class CanalCreate(BaseModel):
    nombre_canal: str
    contenido_principal: str


class CanalUpdate(BaseModel):
    nombre_canal: str | None = None
    creador: int
    contenido_principal: str | None = None



class SalaCreate(BaseModel):
    tipo: tipoSala
    nombre_sala: str  


class SalaUpdate(BaseModel):
    tipo: tipoSala | None = None
    nombre_sala: str | None = None
