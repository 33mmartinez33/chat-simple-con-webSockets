import datetime
import json
from typing import Annotated, Dict

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from datetime import timezone, datetime

from pydantic import ValidationError

from ..dependencies import SessionDep, es_participante_o_admin, get_current_user, son_amigos, verify_origin
from ..schemas import MensajeWs, User
from ..models import Usuarios, Mensajes


router = APIRouter(tags=["ws"])

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


    async def broadcast (self, mensaje: str, id_sala: str):
        if id_sala in self.salas:
            for uid, ws in list(self.salas[id_sala].items()):
                try:
                    await ws.send_text(mensaje)
                except:
                    del self.salas[id_sala][uid]


manager = ConnectionManager()




# endpoints con ws

# Mensajes sala
@router.websocket("/ws/users/me/channels/{id_canal}/rooms/{id_sala}")
async def websocket_sala(websocket: WebSocket, current_user: Annotated[User, Depends(get_current_user)], _: Annotated[None, Depends(verify_origin)], id_canal: int, id_sala: int, session: SessionDep):
    if es_participante_o_admin(session, current_user.id_usuario, id_canal):

        id_sala_str = f"{id_canal}_{id_sala}"
        await manager.connect(websocket, id_sala_str, current_user.id_usuario)

        try:
            while True:
                data = await websocket.receive_text()

                try:
                    mensaje_data = MensajeWs.model_validate_json(data)
                except ValidationError:
                    await websocket.send_text(json.dumps({"error": "Mensaje inválido"}))
                else:

                    nuevo_mensaje = Mensajes(
                        contenido=mensaje_data.contenido,
                        id_usuario_emisor=current_user.id_usuario,
                        id_sala=id_sala,
                        fecha=datetime.now(timezone.utc)
                    )
                    session.add(nuevo_mensaje)
                    session.commit()
                    session.refresh(nuevo_mensaje)

                    usuario = session.get(Usuarios, current_user.id_usuario)
                    
                    # broadcast a los otros usuarios de la sala  y unicamente a estos, se controla mediante str, qe representa la conversacion unica entre ellos
                    await manager.broadcast(json.dumps({
                        "id_mensaje": nuevo_mensaje.id_mensaje,
                        "contenido": nuevo_mensaje.contenido,
                        "id_usuario_emisor": current_user.id_usuario,
                        "username": usuario.username,
                        "fecha": nuevo_mensaje.fecha.isoformat()
                    }), id_sala_str)

        except WebSocketDisconnect:
            manager.disconnect(id_sala_str, current_user.id_usuario)

    else:
        await websocket.close(code=403)


# Mensajes amigo
@router.websocket("/ws/users/me/friends/{id_usuario2}")
async def websocket_dm(websocket: WebSocket, current_user: Annotated[User, Depends(get_current_user)], _: Annotated[None, Depends(verify_origin)], id_usuario2: int, session: SessionDep):

    if son_amigos(session, current_user.id_usuario, id_usuario2):

        id_sala_amigo = f"{min(current_user.id_usuario, id_usuario2)}_{max(current_user.id_usuario, id_usuario2)}"
        await manager.connect(websocket, id_sala_amigo, current_user.id_usuario)

        try:
            while True:
                data = await websocket.receive_text()

                try:
                    mensaje_data = MensajeWs.model_validate_json(data)
                except ValidationError:
                    await websocket.send_text(json.dumps({"error": "Mensaje inválido"}))
                else:
                    
                    nuevo_mensaje = Mensajes(
                        contenido=mensaje_data.contenido,
                        id_usuario_emisor=current_user.id_usuario,
                        id_usuario_receptor=id_usuario2,
                        fecha=datetime.now(timezone.utc)
                    )
                    session.add(nuevo_mensaje)
                    session.commit()
                    session.refresh(nuevo_mensaje)

                    usuario = session.get(Usuarios, current_user.id_usuario)

                    await manager.broadcast(json.dumps({
                        "id_mensaje": nuevo_mensaje.id_mensaje,
                        "contenido": nuevo_mensaje.contenido,
                        "id_usuario_emisor": current_user.id_usuario,
                        "username": usuario.username,
                        "fecha": nuevo_mensaje.fecha.isoformat()
                    }), id_sala_amigo)

        except WebSocketDisconnect:
            manager.disconnect(id_sala_amigo, current_user.id_usuario)

    else:
        await websocket.close(code=403)