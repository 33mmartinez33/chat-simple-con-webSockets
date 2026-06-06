"""
Plan de pruebas — Nexus Chat
============================
Tipos de pruebas contemplados:
  1. Funcionales REST   — validan que los endpoints devuelven el status y cuerpo correctos.
  2. Integración WS     — validan el flujo completo de WebSocket: autenticación, broadcast
                          y creación de notificaciones en base de datos.
  3. Integración UI/REST— validan que acciones del frontend (leer sala) actualizan
                          correctamente el estado de notificaciones en la BD.

Ejecución:
  cd backend
  pytest tests/ -v
"""

from sqlmodel import Session, select

from app.models import UsuarioNotificacion, Usuarios


# ── Helpers reutilizables ──────────────────────────────────────────────────────

def registrar(client, email, username, password="Test1234"):
    return client.post("/sign_in", json={
        "email": email,
        "username": username,
        "contrasenha": password,
        "fecha_de_nacimiento": "1990-01-01",
    })


def login(client, username, password="Test1234"):
    return client.post("/login", data={"username": username, "password": password})


# ══════════════════════════════════════════════════════════════════════════════
# PRUEBA 1 — Registro de usuario
# Tipo: funcional REST
# Entrada: POST /sign_in con email, username, contraseña y fecha de nacimiento válidos
# Resultado esperado: HTTP 200 y mensaje de confirmación
# ══════════════════════════════════════════════════════════════════════════════
def test_registro_usuario(client):
    res = registrar(client, "user1@test.com", "user1")

    assert res.status_code == 200
    assert res.json() == {"message": "Ok"}


# ══════════════════════════════════════════════════════════════════════════════
# PRUEBA 2 — Login con credenciales incorrectas
# Tipo: funcional REST + seguridad (timing attack)
# Entrada: POST /login con contraseña incorrecta para un usuario registrado
# Resultado esperado: HTTP 401 Unauthorized
# ══════════════════════════════════════════════════════════════════════════════
def test_login_credenciales_incorrectas(client):
    registrar(client, "user1@test.com", "user1")

    res = login(client, "user1", "contrasenha_incorrecta")

    assert res.status_code == 401


# ══════════════════════════════════════════════════════════════════════════════
# PRUEBA 3 — Acceso a ruta protegida sin token
# Tipo: funcional REST
# Entrada: GET /users/me sin cookie de sesión
# Resultado esperado: HTTP 401 Unauthorized
# ══════════════════════════════════════════════════════════════════════════════
def test_acceso_sin_token(client):
    res = client.get("/users/me")

    assert res.status_code == 401


# ══════════════════════════════════════════════════════════════════════════════
# PRUEBA 4 — Envío y recepción de mensaje en sala
# Tipo: integración WebSocket
# Procedimiento: usuario autenticado se conecta a una sala, envía un mensaje
#                y recibe el broadcast con los datos correctos
# Resultado esperado: mensaje recibido con contenido, username, fecha e id_mensaje
# ══════════════════════════════════════════════════════════════════════════════
def test_websocket_mensaje_sala(client, setup_chat):
    login(client, "user1")
    id_canal = setup_chat["id_canal"]
    id_sala  = setup_chat["id_sala"]

    with client.websocket_connect(f"/ws/users/me/channels/{id_canal}/rooms/{id_sala}") as ws:
        ws.send_text('{"contenido": "Hola mundo"}')
        data = ws.receive_json()

    assert data["contenido"] == "Hola mundo"
    assert data["username"] == "user1"
    assert "fecha" in data
    assert "id_mensaje" in data


# ══════════════════════════════════════════════════════════════════════════════
# PRUEBA 5 — Notificación para usuario ausente
# Tipo: integración WebSocket
# Procedimiento: user1 conectado a la sala envía un mensaje; user2 es miembro
#                del canal pero no está conectado a la sala
# Resultado esperado: se crea una fila en UsuarioNotificacion para user2
#                     con leida=False
# ══════════════════════════════════════════════════════════════════════════════
def test_notificacion_usuario_ausente(client, setup_chat, engine):
    login(client, "user1")
    id_canal = setup_chat["id_canal"]
    id_sala  = setup_chat["id_sala"]

    # user1 envía mensaje; user2 es miembro pero no está conectado (ausente)
    with client.websocket_connect(f"/ws/users/me/channels/{id_canal}/rooms/{id_sala}") as ws:
        ws.send_text('{"contenido": "Mensaje de prueba"}')
        ws.receive_json()  # consumir el broadcast propio

    # Verificar que se creó la notificación no leída para user2
    with Session(engine) as s:
        user2 = s.exec(select(Usuarios).where(Usuarios.username == "user2")).first()
        notifs = s.exec(
            select(UsuarioNotificacion).where(
                UsuarioNotificacion.id_usuario == user2.id_usuario
            )
        ).all()

    assert len(notifs) == 1
    assert notifs[0].leida == False


# ══════════════════════════════════════════════════════════════════════════════
# PRUEBA 6 — Marcado de notificaciones como leídas
# Tipo: integración UI / REST
# Procedimiento: user2 navega a la sala (llama a PATCH /notifications/read)
# Resultado esperado: HTTP 200, actualizadas == 1
# ══════════════════════════════════════════════════════════════════════════════
def test_marcar_notificaciones_leidas(client, setup_chat):
    # user1 genera una notificación para user2
    login(client, "user1")
    id_canal = setup_chat["id_canal"]
    id_sala  = setup_chat["id_sala"]

    with client.websocket_connect(f"/ws/users/me/channels/{id_canal}/rooms/{id_sala}") as ws:
        ws.send_text('{"contenido": "Mensaje"}')
        ws.receive_json()

    # user2 abre la sala y marca las notificaciones como leídas
    client.cookies.clear()
    login(client, "user2")
    res = client.patch("/users/me/notifications/read", json={"id_sala": id_sala})

    assert res.status_code == 200
    assert res.json()["actualizadas"] == 1
