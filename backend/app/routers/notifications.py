from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from ..dependencies import SessionDep, get_current_user
from ..models import Mensajes, Notificaciones, Salas, UsuarioNotificacion, Usuarios
from ..schemas import MarcarLeidasRequest, NotificacionResponse, User


router = APIRouter(tags=["notifications"])

# NOTIFICACIONES

# Ver notificaciones de un usuario
@router.get("/users/me/notifications", response_model=list[NotificacionResponse])
async def get_user_notifications(
    current_user: Annotated[User, Depends(get_current_user)],
    session: SessionDep
):
    resultados = session.exec(
        select(UsuarioNotificacion, Notificaciones, Mensajes)
        .join(Notificaciones, UsuarioNotificacion.id_notificacion == Notificaciones.id_notificacion)
        .join(Mensajes, Notificaciones.id_mensaje == Mensajes.id_mensaje)
        .where(
            UsuarioNotificacion.id_usuario == current_user.id_usuario,
            UsuarioNotificacion.leida == False
        )
        .order_by(Mensajes.fecha.asc())
    ).all()

    return [
        NotificacionResponse(
            id_notificacion=notif.id_notificacion,
            contenido=notif.contenido_notif,
            id_mensaje=notif.id_mensaje,
            tipo="sala" if mensaje.id_sala else "dm",
            fecha=mensaje.fecha,
            id_sala=mensaje.id_sala,
            id_canal=session.get(Salas, mensaje.id_sala).id_canal if mensaje.id_sala else None,
            id_usuario_emisor=mensaje.id_usuario_emisor
        )
        for usuario_notif, notif, mensaje in resultados
    ]

@router.patch("/users/me/notifications/read")
async def marcar_notificaciones_leidas(
    current_user: Annotated[User, Depends(get_current_user)],
    session: SessionDep,
    body: MarcarLeidasRequest
):
    if body.id_sala is None and body.id_usuario_emisor is None:
        raise HTTPException(status_code=422, detail="Se requiere id_sala o id_usuario_emisor")

    # Buscar notificaciones no leídas del usuario ligadas a mensajes de esa sala o DM
    resultados = session.exec(
        select(UsuarioNotificacion)
        .join(Notificaciones, UsuarioNotificacion.id_notificacion == Notificaciones.id_notificacion)
        .join(Mensajes, Notificaciones.id_mensaje == Mensajes.id_mensaje)
        .where(
            UsuarioNotificacion.id_usuario == current_user.id_usuario,
            UsuarioNotificacion.leida == False,
            Mensajes.id_sala == body.id_sala if body.id_sala else Mensajes.id_usuario_emisor == body.id_usuario_emisor
        )
    ).all()

    for usuario_notif in resultados:
        usuario_notif.leida = True

    session.commit()

    return {"actualizadas": len(resultados)}