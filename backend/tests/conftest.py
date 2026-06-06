import datetime

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.dependencies import get_password_hash, verify_origin
from app.database import get_session
from app.main import app
from app.models import (
    Canales, RolAdministradorParticipanteT, RolUsuarioCanal,
    Salas, TipoSalaT, Usuarios,
)


# Base de datos SQLite en memoria: se crea y destruye por cada test
@pytest.fixture(scope="function")
def engine():
    _engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # misma conexión para todas las sesiones del test
    )
    SQLModel.metadata.create_all(_engine)
    yield _engine
    SQLModel.metadata.drop_all(_engine)


# Cliente HTTP con las dependencias de BD y origen sobreescritas para tests
@pytest.fixture
def client(engine):
    # Cada llamada obtiene su propia sesión sobre el engine de test
    def get_session_override():
        with Session(engine) as s:
            yield s

    # En tests no hay origen HTTP real, se omite la validación
    async def verify_origin_override():
        pass

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[verify_origin] = verify_origin_override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# Crea directamente en BD los dos usuarios, canal, roles y sala necesarios
# para los tests de WebSocket y notificaciones, sin depender de la serialización HTTP
@pytest.fixture
def setup_chat(engine):
    with Session(engine) as s:
        u1 = Usuarios(
            email="user1@test.com", username="user1",
            contrasenha=get_password_hash("Test1234"),
            fecha_de_nacimiento=datetime.date(1990, 1, 1),
            fecha_de_alta=datetime.date.today(),
        )
        u2 = Usuarios(
            email="user2@test.com", username="user2",
            contrasenha=get_password_hash("Test1234"),
            fecha_de_nacimiento=datetime.date(1990, 1, 1),
            fecha_de_alta=datetime.date.today(),
        )
        s.add_all([u1, u2])
        s.commit()
        s.refresh(u1)
        s.refresh(u2)

        canal = Canales(
            id_usuario_dueno=u1.id_usuario,
            nombre="canal-test",
            contenido_principal="Bienvenidos",
        )
        s.add(canal)
        s.commit()
        s.refresh(canal)

        s.add_all([
            RolUsuarioCanal(
                id_usuario=u1.id_usuario, id_canal=canal.id_canal,
                rol=RolAdministradorParticipanteT.ADMINISTRADOR,
            ),
            RolUsuarioCanal(
                id_usuario=u2.id_usuario, id_canal=canal.id_canal,
                rol=RolAdministradorParticipanteT.PARTICIPANTE,
            ),
        ])
        s.commit()

        sala = Salas(
            id_canal=canal.id_canal,
            tipo=TipoSalaT.TEXTO,
            nombre_sala="general",
        )
        s.add(sala)
        s.commit()
        s.refresh(sala)

        # Extraer valores escalares dentro del bloque with para evitar DetachedInstanceError
        id_canal = canal.id_canal
        id_sala  = sala.id_sala

    return {"id_canal": id_canal, "id_sala": id_sala}
