from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from ..dependencies import es_admin, SessionDep, get_current_user
from ..models import Canales, RolAdministradorParticipanteT, RolUsuarioCanal, Salas
from ..schemas import SalaCreate, SalaUpdate, User

router = APIRouter(tags=["rooms"])

# SALAS

# Retorna los datos de una sala si el usuario es miembro del canal al que pertenece
# Parámetros de ruta:
#   id_canal: canal al que pertenece la sala
#   id_sala: sala a consultar
# Lanza HTTP 404 si la sala no existe o el usuario no es miembro
@router.get("/users/me/channels/{id_canal}/rooms/{id_sala}")
async def get_info_sala(current_user: Annotated[User, Depends(get_current_user)], id_canal: int, id_sala: int, session: SessionDep):
    sala = session.exec(
        select(Salas).distinct()
        .join(  # distinct() evita duplicados por múltiples joins
            Canales,
            Salas.id_canal == Canales.id_canal)
        .join(
            RolUsuarioCanal,
            Canales.id_canal == RolUsuarioCanal.id_canal,
        ).where(
            Canales.id_canal == id_canal,
            Salas.id_sala == id_sala,
            RolUsuarioCanal.id_usuario == current_user.id_usuario,
            RolUsuarioCanal.rol.in_([
                RolAdministradorParticipanteT.ADMINISTRADOR,
                RolAdministradorParticipanteT.PARTICIPANTE
            ])
        )
    ).first()

    if not sala:
        raise HTTPException(status_code=404, detail="Sala no encontrada")

    return sala


# Retorna todas las salas de un canal a las que el usuario tiene acceso
# Parámetros de ruta:
#   id_canal: canal cuyas salas se quieren listar
@router.get("/users/me/channels/{id_canal}/rooms")
async def get_salas_canal(current_user: Annotated[User, Depends(get_current_user)], id_canal: int, session: SessionDep):
    salas = session.exec(
        select(Salas).distinct()
        .join(  # distinct() evita duplicados por múltiples joins
            Canales,
            Salas.id_canal == Canales.id_canal)
        .join(
            RolUsuarioCanal,
            Canales.id_canal == RolUsuarioCanal.id_canal,
        ).where(
            Canales.id_canal == id_canal,
            RolUsuarioCanal.id_usuario == current_user.id_usuario,
            RolUsuarioCanal.rol.in_([
                RolAdministradorParticipanteT.ADMINISTRADOR,
                RolAdministradorParticipanteT.PARTICIPANTE
            ])
        )
    ).all()
    return salas


# Crea una nueva sala en el canal indicado
# Solo puede hacerlo un administrador del canal
# Parámetros de ruta:
#   id_canal: canal donde se crea la sala
# Parámetros del body:
#   sala: tipo (texto/voz) y nombre de la sala
@router.post("/users/me/channels/{id_canal}/rooms")
async def crear_sala(current_user: Annotated[User, Depends(get_current_user)], id_canal: int, sala: SalaCreate, session: SessionDep):
    if not session.exec(
        select(RolUsuarioCanal).where(
            RolUsuarioCanal.id_usuario == current_user.id_usuario,
            RolUsuarioCanal.id_canal == id_canal,
            RolUsuarioCanal.rol == RolAdministradorParticipanteT.ADMINISTRADOR)
    ).first():
        raise HTTPException(status_code=403, detail="No tienes permisos suficientes")
    else:
        sala_db: Salas = Salas(
            id_canal=id_canal,
            tipo=sala.tipo,
            nombre_sala=sala.nombre_sala
        )
        session.add(sala_db)
        session.commit()
        session.refresh(sala_db)
        return sala_db


# Actualiza tipo y/o nombre de una sala existente
# Solo puede hacerlo un administrador del canal
# Parámetros de ruta:
#   id_canal: canal al que pertenece la sala
#   id_sala: sala a actualizar
# Parámetros del body:
#   sala_update: campos a modificar (todos opcionales)
@router.patch("/users/me/channels/{id_canal}/rooms/{id_sala}")
async def actualizar_sala(current_user: Annotated[User, Depends(get_current_user)], id_canal: int, id_sala: int, sala_update: SalaUpdate, session: SessionDep):
    sala_db = session.get(Salas, id_sala)
    if not sala_db:
        raise HTTPException(status_code=404, detail="Sala no encontrado")
    elif not es_admin(session, current_user.id_usuario, id_canal):
        raise HTTPException(status_code=403, detail="Permisos insuficientes")

    # Los campos no enviados desde el frontend no se tienen en cuenta
    update_data = sala_update.model_dump(exclude_unset=True)
    sala_db.sqlmodel_update(update_data)
    session.add(sala_db)
    session.commit()
    session.refresh(sala_db)
    return sala_db


# Elimina una sala del canal
# Solo puede hacerlo un administrador del canal
# Parámetros de ruta:
#   id_canal: canal al que debe pertenecer la sala
#   id_sala: sala a eliminar
@router.delete("/users/me/channels/{id_canal}/rooms/{id_sala}")
async def eliminar_sala(current_user: Annotated[User, Depends(get_current_user)], id_canal: int, id_sala: int, session: SessionDep):
    sala_db = session.get(Salas, id_sala)
    if not sala_db:
        raise HTTPException(status_code=404, detail="Sala no encontrada")
    elif id_canal != sala_db.id_canal:
        raise HTTPException(status_code=404, detail="La sala no pertenece a ese canal")
    elif not es_admin(session, current_user.id_usuario, id_canal):
        raise HTTPException(status_code=403, detail="Permisos insuficientes")
    else:
        session.delete(sala_db)
        session.commit()
        return {"message": "Sala eliminada exitosamente"}
