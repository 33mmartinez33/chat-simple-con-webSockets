from datetime import timedelta, timezone, datetime
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, WebSocket, WebSocketException, status
import jwt
from sqlmodel import Session, select

from .database import get_session
from .models import Amigos, RolAdministradorParticipanteT, RolUsuarioCanal, Usuarios
from .schemas import TokenData
from .config import settings, ALLOWED_ORIGINS
from pwdlib import PasswordHash


SessionDep = Annotated[Session, Depends(get_session)]

password_hash = PasswordHash.recommended()

# hash precalculado de una contraseña ficticia ("dummypassword") con propósito de prevenir ataques de temporización (timing attacks).
DUMMY_HASH = password_hash.hash("dummypassword")


# para legibilidad y desacoplamiento
def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password) # Devuelve true o false segun si la contraseña coincide


# para legibilidad y desacoplamiento
def get_password_hash(password):
    return password_hash.hash(password)


def get_user(id_usuario: int, session: Session):
    user_db = session.exec(
        select(Usuarios).where(
            Usuarios.id_usuario == id_usuario
        )
    ).first()

    return user_db


def authenticate_user(username: str, password: str, session: Session):
    print("autenticando usuario")
    user = session.exec(
        select(Usuarios).where(
            Usuarios.username == username
        )
    ).first()
    if not user:
        verify_password(password, DUMMY_HASH)
        return False
    
    if not verify_password(password, user.contraseña):
        return False
    
    return user




def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    print("jwt creado")
    return encoded_jwt


#FastAPI cachea las dependencias por request, por lo que get_session solo se ejecuta una vez aunque aparezca en múltiples sitios.
# Obtiene el token directamente
async def get_current_user(session: Annotated[Session, Depends(get_session)], access_token: Annotated[str | None, Cookie()] = None):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        print("jwt decodificado")
        id_usuario = payload.get("sub")
        if id_usuario is None:
            print("id usuario es none, excepcion")
            raise credentials_exception
        token_data = TokenData(id_usuario=int(id_usuario))
    except jwt.InvalidTokenError:
        print("Invalidtokenerror")
        raise credentials_exception
    user = get_user(id_usuario=token_data.id_usuario, session=session)
    if user is None:
        raise credentials_exception
    return user


# Comprobar el origen de la cookie para ws
async def verify_origin(websocket: WebSocket):
    origin = websocket.headers.get("origin")
    if origin not in ALLOWED_ORIGINS:
        await websocket.close(code=1008)
        raise WebSocketException(code=1008)

# comprubea si el usuario es admin en el canal que se pasa por parametro
def es_admin(session: Session, id_usuario: int, id_canal: int):
    return bool(session.exec(
        select(RolUsuarioCanal).where(
            RolUsuarioCanal.id_usuario == id_usuario,
            RolUsuarioCanal.id_canal == id_canal,
            RolUsuarioCanal.rol == RolAdministradorParticipanteT.ADMINISTRADOR
        )
    ).first())


# comprubea si el rol es admin o participante
def es_participante_o_admin(session: Session, id_usuario: int, id_canal: int):
    return bool(session.exec(
        select(RolUsuarioCanal).where(
            RolUsuarioCanal.id_usuario == id_usuario,
            RolUsuarioCanal.id_canal == id_canal,
            RolUsuarioCanal.rol.in_([
                RolAdministradorParticipanteT.ADMINISTRADOR,
                RolAdministradorParticipanteT.PARTICIPANTE
            ])
        )
    ).first())


# Comprueba si los 2 usuarios que se le pasa como parametro son amigos
def son_amigos(session: Session, id_usuario1: int, id_usuario2: int):
    return bool(session.exec(
        select(Amigos).where(
            Amigos.id_usuario1 == id_usuario1,
            Amigos.id_usuario2 == id_usuario2            
        )
    ).first() or session.exec(
        select(Amigos).where(
            Amigos.id_usuario1 == id_usuario2,
            Amigos.id_usuario2 == id_usuario1            
        )
    ).first())


