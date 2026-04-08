
# USUARIOS

# Ver todos los usuarios
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import select

from ..dependencies import SessionDep, get_current_user, get_password_hash
from ..models import Usuarios
from ..schemas import User, UsuarioUpdate

router = APIRouter(tags=["users"])

@router.get("/users")
async def get_todos_usuarios(_current_user: Annotated[User, Depends(get_current_user)], session: SessionDep, q: str | None = None):
    if q:
        usuarios = session.exec(
            select(Usuarios).where(Usuarios.username.contains(q))
        ).all()
    else:
        usuarios = session.exec(select(Usuarios)).all()
    return usuarios


# Ver info de usuario autenticado
@router.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)]):
    return current_user



# Actualizar usuario
@router.put("/users/me")
async def actualizar_usuario(nuevos_datos: UsuarioUpdate, current_user: Annotated[User, Depends(get_current_user)], session: SessionDep):
    usuario_db = session.get(Usuarios, current_user.id_usuario) #Se obtienen los datos de usuario del currentuser
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado") # si por lo que sea falla, devuelve un error
    
    elif session.exec(
        select(Usuarios).where(
            Usuarios.username == nuevos_datos.username
        ).first()): # Por otro lado, si al intentar cambiar el username resulta que ya esta en uso, devuelve el error

        raise HTTPException(status_code=400, detail="Ese username ya esta en uso")
    # si el usuario cambia la contraseña se hashea, no es elif porque puede cambiar el username tambien 

    if nuevos_datos.contraseña != None:        
        nuevos_datos.contraseña = get_password_hash(nuevos_datos.contraseña)

    nuevos_datos = nuevos_datos.model_dump(exclude_unset=True)
    usuario_db.sqlmodel_update(nuevos_datos)
    session.add(usuario_db)
    session.commit()
    session.refresh(usuario_db)

    return usuario_db


# Eliminar usuario
@router.delete("/users/me")
async def elimina_usuario(current_user: Annotated[User, Depends(get_current_user)], session: SessionDep):
    usuario_db = session.get(Usuarios, current_user.id_usuario)
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
   
    session.delete(usuario_db)
    session.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
