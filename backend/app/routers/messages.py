from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import and_, or_, select

from ..dependencies import es_admin, es_participante_o_admin, son_amigos, SessionDep, get_current_user
from ..models import Mensajes, Salas, Usuarios
from ..schemas import User

router = APIRouter(tags=["messages"])

# MENSAJES

# Ver mensajes sala
@router.get("/users/me/channels/{id_canal}/rooms/{id_sala}/messages")
async def get_mensajes_sala(current_user: Annotated[User, Depends(get_current_user)], id_canal: int, id_sala: int, session: SessionDep):
    sala = session.get(Salas, id_sala)
   
    if not sala or sala.id_canal != id_canal:
        raise HTTPException(status_code=404, detail="Sala no encontrada")
    elif not es_participante_o_admin(session, current_user.id_usuario, id_canal):
        raise HTTPException(status_code=403, detail="Permisos insuficientes")
    else:
        mensajes = session.exec(
            select(Mensajes, Usuarios.username)
            .join(Usuarios, Mensajes.id_usuario_emisor == Usuarios.id_usuario)
            .where(Mensajes.id_sala == id_sala)
            .order_by(Mensajes.fecha.asc())
        ).all()
        return [
            {**mensaje.model_dump(), "username": username}
            for mensaje, username in mensajes
        ]



# Eliminar mensaje sala
@router.delete("/users/me/channels/{id_canal}/rooms/{id_sala}/messages/{id_mensaje}")
async def eliminar_mensaje_sala(current_user: Annotated[User, Depends(get_current_user)], id_canal: int, id_sala: int, id_mensaje: int, session: SessionDep):
    mensaje = session.get(Mensajes, id_mensaje)
    sala = session.get(Salas, id_sala)
    if not mensaje or mensaje.id_sala != id_sala:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
   
    elif not sala or sala.id_canal != id_canal:
        raise HTTPException(status_code=404, detail="Sala no encontrada")
   
    elif not es_participante_o_admin(session, current_user.id_usuario, id_canal):
        raise HTTPException(status_code=403, detail="No tienes acceso a esta sala")
   
    elif mensaje.id_usuario_emisor != current_user.id_usuario and not es_admin(session, current_user.id_usuario, id_canal):
        raise HTTPException(status_code=403, detail="Solo el autor o admin puede eliminar")
   
    else:
        session.delete(mensaje)
        session.commit()
       
        return {"message": "Mensaje eliminado exitosamente"}
   


# Ver mensajes amigo
@router.get("/users/me/friends/{id_usuario2}/messages")
async def get_mensajes_amigo(current_user: Annotated[User, Depends(get_current_user)], id_usuario2: int, session: SessionDep):
       
    if not son_amigos(session, current_user.id_usuario, id_usuario2):
        raise HTTPException(status_code=404, detail="No sois amigos")
   
    mensajes_username = session.exec(
        select(Mensajes, Usuarios.username)
        .join(Usuarios, Mensajes.id_usuario_emisor == Usuarios.id_usuario)
        .where(
            or_(
                and_(Mensajes.id_usuario_emisor == current_user.id_usuario, Mensajes.id_usuario_receptor == id_usuario2),
                and_(Mensajes.id_usuario_emisor == id_usuario2, Mensajes.id_usuario_receptor == current_user.id_usuario)
            )
        )
        .order_by(Mensajes.fecha.asc())  # Más antiguos primero
    ).all()
   
    return [
        {**mensaje.model_dump(), "username": username}
        for mensaje, username in mensajes_username
    ]
       
# Eliminar mensaje amigo
@router.delete("/users/me/friends/{id_usuario2}/messages/{id_mensaje}")
async def eliminar_mensaje_amigo(id_mensaje: int, current_user: Annotated[User, Depends(get_current_user)], id_usuario2: int, session: SessionDep):
   
    mensaje_db = session.get(Mensajes, id_mensaje)


    if not son_amigos(session,current_user.id_usuario, id_usuario2):
        raise HTTPException(status_code=403, detail = "No sois amigos")
    elif not mensaje_db:
        raise HTTPException(status_code=404, detail = "No existe el mensaje")
    elif mensaje_db.id_usuario_emisor != current_user.id_usuario:
        raise HTTPException(status_code=403, detail = "Falta de permisos")
    else:
        session.delete(mensaje_db)
        session.commit()
        return {"message": "Mensaje eliminado exitosamente"}

