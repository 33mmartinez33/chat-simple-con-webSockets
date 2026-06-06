from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import select

from ..dependencies import SessionDep, get_current_user, get_password_hash
from ..models import Usuarios
from ..schemas import User, UsuarioUpdate

router = APIRouter(tags=["users"])


# USUARIOS

# Retorna todos los usuarios. Si se pasa q, filtra por username (búsqueda parcial)
# Parámetros de query:
#   q: texto opcional para filtrar por username
@router.get("/users")
async def get_todos_usuarios(_current_user: Annotated[User, Depends(get_current_user)], session: SessionDep, q: str | None = None):
    if q:
        usuarios = session.exec(
            select(Usuarios).where(Usuarios.username.contains(q))
        ).all()
    else:
        usuarios = session.exec(select(Usuarios)).all()
    return usuarios


# Retorna los datos del usuario autenticado actualmente
@router.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


# Actualiza los datos del usuario autenticado
# Solo se aplican los campos incluidos en el body (exclude_unset)
# Si se cambia la contraseña, se hashea antes de guardar
# Parámetros:
#   nuevos_datos: campos a actualizar (todos opcionales)
# Retorna el usuario con los datos actualizados
@router.put("/users/me")
async def actualizar_usuario(nuevos_datos: UsuarioUpdate, current_user: Annotated[User, Depends(get_current_user)], session: SessionDep):
    usuario_db = session.get(Usuarios, current_user.id_usuario)
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    elif session.exec(
        select(Usuarios).where(
            Usuarios.username == nuevos_datos.username
        ).first()):
        raise HTTPException(status_code=400, detail="Ese username ya esta en uso")

    # Si se cambia la contraseña, se hashea antes de persistir
    if nuevos_datos.contrasenha != None:
        nuevos_datos.contrasenha = get_password_hash(nuevos_datos.contrasenha)

    nuevos_datos = nuevos_datos.model_dump(exclude_unset=True)
    usuario_db.sqlmodel_update(nuevos_datos)
    session.add(usuario_db)
    session.commit()
    session.refresh(usuario_db)

    return usuario_db


# Elimina la cuenta del usuario autenticado y borra la cookie de sesión
# Retorna HTTP 204 sin contenido
@router.delete("/users/me")
async def elimina_usuario(response: Response, current_user: Annotated[User, Depends(get_current_user)], session: SessionDep):
    usuario_db = session.get(Usuarios, current_user.id_usuario)
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    session.delete(usuario_db)
    session.commit()

    response.status_code = status.HTTP_204_NO_CONTENT
    response.delete_cookie(key="access_token")

    return response
