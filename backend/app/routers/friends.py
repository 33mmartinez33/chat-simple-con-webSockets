
# AMIGOS

# Get lista amigos
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from ..dependencies import SessionDep, get_current_user
from ..models import Amigos, Usuarios
from ..schemas import User

router = APIRouter(tags=["friends"])

@router.get("/users/me/friends")
async def get_amigos(current_user: Annotated[User, Depends(get_current_user)], session: SessionDep):
    amigos1 = session.exec(
        select(Amigos, Usuarios)
        .join(
            Usuarios,
            Amigos.id_usuario2 == Usuarios.id_usuario
        ).where(
            Amigos.id_usuario1 == current_user.id_usuario
        )
    ).all()

    amigos2 = session.exec(
        select(Amigos, Usuarios)
        .join(
            Usuarios,
            Amigos.id_usuario1 == Usuarios.id_usuario
        ).where(
            Amigos.id_usuario2 == current_user.id_usuario
        )
    ).all()

    amigos_combined = amigos1 + amigos2

    lista_amigos = []
    for amigo in amigos_combined:
        lista_amigos.append({
            "id_amigo": amigo[1].id_usuario,
            "username": amigo[1].username,
            "email": amigo[1].email,
            "fecha_amistad": amigo[0].fecha_amistad
        })


    return lista_amigos

# Ver info de un amigo
@router.get("/users/me/friends/{id_usuario2}")
async def ver_info_amigo(_current_user: Annotated[User, Depends(get_current_user)], id_usuario2: int, session: SessionDep):
    
    infoAmigo = session.exec(select(Usuarios).where(Usuarios.id_usuario == id_usuario2)).first()

    if not infoAmigo:
        raise HTTPException(status_code=404, detail="Usuario no encontrado") 
    
    return infoAmigo.model_dump(exclude= {"contrasenha", "email", "id_usuario"})


# Añadir amigo
@router.post("/users/me/friends/{id_usuario2}")
async def anhadir_amigo(current_user: Annotated[User, Depends(get_current_user)], id_usuario2: int, session: SessionDep):
    if not session.get(Usuarios, current_user.id_usuario) or not session.get(Usuarios, id_usuario2):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")  
    elif id_usuario2 == current_user.id_usuario:
        raise HTTPException(status_code=400, detail="No puedes añadirte como amigo")  
    elif session.exec(
        select(Amigos).where(
            Amigos.id_usuario1 == current_user.id_usuario,
            Amigos.id_usuario2 == id_usuario2
        )
    ).first():
        raise HTTPException(status_code=400, detail="Ya sois amigos")
    else:
        amistad = Amigos(
            id_usuario1 = current_user.id_usuario,
            id_usuario2 = id_usuario2,
            fecha_amistad = date.today()
        )
        session.add(amistad)
        session.commit()
        session.refresh(amistad)


        return {"message": "Amigo añadido"}


# Eliminar amigo
@router.delete("/users/me/friends/{id_usuario2}")
async def eliminar_amigo(current_user: Annotated[User, Depends(get_current_user)], id_usuario2: int, session: SessionDep):
    amistad = session.exec(
        select(Amigos).where(
            Amigos.id_usuario1 == current_user.id_usuario,
            Amigos.id_usuario2 == id_usuario2
        )
    ).first()
   
    if not amistad:
        raise HTTPException(status_code=404, detail="Amistad no encontrada")
   
    session.delete(amistad)
    session.commit()
   
    return {"message": "Amigo eliminado exitosamente"}

