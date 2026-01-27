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
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173",
        "https://localhost:5173",
        "https://startnext.grodonkey.com",
        "capacitor://localhost",
        "ionic://localhost",
        "http://localhost",
    ]

    # Admin
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_ASSISTANT_ID: str = ""

    # AI Coach Settings
    AI_MAX_ANONYMOUS_MESSAGES: int = 5  # Max messages before login required
    AI_MIN_MESSAGES_FOR_PROJECT: int = 3  # Min messages before project creation allowed
    AI_MAX_ANONYMOUS_DRAFTS: int = 2  # Max drafts anonymous users can generate


settings = Settings()
