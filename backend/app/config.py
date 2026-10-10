"""
Ransomware Early-Warning System — Backend Configuration
Member 5 (Backend Engineer) scope: FastAPI, MySQL, JWT, device/event/alert/incident storage.

Settings are loaded from environment variables (.env supported). Defaults to a local
SQLite database so the service runs out-of-the-box for demos; point DATABASE_URL at a
MySQL instance for the production/judge-demo deployment.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- General ---
    APP_NAME: str = "Ransomware Early-Warning System — Backend"
    ENV: str = "development"

    # --- Database ---
    # Examples:
    #   SQLite (default, zero setup):  sqlite:///./ransomware_ews.db
    #   MySQL:                          mysql+pymysql://user:password@localhost:3306/ransomware_ews
    DATABASE_URL: str = "sqlite:///./ransomware_ews.db"

    # --- JWT Auth ---
    JWT_SECRET_KEY: str = "CHANGE_ME_BEFORE_DEPLOYING"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8  # 8 hours

    # --- Device ingestion ---
    # Monitoring agents / ML engine authenticate with a per-device API key
    # (header: X-Device-Key) instead of a user JWT.
    DEVICE_KEY_HEADER: str = "X-Device-Key"

    # --- Risk tiering (mirrors config.json in the sidecar prototype) ---
    RISK_NORMAL_MAX: int = 30
    RISK_SUSPICIOUS_MAX: int = 75  # 76-100 => CRITICAL

    # --- CORS (dashboard origin) ---
    CORS_ORIGINS: list[str] = ["*"]

    # --- CERT-In reporting ---
    CERT_IN_POC_EMAIL: str = "socadmin@institution.edu.in"


settings = Settings()
