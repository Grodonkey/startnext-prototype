from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SESSION_TOKEN_EXPIRE_HOURS: int = 2

    # Email
    RESEND_API_KEY: str
    FROM_EMAIL: str

    # Application
    FRONTEND_URL: str = "http://localhost:5173"
    BACKEND_URL: str = "http://localhost:8000"

    # Admin
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str


settings = Settings()
