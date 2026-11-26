from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[2]


class Configuracion(BaseSettings):
    """Configuracion de la aplicacion leida desde variables de entorno o archivo .env."""

    database_url: str
    app_env: str = "development"
    secret_key: str

    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


configuracion = Configuracion()
