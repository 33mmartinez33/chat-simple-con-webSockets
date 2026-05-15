from ..models import Usuarios
from ..schemas import UsuarioCreate
from ..config import settings

from datetime import date, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from ..database import get_session
from ..dependencies import SessionDep, authenticate_user, create_access_token, get_password_hash


router = APIRouter(tags=["auth"])

# LOGIN/REGISTRO

# Usuario inicia sesión
@router.post("/login")
async def login_for_access_token(response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Annotated[Session, Depends(get_session)]):
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id_usuario)}, expires_delta=access_token_expires
    )
    response.set_cookie(key = "access_token", value=access_token, httponly= True, samesite="lax", secure=False, path="/")
    # print("SETTING COOKIE:", access_token)
    return {"message": "Ok"}


#  Registrarse
@router.post("/sign_in")
async def sign_in(response: Response, usuario: UsuarioCreate, session: SessionDep):  
   
    if session.exec(select(Usuarios).where(Usuarios.email == usuario.email)).first():
        raise HTTPException(status_code=400, detail = "Email repetido")
    elif session.exec(select(Usuarios).where(Usuarios.username == usuario.username)).first():
        raise HTTPException(status_code=400, detail = "Username repetido")
    else:
        # insert usuario
        usuario_insertar: Usuarios = Usuarios(
            email = usuario.email,
            username = usuario.username,
            contraseña = get_password_hash(usuario.password),
            fecha_de_nacimiento=usuario.fecha_de_nacimiento,
            fecha_de_alta=date.today()
        )
        session.add(usuario_insertar)
        session.commit()
        session.refresh(usuario_insertar)  # ← ID autoincremental + datos frescos
   
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(usuario_insertar.id_usuario)}, expires_delta=access_token_expires
        )
       
        response.set_cookie(key = "access_token", value=access_token, httponly= True, samesite="lax", secure=False, path="/")
        print("SETTING COOKIE:", access_token)
        return {"message": "Ok"}

