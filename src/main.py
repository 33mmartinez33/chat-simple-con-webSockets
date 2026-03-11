from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import date
# from typing import List
from enum import Enum

from sqlalchemy import select
from sqlmodel import Session
from .models import Usuarios, Salas, Canales, Mensajes, Amigos, t_usuarios_activos_sala, RolUsuarioCanal
from .database import get_session



app = FastAPI(title="Chat API", version="1.0")

class tipoSala (str,Enum):
    TEXTO = "texto"
    VOZ = "voz"

# # BaseModels para lecturas completas GET
# # lectura usuario
# class Usuario(BaseModel):
#         id_usuario: int
#         username: str
#         email: EmailStr
# # Basemodel para get lista de canales
# class Canal(BaseModel):
#     id_canal: int
#     nombre_canal: str
#     creador: int
# # Base model para get lista de salas
# class Sala(BaseModel):
#     id_sala: int
#     tipo: tipoSala
#     nombre_sala: str
# # Basemodel para credenciales
class Credenciales(BaseModel):
    username: str
    contrasenha: str
    

# BaseModels para patch/put
# post de sign_in
class UsuarioCreate(BaseModel):
    email: str
    username: str
    contrasenha: str
    fecha_de_nacimiento: date
    fecha_de_alta: date

class UsuarioUpdate(BaseModel):
    username: str | None = None
    contraseña: str | None = None
    fecha_de_nacimiento: date

class CanalCreate(BaseModel):
    nombre_canal: str
    creador: int
    conteido_principal: str

class CanalUpdate(BaseModel):
    nombre_canal: str | None = None
    creador: str
    conteido_principal: str | None = None

class Mensaje(BaseModel):
    id_mensaje: int
    contenido: str
    id_sala: str| None = None
    id_usuario_emisor: int
    id_usuario_receptor: int

class SalaUpdate(BaseModel):
    id_sala: int
    tipo: tipoSala | None = None
    nombre_sala: str | None = None




# PRINCIPAL

@app.get("/")
async def root():
    return {"message": "API Chat activa"}


# LOGIN/REGISTRO

@app.post("/login")
async def login(creds: Credenciales):
    # TODO: validar que exista usuario y que su contraseña coincida
    token = "jwt_123"
    return {"message": "Operación exitosa", "token": token}

@app.post("/sign_in")
async def sign_in(usuario: UsuarioCreate):  
    # TODO: validar email único + INSERT BD
    token = "jwt_123"
    return {"message": "exitoso", "token": token}


# USUARIOS

# Ver info usuario
@app.get("/usuarios/{id_usuario}")
async def datos_usuario(id_usuario: int, session: Session = Depends(get_session)):  
    usuario = session.get(Usuarios, id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return usuario.model_dump(exclude={"contraseña"})


# @app.get("/usuarios/{id_usuario}")
# async def datos_usuario(id_usuario: int):  
#     # TODO: query
#     return Usuario(id_usuario=id_usuario, username="test", email="test@test.com")

# Actualizar usuario
@app.put("/usuarios/{id_usuario}")
async def actualizar_usuario(id_usuario: int, user: UsuarioUpdate):
    return

# Eliminar usuario
@app.delete("/usuarios/{id_usuario}")
async def elimina_usuario(id_usuario: int):
    return {"message": "Usuario eliminado exitosamente"}



# CANALES

# # Ver canales
# @app.get("/usuarios/{id_usuario}/canales")
# # async def get_canales_usuario(id_usuario: int)-> List[Canal]:
# async def get_canales_usuario(id_usuario: int, session: Session = Depends(get_session)):
#     # Busca TODOS los canales DONDE id_usuario_dueno = id_usuario
#     canales = session.exec(
#         select(Canales).where(Canales.id_usuario_dueno == id_usuario)
#     ).all()
#     return canales

# Crear canal
@app.post("/usuarios/{id_usuario}/canales")
async def crear_canal(id_usuario: int, canal: CanalCreate):
    return


# Ver canal
@app.get("/usuarios/{id_usuario}/canales/{id_canal}")
async def get_canal(id_usuario: int, id_canal: int):
    # TODO: query
    # query = """
    # select contenido from canales where id_canal = ?
    # """
    return {"message": "contenido"}


# Actualizar contenido/nombre canal
@app.put("/usuarios/{id_usuario}/canales/{id_canal}")
async def actualizar_contenido_canal(id_usuario: int, canal_update: CanalUpdate):
    return 


# Crear contenido canal (XK?)
@app.post("/usuarios/{id_usuario}/canales/{id_canal}")
async def crear_conenido_canal (id_usuario: int, id_canal: int, contenido: str):
    return


# Eliminar canal
@app.delete("/usuarios/{id_usuario}/canales/{id_canal}")
async def eliminar_canal(id_usuario:int, id_canal:int):
    return {"message": "Canal eliminado exitosamente"}


# SALAS

# Ver salas
@app.get("/usuarios/{id_usuario}/canales/{id_canal}/salas")
async def get_salas_canal(id_usuario: int, id_canal: int):
    # TODO: query
    return [
        {"id_sala": 1, "nombre": "General", "tipo": "texto"},
        {"id_sala": 2, "nombre": "Voz principal", "tipo": "voz"},
        {"id_sala": 3, "nombre": "", "tipo": "texto"}
    ]

# # Crear sala
# @app.post("/usuarios/{id_usuario}/canales/{id_canal}/salas") 
# async def crear_sala(id_usuario: int, id_canal: int, sala: Sala):
#     return 


# actualizar sala
@app.patch("/usuarios/{id_usuario}/canales/{id_canal}/salas/{id_sala}")
async def actualizar_sala(id_usuario: int, id_canal: int, id_sala: int, sala_update: SalaUpdate):
    # Solo actualiza lo que frontend envía
    if sala_update.tipo is not None:
        # UPDATE salas SET tipo = ? WHERE id_sala = ?
        pass
        
    if sala_update.nombre_sala is not None:
        # UPDATE salas SET nombre_sala = ? WHERE id_sala = ?
        pass
    
    return {"status": "sala actualizada"}

# Eliminar sala
@app.delete("/usuarios/{id_usuario}/canales/{id_canal}/salas/{id_sala}")
async def eliminar_sala(id_usuario: int, id_canal: int, id_sala: int):
    return {"message": "Sala eliminada exitosamente"}


# AMIGOS

# Get lista amigos
@app.get("/usuarios/{id_usuario}/amigos")
async def get_amigos(id_usuario: int):
    return [
        {
            "id_amigo": 2,
            "username": "ana",
            "email": "ana@test.com",
            "fecha_amistad": "2026-03-10"
        },
        {
            "id_amigo": 5, 
            "username": "juan",
            "email": "juan@test.com",
            "fecha_amistad": "2026-03-09"
        }
    ]


# Añadir amigo
@app.put("/usuarios/{id_usuario}/amigos/")
async def anhadir_amigo(id_usuario: int, id_usuario2: int):
    return {"message": "Amigo añadido"}

# Eliminar amigo
@app.delete("/usuarios/{id_usuario}/amigos/{id_usuario2}")
async def eliminar_amigo(id_usuario: int, id_usuario2: int):
    return {"message": "Amigo eliminado"}


# MENSAJES

# Ver mensajes sala
@app.get("/usuarios/{id_usuario}/canales/{id_canal}/salas/{id_sala}")
async def get_mensajes_sala():
    return [Mensaje(
        
    ),]


# Crear mensaje en sala
@app.post("/usuarios/{id_usuario}/canales/{id_canal}/salas/{id_sala}")
async def crear_mensaje_sala(id_usuario: int, id_canal: int, contenido: str):
    return  

# Eliminar mensaje sala
@app.delete("/usuarios/{id_usuario}/canales/{id_canal}/salas/{id_sala}/{id_mensaje}")
async def eliminar_mensaje_sala(id_usuario: int, id_canal: int, id_sala: int, id_mensaje: int):
    return {"message": "Mensaje de sala eliminado"}

# Ver mensajes amigo
@app.get("/usuarios/{id_usuario}/amigos/{id_usuario2}")
async def get_mensajes_amigo(id_usuario: int, id_usuario2: int):
    return [
        {
            "id_mensaje": 1,
            "de": id_usuario,      # Quién envía
            "para": id_usuario2,   # Quién recibe  
            "contenido": "¡Hola amigo!",
            "fecha": "2026-03-10T11:00:00",
        },
        {
            "id_mensaje": 2,
            "de": id_usuario2,
            "para": id_usuario,
            "contenido": "¡Hola! ¿Qué tal?",
            "fecha": "2026-03-10T11:01:00", 
        }
    ]