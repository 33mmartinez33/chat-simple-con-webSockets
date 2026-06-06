import json
from typing import Annotated, Dict

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from datetime import timezone, datetime
from pydantic import ValidationError
from sqlmodel import Session, select

from ..dependencies import SessionDep, es_participante_o_admin, get_current_user, son_amigos, verify_origin
from ..schemas import MensajeWs, User
from ..models import Canales, Mensajes, Notificaciones, RolUsuarioCanal, Salas, UsuarioNotificacion, Usuarios


router = APIRouter(tags=["ws"])


# ── MANAGERS ───────────────────────────────────────────────────────────────────

# Gestiona las conexiones WebSocket activas en salas de canal
# salas: diccionario {id_sala_str -> {id_usuario -> WebSocket}}
class ConnectionManager:
    def __init__(self):
        self.salas: Dict[str, Dict[int, WebSocket]] = {}

    # Acepta la conexión y la registra en la sala correspondiente
    # Parámetros:
    #   websocket: conexión entrante
    #   id_sala: identificador de sala (formato "id_canal_id_sala")
    #   id_usuario: ID del usuario que se conecta
    async def connect(self, websocket: WebSocket, id_sala: str, id_usuario: int):
        await websocket.accept()
        if id_sala not in self.salas:
            self.salas[id_sala] = {}
        self.salas[id_sala][id_usuario] = websocket

    # Elimina la conexión del usuario de la sala; borra la sala si queda vacía
    # Parámetros:
    #   id_sala: identificador de sala
    #   id_usuario: ID del usuario que se desconecta
    def disconnect(self, id_sala: str, id_usuario: int):
        if id_sala in self.salas and id_usuario in self.salas[id_sala]:
            del self.salas[id_sala][id_usuario]
            if not self.salas[id_sala]:
                del self.salas[id_sala]

    # Envía mensaje a todos los usuarios conectados en la sala
    # Si una conexión falla, se elimina silenciosamente del registro
    # Parámetros:
    #   mensaje: texto JSON a enviar
    #   id_sala: sala destino
    async def broadcast(self, mensaje: str, id_sala: str):
        if id_sala in self.salas:
            for uid, ws in list(self.salas[id_sala].items()):
                try:
                    await ws.send_text(mensaje)
                except:
                    del self.salas[id_sala][uid]


# Gestiona las conexiones WebSocket para notificaciones en tiempo real
# conexiones: diccionario {id_usuario -> WebSocket}
class NotificationManager:
    def __init__(self):
        self.conexiones: Dict[int, WebSocket] = {}

    # Acepta la conexión y la registra para el usuario indicado
    # Parámetros:
    #   websocket: conexión entrante
    #   id_usuario: ID del usuario propietario de la conexión
    async def connect(self, websocket: WebSocket, id_usuario: int):
        await websocket.accept()
        self.conexiones[id_usuario] = websocket

    # Elimina la conexión del usuario del registro
    def disconnect(self, id_usuario: int):
        self.conexiones.pop(id_usuario, None)

    # Envía un mensaje JSON al usuario si tiene conexión activa
    # Si la conexión está rota, la elimina silenciosamente
    # Parámetros:
    #   id_usuario: destinatario
    #   mensaje: diccionario que se serializa a JSON
    async def enviar(self, id_usuario: int, mensaje: dict):
        if id_usuario in self.conexiones:
            try:
                await self.conexiones[id_usuario].send_text(json.dumps(mensaje))
            except:
                del self.conexiones[id_usuario]


manager = ConnectionManager()
notification_manager = NotificationManager()


# ── NOTIFICACIONES ─────────────────────────────────────────────────────────────

# Crea notificaciones para los miembros del canal que no están activos en la sala
# Solo genera notificación para usuarios ausentes (no conectados a la sala en ese momento)
# Parámetros:
#   session: sesión de base de datos
#   nuevo_mensaje: mensaje recién guardado
#   id_canal: canal al que pertenece la sala
#   id_sala: sala donde se envió el mensaje
#   id_sala_str: clave de sala usada en ConnectionManager
#   emisor: usuario que envió el mensaje
#   sala: objeto Salas con nombre de la sala
#   canal: objeto Canales con nombre del canal
async def crear_notif_sala(
    session: Session,
    nuevo_mensaje: Mensajes,
    id_canal: int,
    id_sala: int,
    id_sala_str: str,
    emisor: Usuarios,
    sala: Salas,
    canal: Canales
):
    usuarios_canal = session.exec(
        select(RolUsuarioCanal).where(
            RolUsuarioCanal.id_canal == id_canal
        )
    ).all()

    activos = set(manager.salas.get(id_sala_str, {}).keys())

    ausentes = [
        u.id_usuario for u in usuarios_canal
        if u.id_usuario not in activos and u.id_usuario != nuevo_mensaje.id_usuario_emisor
    ]

    if ausentes:
        contenido = f"{emisor.username} ha enviado un mensaje en #{sala.nombre_sala} del canal {canal.nombre}"

        notificacion = Notificaciones(
            id_mensaje=nuevo_mensaje.id_mensaje,
            contenido_notif=contenido
        )
        session.add(notificacion)
        session.flush()

        for id_usuario in ausentes:
            session.add(UsuarioNotificacion(
                id_usuario=id_usuario,
                id_notificacion=notificacion.id_notificacion,
                leida=False
            ))

        session.commit()

        # Envío en tiempo real a los usuarios ausentes que tengan WebSocket de notificaciones abierto
        for id_usuario in ausentes:
            await notification_manager.enviar(id_usuario, {
                "id_notificacion": notificacion.id_notificacion,
                "contenido": contenido,
                "id_mensaje": nuevo_mensaje.id_mensaje,
                "tipo": "sala",
                "id_sala": id_sala,
                "id_canal": id_canal
            })


# Crea una notificación de mensaje directo si el receptor no está en la sala de DM
# Parámetros:
#   session: sesión de base de datos
#   nuevo_mensaje: mensaje recién guardado
#   id_sala_amigo: clave de sala DM usada en ConnectionManager
#   emisor: usuario que envió el mensaje
#   id_usuario_receptor: ID del destinatario del DM
async def crear_notif_amigo(
    session: Session,
    nuevo_mensaje: Mensajes,
    id_sala_amigo: str,
    emisor: Usuarios,
    id_usuario_receptor: int
):
    activos = set(manager.salas.get(id_sala_amigo, {}).keys())

    if id_usuario_receptor not in activos:
        contenido = f"{emisor.username} te ha enviado un mensaje directo"

        notificacion = Notificaciones(
            id_mensaje=nuevo_mensaje.id_mensaje,
            contenido_notif=contenido
        )
        session.add(notificacion)
        session.flush()

        session.add(UsuarioNotificacion(
            id_usuario=id_usuario_receptor,
            id_notificacion=notificacion.id_notificacion,
            leida=False
        ))

        session.commit()

        await notification_manager.enviar(id_usuario_receptor, {
            "id_notificacion": notificacion.id_notificacion,
            "contenido": contenido,
            "id_mensaje": nuevo_mensaje.id_mensaje,
            "tipo": "dm",
            "id_usuario_emisor": nuevo_mensaje.id_usuario_emisor
        })


# ── ENDPOINTS ──────────────────────────────────────────────────────────────────

# WebSocket para recibir notificaciones en tiempo real del usuario autenticado
# Se mantiene abierto escuchando mensajes del cliente (keepalive)
@router.websocket("/ws/users/me/notifications")
async def websocket_notifications(websocket: WebSocket, current_user: Annotated[User, Depends(get_current_user)], _: Annotated[None, Depends(verify_origin)], session: SessionDep):
    await notification_manager.connect(websocket, current_user.id_usuario)

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        notification_manager.disconnect(current_user.id_usuario)


# WebSocket para chat en tiempo real en una sala de canal
# Valida que el usuario sea miembro del canal antes de aceptar la conexión
# Parámetros de ruta:
#   id_canal: canal al que pertenece la sala
#   id_sala: sala a la que se conecta el usuario
@router.websocket("/ws/users/me/channels/{id_canal}/rooms/{id_sala}")
async def websocket_sala(websocket: WebSocket, current_user: Annotated[User, Depends(get_current_user)], _: Annotated[None, Depends(verify_origin)], id_canal: int, id_sala: int, session: SessionDep):
    if es_participante_o_admin(session, current_user.id_usuario, id_canal):

        # La clave de sala combina canal y sala para garantizar unicidad entre canales
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

                    await manager.broadcast(json.dumps({
                        "id_mensaje": nuevo_mensaje.id_mensaje,
                        "contenido": nuevo_mensaje.contenido,
                        "id_usuario_emisor": current_user.id_usuario,
                        "username": usuario.username,
                        "fecha": nuevo_mensaje.fecha.isoformat()
                    }), id_sala_str)

                    sala = session.get(Salas, id_sala)
                    canal = session.get(Canales, id_canal)
                    await crear_notif_sala(session, nuevo_mensaje, id_canal, id_sala, id_sala_str, usuario, sala, canal)

        except WebSocketDisconnect:
            manager.disconnect(id_sala_str, current_user.id_usuario)

    else:
        await websocket.close(code=403)


# WebSocket para mensajes directos entre amigos
# Valida que exista relación de amistad antes de aceptar la conexión
# Parámetros de ruta:
#   id_usuario2: ID del amigo con quien se abre el chat
@router.websocket("/ws/users/me/friends/{id_usuario2}")
async def websocket_dm(websocket: WebSocket, current_user: Annotated[User, Depends(get_current_user)], _: Annotated[None, Depends(verify_origin)], id_usuario2: int, session: SessionDep):

    if son_amigos(session, current_user.id_usuario, id_usuario2):

        # Se usa el menor ID primero para que ambos usuarios compartan la misma sala
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

                    await crear_notif_amigo(session, nuevo_mensaje, id_sala_amigo, usuario, id_usuario2)

        except WebSocketDisconnect:
            manager.disconnect(id_sala_amigo, current_user.id_usuario)

    else:
        await websocket.close(code=403)
