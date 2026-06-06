from pydantic_settings import BaseSettings

# Orígenes permitidos para CORS y validación de WebSocket
ALLOWED_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]


# Configuración de la aplicación cargada desde variables de entorno o archivo .env
class Settings(BaseSettings):
    SECRET_KEY: str               # Clave para firmar los JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Tiempo de vida del token en minutos
    DATABASE_URL: str             # URL de conexión a la base de datos
    ALGORITHM: str                # Algoritmo de firma del JWT (ej. HS256)

    class Config:
        env_file = ".env"


settings = Settings()
print("ACCESS_TOKEN_EXPIRE_MINUTES:", settings.ACCESS_TOKEN_EXPIRE_MINUTES)
