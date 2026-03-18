import datetime
from typing import Dict

from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from datetime import UTC, date
from enum import Enum

from sqlmodel import select
from sqlmodel import Session, and_, or_
from .models import RolAdministradorParticipanteT, Usuarios, Salas, Canales, Mensajes, Amigos, t_usuarios_activos_sala, RolUsuarioCanal
from .database import get_session
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Chat API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # SvelteKit dev
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
    # max_age = 3600,
)


class tipoSala (str,Enum):
    TEXTO = "texto"
    VOZ = "voz"


 # Basemodel para credenciales
class Credenciales(BaseModel):
    username: str
    contrasenha: str
    

# BaseModels para patch/put
# post de sign_in
class UsuarioCreate(BaseModel):
    email: EmailStr
    username: str
    contrasenha: str
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

class MensajeAmigoCreate(BaseModel):
    contenido: str

class SalaCreate(BaseModel):
    tipo: tipoSala
    nombre_sala: str   

class SalaUpdate(BaseModel):
    tipo: tipoSala | None = None
    nombre_sala: str | None = None




# comprubea si el usuario es admin en el canal que se pasa por parametro
async def es_admin(session: Session, id_usuario: int, id_canal: int):
    return bool(session.exec(
        select(RolUsuarioCanal).where(
            RolUsuarioCanal.id_usuario == id_usuario,
            RolUsuarioCanal.id_canal == id_canal,
            RolUsuarioCanal.rol == RolAdministradorParticipanteT.ADMINISTRADOR
        )
    ).first())

# comprubea si el rol es admin o participante
async def es_participante_o_admin(session: Session, id_usuario: int, id_canal: int):
    return bool(session.exec(
        select(RolUsuarioCanal).where(
            RolUsuarioCanal.id_usuario == id_usuario,
            RolUsuarioCanal.id_canal == id_canal,
            RolUsuarioCanal.rol.in_([
                RolAdministradorParticipanteT.ADMINISTRADOR,
                RolAdministradorParticipanteT.PARTICIPANTE
            ])
        )
    ).first())

# Comprueba si los 2 usuarios que se le pasa como parametro son amigos
async def son_amigos(session: Session, id_usuario1: int, id_usuario2: int):
    return bool(session.exec(
        select(Amigos).where(
            Amigos.id_usuario1 == id_usuario1,
            Amigos.id_usuario2 == id_usuario2            
        )
    ).first() or session.exec(
        select(Amigos).where(
            Amigos.id_usuario1 == id_usuario2,
            Amigos.id_usuario2 == id_usuario1            
        )
    ).first())


# PRINCIPAL

# @app.get("/")
# async def root():
#     return {"message": "API Chat activa"}


# LOGIN/REGISTRO

# Usuario inicia sesión
@app.post("/login")
async def login(creds: Credenciales, session: Session = Depends(get_session)):
    usuario = session.exec(
    select(Usuarios).where(
        Usuarios.username == creds.username,
        Usuarios.contraseña == creds.contrasenha  # TODO: hashear
    )
).first()
    if usuario:
        token = "jwt_123" # TODO token real OAuth2
        return {"message": "Operación exitosa", "token": token, "id_usuario": usuario.id_usuario}
    else:
        raise HTTPException(status_code=401, detail = "Las credenciales introducidas no son correctas")



#  Crea usuario
@app.post("/sign_in")
async def sign_in(usuario: UsuarioCreate, session: Session = Depends(get_session)):  
    
    if session.exec(select(Usuarios).where(Usuarios.email == usuario.email)).first():
        raise HTTPException(status_code=400, detail = "Email repetido")
    elif session.exec(select(Usuarios).where(Usuarios.username == usuario.username)).first():
        raise HTTPException(status_code=400, detail = "Username repetido")
    else:
        # insert usuario
        usuario_insertar: Usuarios = Usuarios(
            email = usuario.email,
            username = usuario.username,
            contraseña=usuario.contrasenha, # TODO falta hashear la contraseña
            fecha_de_nacimiento=usuario.fecha_de_nacimiento,
            fecha_de_alta=date.today()
        )
        session.add(usuario_insertar)
        session.commit()
        session.refresh(usuario_insertar)  # ← ID autoincremental + datos frescos
    
        # TODO: JWT real
        token = "jwt_" + str(usuario_insertar.id_usuario)
        
        return {
            "message": "Usuario creado exitosamente",
            "token": token,
            "id_usuario": usuario_insertar.id_usuario
        }


# USUARIOS

# Ver info usuario
@app.get("/usuarios/{id_usuario}")
async def datos_usuario(id_usuario: int, session: Session = Depends(get_session)):  
    usuario = session.get(Usuarios, id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario.model_dump(exclude={"contraseña"}) # mode_dump modifica  

# Actualizar usuario
@app.put("/usuarios/{id_usuario}")
async def actualizar_usuario(id_usuario: int, usuario: UsuarioUpdate, session: Session = Depends(get_session)):
    usuario_db = session.get(Usuarios, id_usuario)
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    elif not session.exec(
        select(Usuarios).where):
        raise HTTPException(status_code=400, detail="Ese username ya esta en uso")
    update_data = usuario.model_dump(exclude_unset=True)
    usuario_db.sqlmodel_update(update_data)
    session.add(usuario_db)
    session.commit()
    session.refresh(usuario_db)
    return usuario_db

# Eliminar usuario
@app.delete("/usuarios/{id_usuario}")
async def elimina_usuario(id_usuario: int, session: Session = Depends(get_session)):
    usuario_db = session.get(Usuarios, id_usuario)
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    session.delete(usuario_db)
    session.commit()


# CANALES

# Ver canales
@app.get("/usuarios/{id_usuario}/canales")
async def get_canales_usuario(id_usuario: int, session: Session = Depends(get_session)):
    canales = session.exec(
        select(Canales).distinct().join(  # distinct() evita duplicados
            RolUsuarioCanal,
            Canales.id_canal == RolUsuarioCanal.id_canal
        ).where(
            RolUsuarioCanal.id_usuario == id_usuario,
            RolUsuarioCanal.rol.in_([
                RolAdministradorParticipanteT.ADMINISTRADOR,
                RolAdministradorParticipanteT.PARTICIPANTE
            ])
        )
    ).all()
    return canales

# # ver todos los canales?
# @app.get("/canales")
# async def get_todos_canales(session: Session = Depends(get_session)):

#     return


# Crear canal
@app.post("/usuarios/{id_usuario}/canales")
async def crear_canal(id_usuario: int, canal: CanalCreate, session: Session = Depends(get_session)):
    if session.exec(select(Canales).where(Canales.nombre == canal.nombre_canal)).first():
        raise HTTPException(status_code=400, detail="Nombre ya existente")
    else:
        canal_db: Canales = Canales(
            id_usuario_dueno= id_usuario,
            nombre = canal.nombre_canal,
            contenido_principal = canal.contenido_principal
        )
        session.add(canal_db)
        session.commit()
        session.refresh(canal_db)

        rol_admin = RolUsuarioCanal(
            id_usuario = id_usuario,
            id_canal=canal_db.id_canal,
            rol= RolAdministradorParticipanteT.ADMINISTRADOR
        )
        session.add(rol_admin)
        session.commit()
        return canal_db


# Ver canal
@app.get("/usuarios/{id_usuario}/canales/{id_canal}")
async def get_canal(id_usuario: int, id_canal: int, session: Session = Depends(get_session)):
    canal = session.get(Canales, id_canal)
    if not canal:
        raise HTTPException(status_code=404, detail="Canal no encontrado")
    elif not es_participante_o_admin(session, id_usuario, id_canal):
      raise HTTPException(status_code=403, detail="No tienes acceso a este canal")
    return canal


# Actualizar contenido/nombre canal
@app.put("/usuarios/{id_usuario}/canales/{id_canal}")
async def actualizar_contenido_canal(id_usuario: int, id_canal: int, canal_update: CanalUpdate, session: Session = Depends(get_session)):
    canal_db = session.get(Canales, id_canal)
    if not canal_db:
        raise HTTPException(status_code=404, detail="Canal no encontrado")
    elif not session.exec(
        select(RolUsuarioCanal).where(
            RolUsuarioCanal.id_usuario == id_usuario,
            RolUsuarioCanal.id_canal == id_canal,
            RolUsuarioCanal.rol == RolAdministradorParticipanteT.ADMINISTRADOR
        )
    ).first():
        raise HTTPException(status_code=403, detail="Permisos insuficientes")
    
    update_data = canal_update.model_dump(exclude_unset=True)
    canal_db.sqlmodel_update(update_data)
    session.add(canal_db)
    session.commit()
    session.refresh(canal_db)
    return canal_db


# Eliminar canal
@app.delete("/usuarios/{id_usuario}/canales/{id_canal}")
async def eliminar_canal(id_usuario:int, id_canal:int, session: Session = Depends(get_session)):
    canal_db = session.get(Canales, id_canal)
    if not canal_db:
        raise HTTPException(status_code=404, detail="Canal no encontrado")
    
    session.delete(canal_db)
    session.commit()
    return {"message": "Canal eliminado exitosamente"}


# SALAS

# Ver salas
@app.get("/usuarios/{id_usuario}/canales/{id_canal}/salas")
async def get_salas_canal(id_usuario: int, id_canal: int, session: Session = Depends(get_session)):
    salas = session.exec(
        select(Salas).distinct()
        .join(  # distinct() evita duplicados
            Canales,
            Salas.id_canal == Canales.id_canal)
        .join(
            RolUsuarioCanal,
            Canales.id_canal == RolUsuarioCanal.id_canal,
        ).where(
            Canales.id_canal == id_canal,            
            RolUsuarioCanal.id_usuario == id_usuario,
            RolUsuarioCanal.rol.in_([
                RolAdministradorParticipanteT.ADMINISTRADOR,
                RolAdministradorParticipanteT.PARTICIPANTE
            ])
        )
    ).all()
    return salas

# Crear sala
@app.post("/usuarios/{id_usuario}/canales/{id_canal}/salas") 
async def crear_sala(id_usuario: int, id_canal: int, sala: SalaCreate, session: Session = Depends(get_session)):
    if not session.exec(
        select(RolUsuarioCanal).where(
            RolUsuarioCanal.id_usuario == id_usuario,
            RolUsuarioCanal.id_canal == id_canal,
            RolUsuarioCanal.rol == RolAdministradorParticipanteT.ADMINISTRADOR)
    ).first():
      raise HTTPException(status_code=403, detail="No tienes permisos suficientes")

    else:
        sala_db: Salas = Salas(
            id_canal = id_canal,
            tipo = sala.tipo,
            nombre = sala.nombre_sala
        )
        session.add(sala_db)
        session.commit()
        session.refresh(sala_db)

        return sala_db

# actualizar sala
@app.patch("/usuarios/{id_usuario}/canales/{id_canal}/salas/{id_sala}")
async def actualizar_sala(id_usuario: int, id_canal: int, id_sala: int, sala_update: SalaUpdate, session: Session = Depends(get_session)):
    sala_db = session.get(Salas, id_sala)
    if not sala_db:
        raise HTTPException(status_code=404, detail="Sala no encontrado")
    elif not es_admin(session, id_usuario, id_canal):
        raise HTTPException(status_code=403, detail="Permisos insuficientes")
    
    update_data = sala_update.model_dump(exclude_unset=True) # Lo que no se envia en frontend no se tiene en cuenta
    sala_db.sqlmodel_update(update_data)
    session.add(sala_db)
    session.commit()
    session.refresh(sala_db)
    return sala_db

# Eliminar sala
@app.delete("/usuarios/{id_usuario}/canales/{id_canal}/salas/{id_sala}")
async def eliminar_sala(id_usuario: int, id_canal: int, id_sala: int, session: Session = Depends(get_session)):
    sala_db = session.get(Salas, id_sala)
    if not sala_db:
        raise HTTPException(status_code=404, detail="Sala no encontrada")
    elif id_canal != sala_db.id_canal:
        raise HTTPException(status_code=404, detail="La sala no pertenece a ese canal")       
    elif not es_admin(session, id_usuario, id_canal):
        raise HTTPException(status_code=403, detail="Permisos insuficientes")
    else:
        session.delete(sala_db)
        session.commit()
        return {"message": "Sala eliminada exitosamente"}


# AMIGOS

# Get lista amigos
@app.get("/usuarios/{id_usuario}/amigos")
async def get_amigos(id_usuario: int, session: Session = Depends(get_session)):
    amigos = session.exec(
        select(Amigos, Usuarios)
        .join(
            Usuarios,
            Amigos.id_usuario2 == Usuarios.id_usuario
        ).where(
            Amigos.id_usuario1 == id_usuario
        )
    ).all()

    lista_amigos = []
    for amigo in amigos:
        lista_amigos.append({
            "id_amigo": amigo[1].id_usuario,
            "username": amigo[1].username,
            "email": amigo[1].email,
            "fecha_amistad": amigo[0].fecha_amistad
        })

    return lista_amigos


# Añadir amigo
@app.put("/usuarios/{id_usuario}/amigos/{id_usuario2}")
async def anhadir_amigo(id_usuario: int, id_usuario2: int, session: Session = Depends(get_session)):
    if not session.get(Usuarios, id_usuario) or not session.get(Usuarios, id_usuario2):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")   
    elif id_usuario2 == id_usuario:
        raise HTTPException(status_code=400, detail="No puedes añadirte como amigo")   
    elif session.exec(
        select(Amigos).where(
            Amigos.id_usuario1 == id_usuario,
            Amigos.id_usuario2 == id_usuario2
        )
    ).first():
        raise HTTPException(status_code=400, detail="Ya sois amigos") 
    else:
        amistad = Amigos(
            id_usuario1 = id_usuario,
            id_usuario2 = id_usuario2,
            fecha_amistad = date.today()
        )
        session.add(amistad)
        session.commit()
        session.refresh(amistad)

        return {"message": "Amigo añadido"}

# Eliminar amigo
@app.delete("/usuarios/{id_usuario}/amigos/{id_usuario2}")
async def eliminar_amigo(id_usuario: int, id_usuario2: int, session: Session = Depends(get_session)):
    amistad = session.exec(
        select(Amigos).where(
            Amigos.id_usuario1 == id_usuario,
            Amigos.id_usuario2 == id_usuario2
        )
    ).first()
    
    if not amistad:
        raise HTTPException(status_code=404, detail="Amistad no encontrada")
    
    session.delete(amistad)
    session.commit()
    
    return {"message": "Amigo eliminado exitosamente"}


# MENSAJES

# Ver mensajes sala
@app.get("/usuarios/{id_usuario}/canales/{id_canal}/salas/{id_sala}")
async def get_mensajes_sala(id_usuario: int, id_canal: int, id_sala: int, session: Session = Depends(get_session)):
    sala = session.get(Salas, id_sala)
    
    if not sala or sala.id_canal != id_canal:
        raise HTTPException(status_code=404, detail="Sala no encontrada") 
    elif not es_participante_o_admin(session, id_usuario, id_canal):
        raise HTTPException(status_code=403, detail="Permisos insuficientes") 
    else:
        mensajes = session.exec(Mensajes).where(
            Mensajes.id_sala == id_sala
        ).order_by(Mensajes.fecha.desc()).all()
        return mensajes


# Crear mensaje en sala
@app.post("/usuarios/{id_usuario}/canales/{id_canal}/salas/{id_sala}")
async def crear_mensaje_sala(
    id_usuario: int, 
    id_canal: int, 
    id_sala: int, 
    contenido: str, 
    session: Session = Depends(get_session)
):        
    sala = session.get(Salas, id_sala)
    usuario = session.get(Usuarios, id_usuario)

    if not sala or sala.id_canal != id_canal:
        raise HTTPException(status_code=404, detail="Sala no encontrada")    
    elif not es_participante_o_admin(session, id_usuario, id_canal):
        raise HTTPException(status_code=403, detail="No tienes acceso a esta sala")    
    elif not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    else:
        mensaje = Mensajes(
        id_sala=id_sala,
        id_usuario_emisor=id_usuario,
        contenido=contenido,
        fecha=datetime.now(), 
    )
    session.add(mensaje)
    session.commit()
    session.refresh(mensaje)
    
    return mensaje


# Eliminar mensaje sala
@app.delete("/usuarios/{id_usuario}/canales/{id_canal}/salas/{id_sala}/mensajes/{id_mensaje}")
async def eliminar_mensaje_sala(id_usuario: int, id_canal: int, id_sala: int, id_mensaje: int, session: Session = Depends(get_session)):
    mensaje = session.get(Mensajes, id_mensaje)
    sala = session.get(Salas, id_sala)
    if not mensaje or mensaje.id_sala != id_sala:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    
    elif not sala or sala.id_canal != id_canal:
        raise HTTPException(status_code=404, detail="Sala no encontrada")
    
    elif not es_participante_o_admin(session, id_usuario, id_canal):
        raise HTTPException(status_code=403, detail="No tienes acceso a esta sala")
    
    elif mensaje.id_usuario_emisor != id_usuario and not es_admin(session, id_usuario, id_canal):
        raise HTTPException(status_code=403, detail="Solo el autor o admin puede eliminar")
    
    else:
        session.delete(mensaje)
        session.commit()
        
        return {"message": "Mensaje eliminado exitosamente"}
    

# Ver mensajes amigo
@app.get("/usuarios/{id_usuario}/amigos/{id_usuario2}")
async def get_mensajes_amigo(id_usuario: int, id_usuario2: int, session: Session = Depends(get_session)):
        
    if not son_amigos(session, id_usuario, id_usuario2):
        raise HTTPException(status_code=404, detail="No sois amigos")
    
    mensajes = session.exec(
        select(Mensajes)
        .where(
            or_(
                and_(Mensajes.id_usuario_emisor == id_usuario, Mensajes.id_usuario_receptor == id_usuario2),
                and_(Mensajes.id_usuario_emisor == id_usuario2, Mensajes.id_usuario_receptor == id_usuario)
            )
        )
        .order_by(Mensajes.fecha.asc())  # Más antiguos primero
    ).all()
    
    return mensajes


# Crear mensaje amigo
@app.post("/usuarios/{id_usuario}/amigos/{id_usuario2}")
async def enviar_mensaje_amigo(mensaje: MensajeAmigoCreate, id_usuario: int, id_usuario2: int, session: Session = Depends(get_session)):
    
    if not await son_amigos(session, id_usuario, id_usuario2):
        raise HTTPException(status_code=403, detail = "No sois amigos")
    else:
        nuevo_mensaje_amigo: Mensajes = Mensajes(
            contenido = mensaje.contenido,
            id_usuario_emisor = id_usuario,
            fecha = datetime.now(UTC),
            id_usuario_receptor = id_usuario2
        )

        session.add(nuevo_mensaje_amigo)
        session.commit()
        session.refresh(nuevo_mensaje_amigo)

        return nuevo_mensaje_amigo
        
# Eliminar mensaje amigo
@app.delete("/usuarios/{id_usuario}/amigos/{id_usuario2}/mensajes/{id_mensaje}")
async def eliminar_mensaje_amigo(id_mensaje: int, id_usuario: int, id_usuario2: int, session: Session = Depends(get_session)):
    
    mensaje_db = session.get(Mensajes, id_mensaje)

    if not await son_amigos(session, id_usuario, id_usuario2):
        raise HTTPException(status_code=403, detail = "No sois amigos")
    elif not mensaje_db:
        raise HTTPException(status_code=404, detail = "No existe el mensaje")
    elif mensaje_db.id_usuario_emisor != id_usuario:
        raise HTTPException(status_code=403, detail = "Falta de permisos")
    else:
        session.delete(mensaje_db)
        session.commit()
        return {"message": "Mensaje eliminado exitosamente"}



# # WEBSOCKETS de la DOC

# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# from fastapi.responses import HTMLResponse

# # app = FastAPI()

# html = """
# <!DOCTYPE html>
# <html>
#     <head>
#         <title>Chat</title>
#     </head>
#     <body>
#         <h1>WebSocket Chat</h1>
#         <h2>Your ID: <span id="ws-id"></span></h2>
#         <form action="" onsubmit="sendMessage(event)">
#             <input type="text" id="messageText" autocomplete="off"/>
#             <button>Send</button>
#         </form>
#         <ul id='messages'>
#         </ul>
#         <script>
#             var id_usuario = Date.now()
#             document.querySelector("#ws-id").textContent = id_usuario;
#             var ws = new WebSocket(`ws://localhost:8001/ws/${id_usuario}`);
#             ws.onmessage = function(event) {
#                 var messages = document.getElementById('messages')
#                 var message = document.createElement('li')
#                 var content = document.createTextNode(event.data)
#                 message.appendChild(content)
#                 messages.appendChild(message)
#             };
#             function sendMessage(event) {
#                 var input = document.getElementById("messageText")
#                 ws.send(input.value)
#                 input.value = ''
#                 event.preventDefault()
#             }
#         </script>
#     </body>
# </html>
# """


# class ConnectionManager:
#     def __init__(self):
#         self.active_connections: list[WebSocket] = []

#     async def connect(self, websocket: WebSocket):
#         await websocket.accept()
#         self.active_connections.append(websocket)

#     def disconnect(self, websocket: WebSocket):
#         self.active_connections.remove(websocket)

#     async def send_personal_message(self, message: str, websocket: WebSocket):
#         await websocket.send_text(message)

#     async def broadcast(self, message: str):
#         for connection in self.active_connections:
#             await connection.send_text(message)


# manager = ConnectionManager()


# @app.get("/")
# async def get():
#     return HTMLResponse(html)


# @app.websocket("/ws/{id_usuario}")
# async def websocket_endpoint(websocket: WebSocket, id_usuario: int):
#     await manager.connect(websocket)
#     try:
#         while True:
#             data = await websocket.receive_text()
#             await manager.send_personal_message(f"You wrote: {data}", websocket)
#             await manager.broadcast(f"Client #{id_usuario} says: {data}")
#     except WebSocketDisconnect:
#         manager.disconnect(websocket)
#         await manager.broadcast(f"Client #{id_usuario} left the chat")

# WEBSOKCETS

class ConnectionManager:
    def __init__(self):
        self.salas: Dict[str, Dict[int, WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, id_sala: str, id_usuario: int):
        await websocket.accept()
        if id_sala not in self.salas:
            self.salas[id_sala] = {}
        self.salas[id_sala][id_usuario] = websocket

    def disconnect(self, id_sala: str, id_usuario: int):
        if id_sala in self.salas and id_usuario in self.salas[id_sala]:
            del self.salas[id_sala][id_usuario]
            if not self.salas[id_sala]:
                del self.salas[id_sala]

    async def broadcast (self, mensaje: str, id_sala: str, exclude_id_usuario: int | None = None):
        if id_sala in self.salas:
            for uid, ws in list(self.salas[id_sala].items()):
                if exclude_id_usuario is None or uid != exclude_id_usuario:                    
                    try:
                        await ws.send_text(mensaje)
                    except:
                        del self.salas[id_sala][uid]

manager = ConnectionManager()


# endpoints con ws

# sala
@app.websocket("/ws/usuarios/{id_usuario}/canales/{id_canal}/salas/{id_sala}")
async def websocket_sala(websocket: WebSocket, id_usuario: int, id_canal: int, id_sala: int, session: Session = Depends(get_session)):
    if es_participante_o_admin(session, id_usuario, id_canal):

        id_sala_str = f"{id_canal}_{id_sala}"
        await manager.connect(websocket, id_sala_str, id_usuario)

        try:
            while True:
                data = await websocket.receive_text()
                # await manager.send_personal_message(data, websocket)
                await manager.broadcast(data, id_sala_str, id_usuario)
        except WebSocketDisconnect:
            manager.disconnect(id_sala_str, id_usuario)
            # await manager.broadcast(f"Client #{id_usuario} left the chat")            
    else:
        await websocket.close(code=403)

# dm
@app.websocket("/ws/usuarios/{id_usuario}/amigos/{id_usuario2}")
async def websocket_dm(websocket: WebSocket, id_usuario: int, id_usuario2: int):

    id_sala_dm = f"{min(id_usuario,id_usuario2)}_{max(id_usuario, id_usuario2)}"
    await manager.connect(websocket, id_sala_dm, id_usuario)

    try:
        while True:
            data = await websocket.receive_text()
            # await manager.send_personal_message(data, websocket)
            await manager.broadcast(data, id_sala_dm, id_usuario)
    except WebSocketDisconnect:
        manager.disconnect(id_sala_dm, id_usuario)
        # await manager.broadcast(f"Client #{id_usuario} left the chat")            
