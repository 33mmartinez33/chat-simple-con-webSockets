from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from ..dependencies import UserDependency, es_admin, SessionDep, get_current_user
from ..models import Canales, RolAdministradorParticipanteT, RolUsuarioCanal, Usuarios
from ..schemas import CanalCreate, CanalUpdate, User


router = APIRouter(tags=["channels"])

# CANALES

# Retorna los canales a los que el usuario NO pertenece, opcionalmente filtrados por nombre
# Parámetros de query:
#   q: texto para búsqueda parcial por nombre (insensible a mayúsculas)
@router.get("/channels")
async def get_todos_canales(current_user: UserDependency, session: SessionDep, q: str = ""):
    ids_usuario = select(RolUsuarioCanal.id_canal).where(
        RolUsuarioCanal.id_usuario == current_user.id_usuario
    )
    query = select(Canales).where(Canales.id_canal.not_in(ids_usuario))
    if q:
        query = query.where(Canales.nombre.ilike(f"%{q}%"))
    return session.exec(query).all()


# Retorna los canales en los que el usuario autenticado tiene rol (admin o participante)
@router.get("/users/me/channels")
async def get_canales_usuario(current_user: UserDependency, session: SessionDep):
    canales = session.exec(
        select(Canales).distinct().join(  # distinct() evita duplicados por múltiples roles
            RolUsuarioCanal,
            Canales.id_canal == RolUsuarioCanal.id_canal
        ).where(
            RolUsuarioCanal.id_usuario == current_user.id_usuario,
            RolUsuarioCanal.rol.in_([
                RolAdministradorParticipanteT.ADMINISTRADOR,
                RolAdministradorParticipanteT.PARTICIPANTE
            ])
        )
    ).all()
    return canales


# Une al usuario autenticado al canal indicado con rol de participante
# Parámetros de ruta:
#   id_canal: canal al que se quiere unir el usuario
# Lanza HTTP 404 si el canal no existe, HTTP 400 si ya es miembro
@router.post("/users/me/channels/{id_canal}")
async def anhadir_canal_usuario(current_user: UserDependency, id_canal: int, session: SessionDep):
    if not session.get(Usuarios, current_user.id_usuario) or not session.get(Canales, id_canal):
        raise HTTPException(status_code=404, detail="Usuario o canal no encontrado")
    elif session.exec(
        select(RolUsuarioCanal).where(
            RolUsuarioCanal.id_usuario == current_user.id_usuario,
            RolUsuarioCanal.id_canal == id_canal
        )
    ).first():
        raise HTTPException(status_code=400, detail="Ya sigues este canal")
    else:
        relacion = RolUsuarioCanal(
            id_usuario=current_user.id_usuario,
            id_canal=id_canal,
            rol=RolAdministradorParticipanteT.PARTICIPANTE
        )
        session.add(relacion)
        session.commit()
        session.refresh(relacion)
        return {"message": "Canal añadido"}


# TODO cambiar rol de un usuario en un canal a admin

# Retorna los datos del canal junto con el rol del usuario autenticado en él
# Parámetros de ruta:
#   id_canal: canal a consultar
# Lanza HTTP 404 si el canal no existe, HTTP 403 si el usuario no es miembro
@router.get("/users/me/channels/{id_canal}")
async def get_canal(current_user: UserDependency, id_canal: int, session: SessionDep):
    canal = session.get(Canales, id_canal)
    rol = session.get(RolUsuarioCanal, (current_user.id_usuario, id_canal))
    if not canal:
        raise HTTPException(status_code=404, detail="Canal no encontrado")
    elif not rol:
        raise HTTPException(status_code=403, detail="No tienes acceso a este canal")
    else:
        return {**canal.model_dump(), "rol": rol.rol}  # ** desempaqueta el modelo para añadir el rol


# Crea un canal nuevo y asigna al creador como administrador
# Parámetros del body:
#   canal: nombre y contenido principal del canal
# Lanza HTTP 400 si el nombre ya existe
@router.post("/users/me/channels")
async def crear_canal(current_user: UserDependency, canal: CanalCreate, session: SessionDep):
    if session.exec(select(Canales).where(Canales.nombre == canal.nombre_canal)).first():
        raise HTTPException(status_code=400, detail="Nombre ya existente")
    else:
        canal_db: Canales = Canales(
            id_usuario_dueno=current_user.id_usuario,
            nombre=canal.nombre_canal,
            contenido_principal=canal.contenido_principal
        )
        session.add(canal_db)
        session.commit()
        session.refresh(canal_db)

        # El creador obtiene automáticamente rol de administrador
        rol_admin = RolUsuarioCanal(
            id_usuario=current_user.id_usuario,
            id_canal=canal_db.id_canal,
            rol=RolAdministradorParticipanteT.ADMINISTRADOR
        )
        session.add(rol_admin)
        session.commit()
        return canal_db


# Actualiza nombre y/o contenido principal del canal
# Solo puede hacerlo un administrador del canal
# Parámetros de ruta:
#   id_canal: canal a actualizar
# Parámetros del body:
#   canal_update: campos a modificar (todos opcionales)
@router.put("/users/me/channels/{id_canal}")
async def actualizar_contenido_canal(current_user: UserDependency, id_canal: int, canal_update: CanalUpdate, session: SessionDep):
    canal_db = session.get(Canales, id_canal)
    if not canal_db:
        raise HTTPException(status_code=404, detail="Canal no encontrado")
    elif not es_admin(session, current_user.id_usuario, id_canal):
        raise HTTPException(status_code=403, detail="Permisos insuficientes")

    update_data = canal_update.model_dump(exclude_unset=True)
    canal_db.sqlmodel_update(update_data)
    session.add(canal_db)
    session.commit()
    session.refresh(canal_db)
    return canal_db


# Elimina el canal y todos sus datos en cascada
# Solo puede hacerlo un administrador del canal
# Parámetros de ruta:
#   id_canal: canal a eliminar
@router.delete("/users/me/channels/{id_canal}")
async def eliminar_canal(current_user: UserDependency, id_canal: int, session: SessionDep):
    canal_db = session.get(Canales, id_canal)
    if not canal_db:
        raise HTTPException(status_code=404, detail="Canal no encontrado")
    elif not es_admin(session, current_user.id_usuario, id_canal):
        raise HTTPException(status_code=403, detail="Permisos insuficientes")

    session.delete(canal_db)
    session.commit()
    return {"message": "Canal eliminado exitosamente"}
