from datetime import timedelta, timezone, datetime
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, WebSocket, WebSocketException, status
import jwt
from sqlmodel import Session, select

from .database import get_session
from .models import Amigos, RolAdministradorParticipanteT, RolUsuarioCanal, Usuarios
from .schemas import TokenData, User
from .config import settings, ALLOWED_ORIGINS
from pwdlib import PasswordHash


SessionDep = Annotated[Session, Depends(get_session)]

password_hash = PasswordHash.recommended()

# Hash precalculado de una contraseña ficticia para prevenir timing attacks:
# si el usuario no existe, se ejecuta verify_password igualmente para que
# el tiempo de respuesta no revele si el username es válido o no
DUMMY_HASH = password_hash.hash("dummypassword")


# Verifica que plain_password coincida con hashed_password
# Retorna True si coinciden, False en caso contrario
def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


# Genera y retorna el hash bcrypt de la contraseña recibida
def get_password_hash(password):
    return password_hash.hash(password)


# Busca y retorna el usuario con id_usuario dado, o None si no existe
# Parámetros:
#   id_usuario: ID del usuario a buscar
#   session: sesión activa de base de datos
def get_user(id_usuario: int, session: Session):
    user_db = session.exec(
        select(Usuarios).where(
            Usuarios.id_usuario == id_usuario
        )
    ).first()

    return user_db


# Autentica al usuario verificando username y contraseña
# Retorna el objeto Usuarios si las credenciales son correctas, False si no
# Parámetros:
#   username: nombre de usuario
#   password: contraseña en texto plano
#   session: sesión activa de base de datos
def authenticate_user(username: str, password: str, session: Session):
    user = session.exec(
        select(Usuarios).where(
            Usuarios.username == username
        )
    ).first()
    if not user:
        # Se ejecuta verify_password aunque el usuario no exista para evitar timing attacks
        verify_password(password, DUMMY_HASH)
        return False

    if not verify_password(password, user.contrasenha):
        return False

    return user


# Genera un JWT firmado con el payload data y el tiempo de expiración indicado
# Parámetros:
#   data: diccionario con los claims a incluir en el token (ej. {"sub": id_usuario})
#   expires_delta: tiempo de vida del token; si es None, expira en 15 minutos
# Retorna el token JWT como string
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


# FastAPI cachea las dependencias por request, por lo que get_session solo se ejecuta
# una vez aunque aparezca en múltiples sitios.
# Decodifica el JWT de la cookie, valida al usuario y lo retorna
# Lanza HTTP 401 si el token es inválido, expirado o el usuario no existe
async def get_current_user(session: Annotated[Session, Depends(get_session)], access_token: Annotated[str | None, Cookie()] = None):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        print("jwt decodificado")
        print("jwt decodificado, expira:", payload.get("exp"))
        print("ahora:", datetime.now(timezone.utc).timestamp())
        id_usuario = payload.get("sub")
        if id_usuario is None:
            raise credentials_exception
        token_data = TokenData(id_usuario=int(id_usuario))
    except jwt.InvalidTokenError:
        print("Invalidtokenerror")
        raise credentials_exception
    user = get_user(id_usuario=token_data.id_usuario, session=session)
    if user is None:
        raise credentials_exception
    return user

# Dependencia tipada para inyectar el usuario autenticado en los endpoints
UserDependency = Annotated[User, Depends(get_current_user)]


# Dependencia para WebSocket: cierra la conexión con código 1008 si el origen no está permitido
# Parámetros:
#   websocket: conexión WebSocket entrante
async def verify_origin(websocket: WebSocket):
    origin = websocket.headers.get("origin")
    if origin not in ALLOWED_ORIGINS:
        await websocket.close(code=1008)
        raise WebSocketException(code=1008)


# Comprueba si el usuario tiene rol de administrador en el canal indicado
# Retorna True si es admin, False en caso contrario
# Parámetros:
#   session: sesión activa de base de datos
#   id_usuario: ID del usuario a comprobar
#   id_canal: ID del canal donde se verifica el rol
def es_admin(session: Session, id_usuario: int, id_canal: int):
    return bool(session.exec(
        select(RolUsuarioCanal).where(
            RolUsuarioCanal.id_usuario == id_usuario,
            RolUsuarioCanal.id_canal == id_canal,
            RolUsuarioCanal.rol == RolAdministradorParticipanteT.ADMINISTRADOR
        )
    ).first())


# Comprueba si el usuario es admin o participante en el canal indicado
# Retorna True si tiene alguno de los dos roles, False si no pertenece al canal
# Parámetros:
#   session: sesión activa de base de datos
#   id_usuario: ID del usuario a comprobar
#   id_canal: ID del canal donde se verifica el rol
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


# Comprueba si dos usuarios son amigos
# Retorna True si existe la relación de amistad, False si no
# Parámetros:
#   session: sesión activa de base de datos
#   id_usuario1, id_usuario2: IDs de los dos usuarios a comprobar
def son_amigos(session: Session, id_usuario1: int, id_usuario2: int):
    # Se ordena para cumplir la restricción id_usuario1 < id_usuario2 de la tabla
    menor = min(id_usuario1, id_usuario2)
    mayor = max(id_usuario1, id_usuario2)

    return bool(session.exec(
        select(Amigos).where(
            Amigos.id_usuario1 == menor,
            Amigos.id_usuario2 == mayor
        )
    ).first())
